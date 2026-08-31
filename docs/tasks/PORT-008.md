# PORT-008 — Implement and qualify the compatibility transport

## State

- Status: In progress — r01 P4 forward Stream adapter compile-valid; fixed-backend
  EMOS, cold-boot fixture, identity, procedure, and bench evidence pending
- Started: 2026-08-29 19:12 EDT
- Finished: --

## Intent

Implement the accepted physical transport direction for Extender compatibility:
an eight-bit parallel Agon-to-P4 command path and a P4-to-eZ80 UART1 response
path. Preserve the official VDP application-visible byte-stream and VDP
protocol-packet contracts while replacing the stock PICO-D4 UART hardware
binding with the selected Extender wiring and MOS/eZ80 integration.

This task exercises the actual retained VDP port; it must not substitute a
throwaway receiver, invented command vocabulary, or disposable protocol merely
to make the wiring move bytes. The first bidirectional end-to-end compatibility
canary is the existing official General Poll startup exchange. Before adding
that UART return path,
the task performs a forward-only visible-command tranche over the existing
controlled-power predecessor circuit. Neither tranche may invent a second
discovery handshake or promote the predecessor's experimental fixed-frame UART
protocol into the product design.

## Authority and inputs

- AUDIT-001 requirements `C01` through `C06` and wiring findings `W01` through
  `W05`.
- [SETUP-004 Work 1.c](SETUP-004.md#work-1c-execution-record) and its accepted
  low-level peripheral disposition.
- [`light2-harness-r01`](../../hardware/designs/light2-harness-r01/README.md)
  and `light2-extender-solderless-assembly-r01` for the bounded preserved
  forward-only prototype tranche.
- [`light2-harness-r02`](../../hardware/designs/light2-harness-r02/README.md)
  and `light2-extender-solderless-assembly-r02` for the frozen common-UART and
  forward-parallel target.
- [`la03-p4-probe-fixture-r01`](../../hardware/fixtures/la03-p4-probe-fixture-r01/README.md).
- Official VDP v2.16.0 Stream/parser/packet behavior and official MOS startup
  General Poll behavior.
- [HW-001](HW-001.md), which owns the selected common V1 four-signal UART and
  one-way forward-parallel electrical core. Review Gate 2 froze
  `light2-harness-r02`; exact r02 breadboard construction and powered bench
  qualification remain open.
- [ADR-0016](../decisions/ADR-0016-v1-transport-electrical-core.md), which
  accepts the four-chip transport topology without closing HW-001's remaining
  design and qualification gates.
- [ADR-0014](../decisions/ADR-0014-edu-operating-modes-and-service-architecture.md),
  [SETUP-005](SETUP-005.md), and the durable QUAL-001 matrix when established.
- [Versioning and qualified-run policy](../versions/README.md).
- PORT-003 Gate F run `PORT-003-2026-08-28-15-28-59Z`, which qualifies
  `extender-vdp-v0.1.1` only as a P4-retained-parser/display/browser target and
  makes no transport or Agon-integration claim.

## Required outcomes

1. Receive the selected forward parallel transport on the accepted P4 pins and
   deliver its application payload to the retained VDU Stream boundary in exact
   order without adding application-visible framing or semantics.
2. Return official VDP protocol packets to the eZ80 over UART1 at the accepted
   1,152,000-baud target with exact packet bytes and bounded buffering,
   backpressure, timeout, and recovery behavior.
3. Define and qualify any physical-link framing or integrity mechanism needed
   below the application byte stream as a separately versioned transport
   contract; do not confuse it with VDU or EDU command syntax.
4. Resolve and qualify shared PC0/PC1 parallel/UART ownership, transceiver
   enables, released-idle behavior, break-before-make, resets, failures, and
   coexistence with every retained P4 pin function.
5. Determine the required flow-control contract from official behavior and the
   split-link architecture. If the candidate harness cannot satisfy it, stop
   for a separately approved harness revision before changing wiring.
6. Supply the selected eZ80/MOS-side command routing and MOS-owned response
   parsing path. Extender must not write MOS sysvars or completion flags
   directly.
7. Run the unmodified official General Poll semantics end to end before adding
   any Extender-specific discovery or capability operation.
8. Qualify representative retained VDU streams and every required VDP response
   class against exact bytes, parser state, completion flags, sysvar effects,
   timing, malformed input, reset, and recovery requirements selected by the
   compatibility matrix.
9. Keep diagnostics off the protocol return stream and preserve legacy mode's
   requirement that Extender be logically and electrically absent.

## Work

### Prototype tranche — Exclusive Extended response vertical slice

Before freezing the complete multi-mode D003 contract, build a narrowly scoped
Exclusive Extended learning prototype. This is code-led architecture evidence,
not a production compatibility implementation or permission to infer the
remaining modes from one successful path. Accepted PORT-003 Gate F supplies
the retained official facade, parser integration, and browser-visible output
needed by the canary. The prototype must preserve that qualified source
boundary while replacing only the deliberately disconnected ingress binding.

1. Begin with a forward-only learning stage in the actual retained VDP port.
   Use a fixed-backend development EMOS build so ordinary official command
   bytes reach EDP/P4 firmware through
   the eight-bit parallel direction, then visibly execute a representative set
   of simple display commands. Use the existing controlled-power predecessor
   circuit only under its strict power discipline, keep the UART-return driver
   disabled, and treat the direct GPIO20/open-drain READY_N path as predecessor
   test wiring only. Qualify no either-order-power, powered-off, isolated-
   release, or production-circuit claim.
   The installed 220-ohm series values are accepted only as the experimental
   wiring state for this run; production selection remains deferred.
   The accepted visible fixture uses only official VDP commands: select a
   conventional bitmap mode, clear it, set text color, print a recognizable
   banner, reposition the text cursor, print a second string, set graphics
   color, draw lines and a filled rectangle, then change and visibly use one
   palette entry. Freeze exact bytes and expected pixels from official
   documentation before bench execution.
   The fixture originates in an ordinary eZ80 application through the normal
   MOS/VDU call surface. A fixed-purpose EMOS development build owns routing
   those unchanged bytes onto the parallel transport; the application neither
   manipulates transport GPIO nor uses a new application protocol.
   Agon and EMOS still boot in Legacy mode. After EDP/P4 has acquired its DHCP
   lease and the operator has confirmed the P4-served browser endpoint, the
   operator explicitly requests Exclusive Extended through the existing EMOS
   mode-command framework. A qualification-only forward adapter prepares and
   commits the route under that controlled authorization. With reverse UART
   disabled it cannot prove the eventual EDP handshake or a fully qualified
   runtime transition; it must report that limitation and cannot enable itself
   automatically at boot.
2. Stop for Author review of the forward-only command, display, and physical-
   transfer evidence before enabling any P4-to-eZ80 product traffic.
3. Make EDP/P4 firmware emit an exact official VDP response packet over the
   accepted UART1 return direction; use General Poll as the first canary and do
   not invent a disposable command or response protocol.
4. Route UART1 bytes into one bounded experimental parser owned by EMOS on the
   eZ80. EMOS alone may update canonical MOS sysvars and completion flags; EDP,
   applications, and resident services must not write those assets directly.
5. Exercise enough real code and controlled bench traffic to expose parser
   boundaries, packet ordering, buffering, pacing, timeout, reset, and failure
   assumptions. Record observations without generalizing beyond exercised
   bytes and signals.
6. Keep the onboard VDP outside the prototype's audio/video output and EDP
   response path. Peripheral-input integration, concurrent UART0 packets,
   Exclusive Compatible, Dual, the general EDU result domain, runtime mode
   transitions, and broad legacy-software qualification remain out of scope.
7. Stop for Author review of the bidirectional prototype and its findings. Feed accepted
   evidence back into REMED-001 Work 2.e and SETUP-005-D003 before designing
   the complete response architecture.

**Prototype gate:** before implementation or bench operation, present the
exact fixed-backend EMOS/EDP source boundary, initial visible command set,
later official packet canary, existing Exclusive Extended wiring profile,
minimum fixture, strict controlled-power safety checks, disabled-return proof,
and stop conditions for Author approval. This bounded gate does not require
the complete PORT-008.1 production transport contract or settle its Review
Gate 1.

This tranche may perform the minimum official-source review needed to preserve
wire contracts and memory safety. It must not turn into a survey-only planning
exercise before the first bounded implementation, nor may experimental code be
promoted into the product architecture merely because it runs.

### Prototype execution record

#### 2026-08-29 — P4 forward boundary checkpoint

1. **Authorization and stopping boundary.** The Author previously approved the
   prototype plan and authorized implementation, then directed work to resume
   on the preserved `light2-extender-solderless-assembly-r01` while the new r02
   board is constructed separately. This checkpoint stops after compile-valid
   P4 ingress. It makes no EMOS, fixture, deployment, electrical, or visible-
   output claim.
2. **Official application contract.** Official Agon documentation states that
   VDP input is an unframed byte stream and that `RST 10h` and `RST 18h` send
   raw binary VDU bytes. The retained `VDUStreamProcessor` still owns command
   parsing. The new adapter supplies only its existing Arduino `Stream` input;
   it does not add an application command, envelope, length, padding byte, or
   parser.
3. **Physical record boundary.** ESP-IDF 5.5.5's
   `parlio_rx_level_delimiter_config_t` explicitly defines
   `eof_data_len = 0` as receive completion when the enable signal becomes
   inactive. The r01 receiver therefore uses active-low `VALID_N` deassertion
   to terminate a variable-length physical record. This removes the suspected
   need for a below-stream length prefix. Physical record boundaries disappear
   at the Stream queue and do not change VDU byte semantics.
4. **Selected r01 binding.** `ForwardParallelStream` uses the authoritative r01
   mapping D0--D7 = P4 GPIO 22, 12, 23, 11, 32, 10, 33, 9; external CLOCK =
   GPIO14 sampled on its falling edge; active-low VALID = GPIO13; and active-
   low open-drain READY = GPIO20. It retains the predecessor's ESP-IDF PARLIO
   idiom but not its canary, fixed-size record, or application framing.
5. **Backpressure and failure behavior.** One receiver task arms a 4096-byte
   DMA record only when the 8192-byte FreeRTOS stream buffer has room for the
   complete maximum record. GPIO20 asserts READY only after DMA is armed and
   releases it immediately after completion. Any receive error, zero/oversize
   completion, READY release failure, or impossible short enqueue stops the
   receiver with READY released instead of exposing a truncated VDU stream.
6. **Return exclusion.** Every retained VDP write into this Stream is discarded
   and counted. `setVDPProtocolDuplex` remains an explicit no-op. The new build
   selects no UART output source and makes no P4-to-eZ80 claim.
7. **Build boundary.** New PlatformIO environment `p4-forward-vdp` inherits the
   accepted `p4-browser-vdp` closure, replaces only
   `disconnected_stream.cpp` with `forward_parallel_stream.cpp`, and defines
   `AGON_EXTENDER_PORT008_FORWARD`. Its machine-readable source selection
   retains the same official header-defined implementation and vdp-gl closure.
8. **Compile evidence.** `scripts/vdp-pio.sh run -e p4-forward-vdp` completed
   successfully in 56.25 seconds after correcting two compile-visible API
   details: C++17 requires ESP-IDF structure designators in declaration order,
   and `gpio_num_t` requires `GPIO_NUM_NC` rather than integer `-1`. The first
   attempt also rebuilt PlatformIO's private environment because it retained
   Python 3.12 while the project invoked Python 3.14. The final image used
   47,224 bytes of reported RAM and 1,247,354 bytes of flash.
9. **Fail-closed identity.** No firmware revision or build identity was
   assigned without Author approval. The linked image contains
   `UNVERSIONED-DO-NOT-DEPLOY`; it must not be staged, flashed, or cited as a
   candidate artifact.
10. **Next implementation boundary.** A fixed-purpose development EMOS adapter
    must route unchanged ordinary VDU bytes through the r01 sender and must
    arrange the official General Poll request needed to release the retained
    VDP startup wait while reverse writes remain disabled. BC-001 requires the
    accepted 106-byte visible fixture and mode invocation to run from root
    `/autoexec.txt`. Those changes, artifact identities, a committed physical
    procedure, and bench authorization remain pending.

### PORT-008.1 — Freeze transport and wiring contracts

1. Extract the exact official Stream, UART, packet, timeout, flow-control, and
   General Poll contracts from the pinned VDP/MOS sources and documentation.
2. Reconcile those contracts with `light2-harness-r02`, using r01 PARLIO and
   115,200-baud results only as predecessor evidence, plus the selected P4
   peripherals and QUAL-001 rows.
3. Produce a pin-conflict, ownership-state, flow-control, buffering, and
   failure-state analysis without changing hardware.
4. Identify whether the candidate wiring is sufficient. Any required wire,
   component, enable-logic, or pin change is a proposed new harness revision and
   an Author stop gate.

**Review Gate 1:** Author approves the transport contract, physical ownership
model, test phases, and either the existing harness sufficiency finding or a
separate hardware-revision proposal before production implementation beyond
the bounded prototype tranche.

### PORT-008.2 — Implement the P4 transport boundary

1. Add the project-owned parallel receiver and Stream-compatible adapter behind
   the retained VDU parser boundary.
2. Add the project-owned UART1 packet-output adapter and selected pacing/flow
   control without changing official packet generation.
3. Keep P4 pin assignments visible, centralized, and traceable to the approved
   harness profile.
4. Add deterministic host tests for byte ordering, boundaries, buffering,
   timeout, error, recovery, packet transparency, and ownership state.
5. Update source selection, dependency graphs, compatibility matrix rows, and
   provenance-rich inline comments for every unavoidable hardware substitution.

### PORT-008.3 — Implement the eZ80/MOS integration boundary

1. Outside the bounded prototype tranche, implement the selected command
   backend and UART1 response-parser route only after `SETUP-005-D001` through
   `D003` authorize the relevant mode behavior.
2. Reuse MOS's canonical packet/sysvar ownership wherever selected; do not
   create a competing sysvar writer.
3. Preserve stock UART0/onboard-VDP input handling and legacy fallback according
   to the accepted mode design.
4. Provide bounded eZ80 fixtures for exact transport and parser behavior before
   attempting broad application tests.

### PORT-008.4 — Qualify physical transport

1. Freeze versioned firmware, MOS/eZ80 fixture, harness, analyzer fixture,
   procedure, build, and run identities before each decision-bearing run.
2. Requalify all eight forward data lines and control signals on the clean
   project, including integrity, backpressure, sustained transfer, reset, and
   recovery.
3. Qualify UART1 return at 1,152,000 baud and the accepted flow-control behavior.
4. Measure shared-net ownership and prove no contention through every selected
   transition and failure state.
5. Preserve raw analyzer/serial evidence and bound every claim to signals
   actually observed or independently validated.

### PORT-008.5 — Qualify official compatibility traffic

1. Run the official General Poll startup synchronization as the first
   end-to-end Agon/MOS/Extender canary.
2. Expand only through compatibility-matrix-selected command/response classes;
   do not invent disposable application protocols to stand in for them.
3. Verify exact MOS-owned packet, completion-flag, and sysvar effects.
4. Exercise selected fragmented, back-to-back, stalled, malformed, overrun,
   reset, and recovery cases according to the accepted strict/non-strict mode
   policy.

**Review Gate 2:** Author reviews qualified transport and General Poll evidence
before this task can gate integrated compatibility claims.

## Dependencies and sequencing gates

- Active bench constraint BC-001 requires every eZ80 text fixture to be
  cold-boot executable through the Agon SD card's root `/autoexec.txt`, with no
  interactive keyboard prerequisite. Record the exact invocation and a
  non-keyboard evidence path before each affected run.
- QUAL-001 Review Gate 1 must be accepted before contract implementation, and
  its baseline matrix must exist before PORT-008 qualification evidence is
  recorded.
- PORT-003 Gate F provides the qualified retained VDU/parser/mode lifecycle and
  browser-output target. It does not qualify physical ingress, General Poll,
  EMOS routing, or any Agon integration; PORT-008 must establish those claims
  through its own approved prototype and qualification gates.
- `SETUP-005-D001` and `D002` authorize only the bounded Exclusive Extended
  prototype above. D003 remains open and gates production response parsing,
  generalized MOS sysvar integration, Exclusive Compatible, Dual's separate
  EDU result domain, and broad compatibility qualification. Prototype findings
  remain visibly provisional until the Author accepts their D003 disposition.
- QUAL-002 begins only after a controlled transport candidate exists and gates
  final qualification of assembled-system power/reset behavior.
- PORT-008 Gate 2 is required before PORT-003 Gate G or later tasks claim
  end-to-end Agon compatibility through Extender.
- Read `HARDWARE.local.md` before any physical operation. No bench action is
  authorized by this task plan; each candidate procedure and physical run
  requires the established review and deployment gates.

## Stock-UART hardware boundary

The Author clarified during
[`AUDIT-2026-08-23-001`](../decisions/AUDIT-2026-08-23-001-operating-mode-semantics.md)
that `light2-harness-r01` is not a candidate implementation of Exclusive
Compatible mode's stock-UART transport. It was designed for the predecessor's enhanced
parallel-forward/reverse-UART architecture and must not be incrementally tested
or relabeled into stock physical or firmware conformance.

Exclusive Compatible mode requires hardware-independent firmware work first.
That work must freeze the endpoint, signaling, flow-control, timing, reset,
failure, and recovery requirements through deterministic tests without waiting
for physical qualification. The separate HW-001 design-review task now owns
the frozen `light2-harness-r02` common UART/parallel candidate and records the
firmware dependencies it cannot settle electrically. No stock-UART bench test
against `light2-harness-r01` is authorized or useful. Construction of the r02
assembly is permitted, but powered tests remain procedure-gated.

The final task split remains under SETUP-005. This boundary does not change
PORT-008's currently approved Exclusive Extended split-link work; it
prevents that work and its harness from being mistaken for the newly identified
stock-UART profile.

## Explicit exclusions

- No reverse high-speed parallel bus.
- No new VDU/EDU discovery packet merely for testing.
- No adoption of the predecessor's fixed eight-byte UART experiment as product
  protocol.
- No direct P4 writes to MOS memory or sysvars.
- No Console8 pin assignment; that requires a separate harness task.
- No printer, terminal, ZDI, serial updater, or other accepted maintenance
  carve-out implementation.

## Completion criteria

1. Both review gates are approved.
2. The selected Light 2 transport and any required revised harness are
   versioned and qualified at target speed.
3. The official General Poll passes end to end with exact MOS-visible effects.
4. Required command/response classes have deterministic host evidence and
   controlled physical evidence or an accepted blocker/deferral in QUAL-001.
5. Shared-net ownership, flow control, resets, error recovery, and coexistence
   have no unexplained qualification gap.
6. Source selection, dependencies, compatibility matrix, procedures, artifacts,
   runs, and development log agree.
