# REMOTE-008 — P4 reset from web console

Provide a distinct Reset P4 button beside Reset Agon. The Pi bench bridge owns
exact-device USB reset; the P4 serves the button but does not need working
scanout to accept a host-controlled reset. Author requested this after a mode96
scanout fault. Implementation authorized; no unrelated renderer changes.

## Scope and gates

1. Extend existing fixed-command, origin-restricted, deduplicated reset bridge
   with an optional /reset-p4 target. Keep original Agon configuration compatible.
2. Add separate labelled button, explicit confirmation and target-specific error.
   Release browser keyboard before reset; no automatic retry, flash or Agon reset.
3. Keep USB identity, actuator command and network origins in ignored local config.
4. Verify target isolation, disabled/unconfigured behavior and idempotency with
   HTTP tests. Build from a clean isolated source matching installed renderer.
5. Deploy verified bridge and an identified firmware candidate, preserving exact
   installed rollback and ordinary startup. Author tests actual browser behavior.
6. P4 reset may require subsequent Agon reset for EMOS input admission; document
   this without silently coupling the two reset buttons.

## Status

Implementation active. Owning source: scripts/reset_bridge.py and
vdp/video/extender/web/. No production acceptance or promotion claimed.
