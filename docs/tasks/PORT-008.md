# PORT-008 — Implement and qualify the compatibility transport

## State

- Status: In progress — r01 P4 and corrected fixed-purpose EMOS forward path
  implemented and non-physically qualified; clean identified candidate packages
  prepared; exact SD card identified and read-only preflighted; existing media
  collision, physical inspection, separate deployment authorization, and
  forward-only physical evidence pending
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

#### 2026-08-30 — EMOS forward adapter and fixture checkpoint

1. **Immutable source identities.** P4 ingress remains frozen at
   `agon-extender` commit `c03656c`. The eZ80 sender, mode adapter, VDU routing,
   fixture generator, deterministic checks, and approved emulator evidence are
   frozen in `agon-emos` commit `08fec48`. Reusable product-profile,
   configured-source runtime-audit, named-worktree, and graphical-launcher
   support is frozen in `mos-agondev` commit `5079d4c`.
2. **Ordinary application surface.** `RST 10h`, `RST 18h`, and C `putch` retain
   raw ordinary VDU bytes. Standard bounded `RST 18h` maps one application
   block to one physical record without an application envelope; delimiter
   mode and single-character calls use one-byte records. Legacy continues to
   use the onboard VDP's UART0 path.
3. **Fixed-purpose physical sender.** The profile-selected EMOS adapter uses
   the preserved r01 Port C data bus and Port D READY/CLOCK/VALID signals. It
   snapshots and restores affected GPIO registers and interrupt-enable state,
   admits and completes each record through bounded active-low READY waits,
   writes data before each falling clock edge, rejects empty, reentrant, and
   over-4096-byte records, and contains no reverse-UART call.
4. **Mode authority and startup release.** Only an EMOS-owned Exclusive
   Extended request may prepare this adapter. Preparation acquires the GPIOs
   and sends exact official General Poll request bytes `23, 0, 0x80, 1`; route
   commitment follows successful physical completion. Failed preparation
   restores the GPIO snapshot and leaves the public mode in Legacy. Exclusive
   Compatible and Dual are unavailable through this physical adapter.
5. **Cold-boot fixture.** `agon-emos/projects/port008-forward/fixture.json`
   freezes the accepted 106-byte ordinary VDU command at SHA-256
   `b5d2757ebf1bdaf0132b8a2a6683e749aa57aeb265ad23a25368451860f65595`.
   Its generated 118-byte `P8VDU.BIN` includes a 12-byte `RST.LIL 18h` wrapper
   and measured SHA-256
   `3befe47e271f0351222ce1748a40bea5b8650f99f55069e1183f73d19f6e754a`.
   The eventual SD-card procedure uses `/emos.bin`, `/P8VDU.BIN`, and an
   `/autoexec.txt` containing `EMOS MODE EXTENDED` followed by `P8VDU.BIN`.
6. **Build and deterministic evidence.** The fixed-purpose EMOS image measured
   113,935 bytes at SHA-256
   `1675baf089ecd1420b59a546e5316519ec7b20e7000a3fe3f2c4493604984f9b`.
   These measurements are not deployable identities. Source tests and linked
   disassembly verify the GPIO mapping, register preservation, General Poll,
   record bound, data/clock ordering, forward-only boundary, and fixture. The
   no-macro ordinary profile also builds with the physical adapter unavailable.
7. **Non-physical qualification.** All 50 `agon-emos` tests and the complete
   configured `mos-agondev` gate passed, including translation, compilation,
   restricted runtime closure, linking, headless boot, stock shell parity, VDP
   regressions, and target ABI/FatFS contracts. The Author then approved the
   graphical emulator gate after observing provider discovery; Legacy to fake
   Dual and back to Legacy; keyboard entry; root and `/bin` directory access;
   `help echo`; `time`; `credits`; `mem`; and a responsive prompt.
8. **Bounded claim.** This checkpoint proves source integration and emulator
   compatibility only. It does not prove r01 electrical transfer, visible P4
   browser output from the fixture, General Poll response identity, canonical
   MOS response/sysvar effects, reverse UART, either-order power behavior, or
   any r02/V1 circuit property. One `RST 18h` block above 4096 bytes is
   currently rejected rather than split.
9. **Next gate.** Assign reviewed deployable EMOS, P4, fixture, procedure, and
   run identities; freeze the exact controlled-power r01 procedure; stage media
   only from those commits; and obtain separate bench authorization before the
   forward-only visible-command run. Stop for Author review of that physical
   evidence before enabling P4-to-eZ80 traffic.

#### 2026-08-31 — Forward qualification candidate preparation

1. **Approved identities.** The Author approved `extender-vdp-v0.2.0`,
   `agon-emos-v0.1.0`, `agon-transport-fixture-r01`,
   `port-008-forward-qualification-r01`, and baseline
   `port-008-forward-r01`. Independent UTC build IDs remain unassigned until
   clean committed builds begin; the run ID remains unassigned until the Agon
   cold boot that starts the physical run.
2. **EMOS freeze.** The exact source identity and fail-closed ordinary-build
   behavior are frozen in `agon-emos` commit `59c3102`. The Author graphically
   approved that emulator-coupled change; all 51 repository tests passed under
   the selected worktree. The fixed-purpose `port008-forward` profile remains
   a qualification-only EMOS configuration.
3. **P4 candidate input.** `p4-forward-vdp-identity.json` assigns the approved
   source identity to the existing forward-ingress environment. A task-local
   validator reuses the complete PORT-003 Phase-F closure and changes only its
   ingress assertions: `ForwardParallelStream`, the exact r01 startup
   diagnostic, discard-only return, and absence of `DisconnectedStream`.
4. **Staging and oracle tooling.** The task-local stager reuses the proven
   clean-worktree, identity, and factory-segment checks while emitting the
   narrower PORT-008 claim. The frame-capture tool reuses the established EVF1
   parser, saves the raw RGB888 payload, and requires the frozen 230,400-byte
   SHA-256 oracle without recording the private endpoint.
5. **Keyboardless installation.** Official unmodified `agon-flash` v1.9 already
   provides `-f`; no custom flash-utility build is required. The temporary
   two-line autoexec renames `/emos.bin` before invoking `flash ... -f`, so the
   utility's automatic reset reaches a failing rename rather than flashing a
   second time. This one-shot media arrangement, not the flash utility, is the
   BC-001 bench workaround.
6. **Physical gate remains closed.** The candidate baseline and procedure
   freeze the controlled r01 wiring, two distinct SD-card states, exact hashes,
   P4-first boot order, stop conditions, and bounded claim. No mounted card,
   firmware, wiring, power state, reset, or harness traffic may be changed
   until clean build manifests and read-only preflight are presented and the
   Author separately authorizes those physical actions.

#### 2026-08-31 — Original EMOS hardware-failure capture

1. **Failure preserved.** After restoring stock VDP v2.14.1 Dressing Gown on the onboard
   ESP32, the physical Agon again displayed the VDP banner without a MOS banner
   or flashing cursor. The normal Extender harness was disconnected. An
   external P4 used only GPIO46-to-ZDI-TCK, GPIO47-to-ZDI-TDI, and common
   ground, leaving both boards' power rails separate.
2. **Bounded observer.** A temporary `p4-zdi-probe` environment ports the
   proven `agon-recovery` ZDI operations to P4 GPIO and the USB Serial/JTAG
   console. It contains no target flash, reset, RAM-write, resume, product
   transport, or production command surface. Failed USB console input required
   an identity-gated delayed one-shot capture; all three product reads had to
   be `0007` and the eZ80 had to be running before the halt.
3. **Captured execution.** Run `PORT-008-2026-08-31-21-55-19Z` halted at
   `PC=0x0009EA`. Candidate map, code bytes, and stack place execution in
   `_wait_timer0`, called by `_wait_ESP32` during MOS startup. `gp=0` confirms
   that the official General Poll response had not completed.
4. **Timer finding.** Timer 0 control/data were `0x84`/`0x0000`. The sampled
   timeout had expired and was about to return, so the visible failure is not
   a Timer 0 deadlock; EMOS was repeatedly timing out while waiting for `gp`.
5. **UART finding.** `serialFlags=0x03`, `LCR=0x03`, `MCR=0x02`, `LSR=0x60`,
   and `MSR=0x10` show enabled 8N1 UART0 with hardware flow control, accepted
   CTS, an empty transmitter, and no received byte. This does not establish
   whether the request reached stock VDP or whether the missing response is an
   electrical, VDP-side, baud/configuration, or receive-path defect.
6. **Coherent discriminator.** Rebooting the P4 after the first halt changed
   the ZDI context, and a strict supplement refused to touch UART state at the
   changed PC. After a manual target reset, run
   `PORT-008-2026-08-31-22-27-18Z` reproduced the stopped execution state and
   read UART0 divisor `0x000B` inside the same halt epoch, restoring LCR and
   AF/MB before continuing.
7. **Identity correction.** The candidate YAML contained a mistyped,
   nonexistent long `agon-emos` object name. It now records the actual clean
   source commit `59c31026e1229395d9a9ba44f71cda7b8e78b9f3`; all existing
   short `59c3102` references already named that commit unambiguously.
8. **Root cause.** At 18.432 MHz, 1,152,000 baud requires divisor 1. In the
   AgonDev build, the inherited `16 * baudRate` expression was evaluated at
   native 24-bit width before assignment to `UINT32`; the wrapped product
   makes the subsequent division return 11 exactly. This is a source
   portability defect exposed by AgonDev, not intended stock MOS behavior.
   `agon-emos` QUAL-001 owns the narrow widening correction, deterministic
   linked regression, emulator acceptance, and replacement physical candidate.
9. **Corrective emulator gate.** The widened UART0/UART1 source passed all
   machine checks and the Author's graphical emulator review. The normal MOS
   prompt appeared, EMOS reported its expected identity and three providers,
   service calls completed, and Legacy to Dual to Legacy transitions worked.
   The correction is still uncommitted and no replacement hardware candidate
   has been identified, built from clean source, or authorized for deployment.
10. **Recovery candidate prepared.** The failed installed EMOS cannot run the
    SD-card flash utility. A temporary P4-to-ZDI recovery image therefore embeds
    the exact corrected 114,069-byte EMOS image and upstream `agon-recovery`
    flash agent. Deterministic payload regeneration, isolated source closure,
    image validation, live P4 USB-identity preflight, and remote staging pass.
    Its factory-image SHA-256 is
    `741135661f1f3ce46ddf0f7593c6144195f9e56b7d1e44d8ef69bbc8e0d0d7e6`.
11. **Physical correction passed.** Run
    `PORT-008-2026-08-31-23-11-18Z` used that one-shot image to program and
    read back the exact corrected EMOS payload. The Author then cold-booted
    physical VDP v2.14.1/MOS 3.0.2 and graphically confirmed provider
    discovery, both service calls, fake Dual, final Legacy generation 2, and
    return to the prompt. The onboard ESP32 was then directly flashed from the
    clean official VDP v2.16.0 tag and its writes verified by esptool. After an
    Agon reset, the same keyboardless fixture passed unchanged against VDP
    v2.16.0. This closes the dirty-source boot-blocker diagnostic against the
    task's official VDP baseline; it does not qualify or release the
    unversioned EMOS build.

#### 2026-08-31 — Corrected candidate refreeze

1. The UART-width correction, its physical diagnosis, and the product-owned
   linked-image guard are frozen in `agon-emos` commit `0e24b06` and
   `mos-agondev` commit `29cd336`. The Author approved and pushed both commits.
2. The forward-r01 candidate now selects those corrected authorities while
   retaining `agon-emos-v0.1.0`, the fixed-purpose `port008-forward` profile,
   and the unchanged fixture and frame-oracle bytes. The failed dirty-source
   recovery image remains diagnostic evidence and is not a candidate input.
3. The next controlled boundary is a clean identified P4 build, clean
   identified fixed-purpose EMOS build, deterministic fixture regeneration,
   and read-only deployment preflight. No flash, SD-card write, reset, power,
   or harness operation is authorized by this refreeze.

#### 2026-09-01 UTC — Identified candidate build and read-only preflight

1. **Clean authorities.** The candidate input was committed and pushed as
   `agon-extender` commit `acf9ded5c7936fe61c6377f367ac8c96c3984b78`.
   Clean `agon-emos` commit
   `0e24b06abdb322fdb4e681a21242ccfebfc8ea65` and clean `mos-agondev`
   commit `29cd336f472164156de330cf77c69a4eda450527` supplied the fixed-purpose
   EMOS source and AgonDev build system. The prepared MOS tree contains 126
   tracked files and records the exact clean EMOS source commit.
2. **P4 candidate.** Clean build
   `extender-vdp-v0.2.0-b2026-09-01-00-20-07Z` passed the task-local linked
   closure validator: 24 selected translation units, five assets, 18 required
   symbols, C++17, and all exclusions. Its application image is 1,248,288
   bytes at SHA-256
   `a243e7b2fada7f1f166fa6e7be3a2aa718d606688f1046c88af02f8aaff05ee0`;
   its complete factory image is 1,379,360 bytes at SHA-256
   `bdb9553e87ff73f2d8f5f3cdbe45192618b8c493fe75460eb35bbbe1af225dad`.
   Factory-segment equality and embedded source/build/status identity passed.
3. **EMOS candidate and fixture.** Clean fixed-purpose build
   `agon-emos-v0.1.0-b2026-09-01-00-20-07Z` passed provenance, final-image
   identity, UART-divisor, linked sender-order, General Poll, and exact fixture
   gates. Its 114,082-byte binary has SHA-256
   `8c356f95cb901edcf675e8add5567316a324e5c43559f3034c54218f3998f231`.
   Regenerated `P8VDU.BIN` remains 118 bytes at SHA-256
   `3befe47e271f0351222ce1748a40bea5b8650f99f55069e1183f73d19f6e754a`,
   containing the frozen 106-byte VDU payload unchanged.
4. **Software qualification.** All 54 `agon-emos` tests and all 106
   `mos-agondev` tests passed. The ignored build-ID-specific packages contain
   adjacent manifests, hashes, P4 closure/exclusion evidence, EMOS ELF/HEX/map
   outputs, and the exact fixture. All three controlled repositories remained
   clean after generation and validation.
5. **Read-only bench preflight.** The dedicated Pi was reachable; the stable
   P4 USB identity resolved to one serial endpoint; the logic analyzer,
   Espressif flash tool, Python, and established remote staging root were
   present. No removable SD medium was inserted: both visible reader endpoints
   reported zero-byte empty devices. The procedure therefore stopped before
   selecting a card, reading card files, staging media, or taking any physical
   action.
6. **Closed physical boundary.** No firmware was copied or flashed; no SD-card
   file was read or written; and no reset, power, wiring, probe, or harness
   traffic operation occurred. The next gate requires the Author to identify
   the exact inserted Agon card, followed by the powered-off r01 assembly and
   probe inspection and separate authorization of physical mutation.

#### 2026-09-01 UTC — Exact SD-card read-only preflight

1. **Unambiguous medium.** After the Author inserted the intended card, exactly
   one nonempty removable medium was visible: a 29.7 GB FAT volume labeled
   `AGON`. The other reader endpoint remained empty. This satisfies the
   procedure's Author-identification and no-guessing requirement for this
   mounted-card epoch.
2. **Boot-file state.** Root `/!boot.obey` and `/autoexec.obey` are absent.
   Existing `/autoexec.txt` is a 205-byte CRLF EMOS smoke fixture at SHA-256
   `e6ba3cdc87bb22461d7de131c95a44b680b33304821e9091adfb5066fda597e0`.
   It must be copied into the eventual run-specific recoverable backup before
   any authorized replacement.
3. **Official flasher.** `/mos/flash.bin` is 15,624 bytes at SHA-256
   `480b476703b798cf8d93294cac42d77cad93f7747003b061520b86685c75eb57`.
   A fresh download of the
   [official v1.9 release asset](https://github.com/AgonPlatform/agon-flash/releases/tag/v1.9)
   matched it byte for byte.
4. **Candidate-name check.** Root `/emos.bin` and `/P8VDU.BIN` are absent.
   Root `/emos-installed.bin` is the known prior 114,069-byte unversioned
   diagnostic EMOS at SHA-256
   `bf7633f9853e812d806a6528450d268db68541b12df0dcb47b4f68b15a130478`.
   It is related evidence rather than an unknown collision, but it still
   occupies the one-shot rename destination and must be preserved or relocated
   before Stage A can be staged.
5. **Stop boundary.** This check only read card metadata and file bytes. It did
   not copy, rename, replace, delete, unmount, or otherwise modify the card.
   Media backup and collision resolution belong to the separately authorized
   staging action; powered-off r01 wiring and probe inspection remains the
   other prerequisite to deployment.

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
