# Olimex standard firmware and installed-state reuse

Olimex tests use the pinned standard mainboard VDP and the latest integrated
approved EMOS containing the current Eirene functions as defaults. Each incoming
agent brings and installs the firmware required for its own slot. Smith's
2026-11-11 instruction supersedes the earlier per-slot restoration requirement:
no firmware backup is required for admission and no firmware restoration is
required for release. If an agent's flash leaves the bench inoperable, that
agent restores the standard production firmware on the devices it modified.
Existing physical and test permissions still apply.

Agents are encouraged to check recorded installed firmware against their
required binaries before flashing. From the Extender checkout, name only the
components the job needs:

```sh
.venv/bin/python scripts/bench_firmware_check.py --require vdp=/path/to/vdp.bin --require emos=/path/to/emos.bin
```

`p4=PATH` is also supported. The host-only script hashes the exact required
files and checks the installed inventory, pending-write state and recorded
verification receipt. A match reflects recorded evidence, not a fresh device
reading: confirm no intervening write and obtain normal lease and physical
admission. Skip reflashing a verified matching image. An unknown or different
result requires reconciliation or preparation under the owner's lease.

## Selection and ownership

Smith's full notification also pins the following platform matrix until further
notice. Mainboard VDP firmware and Extender P4 firmware are separate components.

| Platform | Mainboard VDP | MOS |
|---|---|---|
| Olimex | VDPlet v0.1.2-alpha release, verified SHA256SUMS | Latest approved integrated EMOS, exact selector below |
| Alexe / Console8 | Same VDPlet release | Eirene MOS 3.1.0_uart0_rc_3; release ZIP member `mos-rc3.bin`,100879 bytes, SHA256 `d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50` |

Release sources: [VDPlet v0.1.2-alpha](https://github.com/bgates747/agon-vdplet/releases/tag/v0.1.2-alpha)
and [Eirene RC3](https://github.com/bgates747/eirene-mos/releases/tag/3.1.0_uart0_rc_3).
Bare Eirene is not an EMOS image or a substitute for Extender-owned transports.
Existing hardware permissions and human-only invocation restrictions remain.

1. [Standard selection](../olimex-firmware-standard.json) identifies exact
   component artifacts and the current EMOS binding state. The mainboard VDP
   standard is VDPlet **v0.1.2-alpha**, including its UART RX recovery repair.
   Verify the release's `SHA256SUMS` before using its firmware. Never replace
   the pinned tag with an arbitrary branch head or similarly named private image.
   Smith directed a same-tag release amendment on2026-11-08: selection
   `0.1.2-alpha-async-r1` replaces the original async-disabled image. The
   selector now pins1115568 bytes, SHA256 `dc43ecb8b1c324ffd1a032e6cc0c56d8c05dd33a355ce170c23adb35ffb533ab`,
   including ordinary async rendering. Download into a separate retained
   directory and verify current checksums; the unchanged version/tag alone
   cannot distinguish these releases. Preserve old artifacts and frozen controls.
   Disagreement with the superseded b004 hash is expected for this intentional
   amendment. Continue checksum verification: a mismatch against the current
   selected release remains a discrepancy to investigate.
   Private overlap witnesses, counted return, quiet polling and PCM remain
   excluded. The EMOS selector is unchanged.
2. The EMOS standard tracks the latest approved complete project-owned integration of
   the current Eirene public functions. Extender records its exact full-ROM
   identity, source/profile, map, [function inventory](../olimex-emos-functions.md)
   and retained binary when
   resolving/updating the selector. A timestamp, Git HEAD or an Eirene-only ROM
   is not a substitute for that integrated EMOS artifact. The current a25f
   standard covers merged/released Eirene functionality; unmerged 61h/62h and
   private receive experiments are listed separately in the inventory. A missing binding is
   an integration/preparation dependency, not a reason to silently select an
   older subset or demand the same human authorization again.
3. The scheduler checks the selection and actual installed record during normal
   admission. Extender/component owners resolve technical compatibility; the
   operator performs only the already-authorized install/test/restore actions.
   No new source-audit bureaucracy or per-job standard rebuild is required.
4. This policy names the **mainboard** VDP; it does not replace P4 Extender
   firmware, startup, listener, bootloader, partitions or unrelated storage.
   Historical complete production bundles remain selected under
   `production/current.yaml`; their old MOS/VDP preservation instructions do
   not override these defaults for a fresh ordinary deployment. Preserve their
   immutable records and qualify a separately identified successor composition.
   A testing standard is not production promotion,
   proof of hardware qualification or acceptance of every optional feature.

## Recorded installed state

The canonical current installed-identity inventory is the ignored local
`agents/bench-scheduler/installed-firmware.json`. `HARDWARE.local.md` links and
summarizes it. The central lease registry remains the only authority for queue
and custody; grant/release observations retain their original component evidence.
An inventory entry is not a second queue, a fresh CLI observation or a grant.

For each component, retain the actual version/build, exact image byte scope and
SHA-256, source/profile and local artifact reference, the installation and
independent verification receipt, actual verification time and known subsequent
writes. Record whether it is standard, an identified exception, or unknown.
Keep the current record accurate during a job, not merely its incoming identity.

1. Before a firmware write, the exclusive operator records the affected
   component as pending/uncertain with its issued-operation journal and last
   known image retained. Preserve all prior receipts. An interrupted or failed
   write must not leave the inventory asserting that old bytes are installed.
2. After independently checking newly written bytes, the operator records the
   actual resulting image identity and receipt. Record boot/CLI readiness
   separately; verified bytes alone do not mean the component booted correctly.
3. Application-only jobs do not modify the installed identity. Retained verified
   installation provenance, no intervening writer and a locally rehashed exact
   artifact justify reuse. Do not read back the entire unchanged device, make
   another backup or reflash simply because a new test starts.
4. Unknown or contradictory state is reconciled for the affected component and
   overwritten region. Preserve unresolved mutable bytes where needed; do not
   assume the desired standard was installed just because it was selected.
   Do not copy/restamp an old physical observation to make it current.

## Admission and execution

1. Unless the test's stated purpose is firmware development or compatibility
   with another version, bind the job to the standard VDP and fully selected
   current EMOS. Include those identities in existing manifests and results.
2. If recorded installed bytes already match, **skip firmware installation**.
   Perform only normal scope-appropriate CLI/input/service/resource admission.
   A fresh lease observation does not require fresh unchanged-firmware readback.
3. If they differ, arrange the necessary standard preparation under existing
   physical permissions and exclusive custody before declaring readiness.
   Preserve unrelated mutable user data, verify release checksums and independently
   compare the written bytes. Installation is separate from test invocation.
4. A firmware-development/compatibility exception identifies its purpose, exact
   alternate images and API/layout dependencies in the existing job plan. Bind
   write extents and any required recovery resources before changing firmware.
   No additional generic exemption form or human approval
   round is required for a test already authorized for that purpose.
5. A frozen older fixture does not silently become an exception just because it
   expects old firmware. The owner either adapts/re-freezes it for the standard
   or declares its actual version-comparison purpose. Preserve frozen originals.
   Do not invent missing APIs, enable unselected optional VDPlet features, or
   flash an unreviewed hybrid merely to make a fixture launch.
6. Keep original whole-operation clocks and adequate install/restore margins.
   Standard reuse reduces setup; it does not change test authorization, permit
   startup autorun, bypass human-only invocation or authorize uncertain replay.

## Cleanup, restoration and release

1. Firmware restoration is not required merely to release the bench. Record the
   actual installed identity and provenance for the next agent, which brings and
   installs its own required firmware under its lease.
2. If a flash leaves the bench inoperable, the agent that performed the flash
   restores current standard production firmware to the devices it modified,
   independently verifies the recovery and retains custody until safe handback.
   Report any concrete recovery blocker promptly.
3. Independently verify newly written bytes and record installed identity;
   verify the actual physical/process handback and preserve unrelated data.
   Notify the actual successor after release. Preserve frozen evidence and any
   explicit user-directed restoration or current-job stopping boundary.

## Initial transition

The last recorded actual148 handback predates this selection and contains the
older native VDP and a25f EMOS. It remains historical evidence, not proof of the
new standard or an exception to this instruction. The initial standard install
and declared pairing checks are preparation work under existing
permissions; no hardware change occurred while publishing this policy.

The VDPlet release records host/native checks but no execution of these exact
versioned bits on hardware or an emulator at publication. Smith selected them
for testing. Preserve that limit and record the first real installation/checks
when performed; do not require unrelated production promotion before testing.
