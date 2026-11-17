#!/usr/bin/env python3
"""Record commissioned operator files and check the Pi chat endpoint."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from uuid import UUID


ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT = ROOT.parent / "agon-dev-env"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def checkout_snapshot(revision):
    actual = git("rev-parse", "HEAD").decode().strip()
    if actual != revision:
        raise RuntimeError(f"Checkout revision {actual} differs from commissioned {revision}")
    selection = ROOT / "docs/operations/olimex-bench/sparse-paths.txt"
    patterns = selection.read_text().splitlines()
    paths = [line.strip("/") for line in patterns if line.strip()]
    entries = git("ls-tree", "-rz", revision, "--", *paths).split(b"\0")
    files = {}
    for entry in entries:
        if not entry:
            continue
        metadata, name = entry.split(b"\t", 1)
        _, kind, object_id = metadata.decode().split()
        if kind != "blob":
            raise RuntimeError("Operator selection must contain ordinary tracked files")
        path = name.decode()
        data = (ROOT / path).read_bytes()
        if data != git("cat-file", "blob", object_id):
            raise RuntimeError(f"Operator file differs from commissioned revision: {path}")
        files[path] = sha256(data)
    if files.get(selection.relative_to(ROOT).as_posix()) != sha256(selection.read_bytes()):
        raise RuntimeError("Sparse selection differs from commissioned revision")
    return files


def check(revision, source_thread):
    files = checkout_snapshot(revision)
    sys.path.insert(0, str(ENVIRONMENT / "scripts"))
    from codex_rpc import CodexRpc
    from pi_chat import metadata, verify_authorization

    with CodexRpc(timeout=15) as rpc:
        source = metadata(rpc, source_thread)
        proof = verify_authorization(rpc)
        config = rpc.call("config/read", {"cwd": str(ROOT), "includeLayers": False})["config"]
    local_policy = tomllib.loads((ROOT / ".codex/config.toml").read_text())["auto_review"]["policy"]
    effective_policy = config.get("auto_review", {}).get("policy", "")
    if effective_policy != local_policy:
        raise RuntimeError("Effective reviewer policy differs from commissioned project policy")
    sender = ENVIRONMENT / "scripts/pi_chat.py"
    transport = ENVIRONMENT / "scripts/codex_rpc.py"
    return {
        "ready": True,
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "revision": revision,
        "operator_thread": source["id"],
        "operator_files_sha256": files,
        "sender": str(sender),
        "sender_sha256": sha256(sender.read_bytes()),
        "transport_sha256": sha256(transport.read_bytes()),
        "startup_instructions_sha256": sha256((ROOT / "AGENTS.md").read_bytes()),
        "effective_reviewer_policy_sha256": sha256(effective_policy.encode()),
        "authorization_verified": proof["source_verified"],
        "authority": proof["authorization_id"],
        "hardware_accessed": False,
        "message_sent": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", required=True, help="Commissioned full Git commit ID")
    parser.add_argument("--source-thread", required=True, type=UUID)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        if not re.fullmatch(r"[0-9a-f]{40}", args.revision):
            raise ValueError("Use the full commissioned 40-character commit ID")
        result = check(args.revision, str(args.source_thread))
    except Exception as exc:
        result = {"ready": False, "error": str(exc)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"ready": result["ready"], "receipt": str(args.out),
                      **({"error": result["error"]} if "error" in result else {})}))
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
