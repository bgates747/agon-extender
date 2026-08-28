# PORT-003 Phase F — Browser handoff and bootable port

[`../../PORT-003.md`](../../PORT-003.md#phase-f--browser-video-handoff-and-bootable-port)
is the authoritative checklist and scope fence. This directory owns Phase F's
bounded source evidence, immutable snapshot and browser-video contracts,
independent fixtures, host/target qualification, and gate validators.

The initial implementation has one primary product sink: the browser interface
served directly by EDP/P4 over the Olimex DevKit's onboard Ethernet. PORT-006
owns Ethernet and generic HTTP/connection mechanics; PORT-003 owns pixels,
snapshots, video framing, and browser presentation.

## Structure

```text
phase-f/
├── README.md
├── contracts.md
├── legacy-browser-assessment.md
├── compatibility-delta.md       # official behavior retained and substituted
├── implementation-manifest.yaml # deterministic candidate-freeze closure
├── evidence/                    # generated provenance, host, build, target
├── fixtures/                    # independent frame and state expectations
├── scripts/                     # deterministic extractors and runners
└── tests/                       # fixed harness and browser test pieces
```

The Author accepted this planning package on 2026-08-27. It authorizes the
tracked implementation and nonphysical validation checklist, but deployment,
EMOS modification, Agon connection, and bench operation remain separately
gated. After every completed checklist item, reread `TODO.md`, the authoritative
Phase F checklist, and `contracts.md` before continuing.

The bounded source inventory is generated as
`evidence/source-provenance.yaml` for agents and validators and
`evidence/source-provenance.md` for review. Regenerate both with
`scripts/generate-source-provenance.py`; the generator deliberately accepts
the external checkout and installed-framework roots as arguments while keeping
those machine-local paths out of its tracked output.

The preimplementation fixture authority is
`fixtures/independent-fixtures.yaml`. Regenerate it and its pixel-exact,
human-reviewable `fixtures/visible-vdu-command-expected.svg` with
`scripts/generate-independent-fixtures.py`, passing the official `agon-docs`
root and this project's retained `vdp` root. Then run
`scripts/check-independent-fixtures.py` to produce
`evidence/independent-fixtures-check.yaml`. These scripts may inspect the
listed official documentation and retained data files but must never import or
execute the production implementation under test.

Production snapshot ownership lives in
`vdp/video/extender/display/presentation_snapshot_pool.hpp/.cpp`. The pool is
independent of Ethernet and EVF1: it owns fixed RGB888 storage, generations,
publication, and immutable leases only. `P4DisplayController` is the sole
producer and composes at its frame-task boundary; PORT-006 later consumes a
lease through an opaque two-segment send.

Production browser assets live under `vdp/video/extender/web/`. They retain the
accepted legacy visual treatment but implement the frozen dynamic EVF1 and
one-credit contract. The framework-free browser check is
`tests/browser_protocol_tests.html`; serve the repository root over HTTP so its
module can import the production parser and presenter by their firmware path.

The bounded network core and P4 adapter live under
`vdp/video/extender/network/`. PORT-006 sees only a two-segment opaque message
lease. `vdp/video/extender/web/browser_video_provider.hpp/.cpp` is the sole
snapshot/EVF1 bridge. Run its platform-neutral lifecycle and payload tests with
`scripts/run-network-host-tests.py --project-root <repository-root>`; compile
the nondeployable target diagnostic with
`scripts/vdp-pio.sh run -e p4-network-service` from the repository root.

For hybrid Arduino/ESP-IDF targets, embedded browser sources are declared in
the environment's tracked `pio/*-source-selection.json` under
`embedded_text_files`. `pio/select_sources.py` renders them into the generated
application-component `EMBED_TXTFILES` list. Do not reintroduce PlatformIO's
generic `board_build.embed_txtfiles` option here: with the pinned hybrid stack
it generates assembly without linking those objects.

The first bootable retained-port environment is `p4-browser-vdp`. Build it from
the repository root with:

```sh
scripts/vdp-pio.sh run -e p4-browser-vdp
```

Its selected closure is declared in
`vdp/pio/p4-browser-vdp-source-selection.json`. The exceptional
`vdp/video/extender/boot/p4_browser_vdp.cpp` bridge supplies Arduino's normally
generated `.ino` prototypes and then compiles the retained `video.ino`
lifecycle directly. The target has a disconnected parser `Stream`; it is a
bootable P4/browser candidate, not a VDU-ingress or return-transport build.
Do not upload it until the Author has separately approved checklist item 15.

Run the complete nonphysical regression gate with:

```sh
.venv/bin/python \
  docs/tasks/PORT-003/phase-f/scripts/run-host-regressions.py
```

The orchestrator compiles the fixed snapshot/controller and network/provider
harnesses under ASan/UBSan, runs the production browser modules in headless
Firefox against every independent EVF1 vector, rechecks all Phase F contract
models, reruns the Phase A--E host matrix, and runs every dependency and Phase
A--E permanent Python test. Its canonical result is
`evidence/host-regression-results.yaml`; browser details are in
`evidence/browser-test-results.yaml`. Temporary build paths are deliberately
absent so a second successful run is byte-identical.

After one complete `p4-browser-vdp` build, prove its exact application closure
with:

```sh
.venv/bin/python \
  docs/tasks/PORT-003/phase-f/scripts/validate-phase-f-build.py
```

The validator writes `evidence/build-closure.yaml` and
`evidence/link-exclusions.yaml`. It checks the selected objects, embedded
assets, retained and Extender symbols, effective C++17 compile boundary,
pinned Arduino identity, and deferred feature exclusions against the final
ELF and linker map. Do not run PlatformIO's `compiledb` target between the
complete build and this validator: that target clears the linker map while
leaving stale binary products in place, and the validator will correctly
reject the resulting mixed state.

For the identified candidate rebuild, pass `--closure-output` and
`--exclusions-output` paths inside an ignored, build-ID-specific staging
directory. Then run `scripts/stage-identified-build.py` against the clean
candidate commit. That script verifies factory segments, copies every binary
and diagnostic artifact under the full build ID, and writes the adjacent build
manifest without changing tracked predeployment evidence. It never flashes
hardware.

PlatformIO packages are intentionally isolated under ignored `vdp/.pio/` by
the tracked `packages_dir` setting. The official VDP environment and this P4
environment require incompatible Arduino major versions under the same global
package name; project-local packages prevent one build from silently replacing
the other's compiler/framework closure.

## Item 14 regeneration and audit

Item 14 first operated on an uncommitted candidate so that the Author could
review the complete change before approving identities or a commit. After
approval, its final candidate-freeze pass adds the approved identity, procedure,
and registry while retaining the reviewed unversioned build as predeployment
evidence. The source-provenance generator therefore labels project bytes
`working-tree` and records the base commit. The predeployment build must
contain `UNVERSIONED-DO-NOT-DEPLOY`; this proves that it cannot be mistaken
for the later clean identified rebuild.

Regenerate the fixed fixtures and boot rendering with:

```sh
.venv/bin/python docs/tasks/PORT-003/phase-f/scripts/render-boot-closure.py \
  --project-root . \
  --input docs/tasks/PORT-003/phase-f/boot-closure.yaml \
  --output docs/tasks/PORT-003/phase-f/boot-closure.md

.venv/bin/python docs/tasks/PORT-003/phase-f/scripts/generate-independent-fixtures.py \
  --official-docs-root /path/to/agon-docs \
  --retained-vdp-root vdp \
  --output docs/tasks/PORT-003/phase-f/fixtures/independent-fixtures.yaml \
  --expected-svg docs/tasks/PORT-003/phase-f/fixtures/visible-vdu-command-expected.svg
```

Regenerate the bounded source record with:

```sh
.venv/bin/python docs/tasks/PORT-003/phase-f/scripts/generate-source-provenance.py \
  --project-root . \
  --agon-docs-root /path/to/agon-docs \
  --legacy-root /path/to/agon-extender-legacy \
  --emos-root /path/to/agon-emos \
  --idf-root vdp/.pio/packages/framework-espidf \
  --arduino-root vdp/.pio/packages/framework-arduinoespressif32 \
  --output-yaml docs/tasks/PORT-003/phase-f/evidence/source-provenance.yaml \
  --output-markdown docs/tasks/PORT-003/phase-f/evidence/source-provenance.md
```

After the complete build validator, host regression orchestrator, and global
dependency regenerator have passed, join their current hashes with:

```sh
.venv/bin/python \
  docs/tasks/PORT-003/phase-f/scripts/generate-implementation-manifest.py
```

Run each generator twice and compare both output byte sequences. Then run the
fail-closed audit, supplying the read-only official VDP checkout only to compare
the declared patched files:

```sh
.venv/bin/python docs/tasks/PORT-003/phase-f/scripts/audit-predeployment.py \
  --upstream-vdp-root /path/to/agon-vdp
```

The audit parses every changed YAML/JSON document, resolves local Markdown
links, compiles changed Python, checks the shell wrapper, rejects private bench
values, verifies every manifest and project-provenance fingerprint, reconciles
source selection with the linked ELF closure, compares all declared
upstream-shaped patches, and records every changed file and hash in
`evidence/predeployment-audit.yaml`. It makes no hardware or deployment claim.

The hardware-only live checker is
`scripts/check-p4-browser-runtime.py`. It compares all directly served assets
to their committed bytes, performs a raw WebSocket upgrade, grants one masked
`frame` credit, validates a fragmented or unfragmented complete EVF1 message,
proves a no-credit quiet interval, disconnects, and reconnects for another
frame. Its permanent localhost test uses the actual asset files and a
fragmenting fixture server. Neither the localhost test nor the checker run
without an already deployed P4 is target evidence.
