# Resident controller logic audit

On 2026-10-30 the Author requires controller restoration to include an audit of
logic that Agon applications could own instead of resident EMOS. Flash capacity
is the immediate constraint. This record is a bounded source/size assessment,
not an implemented API change or a new firmware qualification.

## Verified baseline

1. The retained installed build is
   `agon-emos-v0.1.27-b2026-10-26-01-06-54Z`: 130,802 raw ROM bytes of 131,072,
   leaving **270 bytes free**. Its raw binary matches the installation manifest
   SHA-256 `6a1c9b4ec244342c80618f2e23ef326b61d95910c5bfe3e85e539c6889c2a95c`.
   The current owner checkout's controller C source and two controller headers
   match the source hashes retained for that build. Other checkout components
   are not assumed to match the installed composition.
2. The retained link map attributes **2,194 bytes of executable code**, **5
   bytes of read-only data**, and **131 bytes of zero-initialized resident RAM**
   to `src/emos_controller.o`. Thus the module accounts for **2,199 ROM bytes**.
   This excludes controller integration in the gateway, keyboard receive/tick
   path and lifecycle hooks, plus shared helpers. It is not a prediction of how
   much flash can be recovered.
3. The installed direct-FS P4 selection services only the keyboard peripheral.
   F310 restoration requires P4 USB host/controller coexistence work. The
   existing CI2/CIS2 transport already delivers F310 input to EMOS and the Agon
   viewer; concurrent physical acquisition should require **zero additional
   EMOS bytes** and no controller wire-format change.
4. Exact local manifests, maps, binaries and the audit receipt remain in ignored
   task evidence. No live hardware was queried, changed or tested for this audit.

## Ownership and relocation candidates

| Duty | Current implementation | Proposed disposition / prerequisite |
|---|---|---|
| USB enumeration, HID reports, physical-device decoding and source arbitration | P4 USB host and controller receiver | Keep on P4. Dual USB acquisition does not belong in EMOS or the Agon application. |
| UART1 ownership, ordinary VDU routing, keyboard admission and complete-packet serialization | EMOS keyboard/console owners | Keep in EMOS. Agon applications continue through the admitted gateway. |
| Caller/buffer bounds, bounded reply storage, interrupt-safe publication and correlation with an outstanding request | EMOS controller gateway/receive path | Retain the minimum necessary resident mechanism. Never retain an unowned application pointer for ISR delivery or restore the old long interrupt-masked READ. |
| Button-mask legality, opposite-direction checks, transition control/down values and sequence-contiguity validation | `emos_controller_packet`; the application also checks transition control/down values | Candidate for a reusable application client, with P4 retaining physical report validation. Current EMOS derives an acknowledgement from the last transition, so validation cannot simply be deleted before that dependency is removed. Keep any count bound still needed for resident indexing. |
| Source identity tracking, transition acknowledgement cursor and one-time transition delivery | EMOS compares source identity, derives an ACK after copying and clears cached transition count; application separately tracks source identity/edge sequence | Candidate for application ownership through an explicit revised gateway contract. Application validation/consumption must precede the ACK. Preserve P4 queue retention, source-session boundaries, tap delivery and restart handling. No byte-savings claim until built. |
| Stale-value clearing and unused-transition zero filling | EMOS clears axes, buttons and transition bytes during publication/READ | Candidate for application normalization. The current result contract promises neutral invalid values, so retain compatibility or version and migrate consumers. Validity and age metadata must remain sufficient for the application to reject stale input. |
| Request/cache deadlines, caller token/query lifecycle and source-age arithmetic | EMOS tick, receive and gateway paths; application already renews a healthy lease | Review separately for a smaller transport contract. Preserve rejection of delayed replies across tick wrap, bounded outstanding work and coherent age information; do not remove these mechanisms without an equivalent owner. Moving some timing/sequence work may require a revised gateway and metadata. |
| Calibration, deadzones/curves, user mappings, repeats, eight-bit axis conversion, gameplay policy, press totals and rendering | Viewer already owns conversion, press totals and rendering; calibration/game policy are not implemented in this resident module | Keep or implement in application code. These are not existing resident features whose removal can be counted as recovered flash. |

## Source and contract references

1. Official MOS API baseline: `../../agon-docs/docs/mos/API.md`, resolved from
   the Extender repository root. It documents application use of MOS calls and VDU output; it does
   not define the project-local controller gateway. No upstream source change
   or new official reference baseline is needed for this read-only assessment.
2. [Current development controller contract](../../protocols/controller-emos.md)
   defines the admitted gateway, 96-byte result, freshness and acknowledgement
   behavior. It remains authoritative until a deliberate implementation change.
3. Owner source, repository-relative to Extender root:
   `../agon-emos/src/emos_controller.c`, `emos_controller.h`,
   `emos_controller_wire.h`, `emos.c` and `emos_keyboard.c`.
4. [Application client](../../../tests/fixtures/controller/live.hpp) already
   owns source/edge tracking, press totals and healthy-lease renewal.
   [Application renderer](../../../tests/fixtures/controller/view.hpp) owns
   eight-bit conversion and visible invalid-state handling.
5. [P4 appliance peer](../../../vdp/video/extender/input/controller/appliance.hpp)
   encodes coherent replies and retires retained transitions using subsequent
   acknowledgements. USB and LAN sources feed this same downstream contract.

## Remaining work within controller restoration

1. Keep concurrent USB implementation on P4 and retain the current EMOS/viewer
   combination during that restoration. Report any actual reason this cannot
   be done without a resident change before extending EMOS.
2. Before selecting an EMOS reduction, measure the candidate through the owner
   wrapper and mandatory linked checks against the exact installed composition.
   Report net linked ROM/RAM change and application cost; source-line counts or
   individual function sizes do not establish net savings.
3. Prepare application-side validation/normalization before removing resident
   behavior. Identify all consumers, including the viewer and fsim bridge, and
   preserve compatibility or deliberately version/migrate the gateway contract.
4. Use the existing native resident/pipeline tests for malformed input, expiry,
   source changes, short taps, acknowledgement ordering and keyboard coexistence;
   retain the linked receive-overlap/Escape regression. Any physical invocation
   follows the applicable test/installation procedures and Author stop boundary.
5. This audit has not established that all 2,199 module bytes are removable.
   No reduction, new ABI, EMOS flash or production promotion is claimed.
