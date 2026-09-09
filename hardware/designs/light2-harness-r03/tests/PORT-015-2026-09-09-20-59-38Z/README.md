# USB keyboard repeat

The operator completed the repeat requested with the Agon harness connected.
Both devices were reported powered, keyboard initially disconnected, and the
keyboard was left connected afterward. Exact harness seating was not separately
confirmed or independently inspected; do not treat this as electrical proof.

P4 recorded a, Shift+A, 1, Enter, Backspace and a after reconnection, each with
matching press/release identity. Two connections, one removal, sixteen reports
and fourteen key events were observed. No application restart occurred after
host readiness. The same `USB HOST: EP command error: ESP_ERR_INVALID_STATE`
appeared once at unplug. Functional checks pass; the no-fault gate remains open.
Full raw serial and private metadata are retained locally; the published excerpt
contains all USB and error-level lines. No new firmware or EMOS/SD change.

Review 2026-09-09T21:06:51+00:00: the [pinned-source trace](../usb-keyboard-unplug-review.md) explains the removal diagnostic; it no longer blocks the bounded acquisition result. Earlier observations and partial outcome remain intact.
