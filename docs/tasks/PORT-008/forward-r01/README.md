# PORT-008 forward-only r01 qualification package

This directory owns the deterministic build and evidence glue for the first
physical EMOS-to-EDP forward test. The task scope and decisions remain in
[`../../PORT-008.md`](../../PORT-008.md); the controlled execution is
[`../../../procedures/port-008-forward-qualification-r01.md`](../../../procedures/port-008-forward-qualification-r01.md).

## Authorities

1. `candidate.yaml` freezes the Author-approved artifact identities, external
   commits, fixture hashes, two-stage keyboardless media contract, and bounded
   claim.
2. `vdp/pio/p4-forward-vdp-identity.json` supplies the committed P4 source
   identity. The build system supplies a new UTC build ID.
3. `agon-emos` commit `0e24b06` supplies the corrected fixed-purpose EMOS
   profile and deterministic ordinary-VDU fixture. `mos-agondev` commit
   `29cd336` supplies the product-linked final-image gate which rejects the
   previously observed UART-divisor failure. The profile is explicitly a
   PORT-008 qualification workaround, not a production EMOS configuration.
4. `port-008-forward-r01` names the candidate combination. The first clean
   identified packages are P4 build
   `extender-vdp-v0.2.0-b2026-09-01-00-20-07Z` and EMOS build
   `agon-emos-v0.1.0-b2026-09-01-00-20-07Z`, both built from
   `agon-extender` commit `acf9ded`. Their full commits, hashes, outputs, and
   not-run physical status live in the generated adjacent manifests rather
   than being copied back into the candidate-input YAML.
5. MOS installation uses the official unmodified `agon-flash` v1.9 utility.
   Its standard `-f` switch is the complete keyboardless authorization
   mechanism; no custom or special flasher build is required.

## Generated outputs

Generated firmware, fixture binaries, closure evidence, and media trees are
ignored build products. Completed run manifests and bounded evidence belong in
tracked `tests/runs/<RUN-ID>/` directories. Scripts in `scripts/` must reject
dirty or mismatched source worktrees, rejected identity markers, changed
fixture bytes, and an existing destination rather than silently overwriting
evidence.

The task-local [post-run source snapshots](evidence/README.md) preserve the
exact current dirty deltas from `agon-extender` and `agon-emos` as historical
patch evidence. They are not maintained source, clean run provenance, or
permission to build, deploy, or promote the prototype.

The P4 validator deliberately extends the already-qualified PORT-003 Phase-F
closure validator. It changes the environment-specific expectation from the
disconnected Stream to `ForwardParallelStream`, requires the r01 startup and
discard-only diagnostic strings, and continues to enforce the same retained
VDP/browser closure and exclusions.

The task-local scripts have these bounded roles:

1. `validate-forward-build.py` reuses the PORT-003 closure audit while replacing
   only its ingress-specific assertions.
2. `stage-forward-build.py` reuses the clean-worktree and factory-segment
   stager while emitting a PORT-008 claim boundary.
3. `stage-emos-build.py` verifies the selected clean EMOS and `mos-agondev`
   commits, prepared-source provenance, embedded deployable identity, fixture
   bytes, and candidate authority before copying EMOS and fixture outputs into
   an ignored build-ID-specific package with adjacent manifests.
4. `capture-visible-frame.py` requests one established EVF1 browser frame,
   preserves its raw RGB888 payload, and compares it to the frozen exact hash.
   It neither sends VDU/EDU traffic nor records the supplied private endpoint.
5. `analyze-forward-capture.py` parses the Sigrok archive with the committed
   LA-03 mapping and applies only this procedure's forward-record, READY,
   CLOCK, and direction-ownership checks. It deliberately does not apply the
   predecessor bidirectional fixed-frame semantics. Its no-edge findings are
   bounded to the capture sample rate.

The browser's HTML load and its video connection are separate gates. A plain
HTTP 200 proves only that the page is served. Pressing Connect opens the
WebSocket and supplies frame credit. It does not arm the physical parallel
receiver, but it must occur before an Agon run whenever visible browser output
is part of the expected evidence.

## Normal wiring and probe reference

`normal-forward-wiring-and-probes.svg` is the task-local human reference for
the normal r01 forward wiring and canonical LA-03 probe placement.
It is generated from the retained `light2-harness-r01` legacy wiring drawing by
`scripts/generate-normal-forward-wiring-and-probes.py`, while its probe markers
follow `la03-p4-probe-fixture-r01`. The drawing shows the ordinary signal path,
including Agon PD4 to P4 GPIO20 for `READY_N`; like its source drawing, it does
not depict the intervening logic device and therefore does not replace the
electrical authority for that circuit.

## Media stages

The physical SD card has two deliberately distinct states:

1. **Install EMOS.** Root `/autoexec.txt` first renames `/emos.bin` and then
   invokes official `agon-flash` v1.9 with `-f`. The rename is a one-shot guard:
   after the utility resets the Agon, the first line fails and MOS stops before
   another flash. The utility and `-f` behavior are standard; using a temporary
   autoexec file is the BC-001 bench workaround, not a production installation
   interface.
2. **Run the fixture.** After power-down and host-side hash verification,
   `/autoexec.txt` is replaced with the accepted two-line mode request and
   fixture invocation. The P4 and browser must be ready before the Agon cold
   boot begins.

Neither stage may be installed until the Author reviews the generated build
manifests, exact card target, preflight, and procedure and separately authorizes
that physical mutation.
