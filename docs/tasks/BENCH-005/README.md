# BENCH-005 results and reusable probes

[Results](RESULTS.md) · [Contract](../BENCH-005.md)

The installed web client's 30 fps request cap materially contributes to visible
latency; no firmware or production UI change made. See the measured table and
limits before interpreting these numbers as keyboard latency.

`fixture/` is the latency app. `textread/` is the stock-command screen reader,
validated on Legacy and ExCom interior text. It cannot recognize the last row or
column because of retained upstream bounds behavior, and does not capture a hung
app's screen autonomously. Its cursor metadata is cached.

Build each with `make -C <directory>`. The tools live on the Agon at
`/test/bench005/`; textread saves the selected current display to a specified SD
path. Keep latency measurements and screen-reading traffic separate.
