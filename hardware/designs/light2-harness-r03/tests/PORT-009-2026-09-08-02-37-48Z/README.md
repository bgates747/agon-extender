# P4 UART receiver deployment

Run `PORT-009-2026-09-08-02-37-48Z` is **partial**: deployment and startup
passed; the operator has not yet booted the Agon UART sender.

The frozen paired candidate is `uart-forward-probe-r01-b2026-09-08-02-35-54Z`.
P4 flash programming and a separate verification both passed. The boot log
shows the selected build, QIO/80 MHz flash, 360 MHz CPU, GPIO22 RX at 115200/8N1,
and repeated WAIT with zero bytes received. Both boards stayed powered with
ribbons connected. No EMOS reflash was performed.

The workstation backed up the original SD autoexec, staged U1SEND.BIN and the
mode-3/status/sender/status script, checked contents, synced and unmounted.
The operator will insert the card with Agon off, invoke the private workstation
capture launcher, then power Agon on at its prompt. The launcher restarts the
verified P4 receiver and captures for 90 seconds, retrieving evidence locally.
The later transfer capture receives its own run ID; this deployment record
must not be relabeled as a UART PASS.

See [deployment metadata](deployment.yaml), [build manifest](build-manifest.yaml),
[receiver boot log](boot.log), and [test sheet](../uart-forward.md).
