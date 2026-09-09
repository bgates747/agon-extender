# USB keyboard acquisition observation

Three keyboard connections and two removals in one recording; each connection admits one lowercase a DOWN/UP pair. Final counters: attached=1, reports=9, key_events=6. No application restart between these connections.

The operator reports corrected data wiring to EXT2.19/20. The unchanged candidate received the keyboard. Removal logs `USB HOST: EP command error: ESP_ERR_INVALID_STATE`; retain this informative diagnostic and investigate before claiming the no-fault gate. Opening serial observed application startup; its cause is unresolved. No restart was observed after host readiness within this recording. Full raw serial and private metadata are retained locally; the published excerpt includes all USB lines and error-level lines. This is acquisition evidence, not EMOS keyboard integration.

## Wiring-state correction — 2026-09-09T20:58:50+00:00

The Author clarified that Agon was powered during these USB captures, but the Agon harness was not connected to the P4 right-side header (the same side as the USB connections). This supersedes the earlier assumption of a fully seated Agon/P4 harness for these runs. Native USB observations remain valid for this reported wiring state; simultaneous operation with the full Agon harness attached was not tested. The relation, if any, to the unplug diagnostic remains unestablished. No reconnection or hardware operation is implied by this correction.

Review 2026-09-09T21:06:51+00:00: the [pinned-source trace](../usb-keyboard-unplug-review.md) explains the removal diagnostic; it no longer blocks the bounded acquisition result. Earlier observations and partial outcome remain intact.
