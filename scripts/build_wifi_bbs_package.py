#!/usr/bin/env python3
"""Create a local manual fixture package; never deploy, compile or contact Agon."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_COMMIT = "e265db1de57c49142420324945c666049dc1ec53"
BINARY_SHA = "6f0c41273eb4ab479ad39ac0bde2cd3550f4403cbc8afec5c4e15a0fae8f9d4c"
OWN_FILES = ("scripts/wifi_bbs.py", "scripts/build_wifi_bbs_package.py",
             "docs/tasks/NET-005/USING.md", "tests/test_wifi_bbs.py")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build(upstream, output):
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    # Unrelated workspace changes are allowed; all selected source must actually
    # be published at the named commit before producing an identified package.
    for name in OWN_FILES:
        recorded = subprocess.check_output(["git", "show", commit + ":" + name], cwd=ROOT)
        if recorded != (ROOT / name).read_bytes():
            raise ValueError("Selected source is not committed: " + name)
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=upstream, text=True).strip()
    if actual != UPSTREAM_COMMIT:
        raise ValueError("Wrong Radiotux source revision")
    relative = "minicom/bin/minicom.bin"
    binary = (upstream / relative).read_bytes()
    if sha(binary) != BINARY_SHA or binary != subprocess.check_output(
            ["git", "show", UPSTREAM_COMMIT + ":" + relative], cwd=upstream):
        raise ValueError("Radiotux binary differs from the selected unchanged bytes")
    manual = "minicom/Agon-Terminal.man"
    if (upstream / manual).read_bytes() != subprocess.check_output(
            ["git", "show", UPSTREAM_COMMIT + ":" + manual], cwd=upstream):
        raise ValueError("Radiotux manual differs from the selected revision")
    stamp = datetime.now(timezone.utc)
    identity = "wifi-bbs-r01-b" + stamp.strftime("%Y-%m-%d-%H-%M-%SZ")
    destination = output / identity
    destination.mkdir(parents=True, exist_ok=False)
    copies = [(ROOT / "scripts/wifi_bbs.py", "host/wifi_bbs.py"),
              (ROOT / "docs/tasks/NET-005/USING.md", "USING.md"),
              (upstream / relative, "sd/extender/network/net005/minicom.bin"),
              (upstream / "minicom/Agon-Terminal.man", "upstream/Agon-Terminal.man")]
    for source, name in copies:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (destination / "NOTICES.txt").write_text(
        "Radiotux's unchanged minicom executable and original manual are retained.\n"
        "The original manual declares the UNLICENSE; see upstream/Agon-Terminal.man.\n"
        "Upstream source: https://github.com/Radiotux/Agon-Software/tree/" + UPSTREAM_COMMIT + "/minicom\n"
        "No claim of a local rebuild or physical Console8 qualification.\n"
        "The Pi BBS is experimental Agon Extender fixture source.\n", encoding="utf-8")
    payloads = {str(p.relative_to(destination)): dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
                for p in sorted(destination.rglob("*")) if p.is_file()}
    manifest = dict(schema_version=1, artifact_id="wifi-bbs", revision="r01", build_id=identity,
                    status="experimental", created_utc=stamp.isoformat(), source_commit=commit,
                    selected_source={name: sha((ROOT / name).read_bytes()) for name in OWN_FILES},
                    upstream_commit=UPSTREAM_COMMIT, client_changed=False,
                    scope="Host loopback checked; Console8/ESP8266 manual review pending",
                    files=payloads)
    (destination / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    members = dict(payloads)
    p = destination / "manifest.yaml"
    members["manifest.yaml"] = dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
    checksum = "".join(f"{value['sha256']}  {name}\n" for name, value in sorted(members.items()))
    (destination / "SHA256SUMS").write_text(checksum, encoding="ascii")
    # Verify the actual generated files, including manifest, before archiving.
    for name, value in members.items():
        data = (destination / name).read_bytes()
        if len(data) != value["bytes"] or sha(data) != value["sha256"]:
            raise ValueError("Package member differs: " + name)
    archive = destination.with_suffix(".zip")
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(destination.rglob("*")):
            if p.is_file():
                z.write(p, identity + "/" + str(p.relative_to(destination)))
    with zipfile.ZipFile(archive) as z:
        for p in destination.rglob("*"):
            if p.is_file() and z.read(identity + "/" + str(p.relative_to(destination))) != p.read_bytes():
                raise ValueError("Archived member differs")
    digest = sha(archive.read_bytes())
    archive.with_name(archive.name + ".sha256").write_text(digest + "  " + archive.name + "\n", encoding="ascii")
    return dict(build_id=identity, package=str(destination.resolve()), archive=str(archive.resolve()),
                archive_sha256=digest, all_members_compared=True, source_commit=commit)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radiotux", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "dist/wifi-bbs")
    args = parser.parse_args()
    print(json.dumps(build(args.radiotux.resolve(), args.output.resolve()), indent=2))


if __name__ == "__main__":
    main()
