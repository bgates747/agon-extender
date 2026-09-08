# General Poll endpoints pass; acquisition shortened

The Author reports Agon General Poll PASS and return to MOS. P4 reports the
exact request, real parser reply and successful transmission. Original serial
hash and the frozen verdict were rechecked. Sigrok decoding and independent
sample inspection confirm 17 00 80 A5 forward and 80 01 A5 return at nominal
1,152,000 baud, valid stop bits and flow-control permission for complete frames.

Analyzer acquisition FAIL is retained: 119481370 of 240000000 samples at
24 MHz, or 4.978390 seconds of the requested ten. The log records repeated
empty USB transfer timeouts and exit zero despite the short extent. The
underlying cause remains unresolved; this does not prove exhausted memory.
The waveform contains 4.655861 seconds of quiet after the final RTS stop,
short of the specified five seconds. Serial monitoring remained clean for
6.005568 seconds after first P4 PASS.

The Author accepted this bounded General Poll milestone on 2026-09-08 with
the acquisition failure and shorter waveform tail explicitly retained.
Disposition is accepted PASS with these exceptions. No sustained-load, analog-margin
or complete-startup claim. Original trace and derived measurements are retained
here; full original logs and machine-specific metadata remain in private records.
