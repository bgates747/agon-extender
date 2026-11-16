# NET-009 — Pi header UART to Pi TCP control

Smith reports the modem wired and instructs Extender to run the planned tests.
The Pi5 owner enabled the live RP1 header UART, TX/RX only, on GPIO14/15.
The GPIO17 reset connection, debug UART and boot configuration remain intact.

1. Extender owns the sole verified RP1 header tty for each finite arm. No
   Olimex target action, reset, firmware flash or startup modification. Use
   the existing modem AT firmware and private runtime JOIN only if needed.
   Start after the physical move at expected default115200 8N1, no flow
   control. If no positive AT, retain the first attempt and distinguish the
   retained previous CUR baud only if applicable; no blind scan or replay.
2. On positive AT and Wi-Fi IP, use the existing NET-008 peer, deterministic
   1024-byte payload pattern and CRC/sequence checks. Test each direction alone
   for 3s at115200/230400/384000/576000/1152000. A rate change requires a
   positive command reply at the new rate. Stop escalating a direction at its
   first failure; continue a distinct direction only after a confirmed clean
   command-mode return. A passing arm requires matched byte/frame counts, CRC,
   pattern, EOS, peer completion and command-mode cleanup. Hold no port between
   arms. Allow at most 140s per arm, with private JOIN only if disconnected.
3. If a higher rate fails, deliberately back down to the last passing rate and
   qualify10/30/60s if useful, with a 190s ceiling for the longest arm. Preserve
   failure and partial bytes. Guarded escape/close returns the modem to command
   mode without persisting settings. Record the final known CUR baud.
4. Current analyzer probes were documented on the old P4/modem wiring. Do not
   acquire them as Pi UART evidence without a verified new mapping. Without
   wire evidence these runs compare endpoint results only. Pi's undervoltage
   telemetry can flag board-level symptoms; it cannot verify modem-pin voltage
   under bursts or certify spare 3.3 V capacity. Report those limits.
5. The later Pi-to-P4 Ethernet comparison requires an identified P4 TCP peer
   candidate and fresh scheduler custody. Do not use P4 production services as
   a substitute for independently verified payload/CRC checks.
