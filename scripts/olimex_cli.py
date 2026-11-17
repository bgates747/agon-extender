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


def command_result(captured, command, prompt, *, success=None, failure=None):
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
    if tail != prompt:
        return False
    if success is not None and (not output or output[-1] != success):
        detail = b" / ".join(output).decode("ascii", "backslashreplace")
        raise CliError(f"CLI returned without the expected completion line: {detail}")
    return True


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

    def exchange(self, label, command, predicate, seconds):
        self.discard_buffered_input()
        self.dispatch(label, command)
        captured = bytearray()
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            data = self.reader.read(1024)
            if not data:
                continue
            self.capture(data)
            captured.extend(data)
            if len(captured) > LIMIT:
                raise CliError(f"Legacy serial evidence cap reached during {label}")
            result = predicate(bytes(captured))
            if result:
                return result
        raise CliError(f"No command-correlated Legacy CLI result for {label}")

    def witness(self):
        marker = secrets.token_hex(3).upper().encode("ascii")
        command = "VDU " + " ".join(str(value) for value in (*marker, 13, 10))
        return self.exchange("witness", command, lambda data: find_witness(
            data, command, marker), 15)

    def quiet_load(self, command, prompt):
        return self.exchange("load", command, lambda data: command_result(
            data, command, prompt), 15)

    def run(self, command, prompt, success, failure, seconds):
        return self.exchange("run", command, lambda data: command_result(
            data, command, prompt, success=success, failure=failure), seconds)

    def mirror_off(self, prompt):
        command = "VDU 3"

        def echo_return(data):
            _, tail = returned_output(data, command, prompt)
            return tail is not None

        # The output stream ends when this command takes effect. The subsequent
        # foreground listener/read/EXIT supplies the independent CLI handback.
        self.exchange("mirror-off", command, echo_return, 10)
