# Displayed/drawing-page controls

## Executive summary

Author authorized execution on 2026-09-20. Complete the retained PAGE_FRONT and
PAGE_SWAP mode136 controls, using existing immutable fixtures and diagnostic
firmware. This is bounded pixel qualification, not a performance benchmark or
firmware repair. No Copper scenes, palette changes or bug fixes.

**QUAL-004-PC01** [ ] Verify exact fixture/firmware identities and diagnostic
capture semantics. Preserve actual mainboard flash and startup before mutation;
keep EMOS and P4 firmware unchanged. Record incoming input/display state.

**QUAL-004-PC02** [ ] Temporarily install and independently verify the existing
mainboard-image-capture-r02 diagnostic. Select mode136 for both routes only in
startup. Verify deployed player, scene and barrier hashes. Each mainboard scene
capture starts with a fresh ordinary mainboard reset; P4 starts from a known
clean palette state and each independent scene clears both pages. Stop on any
unexpected reset, incomplete capture or unsafe state; restore before reporting.

**QUAL-004-PC03** [ ] Capture each scene twice from mainboard, and obtain at least
two distinct matching P4 snapshot generations. Compare every pixel without masks
or tolerance. Independently check the literal red-front/green-swapped background
and white rectangle, rather than accepting two identically wrong pictures. Record
actual geometry from both endpoints. No new fixture changes to obtain a pass.

**QUAL-004-PC04** [ ] Restore exact original startup and overwritten mainboard
flash sectors, independently verify, close serial readers and video observer,
release keyboard and SD service, verify usable MOS prompt. Retain results and
report this scope only; other six deferred mode controls remain unqualified.

Prior procedure: [capture protocol](../PROCEDURE.md). Existing immutable
[scene generator](../prepare_modes.py), [scene identities](../fixtures/SCENES.json).
The historical runner has an expired absolute deadline; use a small task-local
adapter for these two cases, preserving decode/comparison and evidence rules.
No P4 flash/serial open is required solely to repeat old identity checks; retain
latest verified deployment plus current readiness, and disclose provenance limits.
No emulator or hardware notification requested. Freeze this contract before bench
mutation. New run IDs use QUAL-004 plus actual UTC start time; existing firmware
and fixture identities are reused without modification.
