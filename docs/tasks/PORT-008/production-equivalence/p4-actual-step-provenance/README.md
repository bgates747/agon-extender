# P4 actual-step provenance capture

This is the provisional recorder associated with the deferred release-pair
method in PORT-008 Work 2.g. Under accepted D003, the
[staged process](../../../../qualification/staged-circuit-validation.md)
requires adequate evidence for the actual candidate but does not require this
particular recorder to be completed for unrelated electrical measurements.
Its command and environment requirements below remain mandatory if selected;
its unresolved defects and invalid captures are not waived.

`vdp/pio/capture_p4_actual_steps.py` is the qualification-only evidence
producer for PlatformIO environment `p4-port008-nonrelease-qualification`.
It observes the SCons actions that actually produce the linked `.o` files and
`firmware.elf`. It deliberately does not use ESP-IDF's generated
`compile_commands.json` or `build.ninja`; in this hybrid build those files
describe unused CMake `.obj` nodes.

The hook is inert unless the operator explicitly supplies
`AGON_EXTENDER_P4_PROVENANCE_DIR`. The value must be a canonical absolute path
with no whitespace or symlink component, its parent must already exist, and
the named directory must not exist. The qualification build directory must
first be clean, with the capture variable unset. The evidence build then uses
a second invocation and a new evidence directory:

```text
unset AGON_EXTENDER_P4_PROVENANCE_DIR
<clean-source>/.venv/bin/python -m platformio run \
  --project-dir <clean-source>/vdp \
  --environment p4-port008-nonrelease-qualification \
  --target clean

AGON_EXTENDER_P4_PROVENANCE_DIR=<fresh-absolute-evidence-dir> \
<clean-source>/.venv/bin/python -m platformio run \
  --project-dir <clean-source>/vdp \
  --environment p4-port008-nonrelease-qualification
```

Do not reuse an evidence directory or set the variable on the clean command.
Invoke the clean source's hardlinked `.venv/bin/python` directly with
`-m platformio`; do not invoke a copied `bin/pio`, whose absolute shebang may
still select the main worktree's interpreter. The recorder requires the
observed Python lexical path and imported PlatformIO package to belong to that
clean invocation. SCons is imported from the clean project's PlatformIO
package area and is captured from its actual module path rather than inferred
from a global PlatformIO installation.
The hook also rejects any selected object, `firmware.elf`, or `firmware.map`
that exists before its producing action.

The qualification script order is identity generation, source selection, then
capture installation. This lets the recorder inventory the exact generated
`video/CMakeLists.txt` bytes after the tracked selector writes them and verify
that boundary remains unchanged through finalization; the product gate also
reproduces those bytes independently from the tracked selector and manifest.

## Captured boundary

For every project and selected vendored C++ translation unit, the hook records
the exact escaped SCons argument-list boundaries, a non-executed diagnostic
rendering, the strict one-word-per-boundary inverse, and the expanded
response-file vector. It accepts only the pinned, byte-round-trippable SCons
POSIX ordinary-word and literal-word encodings. Live shell syntax, a compiler
driver anywhere except exact argument zero, and any noncanonical encoding fail
before execution. The recorder then executes the decoded C++ vector directly
with no shell. A path or define containing spaces remains one argument. The
hook records compiler binary hash/version/target,
the driver-selected `cc1plus` and assembler-dispatcher hashes/versions, the
exact assembler backend selected for the compile's visible architecture
selectors, response-file bytes and hashes, compiler-reported transitive
dependencies, direct source and output hashes, and before/after input
stability.

The Espressif `riscv32-esp-elf-as` executable is itself a dispatcher. The
recorder therefore reruns that exact hashed dispatcher with only the compile
vector's `-march=` and `-mespv-spec=` selectors, `--version`, and
`ESP_DEBUG_TRACE=1` added to the recorded sanitized environment. It accepts
exactly one JSON `Execute:` trace whose trailing vector is byte-for-byte the
selectors plus `--version`, then resolves, hashes, version-probes, and
pre/post-hashes the reported backend. The product policy must independently
pin both dispatcher and expected backend; a missing or contradictory trace is
ineligible evidence.

Only top-level SCons `@response` arguments are supported. The capture-owned
response bytes are retained and parsed for the analytical expanded vector.
Each file must be one UTF-8, LF-terminated line whose encoded words re-encode
byte-for-byte with the recorder's pinned safe subset of SCons `quote_spaces`;
the event records the encoded word boundaries, decoded vector, and successful
round trip. SCons `quote_spaces` leaves some quote, dollar, backslash, and other
tool-specific response syntax literal. The recorder does not generalize or
reinterpret those forms: any word outside its canonical ordinary-word grammar
fails closed before the compiler driver executes. A nested `@response` or
tool/linker response form such as `-Wl,@response` fails at the same boundary.

The capture-owned long-command helper authenticates the exact loaded
PlatformIO `piomaxlen.tempfile_arg_esc_func` wrapper and its binding to the
loaded SCons `quote_spaces` function. It also freezes the exact `SCons.Subst`
module and `SUBST_CMD` mode used to expand the response, the one-space argument
joiner, `@` prefix, `.tmp` suffix, build-owned temporary directory, and pinned
maximum command length. The helper revalidates every mutable module and
environment value in that stored response contract before materialization; a
replacement or override fails before it can produce executable response bytes.

The compiler action receives and records the `sanitized-deterministic-v1`
child environment: only `PATH`, `LANG=C`, `LC_ALL=C`, `TZ=UTC`, and a
capture-private `TMPDIR` remain, with `PWD` forced to the exact PlatformIO
`PROJECT_DIR`. The recorder also rejects a C++ action observed from any other
working directory. Compiler/include/library injection variables and
`SOURCE_DATE_EPOCH` are cleared. `PATH` is the exact inherited SCons value, not
a machine-independent constant; the product gate must constrain its entries
and compare it across the qualification and release roles.

The completed report and session also bind the capture runtime itself. They
record the resolved Python executable, process launcher, and exact interpreter
version, plus every regular file under the installed PlatformIO and SCons
package roots, including executable bytecode caches. Package symlinks and
non-regular nodes are rejected; bytecode writes are disabled before inventory,
and package-tree hashes and all individual file hashes are recomputed at
finalization and must remain exact. Product eligibility still requires the
independent gate to pin these recorded runtime identities to tracked policy.

The final link record additionally identifies the compiler driver and its
driver-selected `collect2` and linker binaries, prehashes and rehashes every
required policy-unit object immediately around the actual action, binds each
one to its successful compile-event sequence and digest, preserves the
capture-owned long-command response bytes, and requires exactly one direct
`firmware.map` `LOAD` for each required object. It hashes all required objects
plus the resulting ELF and map. This is deliberately a required-policy-unit
input claim, not a claim that implicit/default libraries, `-l` resolution,
driver specs, or the complete linker-script closure have been inventoried.

`pio/build_identity.py` runs before capture and materializes an environment-
owned generated header. Only
`video/extender/boot/p4_parallel_qualification_vdp.cpp` includes the
qualification header; the retained browser boot bridge supplies its own
environment-local default. The three firmware identity macros therefore do not
alter common production translation-unit commands. The non-release header also
contains `AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY`; the generator
accepts that qualification-only value from the like-named environment variable
and rejects it for ordinary boot environments. The recorder inventories the
generator and exact generated header, requires only the boot compile's
dependency closure to contain it, preserves its content and definitions, and
requires all four qualification identity values to occur in `firmware.elf`. No
qualification identity record is assigned here: absent operator-approved
values remain `UNVERSIONED-DO-NOT-DEPLOY`.

SCons' ordinary long-command helper embeds a newline-delimited cleanup command
and deletes its response file. Enabled capture replaces only that response
materialization mechanism with a content-addressed retained response file.
The resulting compiler/linker argument vector is strictly decoded and directly
executed as described above; no cleanup shell command is executed.

`session.json` is written first with status `incomplete`. `events.jsonl`,
content-addressed response blobs, and dependency-scan records accumulate.
Each JSONL line is canonical and independently hashed. The finalizer reloads
the raw bytes and requires exact JSON-value equality with its in-memory events;
the report embeds only those reloaded values. Only a fully passing finalizer
writes `provenance.json` and changes the session status to `complete`; a
detected contradiction writes `failure.json` and makes the build fail before
its ordinary size check.

## Deliberate limits

A complete record proves one qualification invocation's actual selected C++
compile steps, directly executed final-link vector, required selected-object
input and direct map presence, tool identity, compiler-reported dependency
stability, and artifact hashes. It does not independently prove the complete
transitive include closure; implicit/default/library/linker-script input
closure; Git cleanliness or commit identity; release-object equivalence;
nonzero per-object retained code; runtime behavior; deployment authorization;
or electrical/physical qualification. The Work 2.e product gate and a future
release composition own those claims. Driver specs, dynamic loaders, host
shared libraries, the Python standard library, and subtool inputs other than
the explicitly recorded compiler/assembler/link roles remain outside this raw
capture boundary. The evidence also assumes the clean checkout and host are
not being mutated by an adversarial concurrent process; before/after hashing
detects persistent change but is not a hostile-race proof.

Run the host-only adversarial recorder tests from the repository root:

```text
.venv/bin/python -B \
  docs/tasks/PORT-008/production-equivalence/tests/test_p4_actual_step_provenance.py
```

Those tests use synthetic executables and temporary files. They do not invoke
PlatformIO or build, deploy, or run P4 firmware.
