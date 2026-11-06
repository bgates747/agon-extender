"""Exact restoration/tail tests, using synthetic owner images only."""
import unittest
from image_span import compose, digest, extend_verified_prefix


class ImageSpan(unittest.TestCase):
    def test_shorter_application_keeps_existing_tail_without_ff_fill(self):
        old = bytes(range(64)); app = b'A' * 17
        result = compose(app, digest(app), old, digest(old), 64, sector=16)
        self.assertEqual(result['payload'], app + old[17:32])
        self.assertEqual(result['rollback'], old[:32])
        self.assertEqual(result['tail_bytes'], 15)

    def test_larger_candidate_preserves_whole_new_last_sector_tail(self):
        old = bytes(range(64)); app = b'B' * 49
        result = compose(app, digest(app), old, digest(old), 64, sector=16)
        self.assertEqual(result['payload'], app + old[49:])
        self.assertEqual(result['rollback'], old)

    def test_unknown_tail_and_partition_overflow_are_refused(self):
        old = b'x' * 32; app = b'A' * 33
        with self.assertRaises(ValueError): compose(app, digest(app), old, digest(old), 64, sector=16)
        old *= 2
        with self.assertRaises(ValueError): compose(app, digest(app), old, digest(old), 32, sector=16)
        with self.assertRaises(ValueError): compose(app, '0' * 64, old, digest(old), 64, sector=16)

    def test_later_prefix_uses_proven_untouched_suffix(self):
        old = b'o' * 8192; new = b'n' * 4096
        self.assertEqual(extend_verified_prefix(new, digest(new), old, digest(old)), new + old[4096:])
        with self.assertRaises(ValueError): extend_verified_prefix(new, '0' * 64, old, digest(old))
        with self.assertRaises(ValueError): extend_verified_prefix(new[:-1], digest(new[:-1]), old, digest(old))


if __name__ == '__main__': unittest.main()
