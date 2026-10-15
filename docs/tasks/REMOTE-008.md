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

## Candidate validation and deployment

Isolated source c233ac8e based on installed renderer c788b668; identified build
indexed-hdmi-r08-b2026-10-14-04-55-12Z. Board, SDK, dependency lock and renderer
feature flags match the previous installation. Native validation passes. Three
bridge HTTP tests pass (including cross-target deduplication and no Agon fallback),
headless button tests pass, and actual embedded assets plus48codec vectors pass
using installed Chromium. Default Playwright-managed browser was absent; using
system Chromium required no product change.

All four non-NVS segments independently verified after installation; NVS and
mainboard startup preserved. Actual served assets match build inputs. Headless
browser clicked the served Reset P4 button, received target-specific200 and saw a
fresh P4 boot. Reset Agon also passed with fresh admitted input. Executable and
startup independently read back; listener EXIT acknowledged.

Escape-only fixture checked in mode20: Tab retained mode20, Escape returned to
mode0 menu, zero rolling faults. Menu now awaits Author input. The mode96
return/scanout fault remains unresolved and is not claimed repaired by these
changes. Exact r07 rollback retained. Author browser acceptance and production
promotion remain pending; no new version/tag selected.
