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
5. [ ] At the next authorized physical preparation, establish the selected
   standard once, independently verify changed bytes and record installed state.
   This task's policy editing does not itself authorize a new hardware session.

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
