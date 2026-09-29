#!/usr/bin/env python3
"""Launch the pinned unattended suite and stream status unless detached."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import uuid


ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv/bin/python"
LOCAL_CONFIG = ROOT / "agents/regression-suite.local.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="fresh job folder; default is agents/regression-runs/<UTC>-<commit>")
    parser.add_argument("--no-notify", action="store_true",
                        help="omit the required hardware cue; suitable only for runner development")
    parser.add_argument("--phase", action="append", choices=("host", "browser", "build"))
    parser.add_argument("--case", action="append")
    parser.add_argument("--commit", default="HEAD",
                        help="Extender commit to pin; default resolves HEAD at launch")
    parser.add_argument("--detach", action="store_true",
                        help="return after launch instead of streaming case status")
    parser.add_argument("--emos-root", type=Path,
                        help="clean fixed EMOS checkout; defaults to the AUDIT-010 baseline")
    args = parser.parse_args()
    if not PYTHON.is_file():
        parser.error(f"project Python is missing: {PYTHON}")
    commit = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "--verify", args.commit + "^{commit}"],
        text=True
    ).strip()
    short_commit = commit[:12]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d-%H-%M-%SZ")
    job = (args.output or ROOT / "agents/regression-runs" / f"{stamp}-{short_commit}").resolve()
    snapshot = (ROOT / "agents/regression-snapshots" /
                f"{stamp}-{short_commit}-{uuid.uuid4().hex[:8]}").resolve()
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout",
                    str(ROOT), str(snapshot)], check=True)
    subprocess.run(["git", "-C", str(snapshot), "checkout", "--quiet", "--detach", commit],
                   check=True)
    (snapshot / "agents/build001").mkdir(parents=True)
    os.symlink(ROOT / "agents/build001/native-tools",
               snapshot / "agents/build001/native-tools", target_is_directory=True)
    os.symlink(ROOT / "vdp/managed_components",
               snapshot / "vdp/managed_components", target_is_directory=True)
    # A directory ignore does not match a symlink bearing that directory name.
    # This private clone-only exclusion covers the reviewed dependency link;
    # tracked source still has to remain clean throughout the run.
    with (snapshot / ".git/info/exclude").open("a") as exclude:
        exclude.write("\n/vdp/managed_components\n")
    suite = job / "suite"
    command = [str(PYTHON), str(ROOT / "scripts/run_regression_suite.py"),
               "--output", str(suite), "--source-root", str(snapshot),
               "--manifest", str(snapshot / "tests/regression-suite.json")]
    if args.emos_root:
        command.extend(("--emos-root", str(args.emos_root.resolve())))
    for phase in args.phase or []:
        command.extend(("--phase", phase))
    for case in args.case or []:
        command.extend(("--case", case))
    launch = [str(PYTHON), str(ROOT / "scripts/bench_job.py"),
              "--output", str(job)]
    hook_path = None
    if not args.no_notify:
        try:
            config = json.loads(LOCAL_CONFIG.read_text())
            url = config["extender_url"]
        except (OSError, KeyError, json.JSONDecodeError) as error:
            parser.error(f"hardware notification config is unavailable: {error}; use --no-notify only for runner development")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            parser.error("extender_url must be an HTTP(S) URL")
        notify = [str(PYTHON), str(ROOT / "scripts/regression_notify.py"),
                  "--url", url, "--job", str(job), "--suite-output", str(suite)]
        hooks = {
            "success": [*notify, "--expected", "success"],
            "failure": [*notify, "--expected", "failure"],
        }
        hook_path = ROOT / "agents" / f".regression-hooks-{uuid.uuid4().hex}.json"
        hook_path.write_text(json.dumps(hooks, indent=2) + "\n")
        launch.extend(("--terminal-hooks", str(hook_path)))
    launch.extend(("--", *command))
    try:
        completed = subprocess.run(launch, cwd=ROOT)
    finally:
        if hook_path is not None:
            hook_path.unlink(missing_ok=True)
    if completed.returncode == 0:
        print(f"Job: {job}")
        print(f"Pinned Extender commit: {commit}")
        print(f"Pinned source snapshot: {snapshot}")
        print(f"Status: {job / 'result.json'}")
        print(f"Suite progress: {suite / 'progress.json'}")
        print(f"Suite summary: {suite / 'summary.json'}")
        if not args.detach:
            worker_pid = json.loads((job / "launch.json").read_text())["pid"]
            print("Streaming test status; Ctrl-C or closing SSH leaves the detached run active.",
                  flush=True)
            try:
                subprocess.run(["tail", f"--pid={worker_pid}", "-n", "+1", "-F",
                                str(job / "output.log")])
            except KeyboardInterrupt:
                print(f"Status stream stopped; detached job {job} is still active.")
            if (job / "result.json").is_file():
                result = json.loads((job / "result.json").read_text())
                print(f"Detached job terminal status: {result.get('status')}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
