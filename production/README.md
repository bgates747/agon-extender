# Current installation

**v0.3.0** is the accepted production stack for two-way PARLIO on the
commissioned Olimex P4-PC bench. The [current selection](current.yaml) pins
the [immutable bundle](bundles/olimex-parlio-v0.3.0/bundle.yaml).
The [operator procedure](../docs/operations/olimex-bench/README.md) gives
the exact restore files and the default runner workflow.

| Component | Selected build |
| --- | --- |
| Extender VDP on P4 | `port-008-upload-r05-b2026-11-18-03-43-16Z` |
| EMOS on eZ80 | `agon-emos-eirene-r06-b2026-11-18-02-44-46Z` |
| Foreground SD listener | `sdserve-v0.4.0-b2026-11-18-02-44-55Z`, installed as `/emos/sdserve.bin` |
| Mainboard VDP | VDPlet v0.1.2-alpha, existing UART RX recovery build |
| Pi5 tools | The runtime archive preserves the release tools. The bench packet pins the current curated runner revision. |

The runtime and source/support archives are in
`dist/production/olimex-parlio-v0.3.0/`. The generated files are retained
locally. Check both archives against that directory's `SHA256SUMS`; after
extracting into fresh directories, run `sha256sum -c SHA256SUMS` in each.
The bundle records every archive member. On the commissioned host, the
verified runtime tree at the same location supplies the operator's direct
restore links. Obtain the generated files from the Extender owner if absent.
The previous P4 app and write extent, EMOS ROM and listener are in
the runtime's `rollback/` directory.

The release updates the P4 app0, EMOS ROM and SD listener on an existing
bench. It retains existing bootloader, partition tables, startup, and
mainboard VDP. The [physical qualification](../docs/tasks/PORT-008/PRODUCTION-SD-PARALLEL-R03-RESULT.md)
covers both file directions through 1,100,000 bytes and the worked example.
The P4 application embeds a private reset endpoint. Keep the archives local,
subject to the [notices](NOTICES.md). Other hardware and complete installations
retain their own [platform requirements](../docs/procedures/olimex-firmware.md)
and [qualification procedure](../qualification/README.md).

## Retained complete DevKit installation

The earlier **v0.1.0** tag records the
[extender-installation-r02 bundle](bundles/extender-installation-r02/bundle.yaml)
for its qualified local DevKit. Find its archive in
`dist/production/extender-installation-r02/` and its frozen sequence in
the [installation guide](../docs/installing.md). The
[compatibility audit](../docs/tasks/AUDIT-012/RESULTS.md) records companion
migration needs. Keep those immutable images and evidence for that scope.

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
The Author selects **v0.2.1** for the combined previously accepted HDMI and
keyboard/controller result. The tested r16 source already includes the accepted
HDMI import; no new firmware build or v0.2.2 fallback is required. The
[combined release record](releases/v0.2.1.yaml) binds that version to the immutable
update and companion identities. This consolidates the older standalone v0.2.0
promotion; its original bytes and acceptance remain historical evidence.

The combined release remains **unselected** until complete canonical paired
qualification and final selection/tag closeout. The v0.1.0 tag remains historical. [Release closeout](../docs/tasks/RELEASE-001.md) owns those
remaining gates; source integration and feature acceptance do not claim a
canonical suite pass.

The earlier `extender-installation-r01` is failed preparation evidence with an
incompatible bootloader. **Do not deploy it.** Its immutable records and archives
remain retained; they are not an alternative current installation.

## Retained sequential-reader SD utility component

The Author approves the first bench-turnaround tranche on2026-11-03, including
adoption of the exact tested `sdserve-v0.3.0-b2026-11-03-08-07-19Z` utility.
Its [immutable component bundle](bundles/sdserve-v0.3.0-b2026-11-03-08-07-19Z/bundle.yaml)
retains the24753-byte MOSlet, matched host clients, original build/map and exact
source archive; all archive members are independently compared with their inputs.
Generated archives and external hashes are under the relative archive directory
recorded in that manifest. Git alone does not contain these generated bytes.

Its earlier installation passed a 65,537-byte paired transfer with startup
preserved. This archive remains available for that earlier combination.
The v0.3.0 manifest supplies the current Olimex SD tooling.

## Accepted standalone Console8 Wi-Fi utility

Smith reports the corrected manual ESP8266 setup/BBS test passes on2026-11-06.
The [utility selection](../docs/network-setup-tool.json) pins the exact accepted
26053-byte executable and verified20-member runtime/source archive. This is a
standalone Console8 utility, with no change to the installed Extender pair.
The [operating guide](../docs/network-setup.md) records the manual scope.
Public redistribution/license closure, an agreed utility version and annotated
release tag remain pending; this component record does not select a new
whole-installation production version.
