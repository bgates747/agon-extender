# Light 2 r03 tests

Latest completed test: [UART request and acknowledgement](uart-roundtrip.md).
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
