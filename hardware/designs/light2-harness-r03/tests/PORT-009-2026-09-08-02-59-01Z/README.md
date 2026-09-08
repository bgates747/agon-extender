# UART forward test PASS

P4 received the exact 18-byte message `EMOS UART1 -> P4` plus CRLF from the
selected r01 endpoint build during the r02 reset-button procedure. The raw log
contains matching PASS reports and no UART errors or later FAIL. Observation
continued for 79 seconds after the first PASS. Its saved hash and the receiver
verdict were independently rechecked.

The Author confirmed that this same Agon run reset and returned to Legacy,
with the display appearing identical to the earlier screenshot showing the
correct sender, SENT 18 bytes and final Legacy/inactive-EDU prompt. Stock
MOS/VDP branding was not visible. This is an operator report for the passing
run; the earlier photograph is supporting context, not a newly captured image.
The run metadata records the dated amendment from partial to pass.

The Author obtained this PASS after correcting misaligned headers. No firmware
change was needed between failed and successful captures. This completes the
bounded forward UART test at 115200/8N1 without flow control. Return traffic,
RTS/CTS and Exclusive Compatible mode remain outside the result.

See [run metadata](run.yaml), [raw receiver log](serial.log),
[test sheet](../uart-forward.md), and
[paired build manifest](../PORT-009-2026-09-08-02-37-48Z/build-manifest.yaml).
