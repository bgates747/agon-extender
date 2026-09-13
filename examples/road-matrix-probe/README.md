# Buffered road-matrix reduction

Local PORT-003 diagnostic derived from the Author's AgonArcade road protocol;
provenance.json binds the original header and its unchanged startup bytes.
This is a test article, not a Rally renderer change or a released utility.

Build with `make -C examples/road-matrix-probe AGONDEV_TOOLCHAIN=/path/to/agondev`.
Select mode8 before invocation; the fixture never switches modes. At the CLI
or in an autoexec after the selected Extender route is ready:

```
VDU 22 8
CD /codex/agon-extender/PORT-003
LOAD matprobe.bin
RUN . compute
```

`compute` preserves all matrix creation, per-block data transforms and target
buffer replacement, but replaces the two final calls of the transformed PLOT
buffer with six VDU0 bytes. `draw` retains those calls unchanged. Both submit
80 road sections at12 raw MOS ticks apart, target8seconds total, then write
MATCOMP.CSV or MATDRAW.CSV and return to the CLI. The receipt proves eZ80
submission and elapsed time, not P4 command completion. Observe target identity,
output and CLI recovery independently. UART/CTS can block if P4 fails; the host
must keep a bounded observation and the established Pi reset/SD recovery path.

The section range stays inside320x240 and uses the actual production protocol.
This separates matrix/stream lifetime from primitive execution. No font, car,
scenery, network client or private callback is required by the fixture.
Cold-boot use must preserve normal recovery and never leave a failing autoexec.
