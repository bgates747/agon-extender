# Current handback: comparison completed, normal input restored

## Completed historical comparison and verified restoration

Original PRX-06 receiver with GPIO-only P4-PC remap failed its first1024-byte
record at the slowest24-NOP profile. First byte41, lastF4 (expected74), stored
CRC F3F4/calculatedBA67 instead of6474. Remaining21records were not armed.
Original sender assembly/sweep unchanged; only unattended launch adapted.
Analyzer acquisition passed:45seconds at24MHz,1,080,000,000samples; exactly1024
qualified falling clocks with READYlow, zero mismatches on observed source
D2/D4/D5/D6/D7. D0/D1/D3 were not observed; probes are on Agon header, not P4.
Full hash-verified logic.sr and USB verdict retained in ignored local evidence.
Failure without modern coordinator or full EDP means those are not its sole
necessary cause. Harness, hardware, SDK/toolchain and receiver memory/cache/DMA
attribution remain unresolved. No usable throughput or reverse-transfer claim.

After Author confirmed card in Agon, keyboard admission and actual remote-command
checks recovered. Final exact full-HDMI snapshot restored/all four segments
verified; P4 HTTP availability awaited before final Agon recovery reset.
Original38-byte startup independently read back,52remote packets accepted,
input ready/neutral, held0/pending0, listener exited. No active bench operation.
EMOS/mainboardVDP/wiring unchanged. No repair or production change. Earlier
unverified-restoration and current-keyboard-status statements above are history.
Evidence: agents/port008-live-qualification/devkit-control-r01/handback.json,
run-result.json, analyzer-summary.json, installation and restoration receipts.

## Corrected current state — post-flash keyboard regression

Keyboard worked BEFORE agent flashing. Post-flash photo shows KEYINPUT receiver
readiness timeout and mainboard fallback. Do not claim present keyboard operation
or a transient failure: those were agent misreadings. Full-HDMI flash readback
passed, but input restoration is NOT established. Historical comparison has sent
no payload. Further bench operations remain paused pending Author direction.

## Current pause — historical comparison not yet run

See [historical comparison](docs/tasks/PORT-008/DEVKIT-CONTROL-R01.md).
Standalone receiver flashed/verified, but no record armed or payload transferred.
Agent launcher text-mode startup comparison failed and returned15 (“Volume
timeout”); corrected launcher compiled but not deployed. Exact full-HDMI snapshot
rollback restored/foursegments verified. Agon SD currently mounted on Lenovo.
Original38-byte autoexec independently read/verified there, both commands valid;
no test launch remains. Author photo identifies the startup error as line2 KEYINPUT receiver-readiness
timeout, not syntax. MOS maps its FR_TIMEOUT to “Volume timeout”; not proof of
SD failure.
Agent reset while card-reseat reply pending; no more bench activity until Author
returns card and resumes. Current physical/input state in HARDWARE.local.md.

## New harness context — causal attribution remains open

Author reports roughly doubled P4-PC signal lead length and absent earlier
200–220ohm series data resistors. Signal integrity competes with DMA/publication
and TX configuration as explanation; do not interpret the snapshot as proof
of a software-only fault. Details in the latest snapshot record below and
HARDWARE.local.md. No further bench operation or rewiring performed.

## Latest bounded result — received-buffer snapshot

[Snapshot result](docs/tasks/PORT-008/DATA-SNAPSHOT-R01.md): P4 retained RX
fingerprint is already wrong before echo, while first/last16 bytes match.
Return D7 is low throughout first byte despite stored `ff`, so review TX
DMA/output too. Exact3456 clocks bothways; no remedy started. New full-HDMI
P4 data-r02 verified; same EMOS/mainboardVDP/startup/MOSlet. One run, no replay.
Startup verified, listener exited, input ready/neutral; bench idle/released.
Evidence agents/port008-live-qualification/data-snapshot-r01, current installation
and unchanged probe map in HARDWARE.local.md. Earlier checkpoints historical.

## Latest bounded result — clock and handshake capture

[Pinwalk r02](docs/tasks/PORT-008/PINWALK-R02.md): exact3456 payload clocks in
both directions; READY low throughout, one clean VALID interval each. Four
observed reverse bits match; D7 is wrong early, including entire first byte
cycle before Agon samples. Focus next review on P4 receive/storage/transmit;
no remedy started. Same firmware/fixture; no flash/startup edit/replay.
Missing mainboard SD was physically reseated, restoring input. Startup verified,
listener exited, input ready/neutral. Complete trace under ignored
agents/port008-live-qualification/pinwalk-r02; current probe map in HARDWARE.local.md.

## Latest bounded result — data pinwalk

[Eight-data-line pinwalk](docs/tasks/PORT-008/PINWALK-R01.md): all forward
wire mappings match; reverse waveform/readback corrupt. Existing fixture adapted
to EMOS-owned transport; no firmware/startup changes. Input ready/neutral,
listener exited, capture closed. Author controls next probe moves.

## Latest checkpoint — full-HDMI parallel data-only comparison

Author requested latest working full EDP/EMOS base without special transport
diagnostics. P4 port-008-data-r01-b2026-10-10-03-07-07Z installed/four segments
verified; existing latest verified EMOS retained; mainboard VDP unchanged.
No PCNT or private phase/pattern tracing. One-byte echo passes;255 bytes complete
both directions but returned byte3 differs.4096unrun; no uncertain replay.
Separate recovery resets restored input; original startup verified, listener
exited. Result docs/tasks/PORT-008/DATA-ONLY-CONTROL-R01.md. Production unchanged.
Earlier installed-image statements below describe preceding checkpoints.

# Returning developer / external-agent orientation

Documentation checkpoint: 2026-09-25 UTC. Begin with [README](README.md) and
[using an existing installation](docs/using-extender.md). Read the tracked `AGENTS.md` and the canonical workspace instructions it
references before work. Machine-specific bench configuration remains ignored. [TODO](TODO.md) owns
unfinished work; this handoff is not a competing task queue.

## 2026-10-09 active development checkpoint

The second authorized repair hour ends 2026-10-10 02:26:35 UTC.
[Current repair result](docs/tasks/PORT-008/LIVE-QUALIFICATION-BLOCK-R04.md)
and its receipt supersede earlier installation/bench checkpoints. P4 fixed-count
RX EOF plus independent PCNT CLOCK/VALID proofs and an EMOS forward-only
inactive preamble now pass physical one- and two-byte forward blocks. Two
fresh-session suite invocations both reject the 255-byte case: DMA reports 255,
PCNT counts 256 qualified clocks and 4 or 10 VALID edges. Seventeen later cases,
including reverse, are not run. Do not weaken exact proof or infer throughput.

Installed private P4 is `port-008-probe-r10-b2026-10-10-01-45-13Z`, fully
flash-verified. Installed EMOS is `agon-emos-v0.1.24-b2026-10-10-01-48-39Z`,
131,017 bytes / 55 free, with complete128KiB ROM readback. Mainboard Pingo VDP and
production remain unchanged. This private P4 is browser-output, not HDMI.
Original 38-byte startup and ordinary keyboard input have been recovered and
verified after each failed fixture. Retained batches are evidence, not retry scripts.

A separate warm Agon reset ambiguity was reproduced with actual boot adapters.
A proposed paired correction failed a reset-at-phase-3 counterexample and was
preserved under ignored `warm-reset-fresh-candidate`, then removed from maintained
source. The compiled EMOS-only candidate
`agon-emos-v0.1.24-b2026-10-10-02-17-41Z` uses 131,035 bytes / 37 free and is
NOT installed or qualified. Do not install it. The restored existing 736 paired
boot-adapter cases pass; the new counterexample remains a separate reproduction.

LC03-B/F03 remain open; no formal ExExt, ordinary parallel VDU or SD integration.
Emulator-coupled source remains uncommitted pending Author validation. Preserve
unrelated HOST-001 and EMOS application_peer work; older evidence is frozen.

## Current recorded position

1. EMOS v0.1.19 removes the cancelled external `.emo` loading machinery while
   retaining resident input, display and gateway services. Prefixed utilities
   load from `/emos`. [Implementation and physical deployment](docs/tasks/AUDIT-008/HARDWARE.md)
   record exact identities, ROM readback and the bounded checks; broader human
   gameplay acceptance is not implied.
2. The listener is an EMOSlet at `/emos/sdserve.bin`, invoked as
   `EMOS sdserve [--fast] /`. Both listener and host upload must opt into fast
   mode. [Current SD instructions](docs/mainboard-sd.md) supersede old `/mos`
   installation and bare `sdserve` examples. The ordinary application fallback
   remains separate.
3. P4 physical USB, browser capture and host keyboard automation exist.
   [Keyboard ownership](docs/remote-keyboard.md) applies in Legacy and ExCom.
   Remote typing requires Extender input to be admitted already; do not ask an
   agent to enable its own disabled path through that path.
4. The [current local bundle](production/README.md) selects accepted P4 r55,
   EMOS v0.1.19 and sdserve v0.2.0 with pinned host tools. Browser output requests
   full-frame RLE2/packed compression, not inter-frame differencing. Clean builds
   include the selected composition and validate both bootloader/application
   silicon settings. The earlier r01 package is non-deployable historical evidence.
5. Remote reset uses the separate Pi bridge described in the
   [reset guide](docs/bench-reset.md). It is neither a P4 reset nor a power cycle.
6. [AUDIT-009](docs/tasks/AUDIT-009.md) is reconciling documentation. Its inventory
   distinguishes reviewed procedures from unreviewed historical material. Do not
   infer full-documentation acceptance from this orientation update.

## Before bench work

Consult ignored `HARDWARE.local.md` and the latest applicable deployment receipt
for installed artifacts, owner and endpoints. Do not infer the live state from
this handoff or checkout HEAD. Read [bench constraints](docs/qualification/bench-constraints.md)
and [SD placement](docs/sd-layout.md) before fixture execution or deployment.
Observe current authorization and other agents' bench ownership.

Earlier handoff snapshots remain in Git history. Their installed-build claims,
uncommitted-work lists and startup descriptions were dated observations, not
current instructions. No firmware or hardware was changed for this documentation
checkpoint.
