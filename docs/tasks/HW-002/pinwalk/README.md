# Keyboard-free header pinwalk — experimental diagnostic

`header-pinwalk-boot-r01` implements the requested cold-boot launch under
BC-001. The original SD `/bin/pinwalk.bin` remains unchanged. The separate
boot copy is `/bin/PWBOOT.BIN`, with its build manifest in `/bin/PWBOOT.yaml`.

The GPIO assembly and header are copied unchanged from the legacy generic
pinwalk, utility commit `4485e44`, under GPL-3.0-only (see LICENSE). The new
C entry displays its full build ID and experimental status, selects stock
VDP mode 3, releases GPIO, waits approximately five seconds using `clock()`,
emits one walk, releases GPIO and returns to MOS. No keypress is required.
The former I2C exercise is omitted. The unchanged assembly still exercises
PD4–PD7 and PB5 in addition to PC0–PC7, preserving PD0–PD3 and PB1.

Research used stock `agon-docs/docs/MOS.md` for boot precedence and LOAD/RUN,
`docs/mos/API.md` for the MOS clock sysvar, and installed agondev `time.h` for
`clock()` and `CLOCKS_PER_SEC`. The delay follows MOS time, not a calibrated
wall-clock timer. If that clock stops, the fixture waits with pins released.
P4-side connected pins must be inputs before the operator starts the walk.

Build using the project `.venv/bin/python` and `build.py`. It creates a UTC
build ID and experimental manifest with source/binary hashes; it does not
deploy. Generated binaries, objects and the identity header are ignored.

The [test sheet](../../../../hardware/designs/light2-harness-r03/tests/README.md)
owns the operator sequence. `capture.py` runs on the workstation, using the
ignored `agents/bench/hw002-pinwalk.json` for SSH and tool paths. It stages
`capture-on-pi.sh`, selects exactly one FX2 analyzer and captures 60 seconds
at 100 kHz. The operator resets the Agon when prompted. The prompt confirms
a live capture process, not a hardware trigger acknowledgment; the fixture's
boot delay provides margin. Neither script resets a processor or drives GPIO.

The runner retains raw evidence, verifies transfer hashes and exact capture
length/rate/channels, then invokes the retained generic analyzer with the
confirmed eight-color map. A pulse-count PASS is not UART qualification or
proof of P4 input mode. Failure evidence is retained. `capture.py --check`
checks Pi/analyzer availability without capturing.

A short capture with the expected rate/channels receives diagnostic pulse
analysis, but the runner retains an incomplete-acquisition failure result.
`capture-integrity.json` records expected and actual acquisition properties.

Preparation validation: warning-clean build, existing ADL audit, identical
copied assembly, Python/shell syntax, and Pi/analyzer discovery passed. The
new map also passes against the historical August 25 all-RGB trace. That
replay validates the map/tooling, not this new build or current assembly.
