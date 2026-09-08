# P4 acknowledgement candidate deployed

P4 flash programming, independent verification and startup **passed** for
`uart-roundtrip-probe-r01-b2026-09-08-04-28-58Z`, built from clean commit
`748f959`. The [deployment record](deployment.yaml) retains the endpoint
identities, artifact hashes and checks. The [raw boot output](boot.txt) shows
candidate status, GPIO22 RX, GPIO12 TX, 115200/8N1 without flow control, and
repeated empty WAIT. Full private deployment logs remain in the bench records.

This run is **partial** for the overall UART procedure: no Agon request or
P4 acknowledgement has been exercised during deployment. The separate
[round-trip test](../uart-roundtrip.md) must establish those results.

Both boards stayed powered and the harness stayed seated. The installed EMOS
and its combined SD/clock/UARTTEST autoexec remain ready. The workstation
launcher waits for Enter before arming P4, then cues the operator to press and
release the powered Agon reset button. Capture lasts 90 seconds after the cue.
Success requires both the P4 request/ACK record and Agon's UART ROUND TRIP PASS
followed by its prompt.
