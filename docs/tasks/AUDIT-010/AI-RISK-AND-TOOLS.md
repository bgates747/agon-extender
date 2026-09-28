# AUDIT-010 A10-01 — Model-risk and analysis-tool research

## Executive summary

Research cutoff: 2026-09-28. No public evidence found supports the general
claim that GPT-5.6 writes better code than GPT-6 for a large, mixed-language,
multi-repository embedded product such as Extender. The public labels are also
not symmetric: OpenAI documents a GPT-6 family with Astra, Sol and Luna model
IDs, not a model whose public ID is `gpt-6.0`; `gpt-5.6` is a public alias that
routes to `gpt-5.6-sol`. An exact comparison requires retained model, reasoning,
harness, tool, prompt/context and task receipts. Subjective experience is a
useful reason to audit, but it is not a defect attribution or comparative
measurement.

The credible evidence does support a model-independent risk model. Long-context
information can be used unevenly; repository work requires coordinating changes
across files and functions; generated code exhibits missing cases, fabricated
objects or dependencies and incomplete implementation; and a patch can pass its
available tests while still diverging from intended behavior. Those risks map
directly to Extender's present concerns about allocation order, resource
ownership, stale published state, service coexistence and local tests that may
not exercise the integrated product.

The smallest justified A10-04 stack is the existing compiler-warning and
host-sanitizer coverage plus seven local FOSS capabilities: LLVM
Clang-Tidy/Static Analyzer, Cppcheck, Ruff, mypy, ShellCheck, narrowly authored
Semgrep Community Edition policy rules, and OSV-Scanner in offline scan mode.
This is intentionally a heterogeneous stack: no single parser or rule family
covers C/C++, Python, shell, dependency metadata and Extender-specific ownership
rules. Each tool starts report-only, with a canary proving that it analyzed the
intended files and can detect a known synthetic defect. PMD CPD, Vulture, REUSE,
Include-What-You-Use and secret scanning are deferred or excluded for the
reasons below.

The decisive project-specific prerequisite is compilation-database integrity.
Extender's hybrid PlatformIO/SCons build records that ESP-IDF-generated
`compile_commands.json` and `build.ninja` describe unused CMake `.obj` nodes,
while SCons produces the linked `.o` objects. A10-04 must derive or validate
Clang inputs against captured actual SCons actions and the selected-source
manifest. A clean scan of the wrong build closure would be false evidence.

No new scanner was installed or run. No source, firmware, hardware, SD card,
network service or component-owner repository was changed. Author review and
acceptance of the recommended set remain the gate before A10-04 installation or
execution.

## A10-01 research method and evidence classes

A10-RM01 — **Official product facts.** Model names, published behavioral
guidance and supported reasoning settings come only from current
[OpenAI developer documentation](https://developers.openai.com/api/docs/guides/latest-model).
Tool versions, licenses and behavior come from each tool's maintained source,
release page or official manual.

A10-RM02 — **Reproducible evaluations and published research.** The cited
papers disclose tasks, populations and methods that supply general failure
hypotheses. The TACL long-context study, ICLR SWE-bench paper, USENIX Security
package study and DOI-linked SWE-bench patch study have reviewed publication
venues; the generated-code bug taxonomy is cited from its public research
record. None evaluates the exact current GPT-6 Astra and GPT-5.6 Sol
configurations on Extender, so its rates must not be transferred to either
model or this repository.

A10-RM03 — **Maintainer evidence.** Tool identities, licenses, supported
features and documented limits come from maintained source, official manuals
and release pages. A repository-hosted issue such as the Gitleaks false-negative
report is identified as a reproducible report, not silently elevated to a
vendor guarantee; an accepted tool must still pass its own canary.

A10-RM04 — **Project evidence.** Current tracked source and documentation were
inspected without Git-history traversal. The current tree already contains
many host tests using `-Wall -Wextra -Werror` and AddressSanitizer or
UndefinedBehaviorSanitizer. It also contains the explicit actual-action
provenance warning in `vdp/pio/capture_p4_actual_steps.py`. These facts shape
the recommended tools; they are not a completed audit or a finding set.

A10-RM05 — **Subjective reports.** The Author's experience that some GPT-5.6
work has been stronger than GPT-6 work on this project is retained as the
motivation for A10-01. No community anecdote was promoted to comparative
evidence: such reports normally omit exact model snapshot, reasoning level,
context, tools, instructions, task difficulty and acceptance criteria. A broad
collection of anecdotes would add volume without producing a controlled
comparison.

A10-RM06 — **Local inventory only.** On 2026-09-28 the workstation exposed
Ubuntu Clang 18.1.3, but not `clang-tidy`, `scan-build`, Cppcheck, Ruff, mypy,
Semgrep, ShellCheck or Java on `PATH`. This records installation impact, not the
future A10-02 tool baseline. A10-04 must pin every accepted executable and
receipt after installation.

## Model identity and comparative evidence

| ID | Label under discussion | What the public documentation establishes | Audit treatment |
|---|---|---|---|
| A10-M01 | “GPT-6.0” | OpenAI publishes the GPT-6 family IDs [`gpt-6-astra`, `gpt-6-sol` and `gpt-6-luna`](https://developers.openai.com/api/docs/guides/latest-model). It does not publish `gpt-6.0` as the model ID on that page. | Treat “6.0” as ambiguous unless a retained session receipt identifies the model, reasoning setting and harness. The Author's earlier “6 Astra” wording is consistent with the public family name but does not establish a snapshot or run configuration. |
| A10-M02 | GPT-6 Astra | OpenAI calls Astra its highest-capability GPT-6 model and says it is generally better than GPT-5.6 Sol at staying coherent during long tasks. The same guidance says Astra can be more sensitive to skills and `AGENTS.md`, more likely to stop for clarification, and broader in testing than a small task needs. [Official GPT-6 guidance](https://developers.openai.com/api/docs/guides/latest-model) | These are vendor behavioral claims and prompting cautions, not defect rates or proof that an Extender change is correct. They justify explicit authority, scope and test boundaries. |
| A10-M03 | “GPT-5.6” | OpenAI documents `gpt-5.6` as an alias for `gpt-5.6-sol`, with Terra and Luna as other family members. It supports `none`, `low`, `medium`, `high`, `xhigh` and `max` reasoning; the guidance says to compare settings on representative workloads rather than assume more effort is always the best tradeoff. [Official GPT-5.6 guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6) | A bare family label still omits reasoning, mode, harness, context and tools. Record those inputs for any future comparison. |
| A10-M04 | Direct GPT-6 versus GPT-5.6 result | The official guidance contains a general long-task-coherence claim for Astra, but no public reproducible evaluation was found for this exact P4/ESP-IDF, eZ80, Python and hardware-in-the-loop product. OpenAI also states that model output is nondeterministic and behavior changes between snapshots and families, requiring representative evaluations. [Model-optimization guidance](https://developers.openai.com/api/docs/guides/model-optimization) | No general quality ranking is accepted for AUDIT-010. Repository evidence decides findings. A future model comparison would need a frozen task corpus, blind rubric, repeated runs and executable receipts and is not required to complete this code audit. |

A10-M05 — **Comparative conclusion.** There is evidence for distinct documented
behaviors, but not for the proposition that either family has a higher defect
rate in Extender. Code style, a successful local fix, or a visible regression
cannot identify the authoring model. AUDIT-010 must therefore audit all in-scope
code against the same contracts, regardless of provenance.

## Evidence-backed failure modes and Extender controls

Real-world repository tasks often require coordinated changes across multiple
functions, classes and files and very long contexts, as the original
[SWE-bench paper](https://arxiv.org/abs/2310.06770) explains. A TACL study found
that long-context models could perform materially worse when relevant material
appeared in the middle rather than at the beginning or end, although its tested
models predate GPT-5.6 and GPT-6
([Liu et al., 2024](https://aclanthology.org/2024.tacl-1.9/)). These results
justify explicit coverage and source receipts; they do not measure either
current model.

An empirical taxonomy of 333 bugs from CodeGen, PanGu-Coder and Codex includes
misinterpretation, prompt-biased code, missing corner cases, wrong input types,
hallucinated objects or attributes and incomplete generation
([Tambon et al., 2024](https://arxiv.org/abs/2403.08937)). A later study found
that 7.8% of analyzed plausible SWE-bench patches were counted correct while
failing developer-written tests, while 29.6% behaved differently from the
ground-truth patch
([Wang, Pradel and Liu, 2025/2026](https://arxiv.org/abs/2503.15223)). Those
populations are not Extender and do not yield an Extender failure probability;
they demonstrate why a narrow passing test is insufficient evidence.

| Risk ID | Relevant failure mode | Concrete Extender exposure | Required control |
|---|---|---|---|
| A10-R01 | Incomplete dependency tracing | A display-mode change crosses retained VDP code, selected vendor code, P4 allocation capabilities, output adapters, HTTP snapshots, EMOS-visible state and fixtures. Several generations of implementation coexist in the tree. | A10-02 selected-source ledger; actual compile/link action receipt; caller/consumer tracing across repositories; official API source where documentation is insufficient. |
| A10-R02 | Locally correct but globally inconsistent change | A change can correct LCD output while retaining a larger framebuffer, starving an HTTP connection task, changing browser capture or publishing a mode that did not commit. | Actor-explicit A10-03 transition maps; coexistence/resource matrix; full regression manifest rather than only the triggering fixture. |
| A10-R03 | Instruction or contract drift | Long sessions combine repository instructions, task contracts, accepted ADRs, production pins and later user corrections. OpenAI specifically warns that GPT-6 Astra is sensitive to skills and `AGENTS.md`. | Frozen task contract; one authoritative TODO; source-backed decisions; stable coverage/finding IDs; explicit approval gates; instruction contradictions logged rather than silently resolved. |
| A10-R04 | Fabricated API, dependency or environmental assumption | ESP-IDF capability heaps, FabGL behavior, EMOS/VDP ABI and host packages can be plausible but wrong. Package hallucination is a documented code-generation supply-chain risk in a 576,000-sample study, though that study did not test current GPT-5.6/GPT-6 ([USENIX Security 2025](https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen)). | Verify APIs in official docs/source; compile the selected build; pin and inventory packages; use OSV against recognized manifests; never install a proposed dependency merely because generated code names it. |
| A10-R05 | Weak error paths, rollback or truthfulness | A failed allocation or service startup may leave stale mode state, partial resources, silent fallback or a client-visible reset. Happy-path rendering does not prove rollback. | Manual transition review plus Clang/Cppcheck/Ruff/mypy findings; negative and fault-injection tests; published-state assertions; durable failure receipts. |
| A10-R06 | Lifetime, ownership and concurrency mistakes | Renderer, snapshot, LCD, HTTP, keyboard, UART and storage tasks share buffers, queues, callbacks and shutdown paths. Host models cannot reproduce every FreeRTOS schedule or capability heap. | Static lifetime checks; existing ASan/UBSan host harnesses; selected host TSan only where the same synchronization semantics exist; manual FreeRTOS ownership review; later bounded target heap/task diagnostics. |
| A10-R07 | Test overfitting and incomplete oracle | A deterministic Nurples fixture proved a mode-order symptom but did not by itself prove total exhaustion, fragmentation, a capability-heap shortage or the HTTP failure mechanism. | Preserve counterexamples; test both allocation orders and isolated/simultaneous services; define expected state, not just pixels; run broader regression manifests before accepting a fix. |
| A10-R08 | False completion claims | Compilation, ping, HTTP reset, correct LCD pixels and clean exit each prove different things. One cannot substitute for another. | Evidence matrix that names actor and observation; distinguish build, host, transport and physical evidence; require durable receipts and Author physical acceptance where applicable. |
| A10-R09 | Review bias toward plausible generated code | Fluent code and comments can make locally plausible ownership or fallback behavior appear intentional. Tool output can create a second automation bias. | Review contracts and counter-evidence before authorship; triage every tool report; use canaries and coverage counts; require manual end-to-end tracing; never treat “zero findings” as architecture proof. |
| A10-R10 | Model and harness nondeterminism | Model behavior changes with snapshot, effort, compaction, available tools and context order. [OpenAI's evaluation guidance](https://developers.openai.com/api/docs/guides/evaluation-best-practices) recommends representative regression evaluations and identifies long conversations and ambiguous tool data as edge cases. | Preserve model/harness receipts when model comparison matters; judge product behavior through deterministic builds, tests and evidence rather than confidence in a particular model. |

## Repository-specific analysis constraints

A10-C01 — **Actual C/C++ closure.** `vdp/pio/capture_p4_actual_steps.py`
states that generated ESP-IDF `compile_commands.json` and `build.ninja` refer to
unused CMake `.obj` nodes in this hybrid build; SCons emits the linked `.o`
objects. A10-04 must synthesize analysis commands from a fresh actual-action
capture or prove, file by file and argument by argument, that another database
matches it. The source-selection manifest remains the expected-project-source
set. Analyzer coverage must report selected, successfully parsed, skipped and
failed translation units separately.

A10-C02 — **Compiler diversity.** The production build uses its pinned
Espressif/GCC environment; Clang is an independent parser/analyzer. A Clang
parse failure can reflect GNU extensions, Xtensa/RISC-V builtins, generated
headers or mismatched configuration rather than a product defect. Conversely,
successful Clang parsing does not reproduce the target compiler. Native build
warnings and Clang-based analysis are complementary evidence.

A10-C03 — **Vendor boundary.** Automated tools may scan selected vendor files
and project modifications, but third-party reports must be attributed and
triaged against AUDIT-010's integration-focused scope. Unselected examples,
generated HTML and untouched vendor internals must not dominate counts or
silently enlarge AUDIT-007.

A10-C04 — **Host versus target.** Existing ASan/UBSan harnesses are valuable
for project-owned algorithms and explicit adapters. They do not reproduce P4
heap capabilities, DMA alignment, PSRAM fragmentation, FreeRTOS task stacks,
interrupt context, LCD/DSI timing or physical UART behavior. Every retained
result must name which substitutions the host harness made.

A10-C05 — **Assembly.** No maintained standalone FOSS analyzer was found that
can prove eZ80 register preservation, ADL/24-bit assumptions, bank/address
semantics and MOS/VDP ABI correctness across this product. The selected AgonDev
build, assembler diagnostics, maps, ABI probes, emulator tests and bounded
hardware tests remain necessary. C/C++ or Python scanner success says nothing
about assembly correctness.

A10-C06 — **Privacy and network behavior.** Accepted scanners must execute
locally. Rules and vulnerability data may be downloaded into a pinned local
environment before scanning, but project source, firmware, private bench data,
paths and findings must not be submitted to a hosted service. Auto-fix is off.

## FOSS tool survey — identity and applicability

Versions are the newest maintained releases located on the research cutoff,
not pre-accepted installation choices. A10-02 will record the exact installed
identities after Author selection.

| Tool ID | Tool and research version | Maintained source and license | Languages / analysis class | Compilation database | Target execution |
|---|---|---|---|---|---|
| A10-TL01 | LLVM 23.1.2: Clang diagnostics, Clang-Tidy and Clang Static Analyzer | [23.1.2 release](https://github.com/llvm/llvm-project/releases/tag/llvmorg-23.1.2); [Apache-2.0 WITH LLVM-exception](https://github.com/llvm/llvm-project/blob/main/llvm/LICENSE.TXT) | C/C++; compiler diagnostics, AST lint, path-sensitive static analysis. The [Clang-Tidy manual](https://releases.llvm.org/22.1.0/tools/clang/tools/extra/docs/clang-tidy/index.html) exposes bugprone, analyzer, concurrency, CERT, performance and portability families. | Effectively required at this scale; must satisfy A10-C01. | No for static analysis. LLVM sanitizers require instrumented host execution and an appropriate harness. |
| A10-TL02 | Cppcheck 2.22.0 | [2.22 release/source](https://github.com/cppcheck-opensource/cppcheck/releases/tag/2.22.0); [GPL-3.0](https://github.com/cppcheck-opensource/cppcheck/blob/main/COPYING) | C/C++; independent parser/dataflow for bounds, uninitialized data, lifetime, leaks, API misuse and portability. Its project describes support for non-standard embedded syntax. | Optional but preferred. The [manual](https://github.com/cppcheck-opensource/cppcheck/blob/main/man/manual.md) imports `compile_commands.json`; source-only configuration exploration is also possible. | No. |
| A10-TL03 | Ruff 0.16.9 | [0.16.9 release](https://github.com/astral-sh/ruff/releases/tag/0.16.9); [MIT](https://github.com/astral-sh/ruff) | Python; syntax, correctness, import, exception, modernization and selected security lint rules. | No. | No. |
| A10-TL04 | mypy 2.3.1 | [2.3.1 documentation/changelog](https://mypy.readthedocs.io/en/stable/changelog.html); [MIT](https://github.com/python/mypy/blob/master/pyproject.toml) | Python; gradual static typing and interface consistency. | No; requires import/config resolution and useful annotations or stubs. | No. |
| A10-TL05 | ShellCheck 0.11.0 | [0.11.0 release and maintained source](https://github.com/koalaman/shellcheck/releases/tag/v0.11.0); [GPL-3.0](https://github.com/koalaman/shellcheck/blob/master/LICENSE) | POSIX shell/Bash; syntax, quoting, expansion, pipeline, status and portability semantics. | No. | No. |
| A10-TL06 | Semgrep Community Edition 1.178.0 | [1.178.0 release](https://github.com/semgrep/semgrep/releases/tag/v1.178.0); [LGPL-2.1-or-later](https://github.com/semgrep/semgrep/blob/develop/LICENSE) | Multi-language syntactic/semantic pattern queries. Selected here only for locally authored ownership/API/policy rules, primarily Python and declarative files. | No. | No. |
| A10-TL07 | OSV-Scanner 2.6.0 | [2.6.0 release](https://github.com/google/osv-scanner/releases/tag/v2.6.0); [Apache-2.0](https://github.com/google/osv-scanner/blob/main/LICENSE) | Recognized dependency manifests, lockfiles, SBOMs and installed-package inventories; known-vulnerability and license metadata queries. | No. | No. The [official repository](https://github.com/google/osv-scanner) documents local offline-database scans. |
| A10-TL08 | REUSE 6.2.0 | [6.2.0 release](https://github.com/fsfe/reuse-tool/releases/tag/v6.2.0); the [maintained source](https://github.com/fsfe/reuse-tool) documents original code as GPL-3.0-or-later and mixed licenses for borrowed code/docs/data | Repository copyright/SPDX/license policy and SPDX output. | No. | No. |
| A10-TL09 | PMD Copy/Paste Detector 7.28.0 | [7.28.0 release](https://github.com/pmd/pmd/releases/tag/pmd_releases/7.28.0); [BSD-3-Clause](https://github.com/pmd/pmd/blob/main/LICENSE) | Token-level duplicate detection for C/C++, Python and other languages. | No. | No; requires a Java runtime. |
| A10-TL10 | Vulture 2.16 | [2.16 release](https://github.com/jendrikseipp/vulture/releases/tag/v2.16); [MIT](https://github.com/jendrikseipp/vulture/blob/main/LICENSE.txt) | Python dead/unreachable-code candidates with confidence levels. | No. | No. |
| A10-TL11 | Include-What-You-Use 0.26 | [0.26 release](https://github.com/include-what-you-use/include-what-you-use/releases/tag/0.26); [University of Illinois/NCSA Open Source License](https://github.com/include-what-you-use/include-what-you-use/blob/master/LICENSE.TXT) | C/C++ direct include dependency analysis. The maintained README calls it experimental and binds 0.26 to Clang 22. | Required. | No. |
| A10-TL12 | Gitleaks 8.30.1 | [8.30.1 release](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1); [MIT](https://github.com/gitleaks/gitleaks/blob/master/LICENSE) | Secret-pattern scanning of files or Git history. | No. | No. |
| A10-TL13 | ESP-IDF 5.5.5 built-in size and heap diagnostics | Project is already pinned to 5.5.5; [ESP-IDF license](https://github.com/espressif/esp-idf/blob/master/LICENSE) is Apache-2.0 | P4 linked-image size plus capability-heap, task-allocation, failed-allocation and heap-trace diagnostics. | No for runtime APIs; size reporting consumes the real map/ELF. | Yes for heap/task behavior; size analysis is host-side over the built image. |

## FOSS tool survey — likely signal, noise, cost and disposition

| Tool ID | Likely Extender signal | Expected false positives / blind spots | Resource cost | Proposed disposition |
|---|---|---|---|---|
| A10-TL01 | Use-after-move, null/lifetime paths, unchecked results, suspicious conversions, lock/API patterns and target-independent UB in selected C/C++. Host ASan/UBSan can expose executed memory/UB faults; a bounded host TSan run can expose races only in faithfully modeled host concurrency. | GNU/ESP attributes, generated headers, FreeRTOS idioms and vendor code may be noisy. Static analysis is path- and model-limited. [ASan typically doubles runtime](https://clang.llvm.org/docs/AddressSanitizer.html); [TSan uses about 5× memory plus 1 MB per thread by default](https://clang.llvm.org/docs/ThreadSanitizer.html) and cannot establish P4 scheduling correctness. | Moderate-to-high installation/storage; moderate scan CPU; high for sanitizers over broad suites. | **Select.** Pin a project-isolated LLVM release, validate actual commands, use a reviewed check set, and prohibit `-fix`. Retain existing native compiler warnings as a separate pass. |
| A10-TL02 | A second parser can find bounds, uninitialized, leak and ownership problems even where Clang cannot consume the embedded build cleanly. | Configuration explosion, macro-heavy ESP code and incomplete library models can create noise; no FreeRTOS schedule or target heap model. | Moderate CPU and result volume; small-to-moderate install. | **Select as a bounded complementary pass.** First run project-owned/selected files with the validated configuration; stop expanding configurations if the pilot produces no unique signal. |
| A10-TL03 | High-signal Python correctness, exception, resource, import and obvious security issues in build, deployment, fixture and receipt tools. | Rule families can conflict with established style; lint does not prove subprocess protocol, filesystem atomicity or hardware behavior. | Low. | **Select.** Start with correctness/error/security families, report-only, and add style only where it bears on correctness. |
| A10-TL04 | Interface/return-state mismatches, `None` handling, collection shape and typed receipt/schema errors in higher-risk Python tools. | [Mypy does not type-check unannotated function bodies by default](https://mypy.readthedocs.io/en/stable/dynamic_typing.html); dynamic imports, subprocess data and loosely typed scripts limit coverage. Repo-wide strict mode would create annotation debt unrelated to defects. | Low-to-moderate; potentially high triage if enabled indiscriminately. | **Select, staged.** Analyze already typed modules and high-risk orchestration/receipt code first; record typed-line/module coverage. Do not add annotations merely to silence the tool during audit. |
| A10-TL05 | Quoting, wildcard, pipeline-status, unset-variable and portability faults in the small shell surface. | Cannot understand external command contracts or hardware state; intentional word splitting needs review. | Very low. | **Select.** The source surface is small and the semantic signal is distinct. |
| A10-TL06 | Enforce Extender-specific forbidden bypasses, owner-only calls, missing paired cleanup patterns, diagnostic-build guards and policy-sensitive APIs that generic linters do not know. | Semgrep itself states CE is limited to single-file/single-function analysis and tolerates more noise; its advanced C/C++ capabilities are in the proprietary engine ([CE comparison](https://semgrep.dev/products/semgrep-vs-ce/)). A match cannot prove cross-file ownership or absence. | Low-to-moderate for narrow local rules. | **Select narrowly.** Use only reviewed, checked-in local rules with positive/negative canaries and metrics/network disabled. Do not use cloud, Assistant, Pro rules or C/C++ security claims. |
| A10-TL07 | Known vulnerabilities and license metadata for dependency ecosystems and lockfiles it recognizes. It can reveal stale host Python or packaged dependencies relevant to build/deployment integrity. | PlatformIO/ESP-IDF managed components, vendored snapshots and ad hoc pins may be absent or mapped imperfectly. A match does not prove exploitability; a clean result covers only recognized packages and database contents. | Moderate initial database download/disk; low-to-moderate scan. | **Select in offline scan mode.** Record recognized and unrecognized manifests separately; do not run experimental remediation or package-manager actions. |
| A10-TL08 | Missing SPDX/copyright/license records across project files and bundled source. | Extender already has layered notices and vendor provenance not necessarily expressed file-by-file in REUSE form, so initial noise could be very high and remediation could become unrelated metadata work. | Low scan cost, potentially high triage/remediation cost. | **Defer.** First use current manifests, `NOTICES.md` and AUDIT-010 vendor ledger. Pilot REUSE later only if those expose an unresolved provenance gap. |
| A10-TL09 | Large copied blocks that may have diverged, duplicated ownership or repeated fixes across C/C++ and Python. | Token similarity is not semantic duplication; generated fixtures, protocol tables and vendor code dominate unless carefully excluded. Requires Java, currently absent. | Moderate-to-high install/disk and triage. | **Defer.** Manual coverage-ledger review should identify suspicious duplication first; then run CPD against named project-owned areas if needed. |
| A10-TL10 | Unused or unreachable Python functions and imports that may expose abandoned paths. | The project explicitly uses callbacks, plugin-like entry points and generated/invoked scripts; [Vulture documents both missed dead code and implicit-call false positives](https://github.com/jendrikseipp/vulture). | Low. | **Defer.** Use Ruff, mypy, coverage/callers and manual tracing first. Run Vulture only against a bounded module with an explicit entry-point whitelist. |
| A10-TL11 | Direct include hygiene and accidental dependency coupling. | Its own README calls it experimental; version 0.26 targets Clang 22 while the current LLVM release is 23.1.2. Embedded generated headers and the hybrid build add mapping noise. It does not find lifecycle defects. | High integration effort relative to expected A10 signal. | **Exclude from A10-04.** Reconsider only for a demonstrated include/dependency problem. |
| A10-TL12 | Current-tree credentials or private tokens committed in ordinary files. | The latest release has a reproducible maintainer-repository report that canonical secrets can produce “no leaks found” with exit 0 ([issue 2170](https://github.com/gitleaks/gitleaks/issues/2170)). Git-history mode would also violate AUDIT-010's historical-review gate. | Low scan cost but unacceptable false-assurance risk at this version. | **Exclude 8.30.1.** A later fixed/pinned version would require a known-secret canary and current-tree-only scope unless the Author separately approves bounded history. |
| A10-TL13 | Distinguish total free memory from largest contiguous block, capability-specific shortage and low-water marks; attribute allocations to tasks; capture requested size/capabilities/function on failure. Static size reports expose linked DRAM/IRAM/flash growth. | Heap tracing/task tracking consume RAM and can severely affect allocator performance; broad hooks can perturb the exact shortage under study. Static size cannot show runtime allocations or fragmentation. [ESP-IDF heap documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32p4/api-reference/system/heap_debug.html) describes these APIs and overhead. | Low for size reports; moderate-to-high and perturbing for target tracking. | **Select only as later A10-03/A10-06 targeted diagnostics, not a general A10-04 scan.** Each instrumentation change and hardware run needs the task's bounded plan and authorization. |

## Recommended minimum A10-04 tool set

The following set is recommended for Author acceptance. “Minimum” means each
item covers a distinct risk class; it does not mean every available rule should
be enabled.

A10-SET01 — **Existing build and executed host checks.** Preserve the selected
target compilers' warnings and all existing `-Wall -Wextra -Werror` builds.
Inventory and run the existing ASan/UBSan host harnesses under their documented
substitutions. Add no broad sanitizer mode until coverage and cost are known.

A10-SET02 — **LLVM 23.1.2 static pass.** Use Clang-Tidy plus Clang Static
Analyzer over the actual selected project C/C++ closure. Start with compiler,
`clang-analyzer-*`, `bugprone-*`, relevant `cert-*`, `concurrency-*`,
`performance-*` and `portability-*`; remove style-only or inapplicable checks
before the full run. Record parse/coverage counts. Do not auto-fix.

A10-SET03 — **Cppcheck 2.22.0 complementary pass.** Run project-owned and
actively selected C/C++ with the validated defines/includes and a bounded
configuration policy. Compare unique findings with LLVM before considering any
additional configuration expansion.

A10-SET04 — **Python and shell pass.** Run Ruff 0.16.9 across project-owned
Python with reviewed correctness/error/security rules; run mypy 2.3.1 in staged
modules with explicit coverage; run ShellCheck 0.11.0 over maintained shell
scripts. Generated, frozen-evidence and third-party paths need explicit
inclusion/exclusion records rather than silent global ignores.

A10-SET05 — **Local semantic-policy pass.** Run Semgrep CE 1.178.0 only with
locally stored, reviewed A10 rules and canaries. Initial rules should encode
specific known contracts such as owner-only ordinary VDU routing, forbidden
diagnostic code in release selections, allocation/cleanup pair leads and direct
bypasses identified by the coverage ledger. A generic public ruleset is not a
substitute for this pass.

A10-SET06 — **Dependency-vulnerability inventory.** Run OSV-Scanner 2.6.0
offline over recognized current-tree manifests/locks and any task-produced SBOM.
Report ecosystem coverage and unmatched pins. Disable remediation.

A10-SET07 — **Manual assembly, architecture and lifecycle review.** This is part
of the minimum even though it is not a new executable. None of A10-SET01 through
SET06 can prove cross-task ownership, rollback transactions, capability-heap
budgets, eZ80 ABI behavior or truthful externally published state.

## Tool-to-risk coverage and non-claims

| Risk ID | Primary automated evidence | Required manual or runtime evidence | What the combined check still cannot establish |
|---|---|---|---|
| A10-R01 dependency tracing | Actual-action coverage manifest; LLVM parse receipts; Semgrep owner/API matches; Python import/type checks | Coverage-ledger caller/consumer trace across all three project repositories and official references | That every runtime callback, indirect call, assembly edge or generated selection is semantically correct. |
| A10-R02 global inconsistency | Full selected builds; cross-module type/lint; regression suite | Resource/coexistence matrix and end-to-end transition review | Physical service coexistence, peak target resources or externally observed truth without bounded runs. |
| A10-R03 instruction drift | Local Semgrep/policy rules; task/document link and manifest validators | Reconcile current contract, ADR, handbook, production selection and source | That an instruction is the right product decision; Author acceptance remains authoritative. |
| A10-R04 fabricated API/dependency | Compiler/type/import failures; OSV recognized-package report | Official documentation/source verification and pin/provenance review | That an existing API was used with the right lifecycle or that an unrecognized pin is safe. |
| A10-R05 weak errors/rollback | Clang Analyzer, Cppcheck, Ruff, mypy; executed negative tests | Transaction/state trace and fault injection | Completeness of all failure paths or truthfulness to every consumer. |
| A10-R06 lifetime/concurrency | Static lifetime checks; existing ASan/UBSan; bounded host TSan where faithful | FreeRTOS lock/task/callback review and targeted target diagnostics | Absence of target races, ISR violations, stack overflow, capability fragmentation or timing faults. |
| A10-R07 test overfit | Regression manifest, coverage counts and negative cases | Author-reviewed behavioral oracle; isolated and simultaneous service runs | Equivalence to every real application or workload. |
| A10-R08 false completion | Durable phase/result receipts and independent artifact hashes | Evidence-scope review and physical observation where required | A broader success claim than the named observation. |
| A10-R09 review bias | Independent parsers with known-defect canaries; complete triage ledger | Counter-evidence review and source-contract reasoning | That tool agreement means correctness; correlated rules and shared assumptions remain possible. |
| A10-R10 nondeterminism | Frozen commands, versions, inputs and machine-readable output | Repeat only the cases where variability matters and retain exact receipts | General future behavior of a changed model, tool release, environment or target timing. |

## A10-04 execution safeguards proposed for review

A10-ES01 — Every accepted tool runs from an isolated, pinned environment and
prints its version into the receipt. Record binary/package hashes where the
installation channel provides them.

A10-ES02 — Before the real scan, every tool receives a tiny task-owned positive
canary and, where meaningful, a negative canary. Failure to detect the positive
case is a tool failure, not a clean product result. Delete or retain canaries in
the task silo; never seed product source with artificial defects.

A10-ES03 — Produce an explicit input manifest for each run. Counts must separate
project-owned source, selected vendor integration, third-party source, generated
source, tests/fixtures, frozen evidence, skipped files and parse failures.

A10-ES04 — C/C++ analysis begins only after an actual-action-derived or
independently proven compilation database matches the A10-02 selected-source
closure. A generic CMake database is inadmissible for this build.

A10-ES05 — Tools run report-only with network/telemetry disabled during source
analysis. No auto-fix, mass annotation, formatter rewrite, guided dependency
remediation or package-manager execution is permitted.

A10-ES06 — Retain raw machine-readable output and exact commands in the task
silo. Every report is triaged as confirmed, false positive, accepted exception
or unresolved. Suppressions require a local rationale and cannot hide parse or
coverage failure.

A10-ES07 — Run broad source analysis before repairs. Later targeted diagnostics
or per-fix reruns supplement, but do not silently replace, the frozen audit
result or previously passed regression manifest.

## First target diagnostic implied by the latest LCD/Nurples round

This is a proposal for later A10-03/A10-06 authorization, not work performed by
A10-01.

A10-DIAG01 — At boot, before game-asset load, immediately before and after
mode-20 allocation, after snapshot/LCD/HTTP service initialization, and at the
first failed allocation, record `heap_caps_get_free_size()`,
`heap_caps_get_largest_free_block()`, `heap_caps_get_minimum_free_size()` and
the relevant `multi_heap_info_t` fields separately for default/internal,
8-bit, DMA-capable and PSRAM capabilities. ESP-IDF documents the largest free
block as the largest currently possible single allocation and recommends
comparing it with total free memory to detect fragmentation
([ESP-IDF heap debugging](https://docs.espressif.com/projects/esp-idf/en/latest/esp32p4/api-reference/system/heap_debug.html)).

A10-DIAG02 — Register the failed-allocation callback only in the diagnostic
build so the P4 reports requested size, requested capabilities and originating
function. Add task-stack high-water marks for the renderer, LCD, HTTP and
snapshot tasks. Use a bounded standalone heap trace only if the lightweight
measurements do not discriminate total exhaustion, fragmentation,
capability-specific exhaustion and retained/leaked allocation.

A10-DIAG03 — Compare the two already demonstrated orders: early mode 20 before
assets and late mode 20 after assets. Run isolated LCD, isolated browser and
simultaneous LCD/browser cases separately. Browser clients remain disconnected
except in the cases that require them. Static linked-image size belongs in the
receipt but cannot explain runtime fragmentation; ESP-IDF notes that runtime
heap is lower than compile-time static estimates because startup allocates task
and other resources
([ESP-IDF memory allocation](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/system/mem_alloc.html)).

A10-DIAG04 — Declare the diagnostic overhead and removal condition before the
build. Heap task tracking is not a passive observer: ESP-IDF warns of
non-negligible RAM overhead and severe allocator-performance impact. Therefore
the first diagnostic should use lightweight snapshots and a failed-allocation
callback, not broad allocation tracking.

## Research disposition

A10-RD01 — A10-01a is satisfied by A10-R01 through A10-R10 and their controls.

A10-RD02 — A10-01b is satisfied with a negative comparative result: documented
behavioral differences exist, but no evidence justifies a general GPT-6 versus
GPT-5.6 code-quality ranking for Extender, and the bare labels do not completely
identify the runs.

A10-RD03 — A10-01c and A10-01d are satisfied by A10-TL01 through A10-TL13,
including selected, deferred and excluded tools across compiler/sanitizer,
static, semantic-policy, dependency, duplicate/dead-code, Python, security,
repository-policy and target-diagnostic classes.

A10-RD04 — A10-01e is satisfied by A10-SET01 through A10-SET07, the risk
coverage table and A10-ES01 through A10-ES07. The recommendation is not
authorization to install or execute anything.

A10-RD05 — **Review gate.** The Author should accept, revise or reject the
recommended set and safeguards before A10-P01/A10-02 proceed and before any new
scanner installation or run. A10-01 did not inspect Git history and did not
trigger any A10-H01 through A10-H07 exception.
