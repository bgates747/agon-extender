#!/usr/bin/env python3
"""Run the production Phase F browser protocol in a real headless browser."""

from __future__ import annotations

import argparse
import json
import queue
import subprocess
import sys
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import sha256_file, write_canonical  # noqa: E402

FIXTURES = ROOT / "docs/tasks/PORT-003/phase-f/fixtures/independent-fixtures.yaml"
OUTPUT = ROOT / "docs/tasks/PORT-003/phase-f/evidence/browser-test-results.yaml"
PAGE = "/docs/tasks/PORT-003/phase-f/tests/browser_protocol_tests.html"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--firefox", type=Path, default=Path("/usr/bin/firefox"))
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()
    if not args.firefox.is_file():
        raise FileNotFoundError(args.firefox)

    fixture_data = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))["evf1"]
    browser_vectors = {
        "valid_vectors": fixture_data["valid_vectors"],
        "malformed_vectors": fixture_data["malformed_vectors"],
    }
    reports: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=1)

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *handler_args: Any, **handler_kwargs: Any) -> None:
            super().__init__(*handler_args, directory=str(ROOT), **handler_kwargs)

        def log_message(self, _format: str, *args: Any) -> None:
            pass

        def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
            if urlsplit(self.path).path == "/__phase_f_vectors":
                payload = json.dumps(browser_vectors, sort_keys=True).encode()
                self.send_response(200)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            super().do_GET()

        def do_POST(self) -> None:  # noqa: N802 - stdlib callback name
            if urlsplit(self.path).path != "/__phase_f_result":
                self.send_error(404)
                return
            length = int(self.headers.get("content-length", "0"))
            if length <= 0 or length > 65536:
                self.send_error(400)
                return
            report = json.loads(self.rfile.read(length))
            if reports.empty():
                reports.put_nowait(report)
            self.send_response(204)
            self.end_headers()

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    process: subprocess.Popen[str] | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="port-003-phase-f-firefox-") as profile:
            url = f"http://127.0.0.1:{server.server_port}{PAGE}"
            process = subprocess.Popen(
                [
                    str(args.firefox),
                    "--headless",
                    "--no-remote",
                    "--profile",
                    profile,
                    url,
                ],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                report = reports.get(timeout=args.timeout)
            except queue.Empty as error:
                stdout, stderr = process.communicate(timeout=5)
                raise RuntimeError(
                    "Firefox did not report a Phase F browser result\n"
                    f"stdout:\n{stdout}\nstderr:\n{stderr}"
                ) from error
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)

    status = report.get("status")
    checks = report.get("checks")
    if status != "pass" or not isinstance(checks, int) or checks < 78:
        raise RuntimeError(f"browser protocol qualification failed: {report!r}")
    version = subprocess.run(
        [str(args.firefox), "--version"], check=True, capture_output=True, text=True
    ).stdout.strip()
    artifact = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_f_browser_test_results",
        "generated_by": "docs/tasks/PORT-003/phase-f/scripts/run-browser-tests.py",
        "diagnostic_status": "real-browser host qualification; no network-device or hardware claim",
        "browser": version,
        "inputs": [
            {
                "path": path,
                "sha256": sha256_file(ROOT / path),
            }
            for path in [
                "docs/tasks/PORT-003/phase-f/fixtures/independent-fixtures.yaml",
                "docs/tasks/PORT-003/phase-f/tests/browser_protocol_tests.html",
                "docs/tasks/PORT-003/phase-f/tests/browser_protocol_tests.mjs",
                "vdp/video/extender/web/frame_protocol.js",
                "vdp/video/extender/web/webgl2_presenter.js",
            ]
        ],
        "fixture_counts": {
            "valid_vectors": len(browser_vectors["valid_vectors"]),
            "malformed_vectors": len(browser_vectors["malformed_vectors"]),
        },
        "result": report,
        "summary": {"passed": 1, "failed": 0, "checks": checks},
    }
    write_canonical(OUTPUT, artifact)
    print(f"Phase F browser tests: {checks} checks passed in {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
