# BENCH-016 — Standard firmware reuse for Olimex tests

Smith selects VDPlet v0.1.2-alpha and the latest approved integrated Eirene-function EMOS as
Olimex test defaults. Record what is installed, reuse a matching verified image,
and restore the current standards after explicit firmware/compatibility tests.
This removes unnecessary per-run flashing without obscuring actual firmware.

## Work and state

1. [x] Record the [operating policy](../procedures/olimex-firmware.md) and
   [exact standard selector](../olimex-firmware-standard.json); separate desired
   standard from actual installed state and production promotion.
2. [x] Retrieve the pinned VDPlet release and verify all nine SHA256SUMS entries;
   retain firmware/provenance locally. No flash, boot or test claim.
3. [x] Bind the exact latest integrated EMOS artifact, map/source/profile and
   public Eirene-function inventory with its owner. Do not infer completeness
   from a25f's installed history or an arbitrary source HEAD.
4. [x] Refresh the shared scheduling protocol and dedicated scheduler guidance;
   require ordinary jobs to reuse standards and explicit exceptions to restore
   them. Preserve live custody and frozen evidence; no global state migration.
5. [x] Establish the selected standard once during authorized physical cleanup,
   independently verify changed bytes and record installed state. The amended
   dc43 image is installed and independently verified; ordinary paired boot/CLI
   and resource handback pass. No fixture performance or production acceptance
   is inferred. Policy editing itself did not authorize a new hardware session.

Source instruction:2026-11-08, Smith's pinned-release announcement plus direct
request to modify Olimex protocols. Other agents receive the announcement from
Smith; this work does not independently roll out Alexe or Console8 hardware.
Known release limit: no execution of the exact v0.1.2-alpha image on hardware or
emulator at publication. Testing-standard selection is explicit despite that
limit; no general production acceptance is claimed.

The MOS owner returned a source-bound inventory: a25f covers merged API slots
and the released RC3-style guarded 25h path; 61h/62h remain open proposals, and
26h/raw90h belongs to a private receive variant. The selector therefore pins the
retained a25f build for merged/released functionality and lists exclusions
explicitly. It does not claim unmerged proposals are present or infer exhaustive
behavioral parity from table entries. Exact ROM/map were locally rehashed.

## Same-tag async amendment — 2026-11-08

Smith directed the release owner to replace the v0.1.2-alpha assets with
selection `0.1.2-alpha-async-r1`:1115568-byte dc43 image and source60e5b4e.
Extender downloaded all13 assets into a separate retained directory and checked
all12 SHA256SUMS entries and remote sizes. The selector now enables ordinary
async; private witness/count-return/quiet-poll/PCM remain excluded. No hardware
was accessed and no new physical acceptance is claimed. See the
[bounded audit amendment](AUDIT-012/RELEASE-AMENDMENT.md).

Actual149 was already running its frozen original F6/b004 cohort. Preserve that
worker and original clocks, then reconcile the current-standard handback after
the scheduler's actual terminal/joined custody return. Do not edit its live
inputs, relaunch it or record b004 as the amended standard. At the time of that amendment, first amended-image installation and physical
pairing remained pending under item5; the completion below records the later
scoped installation.

## First amended-standard installation — 2026-11-09

After the original delegated benchmark timed out, Extender accepted explicit
exclusive repair custody and preserved supported evidence before firmware
replacement. The current dc43 application1115568B was independently compared
within its1118208B rounded extent, preserving the retained final2640B sector
suffix. Exact extent SHA256 is
`10e11cc4d736151fb4874688748dbaa83850190ce6ca57fb30edaa8d33375c0d`.
Normal bootstrap, actual CLI/raw0/callback0/backend0, unchanged startup/listener,
neutral input, offline idle services, free USB and original parent/programmer
joins pass. EMOS/P4 firmware were retained. Installed identity and receipts
are in the machine-local inventory; no whole unchanged-device backup was made.

The protocol and initial installation work is complete. This records basic
installation/handback only, not a benchmark, async-session qualification, optical
review, production promotion or permission for a new workload. The original
Row failure and Apple UNRUN remain separate; Smith subsequently selected a
combined continuation under the scheduler's existing reservation.
