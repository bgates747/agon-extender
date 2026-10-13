# Nurples rendering optimization — partial results

## Executive summary

Ordinary bitmap drawing improved by **36–41%** in the measured P4 RGB888
rendering scope. Partial vertical scrolling improved by only **4.1%**. These
elementary results do **not** establish a Nurples gameplay speedup or satisfy the
campaign's sprite, repeated-control or widescreen gates. Software/hardware sprite
remedies are preserved on a separate development branch, with host correctness
checks and compiled candidates; their physical comparisons were not executed.

The [eight-hour contract](NURPLES-PERFORMANCE-R01.md) ran from
2026-10-12T13:16:20Z to21:16:20Z. A model/service interruption prevented further
agent work: the peer's last active clock was15:54:07Z and its resumed clock was
2026-10-13T00:11Z. Root resumed after the deadline. This is a time-limit stop with
the performance objective unachieved, not eight hours of completed optimization.
Only evidence preservation and temporary bench restoration follow; no new test
cohort or optimization iteration is authorized by this expired timebox.

## Measured RGB888 result

Worst rendering gain first. Each sample is an entire-window arithmetic mean of
queued primitive execution, including worker and foreground flushes. The control
has **one** measured window; the candidate has **three**. Candidate medians below
are medians of those three window means. They are not per-frame medians/p95s.
Gain =100×(control − candidate)/control; positive means lower rendering cost.

| Identical workload | Current RGB888 control, µs/update | RGB888 fast candidate median, µs/update | Rendering cost reduction | Candidate maximum window mean, µs/update |
|---|---:|---:|---:|---:|
| T03 partial vertical viewport scroll | 4,045.8 | 3,879.1 | 4.1% | 3,895.3 |
| Case41:64 ordinary bitmap plots + marker | 11,560.7 | 7,398.4 | 36.0% | 7,401.4 |
| Case39:16 ordinary bitmap plots + marker | 2,587.1 | 1,528.5 | 40.9% | 1,530.9 |

1. Both builds use clean source `c803856f5fe503386002d2bc8db67ca52ea26af3`,
   identical corrected schema2 instrumentation, mode20 logical512×384×64 and
   the same684×384 HDMI carrier. The candidate enables direct SET bitmap painting
   and a bounded PIE row-copy experiment. P4 installed-byte receipts are retained.
2. Control build `rgb-001-r12-b2026-10-12-14-05-59Z` application SHA256 is
   `398d37e38cf1e8d6c40be33c85d3ac423c4daa47377a656c3d866a7fcc59b3a0`.
   Candidate `rgb-001-r12-b2026-10-12-14-17-24Z` SHA256 is
   `0912941d3a34aa3de5bf0e95e633faeb5435ac4bd6f6bfa1a62b0ac5695d6d0b`.
3. Exact measured bitmap-command coverage passes. Initial worker-only probes
   missed parser-driven foreground flushes; those older rendering totals remain
   invalid for whole-workload comparison. Their separate fenced eZ80 timing is
   not discarded or relabelled as P4 rendering cost.
4. Three candidate windows agree closely, but the single control window cannot
   establish a repeated-control p95 comparison. Neither25% nor50% is formally
   qualified under the contract. T03 remains about60 application updates/s and
   59.94 background publications/s in both variants; pacing is not a speedup.
5. Native-lock waiting, UART/parser work, output preparation, PPA expansion and
   rolling hardware-sprite composition are separate scopes. Queued execution is
   wall time with preemption, not exclusive CPU utilization. Do not add nested
   or concurrent scopes. At60Hz a frame interval is16.667ms.
6. No software/hardware-sprite Nurples performance result was produced by these
   elementary runs. No Author visual/input acceptance, common HDMI dropout fix,
   full-width logical widescreen qualification or production promotion follows.

## Preserved candidate work

Canonical `main` is preserved through `5684bb04ad11b2a937f50f5503bb3951f347e62f`.
The separate pushed branch `codex/nurples-perf-sprites-r01` contains the following
default-off options at `a167e43ebe3a8ba2f51e000cf17a43a68443e273`; it has not been
merged or installed merely because it compiles.

| Candidate | Intended remedy | Completed validation | Physical status |
|---|---|---|---|
| Whole-frame indexed snapshot | Replace384 native-guard handoffs with one coherent row-descriptor/scene snapshot; retain prior-buffer/PPA/cache ownership | Actual-controller snapshot, bounds, row rotation, double-buffer and cancellation checks | Fresh comparison builds prepared; no new physical speedup claim |
| RGB888 bitmap lookup | Expand RGBA2222 through a256-byte internal-SRAM lookup with bounded aligned stores | 268,368 sanitizer cases, guard pages, stock rasterizer oracles and P4 object checks | Compiled; not physically compared |
| Indexed software-sprite visible snapshot | Refuse snapshots while stock software sprites are hidden; notify output after the existing final show operation | Actual-controller queue/guard/visible-state/lifetime tests and mode-service retirement checks | Compiled; P4 scheduling, flicker and Nurples still unqualified |
| Direct BGR hardware overlay | Avoid BGR→RGB222→stock painter→BGR round trip; preserve stock alpha, quantization, ordering and fallback | 1,708 exact stock/candidate sanitizer comparisons, P4 scene compilation and disabled-path code identity | Compiled; rolling composition and hardware Nurples unmeasured |
| Existing rolling cost fields | Expose already-recorded refill/copy/compose counters through HTTP; no new rendering timer | 48 handler compile/JSON checks and response bounds | Compiled; counter brackets are supplemental, not exact tagged frame timing |

The inherited both-horizontal-edge bitmap behavior is preserved through the
original path. This campaign does not fix upstream bugs. Optional flags and
private fixture labels must be checked against each immutable build manifest;
filenames alone do not establish the installed renderer.

Four retained complete `pair-r04` firmware builds all pass validation. All84
recorded artifacts hash-verify; their5,512 source files match the same clean
`a167e43e` commit. All use the same SDK/compiler/dependency/configuration closure
at360MHz CPU/200MHz PSRAM/80MHz flash. Distinct gzip archive hashes are retained;
their decompressed source payloads are identical. None was physically installed.

| Variant | Build ID | Application SHA256 |
|---|---|---|
| RGB888 control | `rgb-001-r12-b2026-10-12-15-43-40Z` | `f93fc0e0be48e0299eb29dbb196edb4afa6b66ce12ec9192abdb49e1ea675ccb` |
| Indexed visible-sprite snapshot | `indexed-hdmi-r06-b2026-10-12-15-43-00Z` | `0a339344516f1fe8c4d8d9e05caa49037502900954fe19b7aa06aafb62d769dd` |
| Same + direct BGR hardware overlay | `indexed-hdmi-r06-b2026-10-12-15-43-01Z` | `a2f0967c999d8ebd449e86fe5c80a5adcbfd90f2785c02b204611d63477754f1` |
| RGB888 lookup + direct BGR hardware overlay | `rgb-001-r12-b2026-10-12-15-43-02Z` | `2da2a7c42e06030d2ebf3257164e28a0da48a17f5418184ac24150727996357e` |

## Evidence and resumption boundary

The ignored local campaign record contains immutable raw data, manifests, hashes,
source archives, reviewed installers and single-session authority. Resolve its
machine-specific paths through the local bench record rather than publishing them
in this document. Relevant retained groups are `bench-r02` (measured result),
`pair-r03` (fresh static controls), `pair-r04` (sprite candidates), and `bench-r05`
(unexecuted comparison preparation). Prior frozen packages remain unchanged.

The next authorized campaign must begin with actual restored bench state and
fresh matched controls. Follow NP03 before NP04/NP05; do not infer a software-
sprite pass from hidden-state host tests or a hardware-sprite speedup from output
task framebuffer preparation. The existing asynchronous strip-compose counter
is the relevant hardware overlay scope. Other video modes remain gated.

## Bench closeout

The interruption also prevented the6502 agent's original mainboard-only lease
restoration. Root issued a new **cleanup-only** grant: collect already-completed
results if admitted, restore the exact incoming fsim P2 mainboard image, verify
startup and real CLI/listener exchange, and hand back positively. P4, EMOS and
wiring were excluded from that peer grant. The peer independently verified the
restored image, stopped on stale input after USB reset, then used exactly one
explicitly authorized ordinary Agon reset. Fresh input and actual CLI/listener/
read/EXIT/restart passed before positive handback at2026-10-13T00:28:14Z.

Root completed ordinary restoration at00:31:16Z. All five saved files received
full independent readbacks; temporary campaign bytes were retained under the
documented agent-evidence directory. No root reset, flash or test launch occurred.

| Restored item | Identity / verified terminal state |
|---|---|
| Mainboard VDP | Incoming fsim P2 application SHA256 `06dcfc3e0d7ddb8bc54eedf45a941330876ac07a74141e105c3dfeba6ba94a18` |
| Ordinary startup | Original38bytes; SHA256 `7b500d81030020f893aee64338889efd21630f7db9a893d0919d1084a69bb3a5`; keyboard setup only, no test/display autorun |
| Four fixture configurations | Exact saved T03/T07/T08/T09 bytes restored/read back; frozen executables/assets unchanged |
| Agon | Idle Legacy CLI after acknowledged listener EXIT; Extender input ready/neutral; no pending SD request |
| P4 | Measured RGB888 fast build14:17:24Z retained, with its earlier independent four-segment installation verification; new pair-r04 candidates never installed |
| EMOS, wiring | Unchanged |
| Active jobs / bench | No fixture, capture or transfer client running; bench released |

The current HDMI logical mode remains20 on the684×384 carrier. Restored ordinary
startup does not force ExCom or that mode on the next reset. Any future fixture
campaign must deliberately prepare its setup-only mode and start tests separately.
No further optimization is running. Production selection remains unchanged;
intermittent HDMI dropout and sprite-candidate visual/performance gates remain open.
