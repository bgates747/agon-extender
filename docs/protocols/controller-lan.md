# Controller LAN protocol

Oryx sends fresh analog state and retained button/D-pad transitions to P4.
This developmental protocol is installed with experimental P4r14 and has
bounded physical host/P4 measurements plus Author review through the matched
EMOS viewer. It is not selected production support or the application API;
eZ80 consumers use the separately specified EMOS controller gateway.
The [accepted decision](../decisions/ADR-2026-10-24-controller-udp.md) establishes
the LAN design. [INPUT-001](../tasks/INPUT-001.md) owns further implementation
and physical qualification. No production version is assigned here.

## Actors and state

1. The Linux sender reads a deliberately selected F310 in XInput mode through
   nonexclusive evdev. SYN_REPORT commits coherent reports. Source overflow
   makes transition history unknown and terminates the sender.
2. The existing P4 Ethernet owner starts one UDP worker and registers controller
   routes on its existing HTTP server. The worker owns its socket, validates
   packets and updates state/queue under one mutex. It never writes UART,
   selects a display route or synthesizes keyboard input.
3. One admitted IPv4/UDP endpoint owns one session. HTTP admission and UDP state
   are separate from keyboard capture, video ownership and SD services.
4. P4 stores signed 16-bit stick state, two unsigned 8-bit triggers, a held mask, validity,
   arrival time and queued transitions. Snapshot state and historical transitions
   are distinct observations; applications must not infer historical presses
   by differencing snapshots after loss.
5. The [development EMOS service](controller-emos.md) supplies a separately
   identified application consumer. Its source/software tests/target builds
   pass, and its EMOSv27/viewer-r03 combination is installed with bounded
   Author handling review; broader lifecycle qualification remains open.
   HTTP status reads do not drain transitions. Without that consumer,128 unconsumed transitions
   fill the queue and the next new transition invalidates input.

## Admission and lifecycle

All control requests use the existing P4 HTTP origin. GET `/controller/status`
returns JSON with `protocol:1`, `instance` and `session` as sixteen-digit hex
strings, `udp_port`, `active`, `valid`, `fault`, `sequence`, `edge_ack`, `queued`,
`received`, `rejected`, `age_ms`, `sticks`, `triggers` and `held`. The UDP worker
binds an available ephemeral port and reports it; clients must rediscover after
receiver restart. `received` counts accepted new states; `rejected` counts
decoded states rejected by the session core, excluding malformed wire packets.
Invalid state reports age zero with `valid:false`, not a fresh observation.

POST requests require `X-Agon-Controller: 1`, no Origin header, exact binary
length, and all reserved fields zero. Integers are little-endian.

| Route | Request body | Response |
|---|---|---|
| `/controller/open` | instance u64, client nonce u64, UDP source port u16, timeout ms u16, reserved u32; 24 bytes | 200: JSON session hex token and timeout; 400: invalid; 409: owned; 410: last nonce expired; 503: worker unavailable |
| `/controller/close` | instance u64, session u64; 16 bytes | 200: closed; 409: wrong identity |

P4 binds the UDP owner to the HTTP peer's IPv4 address and the supplied UDP port.
Each start uses a random nonzero receiver instance; admission uses a fresh
nonzero nonce and random session token. Repeating the same active open with the
same endpoint/timeout is idempotent and never refreshes freshness. Only the most
recent nonce is retained after termination. The sender currently makes one open
attempt; a lost HTTP response fails closed and the receiver expires. A new
explicit invocation uses a new nonce. Tokens do not authenticate an untrusted
network. The client resolves its HTTP hostname once to the same IPv4 endpoint
used for UDP; NAT/proxy forwarding is outside this contract.

Opening starts the expiry clock with `active:true, valid:false`. Only a new valid
STATE makes input valid or renews the deadline. P4 checks expiry before accepting
any queued packet. Duplicate datagrams, older packets, HTTP status or repeated
admission do not renew it. Closed/expired sessions cannot be revived by UDP.

Oryx stops on unplug, source session change, SYN_DROPPED, transition overflow,
recording failure, receiver FAULT or missing fresh ACKs. It attempts HTTP close;
a lost close is covered by expiry. It does not automatically rearm on replug.
Ethernet loss stops P4 input and invalidates the receiver epoch on restart.
Invalidation clears raw state, held controls and queued history. Applications
must check validity; raw neutral is not an instruction to reset game throttle.

## Datagram header

Ordinary UDP checksums remain enabled. No application CRC is added. Packets
must have exact declared lengths; unknown kinds/profiles, reserved fields,
invalid controls and oversized packets are rejected. No C structure is a wire ABI.

| Offset | Bytes | Value |
|---|---:|---|
| 0 | 4 | ASCII `AGCP` |
| 4 | 1 | Protocol 1 |
| 5 | 1 | Kind: STATE=1, ACK=2, FAULT=3 |
| 6 | 2 | Total application packet length |
| 8 | 8 | Receiver instance |
| 16 | 8 | Admitted session |
| 24 | 4 | Datagram sequence, starting at 1 |
| 28 | 4 | Reserved zero |

Datagram and transition sequences never wrap within a session. The sender stops
at exhaustion; an explicit new session is required. Stale instances, sessions
and source endpoints cannot open or steal a session.

## STATE body

| Offset | Bytes | Value |
|---|---:|---|
| 32 | 2 | Current held mask |
| 34 | 2 | Host publication age in ms, accepted range 0–50 |
| 36 | 1 | Analog profile: raw8=1, native=2 |
| 37 | 1 | Transition count, 0–16 |
| 38 | 6 or 10 | Analog values |
| following | 8 each | Retained transitions |

Analog order is left X/Y, right X/Y, left/right trigger. Raw8 uses six unsigned
bytes: each stick is reversibly reconstructed as `value*257-32768`; triggers
remain 0–255. Oryx selects raw8 only when all four stick values satisfy that exact
lattice. Otherwise native uses four signed little-endian 16-bit sticks and two
unsigned 8-bit triggers. No calibration, inversion or dead zone is applied on the
wire. Native recordings are preserved independently of the selected encoding.

Held bits 0–10 are A, B, Y, X, LB, RB, Back, Start, Guide, left stick click and
right stick click. Bits 11–14 are left, right, up, down. Bit 15 is reserved zero;
opposed horizontal or vertical directions are invalid. Triggers remain analog.

Each transition is sequence u32, logical control index u8, down u8 (0/1), reserved
u16 zero. Transitions in a packet form a contiguous increasing sequence. A
SYN_REPORT commits buttons/hat atomically; their relative ordering within that
one report does not represent separately timed physical events. Baseline held
controls at session start do not manufacture press transitions.

Oryx sends the oldest unacknowledged prefix, at most 16 records, alongside the
latest snapshot. P4 queues only the contiguous prefix after its `edge_ack`.
Duplicates never enqueue twice. A missing transition prefix does not prevent
newer analog state; a later packet retries the missing prefix. P4's queue and
Oryx's pending queue each hold 128 records. Overflow terminates the session
explicitly, discarding its history with invalid status rather than claiming
continued reliable delivery.

## ACK and FAULT

Both replies are 40 bytes. Their header repeats the STATE datagram sequence.
At offset 32 is that same sequence u32; at 36 ACK carries highest contiguous
stored transition u32, while FAULT carries a reason u32. Reasons are 0 none,
1 explicit close, 2 timeout, 3 link/service loss, 4 queue overflow; 5 is reserved for
source loss. The current worker emits FAULT for queue overflow. Other losses
are visible through status/absence of fresh ACKs.

ACK confirms P4 queue storage, **not EMOS/application consumption**. P4 may ACK
an exact duplicate of its latest packet to recover a lost ACK, without renewing
input health. Older packets receive no reply. Oryx ignores old ACK sequence
numbers, rejects ACKs claiming unsent data and stops if no newer ACK arrives
within its timeout. A finite run/Ctrl-C closes input; its final JSON reports
pending transitions, without claiming they were consumed.

## Timing and resource limits

| Parameter | Selected default | Tuning/bound |
|---|---:|---|
| Oryx publication | 120 Hz | `--hz`, 1–240 Hz; no catch-up bursts |
| Session timeout | 250 ms | `--timeout-ms`, 50–2000 ms; sender requires at least two publication periods |
| Host reader | Event-driven | At most 4096 evdev records per observer iteration |
| P4 UDP work | At most 8 packets per iteration | Nonblocking receive, then at least 2 ms/task tick delay |
| Worker task | 6144-byte requested stack, priority 2 | Physical high-water/latency measurements pending |
| Socket ceiling in controller build | 16 | Compile-time ceiling, not measured concurrent capacity |
| Empty-edge STATE | 44 raw8 / 48 native bytes | Maximum 172 raw8 / 176 native |
| ACK | 40 bytes | One reply per accepted new/latest duplicate state |

At 120 Hz raw8 STATE/ACK totals 10,080 application bytes/s, or 16,800 bytes/s with
IPv4/UDP headers in both directions, before Ethernet and transition overhead.
Native adds 480 bytes/s. These figures are arithmetic, not observed throughput.

The Author selected 120 Hz to match MOS's nominal tick cadence. The host sender
uses its own monotonic schedule; this rate agreement does not phase-lock UDP
arrival or future EMOS reads to those ticks. The earlier recorded-input replay
used a simulated100Hz clock and remains evidence for that earlier run.

Oryx and P4 use local monotonic clocks. Host age describes publication of the
cached state after evdev polling; connected idle controls still send heartbeats.
It does not prove physical sample age or account for network transit. P4 age
and expiry use local arrival milliseconds from `esp_timer`; Linux scheduling,
network queues and P4 task scheduling remain physical validation limits. No
unsynchronized timestamp subtraction is presented as one-way latency.
