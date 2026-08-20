# SETUP-002 — Define human-readable project versioning

## State

- Status: Complete — approved by the Author on 2026-08-20

## Scope

Design and document one consistent, human-readable identification and
versioning system for project artifacts whose compatibility and provenance
must be understood without consulting Git object hashes.

The system must cover at least:

- firmware builds and released firmware;
- hardware and wiring revisions;
- transport and protocol revisions;
- board profiles and pin assignments;
- deployment fixtures and qualification procedures; and
- test runs and their associated artifact combinations.

## Artifact inventory

The scheme must distinguish three different needs. A project-controlled artifact
gets a version; purchased or upstream equipment gets a recorded identity; each
test run gets a manifest that references the exact combination used. We should
not invent project version numbers for a Pi, PC, or commercial board revision.

### Product and base-hardware identities

- Host Agon model and physical revision: Agon Light 2, Console8, and future
  variants.
- Host Agon board profile and GPIO pinout. Light 2 and Console8 require
  separate profiles even when they run identical MOS and VDP versions.
- ESP32-P4 development board model and physical revision, presently Olimex
  ESP32-P4-DevKit Rev D1.
- ESP32-P4 silicon and eFuse revisions, flash identity/capacity, and PSRAM
  identity/capacity as observed from the actual specimen.
- Eventually, the project-owned Extender PCB model and hardware revision.

These are recorded manufacturer/model/revision identities. Project-owned board
profiles that interpret their connectors and pins are independently versioned.

### Project-controlled hardware and connection artifacts

- Extender PCB or breadboard assembly revision.
- Breadboard placement/layout revision.
- Wiring-harness revision, independently for Light 2, Console8, and any future
  host profile.
- Pin-assignment/board-profile revision.
- Logic-analyzer probe-map revision when a reusable probe arrangement is
  defined.
- Other reusable test fixtures, adapters, loopbacks, level shifting, and power
  arrangements.

A one-off probe placement may live only in its run manifest. Promote it to a
versioned probe map when it is reused or becomes part of a qualification
procedure.

### Firmware, software, and programmable artifacts

- Extender production firmware.
- Temporary P4 canary, diagnostic, and experimental firmware images.
- Agon-side test fixtures and diagnostic programs.
- Any programmable logic, helper-controller firmware, or fixture firmware
  introduced later.
- Build configuration that materially changes the image: board profile,
  partition layout, SDK defaults, framework/toolchain baseline, and feature
  selection.

Temporary code still needs a human identity once it is flashed or used to
produce evidence. It does not necessarily need a production semantic version;
an experimental artifact identifier is sufficient.

### External firmware and software dependencies

- MOS version and build identity.
- Stock/onboard VDP firmware version and build identity.
- Official `agon-docs`, `agon-mos`, and `agon-vdp` source baselines used for an
  API, ABI, or compatibility conclusion.
- ESP-IDF, Arduino-ESP32, pioarduino, PlatformIO, compiler, esptool, and other
  result-affecting tool versions.
- Raspberry Pi and workstation operating-system/kernel/tool identities when
  relevant to reproduction.
- Logic-analyzer capture software and firmware versions.

These are normally recorded upstream identities, not versioned by this
project. A tracked project baseline may give an approved combination its own
named profile.

### Protocols and data contracts

- eZ80-to-P4 parallel transport protocol.
- Stock VDP UART/API compatibility level.
- Extender command, capability-discovery, network, storage, update, and other
  externally consumed interfaces as they emerge.
- Wiring electrical contract where voltage, direction, timing, or pin meaning
  can change independently of physical layout.

Each independently implemented contract needs a compatibility version. Purely
internal implementation changes do not.

### Test procedures and run-specific configuration

- Qualification/test procedure revision.
- Test-fixture revision.
- Logic-analyzer probe map, channel labels, thresholds, sample rate, trigger,
  decoder, and capture-software identity.
- Power/reset state and relevant switch, jumper, or mux positions.
- Input datasets, expected outputs, and test-program identity.
- Result/evidence bundle identity and outcome.

### Ancillary equipment identities

- Logic analyzer/sniffer model, hardware revision, and unique unit identity
  when calibration or unit variation matters.
- Raspberry Pi 5 model/revision and relevant interfaces.
- Development workstation identity only to the extent needed to reproduce a
  result.
- Cables, hubs, power supplies, and measurement equipment only when their
  characteristics can affect the test.

Ancillary equipment belongs in a bench inventory and is referenced by a short
alias from run manifests. It should not clutter every firmware version or get
new project revision numbers merely because an OS package changed.

### Test-run manifest: the convergence point

Every qualified or decision-bearing run receives one human-readable run ID and
a manifest referencing the applicable identities above. The manifest records
exact hashes and commits for audit, but ordinary discussion uses artifact IDs,
versions, profiles, and equipment aliases. Fields are conditional: a firmware
build test does not need a probe map, and a logic capture does.

This keeps versioning manageable: independently reusable things are versioned
once, fixed external things are identified once, and each run records links
rather than duplicating all their descriptions.

## Accepted vocabulary

Use these terms consistently in identifiers, manifests, documentation, and
conversation:

- **Artifact:** Anything reusable whose identity can affect a build, deployment,
  interface, or test result: firmware, wiring, a profile, protocol, fixture,
  procedure, or software tool.
- **Artifact ID:** The stable human name of one artifact lineage, independent of
  its current version; for example, `extender-vdp` or `light2-harness`.
- **Version:** A compatibility-significant software or protocol state. Versions
  normally express major, minor, and patch change.
- **Revision:** A controlled physical, wiring, layout, profile, fixture, or
  document state. Revisions advance monotonically but do not pretend to be
  semantic software versions.
- **Build:** One produced firmware or program image from a specific source,
  configuration, and toolchain. Multiple builds may implement the same version.
- **Variant:** A deliberate sibling form of an artifact, such as Light 2 versus
  Console8 wiring, that is neither newer nor older than the other.
- **Profile:** A machine-readable description of a hardware variant or contract,
  especially pins, capabilities, and board-specific build settings.
- **Fixture:** A reusable physical or software arrangement used to stimulate,
  observe, or validate another artifact.
- **Specimen:** One physical unit. It is identified by a private or public bench
  alias when unit-specific behavior matters; it is not assigned a project
  version.
- **Baseline:** A named, approved combination of independently versioned
  artifacts and external dependencies.
- **Status:** Lifecycle state such as experimental, candidate, qualified,
  released, deprecated, or rejected. Status is not part of version ordering.
- **Run:** One execution of a build, deployment, experiment, or qualification
  procedure under recorded conditions.
- **Run ID:** The unique human-readable name of that execution and its evidence
  bundle.
- **Manifest:** The machine-readable bill of materials for a build, baseline, or
  run. It links human identities to exact commits, hashes, equipment aliases,
  settings, and evidence.
- **Compatibility requirement:** An explicit declaration of which versions,
  revisions, variants, profiles, or ranges may work together.
- **Provenance:** Where an artifact came from and how it was produced.
- **Integrity hash:** A cryptographic check that the referenced bytes are exact.
  It proves identity at the byte level but is not the human-facing version.

The accepted distinction is: software and protocols have **versions**; physical
assemblies, wiring, profiles, fixtures, and procedures have **revisions**;
individual outputs have **builds**; purchased devices have manufacturer
identities and optional local **specimen aliases**; tests have **run IDs**.

## Accepted identifier decisions

- The authoritative policy location is `docs/versions/README.md`.
- Run IDs use `<TASK-ID>-YYYY-MM-DD-HH-MM-SSZ`; UTC is mandatory.
- Software and protocol identities use `vMAJOR.MINOR.PATCH`.
- Revision-controlled identities use `rNN`, beginning at `r01` and continuing
  from `r99` to `r100`.
- Build IDs append `bYYYY-MM-DD-HH-MM-SSZ` to the source version or revision.
- Experimental artifacts use revisions rather than consuming production
  semantic versions.
- Variants are lowercase names and are not ordered.
- Lifecycle status and compatibility declarations remain separate from the
  identifier.

Git commits and cryptographic hashes remain useful for exact provenance and
integrity, but they must supplement rather than serve as the names humans use
to identify versions.

## Implementation gate

Complete this task before serious firmware iteration, compatibility
integration, repeated physical deployment, or wiring/protocol qualification.

SETUP-001 may continue through local canary construction, build inspection,
and limited explicitly approved initial bench investigation. Do not progress
from those investigations into sustained implementation or hardware-interface
work until this task's scheme is accepted and applied.

## Instructions

1. Inventory every artifact class that needs a stable human-readable identity.
2. Separate independent version axes where compatibility can change
   independently; do not force firmware, wiring, protocol, and fixture changes
   into one misleading global number.
3. Define syntax, allowed characters, ordering, rollover rules, and the meaning
   of each component.
4. Define lifecycle states such as experimental, development candidate,
   qualified, released, deprecated, and incompatible, without overloading the
   numeric identity.
5. Define where each identity appears: source constants, boot/diagnostic output,
   filenames, manifests, test evidence, documentation, and release metadata.
6. Define compatibility declarations between firmware, hardware/wiring,
   protocols, board profiles, and fixtures.
7. Define who or what increments each version and which changes require an
   increment.
8. Preserve exact reproducibility by associating human-readable identities with
   Git commits and artifact hashes in manifests, while ensuring neither hash is
   required for ordinary discussion or selection.
9. Include worked examples covering an initial canary, a wiring revision, a
   backward-compatible protocol extension, an incompatible protocol change,
   and a released firmware build.
10. Review the complete proposal with the Author before applying it broadly.

## Dependencies and references

- SETUP-001 supplies the initial firmware, board-profile, partition, and canary
  artifact classes that the scheme must identify.
- `docs/architecture.md` and accepted ADRs define current system boundaries.
- `HARDWARE.local.md` identifies the machine-local bench but must not become a
  public version authority.
- The legacy Extender project's naming and evidence may be audited for lessons,
  but its ad hoc identifiers are not automatically inherited.

## Task précis

The project needs names that let a person answer questions such as “Which
firmware was flashed?”, “Which wiring was attached?”, and “Which protocol did
this test exercise?” without translating a Git hash. Independent artifact
classes need independent versions plus an explicit compatibility manifest.
Hashes remain attached as exact evidence, not as the human-facing identity.

## Decisions and assumptions

- Human readability is mandatory.
- Git hashes alone are insufficient as version identifiers.
- Cryptographic hashes remain required where artifact integrity or exact
  provenance matters.
- Independent artifact identities replace a misleading global project version.
- The Author controls artifact creation and version/revision increments;
  automation may assign UTC build and run timestamps.
- Compatibility is directional, explicit, and contextual. Unknown combinations
  are unqualified.
- Tracked records use aliases instead of private topology or specimen identity.

## Unresolved questions

No design questions remain open in the review candidate. Author review may
accept, amend, or reopen any decision before the policy is applied broadly.

## Affected implementation

- `docs/versions/README.md`: authoritative vocabulary, syntax, lifecycle,
  increment, compatibility, identity-placement, and manifest policy.
- `docs/versions/artifacts.yaml`: initial project artifact registry.
- `docs/versions/build-manifest.template.yaml`: build provenance template.
- `docs/versions/baselines/`: baseline rules and template.
- `docs/versions/SCHEMA.md`: shared field and compatibility-selector guide.
- `docs/versions/EXAMPLES.md`: required worked examples.
- `tests/runs/`: run evidence rules and manifest template.
- `requirements-dev.txt` and `scripts/validate-version-records.py`: pinned YAML
  parser and policy-aware structural validation.
- `AGENTS.md`: mandatory pointer to the authoritative policy.

After Author approval, SETUP-001 must apply the policy to canary revision r02:
add the tracked source identity, generate its build ID and manifest, embed the
identity in diagnostics, and create a run directory before physical deployment.
That application belongs to SETUP-001 and is not silently folded into this
policy-design task.

## Validation gates

- [x] Every in-scope artifact class has an unambiguous human-readable identity.
- [x] Independent compatibility axes can advance without falsely versioning
  unrelated artifacts.
- [x] Names are deterministic and increment triggers and authority are defined.
- [x] Required firmware identity locations and diagnostic surfaces are defined.
- [x] A run can identify firmware, wiring, protocols, profiles, fixtures,
  equipment aliases, dependencies, settings, and evidence without Git access.
- [x] Complete commits and hashes remain attachable for audit and integrity.
- [x] Lifecycle status and compatibility are distinct and machine-recordable.
- [x] Initial canary, wiring, compatible and incompatible protocol changes,
  released firmware, baseline, and run examples are documented.
- [x] Tracked records prohibit private topology, credentials, and specimen IDs.
- [x] The Author approved the policy, registry, templates, and examples on
  2026-08-20 before broad application.
