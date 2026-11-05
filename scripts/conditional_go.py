"""Finite host-only admission gate; the owner supplies validation and invocation.

There is no hardware, networking, scheduler grant, process launcher or daemon in
this module. Importing it does nothing. An exclusive output directory is the
durable one-arm journal; never reuse it after expiry, cancellation or host loss.
Validation and invocation are separate: dispatch is recorded before the callback
can act, and an exception never retries that callback. See NET-003/PHYSICAL.md.
"""
import hashlib
import json
import os
from pathlib import Path
import time

MAX_JSON = 8192


def read_json(path, limit=MAX_JSON):
    with Path(path).open('rb') as handle:
        raw = handle.read(limit + 1)
    if len(raw) > limit:
        raise ValueError('Admission document exceeds its byte bound')
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError('Admission document must be an object')
    return value


def record(path, value):
    raw = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
    if len(raw) > MAX_JSON:
        raise ValueError('Admission receipt exceeds 8KiB')
    with Path(path).open('xb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    directory = os.open(Path(path).parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def require_fields(document, expected, label):
    for key, value in expected.items():
        if key not in document or document[key] != value:
            raise ValueError(label + ' differs: ' + key)


def validate_window(marker, ready, *, epoch=None, monotonic_ns=None,
                    minimum_remaining_seconds=15):
    epoch = time.time() if epoch is None else epoch
    monotonic_ns = time.monotonic_ns() if monotonic_ns is None else monotonic_ns
    require_fields(marker, dict(
        ready_epoch=ready['epoch'], ready_monotonic_ns=ready['monotonic_ns'],
        bridge_pid=ready['bridge_pid'], controller_pid=ready['controller_pid'],
        registration_deadline_monotonic_ns=ready['registration_deadline_monotonic_ns']),
        'Original readiness')
    deadline = ready['registration_deadline_monotonic_ns']
    if not (0 < deadline - ready['monotonic_ns'] <= 90_000_000_000):
        raise ValueError('Invalid original registration deadline')
    if not (0 <= epoch - marker['issued_epoch'] <= 10 and
            0 <= monotonic_ns - marker['issued_monotonic_ns'] <= 10_000_000_000 and
            ready['monotonic_ns'] <= marker['issued_monotonic_ns'] and
            ready['epoch'] <= marker['issued_epoch']):
        raise ValueError('Stale or inconsistent GO observation')
    if deadline - monotonic_ns < minimum_remaining_seconds * 1_000_000_000:
        raise ValueError('Original registration budget insufficient; no extension')


def accepted_delivery(receipt, message, *, source, target, delivery_id):
    require_fields(receipt, dict(phase='accepted', source=source, target=target,
        delivery_id=delivery_id, transport='pi-unix-app-server',
        message_sha256=hashlib.sha256(message).hexdigest()), 'Canonical delivery')
    if receipt.get('method') not in ('turn/steer', 'turn/start'):
        raise ValueError('Delivery was not immediate')


def wait_once(marker_path, output, wait_seconds, validate, invoke, *,
              cancelled=lambda: False, clock=time.monotonic, pause=time.sleep):
    """Observe one fresh marker, validate once, durably claim, invoke at most once.

    The selected owner must use the same output for the whole arm, including
    competing launchers. A retained journal is a stop, never restart permission.
    ``wait_seconds`` bounds admission; the owner's invocation has its own bound.
    This function never resets or kills a device on any failure.
    """
    if not 0 < wait_seconds <= 180:
        raise ValueError('Admission window must be 1..180 seconds')
    marker_path, output = Path(marker_path), Path(output)
    if marker_path.exists():
        raise ValueError('GO predates receiver arm; no dispatch')
    output.mkdir(parents=True, exist_ok=False)
    started = clock()
    deadline = started + wait_seconds
    attempted = False

    def check():
        if cancelled():
            raise InterruptedError('Receiver cancelled; no successor')
        if clock() >= deadline:
            raise TimeoutError('Receiver expired; no successor')

    try:
        if marker_path.exists():
            raise ValueError('GO appeared before arm publication')
        record(output / 'armed.json', dict(pid=os.getpid(), epoch=time.time(),
            monotonic=started, wait_seconds=wait_seconds, marker=str(marker_path)))
        print('Conditional receiver armed; no target command while waiting.', flush=True)
        while True:
            check()
            if marker_path.exists():
                marker = read_json(marker_path)
                proof = validate(marker)
                check()  # Validation cannot restart/extend admission.
                record(output / 'validated.json', proof)
                record(output / 'dispatch.json', dict(epoch=time.time(),
                    monotonic=clock(), marker=marker, state='dispatch-claimed'))
                check()
                attempted = True
                result = invoke(marker)
                record(output / 'result.json', dict(epoch=time.time(),
                    invocation_attempted=True, result=result))
                return result
            pause(min(0.1, max(0, deadline - clock())))
    except BaseException as error:
        record(output / 'failure.json', dict(epoch=time.time(),
            invocation_attempted=attempted, error=repr(error)[:1024],
            no_retry=True, target_state='owner evidence required'))
        raise
