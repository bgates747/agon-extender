"""Report lifecycle tests using local files and a simulated Olimex listener."""

import argparse
from contextlib import contextmanager
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import bench_process
import olimex_bench
import olimex_reports as reports
from olimex_cli import Observer
from sdcard import Client, RemoteError


TOKEN = "0123456789abcdef"
A = "/test/demo/pose/direct/POSE.BIN"
B = "/test/demo/pose/direct/OTHER.BIN"
HEADER = f"OLXR1 {TOKEN}\n".encode()


def save_line(path, length):
    return f"OLXR1 {TOKEN} {Path(path).name} {length} {length} saved 0 0"


class Card:
    def __init__(self):
        self.files = {}
        self.removals = []
        self.break_delete = None

    def stat_entry(self, path):
        for filename, payload in self.files.items():
            if filename.lower() == path.lower():
                return len(payload), 32
        raise RemoteError("File absent", status=6, detail=b"\x04")

    def remove_file(self, path):
        if self.break_delete == "before":
            raise TimeoutError("Lost link before delete")
        self.removals.append(path)
        del self.files[path]
        if self.break_delete == "after":
            raise TimeoutError("Lost link after delete")


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.origin = self.root / "run-direct"
        self.origin.mkdir()
        trace = self.origin / "results/vdp-usb.bin"
        trace.parent.mkdir()
        trace.write_bytes(b"RUN transcript\n")
        self.bench = Mock()
        self.bench.out = self.origin
        self.bench.kit = {"report_lifecycle": {"mode": "token-v1"}}
        self.listener = {"online": False, "boot": 1}
        self.bench.get.side_effect = lambda path: self.listener.copy()
        self.bench.start_listener.side_effect = self.open_listener
        self.bench.exit_staged_listener.side_effect = lambda label: self.listener.update(online=False)
        self.lifecycle = reports.Lifecycle(self.bench, "owner", {"sha256": "job"}, agon_boot=lambda: 4)
        self.fence = {"lease": "owner", "firmware": "production", "agon_boot": 4, "p4_boot": 3}
        self.lifecycle.fence = Mock(side_effect=lambda: self.fence.copy())
        self.lifecycle.run_validator = Mock(return_value={"accepted": True, "reason": "timing agreed"})
        self.card = Card()
        self.lifecycle.metadata = self.metadata
        self.lifecycle.download = Mock(side_effect=self.download)
        self.attempt = {"token": TOKEN, "mode": "token-v1", "binding": {"sha256": "job"},
                        "fence": self.fence.copy(), "paths": [A]}
        self.witness = {"outcome": "passed", "output": [save_line(A, len(HEADER) + 3)],
                        "transcript_bytes": trace.stat().st_size, "transcript_sha256": reports.digest(trace)}
        self.card.files[A] = HEADER + b"abc"

    def open_listener(self, *args):
        self.listener["online"] = True
        self.listener["boot"] += 1

    @contextmanager
    def metadata(self, label):
        yield self.card

    def download(self, journal, remote, archive):
        archive.write_bytes(self.card.files[remote])
        return {"size": archive.stat().st_size, "bytes": archive.stat().st_size, "payload_carrier": "parlio"}

    def collect(self):
        return self.lifecycle.collect(self.origin, {"results": self.attempt["paths"]}, self.attempt, self.witness)

    def resume(self):
        resumes = len(list(self.root.glob("resume-*"))) + 1
        self.bench.out = self.root / f"resume-{resumes}"
        self.bench.out.mkdir()
        return self.collect()

    def test_rejected_timing_archives_bytes_and_reason_before_exact_removal(self):
        self.lifecycle.run_validator.return_value = {"accepted": False, "reason": "invalid VBlank interval"}
        remove = self.card.remove_file

        def check(path):
            entry = self.origin / "report-00"
            self.assertEqual((entry / "POSE.BIN").read_bytes(), HEADER + b"abc")
            self.assertEqual(bench_process.read(entry / "validation.json")["reason"], "invalid VBlank interval")
            self.assertTrue((entry / "delete-intent.json").exists())
            remove(path)

        self.card.remove_file = check
        self.assertFalse(self.collect())
        self.assertEqual(self.card.removals, [A])
        self.assertFalse(self.listener["online"])

    def test_stale_same_size_case_alias_blocks_before_attempt(self):
        self.card.files[A.lower()] = self.card.files.pop(A)
        job = {"results": [A], "sd_program": "/test/demo/pose/direct/demo.bin", "agon": {"sha256": "demo"}}
        with self.assertRaisesRegex(RuntimeError, "Outstanding SD report"):
            self.lifecycle.prepare("run-direct", job, {"binding": self.attempt["binding"], "fence": self.fence})
        self.assertFalse((self.origin / "report-attempt.json").exists())
        self.assertEqual(self.card.removals, [])

    def test_wrong_token_with_correct_filename_size_and_serial_is_retained(self):
        self.card.files[A] = self.card.files[A].replace(TOKEN.encode(), b"fedcba9876543210")
        self.assertFalse(self.collect())
        self.assertEqual(self.card.removals, [])
        self.lifecycle.run_validator.assert_not_called()

    def test_report_save_and_close_have_independent_status(self):
        self.witness["output"][0] = f"OLXR1 {TOKEN} POSE.BIN 26 26 close 0 1"
        self.assertFalse(self.collect())
        self.assertEqual(self.card.removals, [])
        self.assertEqual(bench_process.read(self.origin / "report-00/validation.json")["saved"], "failed")

    def test_resume_after_lost_collection_continues_multi_file(self):
        self.card.files[B] = HEADER + b"def"
        self.attempt["paths"].append(B)
        self.witness["output"].append(save_line(B, len(self.card.files[B])))

        def interrupted(journal, remote, archive):
            if remote == B:
                raise TimeoutError("Lost retrieval")
            return self.download(journal, remote, archive)

        self.lifecycle.download.side_effect = interrupted
        with self.assertRaises(TimeoutError):
            self.collect()
        self.assertEqual(self.card.removals, [A])
        self.assertIn(B, self.card.files)
        self.lifecycle.download.reset_mock(side_effect=True)
        self.lifecycle.download.side_effect = self.download
        self.assertTrue(self.resume())
        self.assertEqual(self.card.removals, [A, B])
        self.assertEqual(self.lifecycle.download.call_count, 1)

    def test_resume_after_delete_ack_loss_never_downloads_or_deletes_again(self):
        self.card.break_delete = "after"
        with self.assertRaises(TimeoutError):
            self.collect()
        self.assertTrue(self.resume())
        self.assertEqual(self.lifecycle.download.call_count, 1)
        self.assertEqual(self.card.removals, [A])

    def test_resume_before_delete_compares_exact_bytes(self):
        self.card.break_delete = "before"
        with self.assertRaises(TimeoutError):
            self.collect()
        self.card.break_delete = None
        self.assertTrue(self.resume())
        self.assertEqual(self.lifecycle.download.call_count, 2)
        self.assertEqual(self.card.removals, [A])

    def test_resume_leaves_changed_same_size_path_after_interrupted_cleanup(self):
        self.card.break_delete = "before"
        with self.assertRaises(TimeoutError):
            self.collect()
        self.card.files[A] = HEADER + b"xyz"
        with self.assertRaisesRegex(RuntimeError, "differs from the archived bytes"):
            self.resume()
        self.assertEqual(self.card.removals, [])

    def test_reset_after_joined_run_allows_archive_only(self):
        self.fence["agon_boot"] += 1
        self.assertFalse(self.collect())
        self.assertTrue((self.origin / "report-00/archive.json").exists())
        self.assertEqual(self.card.removals, [])

    def test_changed_lease_refuses_before_listener(self):
        self.fence["lease"] = "different"
        with self.assertRaisesRegex(RuntimeError, "custody"):
            self.collect()
        self.bench.start_listener.assert_not_called()

    def test_archive_publication_interruption_leaves_sd_file(self):
        publish = reports.publish

        def interrupted(path, value):
            if Path(path).name == "archive.json":
                raise OSError("Simulated Pi archive failure")
            publish(path, value)

        with patch.object(reports, "publish", side_effect=interrupted):
            with self.assertRaisesRegex(OSError, "Pi archive failure"):
                self.collect()
        self.assertEqual(self.card.removals, [])
        self.assertIn(A, self.card.files)

    def test_unbound_online_listener_refused(self):
        self.open_listener()
        with self.assertRaisesRegex(RuntimeError, "unbound listener"):
            self.collect()
        self.lifecycle.download.assert_not_called()

    def test_missing_first_report_does_not_hide_other_report(self):
        del self.card.files[A]
        self.card.files[B] = HEADER + b"def"
        self.attempt["paths"].append(B)
        self.witness["output"].append(save_line(B, len(self.card.files[B])))
        self.assertFalse(self.collect())
        self.assertEqual(self.card.removals, [B])
        self.assertTrue((self.origin / "report-unavailable-00.json").is_file())

    def test_validator_infrastructure_failure_preserves_report(self):
        self.lifecycle.run_validator.side_effect = ValueError("Invalid host validator verdict")
        with self.assertRaisesRegex(ValueError, "Invalid host validator verdict"):
            self.collect()
        self.assertTrue((self.origin / "report-00/archive.json").is_file())
        self.assertEqual(self.card.removals, [])

    def test_legacy_mode_uses_fresh_path_and_witness_or_retains(self):
        self.attempt["mode"] = "legacy"
        self.card.files[A] = b"the old payload is unchanged"
        self.witness["output"] = ["PASS"]
        self.assertTrue(self.collect())
        self.assertEqual(self.card.removals, [A])
        self.assertEqual(bench_process.read(self.origin / "report-00/validation.json")["saved"], "unreported")

    def test_staged_get_resume_uses_the_retained_job_without_post(self):
        file = self.root / "REPORT.BIN"
        file.write_bytes(self.card.files[A])
        receipt = {"bytes": file.stat().st_size, "size": file.stat().st_size, "payload_carrier": "parlio"}
        with patch.object(reports, "StagedClient") as bridge:
            staged = bridge.return_value
            staged.state = {"job": {"remote": A, "destination": str(file), "operation": "get",
                                    "require_parallel": True}}
            staged.resume.return_value = receipt
            self.assertEqual(reports.Lifecycle.download(self.lifecycle, self.root / "transfer.json", A, file),
                             receipt)
            staged.resume.assert_called_once_with()
            staged.begin.assert_not_called()
            staged.close.assert_called_once_with()


class Bindings(unittest.TestCase):
    def test_same_owner_reacquires_after_gap_changes_lease(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scheduler.json"
            path.write_text('{"active":"owner"}')
            prior = reports.lease(path, "owner")
            amended = path.with_name("amended")
            amended.write_text('{"active":"owner"}')
            amended.replace(path)
            self.assertNotEqual(prior, reports.lease(path, "owner"))
            with self.assertRaisesRegex(RuntimeError, "custody"):
                reports.lease(path, "other")

    def test_no_delete_rpc_for_directory(self):
        client = object.__new__(Client)
        client.directory_capability = Mock()
        client.rpc = Mock()
        client.stat_entry = Mock(return_value=(0, 16))
        with self.assertRaisesRegex(RemoteError, "refuses a directory"):
            client.remove_file(A)
        self.assertFalse(any(call.args[1].startswith(b"\x00") for call in client.rpc.call_args_list))

    def test_report_observer_waits_for_command_and_prompt_even_on_failure(self):
        command = f"RUN &040000 {TOKEN}"
        raw = f"/test/demo *{command}\r\n{save_line(A, 26)}\r\nFAIL BOUNDS\r\n/test/demo *".encode()
        reader = Mock(in_waiting=0)
        reader.read.side_effect = [raw[:-1], raw[-1:]]
        dispatch = Mock()
        observed = Observer(reader, io.BytesIO(), dispatch).run_report(command, b"/test/demo *", "PASS", "FAIL", 1)
        self.assertEqual(observed, {"outcome": "failed", "output": [save_line(A, 26), "FAIL BOUNDS"]})
        dispatch.assert_called_once_with("run", command)
        self.assertEqual(reader.read.call_count, 2)

    def test_bound_report_history_rejects_live_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            phase = "run-direct"
            folder = root / phase
            folder.mkdir()
            args = argparse.Namespace(out=root, job=Path("job"), config=Path("config"), sha256="pin")
            argv = olimex_bench.child_argv(args, phase)
            binding = {"sha256": "binding"}
            owner = {"owner": "owner", "lease": "chat:owner", "phase": phase}
            bench_process.record(folder / "supervisor-started.json", owner | {"argv": argv})
            bench_process.record(folder / "operation-binding.json", binding)
            bench_process.record(folder / "blocked.json", owner)
            start = bench_process.identity(os.getpid()) | {"pgid": os.getpid(), "argv": argv}
            bench_process.record(folder / "child-started.json", start)
            bench_process.record(folder / "child-terminal.json",
                                 {"pid": os.getpid(), "returncode": 1, "direct_child_joined": False,
                                  "group_terminal": False, "live_group_members": [start]})
            with self.assertRaisesRegex(ValueError, "not joined"):
                olimex_bench.verify_bound_phase(args, phase, "owner", binding)
            with self.assertRaisesRegex(RuntimeError, "Original operator"):
                olimex_bench.verify_bound_phase(args, phase, "different", binding)

    def test_stage_reuse_skips_upload_with_matching_destination_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bench = object.__new__(olimex_bench.Bench)
            bench.out, bench.url, bench.kit = root, "http://mock", {"schema": 3}
            bench.reuse_stage = {"fence": {}, "source": "original"}
            bench.get = Mock(return_value={"parallel_required_supported": True,
                                           "parallel_get_required_supported": True})
            bench.start_listener = Mock()
            bench.exit_staged_listener = Mock()
            source = "/test/demo/pose/direct/demo.bin"
            with patch.object(olimex_bench, "Client") as client, patch.object(olimex_bench, "StagedClient") as staged:
                client.return_value.rpc.return_value = b"\0" * 6 + b"\x80\x01"
                bench.stage_parallel({source: b"abc"}, [A],
                                     lambda session, path: (3, 32) if path == source else None)
                staged.assert_not_called()
                client.return_value.make_directory.assert_not_called()
            bench.exit_staged_listener.assert_called_once_with("stage")

    def test_resume_worker_never_invokes_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            bench = object.__new__(olimex_bench.Bench)
            bench.config = {"operation_lock": Path(directory) / "lock"}
            bench.reports = Mock()
            bench.validate_ports = Mock()
            bench.invoke = Mock()
            bench.finish_reports = Mock()
            record = (Path(directory), {"id": "direct"}, {"token": TOKEN}, {"outcome": "failed"})
            bench.perform("resume-run-direct-01", resume_reports=record)
            bench.finish_reports.assert_called_once_with(*record)
            bench.invoke.assert_not_called()

    def test_preflight_rejects_case_folded_result_alias(self):
        with self.assertRaisesRegex(ValueError, "Duplicate fixture or result path"):
            olimex_bench.validate_targets({}, [A, A.lower()])

    def test_invoke_dispatches_token_once_and_binds_the_returned_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            phase = root / "run-direct"
            phase.mkdir()
            stage = root / "stage"
            stage.mkdir()
            bench_process.record(stage / "report-stage.json", {"binding": "stage"})
            bench = object.__new__(olimex_bench.Bench)
            bench.out = phase
            cwd = str(Path(A).parent)
            program = f"{cwd}/PROG.BIN"
            job = {"id": "direct", "cwd": cwd, "sd_program": program, "address": "040000",
                   "results": [A], "success": "PASS", "failure": "FAIL", "seconds": 1}
            bench.kit = {"fixtures": [job]}
            bench.c = {"ports": ["mock"]}
            bench.validate_ports = Mock()
            bench.idle = Mock()
            bench.keyboard = Mock()
            bench.reports = Mock()
            bench.reports.prepare.return_value = {"token": TOKEN, "mode": "token-v1", "fence": "same"}
            bench.reports.fence.return_value = "same"
            bench.finish_reports = Mock()
            cursor = b"/ *"
            replies = []
            dispatched = []
            reader = Mock(in_waiting=0)
            reader.read.side_effect = lambda size: replies.pop(0)

            def dispatch(label, command):
                nonlocal cursor
                dispatched.append(command)
                if label == "mirror-on":
                    return
                echo = cursor + command.encode() + b"\r\n"
                if label == "witness":
                    echo += bytes(map(int, command.split()[1:]))
                if label in ("enter-cwd", "restore-cwd"):
                    cursor = command[3:].encode() + b" *"
                if label == "run":
                    echo += save_line(A, 26).encode() + b"\r\nPASS\r\n"
                replies.append(echo + cursor)

            @contextmanager
            def serial(port, timeout):
                yield reader

            bench.type_line = dispatch
            with patch.object(olimex_bench, "open_passive_serial", serial):
                bench.invoke("run-direct")
            command = f"RUN &040000 {TOKEN}"
            self.assertEqual([value for value in dispatched if value.startswith("RUN")], [command])
            witness = bench_process.read(phase / "report-run.json")
            self.assertEqual(witness["command"], command)
            self.assertEqual(witness["output"], [save_line(A, 26), "PASS"])
            trace = phase / "results/vdp-usb.bin"
            self.assertGreater(trace.stat().st_size, witness["transcript_bytes"])
            self.assertEqual(reports.run_digest(trace, witness["transcript_bytes"]), witness["transcript_sha256"])
            bench.finish_reports.assert_called_once()


if __name__ == "__main__":
    unittest.main()
