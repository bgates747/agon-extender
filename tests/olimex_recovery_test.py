"""Offline operator tests. Firmware and the MOS keyboard are never contacted."""

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import bench_process
import olimex_bench as runner
from olimex_cli import Observer, CliError


class HumanStart(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = self.root / "game.bin"
        source.write_bytes(b"game")
        self.job = {"id": "game", "sd_program": "/test/game/game.bin", "cwd": "/test/game",
                    "address": "040000", "results": [],
                    "agon": {"path": str(source), "bytes": 4, "sha256": sha256(b"game").hexdigest()}}
        self.kit = {"fixtures": [self.job], "namespace": "game", "human_start": "stage-only",
                    "firmware": {}, "preserve": dict.fromkeys(runner.PRESERVED, "0" * 64)}

    def test_manual_orders_and_incompatible_automation(self):
        self.assertEqual(runner.preflight(self.kit), ["stage", "handback"])
        self.assertEqual(runner.phases(self.kit, enter_cwd=True), ["stage", "enter-cwd", "handback"])
        self.kit["human_start"] = "preload"
        self.assertEqual(runner.preflight(self.kit), ["stage", "preload", "handback"])
        self.assertEqual(runner.phases(self.kit, enter_cwd=True), ["stage", "preload", "handback"])
        self.job["success"] = "PASS"
        with self.assertRaisesRegex(ValueError, "chat verdict"):
            runner.preflight(self.kit)

    def manual_handoff(self, phase, *replies):
        bench = runner.Bench.__new__(runner.Bench)
        bench.kit, bench.out, bench.c = self.kit, self.root, {"ports": ["unused"]}
        bench.idle = bench.validate_ports = bench.keyboard = MagicMock()
        bench.type_line = MagicMock()
        bench.collect_results = MagicMock(side_effect=AssertionError("unexpected collection"))
        with patch("olimex_bench.open_passive_serial") as serial, patch("olimex_cli.secrets.token_hex",
                                                                        return_value="ABCDEF"):
            reader = serial.return_value.__enter__.return_value
            reader.in_waiting = 0
            reader.read.side_effect = [b"VDU 65 66 67 68 69 70 13 10\r\nABCDEF\r\n/ *",
                                       *replies]
            bench.invoke(phase)
        return [call.args[1] for call in bench.type_line.call_args_list]

    def preload(self, load_reply):
        self.kit["human_start"] = "preload"
        return self.manual_handoff("preload", b"/ *CD /test/game\r\n/test/game *",
                                   b"/test/game *LOAD /test/game/game.bin &040000\r\n" + load_reply,
                                   b"/test/game *VDU 3\r\n")

    def test_enter_cwd_leaves_the_exact_prompt_without_loading_or_running(self):
        commands = self.manual_handoff("enter-cwd", b"/ *CD /test/game\r\n/test/game *",
                                       b"/test/game *VDU 3\r\n")
        self.assertEqual(commands, ["VDU 2", "VDU 65 66 67 68 69 70 13 10", "CD /test/game", "VDU 3"])
        self.assertEqual(bench_process.read(self.root / "enter-cwd.json"), {
            "cwd": "/test/game", "prompt": "/test/game *", "entry_directory": "/",
        })

    def test_rejected_directory_has_no_success_receipt(self):
        with self.assertRaisesRegex(CliError, "Directory not found"):
            self.manual_handoff("enter-cwd", b"/ *CD /test/game\r\nDirectory not found\r\n/ *")
        self.assertFalse((self.root / "enter-cwd.json").exists())

    def test_preload_dispatches_one_load_then_leaves_the_prompt(self):
        commands = self.preload(b"/test/game *")
        self.assertEqual(commands, ["VDU 2", "VDU 65 66 67 68 69 70 13 10", "CD /test/game",
                                    "LOAD /test/game/game.bin &040000", "VDU 3"])
        self.assertEqual(bench_process.read(self.root / "preload.json")["prompt"], "/test/game *")

    def test_missing_returned_prompt(self):
        reader = MagicMock(in_waiting=0)
        reader.read.return_value = b"LOAD test.bin &040000\r\n"
        with patch("olimex_cli.time.monotonic", side_effect=[0, 0, 16]):
            with self.assertRaisesRegex(CliError, "No command-correlated"):
                Observer(reader, BytesIO(), MagicMock()).quiet_load("LOAD test.bin &040000", b"/ *")

    def test_rejected_load_no_success_receipt(self):
        with self.assertRaisesRegex(CliError, "File not found"):
            self.preload(b"File not found\r\n/test/game *")
        self.assertFalse((self.root / "preload.json").exists())

    def test_markers_validated_before_run(self):
        dispatch = MagicMock()
        reader = MagicMock(in_waiting=0)
        observer = Observer(reader, BytesIO(), dispatch)
        for bad in (None, object(), b"", "BAD\n", 32):
            with self.assertRaises(ValueError):
                observer.run("RUN", b"/ *", "OK", bad, 2)
        dispatch.assert_not_called()
        reader.read.assert_not_called()
        reader.read.return_value = b"/ *RUN\r\nOK\r\n/ *"
        observer.run("RUN", b"/ *", "OK", "ERR", 2)
        dispatch.assert_called_once()

    def test_bad_deferred_marker_does_not_start_the_application(self):
        observer = Observer(MagicMock(), BytesIO(), MagicMock())
        with self.assertRaises(ValueError):
            observer.run_to_listener("/test/example/run.txt", 30, {"line": [], "seconds": 10}, MagicMock())
        observer.dispatch.assert_not_called()

    def test_verify_mos_has_no_file_service_or_other_serial_dependency(self):
        bench = runner.Bench.__new__(runner.Bench)
        bench.config = {"operation_lock": self.root / "operation.lock"}
        bench.out = self.root
        bench.reset_config = {}
        bench.c = {"ports": ["mainboard", "unavailable-p4-console"]}
        bench.get = bench.start_listener = MagicMock(side_effect=AssertionError("P4 file service"))
        bench.ports_free = MagicMock()
        with patch.object(runner, "identity"), patch.object(runner.olimex_vdp_ota, "mos_witness") as witness:
            bench.perform("verify-mos")
            witness.assert_called_once_with(bench, "mos")
        bench.get.assert_not_called()
        bench.start_listener.assert_not_called()
        self.assertEqual(bench.ports_free.call_args_list[0].args, ("mainboard",))

    def test_prior_deferred_run_is_the_same_named_phase(self):
        from types import SimpleNamespace
        args = SimpleNamespace(job=self.root / "job.json", sha256="a" * 64,
                               config=self.root / "config.json", out=self.root)
        kit = {"fixtures": [{"id": "named"}]}
        original = runner.child_argv(args, "run-named")
        deferred = runner.child_argv(args, "run-named", defer_results=True)
        self.assertEqual(runner.prior_argv(args, kit, "run-named", {"argv": deferred}), deferred)
        self.assertEqual(runner.prior_argv(args, kit, "run-named", {"argv": original}), original)
        kit["fixtures"][0]["listener_handoff"] = {}
        self.assertEqual(runner.prior_argv(args, kit, "run-named", {"argv": deferred}), original)

    def test_standalone_cli_does_not_preflight_fixture_files(self):
        import hashlib
        raw = b'{"fixtures": [], "firmware": {}}'
        manifest = self.root / "mock.json"
        manifest.write_bytes(raw)
        config = self.root / "config.json"
        config.write_text("{}")
        argv = ["olimex_bench.py", "--job", str(manifest), "--sha256", hashlib.sha256(raw).hexdigest(),
                "--config", str(config), "--out", str(self.root), "--operator", "owner", "verify-mos"]
        with (patch.object(sys, "argv", argv),
              patch.object(runner, "preflight", side_effect=AssertionError("fixture preflight")),
              patch.object(runner.bench_process, "run", return_value=0) as run):
            self.assertEqual(runner.main(), 0)
            self.assertEqual(run.call_args.args[0][-1], "worker-verify-mos")

    def test_two_cli_labels_keep_both_dispatches(self):
        bench = runner.Bench.__new__(runner.Bench)
        bench.out, bench.url, bench.kit = self.root, "unused", {**self.kit, "schema": 1}
        bench.own = bench.keyboard = MagicMock()
        bench.listener = lambda label, command, callback: bench.type_line(label, command)
        with patch("olimex_bench.subprocess.run") as send:
            bench.cli("before")
            bench.cli("after")
            with self.assertRaises(FileExistsError):
                bench.cli("before")
        self.assertEqual(send.call_count, 2)
        for label in ("before", "after"):
            self.assertTrue((self.root / f"dispatch-{label}.json").is_file())


class Recovery(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.args = SimpleNamespace(job=self.root / "job", sha256="job-pin", config=self.root / "config",
                                    out=self.root)
        self.owner, self.binding = "operator", {"sha256": "binding"}
        self.config = {"url": "unused", "operation_lock": str(self.root / "lock"),
                       "inventory": str(self.root / "inventory"), "reset_config": str(self.root / "reset")}
        bench_process.record(self.config["reset_config"], {"stable_port": "unused"})
        self.config["p4"] = {"port": "unused"}
        self.kit = {"namespace": "demo", "fixtures": [{"id": "full"}, {"id": "ground"}],
                    "firmware": {"mainboard": {"candidate_write": {"bytes": 3, "sha256": "cand"},
                                               "restore_write": {"bytes": 3, "sha256": "prod"}}}}
        self.failed = "run-full"
        for phase in ("stage", "install-mainboard", self.failed):
            self.journal(phase, failed=(phase == self.failed))
        receipt = self.root / "install-mainboard/independent-verification.json"
        bench_process.record(receipt, {"sha256": "cand", "selection": "candidate",
                                      "verified_extent_bytes": 3, "verified_extent_sha256": "cand",
                                      "component": "native_vdp", "boot_cli_ready": True})
        self.inventory = {"components": {"native_vdp_sha256": "cand"},
                          "native_vdp": {"verification_receipt": str(receipt)}}
        self.bench = runner.Bench(self.config, self.kit, self.root / "recover-after-run-full")
        self.bench.out.mkdir()

    def journal(self, phase, *, failed=False):
        folder = self.root / phase
        folder.mkdir()
        argv = runner.child_argv(self.args, phase)
        shared = {"owner": self.owner, "lease": f"chat:{self.owner}", "phase": phase}
        bench_process.record(folder / "supervisor-started.json", dict(shared, argv=argv))
        # Use an unused group with the current boot and process namespace.
        identity = bench_process.identity(1)
        bench_process.record(folder / "child-started.json", dict(identity, pid=2**30,
                                                                 pgid=2**30, argv=argv))
        bench_process.record(folder / "child-terminal.json", {"pid": 2**30, "returncode": int(failed),
                             "direct_child_joined": True, "group_terminal": True, "live_group_members": []})
        bench_process.record(folder / "operation-binding.json", self.binding)
        if failed:
            bench_process.record(folder / "blocked.json", shared)
        else:
            bench_process.record(folder / "complete.json", {"state": "completed"})

    def run_recovery(self):
        bench_process.record(self.config["inventory"], self.inventory)
        with patch.object(runner.Bench, "firmware", autospec=True) as restore, \
                patch.object(self.bench, "handback") as handback:
            self.bench.perform("recover-after-run-full", recovery=(self.args, self.failed,
                                                                   self.owner, self.binding))
            self.assertEqual(restore.call_args.args[1:], ("mainboard", "restore"))
            handback.assert_called_once_with({"mainboard": self.bench.out / "restore-mainboard"})
            self.assertTrue(restore.call_args.args[0].lock.closed)

    def test_recovery_uses_only_verified_component(self):
        self.run_recovery()
        self.assertFalse((self.root / "run-ground").exists())
        self.assertTrue((self.root / "run-full/blocked.json").is_file())

    def test_refuses_ambiguous_write(self):
        self.inventory["pending_operation"] = {"component": "native_vdp"}
        with self.assertRaisesRegex(RuntimeError, "Unreconciled"):
            self.run_recovery()
        self.assertFalse((self.bench.out / "plan.json").exists())

    def test_failure_before_any_install_needs_only_handback(self):
        self.failed = "stage"
        from shutil import rmtree
        for phase in ("run-full", "install-mainboard", "stage"):
            rmtree(self.root / phase)
        self.bench.out.rename(self.root / "recover-after-stage")
        self.bench.out = self.root / "recover-after-stage"
        self.journal("stage", failed=True)
        self.inventory["components"]["native_vdp_sha256"] = "prod"
        bench_process.record(self.config["inventory"], self.inventory)
        with patch.object(runner.Bench, "firmware") as restore, patch.object(self.bench, "handback") as handback:
            self.bench.perform("recover-after-stage", recovery=(self.args, self.failed, self.owner, self.binding))
            restore.assert_not_called()
            handback.assert_called_once_with({})

    def test_runtime_preflight_uses_runner_environment(self):
        config = dict(self.config, programmer=str(self.root / "missing" / "esptool.py"))
        runner.runtime_preflight(self.kit, config)
        with patch("esptool.__version__", "4.12.0"):
            with self.assertRaisesRegex(RuntimeError, "5.1.0"):
                runner.runtime_preflight(self.kit, config)

    def test_changed_config_binding(self):
        self.binding = {"sha256": "changed"}
        with self.assertRaisesRegex(RuntimeError, "config differs"):
            self.run_recovery()

    def test_unjoined_original_failure(self):
        path = self.root / "run-full/child-terminal.json"
        terminal = bench_process.read(path)
        terminal["direct_child_joined"] = False
        path.write_text(json.dumps(terminal))
        with self.assertRaisesRegex(ValueError, "not joined"):
            self.run_recovery()

    def test_wrong_component_receipt(self):
        self.inventory["native_vdp"]["verification_receipt"] = "unrelated-operation"
        with self.assertRaisesRegex(RuntimeError, "does not bind"):
            self.run_recovery()

    def test_live_worker(self):
        with patch("bench_process.members", return_value=[{"pid": 42}]):
            with self.assertRaisesRegex(ValueError, "group is live"):
                self.run_recovery()

    def test_wrong_owner(self):
        self.owner = "other"
        with self.assertRaisesRegex(RuntimeError, "operator"):
            self.run_recovery()

    def test_wrong_packet(self):
        self.args.sha256 = "other"
        with self.assertRaisesRegex(RuntimeError, "packet"):
            self.run_recovery()

    def test_started_successor(self):
        (self.root / "run-ground").mkdir()
        with self.assertRaisesRegex(RuntimeError, "run-ground"):
            self.run_recovery()
