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

## Exact-composition preflight correction

The r17 build passes target validation but differs from the accepted composition
in sw-visible-snapshot and overlay-BGR options. Offline comparison rejects it
before any installation. Candidate r18 uses the same c5046ff4 source patch with
both accepted options restored; verify complete source inventory, SDK, compiler,
board, dependency and flash-layout agreement again. No firmware changed during
this build-configuration correction. Preserve r17 as uninstalled build evidence.
The old directRGB888 lifecycle harness compile failure also exists on the exact
accepted baseline and is not a result of this repair.

The r18 comparison also rejects the accidentally selected optional320 scaler:
accepted r16 does not compile that option. Candidate r19 removes it. A pure
precompile comparison now proves the entire generated component CMake (source
list, includes, compile definitions/options, dependencies and embeds) matches
r16 after only exact source/output-prefix normalization; display configuration
also matches. Repeat the existing finished-build proof. Neither rejected build
has been installed; the bench still runs accepted r16.

## Installed repair and targeted result — 2026-10-31

The [portable result](MODE3-REPAIR-RESULT.json) binds installed r19 to clean
source c5046ff4def448807edb3864aafc912955bfcd65, based on accepted r16 source
5f8ef676e3cf4982d009f1fd6a0f00887be34198. Maintained integration is2e9eb7f0;
only `vdp/video/agon_screen.h` differs across5533 inventoried source files.
Generated component definitions/source selection, display settings, compiler,
dependency lock, board/reset configuration and partition bytes match r16.
Two SDK entries relocate the identical partition CSV to the clean checkout;
no other configuration difference is admitted. The finished target validates.

The Pi independently reads/verifies the entire incoming P4 flash, retains
application-sector rollback, writes only the r19 application at0x20000, then
reads all16MiB again. Application1786080B SHA-256
`536229a7661eed67a4f72256019e93a4547328858edaa14edeb8ff61be9a83e0`
matches; every byte outside the written erase sectors is unchanged. P4 startup
identity, direct USB keyboard and hub-connected F310 initialize cleanly before
the Pi releases the Agon reset hold. Two actual listener/read/EXIT exchanges
verify the MOS CLI and unchanged108B normal startup. No EMOS/mainboard flash.

The Author's minimal96→3/clear/text and Legacy→ExCom round trip now passes
with fresh prompts and advancing DMA. A separate16-case run passes in445.36
host-monotonic seconds, including preparation, retrieval and cleanup:

| Origin →3→origin | Passed / run | Highest refill counter observed in mode3, µs |
|---|---:|---:|
|96 →3→96|10/10|1276|
|0 →3→0|3/3|1246|
|20 →3→20|3/3|1104|

Order is worst observed refill first. These are cumulative carrier-lifetime
counters sampled in mode3, potentially including earlier work; they are not
isolated scroll/render timing or comparable throughput results. All112 retained
mode3 status samples report zero faults, with an unchanged1600µs guard. Each
case includes clear,64 lines of scrolling text, completion prompt and idle DMA
progress. Both entry modes0, Legacy CLI, startup and exact owned-file cleanup
are verified; cursor show/flashing commands execute on both displays.

The physical comparison supports the missing early worker join as the cause
of the reproduced overlap fault. It does not isolate each contributor to memory
or interrupt latency, qualify every mode, or test recovery after a deliberately
injected scanout abort. Mode-transaction sanitizer and actual service scheduling
checks pass. The older directRGB888 lifecycle stub fails to compile on the
unchanged accepted baseline too and is not reported as a passing check.

Complete canonical paired qualification also passes25/25 against this exact
installed application and unchanged EMOSv27; see the
[paired report](../RELEASE-001/QUALIFICATION-R19.json). Host job349.18s includes
114.43s preparation,68.77s integrated checks,71.43s mode checks,29.54s raw SD,
16.67s initial restoration and22.82s notification; total also includes final
verification/cleanup. These are operational host times, not rendering metrics.
The raw fixture uses representative native mode20; the separate16-case
regression above directly qualifies the repaired mode3 path. Raw sector2
write/read, restoration and independent restore verification all return0.
Startup is unchanged and temporary support cleanup is verified.

The final read-only handback observes18 DMA frames over at least0.3s, zero
faults, neutral admitted keyboard, valid USB F310 and listener offline. Both
entry modes0 and Legacy CLI are restored; cursor show/flashing commands execute
on both displays and after the completion player. No active runner, serial
reader or reset hold remains. Actual Author visual review, candidate acceptance
and release-selection/tag decisions remain separate. Preserve the accepted
r16 bundle and all old reports; r19 is not silently substituted into them.
