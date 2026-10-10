"""Independent synthetic records; no physical result is manufactured."""
import binascii
import csv
import io
from pathlib import Path
import sys
import unittest
import zlib
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from parallel_probe_results import compare, pattern, SIZES


def sample():
    out = io.StringIO()
    out.write("# start_mos_ticks=100; nominal120_Hz_not_calibrated\n")
    writer = csv.writer(out)
    writer.writerow("row,direction,length,descriptor,crc,first,last,guards,pattern,service_status,elapsed_mos_ticks".split(","))
    peer = []
    for round_ in range(2):
        for direction in range(2):
            for j, n in enumerate(SIZES):
                index = round_ * 10 + direction * 5 + j + 1
                d = bytearray(b"EX\x02\x02") + index.to_bytes(4, "little") + b"\x01\x00" + n.to_bytes(2, "little") + bytes((direction, 0))
                d += binascii.crc_hqx(d, 0xFFFF).to_bytes(2, "little")
                seed = index ^ 1 ^ 0xD3 if direction else (17 + round_ * 109 + j * 11) & 255
                data = pattern(n, seed)
                crc, first, last = f"{zlib.crc32(data):08x}", f"{data[0]:02x}", f"{data[-1]:02x}"
                writer.writerow((index, direction, n, d.hex(), crc, first, last, 1, 1, 0, 2))
                peer.append(f"Parallel probe descriptor={d.hex()} direction={direction} length={n} crc={crc} first={first} last={last} guards=1 pattern={'1' if direction else 'na'} elapsed_us=2000")
    out.write("# end_mos_ticks=900; total_mos_ticks=800; passed=20/20\n")
    return out.getvalue(), "\n".join(peer)


class ResultTests(unittest.TestCase):
    def test_complete_and_negative_evidence(self):
        agon, peer = sample()
        self.assertEqual(len(compare(agon, peer)["cases"]), 20)
        variants = [
            (agon, "\n".join(peer.splitlines()[1:])),
            (agon, peer + "\n" + peer.splitlines()[0]),
            (agon, peer.replace("guards=1", "guards=0", 1)),
            (agon, peer.replace("pattern=1", "pattern=0", 1)),
            (agon, peer.replace("crc=", "crc=0", 1)),
            (agon.replace(",1,1,0,2", ",1,0,0,2", 1), peer),
            (agon.replace("passed=20/20", "passed=19/20"), peer),
            (agon.replace("total_mos_ticks=800", "total_mos_ticks=801"), peer),
            (agon, peer.replace("first=11", "first=10", 1)),
        ]
        for a, b in variants:
            with self.subTest(a=a[:20], b=b[:80]), self.assertRaises(ValueError):
                compare(a, b)

    def test_mirrored_pattern(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / "vdp/video/extender/transport/parallel_probe_pattern.h").read_bytes(),
                         (root.parent / "agon-emos/projects/parprobe/src/pattern.h").read_bytes())


if __name__ == "__main__":
    unittest.main()
