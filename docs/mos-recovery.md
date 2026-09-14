# Maintained MOS recovery protocol

## Executive summary

Recover an Agon that cannot reach MOS using an external programmer connected
to the eZ80 ZDI interface. The **P4 method actually succeeded on this bench on
2026-08-31**; the spare WROOM method was only planned. Keep the onboard VDP
installed, verify the programmed eZ80 flash, then separately prove boot and
keyboard/service recovery. An SD payload or a successful `FLASH` command
submission is not proof of a restored ROM.

Procedure identity: **mos-recovery-r01**. Status: maintained protocol;
maintained implementation; scoped physical recovery passed on the recorded bench.
Created 2026-09-14 at the Author's explicit request. This is enduring operating
documentation, not a disposable task or an automatically executing checklist.
Initial publication was documentation-only. The Author subsequently authorized
recovery of known-good EMOS under [RECOVERY-001](tasks/RECOVERY-001.md).

## Maintenance contract

1. Do not retire this protocol when an investigation finishes. Update it in
   place and preserve its stable path and incoming links.
2. Individual defective, obsolete or payload-specific binaries may be rejected
   or retired. That must not silently retire the recovery capability. Record
   any resulting readiness gap here and in the authoritative TODO when work
   is promoted; never describe an unavailable tool as ready.
3. Promote reusable recovery implementation out of historical task directories.
   Retain historical evidence and guardrails. Do not bypass retired build
   selectors or deploy their embedded payloads merely because they once worked.
4. Record the actual recovery method used. A proposed WROOM alternative is not
   a performed WROOM recovery. A Pi reset through the ZDI connector is not ZDI
   programming.

## Authority and current readiness

The [successful P4 run](tasks/PORT-008/emos-hardware-diagnostic/README.md#prepared-one-shot-zdi-recovery)
uploaded and verified both RAM payloads, executed the upstream flash agent,
read back the programmed MOS image and checked its CRC32. After the Author
reset the target, MOS booted. That image embedded a particular corrective
EMOS build; it is **not** a generic stock-MOS recovery image.

Its source remains at
`vdp/video/extender/diagnostic/p4_zdi_mos_recovery.cpp`, with the associated
payload generator under `docs/tasks/PORT-008/emos-hardware-diagnostic/`.
Both are retired historical references, not current execution entry points.
The maintained replacement now builds under `p4-mos-recovery`, selecting
`vdp/video/extender/recovery/mos_recovery.cpp`. The connected-harness recovery
under RECOVERY-001 passed; this validates the recorded board, payload and build,
not arbitrary targets. Historical selectors remain retired. Prepare payloads with:

```sh
.venv/bin/python scripts/prepare_mos_recovery.py \
  --mos /path/to/known-good-rom.bin --mos-sha256 EXACT_SHA256 \
  --flash-agent /path/to/upstream-90-byte-flash.bin \
  --output vdp/video/extender/recovery/generated/mos_recovery_payload.hpp
.venv/bin/pio run -d vdp -e p4-mos-recovery
.venv/bin/python -m unittest discover -s tests -p test_mos_recovery.py -v
```

These are preparation commands, not deployment commands. On the USB host,
`scripts/mos_recovery_console.py --help` documents capture arguments. Default
behavior is dump-only; `--restore` allows the exact SHA-bound restore command
only after a complete verified pre-erase dump. An already-matching ROM is not
erased. Use the active run's manifest and preserved P4 image for deployment;
never borrow another run's device names or unchecked flash commands.

The algorithm authority is upstream
[agon-recovery, commit 95d68464afd049945e1dfd780c1c07621d565450](https://github.com/AgonPlatform/agon-recovery/tree/95d68464afd049945e1dfd780c1c07621d565450).
Preserve its ZDI and flash-agent logic; adapt only the P4 GPIO, console and
necessary execution environment. The historical 90-byte flash agent SHA-256 is
`ca44786969dc2dd1b0fa51e6b80f530b7241317dc27bf8efac3ca7d56bddee06`.

The [WROOM contingency](../../agon-emos/docs/tasks/QUAL-002.md#recovery-payload-and-method)
is an alternative requiring its own preparation, not the default proven bench
path. It maps GPIO26/27, unlike the P4 mapping below.

## Before touching hardware

1. Read `HARDWARE.local.md`, the active bench constraints, and the relevant
   EMOS incident record. Resolve current device identities and ownership.
   Record the screen, boot sequence and last installed image; do not infer ROM
   corruption solely from the VDP banner. Failure to exchange the startup
   General Poll can produce the same symptom.
2. Preserve the selected P4's installed image and the exact restoration
   procedure. Record firmware identities, hashes, partition layout and tools.
   Replacing P4 firmware temporarily removes network SD and keyboard services.
3. Preserve SD startup and any guarded installer files. If MOS cannot reach
   autoexec, SD scripts cannot repair its flash. Physical SD access is then
   needed to prepare a safe first boot; do not assume the service is available.
4. Choose and record the recovery payload explicitly: known-good EMOS with
   physical validation evidence, or official stock MOS. Capture length, SHA-256,
   CRC32, source/release and reason. Never select a candidate merely because it
   is newest, and never silently substitute an upstream bundled MOS file.
5. Stock MOS 3.0.2 was previously verified as 108,490 bytes, SHA-256
   `d564243283972690933a4554296ad6202ca4ef54572279533a942960846bebae`.
   Recheck selected bytes before use. Stock MOS does not provide Extender
   keyboard input: this bench's damaged mainboard keyboard interface requires
   a keyboardless boot proof and a separately prepared EMOS installation path.
6. Prepare a manifest-bound programmer with explicit operator arming, finite
   timeouts, identity refusal and complete logs. Booting or opening its USB
   console must not silently start another erase. The historical ten-second
   automatic trigger was a workaround, not a requirement for the new tool.
7. Present the exact payload, wiring, replacement P4 image and rollback route
   before destructive execution. This protocol is not blanket flash authority.

## P4-to-Agon wiring

This is the recorded **Olimex P4 DevKit / Agon Light2** combination. Verify the
actual board and connector markings; do not apply these header positions to
another P4 board. Wire and disconnect only with all affected boards powered off.
The normal Extender harness may remain connected. The maintained programmer
explicitly releases GPIO9–15, 17, 20–23, 26–27 and 32–33 as inputs with no
internal pulls; no product transport is selected. Only GPIO46/47 drive ZDI.
The pinned Arduino startup has no board-variant GPIO initialization, and the
console uses internal USB Serial/JTAG rather than a harness UART. This replaces
the historical blanket isolation requirement at the Author's direction.
Preserve the normal connection inventory; reassess any different harness.

| Programmer connection | Target Agon Light2 ZDI1 |
|---|---|
| P4 GPIO46, EXT2 pin 7 | Pin 4, TCK |
| P4 GPIO47, EXT2 pin 6 | Pin 6, TDI |
| P4 GND | Pin 3, GND |

No power rails are joined. ZDI1 pin 1 (+3.3 V) is unused. ZDI1 pin 2 is reset,
not either programming signal. The Pi transistor reset wiring is a separate
fixture; it supplies neither TCK nor TDI. With the header notch facing away,
the recorded top view is:

```text
                       Notch
       [5 GND]       [3 GND]       [1 +3.3 V]
       [6 TDI]       [4 TCK]       [2 RST/EN]
```

Confirm pin 1 physically before wiring. Keep the Agon's ESP_PROG1 and UART_D
jumpers open for normal onboard VDP operation in this external-programmer
configuration. Onboard-ESP recovery has a different jumper procedure; do not
mix its instructions into this one. See [reset documentation](bench-reset.md)
for the independently accepted reset circuit.

## Controlled recovery sequence

1. Verify and deploy the prepared recovery firmware to the identified P4,
   retaining its exact original firmware for restoration. Open its documented
   console, capture all output, and confirm the selected payload identity.
2. Establish idle-high TCK/TDI and obtain three consistent product-ID reads.
   The proven target reported product `0007`, revision `AA`. Refuse writes on
   mismatch; investigate wiring or a different target rather than weakening
   the gate. Establish a fresh target-reset epoch if required by the tool;
   never combine stale halted state with a new capture.
3. If supported by the prepared tool, halt once and preserve the existing
   128 KiB flash before erasing. Record the PC and useful startup state in the
   same halt epoch. The historical tool verifies new flash but is not evidence
   of an implemented pre-erase dump feature. If unavailable, explicitly record
   the evidence loss before proceeding; do not claim a ROM backup was taken.
4. After explicit arming, follow the upstream algorithm to establish target
   state and load the flash agent and chosen MOS into RAM. Read back both RAM
   uploads and verify their lengths and CRCs before executing the flash agent.
5. Execute the agent, wait within a documented bound for its completion, then
   independently read back the complete programmed MOS payload and verify it
   against the selected bytes. Prefer a retained byte-for-byte dump and SHA-256
   as well as the upstream CRC check. Receipt of a command or agent completion
   alone is insufficient. Record the verified address range explicitly.
6. On any programming/readback failure, leave the owned target halted, preserve
   logs and report failure. No automatic erase/retry cycle. An identity refusal
   before ownership must not halt or otherwise mutate the target.
7. After a verified write, leave the eZ80 halted until the controlled reboot.
   Restore and verify original P4 firmware before resetting the Agon, preventing
   programmer retriggering. On the recorded bench both the normal harness and
   ZDI leads remained attached throughout restoration and successful boot.
   Original product firmware does not drive GPIO46/47. No rewiring is required
   merely to reset this configuration; actual lead changes still require power
   off. Leave onboard VDP unchanged.
8. Boot with the deliberately prepared safe SD startup. Confirm the MOS banner
   and a finite execution receipt; confirm no installer repeats on later boots.
   Where EMOS is restored, obtain fresh keyboard admission, prove actual input
   and SD service operation, then release held keys and return to the agreed
   foreground state. Discard pre-recovery keyboard session tokens.

## Evidence and completion

Keep a run record with initial symptoms, payload and programmer manifests,
original P4 backup/restore hashes, wiring confirmation, console transcript,
identity reads, target reset/halt epochs, RAM and flash verification results,
startup before/after, and human boot/input observations. Keep large binaries,
dumps and machine identifiers in ignored evidence storage; link summaries.

Report these outcomes separately: **flash verified**, **MOS boot confirmed**,
**P4 restored**, **keyboard restored**, and **SD service restored**. Recovery
is not complete merely because programming passed. Preserve unresolved limits
and stop at the agreed review gate before resuming performance experiments.

For attention, use the hardware spoken cue only when actual playback is
possible. Otherwise launch the known-good emulator with both startup beep and
the accepted voice cue, clearly labelled notification-only. An emulator alert
is not physical recovery evidence.

## Known historical traps

1. Using onboard ESP32 recovery replaces the VDP: a halted MOS waiting for VDP
   under that arrangement does not diagnose the original startup failure.
2. The previous startup hang was a 24-bit intermediate overflow in baud-rate
   arithmetic, yielding UART divisor 11 instead of 1. This is historical
   evidence, not an established diagnosis of the current failure.
3. P4 Arduino `Serial` did not reach the expected USB Serial/JTAG console in
   the old build. Its successful adaptation used ESP-IDF's registered console.
   GPIO output mode must precede writes; keep the inherited ZDI signal ordering.
4. Long bit-banged verification previously produced a watchdog diagnostic.
   Do not disable verification to avoid it; qualify the execution environment
   and report any watchdog interruption or incomplete readback as a failure.

## Revision record

1. **r01, 2026-09-14:** Establish enduring P4-based protocol from successful
   historical evidence. No tool refresh, wiring, flash or recovery performed.
   Author reports reset and full power cycling still yield VDP branding and a
   stationary cursor with no keyboard response. Current cause remains unknown.
2. **r01 execution, 2026-09-14:** Maintained implementation restored the full
   pre-E05 128 KiB EMOS ROM with independent host byte comparison; original P4
   restored/verified, fresh EMOS keyboard admission, CLI execution and SD
   read/write passed. All harness and recovery wiring remained connected. See
   RECOVERY-001 for human review and notification status. Failed flash was mostly
   FF, including the reset entry; the cause of the normal update failure is open.

The Author subsequently confirmed Rally works and retained the P4/ZDI leads,
Pi5 reset, sniffers and full normal harness for future recovery use. Treat this
as the standing bench arrangement until notified otherwise; do not require
repeated wiring setup. Current machine details remain in HARDWARE.local.md.
