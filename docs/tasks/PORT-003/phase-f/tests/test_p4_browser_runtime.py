#!/usr/bin/env python3
"""Hermetic tests for the Phase F live P4 browser qualification client.

This localhost fixture validates the qualification tool itself. It does not
stand in for the ESP32-P4 runtime check and cannot support a hardware claim.
"""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest


ROOT = Path(__file__).resolve().parents[5]
SCRIPT = ROOT / "docs/tasks/PORT-003/phase-f/scripts/check-p4-browser-runtime.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("p4_browser_runtime", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load live browser checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


def read_exact(connection: socket.socket, size: int) -> bytes:
    result = bytearray()
    while len(result) < size:
        block = connection.recv(size - len(result))
        if not block:
            raise ConnectionError("client closed during WebSocket frame")
        result.extend(block)
    return bytes(result)


def read_client_frame(connection: socket.socket) -> tuple[int, bytes]:
    first, second = read_exact(connection, 2)
    if not second & 0x80:
        raise AssertionError("qualification client frame was not masked")
    length = second & 0x7F
    if length == 126:
        length = struct.unpack("!H", read_exact(connection, 2))[0]
    elif length == 127:
        length = struct.unpack("!Q", read_exact(connection, 8))[0]
    mask = read_exact(connection, 4)
    encoded = read_exact(connection, length)
    return first & 0x0F, bytes(
        value ^ mask[index % 4] for index, value in enumerate(encoded)
    )


class PhaseFFixtureHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    assets = {
        route: (ROOT / relative).read_bytes()
        for route, relative in CHECKER.ASSETS.items()
    }
    connections = 0

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if self.path == "/video":
            self.handle_websocket()
            return
        body = self.assets.get(self.path)
        if body is None:
            self.send_error(404)
            return
        media = {
            "/": "text/html",
            "/style.css": "text/css",
            "/app.js": "text/javascript",
            "/frame_protocol.js": "text/javascript",
            "/webgl2_presenter.js": "text/javascript",
        }[self.path]
        self.send_response(200)
        self.send_header("Content-Type", media)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_websocket(self) -> None:
        key = self.headers.get("Sec-WebSocket-Key")
        if key is None:
            self.send_error(400)
            return
        accept = base64.b64encode(
            hashlib.sha1(
                (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")
            ).digest()
        ).decode("ascii")
        self.send_response(101, "Switching Protocols")
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", accept)
        self.end_headers()
        self.wfile.flush()

        opcode, credit = read_client_frame(self.connection)
        if opcode != 1 or credit != b"frame":
            raise AssertionError("qualification client sent the wrong credit")

        type(self).connections += 1
        sequence = type(self).connections
        payload = bytes(range(12))
        message = struct.pack(
            "<4sBBBBIHHIIII",
            b"EVF1", 1, 32, 1, 3, sequence, 2, 2, 6, len(payload), 16667, 0,
        ) + payload
        split = 19
        self.connection.sendall(bytes((0x02, split)) + message[:split])
        tail = message[split:]
        self.connection.sendall(bytes((0x80, len(tail))) + tail)

        # Remaining connected but silent proves that no-credit quiet detection
        # is testing absence of a frame rather than an early server close.
        time.sleep(0.15)
        self.close_connection = True


class P4BrowserRuntimeCheckerTests(unittest.TestCase):
    def test_evf1_parser_rejects_trailing_bytes(self) -> None:
        payload = bytes(range(12))
        message = struct.pack(
            "<4sBBBBIHHIIII",
            b"EVF1", 1, 32, 1, 3, 1, 2, 2, 6, len(payload), 16667, 0,
        ) + payload + b"x"
        with self.assertRaisesRegex(RuntimeError, "length mismatch"):
            CHECKER.parse_evf1(message)

    def test_complete_cli_against_fragmenting_local_fixture(self) -> None:
        PhaseFFixtureHandler.connections = 0
        server = ThreadingHTTPServer(("127.0.0.1", 0), PhaseFFixtureHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory(prefix="phase-f-live-check-") as directory:
                output = Path(directory) / "result.json"
                process = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--host", "127.0.0.1",
                        "--port", str(server.server_port),
                        "--timeout", "2",
                        "--quiet-seconds", "0.05",
                        "--output", str(output),
                    ],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                self.assertEqual(process.returncode, 0, process.stderr)
                result = json.loads(output.read_text(encoding="utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(PhaseFFixtureHandler.connections, 2)
        self.assertEqual(result["result"], "pass")
        self.assertFalse(result["endpoint_recorded"])
        self.assertEqual(len(result["assets"]), 5)
        self.assertEqual(
            [frame["sequence"] for frame in result["connections"]], [1, 2]
        )


if __name__ == "__main__":
    unittest.main()
