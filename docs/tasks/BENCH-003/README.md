# Nurples cadence investigation

## Executive summary

This task separates application-loop pacing from received web-frame cadence using
one current repair derivative on the eZ80. Same mainboard CPU, different VDP route:
Legacy/mainboard and ExCom/P4. Web output requests are capped at30Hz. Results will
be published in RESULTS.md after the hardware controls complete.

## Reproduction components

1. `prepare.py --source PATH_TO_REPAIR --output NEW_DIRECTORY` builds the
   RAM-only diagnostic derivative and records its source hashes. Run with the
   Extender project-local Python. It does not modify the repair tree.
2. `observe.py` runs beside the existing `scripts/measure_video.py` on the wired
   receiver. Use that host's project-local Python, Chromium and Playwright.
   CLI: `--url ENDPOINT --output agents/NEW_RUN --seconds 120`.
3. `analyze.py PRIVATE_RESULT_DIRECTORY` reads `*-trace.bin`, paired
   `*-telemetry.bin` and `browser*/result.json`. It validates frame accounting
   and produces interval statistics; the controller separately checks vblank
   faults and unexpected output in no-web controls.
4. The frame record buffer is allocated after executable code, before runtime
   tables. `DS` reserves the samples without bloating the uploaded executable.
   Only the recorded sample count is valid; unused tail bytes of a full MOS SAVE
   are not initialized evidence and must not be interpreted or published.

## Hardware layout

| Role | Directory | Entry |
| --- | --- | --- |
| Normal production Nurples | `/mystuff/nurples` | `nurples.bin`, one vblank |
| Ordinary review Nurples | `/test/nurples` | `nurples.bin`, two vblanks |
| Bounded timing derivative | `/test/nurples` | `cadence.bin` |
| Production Rally | `/mystuff/arcade/rally` | unchanged |
| Test Rally | `/test/arcade/rally` | independent runtime copy |

The diagnostic batch selects EMOS routing, sets MOS mode3, changes to the test
working directory, loads/runs the derivative, saves its timestamp/telemetry memory
using exact symbols, returns to Legacy, and runs the existing SD service. No
startup-file changes, firmware flashes or resets. The normal game retains its
mode changes; the derivative is an actual application comparison rather than
an arbitrary new graphics-suite fixture.

Private controller/configuration and transfer journals are under
`agents/nurples-cleanup`; benchmark inputs and output definitions are frozen here.
