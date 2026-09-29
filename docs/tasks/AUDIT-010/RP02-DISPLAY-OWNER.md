# AUDIT-010 RP02 — Sole product display owner and retirement boundary

## Result

`A10-RP02-S01` [ ] Candidate complete; awaiting Author acceptance.

The stock-shaped `StockRuntimeController`/`StockP4Service`/stock-scanline
family is the sole product display owner. The older project-owned generic
display family remains selected only by
`p4-port008-nonrelease-qualification`; it is neither a product fallback nor a
second repair target. The profile manifest and native build tools now reject a
mixed family, an incomplete family, a second product owner, or an unbounded
non-release family.

This item changes selection authority and validation only. It changes no
renderer, mode, palette, Copper, snapshot, browser, transport or hardware
behavior. No repair was copied between families.

## Family inventory

| Family | Selected actors | Role | Buildable profile |
|---|---|---|---|
| `stock-shaped` | `StockRuntimeController`, `StockP4Service`, `stock_native_access`, `stock_scanline`, `stock_render_utils` | Sole product display owner | `p4-console` |
| `port008-parallel-nonrelease` | `P4DisplayController`, `P4FrameService`, `LogicalFrameService`, `NativePixelCodec`, `PlaneStorage`, `PaletteState`, `PresentationCompositor`, `screen_facade_p4_binding`, `fabutils_port` | Bounded qualification dependency; no product authority | `p4-port008-nonrelease-qualification` |
| none | No display source | Recovery programmer | `p4-mos-recovery` |

The shared `ScreenFacadeAdapter`, cursor adapter and presentation snapshot pool
are not family-defining actors. Their presence in more than one profile does
not grant the non-release family product ownership.

## Oracle disposition

`A10-RP02-O01` [x] **Portable rendering and presentation expectations are
already extracted.** The selected-family PORT-003 stock tests contain the
original packed native-row programs, stock scanline/Copper/decorator paths and
runtime-binding checks. They supersede old-family renderer, codec, palette and
compositor tests as product regressions. The older implementation-specific
tests remain frozen evidence; `NativePixelCodec`, `PlaneStorage` and
`PresentationCompositor` API behavior is not itself a product contract. The
current reproducibility limit for the historical stock runner is recorded
below and does not restore authority to old-family tests.

`A10-RP02-O02` [x] **Mode and lifecycle expectations are already independent.**
PORT-003 Phase E's 58-mode and seven-lifecycle fixture is an independent
transcription of the official contract, and the maintained console lifecycle
test applies the lifecycle harness to the selected `agon_screen.h` facade.
Those expectations remain reusable without treating the old
`ScreenFacadeAdapter::configure` transaction as product code.

`A10-RP02-O03` [ ] **PORT-008 transport oracles still need the non-release
closure.** Work 2.e must authenticate the actual P4 qualification compile/link
actions and Work 2.f must exercise retained-parser General Poll and Mode
Information output failure. Until both are accepted, the qualification boot
actor may link the old family to obtain a complete retained-parser closure.
PORT-008 must then move those transport/provenance checks to the selected
family or a display-independent harness and mark this item complete before the
old family can be removed.

`A10-RP02-O04` [x] **LCD has no retention claim.** LCD-001 explicitly consumes
the selected stock presentation path and records that it does not use the
retired `PresentationCompositor`. Historical LCD design evidence therefore does
not keep the old family buildable.

## Retirement contract

`A10-RP02-R01` [ ] Remove
`p4-port008-nonrelease-qualification` and its family declaration after all of
the following are true:

1. PORT-008 Work 2.e is accepted with current actual-action provenance.
2. PORT-008 Work 2.f is accepted with the required retained-parser fault
   injection, or the Author explicitly disposes that claim.
3. `A10-RP02-O03` is complete: every still-required transport/provenance oracle
   runs against the selected family or a display-independent harness.

`A10-RP02-R02` [ ] At that point, remove the old family source from maintained
build selections and ordinary regression discovery. Preserve accepted
PORT-003/PORT-008 evidence as frozen task history. Before deleting source,
recheck active includes and generated/profile authorities; archive source only
if an accepted task still requires byte-identical reproduction that Git and
frozen evidence cannot supply.

`A10-RP02-R03` [x] Until `A10-RP02-R01` is complete, the native manifest is the
enforced containment boundary: exactly one product owner exists, every
display-bearing profile selects one full family and forbids every other family,
and the non-release family names PORT-008 plus the three retirement gates.

## Regression manifest and evidence

| Check | Contract protected | Candidate result |
|---|---|---|
| `tests.native_p4_build_test` | One product owner; complete and mutually forbidden families; bounded non-release owner | PASS, 11 tests |
| Fresh `p4-console` native build | Declared/compiled/archived/linked selected family; alternate family absent | PASS, 33 selected and 11 forbidden sources; ELF SHA-256 `0e2723d5cd9ed3ef6d50274e5d200db3c92d27cbbb75b4a56217cd5e2ca951c7` |
| Fresh PORT-008 non-release native build | Declared/compiled/archived/linked old family; selected family absent | PASS, 28 selected and eight forbidden sources; ELF SHA-256 `ef4f6aa2a449064a73627ecde84ab3e222b9b498d3c8ae1d94ebefdf6ce62b4b` |
| PORT-003 selected stock runtime suite | Product native rows, scanlines, palette/Copper/decorators, lifecycle and snapshots | Not rerun: its frozen token verifier rejects the current `vgapalettedcontroller.cpp` before compilation. This is a stale historical-runner limit, not a product-test failure; prior 70/42/180 results are not claimed as current evidence. |
| PORT-003 independent mode-fixture tests and maintained console lifecycle | Reusable mode/lifecycle oracle remains independent of old family | PASS, four fixture tests plus one selected-facade lifecycle test |
| PORT-008 retained-parser source-contract tests | Qualification transport actor remains bounded and selected only in its profile | PASS, 13 tests |

Both native builds used unversioned, dirty-tree candidate identities rooted at
commit `f8cdd1ff`; neither is deployable evidence. Their common profile-manifest
SHA-256 is `a4c487bd1857db07936fa01c1183cea8c662b26d60e8a7a12591d2dfb8d4bdf4`.
The actual-action validators report each declared source compiled once into the
application archive and the archive present on the ELF link edge.

The stock runtime runner's failure is deliberately not bypassed. Its historical
token-provenance comparison admits only an older set of named binding changes,
while the current selected paletted-controller source contains later accepted
project adaptations. RP02 did not alter that source. A later repair that needs
those runtime cases must create or refresh a current-source regression owner
under that repair's explicit contract rather than weakening frozen provenance
or treating old-family tests as substitutes.

No physical build, flash, reset, SD mutation or target run is required or
authorized by RP02.
