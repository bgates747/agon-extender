# PORT-008 forward-only qualification procedure

Status: Candidate — physical execution requires separate Author authorization

Identity: `port-008-forward-qualification-r01`

Baseline: `port-008-forward-r01`, status `candidate`

Registry revision: `r16`

## Purpose and claim boundary

Qualify one bounded path: an ordinary eZ80 application sends the frozen
106-byte VDU stream through normal `RST.LIL 18h`; the fixed-purpose EMOS build
routes it over the preserved r01 forward-parallel harness; the retained VDP
parser executes it; and the P4 browser service publishes the expected RGB888
frame.

This procedure does not qualify reverse UART, a General Poll response, MOS
sysvar/completion effects, either-order power safety, powered-off isolation,
the r02/V1 circuit, Exclusive Compatible, Dual, or broad legacy software. The
r01 return sink remains discard-only throughout.

## Controlled inputs

1. P4 firmware `extender-vdp-v0.2.0`, candidate, Olimex P4 DevKit variant.
2. EMOS `agon-emos-v0.1.0`, candidate, built from corrected `agon-emos` commit
   `0e24b06` with `port/port008-forward.mk`. This is a fixed-purpose
   qualification workaround and is not a production EMOS configuration.
3. Fixture `agon-transport-fixture-r01`, generated from the same EMOS commit.
4. `light2-harness-r01` and
   `light2-extender-solderless-assembly-r01` only.
5. `la03-p4-probe-fixture-r01` for observed controls and selected data lines.
6. `olimex-p4-devkit-profile-r03` and `p4-ota-partition-layout-r01`.
7. Official `agon-flash` v1.9 at commit
   `e670b5bd910dfe372c29aa9e896e6c24cc8530ec`; record the exact installed
   `/mos/flash.bin` hash before use. Use its standard `-f` switch; no custom
   flash-utility build is needed or permitted by this procedure.
8. Active bench constraint BC-001 and ignored `HARDWARE.local.md`.

## Candidate freeze and clean builds

1. Commit and push every controlled identity, source, procedure, baseline, and
   script. Build only from clean worktrees at the recorded commits.
2. Assign independent UTC build IDs to the P4 and EMOS images. The fixture is
   revisioned source output and its full binary hash is fixed in
   `candidate.yaml`.
3. Build `p4-forward-vdp` with the exact P4 build ID. Require the retained
   Phase-F closure, `ForwardParallelStream`, r01 pin diagnostic, discard-only
   return diagnostic, no disconnected Stream, no rejected identity marker,
   and a staged factory image whose segments equal the standalone outputs.
4. Build EMOS through `mos-agondev` commit `29cd336` with the fixed-purpose
   profile and exact EMOS build ID. Require all repository tests, the
   product-linked UART-divisor gate, linked sender checks, exact General Poll
   bytes, exact r01 GPIO constants, register and interrupt-state preservation,
   bounded READY waits, data-before-falling-edge order, no reverse-UART call,
   and exact identity strings.
5. Generate and verify `P8VDU.BIN`. Require 118 bytes, SHA-256
   `3befe47e271f0351222ce1748a40bea5b8650f99f55069e1183f73d19f6e754a`,
   and its 106-byte payload hash
   `b5d2757ebf1bdaf0132b8a2a6683e749aa57aeb265ad23a25368451860f65595`.
6. Assemble an ignored candidate package with manifests and hashes. Any source,
   configuration, identity, procedure, or output change requires a new build
   ID and another review.

## Read-only preflight

1. Resolve the dedicated Pi, P4 stable USB identity, unique serial endpoint,
   analyzer, flash tool, and current P4 presence from `HARDWARE.local.md`.
2. Ask the Author to identify the exact mounted Agon SD card. Fail if zero or
   more than one target remains plausible; never choose by mount-name guess.
3. Hash and preserve the target card's existing `/autoexec.txt`. Require no
   `/!boot.obey` or `/autoexec.obey`, because MOS 3 gives those files priority.
4. Require `/mos/flash.bin` to be official v1.9 at its recorded hash. Require
   `/emos.bin`, `/emos-installed.bin`, and `/P8VDU.BIN` not to collide with
   unrelated existing files.
5. With both boards powered off, compare the physical assembly to r01 authority.
   Confirm common signal ground, no rail join, the controlled-power boundary,
   reset breakout disconnected, and every probe used in this run. The Author
   must re-seat or confirm the loose-prone green probe on P4 GPIO32.
6. Stage candidate artifacts only after local and destination hashes agree.
   Preserve the original card files in a run-specific recoverable backup.

## Stage A — keyboardless EMOS installation

This stage uses stock VDP video and official `agon-flash`; Extender transport
must not be active. The utility itself is an unmodified official v1.9 binary.
Only the temporary autoexec invocation is a keyboard-loss bench accommodation.

1. Write `/emos.bin` from the identified EMOS build and root `/autoexec.txt`
   with exact CRLF lines:

   ```text
   rename emos.bin emos-installed.bin
   flash mos emos-installed.bin -f
   ```

2. Safely unmount the card, install it in the powered-off Agon, and keep the P4
   electrically inactive according to the r01 controlled-power boundary.
3. Cold-boot the Agon. Require the rename to succeed, official flash v1.9 to
   identify a valid MOS image, erase/program/verify the eZ80 flash, report
   `Done`, and perform its normal automatic reset. Stop on any error or CRC
   failure; do not reset or remove power during erase/program/verify.
4. On the automatic second boot, require the first `rename` to fail because
   `/emos.bin` no longer exists. MOS `EXEC` must stop before the flash line;
   this expected failure is the one-shot guard.
5. Power down the Agon, remove the card, and return it to the development host.
   Require `/emos-installed.bin` to match the candidate hash and
   `/emos.bin` to be absent.

## Stage B — forward-only visible fixture

1. Replace `/autoexec.txt` with exact CRLF lines:

   ```text
   EMOS MODE EXTENDED
   P8VDU.BIN
   ```

2. Copy exact `P8VDU.BIN`; verify both card files byte-for-byte and safely
   unmount. Do not add a timer, GPIO command, EDU envelope, or response probe.
3. With both boards powered off, install the card and connect only the reviewed
   r01 harness and passive LA-03 probes. Confirm the P4 return path is not
   enabled and the reset breakout remains disconnected.
4. Power and boot the P4 first. Capture USB Serial/JTAG from ROM boot onward.
   Require exact source/build/status identity, ESP32-P4 revision 1.3, QIO
   80 MHz, 16 MiB flash, 360 MHz CPU, r01 receiver startup with READY released,
   DHCP lease, and `HTTP browser service ready`. Stop on panic, assertion,
   watchdog reset, restart loop, transport setup failure, or wrong identity.
5. Open the P4's plain HTTP browser endpoint and confirm the live page. Arm the
   logic analyzer if its required probe map has been physically verified.
6. Assign run ID `PORT-008-YYYY-MM-DD-HH-MM-SSZ` immediately before the Agon
   cold boot. Then power the Agon. Do not reset or change wiring during the
   transaction.
7. EMOS starts in Legacy. The first autoexec line requests Exclusive Extended;
   EMOS owns GPIO acquisition, sends the unchanged official General Poll
   request, and commits the route only after READY admission and physical
   completion. The response remains intentionally discarded.
8. The second line runs `P8VDU.BIN` through ordinary `RST.LIL 18h`. Require the
   fixture to return to MOS without reset or error while the P4 reports one
   complete 106-byte application record after its four-byte preparation poll.
9. Acquire an EVF1 frame after the fixture. Require 230,400 RGB888 bytes and
   payload SHA-256
   `d368967667b3eee2315e2bb86129e7f423d904abd203c93dd0810906d08783d8`.
   Preserve the raw payload, metadata, browser screenshot, and P4 diagnostics.
10. If analyzer capture is available, require released-idle start/end,
    active-low READY admission, active-low VALID transaction extent, falling
    CLOCK sampling, and no observed return-enable activation. Analyzer evidence
    supplements but does not replace the exact browser-frame oracle.

## Stop conditions and cleanup

Immediately stop on unexpected rail behavior, heat, odor, reset, identity,
flash verification, source hash, parser/transport failure, truncated record,
wrong frame hash, analyzer contention indication, or any departure from r01.
Preserve partial and failed evidence; do not retry under the same run ID.

After capture, power down both boards before disconnecting the harness or
probes. Restore the Author's original `/autoexec.txt` from the hash-bound backup
unless the Author explicitly requests another state. Leaving EMOS installed is
a separate Author disposition; the procedure does not silently restore or
retain firmware.

## Outcome

Pass only if installation, exact identities, P4 startup, explicit EMOS mode
commit, both forward records, exact browser payload, clean fixture return, and
all applicable electrical observations pass. Record any unavailable analyzer
cell as skipped with a reason. A pass qualifies only `port-008-forward-r01` and
stops for Author review before any reverse-UART implementation or test.
