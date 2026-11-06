"""Real loopback checks of the host fixture, with no UART/Agon/emulator access."""
import asyncio
import importlib.util
import json
import signal
import sys
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "scripts/wifi_bbs.py"
spec = importlib.util.spec_from_file_location("wifi_bbs", SOURCE)
bbs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bbs)


class BBSChecks(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.app = bbs.BBS(self.folder, build_id="loopback-check", timezone_name="America/New_York")
        await self.app.start(port=0)
        self.port = self.app.server.sockets[0].getsockname()[1]
        self.writers = []

    async def asyncTearDown(self):
        await self.app.close()
        for writer in self.writers:
            writer.close()
        self.temp.cleanup()

    async def connect(self):
        reader, writer = await asyncio.open_connection("127.0.0.1", self.port)
        self.writers.append(writer)
        return reader, writer

    async def prompt(self, reader):
        return await asyncio.wait_for(reader.readuntil(bbs.PROMPT), 2)

    async def session(self):
        reader, writer = await self.connect()
        self.assertIn(b"Pi Wi-Fi BBS", await self.prompt(reader))
        return reader, writer

    async def send(self, reader, writer, line):
        writer.write(line)
        await writer.drain()
        return await self.prompt(reader)

    async def test_help_time_uptime_and_unknown(self):
        reader, writer = await self.session()
        self.assertIn(b"note TEXT", await self.send(reader, writer, b"help\r\n"))
        self.assertRegex((await self.send(reader, writer, b"time\n")).decode(),
                         r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [A-Z]+")
        self.assertIn(b"BBS uptime", await self.send(reader, writer, b"uptime\r"))
        self.assertIn(b"Unknown command", await self.send(reader, writer, b"shell\r"))

    async def test_fragmented_crlf_backspace_and_pipeline(self):
        reader, writer = await self.session()
        for piece in (b"not", b"e ABx", b"\x08C", b"\r"):
            writer.write(piece)
            await writer.drain()
            await asyncio.sleep(.01)
        self.assertIn(b"Saved note 1", await self.prompt(reader))
        # The LF arrives in another TCP read, then a second complete command.
        writer.write(b"\nnotes\r\n")
        await writer.drain()
        reply = await self.prompt(reader)
        self.assertIn(b"ABC", reply)
        self.assertNotIn(b"ABx", reply)
        writer.write(b"help\ntime\n")
        await writer.drain()
        self.assertIn(b"note TEXT", await self.prompt(reader))
        self.assertRegex((await self.prompt(reader)).decode(), r"\d{4}-\d{2}-\d{2}")

    async def test_notes_persist_after_restart_and_recent_three_only(self):
        reader, writer = await self.session()
        self.assertIn(b"No notes yet", await self.send(reader, writer, b"notes\n"))
        for text in (b"oldest", b"alpha", b"beta", b"gamma"):
            self.assertIn(b"Saved note", await self.send(reader, writer, b"note " + text + b"\n"))
        await self.app.close()
        self.app = bbs.BBS(self.folder, build_id="restart-check")
        await self.app.start(port=0)
        self.port = self.app.server.sockets[0].getsockname()[1]
        reader, writer = await self.session()
        reply = await self.send(reader, writer, b"notes\n")
        self.assertNotIn(b"oldest", reply)
        self.assertLess(reply.index(b"alpha"), reply.index(b"beta"))
        self.assertLess(reply.index(b"beta"), reply.index(b"gamma"))

    async def test_bad_lines_recover_without_saving_partial_notes(self):
        reader, writer = await self.session()
        for line in (b"note " + b"x" * 200 + b"\n", b"note hi\xff\n"):
            self.assertIn(b"ERR printable ASCII", await self.send(reader, writer, line))
        self.assertIn(b"ERR use note", await self.send(reader, writer, b"note " + b"x" * 61 + b"\n"))
        self.assertIn(b"No notes yet", await self.send(reader, writer, b"notes\n"))
        self.assertIn(b"Saved note", await self.send(reader, writer, b"note " + b"x" * 60 + b"\n"))
        self.assertIn(b"note TEXT", await self.send(reader, writer, b"help\n"))

    async def test_second_client_refused_without_disturbing_first(self):
        reader, writer = await self.session()
        other_reader, other_writer = await self.connect()
        reply = await asyncio.wait_for(other_reader.read(), 2)
        self.assertIn(b"BUSY", reply)
        self.assertIn(b"note TEXT", await self.send(reader, writer, b"help\n"))
        other_writer.close()

    async def test_quit_then_reconnect_and_partial_eof(self):
        reader, writer = await self.session()
        writer.write(b"quit\r\n")
        await writer.drain()
        self.assertIn(b"Goodbye", await asyncio.wait_for(reader.read(), 2))
        reader, writer = await self.session()
        writer.write(b"note incomplete")
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        # Wait for actual handler completion, rather than assuming TCP EOF timing.
        while self.app.active is not None:
            await asyncio.sleep(.01)
        reader, writer = await self.session()
        self.assertIn(b"No notes yet", await self.send(reader, writer, b"notes\n"))

    async def test_real_cli_readiness_and_sigterm(self):
        await self.app.close()
        ready = self.folder / "cli-ready.json"
        data = self.folder / "cli-data"
        proc = await asyncio.create_subprocess_exec(
            sys.executable, str(SOURCE), "--bind", "127.0.0.1", "--port", str(self.port),
            "--data-dir", str(data), "--ready-file", str(ready), "--build-id", "cli-check",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        try:
            async with asyncio.timeout(5):
                while not ready.exists():
                    if proc.returncode is not None:
                        self.fail((await proc.communicate())[1].decode())
                    await asyncio.sleep(.01)
            receipt = json.loads(ready.read_text())
            self.assertEqual(proc.pid, receipt["pid"])
            self.assertEqual("cli-check", receipt["build_id"])
            reader, writer = await self.session()
            self.assertIn(b"note TEXT", await self.send(reader, writer, b"help\n"))
            proc.send_signal(signal.SIGTERM)
            stdout, stderr = await asyncio.wait_for(proc.communicate(), 3)
            self.assertEqual(0, proc.returncode, stderr.decode())
            self.assertIn(b"cli-check", stdout)
            self.assertEqual(b"", await asyncio.wait_for(reader.read(), 2))
            events = [json.loads(row) for row in (data / "events.jsonl").read_text().splitlines()]
            self.assertEqual("service_end", events[-1]["event"])
        finally:
            if proc.returncode is None:
                proc.kill()
                await proc.wait()

    async def test_stop_closes_client_and_records_actual_durations(self):
        reader, _ = await self.session()
        await asyncio.wait_for(self.app.close(), 2)
        self.assertEqual(b"", await asyncio.wait_for(reader.read(), 2))
        events = [json.loads(line) for line in (self.folder / "events.jsonl").read_text().splitlines()]
        self.assertEqual("service_start", events[0]["event"])
        self.assertEqual("service_end", events[-1]["event"])
        session_end = next(event for event in events if event["event"] == "session_end")
        self.assertEqual("service_stopped", session_end["reason"])
        self.assertGreaterEqual(session_end["duration_seconds"], 0)
        self.assertGreaterEqual(events[-1]["duration_seconds"], session_end["duration_seconds"])
        self.assertFalse(self.app.clients)


if __name__ == "__main__":
    unittest.main()
