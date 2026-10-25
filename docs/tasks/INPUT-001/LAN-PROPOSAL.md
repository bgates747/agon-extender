# Controller LAN transport proposal

Historical pre-implementation proposal, superseded by the accepted
[decision](../../decisions/ADR-2026-10-24-controller-udp.md) and
[maintained protocol](../../protocols/controller-lan.md). The Author selected
UDP and delegated layout/cadence/timeout after reviewing this proposal. The
past-tense implementation claims below describe its earlier preparation stage.

Draft for Author review, 2026-10-24. Recommend complete current-state snapshots
from Oryx to P4 over UDP, with a small acknowledged queue for button transitions.
This keeps old axis samples out of the way of new ones while retaining short
taps. The reviewed Linux reader supplies input; neither a LAN sender nor a P4
receiver exists yet. The first decision is transport selection, IN001-D03.
The numerical layout and limits below make that choice reviewable; none are
accepted allocations, measured performance or instructions to operate a bench.

## Actors and boundaries

1. Oryx's existing evdev reader produces coherent changed-state reports and
   timestamped button transitions. A separate sender coalesces only current
   analog state; it never discards unacknowledged transitions silently.
2. P4's existing Ethernet owner retains ownership of the network interface.
   A controller worker owns one UDP socket, validates admitted messages, stores
   the latest coherent state and retains transitions. HTTP handlers manage
   session admission/status only; no per-update HTTP request is required.
3. The P4 controller worker never writes the eZ80 UART, modifies MOS memory,
   changes display routing or synthesizes keyboard input. A later approved
   EMOS integration reads the controller-state service through its own transport.
4. Keyboard, browser/video, SD and gamepad sessions remain separate. A gamepad
   connection does not capture the keyboard or transfer bench ownership.
5. One selected controller and one admitted sender are the initial scope.
   Rumble, browser capture, direct P4 USB and flight mappings are deferred.

## First decision: UDP versus an ordered stream

| Criterion | Proposed UDP state + retained edges | Persistent TCP/WebSocket alternative |
|---|---|---|
| New axis state | Each packet replaces the previous snapshot; omit stale/out-of-order packets | Framing/coalescing still required; queued older stream data precedes newer state |
| Short buttons | Explicit numbered transitions, duplicate suppression and ACK retention | TCP supplies ordered byte delivery; application consumption still needs its own contract |
| Loss | New snapshots supersede missing snapshots; retransmit retained transitions within bounds | TCP recovers byte loss; missing earlier bytes can delay later state |
| Existing code | Uses supported BSD socket APIs, adds a UDP owner/lifecycle | Existing HTTP/WebSocket infrastructure is useful, but video socket ownership/framing cannot simply be reused |
| Main implementation cost | Small state machine for datagram validation and bounded edge retention | Stream framing, backpressure and bounded freshness handling; no custom packet retransmission |

Recommendation: UDP for this small continuously refreshed input stream. The
tradeoff is explicit loss/reorder handling, which must be tested. This is an
architectural recommendation, not a claim that UDP has measured lower latency
on the present P4. If the Author selects TCP/WebSocket, preserve the logical
state/edge and EMOS boundaries; revise the framing and failure details rather
than burying an alternate implementation in the UDP code.

## Reviewable candidate messages

All sizes below are application bytes before UDP/IP/Ethernet. A candidate
32-byte little-endian header carries: magic4, version1, kind1, exact length2,
receiver instance8, admitted session8, datagram sequence4 and reserved-zero4.
Use explicit encoding/decoding, not a packed C structure shared across compilers.
This header is LAN-only: the eZ80 need not parse or receive it.

1. Session open/status uses a proposed dedicated controller HTTP control path,
   naming the receiver instance, compatible state encoding, one sender and its
   UDP endpoint. P4 returns a fresh session token and limits. No numeric port,
   URI, application ABI or firmware build identity is reserved by this draft.
   These trusted-LAN tokens identify sessions; they are not authentication.
2. A STATE body has the analog values, held-control mask2, host publication
   age2, state flags1 and edge count1. Analog profiles remain a later decision:
   native signed16 sticks plus8-bit triggers use10bytes; verified F310 raw8 uses
   six bytes. Thus an empty-edge packet is48 or44bytes respectively. Host age
   is a duration since the sender acquired its snapshot, not an absolute host
   time for comparison against P4's clock. Connected idle input sends fresh
   heartbeats even if evdev has emitted no changes.
3. The held-control mask covers eleven buttons and four D-pad directions, with
   one reserved bit. Opposite directions on an axis are invalid. D-pad taps need
   transition retention just like buttons. Axis samples use the most recent
   committed report; current held state and ordered historical transitions are
   exposed as different observations, not falsely merged into one event time.
4. Each transition record has sequence4, logical control1, down/up1 and reserved2
   (8bytes). Up to16 records per datagram keep the candidate maximum at172bytes
   for raw8 (176native). Records repeat until cumulatively acknowledged; a
   retransmission uses a new datagram sequence but the same transition IDs.
5. ACK names the highest received datagram and highest contiguous retained
   transition (4bytes each), for40bytes including header. ACK means P4 owns the
   queued transition, not that an eZ80 application consumed it. P4's downstream
   queue must remain bounded and report failure rather than silently lose an
   acknowledged transition. The later EMOS delivery/consumption contract is a
   prerequisite to claiming end-to-end button reliability.
6. Complete snapshots can advance despite a gap in transition sequence. P4
   queues only contiguous transitions and acknowledges that contiguous prefix;
   the sender retries the missing prefix before later transitions. A frame's
   held mask remains the latest state, not a substitute for missing tap history.
   Do not synthesize press edges by comparing snapshots after packet loss.
7. Unplug, source overflow or an explicit sender close invalidates input and
   ends the session. A lost close is covered by the receiver timeout. Unknown
   versions, excessive lengths/counts, reserved bits, invalid control values,
   source endpoint mismatch and stale instance/session packets are rejected.
   Duplicates do not replay transitions or renew input health. Keep ordinary
   UDP checksums enabled; no bespoke checksum algorithm is proposed here.

## Candidate pacing, memory and loss limits

1. Read Linux input independently of transmission. Send current state on a
   monotonic schedule at100Hz initially, with60/120Hz controls available for
   measurement. Do not send one packet per evdev axis event or issue catch-up
   bursts after a stalled sender. This is a proposed publication cadence, not
   the controller's USB report rate or an accepted eZ80 polling frequency.
2. At100Hz, raw8 STATE plus one ACK per state is8,400application bytes/s or
   approximately14,000bytes/s including IPv4+UDP headers in both directions,
   before Ethernet overhead and added transition records. Native profile adds
   400bytes/s at that rate. These are planning arithmetic, not a LAN benchmark.
3. Candidate sender and P4 transition queues each hold128records (1,024encoded
   bytes per queue, before implementation metadata). Candidate per-iteration
   receive/parse work is bounded; axis buffers hold latest state only. Inspect
   actual FreeRTOS stack/heap, lwIP socket/mailbox and HTTP socket budgets before
   selecting a firmware composition. No dynamic unbounded event list is allowed.
4. If a queue fills, the reader reports SYN_DROPPED, or the sender cannot keep
   recording transitions, invalidate the session explicitly. Do not continue
   under an unchanged healthy flag. Keyboard/SD continue independently.
5. Candidate receiver timeout is250ms since the last new valid STATE. Evaluate
   timeout before accepting queued data after a scheduling stall; an expired
   session cannot be revived by an old packet. Link/receiver restart invalidates
   immediately. Only a newly admitted session can regain validity after expiry.
6. New session/epoch and explicit start/stop are independent of the hardware
   USB connection. Sequence numbers do not wrap inside a session; renew before
   exhaustion. No packet from an old instance or terminated session can open a
   new session, steal an owner or restore held input. Lost/uncertain admission
   responses need bounded idempotent control handling, specified before coding.
7. On invalidation P4 publishes disconnected/invalid status and neutral
   stick/trigger values with no held buttons. Applications must inspect validity.
   Game throttle position, pause and aircraft rearm behavior remain fsim/game
   policy; neutral raw trigger input is not a command to reset game state.
   Reconnection must not manufacture button presses from an initial held mask.

## Physical and software implementation boundaries

1. Source inspected at host publication commit
   `29c4a8810707ad1edafdada3e6901429c1fb1fa2`: WiredNetworkService already owns
   Ethernet lifecycle and starts HTTP; it includes lwIP sockets, but has no
   controller or UDP receive service. The common HttpVideoService's socket send
   path can wait up to5seconds. A separate controller worker avoids coupling
   freshness deadlines to that video send, but its actual scheduling must be
   measured. Do not advertise isolation merely because tasks are separate.
2. Existing keyboard handlers only enqueue under a narrow lock and leave UART
   output to its owner. The controller should preserve that boundary; no network
   task may call VDU, inject keyboard payloads or write physical transports.
3. ESP-IDF5.5.5 documents BSD sockets, nonblocking operations and UDP support.
   That establishes API availability, not enabled resource limits or performance
   of a particular installed P4 build. Reuse the current Ethernet owner; don't
   start a second Network/ETH instance for the controller.
4. Exact board/source/profile/component identities, receiver port, worker budget
   and rollback are selected only in a later authorized build/staging tranche.
   P4-PC and DevKit have distinct hardware pins. No firmware selection, network
   query, reservation, reset, flash, USB opening or installation occurred here.
5. Keep forthcoming offline codec/session/edge tests separate from an installed
   UDP receiver. Replay the two accepted recordings, add synthetic sub-frame
   taps and deliberately lose/duplicate/reorder packets. Prove bounded expiry,
   queue overflow, delayed previous-session packets and coherent reads. These
   are subsequent implementation requirements after contract decisions, not
   tests already performed by this document.

## Remaining decision sequence

IN001-D03 is presented first. If accepted, resolve analog encoding (D02),
publication/timeout limits (D04/D06), source ownership/admission (D05), transition
retention/consumer semantics (D07) and the EMOS application read (D01/D08 and
IN001-07) before implementing the affected boundary. Task details own all open
questions and authorization gates. This draft becomes a durable protocol only
after those decisions are accepted; it changes no normative architecture now.

References: [task](../INPUT-001.md), [host results](HOST-REVIEW-2026-10-24.md),
[keyboard contract](../../remote-keyboard.md),
[shared Ethernet/services](../../shared-p4-services.md),
[source network owner](../../../vdp/video/extender/network/wired_network_service.cpp),
[source input lock](../../../vdp/video/extender/input/remote_target.hpp), and
[ESP-IDF5.5.5 lwIP documentation](https://docs.espressif.com/projects/esp-idf/en/v5.5.5/esp32p4/api-guides/lwip.html).
