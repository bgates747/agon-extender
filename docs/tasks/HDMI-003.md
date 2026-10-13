# HDMI-003 — Diagnose and correct low-resolution HDMI aspect

## Executive summary

The Author reports vertical squashing during the five-mode rendering smokes.
Retained mode-3 evidence shows a 640×240 logical image in a 684×384 HDMI carrier;
the selected P4 scanout code centers logical pixels without vertical expansion.
This is a plausible explanation, not yet a conclusively reproduced visual
root cause. Establish the expected stock presentation and distinguish fixture
geometry, P4 output mapping and monitor interpretation before repairing the
responsible layer. The Author authorized this task and requested a commit/push
checkpoint before execution on 2026-10-13.

**State:** authorized; initial evidence retained; diagnosis and correction pending.
The [multimode campaign](RESEARCH-007/MULTIMODE-QUALIFICATION-R01.md) stays stopped.
Sixteen RGB888 short receipts in modes 0/3 establish data validity only; the
240-measurement campaign has never started.

## Scope and ownership

1. The host records exact installed P4 bytes, selected source/options, logical
   mode, output carrier and fixture identity using the ignored local bench
   records. Preserve the frozen renderer pair and all informative failures.
2. P4 HDMI presentation owns any confirmed output-coordinate or aspect repair.
   Apply equivalent presentation behavior to optimized RGB888 and indexed/PPA
   variants. EMOS continues to own ordinary VDU routing and mode admission.
3. Keep stock mode IDs, logical dimensions, drawing/readback coordinates,
   clipping and double-buffer semantics unchanged. Do not distort benchmark
   workloads or game assets to hide an output defect.
4. Use the maintained P4 source in a separate project-owned checkout. Leave
   the frozen comparison checkout, official references, EMOS, onboard VDP,
   wiring, NVS, production selection and accepted archives untouched.
5. Reuse proven physical carriers. A new physical timing or broad renderer
   optimization needs a separately recorded decision; neither is implied here.
6. Bounded diagnostic fixture preparation and necessary matched candidate
   build/deployment checks belong to this task. Explicit Author visual review
   is required before claiming the visible issue corrected. No full benchmark
   campaign may start as part of this task.

## Evidence and bounded research

1. Origin: the Author's report during RGB888 mode-3 smokes, 2026-10-13.
   The host stopped the controller and pending mode-8 preparation before its
   reset or invocation, then restored ordinary keyboard-only startup with
   complete readback and actual listener EXIT. The bench remains in Legacy;
   exact current state and evidence locations are in `HARDWARE.local.md`.
2. Confirmed retained metadata: mode 3, 640×240 logical pixels, 684×384 HDMI
   output. Source at `e26c24f743b9b94efa05eac46f2f237689ac3b5b`:
   `vdp/video/extender/display/rolling/scene.hpp`, `Scene::reset`, computes
   centered offsets; `rolling/scene.cpp` forwards source dimensions to scanout.
   Inspect the actual row-copy/expansion and bridge metadata before asserting
   what reaches the monitor. A centering helper alone does not establish the
   complete presentation transform.
3. Official first references: `agon-docs/docs/vdp/Screen-Modes.md` and
   `VDU-Commands.md`; the previously read documentation commit is
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`. Review stock low-resolution
   line/pixel repetition in official VDP source only where documentation is
   insufficient. Verify clean release baselines and record exact commits
   before relying on them. All official reference checkouts stay read-only.
4. [ADR-0024](../decisions/ADR-0024-centered-unscaled-hdmi.md) currently selects
   unscaled presentation by default and a separate 320×240 scaling exception.
   Therefore, do not classify the intentional default as a proven stock bug
   or silently replace the accepted presentation policy. A confirmed mode-3
   correction may require a narrowly scoped amendment.
5. Distinguish logical pixel aspect, displayed object aspect, HDMI active
   raster, HDMI aspect metadata and monitor scaling. Also distinguish Nurples
   derivative bounds/clipping from output distortion. Preserve source-linked
   conclusions and short relevant excerpts in this bounded research record.

## Instructions and gates

### H03-01 [ ] Establish the cause

1. Verify bench availability, installed bytes/source/options and stopped host
   controllers. Read the controlling operation procedures before hardware work.
2. Reconcile official mode-3 presentation with the selected P4 carrier,
   source-to-output row mapping, sprite/cursor mapping and bridge metadata.
3. Reuse or prepare a small labeled geometry fixture with known pixel/line
   spacing and declared expected physical proportions. Compare mode 0/3 and
   a relevant 320×240 control without changing logical drawing contracts.
4. Keep mode selection only in setup-only startup, ending in Legacy. Invoke
   diagnostics explicitly through one MOS command batch; no test autoexec.
5. Record what is source-proven, captured or Author-observed. Obtain the
   decisive visual/measurement evidence before declaring a root cause.

### H03-02 [ ] Correct the responsible layer

1. Implement the smallest supported correction after H03-01 identifies the
   cause. Use fresh experimental source/build identities and preserve rollback.
2. If P4 output mapping is responsible, apply the same policy to both renderer
   variants, including sprites/cursors and both logical banks. Keep rendering
   and output-conversion costs separately observable.
3. Cover row mapping, centering/bounds, output edge handling and logical bank
   publication with meaningful host checks. Reuse existing lifecycle and pixel
   tests rather than constructing implementation-mirroring tests.
4. Record any material accepted presentation decision in the decision register,
   corresponding ADR, architecture and dated log before claiming it normative.

### H03-03 [ ] Verify and hand back to benchmark preparation

1. Build fresh same-source RGB888/indexed variants with exact manifests and
   option parity. Independently verify installed non-NVS segments and real
   CLI/listener handback using the reviewed installer, adapted deliberately.
2. Run bounded geometry, output-error and mode-transition checks; verify both
   banks where applicable. Obtain Author visual confirmation of the correction.
3. Restore and read back ordinary keyboard-only startup. Leave Legacy mode,
   neutral input and documented CLI/service readiness. No unattended fixture
   or completion notification may imply the benchmark campaign has run.
4. Refresh comparison pins and affected smoke evidence; preserve predecessor
   package identities and results. The existing preparation task then owns the
   remaining 80-smoke admission and ready master plan, with an explicit stop
   before the 240-measurement campaign.
5. Tested acceptance follows project production/version/tag closeout rules;
   this task initiation is not production acceptance or a new version choice.

## Decision register

### H03-D01 — Presentation correction — diagnosis pending

1. Authorized objective: correct the Author-reported vertical squashing.
2. Candidate remedy: if stock mode-3 presentation requires repeated rows,
   P4 HDMI should perform equivalent output mapping in both renderer variants
   using an existing proven carrier, without changing logical VDU coordinates.
3. Alternatives depend on diagnosis: repair a fixture adaptation defect or
   incorrect HDMI metadata if either is responsible; retain centered unscaled
   behavior for unaffected modes. Do not select a global scaling policy by
   assumption.
4. Prerequisites: H03-01 evidence, exact source ownership and relevant current
   ADR contracts. Downstream effects may include new matched firmware pins,
   bounded visual qualification and invalidation of affected smoke admission.
5. The Author authorized investigation and correction, but no specific
   row-expansion algorithm or global architecture change has been accepted.
   Bring any remaining material policy choice to the Author one at a time.

## Dependencies and current limits

1. [Multimode qualification](RESEARCH-007/MULTIMODE-QUALIFICATION-R01.md):
   paused consumer of the eventual corrected pair.
2. [HDMI-002](HDMI-002.md): existing carrier/lifecycle evidence and source of
   the accepted 320×240 exception; historical recipes require current review.
3. [Building](../building.md), [installation](../installing.md),
   [test execution](../procedures/test-execution.md) and
   [bench constraints](../qualification/bench-constraints.md) govern execution.
4. No hardware reproduction, corrected firmware, visual acceptance or
   performance improvement is claimed at task creation.
