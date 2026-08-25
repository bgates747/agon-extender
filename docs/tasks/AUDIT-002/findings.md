# AUDIT-002 findings — controlled-power wiring draft

## Disposition

The corrected `light2-extender-breadboard-wiring-draft_v1.fzz` is a logically
complete Fritzing representation of the documented controlled-power
predecessor circuit. It passes the task's evidence-derived connectivity
contract. This is a drawing-level result only: it neither verifies the current
bench assembly nor approves this topology as the new beta or production
design.

At audit acceptance, the preserved Author draft was SHA-256
`9dbd85b7d971cb787df117a9ddc81e4bc05feaa53c2a7e5ae47e5af6db71c541`
and the corrected generated derivative was
`b337326248d4669e3624d07bb336077c7eb252cc0a1333ecec198def22f142a9`.
CA-2026-08-25-001 later corrected only embedded Agon UART1 part metadata and
artwork. Their current hashes are respectively
`df8b899c41b2b186af5c298a30e70178c5fad94f0430a14f7f100407172c3b54`
and `e3b5a44bb1c795dc120c21c77ffd0e3855eb2a6d0772b7781700ce1d59a836c0`.
The regenerated connectivity graph retains 49 instances, 234 conductive nets,
and all 60 passing expected-circuit checks.

## Evidence reconciliation

1. The tracked `carrier-breakout-design.md` pin map was compared with the
   predecessor P4 data/control declarations, P4 reverse-UART declarations,
   eZ80 Port C/Port D masks, U1 probe procedure, and P4 endpoint probe
   procedure from `agon-extender-legacy` tag
   `legacy-archive-2026-08-26` (`df54cf6a7a23cd40e98076856f68cff0559d1c77`).
2. The sources agree on every in-scope signal endpoint, U1 channel, ownership
   control, component value, pull direction, and controlled-power supply
   connection. No source conflict required an audit choice.
3. `expected-circuit.json` records the reconciled circuit as named endpoint
   groups, component identities, isolated endpoints, required net separation,
   prohibited positive-rail joins, and structural invariants.

## Defects found in the first derivative

The first extracted derivative, SHA-256
`1b022148cbaec8c4cf24c1e85354076b2d410794a9fbe874b9cd30bb374db379`,
failed 18 of 60 checks. Those failures arose from five primary defects:

1. Agon pin 33/GND and pin 34/+3.3 V were absent. The top and center supply
   rails were not joined, and P4 EXT1 pin 2 was not connected to common signal
   ground.
2. The `PC1` bidirectional path incorrectly joined U1 pins 2 and 6 while the
   220-ohm reverse-output resistor landed U1 pin 7/GND instead of pin 6.
3. The 10-kilohm pull-ups for `REV_OE_N`, `FWD_OE_N`, and unused U1 pin 10 had
   one unlanded lead each.
4. U1 pin 14/VCC was connected to ground. Consequently both terminals of the
   100-nF bypass capacitor were also on ground.
5. A CLOCK jumper and P4 EXT1 pin 15 occupied the same physical breadboard
   hole even though an adjacent hole on the same five-hole bus was free.

## Corrections made

1. Added independent, labeled contacts for Agon pin 33/GND and pin 34/+3.3 V;
   neither 16-contact signal header was enlarged.
2. Connected pin 34 to the joined red logic-reference rails and pin 33 to the
   joined blue ground rails. Connected P4 EXT1 pin 2 to that common signal
   ground. P4 EXT1 pin 1/+3.3 V and EXT2 pin 1/+5 V remain unconnected to the
   Agon positive rail.
3. Restored the documented `PC1` topology: Agon pin 18 directly feeds U1 pin
   2; U1 pin 6 reaches Agon pin 18 only through its dedicated 220-ohm resistor.
4. Landed the `REV_OE_N`, `FWD_OE_N`, and unused-channel pull-ups on Agon 3.3 V.
5. Moved U1 pin 14 and its capacitor terminal to Agon 3.3 V while retaining
   the capacitor's opposite terminal and U1 pins 7/9 on ground.
6. Moved only the CLOCK jumper endpoint to an adjacent electrically identical
   hole, eliminating the impossible double occupancy without changing its net.
7. Extended the two visually short pull-up leads to their recorded rail holes.
   All unrelated original instance geometry remains generator-checked as
   unchanged.

## Validation result

1. Expected/actual checks: 60 passed, 0 failed.
2. Nonreciprocal recorded connections: 0.
3. Multiply occupied breadboard holes: 0.
4. Dangling resistor or capacitor leads: 0.
5. Deterministic generator check: passed.
6. Deterministic extractor check: passed.
7. Deterministic comparison check: passed.
8. FZZ ZIP/XML integrity: passed.
9. Original Author-draft hash guard: passed.

The detailed results are in `generated/connectivity.md` and
`generated/comparison.md`.

## Claim boundary

1. The audit establishes recorded Fritzing connectivity, not physical
   continuity, component orientation on the bench, powered behavior, signal
   integrity, or safe either-order power operation.
2. The represented `SN74HC125N` circuit remains restricted to the predecessor
   power discipline. It does not satisfy the pending fresh-design
   partial-power-down requirements merely because its drawing is now correct.
3. The Author performed the ordinary Fritzing visual review through the
   cosmetic `draft_v2` derivative and accepted closure of AUDIT-002 on
   2026-08-25. The local Fritzing batch exporter remains unsuitable as a
   headless visual gate; future generated changes still require ordinary GUI
   review.
4. No physical wire, component, rail, probe, or powered device was changed or
   authorized by this audit.

## Author cosmetic derivative v2

The Author saved
`light2-extender-breadboard-wiring-draft_v2.fzz` after making cosmetic edits.
Its accepted pre-CA SHA-256 was
`207a59b795b472db7881b68eadeb7a55464ab13a51690bfa1de8f1476e8564cb`.
After the bounded CA-2026-08-25-001 embedded-part correction, its SHA-256 is
`51a69f6e7200fd46f2a2e2d15e047478e6f4080328f625bd35d648464c64136c`.

The follow-up electrical review found:

1. All 60 expected-circuit checks pass.
2. All non-wire component and connector terminals have exactly the same net
   partition as audited `draft_v1`; this broader equivalence check includes
   terminals not named individually by the 60-check manifest.
3. Nonreciprocal connections, multiply occupied holes, and dangling passive
   leads remain zero.
4. Component identities and values are unchanged. Fritzing added only the
   redundant `part number=SN74HC125N` property to U1.
5. Fritzing represented some cosmetic rerouting as five new jumper objects,
   removed the superseded `AgonGroundEntry` wire object, shifted the red rail
   bridge from column 59 to column 58, and moved several wire landing holes.
   Every such change is net-preserving.
6. FZZ ZIP/XML integrity passes.

`draft_v2` is therefore electrically equivalent to the audited `draft_v1` and
is electrically correct within the same controlled-power predecessor-circuit
claim boundary. It remains a manually edited review artifact rather than an
output reproduced by `make-draft-v1.py`.

The Author accepted this result and closed AUDIT-002 at 2026-08-25 15:00 EDT.
