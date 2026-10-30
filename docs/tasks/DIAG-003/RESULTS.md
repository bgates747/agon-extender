# External diagnostic extraction — offline results

The extraction recovers **2,947 ROM bytes** in both ordinary and controller
EMOS builds, with static RAM unchanged. VDPTEXT now builds as an external SD
utility; fake-adapter and resident text-test hooks are removed. Full builds,
host regressions and selected linked instruction checks pass. Installed
firmware, SD and startup remain unchanged; physical review is still pending.

EMOS implementation: `eebdd76`. Plan commits: Extender `b90e3169`, EMOS
`b63b956`. Builds used the latter plus the retained implementation patch;
all compiled firmware inputs match the final source or the identical reviewed
AgonDev adaptations on both sides of the comparison.

## Comparable ROM accounting

Ranked by least remaining ROM first. Both sides use the same
`UNVERSIONED-DO-NOT-DEPLOY` identity, build profile, toolchain and configuration.
Capacity is 131,072 bytes. Percentage change is `(after − before) / before × 100`.

| Composition | Before ROM, bytes | After ROM, bytes | Recovered, bytes | ROM change | After free, bytes | Static RAM before/after, bytes |
|---|---:|---:|---:|---:|---:|---:|
| Controller | 130,764 | 127,817 | 2,947 | −2.25% | 3,255 | 4,189 / 4,189 |
| Ordinary | 128,467 | 125,520 | 2,947 | −2.29% | 5,552 | 4,058 / 4,058 |

The installed named v0.1.27 image is 130,802 bytes / 270 free. Its longer
identity accounts for the 38-byte difference from the comparable unversioned
controller baseline; those 38 bytes are **not** counted as extraction savings.
These unversioned images are compile/review evidence, not deployment candidates.

| Changed controller object | Before ROM, bytes | After ROM, bytes | Recovered, bytes |
|---|---:|---:|---:|
| Resident text-test object | 1,587 | 0 | 1,587 |
| EMOS gateway/command/mode object | 6,548 | 5,597 | 951 |
| Keyboard object: unused diagnostic text writer | 3,383 | 2,974 | 409 |
| Total | 11,518 | 8,571 | 2,947 |

The 538-byte admitted UART diagnostic gateway and 2,199-byte controller module
are unchanged in size. Controller source/wire/client behavior is preserved;
this work does not claim savings from the separate controller-logic audit.

## External utility and compatibility

1. `/emos/vdptext.bin` retains `EMOS VDPTEXT` through the ordinary utility
   loader. The utility owns text validation, sequence, timing policy and
   reporting; EMOS retains Legacy/MOSlet admission, UART ownership and cleanup.
   No new resident operation, CRC, raw UART access or startup change is added.
2. VDPTEXT is 9,236 file bytes with 124 bytes of static RAM, ending at B2490.
   This leaves 23,408 bytes in the utility slot for heap/stack; it is not a
   worst-case stack measurement. UARTTEST and VDPPOLL remain 9,523 and 9,522
   file bytes. Exact artifact hashes are in [the metrics](results.json).
3. The diagnostic-only `edu.text-probe` service is retired. Historical
   visible-text/browser-typing fixtures require their original firmware;
   ordinary applications use MOS VDU output under EMOS routing. The obsolete
   fake adapter cannot select a route; `EMOS FAKE` returns unavailable.
4. Older fake/provider emulator scripts remain frozen. Their transcript-model
   unit tests are not current-image emulator qualification. No emulator was
   launched and no emulator profile, snapshot or SD mapping was changed.

## Validation and retained limits

1. Both complete EMOS profiles pass maintained wrapper builds and all mandatory
   linked UART, parallel, keyboard, console, gateway and VDU checks. The existing
   accountant reconciles binaries, ELF sections, maps and object totals exactly.
2. All 145 EMOS host tests and 42 Extender controller tests pass. The actual
   external text algorithm and resident transport pass 42 modeled scenarios;
   keyboard tests cover ordinary/telemetry/ExExt selections and an interleaved
   key/release during retained layout polling. Controller renderer tests pass.
3. Linked eZ80 checks pass: 298 diagnostic gateway cases, 21 UART reservation
   cases, and the controller receive-overlap/coherent-copy/Escape regression.
   These synthetic instruction arrivals do not measure physical UART latency.
4. Two stale host-test setup assumptions were repaired: the TX harness omitted
   the required inert startup binding, and the generated-assembly inventory
   omitted four already maintained private assembly leaves. No corresponding
   product behavior was added. Native sanitizers run outside the sandbox's
   ptrace restriction.
5. Utility timing retains nominal 120/600/24-unit TX/RX/quiet limits and the
   stopped-clock fuse. Gateway overhead changes polling cadence. No physical
   timing, keyboard coexistence, utility invocation or flash is claimed.
6. Exact installed baseline, before/after builds, prepared source snapshots,
   provenance, utility bytes, host logs and linked logs remain in ignored
   local evidence. Source/metadata commit identities are recorded in the task
   closeout; selected production and rollback remain unchanged.
