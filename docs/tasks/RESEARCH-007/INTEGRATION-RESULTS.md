# Linear-byte/PPA integration — preparation and deployment results

## Outcome

R07-I01–I03 are complete. The full P4-PC candidate uses linear one-byte physical
RGB222 drawing and PPA CLUT expansion into independent RGB888 HDMI backgrounds.
The target compiles/links and actual component bindings pass validation. Host
correctness and measurement-unit checks pass. Candidate and rollback packages
are verified. **Candidate installation and fixture staging are complete; tests were not run.**
R07-I04/I05 remain open. No integrated performance or visual pass is claimed.

The [contract](INTEGRATION-R01.md) is authoritative for the remaining work.
The earlier [conversion benchmark](PHYSICAL-RESULTS.md) compares unloaded
expansion paths; it does not establish integrated gameplay improvement.

## Candidate identity

| Item | Recorded value |
|---|---|
| Build | `indexed-hdmi-r04-b2026-10-12-01-53-19Z` |
| P4 source commit | `b6e15955c6eabd6e8c64dfb27946a9382023543a` |
| Source inputs | Committed, clean at launch; complete snapshot verified |
| Application bytes | 1,791,856 |
| Application SHA-256 | `4bbb33276dca90a806ad03cb605b2dde13012026fad5c503a2134ea85ec5398c` |
| SDK | ESP-IDF5.5.5, `b774170ff46c393eeb5e495ea37936038d3f4f4f` |
| Selection | P4-PC console, automatic HDMI carriers, rolling scanout,320 SRM, linear-byte/PPA, existing boot release/USB selection, normal timing hooks |
| Excluded | Parallel data-check/probe/ExExt stream selections; no transport optimization |

The generated build contains project-local PPA driver and HAL components. Only
the six hash-pinned upstream-derived files differ from the selected SDK.
The initial PPA-only include overlay failed because esp-dl selected old HAL
types first; overriding the owning HAL component removes that ambiguity for
every consumer. The base SDK checkout remains untouched.

The exact ordinary rollback is
`port-008-data-r20-b2026-10-11-09-07-32Z`, application SHA-256
`01cbd53255fbbae4760bc2ba64fc0f987cb9ef828b397d17a7cd7a64b9322771`.
Unlike the candidate, it compiles the existing parallel data-check selection;
neither comparison invokes parallel payloads. No matched hardware result exists.

## Offline validation

| Check | Result | Evidence scope |
|---|---|---|
| Linear controller golden run | Pass | Actual shared rasterizers: clipping, bitmap alpha/formats, paint, scrolling, background save/restore, overlays and logical swaps |
| Retained RGB888 golden run | Pass | Existing controller selection remains functional |
| HDMI build-selection tests | 14 pass | Explicit composition, reject invalid selections and preserve retained profiles |
| Static collector units | 2 pass | Synthetic regression: whole-image PPA time is not multiplied by height; legacy row normalization retained |
| Full target compile/link | Pass | Actual P4 application and generated CLUT components |
| Target validation | Pass | Selected definitions/sources/archive/ELF and all six derived hashes; no SDK HAL leak in compile paths |
| Candidate/rollback deployment archives | Pass | Four listed segments, source/config manifests, hashes and re-read archive contents |
| Finite SCAN package | Pass | Eight configurations/two startup files and frozen executable hashes |
| Resident controls | Pass | Five local colour/renderer/data files match retained resident manifest |
| Global version validator | Existing failure | Unrelated light2-harness-r02 connectivity hash mismatch; no electrical record changed |

The final compiler reports inherited vendor warnings. No upstream warning/bug
fixes are included. The compiled prototype and local package do not constitute
an installed, accepted or promoted firmware.

## Storage and measurement limits

For a512×384 logical image, representation falls from589,824 to196,608 bytes
(66.7% fewer pixel bytes). The retained native direct controller borrows HDMI
memory, however; its logical image is not another independent allocation.
The candidate adds private logical storage and allocates a maximum848×480
snapshot plus transparent A8 input:814,080 bytes,795KiB combined. Both selections
retain RGB888 HDMI buffers and rolling SRAM strips. Total live memory and
bandwidth must be measured; smaller logical pixels alone do not prove savings.

The fixed CLUT maps physical64 colours, including sync-bit aliases. It does not
add programmable256-colour VDU semantics. Packed-depth/unselected geometries
retain their existing controllers. Native hardware sprites remain in rolling
composition; scaled320 overlays are decorated before expansion/SRM.

Output row locking/composition and whole-image expansion have separate timing
scopes. PPA expansion wall time includes driver cache handling and, at320, the
subsequent SRM pass. It is not isolated CLUT kernel time or CPU occupancy.
The static collector records this unit distinction. Publication counts, DMA
cadence, eZ80 application updates and visibly coherent pictures remain separate.

## Prepared hardware comparison

Use retained data-r20 first, then candidate r04, with identical fixture bytes
and controls. The local index contains executable preparation/collection/
restoration commands, current machine configuration and both verified packages.
No new mainboard VDP, EMOS, game logic, startup policy or wiring is required.

| Existing article | Selection | Recorded evidence |
|---|---|---|
| SCAN T03 | Mode20 partial scroll/clipped tiles,0 sprites;120 updates/60 warm-up | PRT work/wait, completion, tagged P4 phases |
| SCAN T07 | Mode20 partial scroll plus32 software sprites;120/60 | Same fields under sprite load |
| SCAN T08 | Mode20 static background plus32 software sprites;120/60 | Isolate sprite cost |
| SCAN T09 | Mode20 deterministic Nurples;3600 updates/120 warm-up | Work/headroom, pacing, state/actor/projectile checkpoints |
| Render-load case54 | Modes20/136,16 hardware sprites;5s per open window | Native and scaled/double-buffer overlay coverage |
| Resident colour chart | Modes20/136,three10s windows each | Palette/layout/double-buffer output plus independent visual check |

SCAN binaries retain build `scan-scroll-suite-r02-b2026-10-06-23-03-19Z` and
repaired-game source `0c741d5e2021927adfa440f45b8e04b950114889`. Existing
`window-r02.bin` aliases are verified before use; assets and ordinary games are
preserved. Synthetic input still polls MOS keyboard but cannot prove human
input response. PRT nominal72,000counts/s means1,200counts per60Hz budget.
Require complete records, valid correlated windows and matching deterministic
state before comparing timing. No automatic reset/replay on missing progress.

Only autoexec selects fixture video modes. Original startup and all four
configuration files are preserved/restored; evidence stays under the reserved
agent results directory. Independently check mode0 upper text/outro and actual
Nurples input/flicker before acceptance. Flash/verify the four listed segments
while Agon is held reset; never flash a merged factory span over ordinary NVS.
Fresh handover, current device identity, admitted input and SD readiness remain
deployment gates. Read the latest bench handover; the deployment-only checkpoint below supersedes the earlier reservation gate.

Generated/local evidence is indexed under ignored
`agents/research007/integration-r01/INDEX.md`. Production selection is unchanged;
no acceptance, new production version or release tag is implied.

## Deployment-only checkpoint — 2026-10-11

On fresh Author authorization and fsim handover, the Pi flashed candidate r04
and independently verified all four segments, preserving NVS. Fresh EMOS
keyboard admission returned. The foreground fast listener read back all four
frozen SCAN executables and the five resident control/data files against local
hashes/bytes. Ten prepared baseline/candidate configuration and startup files
were uploaded and fully read back under `/agents/extender/results/r07-i01`.
They remain data only: root startup and the four active run.cfg files are
unchanged. No fixture, benchmark or game was invoked.

The Pi exited the listener and verified ready, neutral input with no pending
SD request; Agon remains at the Legacy CLI. Mainboard fsim P1-count VDP, EMOS
and wiring were preserved. Candidate and ordinary data-r20 rollback identities
remain those above. Production selection is unchanged.

The optional WebDAV HEAD preflight returned HTTP503; this did not prevent
foreground-listener deployment. Its cause is not established here. Retained
local receipts include four-segment verification, boot log, all SD readbacks
and final service status under the integration bench evidence directory.
[BENCH-010](../BENCH-010.md) records the separate fsim reset/USB observations.
Matched comparisons and Author gameplay review remain unperformed.
