# UART round-trip test PASS

EMOS sent the exact 18-byte request on PC0 → P4 GPIO22. P4 logged exact
receipt and one five-byte `ACK\r\n` reply on GPIO12 → Agon PC1. The Author
confirmed Agon round-trip success and return to its normal Legacy prompt
for this same capture.

The saved [raw P4 serial output](serial.txt) passes the committed checker;
its hash matches the original capture record. The host captured for 90 seconds
after the readiness cue, including approximately 78 seconds after first
success, with no UART error or extra request bytes. The Agon observations are
Author reports, not a newly archived screen image.

[Run metadata](run.yaml) records both frozen candidate identities, hashes,
observations and evidence limits. The [P4 deployment](../PORT-010-2026-09-08-04-35-25Z/README.md)
and [EMOS installation/no-reply case](../PORT-010-2026-09-08-04-07-39Z/README.md)
provide their preceding checks.

This completes the bounded request/acknowledgement test at 115200 baud, 8N1,
without flow control. EMOS owns UART1 and ordinary output remains on the onboard
VDP. RTS/CTS, production EDP traffic, mode activation and other electrical
conditions remain outside this result.
