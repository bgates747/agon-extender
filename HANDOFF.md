# Extender handoff — 2026-09-19

## Executive summary

Since the returning agent's last conversation on **September 11 at 17:45 America/New_York**, development has concentrated on making the bench remotely operable, bringing EMOS/EDP UART throughput up to stock, qualifying graphics correctness, and investigating browser-output performance. RLE2 remains the preferred 64-colour browser codec; compressed output materially improves delivery, but 60 fps at 512×384 is not established. A direct ExCom screen-text endpoint now lets an agent inspect the display without displacing the human's browser connection.

**The next discussed work is browser keyboard capture/release, planned but not implemented or released for execution.** Read `docs/tasks/REMOTE-001.md`. Preserve the installed candidate and uncommitted screen-readback implementation before changing anything. This handoff is orientation, not a replacement task list or new hardware authorization.

This summary combines session history with a read-only Git/document review. The cutoff is September 11, 2026, 21:45 UTC. Git dates and conversational milestones are not necessarily installation dates.

## Repository and bench state

Publication note: the snapshot below predates the Author's subsequent instruction
to commit the outstanding work in discrete groups and push main. Screen-text
source, planning documents and this handoff are included in that publication;
the dirty/untracked descriptions below preserve the original handoff state.
Use current Git status for repository state. Installed firmware provenance and
the planning-only boundary are unchanged.

1. Extender is on `main`, HEAD `663eb536`. It is **50 commits ahead of the locally recorded origin/main** and has dirty/untracked work. No fetch was performed for this handoff; recheck before publication.
2. Sibling `~/Agon/mystuff/agon-emos` is on `main`, HEAD `26ba877`, clean and aligned with its recorded origin/main. EMOS is the replacement MOS firmware, not a second MOS running alongside stock.
3. Read `AGENTS.md`, the canonical `../agon-dev-env/codex/AGENTS.md`, and `HARDWARE.local.md` before bench operations. Private addresses, SSH identities and wiring readiness belong in the ignored hardware record, not this file.
4. Last verified bench state from this session: mainboard stock VDP, EMOS, **ExCom MOS prompt**, with the human able to watch browser output. The P4 carries screen-text candidate `screen-text-r01-b2026-09-19-09-47-04Z`. This handoff did not query or disturb hardware; verify current ownership/state before operating it.
5. Installed firmware is a preserved candidate, **not simply a build of repository HEAD**. Consult `agents/screen-text/manifest.json`, `docs/tasks/BENCH-006/BUILD.json`, and its retained source overlay. Prior rollback is under `agents/pair-rle/`. Candidate codec work also lives under ignored `agents/rle2-execution/`; do not discard ignored artifacts or assume all experimental code was promoted into maintained sources.

## Brief history and decisive findings

1. **Remote bench operation.** PORT-017 established mainboard SD read/write over the existing Extender wiring, with recovery and native keyboard acceptance. Routine contracts are now `docs/mainboard-sd.md`. Journaled keyboard injection, Pi reset control, spoken notifications, and ad hoc CLI experiments followed. The agent demonstrated BASIC and assembly development directly through keyboard commands. These tools removed repeated physical SD swaps. See commits `5ad7a73d`, `57dc513d`, `d86739bf`, and BENCH-001.
2. **Rally and telemetry.** The agent added telemetry-driven driving and collision-avoidance experiments, while Rally developed splash screens, qualification/race phases and HUD improvements. The maintained game was subsequently promoted to AgonArcade main. Golem is explicitly out of scope/on hold. Production programs belong under `/mystuff`; modified fixtures under `/test/nurples` and `/test/arcade/rally`. Nurples reference is **nurples-repair**, not an older duplicate.
3. **UART alignment and EMOS optimization.** Stock comparisons identified sender/receiver overhead and P4 reply-order/owner-loop differences. Changes restored bulk reads, RX timeout behaviour and reply ordering, then optimized bounded EMOS transmit/receive paths, including assembly where justified. INTEG-014 E07P reached scoped bulk parity on physical hardware in ordinary and bench profiles. Ordinary forward: mainboard **589.670 ms**, P4 route **588.096 ms** for 65,535 bytes; return: **86.068 vs 85.156 ms** for the defined 2,048-byte/256-packet workload. Short-command overhead remains. Authority: sibling `agon-emos/docs/tasks/INTEG-014/E07P-results/README.md`; do not generalize these results to all graphics operations.
4. **Recovery and resource pressure.** A failed MOS installation was recovered using the P4/ZDI method. The maintained protocol is `docs/mos-recovery.md`; the WROOM proposal was not the working method. The user subsequently confirmed reset/recovery/sniffer/normal wiring remained connected. Recorded EMOS link-budget comparison: 136 flash bytes free with parallel support, 3,174 without; same-toolchain stock 29,017. These are historical linked candidates, not an automatic current-build assertion.
5. **Graphics/API repairs.** Rally exposed invalid float-to-integer conversions on P4; safe conversion guards and upstream-import checks were added. Audio command consumption, rather than rendering itself, caused another visible HUD failure; retaining stock parsing with an unavailable audio backend fixed framing. Newest-viewer takeover was qualified. Mainboard/P4 timing suites and command-consumption audits are under PORT-003, PORT-008 and QUAL-003; keep their scope/exception distinctions.
6. **Rendering versus output.** QUAL-003 investigated locks, task scheduling, snapshot ownership, core placement, cache/memory questions, output-load ladders and standalone P4 output. RTOS experiments included confounded/rejected candidates; read results rather than reinstating a promising-looking patch. Research candidates are in RESEARCH-001. User accepted approximately 30 fps as the practical 512×384 browser target for now; this is not a 30 Hz renderer guarantee or a universal browser cap.
7. **Physical pixel correctness.** QUAL-004 matched **66 static scenes / 12,616,704 pixels with zero differences** between mainboard and P4. It remains open pending exceptions: stock sprite-capture crashes, P4 Copper/mode-transition restarts, and deferred coverage. Missing APIs were catalogued, not implemented. Read `docs/tasks/QUAL-004/{RESULTS,COVERAGE}.md`. Neither exhaustive API parity nor dynamic scanout equivalence is claimed.
8. **Codecs and browser UX.** RLE2, SRLE2/SZIP options, indexed PNG, RGB888 JPEG, six-bit packing and pair-RLE were investigated. For one matched Nurples 60-cycle/s fixture, browser receipt improved from **8.25 fps raw to 24.55 fps RLE2**, with both maintaining 60 application cycles/s. A different earlier 30-paced trial reached 29.18 browser fps; do not mix it into an apples-to-apples comparison. SZIP/PNG/JPEG encoding costs did not establish a better live-streaming replacement. Six-bit and pair-RLE experiments were retained but Nurples favoured existing RLE2. Main evidence: `docs/tasks/QUAL-003/debrief/P01h/`, especially `60fps/RESULTS.md` and `codec-screen/`. Fullscreen controls were added outside the video image.
9. **Latency and composed packing.** BENCH-005 measured 76.1 ms median injection-to-browser-submission with a 30 fps request cap versus 42.1 ms without that delay in a small 320×240 control. That is not physical-key-to-monitor latency. Browser cap was subsequently raised to 60; user found mode 20 noticeably better than mode 0. Composed low-colour packing and a 54-mode sweep followed; six-bit/pair experiments did not displace RLE2 for Nurples. See BENCH-005 and its linked continuation records. Discussion alternatives/rejections live in `docs/tasks/BENCH-005/OUTPUT-IDEAS.md`.
10. **Alex and screen observation.** Alex is a local Qwen agent in `~/Projects/alex-ai`. Its experiment now has terse `connect.md`, `typing.md`, `read-screen.md` under `experiments/alex-control-agon/`. BENCH-006 implemented `GET /screen/text` and `scripts/screen_text.py`: HTTP capture through the console owner, no SD service, no eZ80 helper load, no video WebSocket takeover. One 80×60 capture took 2.20 s. Glyph recognition is font/colour dependent, non-atomic and imperfect at edges/non-ASCII; it is not a true text backing-store dump. Legacy readback remains follow-up work; a MOSlet must stay within MOSlet memory and preserve any loaded application.
11. **Future hardware.** RESEARCH-004 led to an Olimex P4-PC backorder; P4PC-001 records purchasing/integration/breadboard plans. Separate parallel-audio feasibility work exists. These are not replacements for the current bench or permission to start new implementation.

## Core changed files to inspect

These are selected functional files changed since the cutoff or currently dirty, not an exhaustive inventory. Paths below are repository-relative.

### EMOS — sibling agon-emos

| Files | Role |
|---|---|
| `src/emos.c` | EMOS integration and service dispatch |
| `src/emos_keyboard.c`, `src/emos_keyboard.h`, `src/emos_keyboard_io.asm` | Processed-key/return parser and optimized UART transfer paths |
| `src/uart.c`, `src/uart.h` | UART integration |
| `src/emos_sdlink.c`, `src/emos_sdlink.h` | Mainboard SD service transport |
| `src/emos_telemetry.c`, `src/emos_telemetry.h` | Application/bench telemetry |
| `projects/sdserve/src/{main.c,service.c,service.h,emos_gateway.asm,sd_wire.h}` | Resident-while-running SD service application and wire contract |
| `port/{mos-agondev.mk,bench-telemetry.mk,parallel-fixed-qualification.mk}` | Build/profile composition; inspect before comparing size or timing |

### EDP/P4 — this repository

| Files or directory | Role |
|---|---|
| `vdp/video/extender/transport/{console_hardware.inc,console_stream.hpp}` | Stock-shaped console ownership, UART reads/replies; latest screen polling hook |
| `vdp/video/extender/input/{remote_keyboard.hpp,remote_target.hpp,usb_cli_keyboard.hpp}` | Host-injected and USB processed-key path |
| `vdp/video/extender/storage/{sd_service.hpp,sd_target.hpp,sd_wire.h}` | P4 side of SD service |
| `vdp/video/extender/network/wired_network_service.{cpp,hpp}` | HTTP/WebSocket service, viewer ownership and output; current screen endpoint integration |
| `vdp/video/extender/network/screen_text.hpp`, `vdp/video/context.h` | **Uncommitted** screen-text capture state and font access |
| `vdp/video/extender/display/{stock_p4_service.cpp,stock_p4_service.hpp,stock_runtime_controller.hpp,stock_scanline.hpp,presentation_snapshot_pool.cpp,presentation_snapshot_pool.hpp,rgb222_row.hpp,drawing_cadence.hpp}` | Rendering/snapshot/composition and pacing work |
| `vdp/vendor/vdp-gl/src/{displaycontroller.cpp,displaycontroller.h,dispdrivers/vgapalettedcontroller.cpp}` | Retained FabGL port/scheduling integration; compare carefully with stock |
| `vdp/video/extender/port/{fixed_conversion.hpp,numeric_conversion.hpp}` | Explicit safe numeric conversions |
| `vdp/video/{vdu.h,vdu_audio.h,vdu_buffered.h,vdu_sprites.h}`, `vdp/video/extender/audio/unavailable_audio_adapter.hpp` | Parser/graphics compatibility and audio-byte consumption |
| `vdp/video/extender/web/{app.js,frame_protocol.js,index.html,style.css,protocol.md}` | Browser decode/display/fullscreen/wire protocol; compare installed candidate as well as HEAD |
| `vdp/video/extender/recovery/mos_recovery.cpp` | P4-assisted MOS recovery |
| `vdp/platformio.ini`, `vdp/pio/select_sources.py` | Candidate/build composition |
| `scripts/{keyboard.py,sdcard.py,bench_job.py,reset_agon.py,screen_text.py}` | Routine host control; last file currently untracked |

## Immediate continuation and preservation

1. Read `TODO.md` and `docs/tasks/REMOTE-001.md`: explicit Capture/Release, released by default, cleanup on focus loss/disconnect, bounded ownership alongside physical/agent input. ADR-0022 records accepted partial decisions. Transport, repeats and ownership details still need resolving. The user requested this plan only, then moved to this handoff.
2. Preserve all current dirt: BENCH-006 code/evidence, REMOTE-001/ADR-0022, BENCH-005 discussion notes, P4PC-001, RESEARCH-004 updates, TODO and September 19 development log. This handoff adds another uncommitted file. Do not stage unrelated changes indiscriminately or infer publication approval.
3. Alex instruction files deliberately omit history/private host paths. Leave its README, NOTES and gitignore unchanged. Do not submit Alex prompts on the user's behalf. The browser sandbox has deliberate host-network access; a read-only filesystem mount does not imply networking is disabled.
4. Keep ExCom available for the user watching remotely. Screen inspection should use `scripts/screen_text.py`, not steal the video WebSocket. Read private bench configuration for invocation details. No hardware notification was requested for this handoff.
5. Agent communication is documented in ignored `agentcoms.md`; check the mailbox as local AGENTS requires. This session remained attached to Pynvaders in the desktop app even while working here. The user is moving back to a correctly associated Extender task; desktop link routing through the Mac Samba mount is unresolved.
