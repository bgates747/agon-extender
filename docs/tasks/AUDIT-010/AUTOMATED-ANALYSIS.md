# AUDIT-010 A10-04 — Automated analysis and triage

## Status and evidence boundary

A10-04 ran the Author-accepted A10-SET01 through A10-SET06 tool set against the
identities frozen by A10-02. It made no product-source change and performed no
target or hardware operation. A10-SET07 remains the A10-05 manual review.

Raw output, per-translation-unit receipts, canaries, input manifests and the
offline vulnerability databases are retained in the ignored local task silo
`agents/audit010/a10-04/`. Those files contain machine-local absolute paths and
are intentionally not copied into tracked documentation. This report records
their reproducible commands, hashes, counts and complete grouped disposition.

The analysis did not inspect Git history. Initial broad unittest-discovery
attempts are retained in the local evidence but disposed as setup errors: one
Extender executable test required a package argument, and four EMOS provenance
tests were invoked without their documented AgonDev root/worktree variables.
The bounded commands below supplied the proper scope and passed, including the
package test as a separate executable.

## Tool identities

| ID | Executable | Version | SHA-256 |
|---|---|---|---|
| A10-AT01 | Clang-Tidy | LLVM 23.1.2 | `f14e3665520c2b38e01c1f36a8bf20e37f5b629fd796bfa275095d20b5a51bfd` |
| A10-AT02 | Cppcheck | 2.22.0 | `6b532e512931187d9621a9be2618a6fc156f626ecfc90fbf88a39d59087c14e3` |
| A10-AT03 | Ruff | 0.16.9 | `b866df917f34629b905a47650bb1b0089e24bb9838e40a6d65b34bcc31f02930` |
| A10-AT04 | mypy | 2.3.1 | `2f5ed74fe4f758192073364d3292702327a5cb2f2312e1824f877506b4e32bb8` |
| A10-AT05 | ShellCheck | 0.11.0 | `4da528ddb3a4d1b7b24a59d4e16eb2f5fd960f4bd9a3708a15baddbdf1d5a55b` |
| A10-AT06 | Semgrep CE | 1.178.0 | `848e650d78bb1be63fb5ec82b5f4f310a5496cc048ef35a9cb63dc9a9a7ca9b7` |
| A10-AT07 | OSV-Scanner | 2.6.0 / OSV-Scalibr 0.5.2 | `ca69b3d3cd08f889a49dc0a383122f71cc528b83803671df5fd874d97485b108` |
| A10-AT08 | P4 compiler/map tools | ESP-IDF 5.5.5, GCC 14.2.0 toolchain pinned by A10-02 | Build hashes remain in `BASELINE.md`; the exact retained ELF/map were consumed. |

Ruff, mypy and Semgrep share one ignored Python virtual environment. ShellCheck
and OSV-Scanner use isolated extracted binaries. LLVM and Cppcheck reuse the
A10-02 project-local installations. No global package was installed or changed.

## Canaries and safeguards

| ID | Tool | Positive result | Negative result | Disposition |
|---|---|---|---|---|
| A10-CAN01 | Clang-Tidy analyzer | Detected conditional use-after-free | Zero diagnostics | Pass |
| A10-CAN02 | Cppcheck | Detected use-after-free; exit status correctly remained zero | Zero findings | Pass; findings are read from XML, never inferred from exit status. |
| A10-CAN03 | Ruff | Detected `shell=True` and an incompatible typed return | Zero findings | Pass |
| A10-CAN04 | mypy | Detected the incompatible typed return | Zero findings | Pass |
| A10-CAN05 | ShellCheck | Detected unquoted expansion | Zero findings | Pass |
| A10-CAN06 | Semgrep local Python rule | One expected `shell=True` match | Zero findings | Pass |
| A10-CAN07 | Semgrep two C++ rules | Two expected owner/API matches | Zero findings | Pass |
| A10-CAN08 | OSV offline database | Found five vulnerabilities for deliberately old `lodash` 4.17.20 | Product scan treated independently | Pass |

All source scanners ran report-only. Semgrep metrics and version checks were
disabled. OSV's databases were downloaded into the local task silo, after which
the product scan used `--offline --offline-vulnerabilities --no-resolve`.
No auto-fix, hosted source scan, remediation or target instrumentation ran.

## Input and execution ledger

| ID | Input / command boundary | Coverage and result |
|---|---|---|
| A10-RUN01 | `validate_p4_build.py --profile p4-console --output <frozen-build>` | Pass: 1,842 actual GCC actions; all 33 selected P4 units exactly once; 11 forbidden units absent; application archive and ELF link edge present. |
| A10-RUN02 | `browser_bundle_test.py --build-output <frozen-build> --expect compressed` | Pass: embedded-byte identity plus 48 EVF1/EVR1/EVP1/EVQ1 codec vectors. |
| A10-RUN03 | Two non-overlapping Extender discovery patterns plus the argument-taking installation-package executable | 86 Extender host checks passed; the suffix discovery also retained one disposed loader/setup error for that executable before it was rerun correctly. One target-object compilation was skipped because `AGON_P4_CXX` was deliberately unset. The inventory includes 30 files that compile sanitizer harnesses or invoke sanitized builds. |
| A10-RUN04 | Pinned EMOS `python -m unittest discover -s tests -p 'test_*.py' -v`, with exact AgonDev root and v0.1.23 prepared worktree | Pass: 132 tests; two independent-checkout codec comparisons skipped. The suite compiles/runs its ASan/UBSan harnesses. |
| A10-RUN05 | Clang-Tidy over the 33-entry actual-action-derived translated database; analyzer, bugprone, CERT, concurrency, performance and portability families | All 33 attempted; 15 completed without parser/compiler errors and 18 were incomplete. Per-unit receipts prevent incomplete units being called clean. |
| A10-RUN06 | Cppcheck imported the same 33-entry database, one bounded selected configuration, warning/style/performance/portability plus inconclusive | All 33 attempted; 976 reports. Two preprocessor-model errors make their affected paths incomplete. |
| A10-RUN07 | Ruff `E,F,B,S` over 128 tracked project Python files under `scripts/` and `tests/`, including active fixture generators | 2,760 reports, completely grouped below. Frozen task generators, vendor and generated output were excluded. |
| A10-RUN08 | mypy staged over 54 already annotated/high-risk `scripts/*.py` modules with untyped bodies checked and missing imports ignored | 107 reports in 19 files; 35 checked files had none. This is staged type coverage, not repo-wide strict conformance. |
| A10-RUN09 | ShellCheck over four tracked maintained shell entry points under scripts/tests/templates/current hardware helper scope | Zero findings. Third-party, emulator snapshots, generated bundles and frozen evidence were excluded. |
| A10-RUN10 | Three reviewed local Semgrep rules over `vdp/video`, `scripts`, and `tests` | 266 files scanned, seven matches, three partial-parse warnings. All matches are disposed below. |
| A10-RUN11 | OSV offline scan of three recognized requirements files | Five pinned PyPI package records; zero known vulnerabilities. ESP-IDF `dependencies.lock`, component pins, vendored source and ad hoc tool pins were unrecognized and receive no clean claim. |
| A10-RUN12 | GCC build log plus retained ELF section and size-sorted symbol reports | Application binary 1,582,848 bytes; IRAM text 103,342 B; DRAM data 20,840 B; DRAM BSS 47,608 B; flash text 1,214,140 B; flash rodata 243,660 B. These are link measurements, not runtime heap use. |

`$REPO` below denotes the repository root; `$RUN`, `$TOOLS`, `$BUILD`, `$CLANGDB`
and `$EMOS` denote the relative local task, tool, frozen-build, translated
database and pinned EMOS paths recorded above. The exact material commands were:

```text
.venv/bin/python scripts/validate_p4_build.py --profile p4-console --output $BUILD
.venv/bin/python tests/browser_bundle_test.py --build-output $BUILD --expect compressed
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
.venv/bin/python -m unittest discover -s tests -p '*test.py' -v
.venv/bin/python tests/installation_package_test.py dist/production/extender-installation-r02/extender-installation-r02
MOS_AGONDEV_ROOT=../mos-agondev MOS_AGONDEV_WORKTREE=<v0.1.23-worktree> python3 -m unittest discover -s tests -p 'test_*.py' -v
$TOOLS/llvm-23.1.2/bin/clang-tidy <each-selected-source> -p $CLANGDB --checks=-*,clang-analyzer-*,bugprone-*,cert-*,concurrency-*,performance-*,portability-*
$TOOLS/cppcheck-2.22.0/bin/cppcheck --project=$CLANGDB/compile_commands.json --enable=warning,style,performance,portability --inconclusive --force --max-configs=1 --suppress=missingIncludeSystem --xml --xml-version=2
$TOOLS/python-a10/bin/ruff check --select E,F,B,S --output-format json <128-file-manifest>
$TOOLS/python-a10/bin/mypy --ignore-missing-imports --follow-imports=silent --check-untyped-defs --show-error-codes <54-file-manifest>
$TOOLS/shellcheck-0.11.0/shellcheck -f json <4-file-manifest>
SEMGREP_SEND_METRICS=off $TOOLS/python-a10/bin/semgrep scan --metrics off --disable-version-check --config docs/tasks/AUDIT-010/A10-04-SEMGREP.yml --json vdp/video scripts tests
XDG_CACHE_HOME=$RUN/osv-cache $TOOLS/osv-scanner-2.6.0/osv-scanner scan source --offline --offline-vulnerabilities --no-resolve --format json --all-packages --lockfile requirements-dev.txt --lockfile $EMOS/requirements-dev.txt --lockfile examples/network-hello/requirements-speech.txt
riscv32-esp-elf-nm --print-size --size-sort --radix=d $BUILD/build/agon_extender.elf
```

The raw receipts preserve fully expanded arguments, output filenames and the
exact absolute paths used on this host.

## Complete grouped triage

“Unresolved” here means A10-05 must inspect the named source/contract; it does
not authorize a fix and is not yet a confirmed audit finding.

### A10-TR01 — Target compiler and linked image

The retained successful build logged 269 warning lines at 109 unique locations.
The repeated majority is inherited/selected-component noise: 123 deprecated
`fabgl::Rect` copy-assignment reports, repeated HTTP/component missing-field
initializers, component deprecation/config warnings and selected-vendor unused
state. These are **accepted for A10-04 triage only**, not declared correct;
A10-05 reviews active integration assumptions rather than line-fixing vendor
style.

The following compiler reports are **unresolved A10-05 candidates**:

1. A10-TR01a — `compression.h` reports that `size` may be used uninitialized.
2. A10-TR01b — retained VDU/context switches omit named enum states, and one
   comparison/bitwise expression and one mixed `&&`/`||` expression need
   semantic review.
3. A10-TR01c — four strict-aliasing reports occur in selected code and require
   target-representation review.

The size report is accepted as exact linked-image evidence only. It cannot
establish runtime free memory, PSRAM demand, fragmentation or stack peaks.

### A10-TR02 — Clang-Tidy

The 12,653 warning lines are highly repeated through header-expanded units.
Dominant families are signed-bitwise (2,103), narrowing conversions (1,327),
easily-swappable parameters (487), pragma-once portability (309), value
parameters (133), enum-size performance (100) and return-reference style (78).
They are **review inventory**, not 4,537 independent defects. Style,
micro-performance and broad portability reports with no demonstrated contract
effect are **accepted exceptions for this audit pass**.

Eighteen units are **tool-incomplete**, primarily because the translated host
Clang action encounters selected vdp-gl's Xtensa inline assembly constraint,
while the real ESP32-P4 compiler accepts the active closure. Additional
`-Werror`-promoted vendor pragmas/captures and retained GNU C++ variable-length
arrays contribute. The database remains provenance-valid, but a clean
Clang-Tidy claim is restricted to the 15 completed units. This limitation is
itself carried into A10-05; no diagnostic was suppressed to inflate coverage.

Analyzer/bugprone reports outside the bulk families remain **unresolved** until
A10-05 checks exact call paths. Particularly relevant groups are 17 unchecked
return-value reports, 17 assignment-in-condition reports, 16 suspicious string
comparisons and the VDU variable-length stack arrays. None alone proves a
defect under the target compiler and bounded inputs.

### A10-TR03 — Cppcheck

Cppcheck produced 976 reports: 735 style, 233 warning, three error, three
performance and two portability. The 735 style reports and broad const/static,
cast syntax, missing override/constructor and argument-name groups are
**accepted A10-04 review noise** unless A10-05 connects one to a contract.

Two of the three errors are **tool failures**: Cppcheck could not evaluate
`__has_builtin(...)` in `vdu_buffered.h` and `MAX(...)` in the configured FatFS
header. A third, returning a temporary through Arduino `WString`, is an
**unresolved selected-component boundary candidate**.

The following source-specific reports are **unresolved A10-05 candidates**:

1. A10-TR03a — opposite nested edge conditions in vdp-gl
   `displaycontroller.h` indicate a dead block.
2. A10-TR03b — `sizeof(CodePage) / sizeof(CodePage*)` is equal on this 32-bit
   target but is a suspicious, non-semantic count expression.
3. A10-TR03c — modeline `sscanf` has no field width; current product callers use
   retained constant modelines, so A10-05 must decide whether the input is ever
   externally reachable.
4. A10-TR03d — dynamic `alloca` and numerous uninitialized-member reports need
   constructor/path review; Cppcheck's ESP/derived-class model may be incomplete.

The reported unreachable code after `xthal_get_cpenable()` is a **false
positive** caused by the imported target intrinsic model marking the call
`noreturn`; the real compiler builds and returns through that path.

### A10-TR04 — Ruff

Every one of the 2,760 results is disposed by rule family:

| Disposition | Rule/count | Rationale |
|---|---|---|
| Accepted style debt | E501 1,029; E702 748; E701 516; E401 27; E402 15; E731 13; E741 2 | Formatting/import layout or identifier style does not establish functional error. No rewrite is authorized. |
| Expected test/tool idiom | S101 125; S603 143; S607 83; S310 15; S311 4 | Assertions are test or fail-closed tool checks; subprocesses and URLs are explicit local/operator inputs; non-cryptographic randomness is not used as a security secret. A10-05 still reviews the owning command boundaries. |
| Low-risk cleanup | F401 12; B007 4; B905 20; B904 2 | Unused imports/loop values, explicit `zip(strict=...)`, and exception chaining do not independently change current behavior. Retain for itemized fixes only if A10-05 finds a related defect. |
| Unresolved | B023 1 | `browser_layout_test.py` captures the loop-local `errors` name in an asynchronous callback without binding it. This can weaken or misattribute a test oracle and requires A10-05 review. |
| Unresolved | S110 1 | `measure_video.py` silently discards an exception while collecting partial browser state; review whether the retained result remains truthful. |

### A10-TR05 — mypy

The staged pass reported 107 errors in 19 of 54 modules. Most are annotation
inference debt in dynamically shaped JSON and argparse dictionaries; they are
not treated as runtime defects. A10-05 will inspect these higher-signal groups:

1. A10-TR05a — hardware/version validators index or iterate values still typed
   as optional after schema parsing.
2. A10-TR05b — console/review/storage helpers call `fileno`, `sendall` or
   `select` on optional handles; exact preceding guards determine validity.
3. A10-TR05c — `mos_recovery_console.py` has a value-shape conflict which may
   reflect either bad annotation inference or a real receipt/schema ambiguity.
4. A10-TR05d — performance analyzers mix string/numeric union values and could
   misstate measurements if parsing validation is incomplete.

Remaining missing annotations and collection-inference reports are **accepted
staged coverage limits**. A10-04 does not add annotations merely to silence
mypy.

### A10-TR06 — ShellCheck

All four maintained shell entry points parsed with zero findings. The positive
canary proves quoting diagnostics were active. This is a clean result only for
the four-file manifest, not emulator snapshots, third-party scripts, generated
bundles or frozen evidence.

### A10-TR07 — Semgrep policy rules

The seven matches are all **accepted owner exceptions or excluded alternatives**:

1. two direct `changeMode` calls are in a non-product canary;
2. three direct calls in `vdu.h` implement the official VDU owner and fallback;
3. one unchecked task-create statement is in the forbidden alternative
   `p4_frame_service.cpp`;
4. one match is in the selected USB host header, but the return value is
   compared with `pdPASS` and assigned to `running` in the same statement; this
   is a syntactic-rule false positive, not an unchecked result.

No selected product bypass of EMOS/VDU ownership was demonstrated. Semgrep
partially parsed `stock_p4_service.cpp`, `forward_parallel_stream.cpp` and
`vdu.h`; those are **coverage limits**, not clean files. CE single-file rules
cannot establish cross-file ownership or cleanup.

### A10-TR08 — OSV dependency inventory

The offline scan recognized PyYAML 6.0.3 twice, jsonschema 4.25.1, SKiDL 2.3.0
and gTTS 2.5.4, with zero database vulnerabilities. This is **accepted clean
evidence for those exact five records only**. ESP-IDF's lock format, four direct
managed-component pins, transitive ESP-IDF/Arduino components, vdp-gl,
ESP32Time, tool downloads and eZ80 toolchain/source pins were unmatched. Their
absence from OSV output is **unresolved inventory coverage**, not a safety
claim; A10-05 uses the frozen provenance ledger and selected integration
review.

## A10-04 candidates handed to A10-05

| ID | Candidate | Automated status |
|---|---|---|
| A10-AF01 | Possibly uninitialized compression size | Compiler warning; unresolved |
| A10-AF02 | VDU/context switch completeness and ambiguous expressions | Compiler warnings; unresolved |
| A10-AF03 | Selected strict-aliasing assumptions | Compiler warnings; unresolved |
| A10-AF04 | Modeled unchecked-return/assignment/string paths | Clang-Tidy groups; incomplete coverage and unresolved |
| A10-AF05 | Arduino `WString` temporary reference | Cppcheck selected-component report; unresolved |
| A10-AF06 | vdp-gl dead edge block / suspicious code-page count / modeline width / stack allocation | Cppcheck reports; unresolved |
| A10-AF07 | Browser-layout asynchronous error callback | Ruff B023; unresolved test-oracle risk |
| A10-AF08 | Silent partial-state exception in video measurement | Ruff S110; unresolved evidence-truth risk |
| A10-AF09 | Python validator, optional socket and receipt-shape paths | mypy groups; unresolved |
| A10-AF10 | WebDAV task creation owner checks | Semgrep rule did not cover the A10-03 rollback seam; manual review still required |
| A10-AF11 | Unrecognized dependency ecosystems and pins | OSV coverage limitation; provenance/manual review required |

These are candidates, not eleven confirmed defects. A10-05 must inspect every
candidate alongside all ledger areas that produced no high-signal automated
report. Clean or noisy scanners cannot dispose architecture, allocation,
concurrency, assembly, ISR, eZ80 ABI or externally published-state questions.

## A10-04 disposition

A10-04 is complete. Canaries passed; exact input scopes and tool limitations
are explicit; every result is classified as unresolved, false positive,
accepted exception/coverage limit, or bounded clean evidence. No tool output
was auto-fixed. Proceed next to A10-05's complete manual integration review;
do not elevate or repair individual candidates before that review is complete.
