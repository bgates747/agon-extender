"""Minimal installed P4 WebSocket video acquisition and EVF1 validation."""

import base64
import hashlib
import os
from pathlib import Path
import socket
import struct
import time
from urllib.parse import urlparse


def _exact(stream, count):
    data = bytearray()
    while len(data) < count:
        part = stream.recv(count - len(data))
        if not part:
            raise EOFError("video WebSocket closed")
        data.extend(part)
    return bytes(data)


def _send(stream, data, opcode=1):
    mask = os.urandom(4)
    if len(data) >= 126:
        raise ValueError("qualification request is too large")
    stream.sendall(bytes((128 | opcode, 128 | len(data))) + mask +
                   bytes(value ^ mask[index % 4] for index, value in enumerate(data)))


def _receive(stream):
    result = bytearray()
    while True:
        first, second = _exact(stream, 2)
        length = second & 127
        if length == 126:
            length = struct.unpack("!H", _exact(stream, 2))[0]
        elif length == 127:
            length = struct.unpack("!Q", _exact(stream, 8))[0]
        if length > 3_000_000 or second & 128:
            raise ValueError("invalid server video frame")
        data = _exact(stream, length)
        opcode = first & 15
        if opcode == 9:
            _send(stream, data, 10)
            continue
        if opcode == 8:
            raise EOFError("server closed video WebSocket")
        if opcode not in (0, 2):
            continue
        result.extend(data)
        if first & 128:
            return bytes(result)


def decode_evf(raw):
    if len(raw) < 32 or raw[:4] != b"EVF1":
        raise ValueError("invalid EVF1 header")
    version, header, pixel_format, flags = raw[4:8]
    sequence, width, height, stride, size, period, reserved = struct.unpack_from(
        "<IHHIIII", raw, 8)
    bytes_per_pixel = 1 if pixel_format == 2 else 3
    if (version != 1 or header != 32 or pixel_format not in (1, 2) or
            not flags & 1 or flags & ~3 or reserved or
            not (0 < width <= 1024 and 0 < height <= 768) or
            stride != width * bytes_per_pixel or size != stride * height or
            len(raw) != 32 + size):
        raise ValueError("invalid EVF1 metadata or size")
    pixels = raw[32:]
    if pixel_format == 2 and any(value > 63 for value in pixels):
        raise ValueError("invalid RGB222 pixel")
    if pixel_format == 1 and any(value % 85 for value in pixels):
        raise ValueError("non-canonical RGB888 pixel")
    return {"sequence": sequence, "width": width, "height": height,
            "format": pixel_format, "period": period,
            "sha256": hashlib.sha256(pixels).hexdigest()}


class VideoSession:
    """One retained browser-video consumer for transition qualification."""

    def __init__(self, url):
        self.parsed = urlparse(url)
        self.stream = None

    def __enter__(self):
        parsed = self.parsed
        self.stream = socket.create_connection(
            (parsed.hostname, parsed.port or 80), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        self.stream.sendall(
            f"GET /video HTTP/1.1\r\nHost: {parsed.netloc}\r\nUpgrade: websocket\r\n"
            f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n".encode())
        response = bytearray()
        while not response.endswith(b"\r\n\r\n"):
            response.extend(_exact(self.stream, 1))
        expected = base64.b64encode(hashlib.sha1(
            (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest())
        if b"101 Switching Protocols" not in response or expected not in response:
            self.stream.close()
            self.stream = None
            raise RuntimeError("video WebSocket upgrade failed")
        return self

    def frame(self, path):
        _send(self.stream, b"frame")
        raw = _receive(self.stream)
        Path(path).write_bytes(raw)
        return decode_evf(raw)

    def __exit__(self, exc_type, exc, traceback):
        if self.stream is None:
            return
        try:
            try:
                _send(self.stream, struct.pack("!H", 1000), 8)
            except OSError:
                pass
        finally:
            self.stream.close()
            self.stream = None


def capture(url, output, count=3):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    records = []
    with VideoSession(url) as session:
        for index in range(count):
            records.append(session.frame(output / f"{index:02}.evf"))
            time.sleep(0.2)
    if len({item["sequence"] for item in records}) != len(records):
        raise RuntimeError("video endpoint returned a stale frame generation")
    return records
