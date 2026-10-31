# Mode96-to-mode3 repair plan and research

The Author directs the agent to fix the independently reproduced mode96→3
scanout abort. Change only the P4 lifecycle, preserve the accepted r16 rollback,
and prove the failed path before complete paired qualification. Do not loosen
the1600µs guard or add processor-link integrity work. EMOS, mainboard VDP and
normal startup remain unchanged. Actual visual acceptance remains separate.

## Bounded contracts and source

1. Official [VDU22](../../../../../agon-docs/docs/vdp/VDU-Commands.md) selects
   the requested logical mode. Baseline docs f9806bd3cbff6ed5d1c08bef1d51fed11764b86b;
   read-only source baselines VDP v2.16.0 c7ac293d2aa81ddfa693390549bcd909069c8fc3
   and MOS v3.0.2 8336409351ee5314e02801a7b72a4f1bb5282519 remain unchanged.
2. [P4 mode replacement](../../../vdp/video/agon_screen.h), function
   changeResolution, prepares candidate resources before no-fail commit. Its
   early drawing/output join was conditional on the target sharing panel pixels.
   Target mode3 does not satisfy that condition; old mode96 indexed/PPA output
   can overlap native allocation/initialization on the unchanged848×480 carrier.
3. [Service detach](../../../vdp/video/extender/display/stock_p4_service.cpp)
   unbinds callbacks, signals cancellation, joins drawing/output and drains the
   native queue outside native exclusion. Reuse it; do not add a new control
   protocol or change normal rendering/USB/controller service semantics.
4. [Mode transaction](../../../vdp/video/extender/display/mode_transaction.hpp)
   preserves fallible preparation and allocation-free commit. On preparation
   failure, release candidate resources before rebinding/reattaching the old
   service. Retain official old/default-mode fallback.
5. [Rolling deadline](../../../vdp/video/extender/display/rolling/strip_runtime.inc)
   includes queue wait, copy, composition and cache handoff; preserve the1600µs
   gate, independent generation checks and acknowledged buffer lifetime rules.

## Work and gates

1. Implement early join for every direct/indexed HDMI candidate, not just a
   target which borrows panel pixels. Run existing preparation-failure/commit,
   HDMI scheduling and service-lifetime host checks. Keep the first candidate
   hypothesis explicit until physical comparison succeeds.
2. Freeze indexed-hdmi-r17 with the exact accepted r16 composition/toolchain,
   dependency lock, USB1.6.0/map3 and private reset endpoint. Use a clean source
   snapshot so unrelated recovery-document work is preserved. Verify compiled
   inputs and retain the old application and complete incoming flash before
   writing only application sectors. Independently compare readback and all
   bytes outside the written sectors before execution; maintain Agon reset hold
   during P4 installation. No EMOS/mainboard/startup write.
3. At actual CLI with unchanged startup, invoke at least ten96→3 transitions
   and both0/20 controls, including clear, text scrolling and mode return.
   Require fresh DMA progress/zero faults after selection and workload, visible
   cursor commands and actual CLI recovery. Preserve a first failure before
   standing recovery; never retry a raw operation or weaken guards.
4. If the candidate fails, retain it as rejected evidence, restore the exact
   accepted bytes as needed and refine the owner/lifetime fix. Do not call a
   build or source hypothesis a completed repair. Further candidates require
   new immutable identities and the same gates.
5. On a passing targeted candidate, run the complete canonical25-check native
   paired suite with its matched installation receipt, ordinary startup and
   full cleanup/notification. Preserve manual-review and release-selection/tag
   boundaries; successful tests do not fabricate Author acceptance.

No firmware has been installed by writing this plan. The first candidate joins
old workers earlier; whether that removes the observed deadline overrun must be
established on hardware.

## Controlled source baseline clarification

The maintained checkout contains committed display/diagnostic changes beyond
accepted r16. Only agon_screen.h's early-join patch will be applied to a clean
clone at the exact accepted5f8ef676e3cf4982d009f1fd6a0f00887be34198 source.
Keep those unrelated maintained changes and current recovery-document dirt
intact. The candidate's source commit is a separate codex branch based on r16;
record both its identity and the maintained integration commit. Build every
component and use the exact original dependency lock/recipe.

Current maintained mode-transaction ASan/UBSan checks (2) and actual service
scheduling pass. Its separate old directRGB888 lifecycle harness does not compile
against the later committed bridge types; that failure is not caused by the
agon_screen.h-only patch. Re-evaluate applicable host checks on the controlled
accepted source; full target compile and physical regression remain mandatory.
