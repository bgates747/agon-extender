# REV-01d — Reset-safe ownership capture

Keep the LA-03 wiring unchanged. This check uses only the existing purple D4
`REV_OE_N`, brown D7 `FWD_OE_N`, and qualified black ground connections.

With the Agon and P4 powered and the normal PRX fixture idle, run the legacy
reset capture and press the P4 RESET button exactly once when armed. Do not
press an Agon key or either P4 BOOT button.

PASS requires forward ownership before reset, both enables released throughout
the reset/boot interval, no active-enable overlap, at least 1 ms both-off, and
one clean return to forward ownership.
