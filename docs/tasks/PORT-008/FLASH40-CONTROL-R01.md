# PORT-008 — Historical receiver 40 MHz flash control

## Executive summary

Author authorizes the proposed single-record control after the
[build comparison](BUILD-COMPARISON-R01-RESULTS.md). Rebuild the exact retained
standalone GPIO-remapped receiver with 40 MHz flash instead of 80 MHz. Preserve
its SDK, compiler, receiver/canary/sender source, GPIO map, DMA settings and
slowest sender profile. No EMOS/mainboard VDP update or wiring change.

FC01 [ ] — Freeze this contract. Prepare a separate local build from the retained
reproduction, prove receiver/canary/sender bytes unchanged and generated settings
differ only in flash frequency (plus generated build identity). Verify both
bootloader and application image/flash settings; retained old evidence stays intact.

FC02 [ ] — Verify current input and original startup through the admitted
foreground listener. Confirm the already-deployed historical sender by complete
readback; do not rebuild it. Stage the reviewed temporary startup selecting mode3
then loading/running the sender. The sender restores original startup before GPIO
access. Preserve the current exact full EDP rollback; no redundant firmware backup.

FC03 [ ] — Flash/read back the identified P4's standalone 40 MHz composition.
Retain boot confirmation of the actual flash clock. Reuse the existing collector
and unchanged analyzer attachment for exactly one 1,024-byte, 24-NOP-profile
record, gated on actual sender admission. No retry or remaining sweep. Record
full pattern/sequence/CRC verdict separately from acquisition and source waveform.

FC04 [ ] — Restore/read back the exact prior full EDP composition, wait for P4
HTTP readiness, then reset Agon for original startup/input admission. Independently
verify original startup, actual remote-command delivery and neutral input; exit
the listener. Compare with the 80 MHz failure, update parent/handoff/log, and stop.
A pass would establish sensitivity, not prove a fundamental flash or DMA fault.

## Scope and recovery

The Author's historical raw-GPIO sender exception remains limited to this
comparison; it creates no supported bypass of EMOS transport ownership. Normal
SD, input and display interfaces remain unchanged. Keep machine identities,
absolute local tool paths and installed receipts in ignored local records.

Use maintained SD placement and fixture-mode rules. Do not reset if the card is
known removed or a card-location question is pending. If readiness is lost,
restore the retained full EDP before attempting input-dependent recovery. Stop
on ambiguous invocation rather than replaying. No source/SDK bug fix or extra
physical test belongs to this control. Production selection remains unchanged.
