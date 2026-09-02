# PORT-008 preliminary object-similarity checker

- Status: Preliminary evidence checker implemented and host-regression tested;
  not a D002 target-object-consumption gate; no production evidence manifest
  exists
- Owner: PORT-008, under accepted `PORT-008-D002`
- Schema:
  [`target-object-equivalence-v1.schema.json`](../schema/target-object-equivalence-v1.schema.json)
- Validator:
  [`validate-target-object-equivalence.py`](../scripts/validate-target-object-equivalence.py)
- Tests:
  [`test_target_object_equivalence.py`](../tests/test_target_object_equivalence.py)

## Purpose and claim boundary

This checker detects drift between supplied compiler outputs, artifact payloads,
and selected final-image symbol/disassembly records from two target builds. A
successful run is preliminary similarity evidence only. Every report sets
`equivalence_proved: false` and names the following missing claims:

1. the final images' declared symbols originated in the supplied object or
   archive member;
2. the manifest's Git commits and `dirty: false` values are true; and
3. the manifest-declared target and manifest-selected tools are authoritative.

Consequently, this checker cannot satisfy D002's requirement that the
qualification and release compositions consume byte-identical production
target objects. A future gate needs replayed linker provenance before that
claim is available.

The checker is evidence infrastructure, not production firmware. It does not
create a passing manifest, assign a build identity, build either composition,
or establish that any present PORT-008 source is production-ready. A future
build-evidence producer must record independently observed values from clean,
identified target builds before the preliminary checks can pass.

The manifest, compiler, `nm`, `objdump`, source tree, response files, and
compiler arguments are trusted local inputs. The checker executes
manifest-selected programs and arguments. Avoiding a shell does not make that
execution safe for untrusted evidence; the checker is not a sandbox. Run it
only after local review and inside an isolated build environment.

## Mechanical claim

For every listed compiler-driver unit, the validator performs all of the
following checks:

1. It requires schema class
   `preliminary-compile-output-final-symbol-similarity`, `host_native: false`,
   a cross-compiler triple, and the object architecture reported by `objdump`.
   A manifest describing the validation host architecture fails. These values
   remain manifest declarations, not an authoritative target identity.
2. It hashes both compile databases, both linked images, the selected compiler,
   `nm`, and `objdump`; it also hashes normalized `--version` output and checks
   each compiler's `-dumpmachine` result.
3. It selects exactly one compile-database record for the declared source and
   output. It expands and hashes nested response files, canonicalizes the two
   build roots, and verifies recorded digests for the complete command,
   ordered defines, and ordered remaining flags.
4. It replays the expanded compiler arguments directly, without a shell, into
   a temporary output. The replayed object's SHA-256 must equal the recorded
   compile output. Dependency side outputs are redirected into the temporary
   directory; response-file side outputs cannot bypass that redirection.
   Listing/profile side effects fail closed. The ordinary eZ80 architecture
   option `-Wa,-march=ez80+full` is not misclassified as a side output.
5. It hashes the exact object bytes. For an archive member, it also hashes the
   archive container, parses System V/GNU/BSD archive structure itself,
   requires one unambiguous member name, and proves that member bytes equal the
   compile output. Thin archives are rejected.
6. It reads each final linked image's symbol table once. Every declared linked
   symbol must occur exactly once with the same type and size in qualification
   and release.
7. It records symbol-relative, address-normalized disassembly for each declared
   symbol in both the compile object and final linked image. Qualification and
   release records must be identical. Exact object hashes remain the byte-level
   authority; normalized disassembly is a mechanically reviewable linked-code
   record rather than a substitute for those hashes.
8. It requires distinct manifest build IDs, build roots, linked-image files, and linked-
   image bytes. This prevents a comparison of one build with itself. The two
   repository commits may differ because release integration can occur later;
   each build remains clean and the gate instead requires identical per-unit
   source bytes, commands, compiler identity, object bytes, symbols, and
   disassembly.

All artifact paths are relative to their supplied evidence root, must remain
inside that root, and may not traverse symlinks. Unknown manifest fields,
missing hashes, ambiguous records, unsupported archive forms, command replay
failure, and any comparison difference fail closed. Passing those checks sets
`preliminary_checks_passed: true`; it never sets `equivalence_proved: true`.

Direct assembler producers are deliberately unsupported by schema v1. In
particular, the real `ez80-none-elf-as -march=... source -o object` command has
no compiler-driver `-c` option and its assembler does not implement
`-dumpmachine`. The checker rejects that command clearly. It therefore cannot
cover the complete EMOS production-object set and must not be described as an
eZ80 object-equivalence gate.

## Evidence workflow

P4 compiler-driver units and any supported eZ80 compiler-driver units require
separate manifests because their triples, object architectures, and inspection
tools differ. A complete eZ80 manifest is impossible under schema v1 because
EMOS includes direct-assembler objects.

1. The operator commits the candidate production source, qualification caller,
   release caller, profiles, and evidence procedure under the project version
   policy.
2. The build owner produces two clean, separately identified target builds in
   distinct build directories. The qualification build links the non-release
   fixed-backend composition; the release build links the intended production
   composition.
3. A controlled evidence producer records schema-v1 hashes and canonical
   record hashes without weakening or bypassing this validator. The project
   must review that producer as an F007-sensitive staging component before its
   output supports qualification.
4. The operator invokes the gate with the exact evidence roots and target
   inspection tools:

   ```text
   .venv/bin/python \
     docs/tasks/PORT-008/production-equivalence/scripts/validate-target-object-equivalence.py \
     --manifest <target-manifest.json> \
     --qualification-root <qualification-evidence-root> \
     --release-root <release-evidence-root> \
     --nm <target-nm> \
     --objdump <target-objdump> \
     --acknowledge-trusted-inputs \
     --report <new-gate-report.json>
   ```

5. The validator refuses to overwrite an existing report. The evidence owner
   records the manifest, report, both build manifests, and their identities
   together. A passed report states only preliminary compile-output, artifact-
   payload, and selected final-symbol/disassembly similarity for the listed
   units. It explicitly denies link contribution, Git provenance, target/tool
   authority, and overall equivalence. It also does not establish source
   completeness, release-link exclusion of the qualification adapter, runtime
   behavior, activation, electrical safety, or physical qualification.

## Current validation

Run the task-local regression suite from the repository root:

```text
.venv/bin/python -m unittest discover \
  -s docs/tasks/PORT-008/production-equivalence/tests -v
```

The suite uses temporary synthetic cross-target tools and artifacts only. It
does not install or preserve a fabricated passing production manifest. Its
negative cases cover stale objects, changed flags, host-class evidence,
changed linked symbols, changed linked disassembly, duplicate archive members,
same-build self-comparison, compiler-identity mismatch, shell operators, and
response-file side-output containment. It also proves that passing preliminary
checks cannot set `equivalence_proved`, that direct assembler commands fail with
an explicit unsupported-producer error, and that P4 host compile/run timeouts
fail closed.
