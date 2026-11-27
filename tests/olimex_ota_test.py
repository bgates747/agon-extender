"""Host checks for the standard runner's UART and ordinary FLASH paths."""

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, call, patch
import struct
import sys
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import olimex_bench as bench
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
        self.runner.start_listener = MagicMock()
        with patch.object(bench, "Client") as client:
            client.return_value.rpc.return_value = struct.pack("<IHH", 1, 212, 0x1ff)
            operation = MagicMock()
            with self.assertRaisesRegex(RuntimeError, "parallel payload capabilities"):
                self.runner.listener("stage", bench.LISTENER, operation)
            operation.assert_not_called()
            client.return_value.download.assert_not_called()
            client.return_value.lock.close.assert_called_once()

    def test_stage_collect_and_handback_use_only_direct_uart(self):
        self.runner.start_listener = MagicMock()
        self.runner.validate_ports = MagicMock()
        inventory = self.runner.out / "inventory.json"
        bench.bench_process.record(inventory, {})
        self.runner.config = {"inventory": inventory}
        self.runner.kit["firmware"] = {}
        staged = "/test/demo/app.bin"
        report = "/test/demo/result.bin"
        with patch.object(bench, "Client") as client, patch.object(bench, "StagedClient") as parallel:
            direct = client.return_value
            direct.rpc.return_value = struct.pack("<IHH", 1, 212, 0x7f)
            direct.upload.return_value = 7
            direct.download.return_value = b"report"
            self.runner.stage_uart({staged: b"app"}, [report], lambda client, path: None)
            self.runner.collect_results({"results": [report]}, self.runner.out, True)
            self.runner.handback()
            self.assertEqual(self.runner.start_listener.call_args_list, [
                call("stage", bench.LISTENER), call("collect", bench.LISTENER),
                call("cli", bench.LISTENER),
            ])
            direct.upload.assert_called_once_with(staged, b"app", activate=True, fast=True)
            direct.download.assert_called_once_with(report)
            parallel.assert_not_called()
        receipt = bench.bench_process.read(self.runner.out / "stage-file-00.receipt.json")
        self.assertEqual((receipt["payload_carrier"], receipt["activated"]), ("uart", True))
        self.assertEqual((self.runner.out / "result.bin").read_bytes(), b"report")


class FlashPath(TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.target = MagicMock()
        self.target.out = self.root
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

                def exchange(_label, command, predicate, _seconds):
                    capture = b"/ *" + command.encode() + b"\r\n\x0c" + ota.FLASH_BANNER + b"\r\n"
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
                        ota.invoke_flash(self.target, "candidate", self.app, journal)
                else:
                    self.assertEqual(ota.invoke_flash(self.target, "candidate", self.app, journal), 1)
                issued = fault != "missing-prompt"
                self.assertEqual(journal.call_count, int(issued))
                self.assertEqual(keyboard.call_count, int(issued))
                if issued:
                    self.assertEqual(keyboard.call_args.args[0][-2:], ["type", "y"])
                self.assertEqual((Path(folder) / "ota-reboot-announced.json").exists(), fault is None)
