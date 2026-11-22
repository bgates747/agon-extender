"""Exercise the fixture's target driver on the host with controlled DMA writebacks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
NATIVE_SHA = "3528544408f51b23f9135c89d05d4c4b02f7143bb9e9a7a0e43f3eb724a7e25b"
TOP_SHA = "58204ce0d40cd2a2426ca942edbc4309ba2d18d211bb744dc6fdde07b247a353"
BOTTOM_SHA = "40c930d3e3ee215618e5260d51a3216c2a5201f93805217c6047a099c4b7128d"
ROW_BYTES = 848 * 3


def oracle(path):
    """Decode the original, pre-compression mode-preview-r02 VDU upload."""
    vdu = path.read_bytes()
    prefix = bytes((23, 0, 160, 0, 250))
    pos = vdu.index(prefix + bytes((2,))) + 6
    native = bytearray()
    while vdu[pos:pos + 6] == prefix + bytes((0,)):
        size = int.from_bytes(vdu[pos + 6:pos + 8], "little")
        native.extend(vdu[pos + 8:pos + 8 + size])
        pos += 8 + size
    assert vdu[pos:pos + 6] == prefix + bytes((14,)), "expected unpacked m000.vdu"
    assert len(native) == 640 * 480 and hashlib.sha256(native).hexdigest() == NATIVE_SHA
    # The preview stores AABBGGRR. The P4 scans B,G,R bytes with black sidebars.
    colours = [bytes((85 * ((n >> 4) & 3), 85 * ((n >> 2) & 3), 85 * (n & 3)))
               for n in range(256)]
    side = bytes(104 * 3)
    image = b"".join(side + b"".join(colours[n] for n in native[y:y + 640]) + side
                     for y in range(0, len(native), 640))
    assert hashlib.sha256(image[:ROW_BYTES]).hexdigest() == TOP_SHA
    assert hashlib.sha256(image[-ROW_BYTES:]).hexdigest() == BOTTOM_SHA
    assert sum(a != b for a, b in zip(native[:640], native[-640:])) == 621
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", type=Path, required=True,
                        help="original unpacked fixture-r02/m000.vdu")
    parser.add_argument("--packed", type=Path, required=True,
                        help="matched fixture-r02-packed/m000.vdu embedded by the firmware")
    parser.add_argument("--trace-dir", type=Path,
                        help="save real driver reports from the host simulation outside source")
    args = parser.parse_args()
    if args.trace_dir:
        args.trace_dir.mkdir(parents=True, exist_ok=True)
    expected = oracle(args.pattern)
    scenarios = ("normal", "cycle-wrap", "delayed-stop", "early", "stale-valid", "early-valid", "duplicate",
                 "invalid", "dma-error", "underrun", "early-frame", "missing-last",
                 "wrong-source", "task-context", "cache-error", "coalesced")
    with tempfile.TemporaryDirectory() as temp:
        out = Path(temp)
        frame = out / "mode0.bgr"
        frame.write_bytes(expected)
        mode0 = HERE.parent / "mode0"
        asset = out / "mode0_rgba2222.bin"
        subprocess.run([sys.executable, str(mode0 / "prepare_pattern.py"), "--packed",
                        str(args.packed), "--output", str(asset)], check=True)
        # Define the same linker symbol as ESP-IDF's EMBED_FILES on the target.
        asset_asm = out / "asset.S"
        asset_asm.write_text('.section .rodata\n.globl _binary_mode0_rgba2222_bin_start\n'
                             '_binary_mode0_rgba2222_bin_start:\n.incbin "mode0_rgba2222.bin"\n'
                             '.section .note.GNU-stack,"",%progbits\n')
        exe = out / "handoff"
        subprocess.run([os.environ.get("CC", "cc"), "-std=gnu11", "-O2", "-g",
                        "-Wall", "-Wextra", "-Werror", "-Wno-unused-function",
                        "-fno-pie", "-no-pie", str(HERE / "mode0_handoff_host.c"),
                        str(mode0 / "mode0_pattern.c"), str(asset_asm),
                        "-o", str(exe)], check=True, cwd=out)
        for name in scenarios:
            result = subprocess.run([str(exe), str(frame), name], check=True,
                                    stdout=subprocess.PIPE, text=True)
            records = result.stdout.splitlines(keepends=True)
            trace = [line for line in records if line.startswith("MODE0_")]
            assert any(line.startswith("MODE0_RESULT ") for line in trace)
            if args.trace_dir:
                (args.trace_dir / (name + ".txt")).write_text("".join(trace))
            verdict = json.loads(trace[0].removeprefix("MODE0_RESULT "))
            if verdict["frame_ok"]:
                assert verdict["refill_cycles"] == ((verdict["published_at"] -
                                                     verdict["irq_entry"]) & 0xffffffff)
                assert verdict["refill_cycles"] < 100     # synthetic host cycles
                slots = dict(line.strip().split()[1:] for line in trace if line.startswith("MODE0_SLOT "))
                assert bytes.fromhex(slots["before"]) == expected[:ROW_BYTES]
                assert bytes.fromhex(slots["after"]) == expected[-ROW_BYTES:]
            print(records[-1], end="")
    print(json.dumps({"scope": "host, DMA register surrogate", "scenarios": len(scenarios),
                      "frame_bytes": len(expected), "carrier_sha256": hashlib.sha256(expected).hexdigest(),
                      "top_sha256": TOP_SHA, "bottom_sha256": BOTTOM_SHA}, sort_keys=True))


if __name__ == "__main__":
    main()
