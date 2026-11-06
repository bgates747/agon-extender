#!/usr/bin/env python3
"""Small, explicitly started TCP BBS for an unchanged serial/Wi-Fi terminal.

Experimental NET-005 fixture: printable ASCII, no Telnet or shell protocol.
The Agon terminal owns local echo. No unsolicited updates, payload acknowledgments
or UART flow-control scheme are added. Notes live only in the selected Pi folder.
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import sqlite3
import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

MAX_COMMAND = 80
MAX_NOTE = 60
RECENT_NOTES = 3
PROMPT = b"bbs> "


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def duration(seconds):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days}d {hours:02}:{minutes:02}:{seconds:02}"


class BBS:
    def __init__(self, data_dir, *, build_id="source-checkout", timezone_name="UTC"):
        self.data_dir = Path(data_dir)
        self.zone = ZoneInfo(timezone_name)
        self.build_id = build_id
        self.source_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        self.server = None
        self.active = None
        self.clients = set()
        self.started = time.monotonic()
        self.started_utc = utc_now()
        self.service_id = f"{time.time_ns()}-{os.getpid()}"
        self.closed = False
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.data_dir / "notes.sqlite3")
        self.db.execute("CREATE TABLE IF NOT EXISTS notes "
                        "(id INTEGER PRIMARY KEY, written TEXT NOT NULL, text TEXT NOT NULL)")
        self.db.commit()
        self.events = (self.data_dir / "events.jsonl").open("a", encoding="utf-8")

    def event(self, event, **fields):
        self.events.write(json.dumps(dict(event=event, service_id=self.service_id,
                                         utc=utc_now(), **fields)) + "\n")
        self.events.flush()

    async def start(self, bind="127.0.0.1", port=2323):
        self.server = await asyncio.start_server(self.handle, bind, port, limit=1024)
        self.event("service_start", build_id=self.build_id, source_sha256=self.source_sha256,
                   pid=os.getpid(), addresses=[list(s.getsockname()) for s in self.server.sockets])
        return self

    def ready(self):
        return dict(build_id=self.build_id, status="experimental", pid=os.getpid(),
                    source_sha256=self.source_sha256, started_utc=self.started_utc,
                    addresses=[list(s.getsockname()) for s in self.server.sockets],
                    data_dir=str(self.data_dir.resolve()))

    def command(self, line):
        """Return printable response lines and whether this TCP session ends."""
        verb, _, argument = line.partition(" ")
        verb = verb.lower()
        argument = argument.strip()
        if not verb:
            return [], False
        if verb == "help" and not argument:
            return ["help | time | uptime | note TEXT | notes | quit",
                    "Notes: 1-60 printable characters; notes shows the last three."], False
        if verb == "time" and not argument:
            return [datetime.now(self.zone).strftime("%Y-%m-%d %H:%M:%S %Z")], False
        if verb == "uptime" and not argument:
            rows = ["BBS uptime " + duration(time.monotonic() - self.started)]
            try:
                seconds = float(Path("/proc/uptime").read_text().split()[0])
            except (OSError, ValueError, IndexError):
                pass
            else:
                rows.insert(0, "Pi uptime  " + duration(seconds))
            return rows, False
        if verb == "note":
            if not 1 <= len(argument) <= MAX_NOTE:
                return ["ERR use note TEXT, with 1-60 printable characters."], False
            written = datetime.now(self.zone).isoformat(timespec="seconds")
            cursor = self.db.execute("INSERT INTO notes(written,text) VALUES(?,?)",
                                     (written, argument))
            self.db.commit()  # A saved reply follows the actual committed write.
            self.event("note_saved", note_id=cursor.lastrowid)
            return [f"Saved note {cursor.lastrowid}."], False
        if verb == "notes" and not argument:
            rows = self.db.execute("SELECT id,written,text FROM notes ORDER BY id DESC LIMIT ?",
                                   (RECENT_NOTES,)).fetchall()
            if not rows:
                return ["No notes yet. Try: note Hello from Console8"], False
            display = []
            for i, stamp, text in reversed(rows):
                display.extend([f"#{i} {stamp[5:10]} {stamp[11:16]}", text])
            return display, False
        if verb == "quit" and not argument:
            return ["Goodbye. Leave modem data mode before exiting the terminal."], True
        return ["Unknown command. Type help."], False

    async def send(self, writer, rows, *, prompt=True):
        body = "\r\n".join(rows)
        writer.write((body + ("\r\n" if rows else "")).encode("ascii")
                     + (PROMPT if prompt else b""))
        await writer.drain()

    async def handle(self, reader, writer):
        task = asyncio.current_task()
        self.clients.add(task)
        admitted = self.active is None and not self.closed
        session = f"{time.time_ns()}"
        began = time.monotonic()
        reason = "disconnected"
        if admitted:
            self.active = task
            self.event("session_start", session=session)
        try:
            if not admitted:
                await self.send(writer, ["BUSY: one terminal is already connected."], prompt=False)
                return
            await self.send(writer, [self.build_id + " (experimental)", "Pi Wi-Fi BBS. Type help."])
            line = bytearray()
            invalid = False
            after_cr = False
            while chunk := await reader.read(256):
                for char in chunk:
                    if after_cr and char == 10:
                        after_cr = False
                        continue
                    after_cr = char == 13
                    if char in (10, 13):
                        if invalid:
                            rows, done = ["ERR printable ASCII only; command limit 80 characters."], False
                        else:
                            rows, done = self.command(line.decode("ascii"))
                        line.clear()
                        invalid = False
                        await self.send(writer, rows, prompt=not done)
                        if done:
                            reason = "quit"
                            return
                    elif char in (8, 127):
                        if line:
                            line.pop()
                    elif not 32 <= char <= 126 or len(line) >= MAX_COMMAND:
                        invalid = True
                    elif not invalid:
                        line.append(char)
        except (ConnectionError, BrokenPipeError):
            reason = "connection_lost"
        except sqlite3.Error as exc:
            reason = "storage_error"
            self.event("storage_error", session=session, error=str(exc))
            with contextlib.suppress(ConnectionError):
                await self.send(writer, ["ERR notes storage unavailable."], prompt=False)
        except asyncio.CancelledError:
            reason = "service_stopped"
            raise
        finally:
            writer.close()
            with contextlib.suppress(ConnectionError, asyncio.CancelledError):
                await writer.wait_closed()
            if admitted:
                self.event("session_end", session=session, reason=reason,
                           duration_seconds=time.monotonic() - began)
                self.active = None
            self.clients.discard(task)

    async def close(self):
        if self.closed:
            return
        self.closed = True
        if self.server:
            self.server.close()
        # asyncio also waits for client transports: close them before joining
        # the listener, otherwise an idle terminal can prevent service shutdown.
        for task in list(self.clients):
            task.cancel()
        await asyncio.gather(*list(self.clients), return_exceptions=True)
        if self.server:
            await self.server.wait_closed()
        self.event("service_end", duration_seconds=time.monotonic() - self.started)
        self.db.close()
        self.events.close()


async def run(args):
    app = BBS(args.data_dir, build_id=args.build_id, timezone_name=args.timezone)
    stopped = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stopped.set)
    try:
        await app.start(args.bind, args.port)
        ready = app.ready()
        if args.ready_file:
            with args.ready_file.open("x", encoding="utf-8") as output:
                json.dump(ready, output, indent=2)
                output.write("\n")
        print(json.dumps(ready), flush=True)
        await stopped.wait()
    finally:
        await app.close()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.remove_signal_handler(sig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=2323)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--timezone", default="UTC")
    parser.add_argument("--build-id", default="source-checkout")
    parser.add_argument("--ready-file", type=Path)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    if not args.build_id.isascii() or not args.build_id.isprintable() or len(args.build_id) > 60:
        parser.error("build ID must be at most 60 printable ASCII characters")
    try:
        ZoneInfo(args.timezone)
    except (ZoneInfoNotFoundError, ValueError):
        parser.error("unknown timezone")
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
