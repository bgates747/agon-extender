# EMOS migration — reuse and readiness tranche

The next tranche reuses Extender's maintained regression tests and UART's frozen
RC2 appliances against the exact installed EMOS candidate. Preserve their
assertions and evidence. Adapt only source selection, native host-I/O seams,
exact-ROM fixture binding and the current appliance lifecycle. Stop before the
full suite starts and report readiness to the Author. No firmware replacement,
startup change, emulator launch or production promotion belongs to this tranche.

## Scope and fixed inputs

1. Installed EMOS: `agon-emos-eirene-r02-b2026-11-04-08-17-43Z`, source
   `16ec1f78c7ead1f38378c5ee9bee4633bcb62c1d`; full ROM SHA256
   `f62eed7f6bab8c164dcfe5e700132d289d52352f19d955acccbe1cff81b5e893`.
   The installation record owns actual boot/input/ROM evidence and rollback.
2. UART RC2 source/tag: `825eaf77176247f5b5ba2f940ae73fcace34e7e5`.
   UART's published ZIP SHA256 is
   `48d2fefa319f174ab4368287e40743c7610a3aeac61c0e32653fa26858166cd4`.
   Its local `build/tm001/rc2-001` and package preserve generated functional,
   example and matched PERF2 sources. Read `docs/tasks/RC-002/package-README.md`
   and `docs/uart0-async.md` in that owner repository. Reuse frozen bytes rather
   than a later mutable HEAD or an RC1 fixture with removed context expectations.
3. Extender source tests: reuse the EMOS owner tests preserved during the native
   port; compile their actual resident C sources from the installed source
   commit. Keep a complete selected-input manifest and distinguish host mocked
   I/O from actual eZ80 instructions. Source/linked validators remain necessary.
4. Official API/executable contracts remain those recorded in the source précis:
   official MOS `v3.0.2`, VDP `v2.16.0`, and pinned official documentation.
   No official checkout or peer-owned source is writable in this tranche.
5. Current P4/native VDP identities and live physical custody remain in the
   machine-local bench record. UART's Console8/stock-VDP results are historical
   coverage, not passes on this EMOS/P4/modified-native-VDP combination.

## Existing coverage and reuse disposition

| Coverage | Existing owner/artifact | Reuse or required adaptation |
|---|---|---|
| UART0 boundary lengths, zero INVALID, BUSY, NULL/callback once, source reuse, RX GP during TX, synchronous output before/after, finish and clean return | UART RC2 `functional` / package `fixture` | Rebuild frozen source with installed EMOS ROM extent/identity and new fixture identity; preserve tests and29-byte callback gate |
| C callback bridge/example | UART RC2 `example` | Same ROM binding adaptation; retain extra-register gate and caller contract |
| Bulk/paced useful work, independent PRT clocks and receiver comparisons | UART RC2 `perf/rc2` and `experiments/uart0-performance2/metrics.py` | Later matched performance phase; preserve measurement core, separate native/P4 receiver and model/physical results |
| Keyboard receive/IRQ behavior | EMOS `tests/test_emos_keyboard.py` | Existing host harness against installed C; retain C-reference flags and mark optional variants separately |
| Console/session transitions | EMOS `tests/test_emos_console.py` | Existing scripted peer; preserve framing/ownership tests; host proof is not ExCom bench proof |
| Controller resident service | EMOS `tests/test_controller.py` | Existing cache/fault/lifecycle harness; physical controller exercise remains separate |
| SD-link and admission | EMOS `tests/test_emos_sdlink.py`, `test_emos_admission.py` | Existing harnesses and simulated application address space; no claim of SD media/transport speed |
| Parallel engine/binding/UART1 guard | Selected methods in EMOS `tests/test_emos_parallel.py` | Existing deterministic peer/register mocks; exclude assumptions tied to old assembly spellings; identify supplemental inactive backend coverage |
| Installed pair Legacy/ExCom, input, modes, SD roundtrip and cleanup | Extender `qualification/run.py`, `manifests/hardware.json` | Reuse canonical runner after schema2 retained-installation receipts and current fixture/lifecycle admission |
| Raw SD dispatcher | Existing canonical raw-sector case | Keep its destructive-region/preimage restoration gate; no casual smoke substitute or invocation during preparation |
| Physical input takeover/controller movement and visible pixels/cursor | Existing manual review cases and controller viewer | Author review remains explicit; host tests and DMA progress cannot substitute |

UART confirms these fixtures do not inject keyboard events, force physical CTS
edge races, guarantee callback-driven exit/crash cleanup, validate arbitrary
contexts or exercise UART1/parallel routing. Do not add redundant tests for their
existing coverage or silently broaden those claims. UART's new IRQ-startup
vector-poison/reset sweep is a separate owner test and must not be run unchanged
against active EMOS vector owners. No new EMOS–P4 checksum is introduced; existing
local ROM guards and test arithmetic are not new transport framing.

## Itemized execution

1. Record the Author's explicit test-reuse instruction and UART owner guidance.
   Keep peer mail immutable and retain pointers, exact package/input hashes and
   actual omissions in this task. Existing work was committed/pushed first.
2. Freeze a private host-test workspace from the installed source and existing
   test files. Reuse the existing host register mocks at the native I/O include
   boundary, without editing resident behavior or weakening test assertions.
   Record every adaptation. Run a finite selected compile/harness tranche under
   the Pi automatic compile lease and reviewed telemetry guard. Stop the first
   failure, diagnose it, and obtain a fresh bounded follow-up if needed.
3. Verify UART's retained ZIP/package, copy functional/example/PERF2 sources
   privately, and compare copies against frozen inputs. Regenerate exact installed
   ROM/test identities only. Preserve original assertions, comparator data,
   callback gate and counter/log behavior. Do not run historical build/staging
   recipes that reflash firmware, alter startup or launch an emulator.
4. Audit each selected physical appliance for mode/route/foreground ownership,
   result placement, unique completion and cleanup. Their no-mode-switch text
   tests can retain the current mode; the Pi coordinator owns visible case
   labels, any necessary preselection/one-second settling and final restoration.
   UART0 appliances require Legacy/mainboard VDP and exclusive UART0 ownership;
   ExCom/P4 coverage is a separate existing compatibility case.
5. Build only required stopped fixtures. Keep source/measurement-core comparisons
   and exact binary/asset manifests. Prepare canonical retained-installation
   receipts without reflashing merely to fit an older receipt schema.
6. Complete safe, authorized fixture staging/input/service preparation and
   readiness checks. Startup stays unchanged and reset launches no test. All
   physical access requires the current central lease; do not disturb queued
   consumers or claim their grant. Announce actual readiness and stop before
   full-suite invocation, honoring the Author's standing boundary.
7. Report passed host checks, prepared artifacts, remaining readiness blockers
   and explicit untested/manual coverage separately. New testing code requires
   a demonstrated gap in the combined existing coverage. UART1 async reuse and
   production promotion remain separate decisions.

## State

The bounded reuse tranche passes: nine existing Extender host-test methods and
three physical UART tests (two functional invocations and the C example).
[Results and remaining readiness work](TEST-REUSE-RESULTS-R01.md) distinguish
that coverage from formal paired qualification. Firmware, startup and production
selection are unchanged. No reset, emulator or full-suite invocation occurred.
Extender retains exclusive physical custody; no queued consumer has been admitted.

## Bounded next execution: UART compatibility, not full qualification

The Author's “commit and push any dirt then proceed with the next tranche” follows
agreement to perform compatibility checks using both projects' tests. The first
finite physical tranche is UART's existing functional regression twice, then its
C example, on the currently installed EMOS/native VDP in Legacy mode0. It is
not the canonical25-check paired qualification or a performance campaign. That
full-suite readiness/invocation stop remains in force. Never label these three
passes complete firmware qualification.

1. Deploy two built binaries and frozen comparator data, with three new result
   directories and per-run tokens. Use existing checksum-free foreground/staged
   clients; verify every byte and preserve normal startup.
2. Before each explicit CLI LOAD/RUN, stop the listener, prove actual prompt and
   correct Legacy/mode0/input state. Observe original PASS plus the wrapper's
   unique completion token and a later MOS prompt. Only then retrieve results
   or dispatch the next independent invocation. The documented120s limit is an
   observation bound, not a completion estimate or permission to reset/replay.
3. Preserve receiver reports and full original log/counter files. Compare returned
   logs using UART's existing analyzer. The example's completion file is separate
   from its original console-only PASS. Preserve callback/input/CTS limitations.
4. Any guest fault, missing marker/prompt, failed byte comparator or uncertain
   source drain stops dispatch and preserves state. No automatic recovery run or
   reinterpretation of keyboard admission as a returned CLI.
5. Restore entry Legacy/mode0 and visible flashing CLI, stop listeners, preserve
   startup bytes and retain exclusive custody. Record preparation, runtime and
   retrieval separately. No P4/native firmware change, reset or emulator launch.
