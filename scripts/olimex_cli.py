"""Command-correlated Legacy MOS observation through the printer mirror."""

import re
import secrets
import time

PROMPT = re.compile(rb"(?:/[^*\r\n]* )?\*")
LINES = re.compile(rb"[\r\n]+")
LIMIT = 65536


class CliError(RuntimeError):
    """The CLI action returned an error or could not be confirmed."""


def returned_output(captured, command, prompt):
    """Separate complete commands/output lines from a partial tail."""
    lines = LINES.split(captured)
    echo = command.encode("ascii").lower()
    for index, line in enumerate(lines[:-1]):
        prefix = line[:-len(echo)]
        if line.lower().endswith(echo) and (
            not prefix or
            (PROMPT.fullmatch(prefix) if prompt is None else prefix.lower() == prompt.lower())
        ):
            return lines[index + 1:-1], lines[-1]
    return [], None


def find_witness(captured, command, marker):
    lines, tail = returned_output(captured, command, None)
    if (marker in lines and tail is not None and PROMPT.fullmatch(tail)
            and not any(line for line in lines[lines.index(marker) + 1:])):
        return tail
    return None


def command_result(captured, command, prompt, *, success=None, failure=None, next_prompt=None):
    """Confirm a quiet LOAD or the requested fixture completion and prompt."""
    lines, tail = returned_output(captured, command, prompt)
    if tail is None:
        return False
    output = [line for line in lines if line]
    failed = next((line for line in output if failure and line.startswith(failure)), None)
    if failed is not None:
        raise CliError(failed.decode("ascii", "backslashreplace"))
    if success is None and output:
        raise CliError(output[0].decode("ascii", "backslashreplace"))
    if tail != (next_prompt if next_prompt is not None else prompt):
        return False
    if success is not None and (not output or output[-1] != success):
        detail = b" / ".join(output).decode("ascii", "backslashreplace")
        raise CliError(f"CLI returned without the expected completion line: {detail}")
    return True


def rename_result(captured, command, prompt, source, destination):
    """Witness the RENAME banner and a fresh prompt without an intervening error."""
    lines, tail = returned_output(captured, command, prompt)
    if tail is None:
        return False
    info = f"Moving {source} to {destination}".encode("ascii")
    output = [line for line in lines if line]
    for index, line in enumerate(output):
        if index != 0 or line.lower() != info.lower():
            raise CliError(line.decode("ascii", "backslashreplace"))
    return output != [] and tail == prompt


def marker_bytes(marker):
    if isinstance(marker, str):
        marker = marker.encode("ascii")
    if not isinstance(marker, bytes) or not re.fullmatch(rb"[ -~]+", marker):
        raise ValueError("Completion markers must be nonempty printable ASCII text or bytes")
    return marker


def completion_markers(success, failure):
    success, failure = marker_bytes(success), marker_bytes(failure)
    if success.startswith(failure):
        raise ValueError("Fixture success matches its failure prefix")
    return success, failure


class Observer:
    def __init__(self, reader, transcript, dispatch):
        self.reader = reader
        self.transcript = transcript
        self.dispatch = dispatch

    def capture(self, data):
        self.transcript.write(data)
        self.transcript.flush()

    def discard_buffered_input(self):
        # Preserve pre-existing output in the log, outside the command window.
        discarded = 0
        while queued := self.reader.in_waiting:
            data = self.reader.read(min(queued, 1024))
            if not data:
                break
            self.capture(data)
            discarded += len(data)
            if discarded > LIMIT:
                raise CliError("Legacy serial stream did not become idle before dispatch")

    def exchange(self, label, command, predicate, seconds, *, deferred=None):
        self.discard_buffered_input()
        self.dispatch(label, command)
        captured = bytearray()
        result = self.receive(label, captured, predicate, seconds)
        if deferred:
            marker, trailing, tail_seconds = deferred
            if not trailing(bytes(captured)):
                self.receive(f"{label} UART terminator {marker!r}", captured, trailing, tail_seconds)
        return result

    def receive(self, label, captured, predicate, seconds, *, poll=False):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            data = self.reader.read(1024)
            if not data and not poll:
                continue
            if data:
                self.capture(data)
                captured.extend(data)
            if len(captured) > LIMIT:
                raise CliError(f"Legacy serial evidence cap reached during {label}")
            result = predicate(bytes(captured))
            if result:
                return result
        raise CliError(f"No command-correlated Legacy CLI result for {label}")

    def witness(self, label="witness"):
        marker = secrets.token_hex(3).upper().encode("ascii")
        command = "VDU " + " ".join(str(value) for value in (*marker, 13, 10))
        return self.exchange(label, command, lambda data: find_witness(
            data, command, marker), 15)

    def quiet_load(self, command, prompt):
        return self.exchange("load", command, lambda data: command_result(
            data, command, prompt), 15)

    def change_directory(self, label, directory, prompt):
        command = f"CD {directory}"
        expected = f"{directory} *".encode("ascii")

        def returned(data):
            _, tail = returned_output(data, command, prompt)
            matched = tail is not None and tail.lower() == expected.lower()
            if command_result(data, command, prompt, next_prompt=tail if matched else expected):
                return tail
            return None

        return self.exchange(label, command, returned, 15)

    def run(self, command, prompt, success, failure, seconds, *, uart_end=None):
        success, failure = completion_markers(success, failure)
        deferred = None
        if uart_end:
            prefix, marker = (marker_bytes(uart_end[key]) for key in ("prefix", "line"))
            if not marker.startswith(prefix) or not 0 < uart_end["seconds"] <= 120:
                raise ValueError("Invalid UART terminator or observation bound")
            # Native logs can interrupt the mirrored prompt or a MOS line
            # between any two characters. Remove only the configured records
            # from the CLI view and preserve every raw byte in the transcript.
            diagnostics = re.compile(re.escape(prefix) + rb"[^\r\n]*(?:\r\n|\r|\n|$)")

            def terminator(data):
                lines, _ = returned_output(data, command, prompt)
                return any(line.partition(prefix)[1:] == (prefix, marker[len(prefix):])
                           for line in lines)

            deferred = marker, terminator, uart_end["seconds"]

        def complete(data):
            if uart_end:
                data = diagnostics.sub(b"", data).rstrip(b"\r\n")
            return command_result(data, command, prompt, success=success, failure=failure)

        return self.exchange("run", command, complete, seconds, deferred=deferred)

    def run_to_listener(self, batch, seconds, uart_end, listener_status):
        marker = marker_bytes(uart_end["line"])
        if not 0 < uart_end["seconds"] <= 120:
            raise ValueError("Invalid UART observation bound")
        self.discard_buffered_input()
        self.dispatch("run", f"EXEC {batch}")
        captured = bytearray()
        next_poll = 0.0

        def online(_):
            nonlocal next_poll
            now = time.monotonic()
            if now < next_poll:
                return None
            next_poll = now + 0.2
            status = listener_status()
            return status if status["online"] else None

        status = self.receive("post-RUN listener admission", captured, online, seconds, poll=True)
        line = re.compile(rb"(?:^|[\r\n])" + re.escape(marker) + rb"(?=[\r\n])")
        if not line.search(captured):
            self.receive(f"native UART terminator {marker!r}", captured, line.search, uart_end["seconds"])
        return status

    def mirror_off(self, prompt, label="mirror-off"):
        command = "VDU 3"

        def echo_return(data):
            _, tail = returned_output(data, command, prompt)
            return tail is not None

        # The output stream ends when this command takes effect. The subsequent
        # foreground listener/read/EXIT supplies the independent CLI handback.
        self.exchange(label, command, echo_return, 10)
