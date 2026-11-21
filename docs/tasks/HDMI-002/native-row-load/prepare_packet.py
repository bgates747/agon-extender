"""Create and preflight display load jobs from retained, local artifacts. Offline only."""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess


def pin(path, expected=None):
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if expected and digest != expected:
        raise ValueError(f"Digest mismatch for {path.name}")
    return {"path": str(path.resolve()), "sha256": digest, "bytes": len(data)}


def load(path):
    return json.loads(path.read_bytes())


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True,
                        help="Shared Extender checkout containing retained assets, games and operator binding")
    parser.add_argument("--native-build", type=Path, help="Completed identified build directory with manifest.json")
    args = parser.parse_args()
    root = args.workspace.resolve()
    old_packet = root / "agents/hdmi002/size01/packet"
    old_binding = load(old_packet / "operator-binding.json")
    runner = Path(old_binding["runner_checkout"])
    revision = subprocess.check_output(["git", "-C", runner, "rev-parse", "HEAD"], text=True).strip()
    if revision != old_binding["runner_revision"]:
        raise ValueError("Commissioned runner revision mismatch")
    config = old_binding["config"]
    pin(Path(config["path"]), config["sha256"])
    work = root / "agents/hdmi002/native-rows"
    packet = work / "packet"
    packet.mkdir(exist_ok=True)
    fixture_root = work / "fixture-build"
    program = fixture_root / "bin/rowload.bin"
    fixture = pin(program)
    package_source = Path(__file__).resolve().parent
    fixture_inputs = {}
    for name in ("src/main.c", "Makefile"):
        supplied = pin(package_source / name)
        compiled = fixture_root / name
        pin(compiled, supplied["sha256"])
        if compiled.stat().st_mtime_ns > program.stat().st_mtime_ns:
            raise ValueError(f"Rebuild rowload.bin after modifying {name}")
        fixture_inputs[name] = supplied
    patterns = root / "agents/visual-review/display-pattern/fixture-r02-packed"
    named = {}
    for name, digest in sorted(load(patterns / "manifest.json")["files"].items()):
        if not name.startswith("m") or not name.endswith(".vdu"):
            continue
        mode = int(name[1:4])
        if 96 <= mode <= 99:
            continue
        data = (patterns / name).read_bytes()
        if data[:2] != bytes((22, mode)):
            raise ValueError(f"{name} does not start with its declared mode")
        named[name] = pin(patterns / name, digest)
    if not all(f"m{mode:03d}.vdu" in named for mode in (7, 8, 9, 10, 11, 20, 136, 137, 138, 139)):
        raise ValueError("Missing stock mode pattern")
    game = load(old_packet / "evidence/nurples-dev/job.json")["fixtures"][0]
    game_cwd = game["cwd"] + "/"
    named["nurples/nurples.bin"] = pin(Path(game["agon"]["path"]), game["agon"]["sha256"])
    for item in game["inputs"]:
        name = item["sd_path"].removeprefix(game_cwd)
        named["nurples/" + name] = pin(Path(item["source"]["path"]), item["source"]["sha256"])
    rally = root.parent / "AgonArcade/rally-game/bin/rally.bin"
    named["rally/rally.bin"] = pin(rally, "ca45138de2c65eff63759c505cf6a98e552b1e35185989ba3fba040ae6251d48")
    road = root / "docs/tasks/QUAL-003/rally-excom/fixture-r03/bin/RXPROBE.bin"
    named["road/rxprobe.bin"] = pin(road, "1723fc7b7252bb9d6d421eff0d03066ae6659071f9cec1d898a418a7bcda81e2")
    source = old_packet / "job-b.json"
    baseline = load(source)
    prior = baseline["firmware"]["p4"]
    table = pin(Path(prior["partition_table"]["path"]), prior["partition_table"]["sha256"])
    release = pin(Path(prior["restore_app"]["path"]), prior["restore_app"]["sha256"])
    old = pin(Path(prior["candidate_app"]["path"]), prior["candidate_app"]["sha256"])
    builds = {"legacy": None, "full-frame": old}
    if args.native_build:
        directory = args.native_build.resolve()
        manifest = load(directory / "manifest.json")
        app = directory / "build/agon_extender.bin"
        record, = [entry for entry in manifest["artifacts"] if Path(entry["path"]).name == app.name]
        native = pin(app, record["sha256"])
        if native["sha256"] in (old["sha256"], release["sha256"]) or not manifest["build_id"].startswith("hdmi-native-row-"):
            raise ValueError("Expected the separately identified native-row build")
        pin(directory / "build/partition_table/partition-table.bin", table["sha256"])
        builds["native"] = native
    # Re-check the old incoming application and restore image against one common
    # aligned extent for *all* arms. This preserves old bytes at the tail.
    extent = max(prior["write_bytes"], *(a["bytes"] for a in builds.values() if a))
    extent = (extent + 4095) // 4096 * 4096
    if extent > prior["partition_bytes"]:
        raise ValueError("Application is larger than the commissioned partition")
    def padded(label, image):
        path = packet / (label + "-app0-write.bin")
        path.write_bytes(Path(image["path"]).read_bytes().ljust(extent, b"\xff"))
        return pin(path)
    restore = padded("restore", release)
    binding = {"runner_checkout": str(runner), "runner_revision": revision, "config": config,
               "fixture": fixture, "fixture_inputs": fixture_inputs,
               "observer": pin(package_source / "observe.py"),
               "scorer": pin(package_source / "score_refills.py"), "patterns": sum(name.endswith(".vdu") for name in named),
               "operator_chat": old_binding["operator_chat"], "write_extent": extent,
               "production_restore_app": release, "preserve": baseline["preserve"], "arms": {}}
    for arm, app in builds.items():
        name = "native-rows-" + arm
        cwd = "/test/" + name
        image = {}
        if app:
            image["p4"] = {"offset": prior["offset"], "partition_bytes": prior["partition_bytes"],
                           "partition_table": table, "write_bytes": extent,
                           "candidate_app": app, "candidate_write": padded(arm, app),
                           "restore_app": release, "restore_write": restore}
        target = {"id": "rowload", "cwd": cwd, "address": "040000", "agon": fixture,
                  "sd_program": cwd + "/rowload.bin", "results": [], "inputs": [
                      {"sd_path": cwd + "/" + name, "source": artifact}
                      for name, artifact in named.items()]}
        job = packet / ("job-" + arm + ".json")
        save(job, {"schema": 3, "namespace": name, "human_start": "stage-only",
                   "fixtures": [target], "firmware": image, "preserve": baseline["preserve"]})
        record = pin(job)
        command = [str(root / ".venv/bin/python"), str(runner / "scripts/olimex_bench.py"),
                   "--config", config["path"], "--job", str(job), "--sha256", record["sha256"]]
        phases = subprocess.check_output(command + ["preflight"], cwd=runner, text=True).splitlines()
        binding["arms"][arm] = {"job": record, "sd": cwd, "preflight": phases,
                                "commands": {phase: shlex.join(command + [
                                    "--out", str(packet / "evidence" / arm),
                                    "--operator", old_binding["operator_chat"], phase]) for phase in phases}}
    save(packet / "operator-binding.json", binding)
    print(json.dumps({"patterns": binding["patterns"], "fixture": fixture["sha256"],
                      "write_extent": extent, "jobs": {
                          a: v["job"]["sha256"] for a, v in binding["arms"].items()}}))


if __name__ == "__main__":
    main()
