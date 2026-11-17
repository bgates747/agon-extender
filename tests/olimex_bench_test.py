"""Offline regression cases for the discovered CLI and phase boundaries."""

from hashlib import sha256
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from olimex_bench import Bench, preflight
from olimex_cli import CliError, command_result, find_witness
from olimex_flash import check_app0, check_extent


class TestObserver(unittest.TestCase):
    LOAD = "LOAD /test/bench019/BENCH19.bin &040000"
    RUN = "RUN &040000"
    PROMPT = b"/ *"

    def test_root_and_working_directory_witness(self):
        for prompt in (b"/ *", b"/test/bench019 *", b"*"):
            with self.subTest(prompt=prompt):
                capture = b"/ *VDU 65 13 10\r\r\n\rA\r\n" + prompt
                self.assertEqual(find_witness(capture, "VDU 65 13 10", b"A"), prompt)
        self.assertIsNone(find_witness(b"A\r\n/ *", "VDU 65 13 10", b"A"))
        self.assertIsNone(find_witness(b"VDU 65 13 10\r\nB\r\n/ *", "VDU 65 13 10", b"A"))

    def test_fragmented_load_with_echo_and_fresh_prompt(self):
        capture = b"/ *" + self.LOAD.encode() + b"\r\n\r/ *"
        for end in range(len(capture)):
            self.assertFalse(command_result(capture[:end], self.LOAD, self.PROMPT))
        self.assertTrue(command_result(capture, self.LOAD, self.PROMPT))
        self.assertFalse(command_result(b"/ *", self.LOAD, self.PROMPT))

    def test_rejected_load_is_immediate(self):
        capture = self.LOAD.encode() + b"\r\n\rFile not found\r"
        with self.assertRaisesRegex(CliError, "File not found"):
            command_result(capture, self.LOAD, self.PROMPT)

    def result(self, captured):
        return command_result(captured, self.RUN, self.PROMPT, success=b"BENCH019 PASS",
                              failure=b"BENCH019 FAIL")

    def test_fixture_result_with_returned_mos_error(self):
        capture = b"RUN &040000\r\r\nBENCH019 FAIL; see result.txt\r\nError accessing SD card\r\n/ *"
        with self.assertRaisesRegex(CliError, "BENCH019 FAIL; see result.txt"):
            self.result(capture)
        with self.assertRaisesRegex(CliError, "Error accessing SD card"):
            self.result(capture.replace(b"BENCH019 FAIL; see result.txt\r\n", b""))

    def test_stale_marker_echo_and_success(self):
        self.assertFalse(self.result(b"BENCH019 PASS\r\n/ *"))
        self.assertFalse(self.result(b"RUN &040000\r\nBENCH019 PASS\r\n"))
        self.assertTrue(self.result(b"/ *RUN &040000\r\n\rBENCH019 PASS\r\n/ *"))


class TestOta(unittest.TestCase):
    def selector(self, sequence, state):
        crc = zlib.crc32(struct.pack("<I", sequence), 0xffffffff)
        record = struct.pack("<I20xII", sequence, state, crc)
        return record + b"\xff" * (8192 - len(record))

    def test_commissioned_app0_only(self):
        check_app0(b"\xff" * 8192)
        check_app0(self.selector(1, 2))
        for data in (self.selector(2, 2), self.selector(1, 1), self.selector(1, 4), b"\0" * 8192):
            with self.subTest(head=data[:4]), self.assertRaises(ValueError):
                check_app0(data)

    def test_slot_bounds(self):
        image = b"\0" * 4096
        spec = {"offset": "0x20000", "partition_bytes": 0x700000, "write_bytes": len(image)}
        check_extent("p4", spec, image)
        with self.assertRaises(ValueError):
            check_extent("p4", dict(spec, offset="0x0"), image)


class TestBench(unittest.TestCase):
    def test_plain_production_plan_and_staging(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            artifact = folder / "demo.bin"
            artifact.write_bytes(b"known")
            kit = {"schema": 1, "namespace": "demo", "firmware": {},
                   "fixture": {"agon": {"path": str(artifact), "bytes": 5,
                                        "sha256": sha256(b"known").hexdigest()},
                               "sd_program": "/test/demo/demo.bin", "sd_result": "/test/demo/results/out",
                               "address": "040000", "seconds": 30, "success": "PASS", "failure": "FAIL"},
                   "preserve": {"/autoexec.txt": "0" * 64, "/emos/sdserve.bin": "0" * 64}}
            self.assertEqual(preflight(kit), ["stage", "run", "handback"])
            bench = Bench.__new__(Bench)
            bench.out = folder
            bench.kit = kit
            client = MagicMock()
            from sdcard import RemoteError
            client.stat_entry.side_effect = RemoteError("absent", status=6, detail=b"\x04")
            client.download.return_value = artifact.read_bytes()
            with patch.object(bench, "listener", side_effect=lambda name, command, callback: callback(client)), \
                    patch.object(bench, "invoke") as invoke, patch.object(bench, "firmware") as firmware:
                bench.stage()
                firmware.assert_not_called()
                invoke.assert_not_called()
            client.make_directory.assert_any_call("/test/demo/results", parents=True)
            client.upload.assert_called_once_with("/test/demo/demo.bin", b"known", activate=True, fast=True)

    def test_keyboard_cancel_keeps_nonzero_session_id(self):
        bench = Bench.__new__(Bench)
        bench.url = "http://example.invalid"
        result = dict(ready=True, physical_neutral=True, pending=0, held=0, session=25, reason=1)
        with patch("olimex_bench.status", return_value=result):
            self.assertEqual(bench.keyboard(), result)
            result["reason"] = 0
            with self.assertRaises(RuntimeError):
                bench.keyboard()


if __name__ == "__main__":
    unittest.main()
