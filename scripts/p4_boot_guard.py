"""Reject a failed P4 startup before a caller performs another readiness poll.

Use after each serial read, before service probes. A startup brand/console marker
can reappear after a panic; it is not readiness. This guard never resets, probes,
retries, flashes or releases another processor.
"""
from __future__ import annotations


def check_startup(captured: bytes, console_marker: bytes) -> None:
    if not console_marker:
        raise ValueError('A specific expected console marker is required')
    lowered = captured.lower()
    for token in (b'guru meditation', b'backtrace:', b'assert failed:',
                  b'stack overflow', b'***error***', b'rebooting...'):
        if token in lowered:
            raise RuntimeError('P4 startup failed: ' + token.decode('ascii'))
    if captured.count(console_marker) > 1:
        raise RuntimeError('P4 repeated console initialization')
