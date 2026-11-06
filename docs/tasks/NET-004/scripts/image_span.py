"""Host-only sector composition from identified owner-retained bytes.

Never pads an unknown incoming tail with FF or treats a source commit as
rollback bytes. Callers must establish that retained identities still describe
the actual incoming installation. This module does not read/write a device.
"""
import hashlib


def digest(data):
    return hashlib.sha256(data).hexdigest()


def extend_verified_prefix(prefix, prefix_sha256, older_span, older_sha256):
    """Join a later verified overwrite with the proven untouched older suffix."""
    if digest(prefix) != prefix_sha256 or digest(older_span) != older_sha256:
        raise ValueError('Retained readback identity mismatch')
    if len(prefix) > len(older_span) or not prefix or len(prefix) % 4096 or len(older_span) % 4096:
        raise ValueError('Verified sector prefix must fit the older full span')
    return prefix + older_span[len(prefix):]


def compose(app, expected_sha256, incoming_span, incoming_sha256, partition_size, *, sector=4096):
    """Return the candidate sectors and exact same-scope incoming rollback."""
    if not app or digest(app) != expected_sha256 or digest(incoming_span) != incoming_sha256:
        raise ValueError('Exact candidate/incoming retained bytes required')
    if sector <= 0 or partition_size <= 0 or len(incoming_span) % sector:
        raise ValueError('Whole sectors and a positive partition required')
    span = (len(app) + sector - 1) // sector * sector
    if span > partition_size or span > len(incoming_span):
        raise ValueError('Candidate exceeds preserved span/partition; reconcile unknown bytes')
    rollback = incoming_span[:span]
    payload = app + rollback[len(app):]
    return dict(payload=payload, rollback=rollback, span=span,
                tail_bytes=span-len(app), app_sha256=expected_sha256,
                payload_sha256=digest(payload), rollback_sha256=digest(rollback))
