# General Poll P4 candidate deployed

The corrected candidate was written and independently verified after the
Author authorized P4 flashing. Startup confirms exact candidate identity,
RX22/TX12/CTS23/RTS11, 1,152,000 baud and empty WAIT with CTS HIGH.
This passes installation/readiness only; paired General Poll and waveform
qualification remain pending. Both boards remain powered with ribbons seated.

The earlier deployment's stale identity failure is retained in private records
and explained in PORT-013. Two successive incremental builds recompiled the
boot object and passed embedded identity checks before this deployment.
