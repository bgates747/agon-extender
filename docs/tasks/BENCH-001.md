# BENCH-001 — Initial experiments

Status: Active goal for resident Rally telemetry, host driving and engine audio.
Started: 2026-09-13 UTC.

## Purpose and authority

The Author wants to see the agent use the real Agon CLI, rather than repeat a
typing demonstration. BENCH names live Agon bench operations. This first task
is deliberately ad hoc: the Author and agent will choose experiments together
as the conversation develops. The Author subsequently authorized the bounded
unattended goal below; earlier experiments remain in the running log.

The initial creation instruction was documentation-only. Subsequent explicit
instructions authorized the recorded CLI experiments and the current goal.
The [introduction](BENCH-001/INTRODUCTION.md) records the starting position and
links to evidence; it is background, not a second task list.

## Working procedure

1. Select the next bounded experiment with the Author in chat. State the
   purpose, commands and expected observation at an appropriate level of detail.
2. The host may use the established remote keyboard, SD client and Pi reset
   tools within the agreed experiment. EMOS retains mainboard control and the
   P4 forwards admitted input through its existing processed keyboard path.
3. Echo comments displayed on the Agon in chat for continuity. Allow the Author
   to observe and steer the experiment; do not run ahead into unrelated work.
4. Record actual commands, relevant artifact identities, observations, failures
   and conclusions under this task directory. Distinguish host submission,
   mainboard execution evidence and human observation.
5. Keep implementation changes in their owning task. Promote substantial new
   implementation work explicitly instead of silently expanding this bucket.
   Preserve concurrent agents' files and task namespaces.
6. Preserve working input, startup and recovery paths. Consult the operational
   guides before manipulating a live MOS batch, changing firmware or resetting.
   Hardware tests do not replace required emulator review or commit approval.

## Current checklist

1. [x] B01-01: Create the task and introduction with the starting context.
2. [x] B01-02: Select the first CLI experiment interactively with the Author: create
   `/codex` and change into it using keyboard commands.
3. [x] B01-03: Author confirmed the `/codex` result ("good"). See
   [experiment record](BENCH-001/EXPERIMENTS.md).

Add further items only as experiments are agreed. No experiment, completion
claim for REMOTE-002, commit or remote integration is performed by this intake.


## Resident telemetry and driving goal — 2026-09-13

The Author selected resident interrupt-driven service work after blind timed
steering left the road in the first bend within about three seconds. Implement
live Rally telemetry, use it for host-controlled driving, and add a simple sine
wave whose frequency follows car speed. The final physical launch and actual
feedback-controlled driving, with engine audio, is the requested wake-up cue.
All preliminary tests are silent/headless. No extra approval pause before the
requested launch. Existing firmware, SD and Pi reset authorizations apply to
necessary scoped work, with identified rollback. No commit/push is requested;
applicable emulator review/commit gates remain in force.

The TSR role is implemented as a resident EMOS Core service, entered by its
existing UART1/VBlank interrupt vectors. This follows the already accepted
architecture: applications do not replace transport vectors, take UART ownership,
or leave transient application code pointers installed in Core. A standalone
RAM TSR loader and background SD filesystem service are not prerequisites or
claims of this goal. Rally publishes a copied snapshot through the existing
EMOS gateway; transmission continues under interrupts while Rally renders.

## Execution checklist

4. [x] B01-04: Record the blind-driving failure, selected architecture, scope,
   owners and this plan before implementation.
5. [x] B01-05: Specify bounded resident publish/transport contracts and lifecycle;
   add owner-local task records in EMOS and AgonArcade. Preserve starting inputs,
   current journals, accepted binaries and rollback before physical changes.
6. [x] B01-06: Implement resident EMOS telemetry publication and interrupt-driven
   transmission; P4 framing, validation and latest-snapshot HTTP access. Test
   partial writes, CTS stalls, packet boundaries, reset/exit, stale samples and
   coexistence with keyboard/SD. Keep filesystem and blocking work out of ISRs.
7. [x] B01-07: Build an isolated derivative of rally-production with optional
   telemetry and speed-linked sine sound. Publish position, speed, steering,
   lateral state, road geometry/look-ahead, game tick and frame. Preserve normal
   manual physics and turn off the built-in demo driver for host driving.
8. [x] B01-08: Implement and test a host feedback controller using the existing
   keyboard API. Require fresh complete telemetry; release input on stale data,
   epoch loss, errors or physical takeover. Validate meaningful driving through
   bends, rather than merely receiving packets or moving the car.
9. [x] B01-09: Run headless real eZ80 integration and silent physical tests of
   telemetry, controls, SD recovery and driving. Record latency, update rate,
   lane error, road/grass occupancy and completed lap progress. Establish a
   coherent build/flash/SD provenance chain and working rollback.
10. [x] B01-10: Deploy the reviewed-by-machine candidate, launch it on hardware
    and drive using live feedback with audible engine tone as the wake-up cue.
    Keep the run observable, record results, and distinguish machine evidence
    from the Author's subsequent visual/hearing acceptance.

The final native v2 part of B01-09 passes under the explicitly identified
TEST-002 UART1 TX-interrupt model; see the bounded
[headless closeout](BENCH-001/HEADLESS-CLOSEOUT.md). It uses the current
delivered controller/step2 candidate and current physical freshness bound,
preserves historical failures and does not resume driving practice. This is
machine completion; human validation and commit/publication approval remain.

## Owners and research bounds

1. agon-extender: this execution register, wire contract, P4 receiver/HTTP,
   host driver and aggregate physical evidence. Use BENCH-001 file namespaces.
2. agon-emos: resident service, gateway validation, UART/VBlank integration,
   interrupt ownership and build/ABI evidence; owner-local BENCH-001 task.
3. AgonArcade rally19-golem worktree: isolated telemetry/audio build derived
   from the accepted rally-production snapshot; owner-local BENCH-001 task.
   RALLY-20's wider optimization queue and all Golem work remain outside scope.
4. Official read-only references: agon-mos v3.0.2; agon-vdp v2.16.0;
   agon-docs f9806bd3cbff6ed5d1c08bef1d51fed11764b86b. Relevant contracts are
   mos/API.md (gateway, interrupts), mos/Executables.md (application lifecycle),
   vdp/Enhanced-Audio-API.md (sine waveform 3 and frequency control).
5. Existing EMOS sdlink rejects ISR callers. Existing keyboard UART driver
   preserves all registers and owns bounded RX; extend that owner for bounded
   TX instead of invoking filesystem calls or the foreground blocking writer
   from an ISR. Legacy VDU output remains on the onboard VDP.
6. Preserve remote agents' unrelated files/refs. Read-only inspection does not
   authorize pulling/merging their remote changes. No delegation is selected.

## Hardware handover

The Author temporarily prohibited all access to the P4, Agon and Pi until
explicit clearance, because another agent will use the bench. This suspends
all previous physical/read-only connection authorization for this task. Continue
local code, builds and headless tests only. Physical validation and the audible
driving cue wait for clearance; do not poll the boards or Pi while waiting.

The Author subsequently lifted this hold and reported the Agon at the EMOS
prompt after the other agent passed its tests. Necessary scoped access is
restored; inspect identities before deployment and preserve that agent's result.

## Current local evidence and Author steering

The Author requested 200% grip for initial physical driving and preserved
telemetry/controls to compare learning. Driver tuning/practice has a 30-minute
budget; debugging and deployment explicitly do not count. Machine-local run
journals track consumed learning time. Do not replace physical acceptance with
simulated driving. Use the manual race, with built-in autosteer disabled.

The first real eZ80 headless run caught an initial zero-physics-tick snapshot
reporting default corner assistance. rally-bench now sets that flag from the
selected race mode before opening telemetry. The corrected silent 40-second
run at 200% grip passed: 404 observations, all on road, 16,869.4 world units
(2.93 oval laps), maximum lateral error 23.75 units. UART publication was about
10 Hz in this emulator, while game updates were about 21 Hz; this is measured
emulator behaviour, not hardware performance or baud proof.

EMOS full ROM previously occupied 130,919/131,072 bytes. Adding all new services
exceeded flash by 696 bytes after initial compaction. The explicit non-release
port/bench-telemetry.mk substitutes resident telemetry for the old standalone
UARTFLOW diagnostic. The normal source profile keeps UARTFLOW and omits
telemetry; both profiles build and pass existing linked guards. This is a bench
composition tradeoff, not a new general MOS memory limit or a shipped product
feature removal. Telemetry copies once into the UART owner's 88-byte resident
slot, eliminating a redundant staging copy. Further product integration needs
a deliberate flash-budget decision.

The retained native emulator's UART model implements only RX interrupt demand
(agon-ez80-emulator/src/uart.rs, is_rx_interrupt_enabled). The approximately
10 Hz telemetry observed there therefore exercises bounded VBlank transmission
kicks, plus RX-triggered drains, rather than proving TX-empty hardware interrupt
delivery. Do not tune real hardware expectations from that artifact or change
the emulator to conceal it. Physical telemetry is the next evidence boundary.

## Traffic avoidance extension — Author instruction, 2026-09-13

The Author heard the engine and asked to leave the tone unchanged; speakers are
now muted. Future attention requests use a labelled emulator startup beep. Each
physical driving test must start a fresh game and quit it on completion, so a
coasting unattended car cannot be mistaken for active driving. Respect physical
keyboard takeover: never reacquire it merely to force an exit. The 30-minute
practice/tuning budget continues; debugging/deployment remain excluded.

11. [x] B01-11: Extend the coherent snapshot to v2 with six opponents' relative
    positions, lanes and speeds plus physics-tick overlap evidence. Keep normal
    gameplay physics unchanged: existing traffic has no collision response.
    Freeze bounds and the explicit contact proxy before coding; update all
    three owners, wire tests and identified draft firmware.
12. [x] B01-12: Add predictive passing and faster driving through ordinary keys,
    with braking for blocked paths, retained telemetry and overlap/pass counts.
    Validate crowded/blocked/wraparound cases before bounded physical runs.
13. [x] B01-13: Enforce fresh launch/held-Escape exit around each test, verify
    telemetry cessation and SD recovery, then demonstrate traffic avoidance on
    the physical Agon at 200% grip within the remaining practice budget.

A press/release Escape pair can fall entirely between Rally's frame polls.
Hold Escape across several frames, release it, and observe telemetry cessation
before typing CLI commands. An emitted key event is not proof the app exited.

The telemetry/audio and initial external driving implementation passed physical
testing in v1. The Author heard the tone. V2 local tests now pass, including
traffic prediction with delayed controls; physical v2 acceptance and fresh-run
exit evidence remain under B01-09/13. No completion mark authorizes a commit.

The Author separately requested deterministic opponent routes generated by
Python into sparse speed/direction/turn-rate/duration records with per-car
countdowns. This is registered as AgonArcade RALLY-21, deferred explicitly out
of this demonstration. Do not alter the six opponents for the passing tests.

## Overnight continuation and 170% run

The Author extended the driving-practice ceiling to one hour for avoidance and
authorized a full-game Rally continuation, followed by faithful Extender video
throughput/VDP-command port work. AgonArcade RALLY-22 owns that sequenced goal;
this task retains the telemetry/driver implementation and evidence. Do not wake
the Author for ordinary progress. Downloaded reference media must remain ignored.

The first v2 physical run made 20 passes at a top speed of 300, all 452 samples
on road, but counted one overlap. Its forecast underweighted immediate danger
relative to later contacts and capped frame duration below hardware's observed
20–22 ticks. The next controller uses measured intervals up to 32 ticks, weights
imminent risk more heavily and includes full braking. Six actual-Motion cases
then passed, including slow/uneven frames, with zero contacts/grass.

The Author called the prior run a good lap and requested 170% grip. A fresh
60-second physical run at 170% passed: 19 passes, zero contacts, all 447 samples
on road, peak speed 300, 38,515.36 world units. Grip was changed/confirmed using
ordinary held minus input, never a game-state write. Automatic held Escape
ended telemetry after both physical tests. The tone remains unchanged.

The Author's final bedtime direction replaces the loose practice allowance
with four 15-minute blocks at 200%, 180%, 160% and 140% grip. Optimize clean lap
time within each block; retain contacts and grass/kerb evidence to distinguish
pace from recklessness. Preserve prior practice separately. The new one-hour
programme is timed independently, with debugging/deployment excluded. Trials
restart/quit and may be split into shorter runs for inspection/tuning. Capture
interpolated MOS-clock lap crossings with their telemetry-interval uncertainty.
After this programme, resume AgonArcade RALLY-22 in order. No overnight alerts.

The Author requests a stronger centre-line preference for spectators. Returning
to centre must outweigh the old lane-change penalty when paths are otherwise
equally safe. A local jitter test exposed a forecast bug: assuming an input
delay could approve a return before the next car cleared. Evaluate both immediate
and one-frame-delayed application of the actual next command. Preserve that
failure, the explicit centre-cost change and each controller's complete source
beside subsequent physical run telemetry.

The first programme run stopped after112.25 seconds on a transient HTTP timeout.
All12 measured laps were contact/grass-free, best8.446s, with six kerb samples.
Keyboard cancellation had succeeded remotely despite the timed-out response.
After verifying the same session/neutral physical input, the host resolved
cleanup and held Escape; telemetry stopped. Cleanup now uses the ordinary
bounded one-second HTTP timeout after driving stops, while active feedback
retains its stricter deadline. No reset or Author assistance was needed.

Physical freshness amendment during the timed grip programme: the earlier
200 ms cutoff caused nuisance stops on a healthy rendered-update stream with
16–22 raw ticks per frame (133–183 ms) plus HTTP/polling variation. Select
300 ms for the current physical trial's receipt/progress checks, while retaining
the 120 ms active HTTP timeout, epoch/CRC/progress checks, no stale-state control,
and automatic quit. Save the last reply on any rejected observation. This
changes the earlier physical limit explicitly; it does not convert the failed
350 ms native-emulator diagnostic into a pass. Cleanup alone uses the ordinary
one-second request bound after active driving stops.

During the next physical trial, all20 completed laps were contact/grass-free
(best8.00s), but another individual HTTP request exceeded120ms at166.39s.
Automatic release and held-Escape exit succeeded. The active per-request bound
is now200ms, still below the separate300ms observation bound. Recheck sample
age after the keyboard-status request before calculating/sending controls;
uncertain mutations remain unreplayed except exact journal recovery on cleanup.
No controller action may use an observation which expired during that lookup.

The remaining uneven-cadence local overlap was a premature cut-in followed by
braking, allowing the previously passed car to catch up. A local guard keeps
the chosen path on the current side of a nearby opponent until its longitudinal
clearance exceeds140 world units. Predictive contact/edge checks still apply.
This guard passed all six180%-grip actual-Motion cases before adoption; a
shortened prediction horizon merely moved the failure to a different case and
was rejected. Centre cost remains2.0, lane-change cost0.35, corner reserve0.72.
Each subsequent run archives this exact controller, so prior results are not
silently attributed to the modified algorithm.

## Author steering comparison and passing priority

The Author interrupted the180% block to request one steering tick per held-key
frame, then two, saying three is too aggressive. The active run was stopped
with a local interrupt; it released input, held Escape and confirmed telemetry
ceased. Its63.53 seconds remain charged to the180% block, with23 passes and
zero contacts/grass. Preserve the unfinished programme; this is steering of the
active goal, not its cancellation.

Add explicit steer1/steer2 options to the isolated bench binary and report the
actual selected step in existing snapshot byte78. Host prediction must consume
that step, including the changed reachable-angle parity after clipping at±21
with step2. Keep the full steering range and five mirrored car views. Compare
one then two on hardware at the same180% grip, within the remaining practice
allowance. Three is retained only as an explicit old-baseline test option;
the new candidate defaults to two. Accepted production files remain preserved.

The Author clarified that centre preference yields to a safe pass on either
side. Rank collision/road risk first, forward progress second, then centre/lane
change cost. Do not trade an available pass for staying behind a slower car at
centre. Keep the cut-in clearance guard; return to centre after passing safely.

### Final bounded practice and recovery,2026-09-13

B01-13 is machine-complete; see BENCH-001/PRACTICE.md and DELIVERY.md.
At this historical checkpoint B01-09 retained its native-v2 limitation:
physical practice passed, but the native diagnostic failed grass acceptance.
The later HEADLESS-CLOSEOUT.md records a separate, explicit UART-model
correction and passing integration; the original diagnostic remains a failure.
ROM/SD/startup preservation and final service exit passed without reset/flash.
No further driving learning under the exhausted hour. Human review and commit
approval remain pending; no experiment is authorized for remote publication.
