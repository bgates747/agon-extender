# DIAG-002 — Report Extender connection and P4 identity at EMOS startup

## Executive summary

On every ordinary EMOS startup, report whether EMOS has established its
Extender transport relationship and, when available, identify the exact P4
firmware/build running at the other endpoint. This should make a stale or
missing EMOS↔P4 relationship visible without relying on a browser-side symptom.

Schedule this work only after AUDIT-010 is complete and after the planned
sparse-checkout/workspace reduction has been reviewed and applied. The task
must define a bounded startup handshake and failure behavior before changing
either firmware; it must not turn a missing Extender into an indefinite boot
delay or silently reset either processor.

Created: 2026-09-30. Owning queue: `TODO.md`. Related work:
[AUDIT-010](AUDIT-010.md), [REMOTE-006](REMOTE-006.md),
[architecture](../architecture.md), and [version policy](../versions/README.md).

## State and evidence

D02-S01 — **Queued; contract not yet reviewed.** The Author requested this task
after an independently verified P4-only flash left EMOS unable to use the new
P4 session until the Agon was reset.

D02-S02 — The 2026-09-30 RP06 qualification setup failure reached the P4 web
server but timed out with keyboard `session: 0`, zero emitted/accepted traffic,
and `ready: false`. Resetting the Agon re-established Extender keyboard input.
This is motivating evidence, not proof of the final protocol or implementation
owner.

D02-S03 — Filing this task authorizes no EMOS/P4 source change, build, flash,
reset, deployment, protocol allocation, production promotion, or sparse-checkout
change.

D02-S04 — During AUDIT-010 qualification on 2026-09-30, keyboard capture was
working at P4 admission epoch `618040141`. The Author then independently reset
only the Agon. The P4 HTTP service remained reachable and advanced its keyboard
epoch to `618040142`, but reported `ready=false`, admission reason 1; fresh
screen capture remained pending and the Author observed that the P4 no longer
accepted the Agon connection. This is direct one-sided-reset evidence for
D02-02/D02-06. It does not authorize advancing this deferred task during the
audit.

D02-S05 — The Author authorized bounded recovery. The host verified the exact
P4 USB identity, issued a no-flash P4-only reset, and observed fresh P4 HTTP
epoch `3114281151`. It then reset only the Agon and required—not inferred—a
fresh ready/neutral Extender admission at epoch `3114281152`. Keyboard locale 1,
mode 0 at 640×480, offline SD listener and a fresh Legacy screen capture were
all observed. This establishes one working recovery order; it does not explain
the lost admission or satisfy D02-06's complete reset-order matrix.

## Required behavior

D02-B01 [ ] During ordinary startup, EMOS reports an actor-explicit Extender
connection state at the mainboard screen: connected, unavailable, incompatible,
or timed out. Define the exact finite wait and distinguish transport absence
from version-query failure.

D02-B02 [ ] When connected, EMOS displays a stable human-readable P4 firmware
version and immutable build identity supplied by the P4. Do not substitute a
browser asset version, Git branch, local checkout state, or qualification label
for the installed firmware identity.

D02-B03 [ ] When the P4 is unavailable or its identity cannot be validated,
EMOS continues into a usable Legacy-mode prompt after the bounded timeout and
prints a durable diagnostic that is not immediately overwritten.

D02-B04 [ ] A P4 restart creates a fresh peer epoch. EMOS must not report the
old P4 identity or connected state as current after transport loss. Whether
EMOS automatically rediscovers the restarted P4 or requires an explicit
operator action remains a design decision for this task.

D02-B05 [ ] Startup reporting must not automatically reset the Agon, P4, or
onboard VDP. It must not make the browser, network, or Extender keyboard path a
prerequisite for Legacy startup or recovery.

## Work items

D02-01 [ ] After AUDIT-010 and the accepted sparse-checkout/workspace change,
review official MOS/VDP contracts and the maintained EMOS↔P4 startup path.
Record exact reference commits and current production identities before design.

D02-02 [ ] Trace the present boot, transport admission, P4 boot-epoch, keyboard
readiness and generated-build-identity mechanisms. Identify which processor
owns each state and where a stale relationship can survive a one-sided reset.

D02-03 [ ] Propose the smallest versioned identity/status exchange, including
timeouts, compatibility handling, absent/older-peer behavior, retransmission,
fresh-epoch detection and operator-visible text. Present unresolved decisions
to the Author one at a time before freezing the contract.

D02-04 [ ] Implement the accepted EMOS and P4 changes without bypassing EMOS
ownership of ordinary VDU routing, Extender activation, transport, or committed
mode.

D02-05 [ ] Add deterministic host tests for connected, absent, late,
incompatible, malformed and P4-restarted cases. Verify that unavailable P4
startup reaches a usable Legacy prompt within the accepted bound.

D02-06 [ ] Add physical qualification covering cold boot, Agon-only reset,
P4-only reset, both reset orders, disconnected P4, Legacy recovery and ExCom
re-entry. Record exact displayed identity against independently verified
installed P4 bytes.

D02-07 [ ] After Author acceptance, update current startup/recovery guidance
and complete normal production promotion, version agreement and tagging.

## Dependencies and ordering

D02-D01 — AUDIT-010 must complete before investigation begins so this task uses
the accepted repaired pre-LCD baseline.

D02-D02 — The planned sparse-checkout/workspace reduction must be separately
reviewed and completed before this investigation. That work changes development
scope and navigation, not product behavior; DIAG-002 must not implement it
implicitly.

D02-D03 — Coordinate with REMOTE-006 because independent P4 reset exposes the
same peer-loss/recovery boundary. Neither task may silently merge the separate
Reset Agon and Reset Extender actions.

## Validation gates

D02-G01 [ ] Startup output truthfully distinguishes connected, unavailable,
incompatible and timed-out states.

D02-G02 [ ] Reported P4 version/build identity matches the independently
verified installed image and cannot remain stale across a P4 boot epoch.

D02-G03 [ ] Missing or malfunctioning P4 does not prevent bounded Legacy boot,
mainboard recovery, or a usable EMOS prompt.

D02-G04 [ ] One-sided reset cases have explicit, tested outcomes and do not
silently reset the other processor.

D02-G05 [ ] Existing startup, keyboard admission, Legacy/ExCom switching,
browser output and qualification tests remain passing.

## Non-goals

D02-N01 — This task does not implement the sparse-checkout scheme, redesign the
browser status UI, combine reset controls, or add automatic firmware update.

D02-N02 — A Git commit string alone is not a product version. This task does
not allocate a production version or tag before accepted qualification.
