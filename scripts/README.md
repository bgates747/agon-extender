# Host tool index

Start with the [handbook](../docs/README.md) for current operation. This index
separates maintained operator clients from build, review and historical test
helpers. A filename such as `prepare_*` or `qualify_*` does not identify the
currently installed firmware or a ready-to-run qualification procedure.

## Existing-installation clients

| Tool | Purpose and maintained instructions |
|---|---|
| [sdcard.py](sdcard.py) | Mainboard-SD list/read/transfer through an already-running foreground EMOSlet; [SD guide](../docs/mainboard-sd.md) owns checked/fast options and journal recovery |
| [keyboard.py](keyboard.py) | Bounded agent input through previously admitted Extender input; [keyboard guide](../docs/remote-keyboard.md) owns arbitration, pacing and journal handling |
| [screen_text.py](screen_text.py) | Pixel-derived P4 text readback, not MOS RAM or Legacy display; [screen-text guide](../docs/screen-text.md) |
| [reset_agon.py](reset_agon.py), [reset_bridge.py](reset_bridge.py) | One Pi-actuated reset and optional browser bridge; [reset guide](../docs/bench-reset.md) owns configuration and effects |
| [prepare_mos_recovery.py](prepare_mos_recovery.py), [mos_recovery_console.py](mos_recovery_console.py) | Manifest-bound recovery payload and maintained programmer console; [ROM recovery](../docs/mos-recovery.md), not ordinary reset |
| [agentcoms.py](agentcoms.py) | Durable agent mailbox; machine-local `agentcoms.md` supplies participants/endpoints. Messages do not expand Author authorization |

Use the local project's Python environment on Linux. The operation guide covers
Mac clients and local journal paths. A command's `--help` describes syntax, not
current bench ownership, foreground state or firmware admission.

## Current build and local-validation entry points

| Tool | Scope |
|---|---|
| [vdp-pio.sh](vdp-pio.sh), [prepare_console.py](prepare_console.py) | In-place compile / clean isolated P4 bundle; [build guide](../docs/building.md) distinguishes local reconstruction from pending hardware equivalence |
| [package_installation.py](package_installation.py), [verify_installation.py](verify_installation.py) | Local draft packaging / extracted-package integrity; [production entry point](../production/README.md). Neither installs or selects a bundle |
| [reproduce_sd_components.py](reproduce_sd_components.py) | Isolated exact-hash EMOS/MOSlet reproduction using owning repositories; no deployment |
| [check_numeric_port.py](check_numeric_port.py) | Bounded pinned-input and sanitized host regressions; [import procedure](../docs/procedures/numeric-upstream-import-r01.md) still requires fresh source/target review |
| [validate-version-records.py](validate-version-records.py) | Registry/manifest structure and integrity; [version policy](../docs/versions/README.md). A passing validator does not qualify an artifact |
| [validate-hardware-objects.py](validate-hardware-objects.py) | Hardware vocabulary schema/references, not electrical qualification; [object authority](../hardware/objects/README.md) |

## Retained development and test helpers

These tools belong to their original bounded fixtures or studies. Before reuse,
review source, selected payloads, paths, mode setup, current input/service handover
and required observations in the owning task. Old LOAD/RUN listener recipes may
replace application memory and are not the current `EMOS sdserve` workflow.
The [procedure index](../docs/procedures/README.md) and
[example index](../examples/README.md) identify already-known refresh needs.

| Family / tools | Evidence owner and limits |
|---|---|
| [prepare_uart_forward.py](prepare_uart_forward.py), [prepare_uart_roundtrip.py](prepare_uart_roundtrip.py), [capture_uart_roundtrip.py](capture_uart_roundtrip.py) | PORT-009/010 historical paired transport diagnostics |
| [prepare_uart_flow.py](prepare_uart_flow.py), [capture_uart_flow.py](capture_uart_flow.py) | PORT-011/012 flow-control diagnostics |
| [prepare_general_poll.py](prepare_general_poll.py), [capture_general_poll.py](capture_general_poll.py) | PORT-013 retained-parser poll fixture |
| [prepare_visible_text.py](prepare_visible_text.py), [capture_visible_text.py](capture_visible_text.py), [prepare_text_sample.py](prepare_text_sample.py), [review_text_sample.py](review_text_sample.py) | PORT-014 visible-text and SD sample fixtures; review and physical capture are separate |
| [prepare_keyboard.py](prepare_keyboard.py), [capture_keyboard.py](capture_keyboard.py) | PORT-005 controlled-key sender; not general input acceptance |
| [prepare_usb_keyboard.py](prepare_usb_keyboard.py), [prepare_usb_cli.py](prepare_usb_cli.py) | PORT-015 USB acquisition/CLI candidates; not a replacement for current combined firmware |
| [prepare_browser_typing.py](prepare_browser_typing.py) | Earlier REMOTE-001 typing fixture, not the later browser-capture production interface |
| [prepare_console_review.py](prepare_console_review.py), [console_peer.py](console_peer.py) | PORT-008/PORT-003 real-EMOS/native-peer review composition; isolated profile and explicit review gates |
| [prepare_sd_headless.py](prepare_sd_headless.py), [qualify_sd_headless.py](qualify_sd_headless.py) | PORT-017 emulator/peer SD qualification, not physical proof |
| [qualify_sdcard.py](qualify_sdcard.py), [qualify_sd_keyboard.py](qualify_sd_keyboard.py) | PORT-017 physical-service tests; require commissioned service and reviewed test-root/startup contract |
| [qualify_keyboard.py](qualify_keyboard.py) | REMOTE-002 receiver/CLI qualification; known old listener handover requires refresh |
| [run_hello_demo.py](run_hello_demo.py) | DEMO-001 finite replacement/playback sequence; original installer/handover needs refresh |
| [measure_video.py](measure_video.py), [analyze_browser_timing.py](analyze_browser_timing.py) | Browser observation versus after-run timing analysis; presentation data is not renderer/game-loop performance |
| [rally_drive.py](rally_drive.py), [rally_trial.py](rally_trial.py), [rally_race.py](rally_race.py) | BENCH-001 and AgonArcade Rally protocols; task-specific live input, not generic automation |
| [qualify_rally_drive.py](qualify_rally_drive.py), [qualify_rally_headless.py](qualify_rally_headless.py), [qualify_rally_traffic.py](qualify_rally_traffic.py) | Local/emulator Rally checks with different scopes; none alone establishes hardware gameplay |
| [plot_rally_learning.py](plot_rally_learning.py), [report_rally_learning.py](report_rally_learning.py) | Archived-result visualization/reporting; no new run or benchmark implied |
| [bench_job.py](bench_job.py) | Detached remote command runner; only for an already-authorized, explicitly bounded bench job |

The documentation audit inspected tool descriptions and selected active contracts;
it did not rerun these historical helpers or certify their current deployment
readiness. Source and retained evidence remain available for an owner to prepare
a new bounded test without rediscovering the original purpose.
