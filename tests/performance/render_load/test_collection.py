"""Exercise local-card collection against independent frozen-format records."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'qualification'))
from render_load_collect import card_path, collect, digest, validate
from resident_render_suite import verify


def sample(frames=80):
    header = bytearray(128)
    header[:5] = b'B9R2\2'
    header[5] = 8
    header[6:8] = (320).to_bytes(2, 'little')
    header[8:10] = (240).to_bytes(2, 'little')
    header[10] = 64
    header[12:15] = (123).to_bytes(3, 'little')
    header[22:29] = b'fixture'
    case = bytearray(24)
    case[:4] = b'B9C2'
    case[4:6] = (9).to_bytes(2, 'little')
    case[7] = 2
    case[14:17] = frames.to_bytes(3, 'little')
    case[17:20] = frames.to_bytes(3, 'little')
    case[20] = 1
    raw = bytes(header + case) + b''.join(bytes([(i + 8) % 40, 0]) + bytes(10) for i in range(frames))
    meta = dict(mode=8, tag=123, first=9, end=10, endpoint='p4', variant='normal', fixture={'build_id': 'fixture'})
    telemetry = dict(output='normal', open=False, overflow=False,
                     windows=[dict(id=9, tag=123, flags=2, start_us=1, end_us=100)])
    return meta, raw, telemetry


class Collection(unittest.TestCase):
    def test_reject_identity_checkpoint_and_window_mismatches(self):
        meta, raw, telemetry = sample()
        self.assertEqual(validate(meta, raw, telemetry)[1]['outcome'], 'pass')
        for offset, value in [(5, 20), (10, 16), (12, 124), (22, ord('x')), (132, 10)]:
            bad = bytearray(raw)
            bad[offset] = value
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                validate(meta, bad, telemetry)
        with self.assertRaises(ValueError):
            validate(meta, raw[:-1], telemetry)
        for changed in [dict(output='off'), dict(open=True), dict(overflow=True),
                        dict(windows=[]), dict(windows=[{**telemetry['windows'][0], 'flags': 1}])]:
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                validate(meta, raw, {**telemetry, **changed})

    def test_short_truncated_error_records_never_pass(self):
        meta, raw, telemetry = sample(32)
        self.assertEqual(validate(meta, raw, telemetry)[1]['outcome'], 'partial')
        meta, raw, telemetry = sample()
        for offset, outcome in [(149, 'partial'), (150, 'fail'), (153, 'partial')]:
            bad = bytearray(raw)
            bad[offset] = 1
            self.assertEqual(validate(meta, bad, telemetry)[1]['outcome'], outcome)

    def test_collect_preserves_card_and_prior_receipt_and_detects_conflict(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            card = base / 'card'
            card.mkdir()
            (card / 'autoexec.txt').write_bytes(b'original')
            evidence = base / 'evidence'
            run = evidence / 'BENCH-009-test'
            run.mkdir(parents=True)
            meta, raw, telemetry = sample()
            (card / 'results.bin').write_bytes(raw)
            for name in ('plan.bin', 'startup.txt'):
                (run / name).write_bytes(name.encode())
            meta.update(outcome='measured-awaiting-local-results', sd_results_path='/results.bin',
                        sd_files={'results.bin': {'bytes': len(raw)}},
                        plan_sha256=digest(b'plan.bin'), startup_sha256=digest(b'startup.txt'))
            initial = json.dumps(meta).encode()
            (run / 'run.json').write_bytes(initial)
            (run / 'telemetry.json').write_text(json.dumps(telemetry))
            (run / 'results.bin').write_bytes(b'conflicting evidence')
            self.assertEqual(collect(card, evidence, base / 'conflict.json')['outcome'], 'partial')
            self.assertEqual((run / 'results.bin').read_bytes(), b'conflicting evidence')
            self.assertEqual((run / 'run.json').read_bytes(), initial)
            (run / 'results.bin').unlink()
            receipt = collect(card, evidence, base / 'collected.json')
            self.assertEqual(receipt['outcome'], 'pass')
            self.assertEqual((run / 'run-before-local-collection.json').read_bytes(), initial)
            self.assertEqual((card / 'results.bin').read_bytes(), raw)
            self.assertEqual((card / 'autoexec.txt').read_bytes(), b'original')
            with self.assertRaises(ValueError):
                collect(card, evidence, base / 'collected.json')

    def test_card_root_escape_and_resident_integrity(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            card = base / 'card'
            card.mkdir()
            (card / 'autoexec.txt').write_text('original')
            (base / 'outside').write_bytes(b'fixture')
            (card / 'link').symlink_to(base / 'outside')
            for remote in ('/../outside', 'relative', '/link'):
                with self.subTest(remote=remote), self.assertRaises(ValueError):
                    card_path(card.resolve(), remote)
            catalog = base / 'catalog.json'
            catalog.write_text(json.dumps(dict(identity='test', files=[dict(sd_path='/fixture.bin', bytes=7, sha256=digest(b'fixture'))])))
            self.assertEqual(verify(card, catalog)['outcome'], 'fail')
            (card / 'fixture.bin').write_bytes(b'fixture')
            self.assertEqual(verify(card, catalog)['outcome'], 'pass')
            (card / 'fixture.bin').write_bytes(b'changed')
            self.assertEqual(verify(card, catalog)['outcome'], 'fail')

    def test_local_recovery_samples_remain_failed_and_separate(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            card = base / 'card'
            card.mkdir()
            (card / 'autoexec.txt').write_text('original')
            run = base / 'evidence/BENCH-009-failed'
            run.mkdir(parents=True)
            meta, raw, telemetry = sample()
            (card / 'results.bin').write_bytes(raw)
            for name in ('plan.bin', 'startup.txt'):
                (run / name).write_bytes(name.encode())
            meta.update(outcome='fail', failure='original missing window', result_retrieval='deferred-sd-mount',
                        recovery_result_suffix='-recovery-only', sd_results_path='/results.bin',
                        sd_files={'results.bin': {'bytes': len(raw)}},
                        plan_sha256=digest(b'plan.bin'), startup_sha256=digest(b'startup.txt'))
            (run / 'run.json').write_text(json.dumps(meta))
            receipt = collect(card, run.parent, base / 'collection.json')
            self.assertEqual(receipt['runs'][0]['outcome'], 'fail')
            self.assertEqual(json.loads((run / 'run.json').read_text())['outcome'], 'fail')
            self.assertEqual((run / 'results-recovery-only.bin').read_bytes(), raw)
            self.assertFalse((run / 'results.bin').exists())


if __name__ == '__main__':
    unittest.main()
