# Light 2 r03 tests

Current preparation: [paired mainboard/EDP graphics](paired-graphics-probe-r01.md).
Native USB keyboard input and [ordinary ExCom console](uart-excom-console-r03.md)
are accepted functional baselines. The earlier
[browser timing result](REMOTE-001-2026-09-09-18-00-44Z/README.md) remains historical;
browser keyboard input is deferred, while browser video remains the display.

Accepted controlled-input baseline: [controlled P4 keyboard sender](keyboard-sender.md)
[PASS](PORT-005-2026-09-09-03-26-09Z/README.md). The full capture verifies twelve
stock keyboard packets at 1152000 baud; the Author confirmed Agon SD/CLOCK,
keyboard API effects and MOS return on the captured run and two Agon-only
resets. Browser/session qualification remains incomplete. The
[keyboard-test SD](PORT-005-2026-09-09-03-19-20Z/README.md) and
[P4 deployment](PORT-005-2026-09-09-03-22-37Z/README.md) records identify the inputs.

Previous completed test: [SD-loaded clear/banner/count sample](visible-text-sd-sample.md),
following the [repeatable single-banner fixture](visible-text-repeatable.md).
Both the first [r01 text result](PORT-014-2026-09-08-19-36-36Z/README.md) and
[r02 text result](PORT-014-2026-09-08-19-52-44Z/README.md) retain their individual
observations and limitations. The [r03 counting result](PORT-014-2026-09-08-21-22-24Z/README.md)
passes exact UART bytes, full acquisition, browser rendering and Author-confirmed
Agon smoke/prompt plus two additional reset runs.

Earlier completed test: [UART RTS/CTS pause and timeout](uart-flow.md).
[P4 deployment](PORT-011-2026-09-08-05-54-22Z/README.md) passed;
[EMOS installation](PORT-011-2026-09-08-05-55-02Z/README.md) is Author-confirmed.
The [smoke/flow test SD](PORT-011-2026-09-08-06-05-59Z/README.md) is ready and
unmounted before the run. The
[physical flow result](PORT-011-2026-09-08-16-16-36Z/README.md) passes both
endpoint reports and all retained-waveform checks. The analyzer saved 27.57632
of the requested 60 seconds, including the complete exchange and 11.526723
seconds after the final stop. The Author accepted this bounded test as PASS
with that acquisition limitation explicit; the original acquisition FAIL
remains recorded.

Previous completed test: [UART request and acknowledgement](uart-roundtrip.md).
The [acknowledged round trip](PORT-010-2026-09-08-04-39-39Z/README.md) passed exact P4
request/ACK capture and Author-confirmed Agon success with prompt return.
The [EMOS installation and timeout record](PORT-010-2026-09-08-04-07-39Z/README.md)
confirms successful installation, physical SD/clock smoke and the intentional
no-reply case. The [P4 acknowledgement candidate deployment](PORT-010-2026-09-08-04-35-25Z/README.md)
passed flash verification and startup before the successful capture.

The [first UART1 forward message](uart-forward.md) is the accepted predecessor.
The [P4 deployment checkpoint](PORT-009-2026-09-08-02-37-48Z/README.md) passed
flash verification and receiver startup. The
[corrected UART capture](PORT-009-2026-09-08-02-59-01Z/README.md) passed exact receiver receipt and
the Author confirmed the same-run Agon SENT/final Legacy prompt.

## Initial Port C pinwalk (historical)

[HW-002](../../../../docs/tasks/HW-002.md) owns this diagnostic and its
[keyboard-free fixture](../../../../docs/tasks/HW-002/pinwalk/README.md).

For the accepted pinwalk, the SD card's `autoexec.txt` contained:

```text
LOAD /bin/PWBOOT.BIN
RUN
```

The previous script is preserved as `autoexec.pre-pinwalk-69d5b80f4651.txt`.
The original `/bin/pinwalk.bin` is unchanged. The separate boot build is
`header-pinwalk-boot-r01-b2026-09-07-23-01-31Z`; `/bin/PWBOOT.yaml` records its
identity and hash. No higher-priority `!boot.obey` or `autoexec.obey` was present.

## Operator sequence

1. Establish that the P4 is powered, its PC0–PC7 endpoints are inputs, and analyzer ground
   joins common circuit ground. Record where probes attach relative to the
   220 Ω resistors; Agon-side observation alone cannot prove the P4 connection.
2. Match lead colors: PC0 yellow/D1, PC1 gray/D6, PC2 orange/D3,
   PC3 purple/D4, PC4 red/D5, PC5 blue/D2, PC6 brown/D7, PC7 green/D0.
   Ignore the old probe circles. Leave isolated handshake landings alone.
3. Safely eject the SD from the workstation and insert it into the Agon.
   From the Extender repository on the workstation, run:

   ```text
   .venv/bin/python docs/tasks/HW-002/pinwalk/capture.py
   ```

4. When prompted, reset the Agon once within 20 seconds. Autoexec launches
   the fixture, which waits about five seconds, emits one walk and returns
   to MOS. Do not reset again during the 60-second capture.
5. Observe the build banner, `PINWALK BEGIN`, `PINWALK END` and return to MOS.
   The script prints eight results and the local evidence directory. Retain
   the raw trace and any failures. A repeat needs a new script invocation
   and one further operator reset.

The script does not reset processors or configure P4 firmware/GPIO.

## Results

The [first capture](HW-002-2026-09-07-23-11-02Z.md) contains the expected
1–8 pulse counts on all eight lines. Acquisition stopped at 35.81952 seconds
instead of 60 seconds. The Author accepted the pinwalk as a PASS because the
full pulse sequence is present with a quiet tail; the acquisition discrepancy
and original partial verdict remain recorded. Exact displayed versions, build banner, P4
input state and probe positions remain unrecorded. Private bench identifiers
stay in the ignored local record.
