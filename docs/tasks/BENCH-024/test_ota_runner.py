from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import ota_runner as runner
from ota_receipt import SNAPSHOT, Snapshot, verify_candidate_boot, verify_selection, verify_write


BUILD_A, BUILD_B = "12" * 16, "23" * 16
IMAGE = bytes([3, 1, 4, 1, 5])
IDLE = Snapshot(0, 0, 0, 0x1234, 0, 0, 255, 0, 0, 0, "00" * 32, BUILD_A)
VERIFIED = replace(IDLE, state=3, transaction=123, target=1, digest_valid=1,
                   accepted=len(IMAGE), length=len(IMAGE), digest=sha256(IMAGE).hexdigest())
SELECTED = replace(VERIFIED, state=4, configured=1)
BOOTED = replace(IDLE, boot=0x5678, running=1, configured=1, build=BUILD_B)


def encode(snapshot):
    values = vars(snapshot)
    words = [values[k] for k in values if k not in ("digest", "build")]
    return SNAPSHOT.pack(1, *words, bytes.fromhex(snapshot.digest),
                         bytes.fromhex(snapshot.build), bytes(4))


class Receipts(unittest.TestCase):
    def test_write_preserves_current_boot_build_and_selector(self):
        self.assertEqual(verify_write(encode(IDLE) + encode(VERIFIED), 123, 0, BUILD_A, IMAGE),
                         (IDLE, VERIFIED))

    def test_writer_rejects_truncated_stale_wrong_slot_and_hash_results(self):
        for change in [
            {"transaction": 122}, {"target": 0}, {"running": 1}, {"configured": 1},
            {"accepted": len(IMAGE) - 1}, {"length": len(IMAGE) - 1}, {"boot": 0x5678},
            {"build": BUILD_B}, {"digest_valid": 0}, {"digest": "00" * 32}, {"error": 10},
        ]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                verify_write(encode(IDLE) + encode(replace(VERIFIED, **change)),
                             123, 0, BUILD_A, IMAGE)
        with self.assertRaises(ValueError):
            verify_write(encode(VERIFIED), 123, 0, BUILD_A, IMAGE)

    def test_selection_requires_the_identical_verified_transaction(self):
        self.assertEqual(verify_selection(encode(VERIFIED) + encode(SELECTED), VERIFIED),
                         (VERIFIED, SELECTED))
        for change in [{"boot": 0x5678}, {"configured": 0}, {"target": 0}, {"transaction": 122}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                verify_selection(encode(VERIFIED) + encode(replace(SELECTED, **change)), VERIFIED)

    def test_candidate_boot_requires_new_nonce_and_exact_build(self):
        self.assertEqual(verify_candidate_boot(encode(BOOTED), SELECTED, BUILD_B), BOOTED)
        with self.assertRaises(ValueError):
            verify_candidate_boot(encode(BOOTED), SELECTED, BUILD_A)
        with self.assertRaises(ValueError):
            verify_candidate_boot(encode(replace(BOOTED, boot=SELECTED.boot)), SELECTED, BUILD_B)


class Phases(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bench = Mock()
        inventory = self.root / "inventory.json"
        inventory.write_text('{"components":{"native_vdp_sha256":"bootstrap"}}')
        self.bench.config = {"inventory": inventory}
        self.bench.keyboard.return_value = {"boot": 8}
        self.bench.image.return_value = IMAGE
        self.bench.kit = {
            "bootstrap_app0": {"sha256": "bootstrap"},
            "legs": {"candidate": {
                "source_build": BUILD_A, "transaction": "0000007b",
                "image": {"sha256": sha256(IMAGE).hexdigest()},
            }, "production": {"source_build": BUILD_B}},
        }

    def phase_directory(self, phase):
        self.bench.out = self.root / phase
        self.bench.out.mkdir()
        return self.bench.out

    def saved(self, phase, data):
        path = self.root / phase / "results"
        path.mkdir(parents=True)
        (path / f"{phase}.dat").write_bytes(data)

    @patch.object(runner, "reboot_pair")
    def test_write_and_select_are_distinct_non_rebooting_phases(self, reboot):
        folder = self.phase_directory("write-candidate")
        self.bench.run_flash.return_value = encode(IDLE) + encode(VERIFIED)
        runner.perform(self.bench, "write-candidate")
        self.assertEqual(json.loads((folder / "vdplet.json").read_text())["after"]["state"], 3)
        self.bench.run_flash.assert_called_once_with("write-candidate")
        self.saved("write-candidate", encode(IDLE) + encode(VERIFIED))

        self.phase_directory("select-candidate")
        self.bench.run_flash.return_value = encode(VERIFIED) + encode(SELECTED)
        runner.perform(self.bench, "select-candidate")
        self.bench.run_flash.assert_called_with("select-candidate")
        reboot.assert_not_called()

    def test_batch_launches_listener_after_the_one_explicit_flash_command(self):
        probe = runner.UpdateBench.__new__(runner.UpdateBench)
        probe.kit = self.bench.kit
        probe.kit["legs"]["candidate"]["image"]["bytes"] = len(IMAGE)
        command, followup = probe.batch("write-candidate").decode().splitlines()
        self.assertEqual(command, f"RUN &0B0000 vdp-stage candidate.bin write-candidate.dat "
                                  f"0000007b 1 {len(IMAGE)} {sha256(IMAGE).hexdigest()}")
        self.assertEqual(followup, runner.PARALLEL_LISTENER)

    @patch.object(runner, "open_passive_serial")
    @patch.object(runner, "Observer")
    def test_printer_mirror_is_off_during_command_and_result_collection(self, observer, serial):
        probe = runner.UpdateBench.__new__(runner.UpdateBench)
        probe.out = self.phase_directory("write-candidate")
        probe.install_dir = "/extender/install/b024-example"
        probe.c = {"ports": ["mock"]}
        events = []
        probe.validate_ports = Mock()
        probe.idle = Mock()
        probe.keyboard = Mock()
        probe.get = Mock(return_value={"online": True})
        probe.type_line = lambda kind, _: events.append(kind)
        obs = observer.return_value
        obs.witness.return_value = b"/extender/install/b024-example *"
        obs.change_directory.return_value = obs.witness.return_value
        obs.mirror_off.side_effect = lambda *args: events.append("mirror-off")

        def collect(job, output, named, *, listener_online):
            self.assertTrue(named and listener_online)
            self.assertTrue(job["results"][0].endswith(".log"))
            events.append("collect")
            (output / "write-candidate.dat").write_bytes(encode(IDLE) + encode(VERIFIED))

        probe.collect_results = collect
        self.assertEqual(probe.run_flash("write-candidate"), encode(IDLE) + encode(VERIFIED))
        self.assertEqual(events, ["mirror-on", "mirror-off", "run-flash", "collect",
                                  "mirror-resume", "mirror-off"])

    def test_missing_write_receipt_blocks_selection_before_dispatch(self):
        self.phase_directory("select-candidate")
        with self.assertRaises(FileNotFoundError):
            runner.perform(self.bench, "select-candidate")
        self.bench.run_flash.assert_not_called()

    @patch.object(runner, "reboot_pair")
    def test_candidate_boot_rejects_a_changed_emos_boot(self, reboot):
        self.saved("write-candidate", encode(IDLE) + encode(VERIFIED))
        self.saved("select-candidate", encode(VERIFIED) + encode(SELECTED))
        (self.root / "select-candidate" / "vdplet.json").write_text('{"emos_boot": 7}')
        self.phase_directory("boot-candidate")
        with self.assertRaisesRegex(RuntimeError, "boot changed"):
            runner.perform(self.bench, "boot-candidate")
        reboot.assert_not_called()

    def test_missing_terminal_result_leaves_write_outcome_unverified(self):
        folder = self.phase_directory("write-candidate")
        self.bench.run_flash.return_value = b""
        with self.assertRaises(ValueError):
            runner.perform(self.bench, "write-candidate")
        self.assertFalse((folder / "vdplet.json").exists())


if __name__ == "__main__":
    unittest.main()
