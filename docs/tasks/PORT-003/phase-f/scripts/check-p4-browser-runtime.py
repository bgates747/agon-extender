#!/usr/bin/env python3
"""Check Phase F assets and EVF1 delivery from a live P4 over trusted HTTP.

This is qualification tooling, not a product client. It uses only the Python
standard library, emits no supplied address, and never sends a VDU command or
touches a physical transport GPIO. The P4 must already have been deployed and
its observed DHCP address must be supplied explicitly by the operator.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
from typing import Any
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[5]
ASSETS = {
    "/": "vdp/video/extender/web/index.html",
    "/style.css": "vdp/video/extender/web/style.css",
    "/app.js": "vdp/video/extender/web/app.js",
    "/frame_protocol.js": "vdp/video/extender/web/frame_protocol.js",
    "/webgl2_presenter.js": "vdp/video/extender/web/webgl2_presenter.js",
}
MAX_MESSAGE_BYTES = 32 + 1024 * 768 * 3


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class WebSocket:
    def __init__(self, host: str, port: int, timeout: float) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = socket.create_connection((host, port), timeout=timeout)
        self.buffer = bytearray()
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = (
            "GET /video HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        ).encode("ascii")
        self.socket.sendall(request)
        response = self._read_until(b"\r\n\r\n", 16384)
        head, remainder = response.split(b"\r\n\r\n", 1)
        self.buffer.extend(remainder)
        lines = head.decode("iso-8859-1").split("\r\n")
        if not lines[0].startswith("HTTP/1.1 101 "):
            raise RuntimeError(f"WebSocket upgrade failed: {lines[0]}")
        headers = {}
        for line in lines[1:]:
            name, value = line.split(":", 1)
            headers[name.lower()] = value.strip()
        expected = base64.b64encode(
            hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
        ).decode("ascii")
        if headers.get("sec-websocket-accept") != expected:
            raise RuntimeError("invalid WebSocket accept value")

    def _read_until(self, delimiter: bytes, maximum: int) -> bytes:
        data = bytearray(self.buffer)
        self.buffer.clear()
        while delimiter not in data:
            if len(data) >= maximum:
                raise RuntimeError("WebSocket HTTP header exceeds bound")
            block = self.socket.recv(4096)
            if not block:
                raise RuntimeError("connection closed during WebSocket upgrade")
            data.extend(block)
        return bytes(data)

    def _read_exact(self, size: int) -> bytes:
        while len(self.buffer) < size:
            block = self.socket.recv(min(65536, size - len(self.buffer)))
            if not block:
                raise RuntimeError("WebSocket closed during frame")
            self.buffer.extend(block)
        result = bytes(self.buffer[:size])
        del self.buffer[:size]
        return result

    def send_text(self, payload: bytes) -> None:
        if len(payload) > 125:
            raise ValueError("qualification request must be a short control message")
        mask = os.urandom(4)
        encoded = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        self.socket.sendall(bytes((0x81, 0x80 | len(payload))) + mask + encoded)

    def _read_frame(self) -> tuple[bool, int, bytes]:
        first, second = self._read_exact(2)
        if first & 0x70:
            raise RuntimeError("server set reserved WebSocket bits")
        if second & 0x80:
            raise RuntimeError("server WebSocket frame must not be masked")
        length = second & 0x7F
        if length == 126:
            length = struct.unpack("!H", self._read_exact(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self._read_exact(8))[0]
        if length > MAX_MESSAGE_BYTES:
            raise RuntimeError("server WebSocket frame exceeds EVF1 bound")
        return bool(first & 0x80), first & 0x0F, self._read_exact(length)

    def read_binary_message(self) -> bytes:
        message = bytearray()
        initial = True
        while True:
            final, opcode, payload = self._read_frame()
            if opcode == 0x9:
                self._send_control(0xA, payload)
                continue
            if opcode == 0x8:
                raise RuntimeError("server closed before EVF1 message")
            expected = 0x2 if initial else 0x0
            if opcode != expected:
                raise RuntimeError(f"unexpected WebSocket opcode {opcode}")
            initial = False
            message.extend(payload)
            if len(message) > MAX_MESSAGE_BYTES:
                raise RuntimeError("reassembled EVF1 message exceeds bound")
            if final:
                return bytes(message)

    def _send_control(self, opcode: int, payload: bytes) -> None:
        mask = os.urandom(4)
        encoded = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        self.socket.sendall(bytes((0x80 | opcode, 0x80 | len(payload))) + mask + encoded)

    def expect_quiet(self, seconds: float) -> None:
        previous = self.socket.gettimeout()
        self.socket.settimeout(seconds)
        try:
            if self.buffer:
                raise RuntimeError("received an unsolicited WebSocket frame")
            try:
                data = self.socket.recv(1)
            except TimeoutError:
                return
            if data:
                raise RuntimeError("received an unsolicited WebSocket frame")
            raise RuntimeError("WebSocket closed during no-credit interval")
        finally:
            self.socket.settimeout(previous)

    def close(self) -> None:
        try:
            self._send_control(0x8, struct.pack("!H", 1000))
        except OSError:
            pass
        self.socket.close()


def parse_evf1(message: bytes) -> dict[str, Any]:
    if len(message) < 32:
        raise RuntimeError("truncated EVF1 message")
    fields = struct.unpack_from("<4sBBBBIHHIIII", message)
    magic, version, header_bytes, pixel_format, flags, sequence, width, height, stride, payload_bytes, period, reserved = fields
    if magic != b"EVF1" or version != 1 or header_bytes != 32 or pixel_format != 1:
        raise RuntimeError("invalid EVF1 identity fields")
    if flags & ~3 or not flags & 1:
        raise RuntimeError("invalid EVF1 flags")
    if not (1 <= width <= 1024 and 1 <= height <= 768):
        raise RuntimeError("invalid EVF1 dimensions")
    if stride < width * 3 or payload_bytes != stride * height:
        raise RuntimeError("invalid EVF1 payload arithmetic")
    if payload_bytes > 1024 * 768 * 3 or reserved != 0:
        raise RuntimeError("invalid EVF1 bounds or reserved field")
    if len(message) != header_bytes + payload_bytes:
        raise RuntimeError("EVF1 message length mismatch")
    payload = message[header_bytes:]
    return {
        "sequence": sequence,
        "width": width,
        "height": height,
        "stride_bytes": stride,
        "payload_bytes": payload_bytes,
        "present_period_us": period,
        "payload_sha256": sha256(payload),
    }


def receive_one(host: str, port: int, timeout: float, quiet: float) -> dict[str, Any]:
    client = WebSocket(host, port, timeout)
    try:
        client.send_text(b"frame")
        frame = parse_evf1(client.read_binary_message())
        client.expect_quiet(quiet)
        return frame
    finally:
        client.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=80)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--quiet-seconds", type=float, default=1.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    assets = []
    for route, relative in ASSETS.items():
        with urlopen(f"http://{args.host}:{args.port}{route}", timeout=args.timeout) as response:
            observed = response.read()
            status = response.status
            media_type = response.headers.get_content_type()
        expected = (ROOT / relative).read_bytes()
        if status != 200 or observed != expected:
            raise RuntimeError(f"asset mismatch at {route}")
        assets.append({
            "route": route,
            "source": relative,
            "bytes": len(observed),
            "sha256": sha256(observed),
            "media_type": media_type,
        })

    first = receive_one(args.host, args.port, args.timeout, args.quiet_seconds)
    second = receive_one(args.host, args.port, args.timeout, args.quiet_seconds)
    report = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_f_live_browser_check",
        "generated_by": "docs/tasks/PORT-003/phase-f/scripts/check-p4-browser-runtime.py",
        "scope": "direct P4 assets, EVF1 delivery, no-credit quiet interval, and reconnect",
        "endpoint_recorded": False,
        "assets": assets,
        "connections": [first, second],
        "checks": {
            "assets_match_committed_sources": True,
            "evf1_messages_valid": True,
            "no_unsolicited_frame_without_credit": True,
            "reconnect_delivers_frame": True,
        },
        "result": "pass",
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
