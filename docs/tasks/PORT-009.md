# PORT-009 — Prove one UART1 message from EMOS to P4

Status: complete — exact 18-byte P4 receipt and same-run Agon Legacy return confirmed.
Started: 2026-09-07. The Author directed “make it so” after accepting one fixed
forward UART message as the next implementation chunk.

## Scope and decisions

1. An SD-loaded diagnostic caller invokes the installed EMOS v0.2.0 UART1 APIs.
   EMOS owns opening, transmitting and closing; the caller never accesses GPIO,
   UART registers or vectors. No EMOS firmware rebuild is needed. EMOS ordinary
   VDU output stays on onboard UART0 in Legacy, with EDU inactive.
2. eZ80 PC0/TXD1 sends to P4 GPIO22/RX through light2-harness-r03. Begin at
   115200 baud, 8N1, with flow control and UART1 interrupts disabled. PC1 is
   EMOS RX but unused; PC2–PC7 remain inputs. This deliberately defers return
   traffic, RTS/CTS and target-rate qualification.
3. A minimal P4 receiver uses the pinned project ESP-IDF UART driver. It makes
   all harness pads inputs with internal pulls disabled, then connects only
   GPIO22 to UART RX. No P4 harness output is configured, including TX/RTS.
   USB Serial/JTAG reports identity, READY, bytes and terminal verdict.
4. There is no compatible production P4 UART ingress adapter yet; the held
   forward-parallel composition is unsuitable. This bounded receiver follows
   staged-circuit-validation.md's diagnostic exception and proves byte receipt,
   not a product protocol, parser, activation, or Exclusive Compatible mode.
5. One fixed message, no flow-control wait, no reply wait and no automatic retry.
   The eZ80 caller reports submission, not remote receipt. Only P4's exact-byte
   comparison plus error-free quiet interval can establish receiver PASS.

## Bounded reference précis

Official docs: agon-docs commit f9806bd3cbff6ed5d1c08bef1d51fed11764b86b,
[MOS API](../../../../agon-docs/docs/mos/API.md) sections 0x15–0x18:
eight-byte UART settings, flowControl=0,
interrupts=0, open/close/put-character calls. Installed EMOS candidate
`agon-emos-v0.2.0-b2026-09-08-01-20-50Z` implements those APIs in
[uart.c](../../../agon-emos/src/uart.c),
[mos_api.asm](../../../agon-emos/src/mos_api.asm) and
[serial.asm](../../../agon-emos/src/serial.asm), retaining the production UART1 lifecycle
guard. Source inspection matters: disabled flow control skips the CTS wait;
PUTCH still polls transmitter readiness. close_UART1 resets UART state but
**does not restore PC0/PC1 GPIO mux**. Leave the Agon off before wiring changes.

The sender waits several observed MOS clock transitions after its last queued
byte before close, with a finite stalled-clock escape. This is conservative
transmit settling, not a calibrated UART-drain API. No low-level register
polling is added to the diagnostic caller.

Wiring authority: hardware/designs/light2-harness-r03/connectivity.yaml and
README.md. All eight lane mappings passed the accepted pinwalk. That does not
verify present ground continuity, power asymmetry or startup electrical states.
ESP-IDF APIs are checked against the pinned local framework's esp_driver_uart
and esp_driver_gpio headers; P4 framework/board/flash defaults are reused.

## Work

1. [x] Build the ordinary EMOS API caller and minimal P4 receiver; test exact
   matching, split input, wrong/extra/truncated bytes, and UART error handling.
2. [x] Prepare the test sheet beside r03's tests with identities, pin states,
   serial capture, exact autoexec and clear pass/fail/timeout criteria. Preserve
   the existing smoke autoexec before any SD replacement.
3. [x] Obtain identity approval and freeze the concrete artifacts before a
   decision-bearing bench run. Approved shared fixture lineage:
   `uart-forward-probe-r01`, with sender/receiver variants and one paired build.
   Compile exploration uses UNVERSIONED-DO-NOT-DEPLOY until approved.
4. [x] With the reviewed operation authorized and current wiring checked,
   deploy the receiver with both boards powered, ribbons seated and Agon idle;
   verify READY and only then let the operator press Agon's powered hard-reset button.
   Capture exact receipt and return to Legacy prompt; stop for review.

Private device identities, SSH and access boundaries remain in HARDWARE.local.md.
EMOS caller ownership is tracked in agon-emos INTEG-003. No held PORT-008 work,
production transport, circuit modification or return-channel implementation is
resumed by this task. MOS APIs are reused; no direct client transport bypass is
introduced into supported product operation.

## Implementation checkpoint — 2026-09-07

1. `scripts/prepare_uart_forward.py` builds both endpoints from one generated
   contract: 115200/8N1, no flow control, exactly 18 bytes
   (`EMOS UART1 -> P4` plus CRLF). It prepares an ordinary SD caller and boot
   script in its local output directory, without touching removable media.
2. The latest unversioned review build passed sender compilation with warnings
   treated as errors, linked UART wrapper checks, P4 compilation, and matcher
   tests under AddressSanitizer/UndefinedBehaviorSanitizer. The P4 application
   source closure contains only the receiver. Effective board configuration
   and factory-image component offsets/bytes match the selected build.
3. Inherited AgonDev b67ab244 `libmos/mos_uputc.src` returns zero for success,
   contrary to its C header comment. The caller accounts for that convention
   and the builder verifies actual linked instructions. This local remedy is
   removed/reviewed when a corrected upstream wrapper is adopted. No upstream
   checkout or installed EMOS firmware was changed.
4. The initial hybrid Arduino/ESP-IDF build ignored `build_src_filter` and
   selected unrelated VDP sources. The existing `pio/select_sources.py` hook
   with an explicit one-source allowlist resolves this build integration issue.
   No unrelated VDP code was repaired or included in the receiver image.
5. The [test sheet](../../hardware/designs/light2-harness-r03/tests/uart-forward.md)
   and `PORT-009/capture_on_pi.py` are ready for review. Six host capture tests
   reject absent/malformed PASS, wrong build/bytes/count, UART errors, later
   FAIL, and receiver restart. Capture requires five seconds of observation
   after the first matching PASS. Physical results remain pending.
6. The Author confirmed common ground, both powered boards and connected GPIO
   ribbons; the SD is mounted locally. Read-only bench inspection located the
   P4 by its stable USB identity. No serial capture, SD write, flash, reset or
   power operation was performed. The initial ribbon-isolation instruction was
   revised after the Author reported mechanical strain from disconnection and
   successful prior connected/powered flashes. The test sheet now keeps both
   boards powered and ribbons seated, with Agon idle during the USB update.
   The USB flashing pins are separate from the harness lanes and the new P4
   application has no harness outputs. Powering off only the Agon is not an
   isolation substitute; this procedure does not qualify unequal-power states.

Private build logs/manifests remain in the ignored build directory. These are
compile checks, not an identified candidate or hardware qualification result.

The Author subsequently directed “ok flash away and tell me what i need to do
next,” authorizing the proposed fixture identity/source freeze and connected,
powered P4 deployment. Registry r24 records uart-forward-probe-r01 as candidate.
The workstation will stage the ordinary sender; no EMOS flash is authorized or
needed for this step. UART hardware receipt remains pending.

## Deployment checkpoint

The candidate `uart-forward-probe-r01-b2026-09-08-02-35-54Z` was built from
clean Extender `fd25958029c09b3828f7559aef519a4428c2789d` and EMOS
`4baeb277b041783b5fa01f1c48487ac52a22b294`. All paired build checks passed.
The [deployment record](../../hardware/designs/light2-harness-r03/tests/PORT-009-2026-09-08-02-37-48Z/README.md)
records successful P4 write, independent flash verification and matching
receiver boot/WAIT at zero received bytes with the powered harness connected.
The exact sender and mode-3 autoexec were staged to SD after backup; the card
was verified, synced and unmounted. The local capture launcher restarts the
verified receiver, prompts the operator to boot Agon, records 90 seconds and
retrieves the Pi evidence. Its private location is in the local bench record.
No UART transfer PASS or final Agon observation is claimed yet.

## Operator capture correction

The Author reported that console chatter hid the reset cue and requested a
workstation Enter pause before P4 arming, a clear reset cue, and an Agon reset
button press with power retained. The reported MOS startup delay is 2–3 seconds.
Revision uart-forward-probe-r02 records this host/procedure correction and
explicitly selects the already-deployed r01 endpoint build; no firmware change
or flash is needed. Registry r25 records r02 as experimental. The original r01
test sheet remains archived beside its replacement.

The launcher now pauses before any P4 reset, hides esptool/boot chatter in logs,
and displays RESET AGON NOW only after the capture port is open and the expected
receiver reports a complete empty WAIT. The 90-second observation begins then.
Nine host tests pass, including simulated three-second Agon startup, a complete
90-second window after the cue, quiet output and rejection of incorrect WAIT.

The Author corrected misaligned headers; the unchanged firmware then passed.
Keep the harness seated to avoid repeated mechanical strain and alignment
errors. At the Author's direction, the uninformative failed capture bundles
were removed from both hosts; the passing evidence is retained.

The [corrected capture](../../hardware/designs/light2-harness-r03/tests/PORT-009-2026-09-08-02-59-01Z/README.md)
passed exact P4 receipt: 18 expected bytes, matching build, no UART errors or
later FAIL, and 79 seconds of observation after PASS. Raw log hash and verdict
were independently checked. The Author confirmed the same-run Agon SENT/final
Legacy prompt, completing the test.

## Closeout — 2026-09-07

The Author confirmed that the passing run reset and returned to the Legacy
prompt, with the screen appearing identical to the earlier sender/SENT
photograph and without stock MOS/VDP branding. Combined with independently
verified exact receipt in PORT-009-2026-09-08-02-59-01Z, this completes the
bounded test. The earlier pending-confirmation checkpoints above are historical.
Removed this completed item from the authoritative TODO. No return-channel
work, broader qualification, firmware reflash, commit or push follows from
this confirmation.
