# Parallel resumption results

## Executive summary

A clean matched format4 pair now builds with the current indexed display and
dual USB hosts. EMOS retains the reduced controller endpoint and has2,201 ROM
bytes free. Offline owner and linked-instruction checks pass. Physical transport
comparison and exact restoration remain pending; no speedup or production
qualification is claimed.

## Composed inputs and artifacts

| Component | Exact input/build | Result |
|---|---|---|
| P4 source | `03e428f3bb87951bd4f296ccb36ef677ef1db617`, based on installed R25 source `9c393360f8db0583e56f62c3266a6dad0090dda8` | Clean; only build wrapper changes in firmware source inventory |
| P4 image | `port-008-stream-r17-b2026-11-02-01-06-24Z` |1,828,032 bytes; SHA256 `4e2e5348cc798336d94fa1655b32de61b52a0ce55a86dc3024e01eed49f5a1aa` |
| EMOS source / builder | `0db7276f2a61031fce9b4bc9705b41e48ce0df47` / `49dc33fee817cb184572351ee71dae7da9a139c4` | Clean canonical source and existing AgonDev builder |
| EMOS image | `agon-emos-v0.1.27-b2026-11-02-01-06-34Z` |128,871 bytes;2,201 free of131,072; raw SHA256 `2f508d8e34b23ab09f7bc207cfbab6eca6ba0072f0a4ace2cff274c5e5482de3` |
| Padded EMOS ROM | Same build, erased padding | SHA256 `0a42af05e77ab335009f76e6e797a6279c9395c6323fae398dd6742f100acbf7` |
| Timing appliance | `port-008-stream-timing-r01-b2026-11-02-01-09-43Z` |13,386 bytes; SHA256 `b71f5ee5e7bf0de372cabc8fc7e63bc9f0f0e8b17be7befbbb4d834192745c40` |

The P4 image keeps the exact installed display sources/configuration, board,
compiler, cache component, USB options, reset-endpoint hash and dependency lock.
Only unrelated graphics timing is omitted and the native format4 transport is
selected. Partition-table bytes are identical. SDK configuration differs only
in absolute generated partition-file paths. Validation covers44 selected
sources and1,856 compile actions. This does not repair R25's known wide-mode
deadline failure; the comparison is limited to mode0.

EMOS's `exext-controller-timing.mk` composes the existing native/timing owner
with factored, unchanged controller selection/identity checks. Its reduced
controller gateway is the existing development operations4–7, not acceptance
of old on-card controller clients. No controller application belongs to this
transport workload. Both physical USB hosts remain selected in P4.

## Offline checks

1. Native P4 build selection:19 root tests and18 controlled-source tests pass,
   including dirty/wrong-owner/private-endpoint/wrong-identity refusals and
   preservation of display/controller sources in the composed profile.
2. Eight sanitizer-enabled host invocations pass: control, session, block
   control, ordinary stream, native paired coordinator, P4 coordinator,
   EMOS controller and EMOS ExExt stream. LeakSanitizer requires execution
   outside the ptrace sandbox; address/undefined-behavior checking remains on.
3. Exact newly linked EMOS instructions pass controller, UART observation,
   ordinary ExExt output and IRQ checks. The exact MOSlet/ROM ABI check passes
   empty drain, refusal, timer values and register/interrupt preservation.
4. Eight fixture evidence-interpretation checks pass. Full EMOS wrapper checks
   retain physical ROM bounds, UART divisor, ABI, keyboard/callback, ordinary
   console and RST10/RST18 dispatch guards. Full P4 graph validation passes.
5. AgonDev clang15 cannot lower SJLJ exception contexts. The appliance builder
   now explicitly disables exceptions; ordinary return-path cursor cleanup
   then compiles and links. The compiler failure remains retained as a bounded
   toolchain gotcha, not a firmware or bench failure.

## Preparation and remaining boundary

The initial live CLI/startup/read/EXIT proof passed twice. Support files were
staged and completely read back under the current SD layout. The first ROM
SAVE did complete correctly, but immediately injected listener input did not
establish service handback. One ordinary Agon reset restored admission. Fresh
evidence capture now uses a separately staged, explicitly invoked finite EXEC
file: MOS finishes SAVE before entering the listener. Startup is never edited.
This preparation correction makes no parallel performance claim.

The resumption contract governs matched installation, new full-ROM readback,
the eight-case four-length comparison and exact incoming-pair restoration.
P4 and EMOS require matching boot fencing: observe the exact new EMOS identity
after FLASH before holding Agon for P4 replacement; verify both installed
components and actual CLI before any timing invocation. Never infer FLASH
completion from a timer. No comparison case has been invoked at this checkpoint.

Ignored `agents/parallel-resumption` retains build requests/logs, manifests,
exact images/ELFs, source inventories, offline results, staged-file proofs and
the inspected finite helpers. These are experimental evidence, not a selected
installation, canonical qualification, general-purpose runner or new public API.
