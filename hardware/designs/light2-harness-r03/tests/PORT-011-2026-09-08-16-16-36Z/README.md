# UART flow test PASS; shortened capture accepted

The Author explicitly accepted this bounded UART flow test as PASS on
2026-09-08, with the acquisition limitation below recorded.

Both endpoints report success. The Author confirmed Agon SD/CLOCK PASS,
UART FLOW PASS and return to the normal MOS prompt. The P4's
[original serial output](serial.txt) independently passes the frozen checker,
including its exact request/ACK, queued-but-blocked byte cancellation and
70.125 seconds of observation after first success without later RX errors.

The [original analyzer capture](logic.sr) contains the complete exchange.
Independent 115200/8N1 decoding gives exactly `FLOW\r\n` on EMOS PC0 → P4
GPIO22 and `FLOWACK\r\n` on P4 GPIO12 → Agon PC1. No extra bytes or framing
warnings appear. The saved [decoder output](uart-decoder.txt),
[edge inventory](edges.json) and [measurements](measurements.json) support:

| Check | Measured result |
| --- | --- |
| P4 holds EMOS transmission stopped, PC3 HIGH | 1.0012325 s; PC0 remains idle until release |
| EMOS holds P4 transmission stopped, PC2 HIGH | 0.985767 s; PC1 remains idle until release |
| EMOS's blocked A5 attempt | No further PC0 edges after P4 stops transmission |
| P4's blocked 21 attempt and cancellation | No further PC1 edges after EMOS's final stop |
| Quiet trace after final stop | 11.526723 s, exceeding the five-second waveform requirement |

P4's queue/timeout logs and the Author-confirmed EMOS PASS establish the
attempted transfers; quiet wires alone do not. Sample times use the archive's
2 MHz rate, with 0.5 microsecond sample spacing and no separate calibration.

**The acquisition check still FAILS:** sigrok saved 55,152,640 samples
(27.57632 seconds), rather than the requested 120,000,000 (60 seconds).
It exited zero after repeated empty USB transfer timeouts; see the
[original end-of-capture excerpt](acquisition-end.txt). The earlier shortened
preflights, sniffer power cycle and Pi restart do not establish the cause.
There is no waveform evidence after the retained trace ends.

The [run record](run.yaml) records outcome **pass** following the Author's
instruction, "approve this as a passed test." Its dated disposition preserves
the earlier partial outcome and accepts the shortened capture because the
complete exchange and required quiet tail are present. Original measurements
and the acquisition FAIL are unchanged. This completes PORT-011 and EMOS
INTEG-005; artifact lifecycle states are unchanged. Exact probe positions
relative to the series resistors remain unrecorded; the Author checked the
probe wiring.

No new firmware, SD content or hardware state changed during this evidence
review. This result covers the short fixed exchange and deliberate flow stops;
it does not establish sustained load, faster baud rates, production EDP
traffic, mode activation or other electrical conditions.
