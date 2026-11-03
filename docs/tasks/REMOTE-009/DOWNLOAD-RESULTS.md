# Sequential download results — 2026-11-03

Keeping the source file open makes the tested1.1MB download5.76times faster:
250.92seconds becomes43.57seconds, including final host delivery. Both file
sizes return exact bytes. The bench is released at a responsive CLI with the
installed listener/startup preserved and temporary utilities removed. The
optimized utility is a verified development candidate awaiting Author review.

## Matched host elapsed

Worst cases first, ranked by control elapsed. Bytes are SI bytes; seconds use
the Pi monotonic clock. Speedup is control/candidate; reduction is
`100 × (control − candidate) / control`. These are one ordered pair per size,
including client journals, P4 staging/worker, HTTP delivery and job cleanup;
there is no run-to-run variance estimate or independent clock calibration.

| Source bytes | Control s | Candidate s | Speedup | Less elapsed |
|---:|---:|---:|---:|---:|
| 1,100,000 | 250.920 | 43.573 | 5.759× | 82.63% |
| 65,537 | 13.728 | 3.029 | 4.532× | 77.94% |

## Worker and output scopes

P4's worker timer combines its local spool I/O, mainboard UART roundtrips and
the eZ80 foreground listener. It is not an isolated eZ80 filesystem timer.
Separate final HTTP delivery stayed effectively constant on the large pair.
The UART record counts are identical; this gain removes filesystem setup and
retains the existing216-byte request/reply protocol.

| Source bytes | Control worker s | Candidate worker s | Less worker elapsed | Control HTTP s | Candidate HTTP s | Records in each |
|---:|---:|---:|---:|---:|---:|---:|
| 1,100,000 | 249.277 | 42.100 | 83.11% | 1.287 | 1.284 | 5,095 |
| 65,537 | 13.531 | 2.595 | 80.83% | 0.089 | 0.097 | 306 |

P4 pre-worker staging is approximately0.013seconds in every case. Host file
comparison occurs after each measured transfer. The short worker result clears
the predeclared10percent improvement gate before the large pair starts. The
unmeasured1.1MB preparation upload takes43.263seconds; it is contextual, not a
new upload comparison. Preparation plus finite execution/cleanup lasts456.10
seconds; independent entry admission and final resource/release checks are
additional time. No spoken notification timing is included.

## Reproduction and preservation

1. Same P4r27 worker, EMOSv27, restored native VDP, cards, deterministic source
   files, route and compiler are used throughout. No resets, firmware writes,
   startup changes, mode switches or serial captures occur in this comparison.
2. The control utility is exact accepted listener source9a92d811, rebuilt with
   the same compiler as the candidate. Its22968bytes match the installed utility
   apart from one UTC build-ID string. The optimized owner source is b8e72c9.
   Exact build identities, hashes and static layout are in
   [the bounded research/build contract](DOWNLOAD-R01.md).
3. Control/candidate utilities occupy distinct temporary `/emos` names; deploy
   readbacks match their generated binaries. Explicit CLI invocations and fresh
   metadata EXIT separate each foreground service. Mainboard source files stay
   in the run's `/extender/diagnostics` directory; no root clutter or user file
   replacement. Unknown or pre-existing paths are never overwritten.
4. Canonical startup/listener bytes match before and after; temporary utility
   aliases are removed. Final canonical listener EXIT, neutral ready input,
   idle worker/listener and ownerless serial endpoints pass. Text/flashing cursor
   and completion commands are sent; optical/sound behavior is not claimed.
   Central generation2 lease is released with no next waiting request.
5. The installed canonical listener remains its incoming accepted bytes. This
   candidate has not been accepted/promoted or folded into the fast-transfer
   pin. No full suite, interruption/durability, checked-mode hardware or new
   wire-protocol qualification follows from these four successful downloads.

[Machine-readable results and raw receipt hashes](DOWNLOAD-EVIDENCE.json)
retain exact numbers and scope. Raw data, immutable build manifests, source
worktrees, helpers, input/output files and central release observations are
retained in the ignored local run record identified by `HARDWARE.local.md`.
Consumed helper/output paths are evidence, not an automatic rerun instruction.
