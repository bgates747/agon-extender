# Paired graphics — paired-graphics-probe-r01

Candidate hardware procedure owned by [QUAL-003](../../../../docs/tasks/QUAL-003.md).
The Author accepted the paired emulator images and authorized deployment on
2026-09-09. Hardware observations remain pending.

## Candidate and installation

1. Freeze and build EMOS v0.1.12, P4 uart-excom-console-r04 and this fixture
   from clean committed inputs. Record exact build identities and hashes.
   Preserve the working EMOS v0.1.11 image and P4 r03 rollback bundle.
2. Retain the existing seated r03 UART harness, common ground and native P4
   USB keyboard. No parallel transport, browser keyboard or rewiring is needed.
   Apply the machine-local bench identity and active bench constraints.
3. Flash and readback-verify P4 using the established deployment procedure;
   observe its candidate identity, USB host readiness and absence of startup
   faults. Opening P4 serial can reset it: start any recording before Agon
   test startup, and do not reopen serial during the comparison.
4. Stage the guarded MOS-only installer on the Agon SD. Preserve the old
   payload before using the established one-shot commands:

   ```text
   RENAME /EMNEW.BIN /EMDONE.BIN
   FLASH mos EMDONE.BIN -f
   ```

   The Author inserts the card, resets Agon and reports the flash result.
   Return the card to the workstation afterward so the agent can remove the
   installation startup and select the repeatable test startup. Do not mix
   the installer and graphics test in one boot.
5. Install only the candidate `shapes.bin`, `bitmaps.bin`, generated
   `assets/bitmaps/` under `/extender`, matching `/bin/EMBOOT.BIN` and its
   `/emos-boot/check.txt`. Keep source and emulator files off the bench SD.

## Repeatable startup

```text
VDU 22 3
LOAD /bin/EMBOOT.BIN
RUN
SET KEYBOARD 1
EMOS KEYINPUT extender
VDU 22 20
EMOS EXCOM
VDU 22 20
CD /extender
LOAD shapes.bin
RUN
```

Autoexec configures mode 20 on mainboard VDP before ExCom, then on EDP.
Applications never change video modes. Both displays retain independent state;
the applications request switching through public `mos_oscli`, using
`EMOS LEGACY --keep-display` and `EMOS EXCOM --keep-display`.

## Operator comparison

1. Connect the browser video page and reset Agon with the prepared test card.
   Confirm SD/CLOCK PASS and native Extender keyboard selection. The browser
   must use the video-only page; the physical USB keyboard controls Agon.
2. Shapes starts with page SHP-01. Mainboard renders first, EDP second. Wait
   until both completed images are visible, allowing for browser frame delay.
   Compare geometry, colours, text and each renderer's pixel sample counts.
   Press Space to advance one pair. Both images must remain visible at every
   pause; a switch must not replace the mainboard image with a mode banner.
3. Continue through the 24 pages, or press Escape to end early. Record which
   pages were observed; a short spot check does not qualify the entire suite.
   After normal completion or Escape, the browser must show an ExCom MOS
   prompt and native USB input must still work.
4. At that prompt enter `LOAD bitmaps.bin`, then `RUN`. Compare its 32 pages
   and 123 keypress stages the same way. Sprite definitions and intermediate
   changes must survive switching. Page 22 intentionally defers a sprite move;
   page 26 exercises hardware sprites; page 29 retains transformed frames.
   Use `RUN . N` after loading to revisit one page. Escape returns to MOS.
5. Repeat a representative page and confirm ordinary CLI input after exit.
   If a switch fails, video freezes, P4 restarts or USB input is lost, stop and
   record the page/stage, both screens and any retained serial diagnostic.

## Results and interpretation

Record the exact EMOS/P4/fixture pair, wiring reference, pages/stages observed,
return to MOS and whether a repeat succeeded. Store passing observations and
informative failures alongside this sheet. No analyzer capture or latency
benchmark is required for this visual comparison.

The stock/native Shapes reference has seven known pixel disagreements
(237/244); preserve them separately from new differences between the displays.
The native Bitmaps reference returns 95/95 samples and passes 41 presentation
comparisons. Hardware sprites require visual presentation checks because
framebuffer queries do not include them. A zero program return or matching
probe count is not a complete graphics-fidelity pass. This procedure does not
qualify audio, RTC, parallel transfer, browser input or arbitrary application
migration between displays.
