# UART request and acknowledgement — candidate test sheet

Approved procedure identity: **uart-roundtrip-probe-r01**; lifecycle: candidate. Owning task: [PORT-010](../../../../docs/tasks/PORT-010.md).
Reviewed source is frozen for candidate builds; draft review images remain non-deployable.

## What this proves

EMOS sends `EMOS UART1 -> P4\r\n` (18 bytes) on PC0 → P4 GPIO22.
P4 verifies the complete request, observes 200 ms without extra request bytes,
then sends `ACK\r\n` (5 bytes) on GPIO12 → PC1. EMOS verifies the reply,
observes about 200 ms without extra reply bytes, closes UART1 and reports its
result. Both endpoints use 115200 baud, 8N1 and no flow control. UART1 is owned
by EMOS throughout; ordinary output remains on the onboard VDP in Legacy.

This tests two UART data directions. It does not qualify flow control,
Exclusive Compatible activation, production EDP packets, keyboard input,
parallel transport or any other r03 lanes.

## Preparation

1. Leave the proven r03 harness seated, including common ground. Both boards
   stay powered. Only P4 GPIO12 is added as an output by the reply composition;
   Agon PC1 is UART1 RX. PD4/PD5/PD7 remain isolated.
2. Review and accept the new EMOS image in the emulator, including the
   ordinary boot smoke and the diagnostic's no-peer return. Freeze candidate
   inputs and rebuild before physical deployment. The v0.2.0 rollback image
   does **not** implement `EMOS UARTTEST`; v0.3.0 is required.
3. Stage and install the reviewed EMOS through the established minimal-boot
   procedure, retaining its working rollback image. No flash invocation is
   hidden in this UART test's autoexec. Record the installed EMOS build and
   binary hash independently of the P4 build.
4. After installation, the minimal SD-root `autoexec.txt` is (CRLF):

   ```text
   VDU 22 3
   EMOS UARTTEST
   ```

   EMOS prints identity before the diagnostic and the outcome last. There is
   no transport application and no repeated STATUS block. The accepted combined
   smoke script inserts `LOAD /bin/EMBOOT.BIN` and `RUN` before UARTTEST, using
   the same-build ordinary SD/clock smoke and its check file. The
   [installed combined script](PORT-010-2026-09-08-04-07-39Z/test-autoexec.txt)
   can remain for the ACK test. Mode selection belongs only in autoexec.
   Safely unmount before returning SD to the Agon.

## First: prove the timeout

1. Keep the currently installed, proven forward-only P4 receiver. It cannot
   send an acknowledgement. No wire removal or replacement P4 build is needed.
2. Press/release the powered Agon's reset button. Allow its usual 2–3 seconds
   to boot, then approximately five seconds for the missing-reply timeout.
3. Expected Agon result: **UART ROUND TRIP FAIL: no reply from P4**, followed
   by the normal MOS prompt. The MOS command may additionally print its
   standard timeout error. For this deliberate negative test, the timeout and
   prompt return are the expected passing observation. A hang, wrong failure
   reason or unexpected PASS fails the test.
4. Record the installed EMOS and receive-only P4 identities, elapsed-time
   observation and Agon screen. The separate stopped-clock escape is a finite
   poll budget, not a calibrated duration; host tests cover it.

## Then: prove the acknowledgement

1. With the Agon idle at its prompt, deploy the separately approved P4 reply
   candidate and verify its flash/boot identity using the established bench
   procedure. Keep both boards powered and ribbons seated.
2. Start the prepared workstation launcher. It must wait for **Enter** before
   restarting/arming P4, save low-level output in its evidence folder and show
   **RESET AGON NOW** only after opening the verified serial port and observing
   a matching, empty receiver WAIT. No Agon reset before that cue.
3. Press/release Agon's reset button at the cue. The host records for 90 seconds
   after the cue, including Agon boot delay. P4 receives the exact request and
   logs exactly one `UART RETURN SENT count=5 hex=41434B0D0A build=<P4 build>`.
4. Expected Agon result: **UART ROUND TRIP PASS**, then the normal prompt.
   Capture the result and confirm prompt return. P4's USB log alone proves
   only request receipt and ACK transmission, not receipt by EMOS.
5. The host rejects missing/malformed/duplicate ACK records, wrong identities,
   wrong request/reply bytes, UART errors, P4 restart, later extra request
   bytes, or fewer than five seconds of observation after P4 success.

## Results

The [physical smoke and no-reply case](PORT-010-2026-09-08-04-07-39Z/timeout-result.yaml)
passed on the installed v0.3.0 candidate, including prompt return. Elapsed
time was not measured. The [acknowledged round trip](PORT-010-2026-09-08-04-39-39Z/README.md)
also passed: exact request, single ACK and clean observation after success,
with Author-confirmed Agon success and prompt return. These complete the
bounded test. The two candidate build identities and hashes remain recorded
in the run metadata; this result does not imply broader lifecycle or circuit
qualification. Keep future runs separate and retain passing or informative
evidence under the Author's retention policy.
