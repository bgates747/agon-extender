# AUDIT-008 — Where EMOS can recover ROM

This is the frozen research report. Subsequent implementation measurements and
validation are recorded in [IMPLEMENTATION.md](IMPLEMENTATION.md).

## Executive summary

The fresh ordinary EMOS build confirms **16 bytes free out of 128 KiB**. The
best first saving is not relocating the SD listener—it already lives on SD—but
reviewing removal of the cancelled transient-provider machinery still linked
into ROM. Eleven identifiable functions occupy **6,052 code bytes**, before
associated CLI branches and strings; its registry also occupies **3,154 RAM
bytes**. Retiring this machinery and adding a small stock-format EMOSlet launcher
has a planning estimate of roughly **5 KiB net ROM recovery**, not a measured
post-change result.

The old UART diagnostic objects occupy another **4,948 ROM bytes**, but they are
not drop-in MOSlets: private nonblocking UART/RTS interfaces and an application
text-test service complicate extraction. Do not create a new general transport
API merely to move these tests. Keyboard reception, display routing, mode
commitment and the SD transport's interrupt-side mailbox must remain resident.

**Recommended first tranche:** reconcile and retire the cancelled external
`.emo` provider path, preserve the resident gateway and operational services,
and add explicit `/emos` MOSlet loading. Initially use the already tested
`sdserve` MOSlet to validate that launcher. This is a proposal for A08-08/A08-09,
not an implemented change. A08-01–A08-07 research is complete; Author approval
of the retirement and launcher is the remaining gate. No new subtasks were added.

## Scope and evidence

The Author approved a maximum one-hour autonomous investigation on 2026-09-23
(local date). Existing dirt was committed first as `8ea1908d`. This run used an
isolated build checkout and unchanged project-owned EMOS source. It did not
flash, reset, change SD contents, launch an emulator, modify product code or
run the conditional implementation/validation items.

1. [BASELINE.json](BASELINE.json): reconciled linked section/object accounting,
   binary/map/ELF hashes and build identity.
2. [OBJECTS.csv](OBJECTS.csv), [FUNCTIONS.csv](FUNCTIONS.csv), [MOS.map](MOS.map):
   exact attribution; function costs are code only, object costs include constants
   and initializers. Neither is automatically a deletion saving.
3. [SOURCES.json](SOURCES.json): pinned inputs, tool versions/hashes, commands,
   source hashes and completed checks. [account.py](account.py) reproduces the
   read-only accounting from a completed canonical build.
4. Existing research: [EMOS E02 memory accounting](../../../../agon-emos/docs/tasks/INTEG-014/E02.md)
   and [E03 source reuse](../../../../agon-emos/docs/tasks/INTEG-014/E03.md).
   These already identified the large command/module and diagnostic objects;
   this review refreshes the baseline and evaluates the resident/SD split.
5. Official documentation was read first: [executables](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/Executables.md),
   [path variables](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/System-Variables.md),
   [RunBin](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/Star-Commands.md#runbin),
   and [UART APIs](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#0x15-mos_uopen).
   Official MOS is clean at tag v3.0.2, `8336409`; remote tag listing agrees.
   No official checkout was edited.

## A08-01 — Current ROM baseline

Fresh unchanged-source build: `agon-emos-v0.1.18-b2026-09-24-01-29-36Z`, draft,
from EMOS `f047b6a652eb3dd7c3ca2645f044536b054a0fdc`, ordinary
`port/mos-agondev.mk`. AgonDev port `90034c2348761c42bab4217ce5b0f906922dc0e4`;
Clang 15.0.7 (Agon LLVM `c76386c`), GNU binutils/ld 2.45. Exact tool executable
hashes and full commands are recorded in SOURCES.json. Compiler optimization is
`-Oz`; this is not a new ZDS build or a measurement of installed hardware.

| Resource | Current measured bytes | Capacity / interpretation |
|---|---:|---|
| ROM occupied | 131,056 | 99.9878% of 131,072 |
| ROM free | **16** | **0.0122%** |
| Static MOS RAM | 6,826 | Initialized data, BSS, writable vectors |
| MOS heap arena | 7,510 | Capacity before metadata/live allocations |
| MOS stack reservation | 2,048 | Linker convention, not measured high-water |

| Flash component | Bytes |
|---|---:|
| Main code | 109,480 |
| Constants | 12,693 |
| Startup/assembly | 7,591 |
| Initialized-data image | 748 |
| Interrupt vectors | 288 |
| Reset code | 107 |
| Descriptor/reset slot | 149 |
| **Total** | **131,056** |

There are 70 fill bytes inside the fixed reset slot, not free allocatable tail
space. BSS contributes RAM, not ROM. `.data` costs space in both budgets. The
image end, section sum and binary file size agree. The earlier provisional
MOSlet record's 131,056-byte result is reproduced in size; this does not assert
byte identity across build-date strings or installed firmware provenance.

The canonical wrapper passed prepared-source provenance, restricted-runtime,
linker layout (including five rejection cases), complete resolved-image and
profile checks for UART divisor, parallel, keyboard and console; the EMOS ABI
and VDU dispatch checks also passed. No broad host-test or runtime pass is inferred.
The isolated checkout initially lacked required toolchain/venv links; those local
setup omissions were corrected before the successful fresh build.

Linking does **not** use `--gc-sections`; the firmware explicitly links whole C
objects and collects `.text`/`.rodata`. Removing one CLI reference alone does not
prove its externally visible function disappeared. The compiler inlines several
private helpers into `emos_cmd`/`emos_discover`. Their source sizes cannot be
summed again. Stock `printf`, FatFS and runtime helpers remain used elsewhere:
none of their shared cost is counted as a prospective saving here.

## A08-02 / A08-03 — Inventory and residency

Rows are ordered approximately by ROM opportunity; overlapping rows are marked.
All costs are from the current map, not line counts or new extraction builds.

| Code / entry points | ROM attribution | Callers, state and lifetime | Disposition |
|---|---:|---|---|
| External `.emo` discovery/validation/load/invoke/swap/fallback cluster | 6,052 code bytes; subset of 13,053-byte `emos.o` | `EMOS DISCOVER/CLEAR`, unknown-command fallback, generic gateway fallback; registry and synchronous module-area replacement | Best retirement candidate, subject to explicit compatibility disposition below |
| `emos_cmd`, including status, parsing and inlined helper code | 3,580 code bytes; overlapping `emos.o` | CLI and application `mos_oscli`; some commands initiate resident transitions | Split by operation, not a wholesale MOSlet conversion |
| UART probe/text object | 3,217 incl. constants | `UARTTEST`, `VDPPOLL`, `VDPTEXT`; also resident `edu.text-probe` gateway called by SD applications | Mixed: old frontend/test logic could move, text gateway and private transport dependencies must be addressed |
| Parallel binding/engine/assembly | 3,059 incl. constants | RST dispatch, explicit route lifecycle, public UART1 guard; state/locking persist across calls | Resident while supported. Not an EMOSlet candidate; deferred functionality is not proof of dead code |
| Keyboard C and assembly objects | 3,476 | UART IRQ, VBlank tick, callbacks, source/layout selection; retained key state | Must remain resident |
| Console C and assembly objects | 1,950 | VDU output, reply IRQ, mode transactions, retained lease/sysvars | Must remain resident |
| UARTFLOW object | 1,731 incl. constants; 10 static RAM bytes | One CLI diagnostic; private nonblocking TX/RX, RTS claim/control, timer/failure state | Foreground in principle; ABI work makes immediate extraction unattractive |
| SD transport | 685; 486 static RAM bytes | Resident gateway, UART ISR mailbox, application enter/leave reset | Must remain resident. SD filesystem/protocol logic is already in sdserve |
| Bench telemetry object, ordinary profile | **0** | Preprocessor excludes implementation | No ordinary-ROM saving; do not advertise removal as optimization |
| Firmware identity, essential errors, keyinput and mode coordinator | Within shared `emos.o` | Boot, recovery, CLI/app mode request | Retain a useful no-SD control/recovery path |
| Installer/bootstrap tools | No dedicated installer object found in selected EMOS profile | Maintained host/SD tools | No demonstrated resident candidate to extract |

Every current EMOS subcommand is accounted for:

| Command | Proposed treatment |
|---|---|
| Bare `emos`, `status` | Keep essential identity/current-state reporting resident for the first tranche; rich registry listing becomes irrelevant only after retirement approval |
| `keyinput mainboard|browser|extender` | Keep parsing and resident receiver/source control; do not make recovery depend on SD |
| `excom`, `legacy`, `mode` | Keep resident coordinator and admission, including application `--keep-display` behavior |
| `fake` | Test-only seam in the existing mode coordinator; leave unchanged in first tranche, not an independent relocation saving |
| `discover`, `clear` | Retire external-provider semantics only if Author accepts that compatibility change |
| `call` | Generic request construction is inlined in `emos_cmd`; retain resident-service uses initially, reject retired external providers deterministically |
| `uarttest`, `vdppoll`, `vdptext`, `uartflow` | Leave unchanged in proposed first tranche; foreground eligibility alone is insufficient to move them safely |

### Cancelled design versus retained implementation

[SETUP-005](../SETUP-005.md#implementation-strategy--resident-emos) and the
[EMOS MOS-001 disposition](../../../../agon-emos/docs/tasks/MOS-001.md) explicitly
cancel the generic module development path. However, `emos.c` still implements
`.emo` containers, `EMOS$Path`, discovery, CRC validation, provider dispatch and
32 KiB swap/restore. The older [EMOS v1 provisional contract](../../../../agon-emos/docs/emos-v1-contract.md)
still describes that behavior. Cancellation did not remove the linked code.
This is a documentation/compatibility discrepancy, not permission to silently
remove observable behavior.

The exact 6,052-byte cluster is:

| Function | Code bytes |
|---|---:|
| `emos_discover` (includes inlined file-validation work) | 2,588 |
| `emos_invoke` | 1,379 |
| `emos_validate_header` | 891 |
| `emos_preserve_module_area` | 348 |
| `emos_dispatch_command` | 312 |
| `emos_crc32_update` | 144 |
| `emos_find` | 125 |
| `emos_read32` | 104 |
| `emos_entry_compare` | 72 |
| `emos_clear` | 66 |
| `emos_scrub_module_area` | 23 |
| **Non-overlapping code total** | **6,052** |

These functions are exclusively or principally associated with the external
provider path. `scrub_module_area` also appears in failed-provider recovery on
application exit, so removal must remove that obsolete caller together, not
leave a broken branch. Shared request identity/range validation, `emosBusy`, mode
policy and application lifecycle hooks still serve resident facilities and
must not be deleted as a block. The 3,154-byte registry is a separate RAM saving;
stack/heap preservation-file buffers are not all persistent allocations.

Known module consumers include the old provider fixture builder/runtime checks.
Current sdserve, browser typing and text sample call the resident gateway, so
that gateway, its API 0x51 / C slot 0x20 and reserved provider names must survive.
No SD inspection was performed: there is no claim that the user has zero external
`.emo` consumers. Unknown providers would cease to work after retirement.
Preserve the old firmware/evidence and report an unavailable/not-found status;
never silently reinterpret a `.emo` container as a MOSlet `.bin`.

## A08-04 — Minimal launcher proposal

The simplest safe implementation uses the **existing load and execution helpers
with an explicit MOSlet address**, not a new loader/container or a call to the
CLI with an assembled command string.

1. Resident built-ins retain precedence and existing semantics. Only an
   unmatched, exact EMOS subcommand becomes a `/emos` lookup. Use a proposed
   1–24-character leaf name of letters, digits, `_` or `-`, normalized to
   lowercase; no slash, dot, wildcard, variable expansion or path traversal.
   `/emos/` + leaf + `.bin` + NUL needs at most 35 bytes. These are proposed
   command limits, not current behavior or a stock MOS requirement.
2. Resident EMOS permits loading only from the idle/Core CLI context, including
   ordinary autoexec execution. An application or another MOSlet cannot invoke
   a disk EMOSlet recursively and overwrite its own slot/stack. Existing resident
   mode calls via `mos_oscli` retain their current supported behavior.
3. Form `/emos/<name>.bin`, check file size is at least the basic 69-byte header
   extent and no more than 32 KiB, then use stock `mos_LOAD` at `0x0B0000` and
   `mos_runBin` for header checking, register ABI and application enter/leave.
   The general stock load bound is MOS system RAM at `0xBC000`; **that is not
   the stricter `0xB8000` EMOSlet limit**. Do not pass a 32 KiB truncation limit
   and then run a truncated oversized file.
4. Preserve the remaining argument string and stock numeric return code. Missing
   card, file, OOM and invalid executable errors use existing MOS reporting.
   On failure do not execute stale slot contents; invalidate the old header
   before a permitted load. A basic MOS header does not authenticate content
   or encode required EMOS version: syntactically valid but corrupted programs
   retain stock executable limitations, not an invented integrity guarantee.
5. Keep `Moslet$Path` and global `Run$Path` unchanged. Stock `mos_runBinFile`
   selects `0xB0000` only when `isMoslet` matches the directory against
   `Moslet$Path`; calling it naively for `/emos/foo.bin` selects application RAM
   at `0x40000`. Adding `/emos` globally would also make bare command lookup
   find these utilities, contrary to the desired explicit prefix separation.
6. Do not create a service registry or resident per-utility callbacks. Each
   utility links for the stock MOSlet address, executes synchronously, cleans
   up, and returns. Ordinary `emos legacy` and `emos keyinput mainboard` must
   remain available when the SD card/utility is absent.

Estimated resident addition: **500–900 ROM bytes** for dispatch/name/path/bounds
and context checks using already-linked helpers. This is a conservative planning
allowance, not compiled prototype evidence. Keep a further **0–200-byte** allowance
for deterministic retired-provider stubs. Implementing an extraction solely to
measure it would cross A08-07's approval gate, so no such prototype was made.

## A08-05 — RAM, ABI and lifecycle feasibility

| Concern | Finding / required boundary |
|---|---|
| Fixed load region | MOSlets use `0xB0000`–`0xB7FFF`, including code/data/BSS/heap/stack; file length alone is insufficient |
| Existing sdserve evidence | 18,987-byte file, static end `0xB5333`, 11,469 bytes remaining to `0xB8000`; not measured peak runtime headroom |
| C runtime | Inspected AgonDev CRT saves caller SP/registers, switches to linker `__stack`, initializes its own BSS/heap/stdio, restores caller on exit. Utilities must use their own linked runtime state, not private resident C globals |
| Loaded application | Normal application RAM below the MOSlet slot is preserved by placement; arbitrary programs using MOSlet space are not protected by magic. Reject nested disk launch; do not revive disk swapping |
| Resident SD API | Existing narrow gateway accepts MOSlet request/input/output memory for `ext.sdlink`. Other providers retain exclusion. Expanding eligibility globally is not part of the launcher |
| Diagnostic APIs | `edu.text-probe` still requires ordinary application RAM; UART tests call private driver helpers. Merely relinking them at B0000 does not satisfy the API contract |
| Callbacks / interrupts | No utility pointer may remain in a vector, callback, resident queue or active request after return. Resident IRQ mailbox must copy transient data as sdlink already does |
| Service lifetime | `mos_runBin` invokes EMOS enter/leave hooks, including sdlink reset; preserve them. sdserve remains foreground and does not become a background server |
| Compatibility | Keep resident gateway ABI 1 and existing slots. sdserve uses that contract; unsupported firmware must return a clear error before transfer. A future utility requiring a new resident operation needs explicit capability/version admission, not an assumption that all EMOS v0.1.x images support it |
| Update/recovery | Keep existing `/mos/sdserve.bin` and ordinary `/extender/sdserve.bin` fallback during launcher validation; deploying a new `/emos/sdserve.bin` does not require deleting either. Stage/read back replacement, preserve rollback, and never overwrite a running protected utility |

The SDK linker uses the same upper bound for stack and heap; the remaining
space is shared, not two separate allowances. The saved MOSlet acceptance proves
a 4 KiB application sentinel and small transfers, not full RAM preservation or
stack high-water. New extractions need their own map/runtime checks under A08-09.

## A08-06 — Ranked savings and recommendation

Ranking is estimated safe benefit versus added mechanism, not byte count alone.
Rows overlap where indicated and must not be added into a grand total.

| Rank | Candidate | Measured containing cost | Retained portion / new cost | Estimated net ROM and RAM effect | Recommendation |
|---|---|---:|---|---|---|
| 1 | Retire cancelled provider cluster + minimal launcher | 6,052 distinct code bytes; extra CLI/constants uncounted | Keep resident gateway, services, validation and lifecycle. Budget 500–900 launcher + 0–200 stub bytes | **4,952–5,552 ROM bytes recovered**, plus 3,154 registry RAM bytes; added utility RAM is separate | First bounded proposal; needs retirement approval |
| 2 | UARTFLOW MOSlet | 1,731 ROM, 10 RAM bytes | Private nonblocking UART/RTS ownership cannot disappear; adapter cost not determined | At most containing ROM; **no defensible net estimate yet** without selecting API vs test-only firmware composition | Defer extraction; keep old fixture available |
| 3 | UART probe/text utilities | 3,217 ROM | Keep `edu.text-probe`, text validation/exchange and shared clock helper; 4,948 total with UARTFLOW is not all removable | UARTTEST + VDPPOLL functions alone are 1,093 code bytes; excludes strings and new admission cost | Possible later frontend split, not first tranche |
| 4 | Rich status/help and generic CALL frontend | Overlaps 3,580-byte `emos_cmd` and 1,056-byte constants section | Keep no-SD identity/errors/mode/key commands; would need a resident query/service interface | Unmeasured; moving text without deleting resident copy saves nothing | Prefer modest static simplification after retirement over a new introspection framework |
| 5 | External discovery as a MOSlet while retaining providers | 2,588 code bytes, overlaps rank 1 | Registry mutation/validation API and runtime loader remain | Below gross cost, unknown net | Inferior to retirement if that path is truly cancelled |
| Exclude | Keyboard, console, SD IRQ transport, active parallel ownership | See inventory | Required resident services/guards | No proposed recovery | Leave resident |
| Exclude | Existing sdserve or excluded telemetry | 0 extractable ordinary-ROM bytes | Disk file / uncompiled feature already | **0** | Do not count as savings |

The rank-1 planning envelope yields **4,968–5,568 bytes total free ROM**, or
**3.79–4.25% of 128 KiB**, against the measured 16-byte / 0.0122% baseline.
Those numbers deliberately credit only the named 6,052-byte cluster and charge
new code allowances; actual link effects, retained stubs, CLI edits and strings
can change them. They are not a before/after qualification. A useful first-tranche
acceptance target is **at least 4,096 net bytes recovered**, verified by a full
link without weakening required behavior; otherwise return for review.

## A08-07 — First implementation contract proposed for approval

This is the proposed scope of the existing A08-08/A08-09, not additional work IDs.

**Resident EMOS changes:** modify `src/emos.c`, `src/emos.h` and the relevant
`src/mos.c` command-fallback/default-variable/help references in agon-emos.
Remove external provider discovery/container verification/invocation/swap only
after reconciling the cancelled-task decision with the provisional v1 contract.
Keep API 0x51/C slot 0x20, ext.sdlink and text-probe services, caller validation,
mode/input controls, transport ownership and enter/leave cleanup. Do not replace
the generic loader with another registry. Removed provider commands return
existing deterministic errors and their old fixtures become historical controls.
No broad ABI renumbering, telemetry or parallel removal.

**SD-side change:** add the fixed-address `/emos` launcher described above and
validate it using the existing sdserve MOSlet. Keep its canonical basename for
self-write protection. No filesystem protocol changes, new utility format or
change to stock `/mos` search. Only after acceptance promote `/emos` from proposed
to supported in SD layout/install documentation. Firmware and file placement
must be tracked together; old listener entry paths stay available for rollback.

**Validation:** exact before/after map accounting; all required firmware/profile
link checks; deterministic retired-provider errors; intact resident gateway and
operational services; case/argument/return behavior; missing/card/file/header/
size errors; nested-launch rejection; loaded-application sentinel and MOSlet
stack/BSS bounds; repeated listener transfer/exit; affected Legacy/ExCom and
mainboard/Extender input behavior. Preserve existing fixture identities and
obtain candidate identities under the standing version policy before deployment.
Use focused emulator checks and Author review before physical installation.
No performance or whole-memory pass is inferred from compilation.

**Rollback:** retain prior ROM, source/build identity and utility set. If the
new SD path fails, ordinary resident recovery commands and existing listener
paths remain usable. Do not migrate/delete unknown `.emo` files or the old
swap artifact from a card automatically. Historical root-writing module fixtures
are evidence, not deployment instructions under the current SD layout policy.

**Decision for the Author:** approve retirement of the external provider system
and this minimal launcher as the first tranche, or retain that compatibility and
accept that the large saving requires a different plan. There is no unanswered
question blocking the completed source investigation itself.
