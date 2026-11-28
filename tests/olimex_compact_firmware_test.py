"""Host-only tests for compact verification of the Olimex P4 and EMOS."""

from contextlib import nullcontext
from hashlib import md5, sha256
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import zlib


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from olimex_flash import FLASH_BANNER, FLASH_PROMPT, flash_mos, mos_write_success
from olimex_p4_app import replace, verify_write_log


class P4Proof(unittest.TestCase):
    def test_write_log_requires_one_range_and_its_result(self):
        summary = b"Wrote 4096 bytes (24 compressed) at 0x00020000 in 1.0 seconds."
        verified = b"Hash of data verified."
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "write.log"
            log.write_bytes(b"\n".join((b"esptool v5.1.0", summary, verified)))
            verify_write_log(log, 0x20000, 4096)
            for data in (summary,
                         summary.replace(b"4096", b"8192") + b"\n" + verified,
                         summary.replace(b"00020000", b"00010000") + b"\n" + verified,
                         b"\n".join((verified, summary)),
                         b"\n".join((summary, verified, summary))):
                with self.subTest(data=data):
                    log.write_bytes(data)
                    with self.assertRaisesRegex(RuntimeError, "exact application extent"):
                        verify_write_log(log, 0x20000, 4096)

    def test_retry_checks_entry_without_payload_readback(self):
        image = b"X" * 4096
        spec = {"offset": "0x20000", "partition_bytes": 0x700000, "write_bytes": len(image)}
        table = b"table"
        calls = []
        begin = MagicMock()

        def stock(out, label, port, before, *args):
            calls.append((label, args))
            if label == "partition":
                args[-1].write_bytes(table.ljust(4096, b"\xff"))
            elif label == "selector":
                args[-1].write_bytes(b"\xff" * 8192)
            elif label == "entry":
                self.assertEqual(args[-1].read_bytes(), b"Y" * 4096)
            elif label == "write":
                (out / "write.log").write_bytes(
                    b"Wrote 4096 bytes at 0x00020000 in 0.2 seconds.\nHash of data verified.\n")
            else:
                self.fail(f"Unexpected USB command: {args}")

        with tempfile.TemporaryDirectory() as tmp:
            bench = MagicMock(out=Path(tmp))
            bench.c = {"ports": ["agon", "p4"]}
            with (patch("olimex_p4_app.stock", stock), patch("olimex_p4_app.hold_agon", nullcontext),
                  patch("olimex_p4_app.reset_until_pads_release") as restart,
                  patch("olimex_p4_app.wait_boot", return_value={"boot": 42})):
                result = replace(bench, spec, image, table, 41, begin, required_entry=b"Y" * 4096)
            begin.assert_called_once_with()
            restart.assert_called_once_with(bench)
            proof = json.loads(result.read_text())
            self.assertEqual(proof["write_sha256"], sha256(image).hexdigest())
            self.assertEqual(proof["write_md5"], md5(image, usedforsecurity=False).hexdigest())
            self.assertFalse((bench.out / "readback.bin").exists())
        self.assertEqual([label for label, _ in calls], ["partition", "selector", "entry", "write"])
        self.assertEqual(calls[2][1][:-1], ("verify-flash", "0x20000"))


class MosProof(unittest.TestCase):
    # FLASH v1.9 update_mos calculates CRC over the number of bytes in the
    # input, from address 0. The proof requires the full 128 1024-byte pages.
    SUCCESS = (
        b"\x0c" + FLASH_BANNER + b"\n\r\n\rProgramming MOS firmware to ez80 flash...\r\n"
        b"\rWriting flash page 127/128\rWriting flash page 128/128\r\n"
        b"Checking CRC... OK\r\n\r\n\r\nDone\r\n\r\nSystem reset in 3...2...1..."
    )

    def test_crc_pass_needs_last_page_and_reboot(self):
        self.assertTrue(mos_write_success(self.SUCCESS))
        self.assertFalse(mos_write_success(self.SUCCESS.replace(b"128/128", b"127/128")))
        self.assertFalse(mos_write_success(self.SUCCESS.replace(b"CRC... OK", b"CRC... ERROR")))
        self.assertFalse(mos_write_success(self.SUCCESS[:-4]))
        with self.assertRaisesRegex(RuntimeError, "reported an update failure"):
            mos_write_success(b"Checking CRC... ERROR\r\nMultiple errors occured during flash write.")

    def flash(self, *, wrong_crc=False, missing_write_proof=False):
        image = b"X" * 0x20000
        file = "/extender/install/emos-test/candidate.bin"
        events = []
        begin = lambda: events.append("inventory pending")
        with tempfile.TemporaryDirectory() as tmp:
            target = MagicMock(out=Path(tmp), url="http://p4.test")
            target.c = {"ports": ["agon", "p4"]}
            target.keyboard.return_value = {"boot": 41}
            reader = MagicMock(in_waiting=0)
            crc = zlib.crc32(image) ^ wrong_crc
            reader.read.side_effect = [
                b"/ *VDU 65 66 67 68 69 70 13 10\r\nABCDEF\r\n/ *",
                b"/ *FLASH mos " + file.encode("ascii") + b"\r\n\x0c" + FLASH_BANNER + b"\n\r\n\r"
                + f"MOS CRC 0x{crc:08X}\r\n\r\n".encode("ascii") + FLASH_PROMPT,
                b"Multiple errors occured during flash write." if missing_write_proof else self.SUCCESS,
            ]
            with (
                patch("olimex_flash.open_passive_serial", return_value=nullcontext(reader)),
                patch("olimex_cli.secrets.token_hex", return_value="abcdef"),
                patch("olimex_flash.subprocess.run", side_effect=lambda *a, **k: events.append("confirm")),
                patch("olimex_flash.wait_boot", return_value={"boot": 42}) as boot,
            ):
                if wrong_crc or missing_write_proof:
                    message = "pinned EMOS input CRC" if wrong_crc else "reported an update failure"
                    with self.assertRaisesRegex(RuntimeError, message):
                        flash_mos(target, file, image, begin)
                    boot.assert_not_called()
                    target.verify_mos.assert_not_called()
                    self.assertFalse((target.out / "write-verified.json").exists())
                    self.assertEqual(events, [] if wrong_crc else ["inventory pending", "confirm"])
                    return
                receipt = flash_mos(target, file, image, begin)
                boot.assert_called_once_with(target.url, 41, 100)
                target.verify_mos.assert_called_once_with("after-flash-mos")
                self.assertEqual(events, ["inventory pending", "confirm"])
                proof = json.loads(receipt.read_text())
                self.assertEqual(proof["crc32"], f"{crc:08X}")
                self.assertEqual(proof["write_sha256"], sha256(image).hexdigest())
                self.assertFalse((target.out / "readback.bin").exists())

    def test_command_correlated_crc_rom_and_fresh_mos(self):
        self.flash()

    def test_bad_input_crc_does_not_confirm_write(self):
        self.flash(wrong_crc=True)

    def test_post_write_error_does_not_become_boot_proof(self):
        self.flash(missing_write_proof=True)

    def test_short_rom_never_touches_hardware(self):
        target = MagicMock()
        with self.assertRaisesRegex(ValueError, "full 128 KiB"):
            flash_mos(target, "short.bin", b"X", MagicMock())
        target.own.assert_not_called()


if __name__ == "__main__":
    unittest.main()
