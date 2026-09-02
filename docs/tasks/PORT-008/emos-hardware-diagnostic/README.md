# PORT-008 EMOS hardware-failure diagnostic

> **Retired historical record — do not execute.** This diagnostic and its
> one-shot recovery variant completed their bounded predecessor roles. Their
> PlatformIO source selections and payload generator now fail closed. The
> source, hashes, and observations below remain only to interpret preserved
> run evidence; they are not current build, deployment, wiring, or recovery
> instructions.

## Historical purpose and boundary

The first physical `agon-emos-v0.1.0` candidate displayed the stock VDP banner
but did not reach the MOS banner or prompt. Running a modified `agon-recovery`
image on the target Agon's onboard ESP32 could inspect ZDI, but necessarily
replaced the stock VDP and changed the startup configuration under diagnosis.
Its capture at `PC=0x0009EA` inside `_wait_timer0` therefore described EMOS
normally waiting for a General Poll response from the absent stock VDP; it is
not evidence of the original failure.

The controlled follow-up uses the otherwise electrically isolated P4 as an
external ZDI observer. The target Agon must run the exact failed EMOS candidate
and restored stock VDP. The P4 diagnostic performs three passive identity
reads, waits ten seconds, verifies that the eZ80 is still running, then halts it
once and captures its architectural, memory, Timer 0, Port D, and UART0 state.
The delayed one-shot trigger is a bench workaround for USB Serial/JTAG input
not reaching the diagnostic; it remains fail-closed on identity and target
state. The diagnostic never flashes or resets the target, writes target RAM,
resumes the eZ80, or implements a product transport.

## Diagnostic identities and provenance

1. EMOS source/candidate authority: `agon-emos` commit `59c3102`, identity
   `agon-emos-v0.1.0`.
2. ZDI protocol source: `envenomator/agon-recovery` commit
   `95d68464afd049945e1dfd780c1c07621d565450`.
3. P4 build environment: `p4-zdi-probe` in `vdp/platformio.ini`.
4. P4 source: `vdp/video/extender/diagnostic/p4_zdi_probe.cpp`.
5. This diagnostic is temporary qualification infrastructure, not Extender VDP
   firmware and not evidence for any product transport or hardware claim.

## Temporary electrical model

Perform all wiring with both boards powered off and the normal Extender harness
disconnected from the target Agon.

1. P4 `GPIO46` on EXT2 pin 7 to target Agon ZDI `TCK`.
2. P4 `GPIO47` on EXT2 pin 6 to target Agon ZDI `TDI`.
3. P4 `GND` to target Agon ZDI `GND`.
4. No P4 power rail connects to the target Agon.
5. The target Agon's `ESP_PROG1` and `UART_D` jumpers remain open for normal
   stock-VDP operation.

GPIO46 and GPIO47 are exposed by the Olimex P4 DevKit but absent from both
accepted Extender harness connectivity models. The assignment is diagnostic
only and creates no production pin reservation.

## Staged procedure and stop gates

1. Restore the target onboard ESP32 to stock VDP with `agon-recovery` option 3;
   preserve EMOS in eZ80 flash.
2. Power off both boards and install only the three diagnostic connections
   above.
3. Build and flash the exact reviewed `p4-zdi-probe` artifact to the P4 under a
   separately authorized P4 deployment step.
4. Power and verify the P4 reports ZDI product `0007`; if not, stop and correct
   unpowered wiring.
5. Cold-boot the target Agon with stock VDP and failed EMOS. Wait for the same
   externally visible failure state.
6. Preserve the complete transcript emitted by the identity-gated, delayed
   one-shot capture before changing either board.
7. The target eZ80 remains halted. Power it off or reset it before any other
   use.

No stock-VDP restoration, wiring, P4 flash, target boot, ZDI halt, or capture is
authorized merely by this document.

## Prepared P4 artifact

The initial 2026-08-31 deployment exposed two P4-port defects before any ZDI
capture occurred: Arduino `Serial` was not the DevKit USB Serial/JTAG console,
and P4 rejected a `digitalWrite()` performed before the pin was assigned to
GPIO output. The corrected diagnostic uses ESP-IDF's already-registered
USB Serial/JTAG stdin/stdout VFS, moves GPIO initialization into `setup()`, and
sets output mode before every first write. This is a local-port correction,
not a change to the inherited ZDI protocol.

The corrected clean build selected only
`video/extender/diagnostic/p4_zdi_probe.cpp` as the application translation
unit. The ignored build outputs are:

1. `firmware.bin`: 320,032 bytes; SHA-256
   `04ebd67cb2801e52ff6721df958e81a0f3e245ed30147dbeb006dc42e2a84b2a`.
2. `firmware.factory.bin`: 451,104 bytes; SHA-256
   `11f1cb95cf27189536c03c828e7599e5ec6b2cae8f643dde93f6175b508ff69e`.
3. `bootloader.bin`: SHA-256
   `117e8908d37e147dfa177759055f9ce7c2538088f3a3a9d02c480ca9f4795838`.
4. `partitions.bin`: SHA-256
   `e29396a4f5ecc129c0e275d2df19d69adb5ee33389e3d5659e9a50932ac6864a`.

The binary contains its diagnostic-only warning, GPIO46/GPIO47/common-ground
wiring declaration, explicit `c` capture gate, and halted-target terminal
state. These host checks do not authorize deployment or prove P4 GPIO behavior.

## Runtime observations

1. The first deployed image booted but emitted only ESP-IDF startup messages.
   Arduino `Serial` did not address the P4 DevKit USB Serial/JTAG console, and
   P4 rejected the image's write-before-output GPIO initialization. No ZDI halt
   or capture command was issued.
2. The first corrected console/GPIO image reported product `3C3C`, which did
   not satisfy the `0007` stop gate. No ZDI halt or capture command was issued.
3. A second correction replaced repeated Arduino GPIO reconfiguration with
   ESP-IDF GPIO operations ordered like the proven `agon-recovery` source and
   added passive startup diagnostics. It found TDI low before the first ZDI
   command and returned product probes `043C`, `3C3C`, and `3C3C`.
4. Those values cannot qualify the connection. The target eZ80 has not been
   reset since the onboard recovery utility halted it, so its inherited ZDI
   state is a live confounder. The next gate is a target reset with the P4
   holding TCK and TDI idle high, followed by another passive identity read.
5. After that reset reproduced the VDP-banner/no-MOS-banner failure, TDI idled
   high and all three product probes returned `0007`, revision `AA`. The
   electrical and identity gate therefore passed.
6. Two host writes of the lowercase `c` command produced no acknowledgement;
   no evidence showed that the command reached the P4 USB Serial/JTAG stdin
   path. The exact bench build therefore enables a temporary one-shot
   auto-capture workaround. It refuses unless all three identity probes are
   `0007` and the initial ZDI status says the target was not already halted,
   announces a ten-second delay, checks that status again, then performs the
   same bounded capture. This is not a product interface or retained protocol.
7. Run `PORT-008-2026-08-31-21-55-19Z` preserved the original stock-VDP
   failure and passed the bounded capture objective. Three product probes were
   `0007`, revision was `AA`, and the target was running before the one-shot
   halt. The raw 2,995-byte transcript remains on the bench at SHA-256
   `94d1ea7f4a1353651ce079a87c0e0c63613eff5091835f23edc3596ce2348ec1`;
   its tracked interpretation is in the run record.
8. The stopped PC `0x0009EA`, surrounding bytes, and stack correlate exactly
   with the candidate's inherited `_wait_timer0`, its `_wait_ESP32` caller,
   and MOS startup. Timer 0 control/data were `0x84`/`0x0000`, so the sample is
   not a timer deadlock: EMOS was completing one timeout inside its repeated
   wait for `gp`, which remained zero.
9. UART0 was enabled with hardware flow control and 8N1 framing. Captured
   `LSR=0x60` showed an empty transmitter and no received byte; `MSR=0x10`
   showed the CTS condition accepted by the stock send path. This narrows the
   failure to request transmission/physical delivery, stock-VDP handling or
   response, or receive configuration/delivery. It does not select among them.
10. A separately flashed supplement correctly refused to alter UART state
    after P4 rebooting had changed the halted ZDI context from PC `0x0009EA` to
    `0x000107`. Divisor inspection must therefore occur inside the same halt
    epoch as the primary capture. The current coherent one-shot build does so,
    restoring UART LCR and AF/MB before continuing the snapshot.

## Coherent follow-up capture

The exploratory follow-up remained a dirty-source diagnostic and cannot
qualify a product artifact:

1. `firmware.bin`: 323,456 bytes; SHA-256
   `a821a52bd527b46c37405d4db7e70cdac1c7d96a2925359b100f49f4236272b6`.
2. `firmware.factory.bin`: 454,528 bytes; SHA-256
   `cb4b5128e3c89c95f69eba3cea88c480a54a1f3ee4722314ff533e039386d846`.
3. `bootloader.bin`: 24,448 bytes; SHA-256
   `0ac6eb5518f6a06fc0fad9d7aa5f7723314b3b988b912bfeb4deb2d6e2276db4`.
4. `partitions.bin`: 3,072 bytes; SHA-256
   `e29396a4f5ecc129c0e275d2df19d69adb5ee33389e3d5659e9a50932ac6864a`.

The exact factory image was staged, flashed at offset zero, and independently
verified on the identified P4. It first observed the already-halted target and
refused the stale supplemental read. After a manual target reset and P4 reset,
run `PORT-008-2026-08-31-22-27-18Z` reproduced `PC=0x0009EA`, `gp=0`, and no
UART0 receive byte. In the same halt epoch it read `LCR=0x03` and UART0 divisor
`0x000B`, restoring LCR and AF/MB before continuing.

At 18.432 MHz, the official 1,152,000-baud link requires divisor 1; divisor 11
is approximately 104,727 baud. The value is an exact oracle for an inherited
source portability defect exposed by AgonDev: native 24-bit evaluation wrapped
`16 * 1,152,000` from `0x01194000` to `0x00194000` before assignment to
`UINT32`, and `18,432,000 / 1,654,784` truncates to 11. This identifies the
immediate physical boot blocker. The target was manually reset after the
capture; corrected EMOS emulator acceptance and physical requalification are
separate gates.

## Prepared one-shot ZDI recovery

The failed EMOS cannot execute `/autoexec.txt`, so the correctly staged SD-card
payload cannot repair the current eZ80 flash. A temporary P4 recovery image was
therefore prepared from the exact upstream `agon-recovery` algorithm. It is a
bench recovery mechanism only, not an Extender transport or update facility.

1. The corrected EMOS payload is 114,069 bytes, SHA-256
   `bf7633f9853e812d806a6528450d268db68541b12df0dcb47b4f68b15a130478`,
   and CRC32 `f202107f`.
2. The embedded 90-byte flash agent is byte-identical to
   `agon-recovery` commit `95d68464afd049945e1dfd780c1c07621d565450`,
   SHA-256
   `ca44786969dc2dd1b0fa51e6b80f530b7241317dc27bf8efac3ca7d56bddee06`.
3. `generate-recovery-payload.py` fails closed on both SHA-256 values and
   reproduced the generated header byte-for-byte in a second temporary output.
4. The P4 source selection contains only
   `video/extender/diagnostic/p4_zdi_mos_recovery.cpp`. The image requires three
   `0007`/`AA` ZDI identity reads and gives a ten-second power-off abort window
   before it halts or writes the eZ80.
5. The pre-deployment audit found and corrected a local safety defect: the
   first common failure routine halted the target even after an identity-gate
   refusal. Pre-ownership failures now remain passive; failures after recovery
   begins halt the eZ80 and leave it halted.
6. The final factory image is 569,632 bytes, SHA-256
   `741135661f1f3ce46ddf0f7593c6144195f9e56b7d1e44d8ef69bbc8e0d0d7e6`.
   Its bootloader, partition, OTA-data, and application regions compare
   byte-for-byte with the independently generated build segments. Both ESP32-P4
   image checksums and validation hashes pass.
7. Read-only bench preflight resolved the expected P4 stable identity to
   `/dev/ttyACM0` and confirmed the expected USB serial identity. The exact
   factory image is staged on the Pi under its hash-qualified name and its
   remote SHA-256 matches. The superseded pre-audit staging image was removed.
8. Authorized run `PORT-008-2026-08-31-23-11-18Z` flashed the identified P4,
   passed all three eZ80 identity probes, verified both RAM uploads, received
   the upstream agent's completion acknowledgement, and read back the complete
   programmed image at CRC32 `f202107f`. The eZ80 remained halted until the
   Author physically reset the Agon. A P4 task-watchdog diagnostic appeared
   during the long bit-banged RAM readback but did not reset either core or
   interrupt recovery; preserve it as a temporary-tooling gotcha.
9. The physical cold boot displayed VDP v2.14.1 Dressing Gown and MOS 3.0.2
   Arthur. The keyboardless smoke fixture discovered all three providers,
   reported the expected unversioned corrective identity, completed both
   service calls, transitioned Legacy to fake Dual and back to Legacy at mode
   generation 2, and returned to the prompt without a diagnostic or reset.
10. The onboard ESP32 was then directly flashed over USB from the clean
    official VDP v2.16.0 tag at commit
    `c7ac293d2aa81ddfa693390549bcd909069c8fc3`. Esptool verified bootloader,
    partitions, OTA data, and the 1,077,552-byte application image before its
    automatic hard reset. The rebuilt application SHA-256 was
    `9103c100746dc050cb4837747940fb2986c58913b03a80d891da684160b77368`.
11. After an Agon reset, the screen identified VDP v2.16.0 Bistromathics and
    MOS 3.0.2 Arthur. The same fixture again discovered all three providers,
    completed both calls, entered fake Dual, returned to Legacy generation 2,
    and returned to the prompt. This proves the dirty corrective EMOS build on
    the physical UART path against the task's official VDP baseline; it is not
    a qualified or deployable EMOS identity.
