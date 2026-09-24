# RESEARCH-003 — Standalone P4 rendering and Ethernet reference experiment

## Current-state clarification — 2026-09-20 queue review

The candidate-left-installed statement below describes this experiment's own
review handover, not today's bench. Later experiments and recorded restorations
supersede it as an installed-state description. The twelve-run research result
still awaits disposition; no rerun or new deployment is implied.


## Executive summary

Author authorizes replacing the bench P4's VDP application temporarily with a
P4-targeted reference firmware to isolate concurrent rendering and Ethernet
delivery. Start with Espressif, reuse RESEARCH-001/002, then inspect independent
implementations. The target is 512×384, 64 colours, 60 distinct complete frames/s;
one-byte-per-pixel output remains a separate hard goal for future 256 colours.
Published codec or LCD rates are not network qualification.

This contract is frozen before implementation. All new experimental firmware,
host scripts and configuration live in `docs/tasks/RESEARCH-003/`; generated
builds, downloaded dependencies and private bench records there are ignored.
No production source changes, MOS/mainboard VDP flashing, Golem or push.

## Authorization and boundaries

The Author requested a new task, freeze and execution, with Espressif-first
research and freedom to use HTTP control without Agon integration. This
authorizes task-scoped builds, temporary P4 deployment and measurement with
the existing wiring. Preserve and verify the installed baseline before any
write; retain it for verified rollback. Do not assign any
GPIO from an external board example without checking the local harness.

No requirement to manufacture a successful candidate: if none advertises a
comparable measured workload, record that explicitly. A minimally adapted
official HTTP/Ethernet example with a deterministic software producer is a
permitted diagnostic fallback, clearly labelled our fixture, not upstream
performance. Avoid external camera/LCD requirements absent on this bench.

## Itemized execution plan

1. [x] R01 — Reuse prior candidate evidence; inspect Espressif first then
   independent P4 firmware. Record claims, target/revision, licence, dependencies,
   physical requirements and reasons for selection/rejection; pin reused code.
2. [x] R02 — Freeze selected design and exact build inputs in this silo.
   Use no VDP/FabGL/parser, no Agon control requirement. HTTP starts bounded
   tests and returns status/results; network receiver validates sequence and
   pixels. Separate deterministic rendering from immutable output ownership.
3. [x] R03 — Build and host-validate protocol, pixel reference and error paths.
   Preallocate buffers, bound waits, record memory/clocks/task placement and
   output fidelity. Inspect pin assignments and preserve rollback artifacts.
4. [x] R04 — Deploy with stable USB identity/readback verification. Run
   render-only, send-only and combined controls using the same deterministic
   animation. Test 30 and 60 fps targets, with full-frame output as primary;
   any smaller/compressed variants explicitly separate. At least two repeats
   of decisive cases; stop escalating on corruption/reset and retain evidence.
5. [x] R05 — Report rendering ms, completed/received unique fps, payload Mbit/s,
   p50/p95/max intervals, drops, correctness and elapsed durations. Do not claim
   browser presentation from a socket receiver or VDP parity from a new workload.
6. [x] R06 — Record results, limits and installed firmware identity; notify
   through an emulator with the accepted spoken cue and stop for review.
   Preserve a healthy test image for review rather than restoring Extender
   solely to obtain Agon control for notification. Keep verified rollback ready;
   restore the baseline if required for recovery and record that distinction.

Author amendment after contract freeze: use an **emulator** notification at the
conclusion so the installed test firmware need not be disrupted to control the
Agon. This supersedes the original hardware-voice/restoration closeout, without
relaxing image preservation, deployment verification or recovery requirements.

## Measurement contract

Use wired receiver and a changing full-frame deterministic pattern with frame
IDs; no retransmitting one static buffer counted as rendering. Separate setup
and timed windows, include warmup, count missed producer deadlines and receiver
sequence gaps. Use bounded runs and durable progress/result files; validate
payload bytes outside timed hot paths when feasible and disclose validation
cost. Account for framing overhead separately from pixels. No fabricated fps
from configured camera/display rates. Compression, if selected, must report
encoding/decoding cost and lossiness; no substitution for exact-pixel success.

## Review and change control

Granular local commits preserve contract, implementation and findings. Newly
discovered changes to the plan must be marked agent-assigned with rationale;
they cannot silently enlarge hardware or production scope. P01h remains
separately queued. Existing research: RESEARCH-001/C1–C5, RESEARCH-002 and
QUAL-003/P01g. Hardware details stay in ignored local records.

## Execution checkpoint

Twelve runs complete; [results](RESEARCH-003/RESULTS.md) show47.02–47.29fps
combined exact raw output,49.59–49.60send-only,60render-only. All30fps cases
pass without drops.60fps delivery target unmet. Healthy standalone image remains
installed; emulator spoken cue issued with stage6/audio_commands=pass receipt.
Emulator left open; human hearing unconfirmed. No production edits or push.
