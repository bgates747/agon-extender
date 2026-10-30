# Current installation

**v0.1.0** is the Author-accepted production version, tagged `v0.1.0`.
It selects the unchanged **extender-installation-r02** local DevKit bundle.
[Current selection](current.yaml) points to its
[immutable manifest](bundles/extender-installation-r02/bundle.yaml) and archive
checksums. This is the single installation selection authority; extracted
packages do not select or install themselves.

| Component | Selected build |
|---|---|
| P4 | `uart-excom-console-r55-b2026-09-25-02-18-28Z` |
| EMOS | `agon-emos-v0.1.19-b2026-09-24-02-02-56Z` |
| Foreground EMOSlet | `sdserve-v0.2.0-b2026-09-24-02-21-03Z`, installed in `/emos` |
| Host clients | Exact versions and hashes in `builds/host.yaml` within the bundle |

On the maintained checkout, the runtime and source/support archives are in
`dist/production/extender-installation-r02/`, with external `SHA256SUMS`.
These generated local archives are not in Git and have no public download.
Another operator obtains both archives and recorded hashes from the build owner;
cloning this repository alone does not fetch them. Retain both archives together.

Use the [installation guide](../docs/installing.md) for verification, selective
installation, input bootstrap and rollback. Routine operation begins at the
[handbook](../docs/README.md). [Acceptance](../docs/tasks/RELEASE-001/R01-07.md)
and [packaging checks](../docs/tasks/RELEASE-001/R01-08.md) define the scope.

The firmware embeds this bench's private reset endpoint. It is local-only;
other endpoints require a new identified build. Public redistribution remains
subject to [source/license review](NOTICES.md). No blanket all-mode, other-board
or performance qualification is implied. A firmware revision may be accepted
or promoted only after the canonical [`../qualification/`](../qualification/README.md)
suite passes against its verified installed bytes; a build, flash receipt, or
offline-only pass is insufficient. Historical component draft labels are
retained; the installation baseline records bounded qualification. See the
[status interpretation](../docs/versions/README.md#status-belongs-to-a-record-and-its-declared-scope):
a build-time draft label does not negate its later recorded acceptance.

## Accepted native keyboard/controller update

The Author accepts the P4-PC direct-header USB keyboard and onboard-hub F310
coexistence build `indexed-hdmi-r16-b2026-10-30-22-37-38Z`. Its exact tested
application, matched old-ABI viewer, source/support and archive hashes are frozen
in [the native update bundle](bundles/indexed-hdmi-r16-b2026-10-30-22-37-38Z/bundle.yaml).
Both generated archives are retained under
`dist/production/indexed-hdmi-r16-b2026-10-30-22-37-38Z/`; extraction and independent
inventory/checksum verification pass. This component update preserves the
existing bootloader, partitions, EMOSv27, listener and mainboard VDP. It does not
contain an untested replacement factory image.

Use [native update handling](native-p4-update.md) and its [source/notices](native-p4-notices.md).
The archive is local-only and embeds the existing private reset endpoint.
It remains **unselected**: an agreed successor production version and complete
canonical paired qualification are still required before changing `current.yaml`
or creating a release tag. The earlier v0.2.0 authorization applies to the older
r10/EMOSv24 combination. [Release closeout](../docs/tasks/RELEASE-001.md) owns these
remaining gates; feature acceptance is recorded without claiming a suite pass.

The earlier `extender-installation-r01` is failed preparation evidence with an
incompatible bootloader. **Do not deploy it.** Its immutable records and archives
remain retained; they are not an alternative current installation.
