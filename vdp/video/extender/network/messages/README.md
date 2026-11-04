# Experimental application message core

NET-003 supplies stopped, independently checked building blocks. No console build
imports these files, no service starts, and no EMOS/eZ80 endpoint exists yet.
The accepted architecture selects P4 outbound TCP to a consumer-owned Pi bridge;
this source does not install that architecture on a device.

`Channel<MaxPayload, Depth>` stores bounded FIFO messages in each direction.
The caller serializes all methods and network I/O. `send` copies into local
storage or returns busy without accepting the message. `receive` reports the
required size and leaves a too-large message queued. Empty/binary messages work.
The prototype stream prefix is four-byte little-endian payload length; this is
an internal experimental encoding, not a frozen public protocol or capacity.

`open` issues a nonzero, never-reused per-object generation; a live or faulted
session requires explicit close before another open. Stale operations cannot
change the current session. On fault, complete received records can still be
drained in order, then `receive` reports fault. Uncertain outgoing records remain
visible as a count only and cannot resume. Explicit close discards them and any
unread/partial input. No message is replayed on a later connection.

`pump` uses an `Io` adapter and explicit operation/byte budgets. Keep one
`PumpCursor` per owner; it alternates directions across calls even with a
one-operation/one-byte budget. Would-block yields to the caller. Partial writes
continue at the exact offset. Invalid lengths/I/O results and truncated records
fault the session. The owner must allocate a channel in lifetime-owned storage; the larger test
profile can exceed a small worker stack and is not a stack-allocation recommendation.
The core never allocates, waits, takes a lock, or opens a
socket. Views are synchronous borrows: no pointer may survive a core mutation
or be passed to asynchronous/DMA code without a separate lifetime contract.

`TcpClient` owns one numeric-IPv4 outbound nonblocking socket. `start` returning
OK may mean connecting; `pollConnect` checks completion without waiting. The
worker must supply a deadline and cancel/close on timeout or link loss. The
adapter performs no DNS, reconnect, application handshake, worker scheduling or
EMOS admission. Connect failure remains terminal until explicit close. Its
lwIP build is compiled separately; host success alone is not P4 link/runtime
qualification. Keep the owner alive through all synchronous I/O and close it
before destruction or service teardown.

Finite host checks, under the current Pi build reservation:

```sh
.venv/bin/python tests/network/messages/run.py --output agents/net003/FRESH-RUN
```

The runner compiles the actual core/adapter with ASan/UBSan, exercises fake I/O
and an ephemeral loopback connection, records input hashes and durable elapsed
nanoseconds, then stops all children and closes sockets. It contacts no LAN or
bench. Durations measure this host build/check workload, not network performance.

Compile-only P4 checks use an existing native build's headers/configuration:

```sh
.venv/bin/python tests/network/messages/compile_target.py \
  --build-output PATH-TO-RETAINED-NATIVE-BUILD --output agents/net003/FRESH-OBJECTS
```

This reuses compiler/include selections while writing new objects and logs only
to the fresh output. It neither rebuilds the retained firmware nor identifies a
new installed candidate. The owning task holds all remaining integration gates.
