# Accuracy core and Pi peer — offline r01

Portable source implements the fixture record, deterministic byte oracle and
five-attempt state machine. The independent Python peer checks one trusted case
attempt over actual bounded TCP. This is not yet the mixed-carrier Agon/P4
appliance and does not implement physical UART1 NACK delivery or retirement.

1. `core.hpp` and `scripts/comms_accuracy.py` independently encode/validate the
   documented40-byte header, up to84 payload bytes and4-byte CRC. A complete
   record is at most128 bytes; the TCP wrapper is uint32LE record length.
2. `Attempts` requires positive retirement and a verified UART report before a
   RETRY control can admit one new numbered attempt. Fifth failure exhausts the
   case; duplicate, stale or mismatched controls cannot create an extra attempt.
3. `scripts/comms_accuracy_peer.py` requires a trusted local JSON case plan,
   exclusive output journal and finite duration. It accepts exactly one TCP
   connection, checks every record and clean close, then stops. The default
   bind is loopback; a real Pi/P4 endpoint must be selected under the later
   frozen run. No background service or automatic reconnect is installed.
4. Example plan fields are `run`, `case`, `tx`, `rx`, `pattern`, `seed`, `total`
   and optional `attempt`; see the protocol table in the task's offline plan.
   Each DATA record has sequence1..N, offsets0..total, maximum84 byte chunks.
5. `Journal` creates a new file and checks each complete write/fsync. Inspection
   preserves an incomplete tail/outstanding intent instead of repairing or
   replaying it. These are host witness semantics; the Agon SD adapter must
   separately bind MOS write/commit behaviour.
6. `selfcheck.cpp` is a stopped target compilation probe. Its successful link
   is not permission to deploy, invoke it, or call this a ready transport test.

The [task](../../../docs/tasks/COMMS-001.md) owns remaining adapters and physical
gates. The separate benchmark has no dependency on this retry/CRC engine.
