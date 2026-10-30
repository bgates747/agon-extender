# INPUT-005 — Application-owned controller routines and minimal EMOS transport

Move every practical controller-specific duty from resident EMOS into a reusable
application include, recovering as much eZ80 flash as measured, correct builds
permit. The Author calls this their personal API: standardized, proven routines
shared across applications. It is linked into each application, not a MOSlet.
Preserve controller operation, ordinary input and EMOS ownership of transport.

## Authority and state

1. Author authorizes this task on 2026-10-30, requests that all guidance be
   recorded, then all current dirt committed/frozen before implementation.
   Extender and EMOS are clean at task creation. Publish this plan first.
2. Extender owns the public application include, viewer integration, P4 wire
   contract and cross-component tests. EMOS component task INTEG-018 owns its
   resident endpoint. The prior diagnostic extraction remains independent.
3. Baseline is the tested DIAG-003 source: EMOS `eebdd76`, controller module
   2,199 ROM bytes, complete unversioned controller image 127,817 bytes / 3,255
   free. Preserve exact baseline artifacts and compare equal build identities.
4. This tranche is offline source, target builds and native/linked checks. No
   hardware, flash, SD, startup, emulator launch or production selection change
   is implied. The installed keyboard-only P4 and named EMOS remain untouched.

## Accepted direction and implementation decisions

| ID | State | Decision / consequence |
|---|---|---|
| I5-01 | Author accepted | Move as much controller logic as practical into ordinary application code; measure complete EMOS savings and retain only justified resident duties. |
| I5-02 | Author accepted | Provide one maintained public include containing reusable proven controller routines. No MOSlet, dynamically loaded provider, daemon or per-game copy of the implementation. |
| I5-03 | Author accepted; compatibility bounded | Applications consume one normalized gamepad interface compatible with the on-hand F310's XInput-style controls. No USB VID/PID checks or device report layouts in the application include. P4/host acquisition adapters own physical USB differences; unsupported hardware is not made compatible merely by including this file. |
| I5-04 | Selected implementation | Keep P4 CI2/CIS2 wire bytes and its retained-edge queue. Application code builds requests, validates replies, tracks source/edge identity, acknowledges accepted transitions and applies freshness/neutralization. |
| I5-05 | Selected implementation | EMOS retains the existing gateway/UART owners, fixed controller endpoint, bounded resident reply, lifetime/correlation protection and interrupt-safe copy. No arbitrary control-envelope or application UART/GPIO bypass; controller and SD ownership remain separate. |
| I5-06 | Selected implementation | Use distinct new gateway operation values so old clients/services fail clearly. Supply raw timing metadata with the copied reply; keep request/cache deadline enforcement resident to reject clock-wrap/delayed replies. Do not retain the old full semantic service alongside the new one. |
| I5-07 | Constraint | No new CRC/checksum, calibration policy in ROM, automatic reconnect after faults, unrelated USB restoration or universal configurable message framework. |

## Bounded research précis

1. [The existing audit](INPUT-004/EMOS-CONTROLLER-AUDIT.md) identifies duplicate
   validation, source/transition tracking and stale normalization in EMOS and
   `tests/fixtures/controller/live.hpp`. Existing UART framing, serializer,
   gateway, clock and lifecycle already are reused. Consolidating tiny helpers
   is secondary to removing resident controller interpretation.
2. Official MOS API documentation in `../../agon-docs/docs/mos/API.md`, resolved
   from repository root, describes routed VDU and fixed sysvar replies. Legacy
   ordinary VDU reaches onboard UART0; it cannot replace admitted P4 UART1
   controller requests. The keyboard callback is not a generic packet inbox.
3. The existing SD service has a different lease, wider MOSlet memory admission
   and interrupt-masked bulk copying. Do not borrow that service or reproduce
   its copy pattern. The controller reply must remain coherent while keyboard
   interrupts continue, with no application pointer retained by an ISR.
4. Current controller wire authority is
   `vdp/video/extender/input/controller/appliance_wire.h`; keep mechanical EMOS
   copies and any embedded public-header definitions checked against it.

## Work plan and gates

1. [ ] Publish/freeze this task, component task and accepted architecture before
   coding. Preserve diagnostic-extraction baseline bytes/maps/provenance.
2. [ ] Specify the small gateway and application include together. Keep a single
   active consumer, opaque boot-local ownership and request correlation; use
   finite expiry and distinguish source invalidity from carrier loss.
3. [ ] Implement the reusable, allocation-free include in a role-named public
   location. Provide named buttons, native sticks/triggers, optional eight-bit
   conversion, validity/age/source generation and retained press accounting.
   Bind through admitted EMOS calls; keep the header usable in host tests.
4. [ ] Reduce resident code iteratively, moving request encoding, controller
   semantics, source/ACK tracking and age interpretation into the include.
   Preserve caller/buffer bounds, fixed endpoint, lifetime cleanup and short
   interrupt locks. Compare measured alternatives before retaining complexity.
5. [ ] Make the mode20 viewer use the same include without changing its display
   lifecycle or input pacing. Identify fsim integration changes; do not modify
   another project's consumer or emulator without its own authority/review.
6. [ ] Update meaningful tests for malformed state/transitions, no premature ACK,
   duplicate/short taps, source change, clock wrap, expiry/reopen, old-service
   refusal, failure cleanup and keyboard/Escape delivery. Exercise actual P4,
   resident and application code together; compile the public include on Agon.
7. [ ] Build complete ordinary/controller EMOS through owner wrappers and all
   mandatory guards. Record ROM/RAM deltas, resident increment, application
   code/RAM cost and exact artifacts. Keep rendering/transport timing separate.
8. [ ] Update current public/operating/build contracts, frozen old-ABI description,
   task evidence and logs. Commit reviewable offline work where no emulator
   validation gate applies. Leave deployment identity, physical review and
   production acceptance/promotion explicitly pending.

## Completion boundary

## Selected gateway layout for coordinated implementation

The new development transport ABI uses input operations 4..7, leaving the old
0..3 operations unsupported in the reduced endpoint. The service name remains
`ext.controller`; P4 CI2/CIS2 wire version2 remains unchanged.

| Input operation | Input bytes | Output | Owner action |
|---:|---:|---|---|
| 4 OPEN | 1 | 4-byte boot-local token | EMOS allocates a nonzero token; a 24-bit counter encoded as u32 with high byte zero suffices and must fail rather than wrap. |
| 5 RECEIVE | 1 | 98 bytes | EMOS copies untouched96-byte CIS2 plus raw request-to-receive and receive-to-copy MOS tick deltas, one byte each. One consumption per reply; no cached-state interpretation. |
| 6 SEND | 20 | none | Application supplies operation byte plus the complete19-byte `23,0,F7,CI...` request. EMOS admits only this fixed controller envelope/operation and the current token, records correlation and invokes its existing serializer. |
| 7 CLOSE | 1 | none | EMOS revokes local admission. Application may first send a best-effort CI close through SEND; cleanup must still revoke admission after transport failure. |

EMOS retains one outstanding request and one unread reply. RECEIVE while waiting
or without a reply returns busy; SEND request while either exists returns busy.
An admitted CI close may cancel that pending state. Reply correlation uses
token/query and exact length; application code owns magic/content validation.
Expiry remains30 nominal MOS ticks and cannot be revived across low-byte wrap.
Application code owns query sequencing/renewal and accepted-edge ACK; EMOS does
not parse transition records. App freshness reproduces the conservative source
age plus each local tick delta with its phase margin, without presenting those
nominal units as calibrated milliseconds. No application pointer survives a call.

The public header lives at `include/agon/controller.hpp`, with maintained
controller-wire definitions mechanically embedded/checked for standalone reuse.
It must support AgonDev and host-model transport bindings. The viewer's existing
mode/graphics code remains separate from these reusable input routines.

## Completion boundary

A smaller measured EMOS endpoint, a genuinely reused application include, a
working target build of the existing viewer and passing software/instruction
regressions complete the offline tranche. No claimed minimum size or universal
USB compatibility follows from a code-size reduction. Physical USB coexistence
remains INPUT-004, and future calibration/mapping UI remains a separate feature.
