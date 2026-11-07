# Mixed-carrier communications accuracy fixture — design r01

This fixture will check whether Agon, Extender and a Pi peer exchange the exact
intended bytes over long mixed workloads. It will alternate UART1 and eight-bit
parallel transfers, verify CRCs at receiving endpoints, retain failures on Agon
SD and retry a failed case through a UART1 control exchange. It is an accuracy
and endurance test, not a speed benchmark. No extra sniffers or probes are used.

**Status:** Design only, not implemented or qualified. The authoritative work
and unresolved decisions are in [COMMS-001](../tasks/COMMS-001.md). This document
defines the proposed appliance, not a new production transport contract.

Smith explicitly requests a separate, complementary
[performance comparison](communications-performance-design.md). That benchmark
has its own program, invocation, logs and results; it is not a timing mode or
analysis of this endurance run.

## 1. Purpose and evidence limits

1. Previously observed communication failures are the primary reason for this
   fixture. Parallel-path failures, including excess VALID-edge counts and
   stalled control transfers, are recorded; their causes, severity and remaining
   exposure are unresolved. Bounded passing runs after filtering do not settle
   hours-long reliability. Smith also reports watching approximately one to two
   hours of uninterrupted MechAgon play over UART earlier on November 6. That
   experience makes communication failure a reasonable suspect in the later
   freeze; the freeze is additional motivation, not the sole evidence behind
   this investigation. Its particular cause remains unproven, and the observed
   UART run is useful context rather than a controlled carrier comparison.
   CPU stalls, receiver state, ownership, buffering, scheduling, framing,
   filesystem delays and network disconnects remain possible contributors.
2. The appliance must distinguish corruption, truncation, extra bytes, missing
   records, duplicates, reordering, stale replies, refusal and timeout. A correct
   eventual answer must not erase an earlier failure.
3. CRCs check received bytes. They do not by themselves prove that a VDU command
   executed correctly or that physical pixels match. A matching deterministic
   byte comparison and a receiver execution fence provide separate evidence.
4. No optical FPS, calibrated latency, noise amplitude or electrical root-cause
   conclusion follows from this fixture. Recorded times support ordering,
   timeout diagnosis and correlation, not a throughput competition.

## 2. Actors and ownership

| Actor | Responsibility |
|---|---|
| Agon eZ80 appliance | Generate deterministic cases; call admitted EMOS services; validate incoming data; write Agon SD logs; accept Escape; restore entry display state and CLI |
| Extender MOS (EMOS) | Own UART1, shared pins, parallel admission, direction changes, VDU routing and positive retirement; reject unsupported combinations |
| P4 transport owner | Admit the selected leg, own buffers/DMA/peripheral lifetime, capture counts and faults, validate received fixture data, deliver selected VDU bytes through the owned dispatcher |
| P4 network worker | Own its socket and relay framed test data to/from the Pi; retain bounded backpressure and report socket state |
| Pi peer | Independently generate expected data, verify received bytes/CRC, emit deterministic responses and selected network fault cases, retain an independent witness log |
| Pi suite coordinator | Hold the actual bench lease; invoke explicitly, supervise bounded progress, preserve evidence and perform only the selected cleanup/recovery |

The Agon application must not take over GPIO/UART registers or bypass EMOS VDU
routing. UART1 error traffic must use an owner-admitted framed control path,
not arbitrary text interleaved with VDP, keyboard or transport bytes. UART0
mainboard graphics remains a separately named workload, not a substitute for
the selected P4 VDU tests.

## 3. Carrier matrix and workload schedule

The terms **outbound** and **return** below mean Agon→P4 and P4→Agon. The Pi
extension is Agon→P4→Pi and Pi→P4→Agon, with local-carrier choices retained.

| Outbound carrier | Return carrier | Required coverage |
|---|---|---|
| UART1 | UART1 | Reference and interleaved control cases |
| UART1 | PARLIO/eight-bit parallel | Mixed-direction case |
| PARLIO/eight-bit parallel | UART1 | Mixed-direction case |
| PARLIO/eight-bit parallel | PARLIO/eight-bit parallel | Both parallel directions |

1. A fixed case order plus a stored seed defines a reproducible cycle. Adjacent
   cases deliberately alternate carriers; an optional seeded order is recorded
   in full. Carrier selection is explicit for every leg, never fallback.
2. Each matrix row includes short isolated records, back-to-back short bursts,
   medium blocks and sustained logical blocks split at supported carrier limits.
   Exercise zero length where supported, one byte, and lengths immediately
   below/at/above legal record and buffer boundaries. Long blocks must not
   invent a larger resident ABI or bypass backpressure.
3. Patterns include zeroes, ones, alternating bits, walking bits, byte ramps,
   complements and seeded pseudorandom bytes. Changing seeds and logical block
   numbers prevents a stale response from matching by accident.
4. VDU cases carry valid short commands, medium command batches and long binary
   buffer/image command streams to the P4 display path, especially over parallel.
   Interleave them with pure opaque data transfers and idle gaps. Use only
   task-owned display resources and reversible, bounded operations.
5. Repeat open/transfer/positive-close cycles as well as long-lived sessions.
   Include legal near-capacity/backpressure, delayed servicing and serialised
   UART0 graphics/query or guarded RFC25 work inspired by existing consumers.
   Any overlap must be separately supported by the owners; no unsafe concurrent
   gateway calls or claimed interrupt concurrency are implied.
6. The Pi route covers both directions and partial socket reads/writes, delayed
   responses, disconnect/reconnect and clean close. TCP delivery is not evidence
   that the Agon/P4 leg was correct. Validate at each observable endpoint.

## 4. Deterministic records and CRC checking

1. Every logical transfer identifies protocol revision, run/session, case,
   attempt, direction, selected carriers, pattern seed, logical length, block
   offset and sequence. Encode integers explicitly; never transmit native C
   structures or uninitialised padding.
2. Use CRC-32/ISO-HDLC for the fixture: polynomial `0x04C11DB7`, reflected
   implementation `0xEDB88320`, initial/final XOR `0xFFFFFFFF`, check value
   `0xCBF43926` for ASCII `123456789`. Freeze exact coverage and little-endian
   wire encoding before implementation. Cover routing/identity/length metadata
   as well as payload so a valid body cannot conceal a wrong case or carrier.
3. The sender computes the expected CRC before submission. The receiver computes
   a CRC over its actual received bytes before reuse, and independently compares
   the generated expected pattern. Check each completed transfer/block boundary
   and the whole logical stream, including both outbound and return directions.
   Do not add per-byte software handshakes.
4. A response carries the receiver's observed length, CRC and verdict; it is
   itself checked. The receiver must not merely echo the sender's CRC. The Pi
   and P4 check inbound data before echoing; Agon checks the returned data again.
5. Exact mismatches retain first differing offset, expected/actual values and a
   bounded surrounding sample. A CRC match is not a mathematical guarantee
   against every possible corruption; deterministic byte comparison strengthens
   this fixture's verdict where expected bytes are known.
6. CRC work is explicitly requested by Smith for this appliance. It does not
   turn CRC into a default requirement for ordinary EMOS/P4 communications or
   authorise changing existing production packet formats.

## 5. VDU receive and execution evidence

1. P4 records the actual VDU bytes at the owned receive/dispatcher boundary,
   alongside their CRC, command boundaries and execution completion. Agon must
   select the intended Extender display route through EMOS; opaque network data
   must not silently become VDU output.
2. Keep a byte-validation sink case separate from a real streaming VDU case.
   Buffering an entire command before execution changes receiver behaviour;
   do not present that as evidence for the ordinary streaming parser.
3. For real streaming cases, commands may execute before a final CRC verdict.
   Restore the case's task-owned display baseline before each repeat. Exclude
   flash writes, startup changes and irreversible or unrelated resource changes.
   An uncertain partially parsed command must be retired/reset by a supported
   parser/owner operation before another command is sent.
4. Record byte correctness, parser status and positive execution fence as
   separate fields. No screenshot or additional electrical sensor is needed
   for the requested transport checks.

## 6. UART1 error reporting and bounded repeats

1. Either receiving endpoint reports a detected failure over **UART1**. The
   framed report identifies the run/case/attempt and failing direction, reason,
   observed length/CRC, expected CRC and local owner state. UART reports also
   receive framing, identity and CRC validation.
2. EMOS and P4 must first positively retire the current parallel epoch, release
   shared pads and re-establish UART1 ownership. UART control cannot bypass an
   unsafe or uncertain parallel owner. A physical transfer-complete flag alone
   does not establish retirement or permission to overwrite buffers.
3. The Agon coordinator confirms the failure report and authorises one fresh,
   numbered attempt of the same deterministic case. Repeat the whole case from
   its known baseline; preserve the old attempt and quarantine late replies.
   Use attempt IDs to make duplicate retry requests harmless.
4. Interpret Smith's limit as **five consecutive failed attempts total**, not
   an initial failure plus five more. Success ends that case's retry sequence;
   report it as recovered-after-failure. On failure five, mark the case failed,
   positively retire it, then proceed to the next independent case.
5. A missing/corrupt UART report, inability to retire ownership, unknown parser
   state or lost control link is an infrastructure failure. Save what remains
   available and stop dispatch; do not skip into another case on unknown pins,
   session or buffers. A blind reset/replay loop is not failure tolerance.
6. This is an explicit fixture-level repeat protocol. Existing production
   transports retain their strict acceptance checks, refusal and no-hidden-replay
   rules. No weakening of VALID-edge, count, DMA or timeout checks is selected.

## 7. Filter/error correlation and time bases

1. Each transfer retains filter enable/configuration and before/after snapshots
   of available hardware/driver counters, including VALID/CLOCK edge proofs,
   requested/completed byte counts, DMA status, UART line errors, queue pressure,
   parser state and carrier retirement result.
2. A filter being enabled is **not** an event proving it rejected a pulse.
   The currently used fixed GPIO filter path does not publish a rejected-pulse
   count. Strict post-filter edge counts are not that count either. The owner
   must investigate an internal counter/timestamp source without extra wires or
   sensors before claiming the requested rejection-event correlation.
3. If the hardware cannot expose actual filter rejections, log that field as
   unavailable and state the limitation prominently. Software protocol rejection
   events are separately counted with reasons. Do not invent filter events from
   CRC failures, or declare this part of the requirement complete from enable bits.
4. Retain endpoint-local monotonic counters, counter width/wrap handling and
   units. For the selected EMOS profile use its verified nominal 120-count/s
   clock, not a generic MOS centisecond assumption. Record P4 and Pi monotonic
   times and bounded cross-endpoint timing markers; do not subtract unsynchronised
   clocks as though they shared one epoch.
5. Log correlation by run/case/attempt/sequence and by time intervals containing
   counter snapshots. An aggregate delta gives an interval, not the exact time
   of a physical pulse or proof of causation.

## 8. SD journal, independent witness and operator control

1. The Agon application writes under a fresh run directory in
   `/agents/extender/results/comms-accuracy`. Maintained executables/configuration
   belong under `/extender/tests/comms-accuracy`. Keep machine addresses and
   secrets in ignored/private configuration, never in tracked examples.
2. Write a run header containing exact executable/firmware/configuration hashes,
   seed, matrix, selected duration, nominal clocks, limits and entry state.
   Write and commit an intent checkpoint before a risky case/attempt, then append
   its actual outcome. An intent without a terminal record is incomplete, not pass.
3. Check write lengths, close/sync results and available space. Use bounded
   buffering and rotation; log errors and consecutive failures immediately.
   A failed durable log stops new dispatch rather than silently dropping records.
   Define the exact commit mechanism from the selected MOS/FatFS implementation;
   do not promise arbitrary power-loss atomicity.
4. The Pi peer/coordinator keeps an independent append-only witness, including
   last accepted sequence and liveness. If Agon blocks inside a call, Agon may
   be unable to write its own timeout. Pi records that missing progress without
   requiring an added USB/sniffer capture or pretending the SD log is complete.
5. The screen shows case, carrier pair, attempt, totals and periodic English
   wait breadcrumbs, with Escape to stop at admitted servicing points. Check
   cancellation between bounded work slices; an unreturning firmware call can
   prevent immediate Escape and must be reported as such.
6. A configurable hours-long run uses one explicit invocation and a finite
   duration/cycle bound. Record actual start/end and completed/failed/incomplete
   attempts. Leave normal startup unchanged; reset never launches or resumes it.
7. Finish with positive owner release, entry mode/route restoration, any required
   monitor-settling delay, visible CLI and stopped peer/coordinator actors.
   Any recovery must follow the selected monitored recovery plan and must not
   automatically restart the test after reset.

## 9. Qualification and staged delivery

1. Qualify record parsing, exact CRC vectors and independent pattern generators,
   wrong identity/length/sequence/CRC refusal, duplicate UART reports, five-failure
   advancement, late replies, cancellation and short/failed log writes offline.
2. Prove the detector with explicitly labelled injected corrupt/truncated/dropped/
   duplicated/reordered records and selected peer delays/disconnects. Count these
   separately from unexpected errors; they are expected detector checks.
3. Before deployment, qualify the mixed-carrier owner build, UART1 return after
   failed parallel epochs, safe VDU baseline restoration and all resource bounds.
   Freeze exact binaries, source/configuration and installation/rollback manifests.
4. Under normal fresh bench custody, run a short bounded matrix first, followed
   by an hours-long unattended window only when available and selected. No peer
   preemption, automatic checkout, hidden fallback or startup modification.
5. A clean accuracy result requires every intended non-injected case accounted
   for, both endpoint verdicts and CRCs matched, no unexplained missing journal
   tail and positive cleanup. Report first-pass errors and all retries even when
   the last attempt passes. A completed run with failures is not a clean pass.

## 10. Source basis

1. Official MOS [API](../../../../agon-docs/docs/mos/API.md), especially stream
   output, file handle lifetime and returned write counts; official
   [VDU commands](../../../../agon-docs/docs/vdp/VDU-Commands.md). Reviewed documentation
   checkout `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`; no source was modified.
   Its generic clock description does not override the selected EMOS clock.
2. Existing [parallel application contract](../protocols/application-network-parallel.md),
   `include/agon/net.h` and `include/agon/net_parallel.h`: current UART and
   parallel compositions are distinct. They do not yet provide this mixed-leg
   or fixture retry interface. Existing NM records allow 128 application bytes.
3. Existing [repeated transport results](../tasks/PARALLEL-001/REPEAT-RESULT-R01.md)
   and [live result](../tasks/PARALLEL-001/LIVE-RESULT-R01.md) provide bounded
   inspiration, not hours-long accuracy or mixed-carrier qualification.
4. The [appliance lifecycle](../procedures/test-appliances.md),
   [test execution protocol](../procedures/test-execution.md),
   [bench constraints](../qualification/bench-constraints.md) and
   [SD layout](../sd-layout.md) govern later execution.
