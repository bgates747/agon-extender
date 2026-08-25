# CA-2026-08-25-001 — Agon UART1 pin-label correction

- Document type: Corrective action
- Status: Resolved — corrective implementation approved
- Date opened: 2026-08-25
- Affected task: SETUP-006.3 and its SETUP-006.4 derivatives
- Originating commit: `1a19574f27de173ed0f41d04295e0503e3bc93de`
- Authoritative work tracker: `docs/tasks/SETUP-006.md`

## Trigger

During SETUP-006.4 GPIO review, the official Agon Light 2 pinout disproved four
UART1 alternate-function labels embedded in the accepted SETUP-006.3 Fritzing
scaffold. The Author directed a complete current-tree correction, preservation
of the erroneous historical commit, and a review boundary before committing
the corrective files.

## Controlling pin identities

The official Agon Light 2 pinout and eZ80F92 UART1 assignment establish:

1. Agon header pin 17 is `PC0 / TXD1`.
2. Agon header pin 18 is `PC1 / RXD1`.
3. Agon header pin 19 is `PC2 / RTS1`.
4. Agon header pin 20 is `PC3 / CTS1`.
5. Agon header pins 13 and 14 are `PD4` and `PD5`; neither owns a UART1 role.

The read-only legacy Extender repository independently records `PC0/TxD1` and
`PC1/RxD1` and uses PC0--PC3 and PD4--PD5 consistently with those identities.
Legacy contains no reachable occurrence of the four erroneous assignments.

## Origin and classification

Commit `1a19574` introduced all four errors together while creating the
pristine project's deterministic Fritzing generator:

1. `PD4 / RTS1`;
2. `PD5 / CTS1`;
3. `PC0 / RXD1`; and
4. `PC2 / TXD1`.

The same commit copied those values into task prose, generator assertions,
Fritzing connector metadata, label-bank artwork, and the generated SVG. Later
wiring drafts inherited the bundled defective header and label-bank parts.
This is a clean-sheet transcription and source-verification failure, not a
legacy design defect.

The defect changes displayed labels and Fritzing connector descriptions. It
does not change Agon physical pin numbers, connector IDs, breadboard geometry,
or recorded wire/net connectivity. Nevertheless, it can mislead design review
or physical construction and must be corrected before the diagrams are used as
pin-identity authority.

## Immediate containment

1. Preserve commit `1a19574` and all subsequent history; do not rewrite Git
   history for this defect.
2. Do not use the affected scaffold or wiring drafts as UART1 pin-label
   authority until this corrective action is resolved.
3. Change no physical wiring and make no electrical qualification claim under
   this corrective action.
4. Keep the correction inside SETUP-006 and stop before commit for Author
   review.

On 2026-08-25 the Author explicitly approved advancing both Agon 16-contact
header parts and both movable label-bank parts from Fritzing revision `r02` to
`r03` as one corrective set.

## Numbered corrective procedure

1. Inventory every current plain-text, generated, archived, and hash-bound
   occurrence of the defective assignments.
2. Correct the authoritative pin table and assertions in the SETUP-006.3
   generator. Advance both Agon header and label-bank Fritzing module identities
   so Fritzing cannot reuse cached defective metadata or artwork.
3. Correct the SETUP-006 task and scaffold documentation, preserving the
   historical origin and correction rather than silently implying that the
   accepted scaffold was always correct.
4. Regenerate the canonical scaffold, preview, archives, and checksums solely
   from the corrected generator.
5. Migrate the three current SETUP-006.4 wiring drafts to the corrected bundled
   header and label-bank parts without changing their physical connector IDs,
   sketch geometry, wires, or net partitions. Regenerate deterministic
   `draft_v1` from its corrected source and preserve the Author's cosmetic v2
   geometry.
6. Refresh every hash-bound README, AUDIT-002 finding, generated connectivity
   record, comparison record, and development-log reference affected by the
   corrected archive bytes. Preserve superseded hashes where they remain
   historical facts and clearly identify their corrected replacements.
7. Validate that all current artifacts contain only the controlling mappings;
   the four defective assignments occur only in this CA's historical account
   and the migration tool's negative test fixtures; all generator and
   AUDIT-002 checks pass; regeneration is deterministic; and the corrected
   v1/v2 net partitions remain electrically unchanged.
8. Record the exact corrected-file manifest below and present only that set for
   Author review. Do not stage, commit, or push it without explicit approval.

## Corrected-file manifest

### Maintained records and generators

1. `docs/decisions/CA-2026-08-25-001-agon-uart1-pin-labels.md`
2. `docs/tasks/SETUP-006.md` *(also contains preceding uncommitted SETUP-006.4
   work)*
3. `docs/tasks/SETUP-006/SETUP-006.3-fritzing/README.md`
4. `docs/tasks/SETUP-006/SETUP-006.3-fritzing/generate.py`
5. `docs/tasks/SETUP-006/SETUP-006.3-fritzing/correct-uart1-labels.py`
6. `docs/tasks/SETUP-006/SETUP-006.4-wiring-design/README.md` *(also contains
   preceding uncommitted SETUP-006.4 work)*
7. `docs/tasks/SETUP-006/SETUP-006.4-wiring-design/electrical-requirements.md`
   *(also contains preceding uncommitted SETUP-006.4 work)*
8. `docs/tasks/SETUP-006/SETUP-006.4-wiring-design/gpio-ownership-and-passthrough-discussion.md`
   *(new preceding SETUP-006.4 work with a CA correction section)*
9. `docs/tasks/SETUP-006/SETUP-006.4-wiring-design/make-draft-v1.py`
10. `docs/tasks/AUDIT-002.md`
11. `docs/tasks/AUDIT-002/findings.md`
12. `docs/development/2026-08-25.md` *(also contains preceding uncommitted
    SETUP-006.4 work)*

### Regenerated and migrated artifacts

1. `docs/tasks/SETUP-006/SETUP-006.3-fritzing/generated/SHA256SUMS`
2. `docs/tasks/SETUP-006/SETUP-006.3-fritzing/generated/light2-extender-breadboard-scaffold.fzz`
3. `docs/tasks/SETUP-006/SETUP-006.3-fritzing/generated/light2-extender-breadboard-scaffold.svg`
4. `docs/tasks/SETUP-006/SETUP-006.4-wiring-design/light2-extender-breadboard-wiring-draft.fzz`
5. `docs/tasks/SETUP-006/SETUP-006.4-wiring-design/light2-extender-breadboard-wiring-draft_v1.fzz`
6. `docs/tasks/SETUP-006/SETUP-006.4-wiring-design/light2-extender-breadboard-wiring-draft_v2.fzz`
7. `docs/tasks/AUDIT-002/generated/connectivity.json`
8. `docs/tasks/AUDIT-002/generated/connectivity.md`
9. `docs/tasks/AUDIT-002/generated/comparison.json`
10. `docs/tasks/AUDIT-002/generated/comparison.md`

The two independently packaged P4 and BB1460 `.fzpz` files are byte-unchanged
and deliberately absent from this manifest.

## Outcome

1. The canonical table and all current archives now assign `PC0/TXD1`,
   `PC1/RXD1`, `PC2/RTS1`, and `PC3/CTS1` to Agon pins 17--20 and leave pins
   13--14 as `PD4` and `PD5`.
2. Both Agon headers and both label banks use the approved `r03` identities.
   Every current wiring archive embeds byte-identical copies of the canonical
   corrected parts; no `r02` identity survives in those archives.
3. Scaffold generation, draft-v1 generation, migration validation, Python
   compilation, ZIP integrity, AUDIT-002 extraction and comparison, and the
   central version-record validator pass. Repeated generator checks report
   deterministic current outputs.
4. Normalizing only the four module IDs makes each source, v1, and v2 sketch
   XML byte-identical to its pre-CA form. No connector ID, geometry, wire, or
   net definition changed.
5. Regenerated AUDIT-002 evidence retains 49 instances, 234 conductive nets,
   and 60 passing checks with zero failures. Its structured diff changes only
   the input hash and the four corrected module identities.
6. Current SHA-256 identities are:
   - scaffold FZZ:
     `453689e18bb2b084fde70ef21b0dd36ee753174879796c5e30aef015edb5c082`;
   - corrected Author source draft:
     `df8b899c41b2b186af5c298a30e70178c5fad94f0430a14f7f100407172c3b54`;
   - deterministic v1:
     `e3b5a44bb1c795dc120c21c77ffd0e3855eb2a6d0772b7781700ce1d59a836c0`;
   - cosmetic v2:
     `51a69f6e7200fd46f2a2e2d15e047478e6f4080328f625bd35d648464c64136c`.
7. No physical wiring, firmware, hardware profile, qualification status, or
   remote was changed, and Git history was not rewritten.

The Author approved the corrective implementation and authorized its commit on
2026-08-25.
