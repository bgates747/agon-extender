#!/usr/bin/env python3
"""Materialize a PORT-008 packet locally after the candidate builds pass."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
import tarfile

from qualify_parallel_upload import ROOT, validate


def pin(path, expected=None):
    path = path.resolve(strict=True)
    data = path.read_bytes()
    digest = sha256(data).hexdigest()
    if expected is not None and digest != expected:
        raise ValueError(f"Artifact differs from its accepted hash: {path.name}")
    return {"path": str(path), "bytes": len(data), "sha256": digest}


def relative_pin(path, specification):
    result = pin(path, specification["sha256"])
    if result["bytes"] != specification["bytes"]:
        raise ValueError(f"Artifact length differs from its accepted pin: {path.name}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p4-build", type=Path, required=True)
    parser.add_argument("--listener", type=Path, required=True)
    parser.add_argument("--worked-job", type=Path, required=True)
    parser.add_argument("--worked-artifact", type=Path, required=True)
    parser.add_argument("--p4-table", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    p4_manifest = json.loads((args.p4_build / "manifest.json").read_text())
    if not (p4_manifest["parallel_upload_candidate"] and p4_manifest["network_messages"]
            and p4_manifest["parallel_boot_candidate"] and not p4_manifest["network_parallel"]
            and not p4_manifest["source_dirty"]):
        raise ValueError("Expected a clean matched P4 build with the parallel upload sender")
    table = pin(args.p4_table, "e29396a4f5ecc129c0e275d2df19d69adb5ee33389e3d5659e9a50932ac6864a")
    relative_pin(args.p4_build / "build/partition_table/partition-table.bin", table)
    candidate = pin(args.p4_build / "build/agon_extender.bin")
    restore = pin(ROOT / "dist/bench-standards/extender-p4-pc-d9bcb1a2/agon_extender.bin",
                  "d9bcb1a2b277e4dcec808d46a33d53879ea4ac4f3e35d69f80345d3c9ac4043e")
    extent = (max(candidate["bytes"], restore["bytes"]) + 4095) & ~4095
    args.out.mkdir(parents=True, exist_ok=False)
    p4 = {"offset": "0x20000", "partition_bytes": 0x700000, "write_bytes": extent,
          "partition_table": table, "candidate_app": candidate, "restore_app": restore}
    for name, spec in (("candidate", candidate), ("restore", restore)):
        path = args.out / f"p4-{name}-write.bin"
        path.write_bytes(Path(spec["path"]).read_bytes().ljust(extent, b"\xff"))
        p4[f"{name}_write"] = pin(path)

    current = json.loads((ROOT / "docs/mainboard-sd-tools.json").read_text())["listener"]
    archive = ROOT / "dist/production" / current["build_id"] / (current["build_id"] + ".tar.gz")
    old_listener = args.out / "restore-sdserve.bin"
    with tarfile.open(archive) as tar:
        member, = [m for m in tar.getmembers() if m.name.endswith("sd/emos/sdserve.bin") and m.isfile()]
        with tar.extractfile(member) as stream:
            old_listener.write_bytes(stream.read())
    rollback = relative_pin(old_listener, current)
    fixture = json.loads(args.worked_job.read_text())
    if fixture["preserve"]["/emos/sdserve.bin"] != rollback["sha256"]:
        raise ValueError("Worked job and accepted listener baseline disagree")
    fixture.update(schema=2, namespace="port008-sdupload-r01", firmware={"p4": p4})
    job = fixture["fixture"]
    # Use the worked example rebuilt for a fresh result path. The original
    # example's compiled-in destination may contain another job's evidence.
    result = "/test/port008-sdupload-r01/fixture/result.txt"
    if result.encode("ascii") + b"\0" not in args.worked_artifact.read_bytes():
        raise ValueError("Worked example lacks the dedicated qualification result path")
    job.update(agon=pin(args.worked_artifact),
               sd_program="/test/port008-sdupload-r01/fixture/OLIMT2.bin",
               sd_result=result, seconds=30)
    job["inputs"] = []
    rng = random.Random(8008)
    for number, size in enumerate([0, 65537, 1100000, 2625992] + [70472] * 20):
        local = args.out / f"upload-{number:02d}.bin"
        local.write_bytes(rng.randbytes(size))
        job["inputs"].append({"sd_path": f"/test/port008-sdupload-r01/scratch/{local.name}",
                              "source": pin(local)})
    packet = {"job": fixture, "listener": {"candidate": pin(args.listener), "restore": rollback},
              "emos": pin(ROOT / "dist/bench-standards/emos-eirene-r04/ROM.bin",
                          "a25f1612f4aaa542c5488cf3266d968ad3d1d61e9df3b5ce2c680650f5d7a2ca")}
    validate(packet)
    manifest = args.out / "qualification.json"
    manifest.write_text(json.dumps(packet, indent=2) + "\n")
    print(pin(manifest)["sha256"])


if __name__ == "__main__":
    main()
