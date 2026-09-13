# BENCH-001 experiment record

## 1. Card workspace — 2026-09-13 05:32 UTC

The Author requested creation of `/codex` and changing into it, specifically
using keyboard commands so they could follow on the hardware screen.
Read-only status showed the SD service online and keyboard admission neutral.
The host sent Escape to return from the known final service, waited two seconds,
then typed these commands, allowing two seconds after each:

```text
MKDIR /codex
CD /codex
```

The keyboard client reported successful emission with no pending or held keys.
No SD API directory creation, reset, firmware change or program launch was used.
The intended terminal state is the ordinary CLI in `/codex`; the Author's
screen observation is pending. Emission alone is not filesystem/CWD proof.
The ignored host journal is under `agents/bench-001`.

The Author confirmed this result ("good"), then requested project and task
subdirectories beneath it.

## 2. Project and task directories — 2026-09-13 05:33 UTC

From the Author-confirmed `/codex` prompt, the host typed:

```text
MKDIR agon-extender
CD agon-extender
MKDIR BENCH-001
CD BENCH-001
```

All four commands were emitted through the keyboard path, with two-second
post-command pauses. Intended final directory:
`/codex/agon-extender/BENCH-001`. Screen confirmation remains pending; no SD
API mutations or other hardware actions were used.

## 3. Inspect installed commands

At the Author's request, the host typed `DIR /bin` through the keyboard
path for the Author to read on the Agon. No directory change or BASIC launch
was requested or performed. Keyboard emission succeeded; listing contents
have not been captured by the host.

The Author then requested `ls -l /bin` instead. The host typed that exact
command and Enter through the keyboard path; emission succeeded. The result
is for the Author to observe on the hardware screen.

## 4. Try BBC BASIC

The Author requested `bbcbasic`, believing it may be the desired ADL build.
The host typed `bbcbasic` and Enter through the keyboard path. Emission
succeeded; interpreter startup and ADL identity await screen observation.
No BASIC program has been entered.

The Author observed the expected v3 BASIC banner; ADL identity remains unknown
and was explicitly set aside for these experiments.

## 5. Hello world in BASIC

Before typing, consulted the local `agon-docs/docs/BBC-BASIC-for-Agon.md`
LOAD/SAVE extension notes and the linked Agon BASIC manual:
https://oldpatientsea.github.io/agon-bbc-basic-manual/0.1/bbckey3.html (PRINT),
https://oldpatientsea.github.io/agon-bbc-basic-manual/0.1/bbckey4.html (SAVE/RUN).
The Agon documentation specifies `.BAS` as plain text. Historical platform
identity statements in that manual do not identify the installed binary.

Typed through the existing keyboard path, pausing between lines:

```basic
10 PRINT "Hello, world!"
20 END
SAVE "helloworld.bas"
RUN
```

All commands were emitted. Intended save location is the current task folder,
`/codex/agon-extender/BENCH-001/helloworld.bas`; expected output is
`Hello, world!`. Save success and execution output await Author observation;
no independent file readback or interpreter exit was performed.

The Author reacted positively to the Hello World result ("absolutely nuts")
and requested this running log be maintained for later copying to the SD card.
This is positive attended feedback; no independent saved-file readback has
been performed. The log remains on the host until copying is requested.

## 6. Return to MOS

At the Author's explicit instruction, the host typed `*BYE` and Enter through
the keyboard path. Emission succeeded with no pending or held remote keys.
Expected result: exit BBC BASIC to the ordinary MOS CLI. Screen confirmation
remains with the Author.

The Author confirmed the expected return to MOS after `*BYE`.

## 7. Open nano for assembly editing

The Author proposed writing an ez80asm-compatible Hello World through nano,
but explicitly limited the initial action to launching the editor. The host
typed `nano` and Enter, then stopped. The Author observed that nano requires
a filename and stated that filenames are relative to the current directory.
At their next instruction, the host typed `nano hello_world.asm` and Enter.
Keyboard emission succeeded; editor startup awaits Author observation. No
assembly text, save command or assembler invocation has been entered yet.

## 8. Type the assembly source

At the Author's request, typed the following 26 lines into nano and stopped.
It uses ADL mode, the ordinary MOS header at offset 0x40, the stream-output
RST, and returns success in HL. Local assembly conventions and MOS API/header
references were checked. All line submissions succeeded; editor contents have
not been read back. No save, exit, assembly or execution command was sent.

```asm
.assume adl=1
.org 0x040000
jp start
.align 64
db "MOS",0,1

start:
push af
push bc
push de
push ix
push iy
ld hl,message
ld bc,0
xor a
rst.lil 0x18
pop iy
pop ix
pop de
pop bc
pop af
ld hl,0
ret

message:
db "Hello, world!",13,10,0
```

## 9. Nano save/exit reference (no keys sent)

Found Lennart Benschop's nano in the local read-only `agon-utilities` checkout.
README.md's nano section documents Ctrl-O save and Ctrl-X exit. nano.asm
`do_save`, `do_exit` and `Save_File` clarify the interaction: Ctrl-O prompts
with an editable existing filename and returns to editing after saving;
Ctrl-X or Escape, when modified, asks `Save file (Y/n)` before the filename
prompt. Only n/N skips saving in this source; Enter selects saving, followed
by another Enter to accept the current filename. Installed binary equivalence
to this source has not been established. No save/quit keys were sent during
this documentation lookup.

## 10. Save first, then exit nano

The Author confirmed the documented interaction and requested separate save
and exit steps. The host sent Ctrl-O, waited two seconds, sent Enter to accept
`hello_world.asm`, waited three seconds, then sent Ctrl-X. All sequences were
emitted successfully. Save and return-to-CLI observation remain with the Author;
no assembly or program execution was performed.

## 11. Assemble on the Agon

At the Author's instruction, typed `ez80asm hello_world.asm` and Enter.
Keyboard emission succeeded. Expected output is `hello_world.bin` in the
current task directory; assembler diagnostics and success await the Author's
screen observation. No binary execution command was sent.

The Author confirmed assembly succeeded ("wow it worked").

## 12. Load and run the assembled program

At the Author's request, typed `LOAD hello_world.bin`, allowed two seconds
for this small binary to load, then typed `RUN`. Both keyboard submissions
succeeded. Expected output is `Hello, world!` followed by return to MOS;
execution output awaits Author observation.

The Author confirmed execution succeeded ("success"). This completes the
attended nano → save → ez80asm → LOAD → RUN Hello World experiment on the
physical Agon, using host keyboard input for every on-device step.

## 13. Drive Rally through the keyboard

The Author requested launching Rally and actually driving it. Consulted the
production usage and controls: Up accelerates, Down brakes, Left/Right adjust
persistent steering; `race` disables the opening demo driver.

Typed `CD /mystuff/arcade/rally`, `LOAD rally.bin`, then `RUN . oval race`,
with pauses for loading and startup. Sent Up held for four seconds; Left,
Right, Right, Left each held about 0.1 seconds with two-second coasting pauses;
then Down held for five seconds. The host renewed leases during holds and
released all remote keys afterward. No Escape was sent; Rally remains the
intended foreground program.

This was explicitly blind, open-loop input, not a visual or telemetry-based
driver. Keyboard submissions succeeded; lane position, observed motion and
successful braking await Author feedback. No demo/autosteer option, new
firmware, reset or game modification was used. The source of the control
sequence and machine journal remain under ignored `agents/bench-001`.

The Author reported the blind drive left the road to the right in the first
turn within about three seconds and never recovered. This confirms visible
control response, not successful driving. The Author then selected resident
interrupt-driven telemetry and authorized the goal recorded in BENCH-001,
with a speed-linked sine engine tone and the final actual hardware driving
run as the wake-up cue. This is a new bounded unattended phase of the ad hoc
work, not permission to resume unrelated Rally/Golem optimization.

## First feedback-controlled physical Rally run — 2026-09-13

The Author restored hardware access, requested immediate physical driving at
200% grip, and asked for preserved telemetry. A 30-minute learning/practice cap
excludes debugging and deployment by explicit clarification.

The host installed identified draft P4 r16 and EMOS v0.1.15 bench composition,
using the already working keyboard/SD/Pi reset paths. P4 flash was preserved
before replacement and independently verified afterward. Its previous image
identified r15-b2026-09-13-04-55-55Z. Onboard VDP was unchanged. MOS SAVE preserved
full 128 KiB before/after mainboard ROM files on the card; a small SAVE of the
new ROM's build-identity address was downloaded and matched the selected image.

At the real CLI the host ran these commands separately, allowing each to finish:

```
CD /mystuff/arcade/rally
LOAD /codex/agon-extender/BENCH-001/rally.bin
RUN . oval race telemetry engine grip200
```

The external host controller actuated ordinary left/right/up/down transitions.
Game telemetry reported manual mode, corner assistance disabled, 200% grip and
engine enabled. First 60-second physical run: 514 observations, every sample
on road, no kerb/grass sample, 25,159.36 world units (4.368 oval laps), maximum
absolute lateral error 4.727 world units. Rendered-update rate was 8.575/s;
this is instrumented physical behaviour, not the historical baseline's rate.
Engine commands are present and enabled; audible/visual human acceptance is
separate. The first run used about one minute of the learning budget.

Exact JSONL snapshots include the CRC-protected wire payload, receipt age,
sequence, game-observed keys, host-requested keys and controller targets. The
host retained summaries, source hashes, keyboard journals and firmware/card
provenance in its ignored BENCH-001 run directory. A subsequent run continues
physical driving; no commit/push or emulator attention cue was performed.

Deployment gotcha: sending LOAD and RUN as one typed batch did not start
sdserve on the real CLI. Releasing keys, exiting with Escape, and sending each
command separately with a one-second completion allowance restored service.
Do not equate the P4's emitted-event count with completed CLI execution.

## Traffic extension and test lifecycle

The Author heard the engine, found it obnoxious, and explicitly requested no
audio change. Speakers are muted; future attention cues use an emulator beep.
The second physical run's 11 grass and two kerb samples occurred entirely in
its first 1.51 seconds, recovering from coasting between runs. After three
seconds its maximum lateral error was 12.54 world units. A quick Escape tap
was subsequently missed between game polls; a held Escape returned to the CLI
and sdserve restarted. Full before/after 128 KiB ROM files were downloaded;
the entire installed v0.1.15 image prefix matched the frozen candidate.

The Author requested faster driving and opponent avoidance. V2 reports all six
opponents plus physics-tick overlap entries, with an explicit conservative
contact proxy and no gameplay collision response. The controller predicts lane
and speed choices through ordinary keys. A delayed-input test exposed failure
to account for the previously requested key batch; including that pending input
removed the observed overlap. Four 60-second actual-Motion tests now pass: oval
21 passes, Fuji six, delayed input 20, and a three-abreast blocked road with no
passes. All four had zero contacts/grass; open-road cases reached speed 300.
The blocked case reached only 192 and waited behind traffic. These are local
simulations, not physical results. Decision computation took at most 4.7 ms.

The v2 headless real-eZ80 run with the physical 200 ms gate rejected delayed
telemetry. A second explicitly labelled 350 ms emulator-only diagnostic allowed
30 seconds of control: zero contacts but 36 grass samples, so it failed driving
acceptance. The retained native UART model lacks TX-empty interrupt demand;
144-byte packets drain through VBlank kicks and report old state. The physical
driver retains 200 ms, and no emulator or ISR was changed to hide this result.
Both informative failures are retained. Next evidence is a bounded physical run
with automatic fresh start and held-Escape exit, not an assumed emulator pass.

## Centre preference and longer physical trial

The Author requested centre-line driving for spectators. The controller's
centre cost is now 2.0 per world unit, above the 0.35 lane-change penalty;
contact/road-edge risk still ranks ahead of progress and lane preference. Both
immediate and one-frame-delayed keyboard application are forecast. The current
corner reserve is 0.72. A local uneven-frame case still produced one contact;
this is exploratory driving evidence, not a universal collision-free guarantee.

The 2026-09-13 08:15:23 UTC physical trial completed 300.08 seconds at 200% grip:
2,244 road observations, zero kerb/grass observations, zero overlap entries,
98 passes and 35 clean laps. Best interpolated lap was 8.00 seconds, the oval's
full-speed floor for the current physics. Average absolute centre distance was
11.56 world units by sample, or 12.01 weighted by observed MOS-clock intervals.
The car spent approximately 77.3% of observed time within 16 world units of
centre on the 180-unit-wide road, and targeted centre for 78.3% of the time.
It still moved aside to pass traffic. Multiple parameters changed since the
previous trial, so this is not an isolated causal comparison of centre cost.

All controller source, wire snapshots, choices, lap crossings and journals were
preserved. Held Escape ended telemetry automatically. Subsequent trials restart
from the CLI. The instrumented game's roughly 7–8 observations/second are not
measurements of the accepted production game's frame rate. The physical
freshness bound is explicitly 300 ms now; the earlier 200 ms statement above
is historical. No game binary, EMOS, P4 or onboard VDP changed during this
controller adjustment; engine tone remains as requested.

## Completed 200% practice block

The first15-minute block ended with900.09 seconds of recorded driving/cleanup:
102 completed laps, all clean,299 passes, zero overlap entries and zero grass
samples. Best and median interpolated lap times were8.00 seconds. Six kerb
samples belonged to the first, older-controller run. All completed trials
returned to the CLI; the initial timeout needed same-session cleanup, later
exits were automatic. The final full300-second run with the cut-in guard had
98 passes and zero kerb/grass/contact observations. Its time-weighted absolute
centre distance was13.10 world units;72.6% of observed time was within±16.
The brief final11.73-second fresh-start trial consumed the remaining allowance;
its starting traffic pass dominates its centre metric and no lap completed.

The180% block started next. Each block has a900-second ceiling, with at most
small cleanup/loop timing overshoot recorded honestly. An unattended local
wrapper advances only these explicit blocks, refuses changed controller sources,
and stops on a trial error, unresolved release or unconfirmed game exit. It
never resets/flashes or forces input ownership. Run/controller snapshots and
raw wire evidence remain in the private bench record. No overnight alert.

The first180% physical segment completed300.06 seconds,34 clean laps,93 passes,
zero contacts/grass/kerb and an8.00-second best lap. Held Escape/telemetry-stop
checks passed. A deliberate between-run pause installed the programme wrapper's
pace-selection policy; no active driving was interrupted. The remaining180%
segments retain0.72 corner reserve. At160% and140%, compare five minutes at0.72
with five minutes at0.80/0.84 respectively, then use the cleaner/faster observed
choice for the final five minutes. All six actual-Motion cases passed locally
at each of those faster settings before physical use. No changed grip, physics,
traffic layout or direct state writes hide the increased throttle commitment.
Controller source stays frozen throughout these wrapper-selected trials.

## One-then-two steering comparison

The Author requested a one-tick trial followed by two, rejecting the aggressive
three-tick response; passing must outrank centre preference on either side.
The third180% segment stopped deliberately at63.53 seconds,23 passes and no
contact/grass; it returned to the CLI through normal cleanup. This is an Author
interruption, not a runtime failure. The remaining practice allowance is retained.

The new135899-byte steering candidate builds with steer1/steer2/steer3, default2,
while preserving±21 bounds and all existing artwork. The host reads snapshot
byte78 and uses current-angle-relative quantization: clipping a two-tick motion
at±21 changes its attainable parity. Six actual-Motion cases pass for both1
and2 at180% grip, zero contacts/grass. Separate bounds/reversal tests cover
one versus32 elapsed physics ticks, opposing held keys and both endpoints;
steering changes exactly once per frame in each case. Passing ranks risk,
progress, then centre/lane-change cost. Firmware transport is unchanged.

The separate steering.bin upload, staged readback and activated readback passed;
sdserve exited. Source, binary, controller and host tests were archived. The
one-tick90-second physical trial started08:57:28 UTC at180% grip, followed by
the requested two-tick trial. Their actual results follow after completion.

Both physical comparisons completed and automatically quit. At180% grip and
0.72 corner reserve, step1 (08:57:28 UTC) ran90.095s:684 road samples,31 passes,
10 clean laps, best8.043s. Step2 (08:59:21 UTC) ran90.065s:675 road samples,
31 passes,10 clean laps,best8.108s. Neither recorded contacts,kerb or grass.
Time-weighted absolute centre distance was10.44 versus11.05 world units;
76.2% versus75.5% of observed time lay within16 units of centre. These short
trials do not resolve a lap-time advantage: crossing uncertainty is133–167ms
and traffic encounters differ. Two ticks remains the candidate default for
the remaining grip blocks. Passing progress now outranks centre preference;
safety and the nearby-opponent cut-in guard remain ahead of either.

## Bounded programme completed

All four requested grip blocks ended after3600.066recorded seconds,399clean
laps and1108passes,with zero contact entries/grass samples. Final140% block
recorded96clean laps,244passes,best8.479s. Every trial exited; the detailed
comparison, source hashes and plot are in PRACTICE.md and evidence/driving-hour.*.
A post-practice ROM/SD recovery audit is running from the confirmed EMOS prompt;
no further learning runs will be started under this allowance.

## Final native v2 qualification and UART-model diagnosis

The fixed current-candidate run in the old RX-only model fails with45grass
observations and two contacts, despite the current300ms freshness check.
A separate stationary trace exposes median134.260ms packet assembly at the
host. This diagnosis is independent of steering. The reusable mos-agondev
TEST-002 task implements a datasheet-supported opt-in UART1 TX interrupt/IIR
correction; default model and old failures remain preserved.

With unchanged Rally, EMOS, controller, step2, grip200 and300ms bound, packet
assembly falls to median2.180ms in the stationary trace. Two fixed40-second
drives pass. The final run records660manual road observations, four clean
laps and12passes without contact, kerb or grass, then proves later guest key
release and normal application exit. HEADLESS-CLOSEOUT.md owns exact evidence
and caveats. No new physical test, gameplay tuning or practice-time extension
occurred. B01-09 is machine-complete; human review remains separate.
