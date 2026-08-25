# AUDIT-002 — Verify and complete the draft Extender wiring diagram

## State

- Status: Complete — accepted by Author
- Started: 2026-08-25 03:19 EDT
- Finished: 2026-08-25 15:00 EDT

## Intent

Establish whether the current SETUP-006 Fritzing `draft_v1` is a correct,
complete representation of the documented controlled-power prototype circuit.
Compare its electrical connectivity—not merely visual proximity—against the
tracked legacy design evidence, official Agon/P4 pin identities, and the
firmware pin assignments that exercised the predecessor circuit. Correct the
review draft and deterministic generator where the expected circuit is clear.

This audit does not approve the predecessor topology for production, qualify
either-order power behavior, select the pending fresh-design electrical
candidate, change physical bench wiring, or promote `draft_v1` into an
authoritative harness revision.

## Input and authority

1. Review input:
   `SETUP-006/SETUP-006.4-wiring-design/light2-extender-breadboard-wiring-draft_v1.fzz`.
2. Preserved Author source:
   `SETUP-006/SETUP-006.4-wiring-design/light2-extender-breadboard-wiring-draft.fzz`.
3. Tracked predecessor circuit authority:
   `hardware/designs/light2-harness-r01/legacy-evidence/carrier-breakout-design.md`
   and `wiring-diagram.svg`.
4. Official board identities and current project findings under
   `hardware/designs/light2-harness-r01/` and SETUP-006.
5. Read-only predecessor firmware and host test code only where required to
   confirm that a documented wire was exercised with the stated GPIO role.

## Work

1. [x] Create this audit as the first active TODO item and freeze its scope,
   authorities, exclusions, and stop boundary.
2. [x] Build a deterministic task-local extractor that resolves Fritzing
   instance connections, custom breadboard buses, wires, passive endpoints,
   U1 pins, Agon contacts, P4 contacts, and supply rails into a reviewable
   connectivity inventory. The extractor records the exact input hash, emits
   structured JSON plus a compact Markdown component inventory, checks
   reciprocal connections and occupied holes, and retains visually floating
   passive leads as explicit dangling endpoints.
3. [x] Derive an expected controlled-power circuit manifest from written
   evidence and corroborating code, preserving conflicts instead of silently
   selecting one source. The sources agree on every in-scope route; the
   machine-readable authority is `AUDIT-002/expected-circuit.json`.
4. [x] Compare actual and expected connectivity one route at a time, including
   D0--D7, CLOCK, VALID_N, READY_N, all U1 channels and enables, series and
   bias resistors, bypass capacitance, Agon pin 33/GND, Agon pin 34/+3.3 V,
   P4 ground, rail continuity, and prohibited positive-rail joins.
5. [x] Correct `draft_v1` through its deterministic generator where evidence
   is unambiguous. Represent Agon pins 33 and 34 as separate single-wire
   contacts rather than expanding either 16-contact signal header. Keep pin
   33 on common ground and pin 34 on the Agon-derived 3.3 V logic rail.
6. [x] Re-extract and validate the corrected artifact. Require deterministic
   output, valid ZIP/XML, no occupied-hole collisions, complete reciprocal
   connections, preserved unrelated geometry, expected endpoint-to-net
   membership, and explicit negative checks for forbidden positive-rail
   joins.
7. [x] Record findings, corrections, remaining conflicts, and the exact scope
   of any claim the corrected draft can support. Stop for Author review
   without committing, pushing, changing bench wiring, or authorizing power.

## Accepted result

The corrected generated `draft_v1` and the Author's cosmetically edited
`draft_v2` each pass all 60 expected/actual checks. A broader comparison also
proves identical non-wire terminal net partitions between the two. The
complete defect list, corrections, validation evidence, v2 equivalence result,
and claim boundary are recorded in `AUDIT-002/findings.md`. The Author accepted
the result and closed the audit at 2026-08-25 15:00 EDT.

## Stop condition

Stop after producing a deterministic corrected review draft, machine-readable
audit evidence, and a human-readable findings report. Any unresolved circuit
contract remains an explicit audit finding or SETUP-006 decision; it must not
be guessed into the drawing.
