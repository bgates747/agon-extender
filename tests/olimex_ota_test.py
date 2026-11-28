"""Host checks for the standard runner's UART and ordinary FLASH paths."""

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, call, patch
import json
import struct
import sys
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import olimex_bench as bench
import olimex_vdp_cache as cache
import olimex_vdp_ota as ota


class UartOnly(TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.runner = bench.Bench.__new__(bench.Bench)
        self.runner.out = Path(folder.name)
        self.runner.url = "http://offline"
        self.runner.kit = {"transfer": "uart", "preserve": {}}
        self.runner.idle = MagicMock()
        self.runner.keyboard = MagicMock(return_value={"boot": 1})
        self.runner.type_line = MagicMock()

    def test_refuses_parallel_start_and_listener_capabilities(self):
        with self.assertRaisesRegex(RuntimeError, "parallel listener"):
            self.runner.start_listener("stage", bench.PARALLEL_LISTENER)
        self.runner.type_line.assert_not_called()

    def test_uart_phases_stage_bulk_in_both_directions_and_keep_metadata_separate(self):
        self.runner.start_listener = MagicMock()
        self.runner.validate_ports = MagicMock()
        self.runner.verify_mos = MagicMock()
        inventory = self.runner.out / "inventory.json"
        bench.bench_process.record(inventory, {})
        self.runner.config = {"inventory": inventory}
        self.runner.kit["firmware"] = {}
        staged_path = "/test/demo/app.bin"
        report = "/test/demo/result.bin"
        startup = b"startup"
        self.runner.kit["preserve"]["/autoexec.txt"] = sha256(startup).hexdigest()

        def transfer(operation, remote, *, require_uart, **paths):
            self.assertTrue(require_uart)
            if operation == "put":
                data = paths["source"].read_bytes()
                self.assertTrue(paths["activate"])
            else:
                data = startup if remote == "/autoexec.txt" else b"report"
                paths["destination"].write_bytes(data)
            return {"bytes": len(data), "id": 7, "payload_carrier": "uart"}

        with patch.object(bench, "Client") as client, patch.object(bench, "StagedClient") as worker:
            worker.return_value.begin.side_effect = transfer
            self.runner.stage_uart({staged_path: b"app"}, [report], lambda client, path: None)
            self.runner.collect_results({"results": [report]}, self.runner.out, True)
            self.runner.handback()
            self.assertEqual(self.runner.start_listener.call_args_list, [
                call("stage", bench.LISTENER), call("collect", bench.LISTENER),
            ])
            direct = client.return_value
            direct.upload.assert_not_called()
            direct.download.assert_not_called()
            self.assertEqual(direct.rpc.call_args_list, [call(11)] * 2)
            self.runner.verify_mos.assert_called_once_with("handback-mos")
            self.assertEqual([entry.args for entry in worker.return_value.begin.call_args_list], [
                ("get", "/autoexec.txt"), ("put", staged_path),
                ("get", "/autoexec.txt"), ("get", report),
            ])
        receipt = bench.bench_process.read(self.runner.out / "stage-file-00.receipt.json")
        self.assertEqual((receipt["payload_carrier"], receipt["activated"]), ("uart", True))
        self.assertEqual((self.runner.out / "result.bin").read_bytes(), b"report")

    def test_failed_uart_stage_keeps_evidence_and_never_tries_direct_upload(self):
        self.runner.start_listener = MagicMock()
        with patch.object(bench, "Client") as client, patch.object(bench, "StagedClient") as worker:
            worker.return_value.begin.side_effect = TimeoutError("P4 worker pending")
            with self.assertRaisesRegex(TimeoutError, "P4 worker pending"):
                self.runner.stage_uart({"/test/demo/app.bin": b"app", "/test/demo/next.bin": b"next"},
                                       [], lambda client, path: None)
            worker.return_value.begin.assert_called_once()
            worker.return_value.close.assert_called_once()
            client.return_value.upload.assert_not_called()
            client.return_value.rpc.assert_not_called()
        self.assertTrue((self.runner.out / "stage-file-00.bin").exists())
        self.assertFalse((self.runner.out / "stage-file-00.receipt.json").exists())

    def test_durable_restore_is_checked_before_any_upload(self):
        self.runner.uart_listener = MagicMock()
        self.runner.staged_uart = MagicMock(return_value={
            "payload_carrier": "uart", "bytes": 3, "id": 1,
        })
        cache = {"path": "/extender/recovery/vdp/production.bin", "bytes": 10, "sha256": "a" * 64}
        with patch.object(bench, "Client"):
            with self.assertRaisesRegex(RuntimeError, "Provision"):
                self.runner.stage_uart({"/test/demo/app.bin": b"app"}, [],
                                       lambda client, path: None, restore_cache=cache)
            self.runner.staged_uart.assert_not_called()
            self.runner.stage_uart({"/test/demo/app.bin": b"app"}, [],
                                   lambda client, path: (10, 0) if path == cache["path"] else None,
                                   restore_cache=cache)
        self.assertEqual(self.runner.staged_uart.call_args.args[1:], ("put", "/test/demo/app.bin"))
        self.assertEqual(bench.bench_process.read(self.runner.out / "flash-restore-cache.json"), cache)

    def test_handback_retains_mos_evidence_if_transfer_status_is_unavailable(self):
        self.runner.kit["firmware"] = {}
        self.runner.verify_mos = MagicMock()
        self.runner.idle.side_effect = OSError("unavailable transfer status")
        self.runner.start_listener = MagicMock()
        with self.assertRaisesRegex(OSError, "unavailable transfer status"):
            self.runner.handback()
        self.runner.verify_mos.assert_called_once_with("handback-mos")
        self.runner.start_listener.assert_not_called()
        self.assertFalse((self.runner.out / "handback.json").exists())


class FlashPath(TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.target = MagicMock()
        self.target.out = self.root
        self.target.offboard = None
        self.target.install_dir = "/extender/install/demo"
        self.target.config = {"mainboard_mac": "00:01:02:03:04:05"}
        self.target.c = {"ports": ["offline"]}
        self.target.keyboard.return_value = {"boot": 1}
        self.image = b"\xe9application"
        self.table = b"table"
        self.app = {"bytes": len(self.image), "sha256": sha256(self.image).hexdigest()}

    @staticmethod
    def selector(sequence):
        prefix = struct.pack("<I", sequence)
        row = struct.pack("<I20xII", sequence, 2, zlib.crc32(prefix, 0xFFFFFFFF))
        return row.ljust(0x2000, b"\xff")

    def test_read_only_verification_checks_slot_then_exact_app(self):
        for selector, payload, message in (
            (self.selector(1), self.image, "selected app0, expected app1"),
            (self.selector(2), b"bad", "bytes differ"),
            (self.selector(2), self.image, None),
        ):
            with self.subTest(message=message), patch.object(ota, "mainboard_rom") as loader:
                rom = loader.return_value.return_value
                rom.read_mac.return_value = tuple(range(6))
                stub = rom.run_stub.return_value
                stub.read_flash.side_effect = [self.table.ljust(0x1000, b"\xff"), selector, payload]
                if message:
                    with self.assertRaisesRegex(RuntimeError, message):
                        ota.app_readback(self.target, 1, self.table, self.image)
                else:
                    _, readback = ota.app_readback(self.target, 1, self.table, self.image)
                    self.assertEqual(readback.read_bytes(), self.image)
                loader.return_value.assert_called_once_with("offline", 115200)
                rom.connect.assert_called_once_with("default-reset", 1)
                self.assertEqual(stub.method_calls, [
                    call.read_flash(0x8000, 0x1000), call.read_flash(ota.SELECTOR, 0x2000),
                    *([] if "app0" in (message or "") else [call.read_flash(ota.SLOTS[1], len(self.image))]),
                ])
                rom._port.close.assert_called_once()

    def test_entry_proof_refuses_wrong_slot_or_image(self):
        spec = {"restore_app": self.app, "restore_slot": 1}
        entry = {"component": "native_vdp", "slot": 1, "address": hex(ota.SLOTS[1]),
                 **self.app, "boot_cli_ready": True, "verified_extent_bytes": self.app["bytes"],
                 "verified_extent_sha256": self.app["sha256"]}
        ota.require_image(entry, spec, "restore")
        for change in ({"slot": 0}, {"sha256": "other"}):
            with self.assertRaisesRegex(RuntimeError, "Independent proof"):
                ota.installed({"native_vdp": entry | change}, spec, "restore")

    def test_prior_padded_entry_requires_exact_prefix_padding_and_slot(self):
        spec = {"restore_app": self.app, "restore_slot": 1}
        raw = self.image
        padded = raw + b"\xff" * 16
        path = self.root / "readback.bin"
        path.write_bytes(padded)
        receipt = {"component": "native_vdp", "slot": 1, "address": hex(ota.SLOTS[1]),
                   **self.app, "boot_cli_ready": True, "verified_extent_bytes": len(padded),
                   "verified_extent_sha256": sha256(padded).hexdigest(), "readback": str(path)}
        ota.require_image(receipt, spec, "restore", allow_padded=True)
        with self.assertRaisesRegex(RuntimeError, "extent proof"):
            ota.require_image(receipt, spec, "restore")
        for data in (b"A" + padded[1:], padded[:-1] + b"A"):
            path.write_bytes(data)
            forged = receipt | {"verified_extent_sha256": sha256(data).hexdigest()}
            with self.assertRaisesRegex(RuntimeError, "extent proof"):
                ota.require_image(forged, spec, "restore", allow_padded=True)
        with self.assertRaisesRegex(RuntimeError, "app1"):
            ota.require_image(receipt | {"slot": 0}, spec, "restore", allow_padded=True)

    def test_offboard_flash_uses_frozen_updater_proof_and_live_read(self):
        self.target.offboard = {"verification_sha256": "b" * 64}
        installed = self.root / "readback.bin"
        with (patch.object(ota, "check_updater") as fetch,
              patch.object(ota, "invoke_flash", return_value=1),
              patch.object(ota, "reboot_pair"), patch.object(ota, "mos_witness"),
              patch.object(ota, "app_readback", return_value=(2, installed)) as readback,
              patch.object(ota, "pulse"), patch.object(ota, "wait_boot", return_value={"boot": 3})):
            answer = ota.replace(self.target, {"candidate_app": self.app, "candidate_slot": 0},
                                 "candidate", self.image, self.table, MagicMock())
        fetch.assert_not_called()
        readback.assert_called_once()
        self.assertEqual(answer, (installed, 3))
        self.assertEqual(bench.bench_process.read(self.root / "updater.json")["offboard_verification_sha256"],
                         "b" * 64)

    def test_failed_read_prevents_reset_and_post_read_mos(self):
        with (patch.object(ota, "check_updater"), patch.object(ota, "invoke_flash", return_value=1),
              patch.object(ota, "reboot_pair"), patch.object(ota, "mos_witness") as mos,
              patch.object(ota, "app_readback", side_effect=TimeoutError("ROM sync")) as readback,
              patch.object(ota, "pulse") as reset):
            with self.assertRaisesRegex(TimeoutError, "ROM sync"):
                ota.replace(self.target, {"candidate_app": self.app, "candidate_slot": 0},
                            "candidate", self.image, self.table, MagicMock())
            readback.assert_called_once()
            reset.assert_not_called()
            mos.assert_called_once_with(self.target, "after-flash-mos")

    def test_confirmation_and_reboot_are_required(self):
        for fault in ("missing-prompt", "missing-reboot", None):
            with (self.subTest(fault=fault), TemporaryDirectory() as folder,
                patch.object(ota, "open_passive_serial"),
                patch.object(ota, "Observer") as observer_type,
                patch.object(ota.subprocess, "run") as keyboard,
                patch.object(ota.time, "sleep"),
            ):
                self.target.out = Path(folder)
                observer = observer_type.return_value
                observer.witness.return_value = b"/ *"
                journal = MagicMock()

                expected_crc = zlib.crc32(self.image)

                def exchange(_label, command, predicate, _seconds):
                    capture = b"/ *" + command.encode() + b"\r\n\x0c" + ota.FLASH_BANNER + b"\r\n"
                    capture += f"VDP CRC 0x{expected_crc:08X}\r\n".encode()
                    if fault != "missing-prompt":
                        capture += ota.FLASH_PROMPT + b"\r\n\r\n"
                    if not predicate(capture):
                        raise TimeoutError("prompt")

                def receive(_label, _buffer, predicate, _seconds):
                    capture = b"checksum ok!\r\n"
                    if fault != "missing-reboot":
                        capture += ota.REBOOT_NOTICE
                    if not predicate(capture):
                        raise TimeoutError("reboot")

                observer.exchange.side_effect = exchange
                observer.receive.side_effect = receive
                if fault:
                    with self.assertRaises(TimeoutError):
                        ota.invoke_flash(self.target, "candidate", self.app, journal, expected_crc=expected_crc)
                else:
                    self.assertEqual(ota.invoke_flash(self.target, "candidate", self.app, journal,
                                                      expected_crc=expected_crc), 1)
                issued = fault != "missing-prompt"
                self.assertEqual(journal.call_count, int(issued))
                self.assertEqual(keyboard.call_count, int(issued))
                if issued:
                    self.assertEqual(keyboard.call_args.args[0][-2:], ["type", "y"])
                self.assertEqual((Path(folder) / "ota-reboot-announced.json").exists(), fault is None)

    def test_candidate_and_restore_require_the_card_crc_before_confirming(self):
        crc = zlib.crc32(self.image)
        for selection, observed in (("candidate", None), ("candidate", crc ^ 1), ("restore", crc)):
            cached = "/extender/recovery/vdp/production.bin" if selection == "restore" else None
            path = cached or ota.staging_path(self.target, selection)
            with (self.subTest(selection=selection, observed=observed), TemporaryDirectory() as folder,
                  patch.object(ota, "open_passive_serial"), patch.object(ota, "Observer") as observer_type,
                  patch.object(ota.subprocess, "run") as keyboard, patch.object(ota.time, "sleep")):
                self.target.out = Path(folder)
                observer = observer_type.return_value
                observer.witness.return_value = b"/ *"
                begin = MagicMock()

                def exchange(_label, command, predicate, _seconds):
                    self.assertEqual(command, f"flash vdp {path}")
                    data = f"/ *{command}\r\n".encode() + ota.FLASH_BANNER + b"\r\n"
                    if observed is not None:
                        data += f"VDP CRC 0x{observed:08X}\r\n".encode()
                    self.assertTrue(predicate(data + ota.FLASH_PROMPT))

                observer.exchange.side_effect = exchange
                if observed == crc:
                    ota.invoke_flash(self.target, selection, self.app, begin,
                                     cached_path=cached, expected_crc=crc)
                    self.assertEqual(bench.bench_process.read(self.target.out / "flash-sd-input.json")["path"], path)
                    begin.assert_called_once()
                    keyboard.assert_called_once()
                else:
                    with self.assertRaisesRegex(RuntimeError, "on-card CRC"):
                        ota.invoke_flash(self.target, selection, self.app, begin,
                                         cached_path=cached, expected_crc=crc)
                    begin.assert_not_called()
                    keyboard.assert_not_called()


class RecoveryCard(TestCase):
    def test_only_initial_deployment_reads_the_full_file(self):
        with TemporaryDirectory() as folder, patch.object(cache, "Client") as client:
            local = Path(folder)
            source = local / "app.bin"
            source.write_bytes(b"new firmware")
            old = "/extender/recovery/vdp/old.bin"
            new = "/extender/recovery/vdp/new.bin"
            old_pin = {"bytes": 11, "sha256": "a" * 64}
            new_pin = {"path": str(source), "bytes": 12, "sha256": sha256(source.read_bytes()).hexdigest()}
            receipts = {old: old_pin | {"method": "uart-readback-byte-compare", "receipt_sha256": "b" * 64}}
            images = {old: old_pin, new: new_pin}
            target = MagicMock()
            target.out = local
            client.return_value.stat_entry.side_effect = [(11, 0), cache.RemoteError(
                "missing", status=6, detail=b"\x04")]

            def transfer(label, mode, path, **args):
                self.assertEqual(path, new)
                if mode == "get":
                    args["destination"].write_bytes(source.read_bytes())

            target.staged_uart.side_effect = transfer
            cache.provision(target, images, receipts)
            self.assertEqual([entry.args[1] for entry in target.staged_uart.call_args_list], ["put", "get"])
            self.assertTrue((local / "old-present.json").exists())
            verified = bench.bench_process.read(local / "new-verified.json")
            self.assertEqual(verified["sha256"], new_pin["sha256"])

            target.out = local / "repeat"
            target.out.mkdir()
            target.staged_uart.reset_mock()
            client.return_value.stat_entry.side_effect = [(11, 0), (12, 0)]
            receipts[new] = verified | {"receipt_sha256": "c" * 64}
            cache.provision(target, images, receipts)
            target.staged_uart.assert_not_called()
            self.assertTrue((target.out / "new-present.json").exists())
            with self.assertRaisesRegex(ValueError, "unrecorded"):
                cache.provision(target, images, receipts, verify_existing=new)


class OffboardStage(TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.report = "/test/demo/result.bin"
        self.app = {"bytes": 1, "sha256": sha256(b"A").hexdigest()}
        self.job = {"id": "demo", "cwd": "/test/demo", "sd_program": "/test/demo/app.bin", "agon": self.app,
                    "results": [self.report], "address": "040000", "success": "REPORT SAVED",
                    "failure": "FAIL", "seconds": 10}
        self.kit = {"transfer": "uart", "namespace": "demo", "preserve": {"/autoexec.txt": "a" * 64},
                    "firmware": {"mainboard": {"method": "agon-flash", "candidate_app": self.app,
                                               "restore_app": self.app}},
                    "fixtures": [self.job]}
        self.job_sha = "123"
        self.manifest = {"job_sha256": self.job_sha, "preserve": self.kit["preserve"],
                         "expected_absent": [self.report],
                         "payloads": {path: self.app for path in (self.job["sd_program"],
                                      "/extender/install/demo/candidate-vdp.bin",
                                      "/extender/install/demo/restore-vdp.bin")}}
        self.verified = {"job_sha256": self.job_sha, "files_verified": 3, "bytes_verified": 3,
                         "preservation_verified": ["/autoexec.txt", ota.FLASH_PATH],
                         "expected_results_absent": [self.report], "writes_synced": True}

    def write_proof(self):
        paths = []
        for name, data in (("manifest.json", self.manifest), ("verification.json", self.verified)):
            payload = json.dumps(data).encode()
            (self.root / name).write_bytes(payload)
            paths.append(sha256(payload).hexdigest())
        return [str(self.root), *paths]

    def test_offboard_proof_requires_pinned_files_and_fresh_reports(self):
        option = self.write_proof()
        self.assertEqual(bench.offboard_proof(self.kit, self.job_sha, option)["files"], 3)
        (self.root / "verification.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "changed"):
            bench.offboard_proof(self.kit, self.job_sha, option)
        self.verified["expected_results_absent"] = []
        with self.assertRaisesRegex(ValueError, "fresh reports"):
            bench.offboard_proof(self.kit, self.job_sha, self.write_proof())
        self.manifest["payloads"].pop(self.job["sd_program"])
        with self.assertRaisesRegex(ValueError, "commissioned files"):
            bench.offboard_proof(self.kit, self.job_sha, self.write_proof())

    def test_production_job_can_admit_offboard_pins(self):
        self.kit["firmware"] = {}
        self.kit["fixtures"][0]["agon"] = self.app | {"path": str(self.root / "app.bin")}
        (self.root / "app.bin").write_bytes(b"A")
        self.manifest["payloads"] = {self.job["sd_program"]: self.app}
        self.verified.update(files_verified=1, bytes_verified=1, preservation_verified=["/autoexec.txt"])
        proof = bench.offboard_proof(self.kit, self.job_sha, self.write_proof())
        runner = bench.Bench.__new__(bench.Bench)
        runner.kit, runner.out, runner.offboard = self.kit, self.root, proof
        runner.stage_uart = MagicMock()
        runner.stage()
        self.assertEqual(bench.bench_process.read(self.root / "offboard-stage.json"), proof)
        runner.stage_uart.assert_not_called()

    def test_ordinary_named_run_can_defer_collection_and_join_same_phase(self):
        self.kit["firmware"] = {}
        runner = bench.Bench.__new__(bench.Bench)
        runner.kit, runner.out, runner.offboard = self.kit, self.root, None
        runner.c = {"ports": ["offline"]}
        runner.validate_ports = runner.keyboard = runner.type_line = MagicMock()
        runner.idle = MagicMock()
        runner.collect_results = MagicMock()
        with patch.object(bench, "open_passive_serial"), patch.object(bench, "Observer") as observer:
            serial = observer.return_value
            serial.change_directory.side_effect = [b"/test/demo *", b"/ *"]
            serial.witness.side_effect = [b"/ *", b"/test/demo *"]
            runner.invoke("run-demo", defer_results=True)
            serial.run.assert_called_once()
            serial.witness.assert_called_with("post-run-witness")
        runner.collect_results.assert_not_called()
        runner.idle.assert_not_called()
        record = bench.bench_process.read(self.root / "deferred-results.json")
        self.assertEqual(record["collection"], "pending-collection")
        self.assertEqual(record["reports"], [self.report])

    def test_named_run_proves_mos_and_leaves_report_on_card(self):
        runner = bench.Bench.__new__(bench.Bench)
        runner.kit, runner.out, runner.config = self.kit, self.root, {"inventory": self.root / "inventory.json"}
        runner.offboard = {"verification_sha256": "a" * 64}
        runner.c = {"ports": ["offline"]}
        runner.validate_ports = runner.idle = runner.keyboard = runner.type_line = MagicMock()
        runner.collect_results = MagicMock()
        bench.bench_process.record(runner.config["inventory"], {})
        with (patch.object(bench, "open_passive_serial"), patch.object(ota, "installed"),
              patch.object(bench, "Observer") as observer):
            serial = observer.return_value
            serial.change_directory.side_effect = [b"/test/demo *", b"/ *"]
            serial.witness.side_effect = [b"/ *", b"/test/demo *"]
            runner.invoke("run-demo")
            serial.run.assert_called_once()
            serial.witness.assert_called_with("post-run-witness")
        runner.collect_results.assert_not_called()
        record = bench.bench_process.read(self.root / "offboard-results.json")
        self.assertEqual(record["collection"], "pending-physical-collection")
        self.assertEqual(record["reports"], [self.report])
        with self.assertRaisesRegex(RuntimeError, "does not admit"):
            runner.start_listener("collect", bench.LISTENER)
