#!/usr/bin/env python3
"""Build a separately identified keyboard-free diagnostic; never deploy or run."""
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[3]
stamp = datetime.now(timezone.utc)
identity = yaml.safe_load((ROOT / "version.yaml").read_text())
build_id = identity["identity"] + stamp.strftime("-b%Y-%m-%d-%H-%M-%SZ")
(ROOT / "src/build_identity.h").write_text(f'#define BUILD_ID "{build_id}"\n')
subprocess.run(["make", "clean"], cwd=ROOT, check=True)
subprocess.run(["make", "all"], cwd=ROOT, check=True)
binary = ROOT / "bin/PWBOOT.bin"
full_binary = binary.with_name(build_id + ".bin")
full_binary.write_bytes(binary.read_bytes())
manifest = {
    "schema_version": 1,
    "build": {"build_id": build_id, "artifact_id": identity["artifact_id"],
              "source_identity": identity["identity"], "variant": None,
              "created_at": stamp.strftime("%Y-%m-%dT%H:%M:%SZ"), "status": "experimental"},
    "provenance": {"repository": "https://github.com/bgates747/agon-extender.git",
                   "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPOSITORY, text=True).strip(),
                   "dirty": True,
                   "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in sorted((ROOT / "src").glob("*"))}},
    "outputs": [{"filename": full_binary.name, "deploy_alias": "PWBOOT.BIN",
                 "size_bytes": binary.stat().st_size,
                 "sha256": hashlib.sha256(binary.read_bytes()).hexdigest()}],
    "notes": ["Uncommitted diagnostic build; no qualification claim.",
              "Inherited GPIO assembly; new noninteractive entry; no I2C exercise."],
}
(ROOT / "bin/build-manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False))
print(build_id)
