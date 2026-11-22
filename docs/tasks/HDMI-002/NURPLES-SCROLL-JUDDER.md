# HDMI02-SIZE01e — Stock-compatible P4 presentation timing, with Nurples as the scrolling reproducer

**Current work.** Smith approved the [two-row interrupt test](#two-row-interrupt-test-for-review) on November 22. After the offline checks, Smith explicitly selected installation, readback and display of the reference card. Keep the Olimex reservation and hold that card for Smith. The wake-only build proposal is withdrawn.

**Current review concerns stock-compatible presentation and performance.** Smith selected exact pixel doubling for 320×240. The [native row scanout plan](NATIVE-ROW-SCANOUT-PLAN.md) records the decision, the redundant work to eliminate and the refill tests under load. Smith approved that design for the P4 candidate. The [offline verification](NATIVE-ROW-SCANOUT-RESULTS.md) and [matched load-test packet](NATIVE-ROW-LOAD-PACKET.md) await his review before reservation. Nurples supplies the mode-20 scroll reproduction. The [comparative source review](STOCK-SCROLL-TIMING-REVIEW.md) and its spare-buffer control remain available for diagnosis. The earlier blackout comparison is deferred.

**Application scope.** Smith confirms that Nurples should keep a single logical framebuffer. The compatibility question belongs to EVDP and applies to every application using its display paths. Nurples supplies the mode-20 reproduction. Each stock mode retains its own logical buffering and swap behavior. The mode-20 observation establishes no result for other modes. Smith has asked how directly the P4 can preserve stock's timing between native row preparation, physical scanout and queued drawing. The proposed spare-HDMI-buffer comparison isolates one possible cause. Smith selected DMA-paced native rows for the candidate.

**Closer stock timing on the P4.** A P4 scanout driver could use a hardware DMA block event to refill a retired output slot directly from the next native rows. EVDP would apply the mode's row decoration and output conversion, hand the completed slot to DMA, and release queued drawing when the final visible source rows have been prepared. Stock performs this work during scanout. The P4's existing experimental rolling driver already recycles slots, but its refill copies an already-rendered RGB888 background and can composite staged sprites. A native producer would need bounded access to drawing state and enough time to finish each refill under load. At the candidate's 684×384 timing, 32 active carrier rows pass in about 1.03 ms. The earlier driver's 1,600 µs guard covers a particular slot-reuse schedule. The recorded failure came from that driver on a different build. [Strip refill](../../../vdp/video/extender/display/rolling/strip_runtime.inc) · [Slot geometry](../../../vdp/video/extender/display/rolling/strip_config.h) · [Recorded transition](../EMOS-001/QUALIFICATION-RESULT-R01.md)

## Stock timing review commissioned November 21

Smith reports the mainboard VDP does not show the scrolling problem. Review stock VDP and its graphics-library timing against the P4 candidate first. Verify the relationship of the installed mainboard companion to the official stock reference. Trace scroll execution, vertical blank, work budgets, framebuffer access and physical scanout, and identify intentional substitutions or lost guarantees with exact code evidence. Report ranked findings and uncertainties. This tranche covers source review and written results only. The transient HDMI blackout and the earlier physical plan are deferred.

**Completed November 21.** Stock and the installed mainboard companion prepare VGA rows in pairs at hardware-defined positions in the raster. The P4 wakes its drawing worker at DMA frame completion, then separately converts a whole image, locking one native row at a time and writing the scanned HDMI buffer in mode 20. Stock also disables the optional drawing timeout. Nurples polls the mainboard VBlank-derived MOS clock in both routes. P4 HDMI has its own clock. The two P4 builds share these mechanisms. The mainboard comparison comes from Smith, and the observed P4 game interval has no row or DMA trace. [Detailed findings, evidence and proposed controls](STOCK-SCROLL-TIMING-REVIEW.md)

## What was observed

Smith described vertical judder that appeared to span multiple scanlines. Different parts of the playfield seemed to move unevenly. He saw no alternating blank and drawn scanlines. He raised scanout errors as a possibility. The trial provided a visual observation only. There is no game-time frame trace, video recording or matched release playthrough in this record. The earlier static pattern verdict and scanout samples belong to a separate run. [Bench observations](SIZE01-BENCH.md)

During regular play the whole picture went black once and returned after about one second. Smith saw no obvious framebuffer corruption after recovery and suspects the monitor briefly lost HDMI sync. The recovered picture describes the framebuffer’s visible contents after the event. Framebuffer contents and HDMI signal continuity during the event are unknown.

The Olimex ran Nurples from `/mystuff/nurples`, using the four-file physical runtime bundle from Nurples dev commit `7acfbfa3f27c0100afbedc9d40d75a98a4d1e846`. The executable SHA-256 was `b596aec8592dfc295bd379d6812cfeca96e725b59bd6676c77afaf96460c8ff9`. The P4 ran `hdmi-coverage-r01-b2026-11-21-16-58-59Z`. Its build uses full-frame DMA. Capture the game's actual mode, buffering and HDMI carrier during reproduction. [P4 build and release identities](SIZE01-RESULT.json)

## Offline trace at the tested revisions

**Mode 20 exposes two opportunities for different parts of one image to show different game updates.** The P4 samples a changing logical image one row at a time. It also writes the expanded rows into the HDMI buffer that DMA is scanning. Both released and candidate firmware do this. Neither mechanism requires a missing scanline or a loss of HDMI sync. An actual cause in the reported game interval remains unmeasured.

| Stage | What the checked source does |
|---|---|
| eZ80 game | Nurples selects or reuses stock mode 20 and checks 512×384 and 64 colours. This is the single-buffered mode. In ordinary live terrain travel it sets the 256×336 playfield at origin (128,48), sends `VDU 23,7,2,2,1` to scroll that viewport down one pixel, clips to the exposed top line and plots the tile strip. Tile plots are separate commands. The game loop waits for a change in the MOS time sysvar, with a bounded timeout. This does not fence the P4’s composition or guarantee one game update reaches each HDMI refresh. The existing P key freezes gameplay updates while the display continues running. [Mode validation](../../../../nurples/src/asm/playfield_display.inc) · [Viewport](../../../../nurples/src/asm/screen.inc) · [Terrain update](../../../../nurples/src/asm/tiles.inc) · [VDU and pacing](../../../../nurples/src/asm/vdu.inc) · [Game loop](../../../../nurples/src/asm/nurples.asm) |
| EMOS and P4 drawing | Nurples sends the scroll through MOS. EMOS in ExCom routes ordinary VDU commands over UART to the P4. Its VDU parser selects the graphics viewport, and Canvas emits a vertical scroll primitive. The 64-colour controller’s downward scroll works bottom-up, exchanges the side regions to preserve the pixels outside the playfield when swapping row pointers, then fills the exposed row. The drawing worker drains primitives with native exclusion per operation. Scroll, tile plots and sprite updates are not one atomic frame. [Parser](../../../vdp/video/vdu_sys.h) · [Viewport translation](../../../vdp/video/context/graphics.h) · [VGA64 scroll](../../../vdp/vendor/vdp-gl/src/dispdrivers/vga64controller.cpp) · [Row algorithm](../../../vdp/vendor/vdp-gl/src/displaycontroller.h) · [Drawing and row locks](../../../vdp/video/extender/display/stock_runtime_controller.hpp) |
| P4 composition | DMA frame completion wakes the drawing worker, which in turn wakes the output worker after its drain. Output notifications can coalesce. The output worker reads and decorates native rows from top to bottom, releases the native guard between rows, and expands them to RGB888. A later scroll can therefore fall between reads of the top and bottom of the same terrain feature. Each sampled row can be valid while the picture contains two terrain positions. [Scheduling](../../../vdp/video/extender/display/stock_p4_service.cpp) · [Row publication](../../../vdp/video/extender/display/hdmi_output.cpp) |
| P4 scanout | In `HdmiOutput::publish`, independent HDMI front/back publication requires a scaled or logically double-buffered surface **and** two panel buffers. Mode 20 is unscaled and logically single-buffered, even when the panel has two buffers. Both builds use `ownership_.writable(false)`, which selects the current front. The output worker writes it while the peripheral can scan it. The IDF panel-owned-buffer submission writes back the affected cache rows and selects the buffer. Its full-transfer callback normally rearms the selected descriptor for another frame. Thus even a coherent source image could change partway through physical scanout. The generation-drop and pending-back-buffer checks do not protect this single-buffered path. [Ownership](../../../vdp/video/extender/display/hdmi_buffer_ownership.hpp) · [Publisher and DMA callback](../../../vdp/video/extender/display/hdmi_output.cpp) |
| HDMI signal | The release keeps 1280×720. The candidate selects 684×384 for mode 20 and 848×480 for mode 0. Mode 20 uses native-size pixels on both. The 320×240 PPA scaler and experimental rolling path are inactive. The candidate’s DMA stop and panel restart serve a carrier change. An ordinary viewport scroll does not request a timing change. Full-frame DMA feeds the P4 DSI output, the LT8912B bridge drives HDMI, and the monitor acquires the signal. The SDK can report a DSI fetch underrun. A P4 frame-complete callback, an HTTP mode report or a high hot-plug-detect bit alone cannot establish monitor input lock. Neither image enables the optional link observer. [Mode selection](../../../vdp/video/agon_screen.h) · [Timing policy](../../../vdp/video/extender/display/hdmi_timing.hpp) · [Bridge driver](../../../vdp/components/esp_lcd_lt8912b/esp_lcd_lt8912b.c) |

The release source is `be1d9432` and the candidate source is `21349e0a`. The retained source inventories show the native scroll and row-preparation code is shared. The mode-20 publication loop is unchanged between those revisions. A candidate-only symptom would warrant checking the carrier, buffer dimensions and monitor behavior before attributing it to a new scroll primitive. [Build comparison](SIZE01-RESULT.json) · [VDU scroll contract](../../../../../agon-docs/docs/vdp/VDU-Commands.md)

Two independent observations inform the controls. In one retained **static mode-20 preview** window the candidate reported 32.174 submissions/s, 29.445 ms mean conversion and 60.051 DMA frames/s. This establishes that the refresh counter can advance substantially faster than new images are prepared. Those values are not gameplay measurements. On earlier hardware-game and firmware combinations Smith saw a thinner tear disappear on pause, and an older held mode-20 chart blinked without new game drawing commands. These motivate the pause and receiver controls. Neither historical event identifies the cause of this report. [Preview capture identity](SIZE01-BENCH.md) · [Prior pause comparison](MEMORY-RESULTS.md) · [Prior dropout controls](../RESEARCH-007/HDMI-DROPOUT-R01.md)

## Earlier matched release/candidate test, deferred

1. **Setup and signal witness.** Use the pinned Nurples binary (`b596aec8…`) and the same three assets on both arms. Keep EMOS, mainboard VDP, ExCom route, save/start state, input, cable, monitor input, aspect settings and observation equipment identical. Preflight the chosen HDMI receiver/analyzer on **both** carriers. It must report input timing/lock independently of pixel brightness and preserve timestamps across a signal gap. Prefer the monitor’s own lock indication for a claim about that monitor. If inserting an analyzer changes the connection, use the same topology in both arms and identify precisely which receiver reported lock. A device that renegotiates or regenerates HDMI changes what the monitor sees. With only video or a camera, still score the judder and mark sync loss inconclusive wherever lock is unobserved.
2. **Two arms, one workload.** A uses released v0.3.0. B uses the already-built, previously verified candidate. Confirm the working prompt and P4 build identity, launch the same game from the same directory, and record mode, buffering and carrier at entry and during play. Use the normal mode-0-to-20 entry and exit as timestamp markers outside the gameplay score. They are not spontaneous outages. Smith selects the same opening level and steering sequence. Proposed exposure per arm is three matched 60-second intervals of ordinary terrain scrolling and three 20-second P-key holds on a visible landmark, resuming the same scene after each hold. Log actual seconds, deaths, level transitions and restarts separately. Match exposure if a scene ends early. A rare outage can remain unresolved after both arms.
3. **Evidence on a common clock.** The operator aligns receiver lock/timing events, timestamped native-input HDMI frames when available, passive P4 serial and read-only display status. Record clock alignment and uncertainty against the visible entry/pause/resume transitions. Preserve at least two seconds either side of an event. Keep the monitor bezel or signal banner in the optical recording. Record repeated or missing capture frames. Use row positions in logical playfield coordinates so the different carriers and monitor scaling do not move the measurement points. Sample identifiable terrain at the top, middle and bottom and a static HUD reference. Compare successive images at the same scroll step, avoiding independently moving actors and the newly drawn tile strip. Camera rolling shutter alone can mimic a horizontal tear. Prefer complete digital input frames, with the monitor view for corroboration.
4. **Score each symptom independently.** Use the table below. Record judder occurrences per scrolling minute, blackout count per observed minute, duration, lock transitions and whether either symptom occurred on pause. Log the observed timing of a P4 underrun, restart, mode change or stopped submission window alongside the event. Ten-second P4 averages and polling cannot certify continuity through a one-second event. Follow the commissioned stop rule for unexpected faults; preserve the first failure. After the authorized arms, the operator performs the verified app-only restore and checks the bench in.

| Observation at event time | What it supports |
|---|---|
| Receiver stays locked. In one captured HDMI frame terrain advances by different amounts at different heights; the HUD stays put. | Row-dependent presentation judder in the delivered picture. Disappearance on pause ties it to updates. Source-row mixing and front-buffer scanout overlap still need separation. |
| Receiver stays locked. Complete frames repeat or advance unevenly, with the same displacement throughout the terrain. | Uneven whole-frame cadence. Record separately from a row-dependent tear. |
| Receiver reports loss and reacquisition at the blackout, with no commanded mode switch. | Timing/signal interruption at that receiver. The event alone cannot localize the fault to P4, bridge, cable or monitor. Record any simultaneous judder separately. |
| Receiver stays locked and delivers valid black active pixels throughout the outage. | Black video was delivered while timing remained valid at that point. If input frames retain the intact game while only the monitor darkens, investigate downstream of the capture point. |
| Only a black camera image, a capture application’s replacement black frames, missing lock telemetry, or no recurrence. | Cause unresolved. Record what was visible, which receiver was observed and the exposure time. |

**Decision after A/B.** If locked-signal row judder is reproduced, propose a separate single-variable comparison on the candidate carrier: first publish each completed conversion to an independent back buffer and allow reuse of the old front only after DMA acknowledges the handoff, keeping the source row reader unchanged. If mixed terrain persists, propose comparing that version with one that also takes a coherent source snapshot. Compare conversion time and delivered-frame cadence for each, because a slower control can mask the symptom. If the receiver loses lock, prioritize time-aligned evidence across P4 DMA, DSI/bridge output and receiver lock; a framebuffer change alone cannot resolve that question. These are follow-up decisions for Smith. No test, build, instrumentation or reservation is part of this offline result.

## Olimex stock mainboard baseline preload — November 21

Smith approved the matched packet and requested its Legacy arm first. The
operator obtained exclusive custody and confirmed the production handback
identities. EMOS reported Legacy on VDU route 0. A mainboard mode query
returned 0. All 61 files (2,822,927 bytes), including the 54 ordinary-mode
patterns, completed staging over PARLIO. MOS loaded the 10,574-byte
`rowload.bin` at `&040000` and returned to `/test/native-rows-legacy *`.
The keyboard was ready and the SD listener idle. This stage made zero firmware
writes. Smith owns invocation with `RUN &040000`. The operator retains the
slot for his run. The stage and preload receipts are in the local
`agents/hdmi002/native-rows/packet/evidence/legacy/` directory.

### Stock baseline collection after launch

Smith launched rowload and assigned the remaining menu and timing work to the
Pi operator. The stock mainboard run supplies numerical reference data. Smith
will judge scrolling visually in Nurples. The operator keeps the staged
appliance and any existing CSV rows, and uses the standard bench keyboard.
The first automated window is mode 20, resident drawing, for 60 seconds.
Before continuing the matrix, verify its new SD row, elapsed time, observer
record and return to MOS. Keep this run separate from P4 refill measurements.

**Stock pilot disposition, November 21.** Exclude the mode-20 R row from the
matched performance comparison. The Pi observer covered 60.011 seconds with
122 successful service reads. The eZ80 reported 34,795 loops, 7,272 MOS ticks,
zero SD payload bytes and success. The Pi recovered the new 32-byte CSV over
PARLIO and witnessed the mode-0 MOS prompt after collection. The worker and
supervisor exited cleanly. The operator retains the reservation.

Review of the printer mirror showed repeating palette operand bytes during
the supposedly graphics-only draw loop. The fixture sends Copper commands
without enabling the Copper API. Stock VDP can return at the feature check
before reading the operands, so the ordinary VDU parser processes them. The
fixture's success flag checks mode and I/O, and misses this workload error.
Treat the row as automation evidence only. The other 59 windows were held
before launch. Retain the original fixture, CSV, raw transcript and job in
the pilot evidence. Proposed correction for review: enable Copper for the
fixture, preserve and restore its prior state, and check command consumption
before timing drawing on either route. Keep Nurples as Smith's visual test.

### Corrected stock collection

Smith authorized the rowload repair, another pilot and automatic continuation
on success. The eZ80 now reads the Copper variable through buffered command
48 and an ordered general-poll reply. Two missing-value defaults distinguish
absence from a present word, including zero. Each drawing window enables
Copper only if absent and reads the full setting back after teardown.
The preflight exercises absent, present-zero and present-0x6A35 entry
settings, issues palette commands with printable RGB operands, and restores
the observed original setting. The Pi rejects unexpected bytes between
the preflight and drawing banners or a mismatched entry/exit word.

The corrected binary is 11,816 bytes, SHA-256
`69b2aec1f5d127482be14da83b70676decf26d9b79a61b19e5f0c20e98eaed91`.
The Pi stages it beside the first binary and preserves the excluded CSV row.
The mode-20 draw pilot counts as the first of sixty windows only on passing
preflight, clean serial capture, valid SD row, service observation and MOS
handback. Each later window also gates the next. The earlier bad trace and
synthetic operand leaks and restoration mismatches were rejected offline.
The local binding, build and bench receipts are under
`agents/hdmi002/native-rows/copper-r02/`. Nurples remains Smith's visual check.

Smith shortened stock collection to one final 60-second mode-8 drawing
sample. The corrected mode-20 drawing pilot had passed with 44,410 loops,
7,268 MOS ticks, 60.011 seconds of Pi service observation and 122 status
reads. The printer transcript passed the operand check and the Copper
variable returned to its original absent state. The subsequent mode-20
clear window was already underway. At exit it printed “Row test failed.”
and MOS printed “Error accessing SD card” and the test directory prompt.
The CSV for this window was not collected; the generic fixture exit status
does not distinguish a media failure from another failed fixture check.
The batch stopped there, before mode 8. The operator retained the reservation
and the first-failure evidence. The final authorized measurement is pending
the commissioned bench failure handoff.

Smith confirmed that MOS uses “Error accessing SD card” for unclassified
errors and that a directory listing read the mainboard card successfully.
He authorized prompt verification, preservation of the current CSV, and
only the final mode-8 drawing sample. The Pi witnessed the test directory
prompt on Legacy route 0 and downloaded the 96-byte, three-row CSV over
PARLIO before launching mode 8. The clear case had written 54,953 loops
with its success field zero. In that case the only path that writes a zero
in the CSV is the final active-mode check. The result does not distinguish
a missing mode reply from a reply reporting another mode. Exclude that row.

**Stock collection complete.** The one final mode-8 drawing sample passed.
The CSV preserved all three prior rows and appended exactly one passing row.
The mainboard consumed the palette operands in both corrected drawing
samples and restored the observed Copper setting (absent). Each service
observer recorded 122 successful status reads over 60.011 seconds.

| Stock drawing case | Logical pixels | Pi interval from entry banner to Escape dispatch (s) | eZ80 loops | Approx. loops/s |
|---|---:|---:|---:|---:|
| Mode 20 | 512 × 384 | 60.380 | 44,410 | 735.5 |
| Mode 8 | 320 × 240 | 60.379 | 46,285 | 766.6 |

Mode 8 submitted 4.2% more loops/s than mode 20 in these single samples.
These are workload iterations, with each rate calculated using the Pi interval.
The sample does not measure displayed frames or P4 refills. The Pi witnessed
the mode-0 MOS prompt after collection, the SD listener was idle, and the
worker group exited cleanly. Stock collection stopped with Olimex custody
retained. Smith owns the Nurples visual check. Last window receipts and
the cumulative CSV are under the local evidence directory `final-stock-m8/`.

### Matched P4 drawing runs

Smith commissioned one 60-second resident drawing window each in modes 20
and 8 on the full-frame build, then on the native-row candidate. Use the
same corrected 11,816-byte eZ80 fixture as the stock runs. The operator
verifies every P4 application write by independent readback across the
1,794,048-byte extent. ExCom exposes sampled display text and status.
The final handoff is the candidate running, with the four-file pinned
Nurples dev runtime staged and the program loaded for Smith to start.
The machine-local jobs and receipts are under
`agents/hdmi002/native-rows/copper-r02/matched-p4/`.

The full-frame install passed the independent byte comparison at offset
0x20000. The SHA-256 of the complete 1,794,048-byte readback was
`e79ebbb8927245d2173a8a4306a09e97a1f181c4c80bed2db6a865aee81b73a1`.
The post-flash MOS CLI and keyboard were verified. Each P4 window uses a
Legacy CLI load receipt followed by EMOS ExCom routing, a fresh on-screen
marker and route status, the rowload drawing menu, a settled 60-second
HDMI/status observation, and the eZ80's SD result. The Pi samples menu
text outside the timing interval. The full-frame arm restores the production
app and verifies it before the candidate stage. The candidate remains loaded
at the Nurples handoff.

**P4 bench outcome.** Both full-frame draw windows passed. Mode 20 recorded
49,190 loops in 7,316 MOS ticks and mode 8 recorded 61,086 in 7,316 ticks.
Each Pi observer acquired 122 status reads over 60.01 seconds with the
expected logical and HDMI dimensions. The full-frame arm's production restore
passed independent readback and CLI handback. The candidate's independent
1,794,048-byte readback matched SHA-256
`a67918f8a586768f6f13e418b74aff1b7062d2ba14df99e4301a89d67113a1fa`.

Before the candidate entered either draw workload, its active and saved
scanout registers both reported a sequence fault (code 1), epoch 1, frame 2,
block 0, at 848 × 480. One rejection, zero invalid descriptors, zero reported
underruns, and a maximum observed refill of 1,048 µs were recorded. Root cause
and physical DMA timing remain unresolved. The operator stopped before RUN.
The five staged files include the four-file Nurples runtime. Nurples was not
loaded or started. The candidate remains installed, the Olimex lease is held,
and all bench worker processes joined. The failure alert completed. Preserve
`native/draw/m20-entry-fault.json` under the local matched-P4 evidence root.

After the batch stopped, Smith observed that the entire P4 display was solid
blue with no text. He recognized the appearance from earlier incidents. The
candidate had already reported a scanout sequence fault at frame 2, block 0,
before the drawing workload or Nurples ran. The first blue frame and HDMI
receiver lock were not captured, so the observation establishes the visible
end state only. Keep it distinct from the earlier brief black screen during
Nurples gameplay.

### Failure preservation, release restore and frame-wrap review

The operator preserved 44 files and verified each archive member against the
SHA-256 manifest. The private archive SHA-256 is
`daabef48f774f3eed550251e1af4aea942d13425eaaa5a99812fc24e59cdd6e1`.
The operator restored the released v0.3.0 P4 application at 0x20000. The
independent readback matched all 1,794,048 bytes of the programmed extent,
SHA-256 `071ac03fe4b6159df8e1b15f825d523e92fe55653e681571bb44496c2d0368c1`.
The application itself is 1,768,624 bytes, SHA-256
`539dc7176f079bc6c298c48352b7e94c54db654fb6fdbb9c42897370fb19834b`.
Handback verified the working Legacy CLI, neutral keyboard, inactive listener,
idle transfer service and free serial ports. The scheduling channel accepted
the bench check-in. Local receipts are in the matched-P4 evidence root under
`native-release/`, `native/restore-p4/` and `native/handback/`.

**Why the P4 stopped.** The installed candidate application hash matches the
retained build at source revision `2f99ab28dff2b18fea48337a46e382997e7ab5d1`.
The compiled DPI driver's include path and source archive identify the same
`native_runtime.inc` and `native_ring.h` reviewed here. At 848×480 each
frame has fifteen 32-row DMA blocks. Block and frame numbers start at zero.

| Event in frame 1 | P4 DMA interrupt and refill worker |
|---|---|
| Block 12 retires | Slot 0 becomes writable for frame 2, block 0. The interrupt invalidates the old descriptor and queues the new tag. The worker checks for a drawing wake. |
| Block 13 retires | Only now does the worker's unconditional next-frame sampling gate open. That wait consumes one nominal 1,030.4 µs active-block interval, even in startup with no previous reader. |
| Block 14 retires and the list ends | All 30 blocks across frames 0 and 1 have retired. Three slots were primed and 27 later publications completed in FIFO order, ending at frame 1, block 14. Frame 2, block 0 is still unpublished. The frame callback rejects the next list and disables DMA. |

The exact-tag check worked. The interrupt handler built into this candidate
dispatches the block callback before the full-transfer callback when both bits
are pending and yields only afterward. The core-1 refill worker therefore
cannot rely on running between those callbacks. The reported 1,048 µs was the
previous frame's successful top-block publication (1,042 µs before work,
3 µs render, 3 µs finish). The frame callback supplies literal zeros to the
fault timer. The receipt identifies which publication missed rearm, but has no
timestamps for that job's dequeue, gate release, reader mutex or first render.
It establishes neither the exact source of the final delay nor receiver sync.

**Why the startup wait was unnecessary.** HDMI startup waits for the first
successful frame rearm before allowing the stock row service to bind.
Frame 1's top slot had to be ready before that first rearm, so it could not
have enabled a reader. Only a block-0 job can enable reading, and binding
initializes reading to false. No preceding reader could have issued a drawing
wake on entry to the frame 2 top job. Its wait offered drawing no protected
time. A reader *could* have bound in time to render frame 2. The zero sampled
profile count does not establish that frame 2 was blank.

**Smallest proposed change, awaiting review.** In the P4 worker's
`native_do_job`, skip the penultimate-retirement wait for block 0 when the
worker issued no drawing wake for that handoff. The worker can then begin
at block 12 retirement. Use the decision already made under the reader mutex.
Keep binding and first-frame adoption at block 0 under that mutex. When the
worker releases drawing, retain the existing sampling gate. Every path still
requires slot ownership, cache visibility, the 1,600 µs guard, exact-tag
publication and a ready descriptor at rearm. This change needs no new buffer,
copy, interrupt or allocation.

**Offline check and limit.** A two-frame FIFO schedule allowed the worker to
take the top job at third-last retirement and withheld worker service from
penultimate retirement through EOF. On the 15-block carrier the existing rule
reproduced 30 retirements, 27 publications, peak queue depth 2 and rejected
rearm. Exempting the no-wake handoff gave 28 publications and a ready top
descriptor. The 12-block carrier gave 21 and 22 publications respectively
after 24 retirements. These are scheduling-model results. The existing C host
test drains the worker before invoking the frame callback and misses this
interleaving. For an approved fix, exercise the actual callbacks on both
carriers with deferred worker service, bind during startup, a real drawing
wake, and a deliberately withheld publication. Check that an unpublished
descriptor still stops DMA. A bounded first-fault record of dequeue, gate,
render start and rearm would distinguish later worker dispatch from an
in-flight render if the failure recurs. Candidate drawing, physical refill
lead and Nurples remain unmeasured.

**Approved implementation freeze.** Smith authorized this P4-only correction
and an offline candidate build. Change only the top-block wait when the
worker issued no drawing wake. Exercise the production callbacks for both
12- and 15-block carriers, including first binding, a real drawing window,
deferred worker service at frame end and a withheld top block. Verify the
regression against the failed source, run the existing pixel and service
checks, build with the failed candidate's flags, and retain the experimental
application and its hash for review. Bench time requires a separate request.

### Startup handoff correction and offline results

The plan and the preserved failure were pushed in `8f682831` before implementation.
The candidate source commit is `bae12499bda62b6d3b2c822ba0da1f5c11581515`
on `codex/hdmi02-size01`. In `native_do_job` the P4 worker now skips the
sampling wait for block 0 when it issued no drawing wake. The one runtime
condition uses the worker's existing wake timestamp and introduces no allocation
or pixel copy.

The regression binds the reader after the first successful frame rearm. It
then delivers the last two block interrupts and the end-of-list interrupt
without further worker service. The old driver failed the new successful-rearm
assertion. With the correction, the compiled production callbacks gave the
following results in the host hardware model.

| Frame 2, block 0 | 848×480, 15 blocks/frame | 684×384, 12 blocks/frame |
|---|---|---|
| Worker services the available slot | 30 retirements, 28 publications, rearmed | 24 retirements, 22 publications, rearmed |
| Worker withholds the slot | 30 retirements, 27 publications, DMA stopped | 24 retirements, 21 publications, DMA stopped |

Both withheld cases reported one sequence rejection at 2:0, an invalid top
descriptor and a cleared channel enable bit. The genuine drawing-wake cases
retained their modeled one-block drawing window through five wraps per carrier.
The pixel oracle passed two-frame comparisons in 15 configurations, including
exact 2×2 replication across the strip seam. HDMI service, carrier lifecycle
and frame scheduling checks also passed.

The clean experimental build `hdmi-native-row-r02-b2026-11-22-00-18-45Z`
passed target validation. The independent comparison against the failed r01
build found one changed firmware source input in 5,574, matched all 108
checked DPI compiler options, and confirmed the no-wake branch in the linked
RISC-V worker. All 85 manifest artifact hashes verified. The 1,769,824-byte
P4 application has SHA-256
`ac6f0f47c558a4224a3354fe2a383df6c2a3f97f3f115c09daf1cce5ad485da1`.
The local build, comparison receipt and red/green logs are retained under
`agents/hdmi002/native-rows/startup-r02/`. This offline result leaves
target startup, physical refill timing under load and Nurples visual
acceptance open. The Olimex bench remains released with v0.3.0 installed.

### Corrected candidate on Olimex and proposed first-fault trace

The corrected candidate reproduced the startup failure at epoch 1, frame 2,
block 0, on the 848×480 carrier. The P4 worker had taken the request from
the queue. The missing observation is how far that request progressed before
the DMA interrupt rejected frame rearm. Smith is using the bench interactively
after the stopped batch. This review used only retained files.

**Evidence.** The operator archived the complete r02 bench evidence directory
outside the run directory and rehashed all 136 members against the originals.
The archive SHA-256 is
`8b32a5b11ef60342556dcf37059b83e84c4913113ecf9c0b4a8fd444d53b513c`.
The local archive and member manifest are under
`agents/hdmi002/native-rows/startup-r02/failure-preservation/`.
All 1,794,048 saved readback bytes matched the candidate application and
its prescribed padding. The boot log identifies the same r02 build.
Both active and saved scanout reports agree on the following counters.

| At first fault | r01 | r02 |
|---|---:|---:|
| Successful frame rearms / blocks retired / publications after priming | 1 / 30 / 27 | 1 / 30 / 27 |
| Queue high-water / rejections / invalid-descriptor IRQs / reported underruns | 2 / 1 / 0 / 0 | 2 / 1 / 0 / 0 |
| Slowest completed refill | 1,048 µs, frame 1 block 0 | 60 µs, frame 0 block 3 |

Each retirement enqueues one request. The interrupt reads queue occupancy
after every successful send. With 30 sends and at most two entries left, the
single FIFO worker had removed at least 28 requests by the end of frame 1.
The first three descriptors were primed, so request 28 is frame 2, block 0.
The final 27 publications cover only through frame 1, block 14. The worker
could have been interrupted immediately after removing request 28. The two
maxima refer to different completed jobs and cannot establish a speedup or
measure the missing publication. The EOF rejection supplies literal zeroes
for the failed-job timing. Frame 2 is outside the every-sixteenth-frame row
profile. The row profile cannot tell whether its renderer started.

The runner observed the fault after loading rowload and before issuing RUN.
Neither drawing window began and the runner did not preload Nurples. The
supervisor joined its child with exit 1. The spoken-alert helper returned
success. The last commissioned state was r02 installed and the slot held.

**Proposed diagnostic, for review.** Use one compile-time diagnostic on the r02
P4 source, armed once per boot for epoch 1 and tag (2,0). Allocate one fixed
internal-RAM record. The ISR and worker use the same microsecond clock. Record
elapsed time from the target retirement, with an explicit unseen value.
Each milestone occupies one aligned, lock-free 32-bit word. Use a separate
packed phase/source-row word for progress inside the renderer. No serial I/O,
heap allocation, pixel copy, per-row timestamps or general scheduling log.

| Owner and point | Capture for this handoff only |
|---|---|
| DMA block interrupt | Save the entry times for frame 1 blocks 12, 13 and 14, and mark success of the (2,0) queue send. Reuse the existing retirement timestamp. This measures the worker's actual software service window. |
| Refill worker | Mark return from the queue receive, before/after the first reader-mutex take, drawing callback entry/return if invoked, the gate outcome (wait, open or no-wake bypass), and before/after the second reader-mutex take. Record ownership and reader-bound decisions where the driver already makes them. |
| Refill worker and stock row reader | Mark render entry/return, or the no-reader clear/already-black path. If the callback runs, distinguish inactive black output from active rows. For just this block, overwrite the progress word with source row and operation at the native row lock, after acquisition during stock row preparation, and during RGB expansion. Instrument the ordinary frame-2 path, including the first cropped row where applicable. |
| Refill worker | Mark before/after cache clean or its skip, and entry to the publication critical section. Record completion only after the existing fence, descriptor VALID write and budget check succeed. Cache work and publication retain their original ordering. |
| DMA frame interrupt | Immediately before the existing rearm check, capture time, retired count, queue occupancy, slot 0 generation and ready bit. Save the check outcome and the fault site. Seal the record at this decision, or at an earlier first fault. A successful wrap also produces a receipt. |

Keep the ISR and worker fields single-writer. Publish each marker atomically,
with compiler ordering at the measured boundary. Snapshot into retained
diagnostic storage under the existing first-fault/rearm critical section on
core 1, before later worker progress or panel teardown can change it. Expose
the sealed record in the existing scanout diagnostic response. Read it after
the event. The observer need not poll during startup.

**How to use the result.** Subtract adjacent milestone times to find where
the available interval went. At EOF an entered operation with no return
brackets the unfinished work. The renderer cursor distinguishes row-lock
acquisition, stock composition and expansion. A completed cache clean with
no publication directs attention to the final critical section. A published
top descriptor with rejected rearm directs attention to ring state and the
rearm predicate. A preemption between two markers leaves that interval open.
A phase names the interrupted software path; it does not identify another
task holding a mutex or establish physical HDMI timing.

Before a diagnostic build goes to hardware, exercise this receipt with the
existing host callback model: successful frame-2 wrap, intentionally withheld
worker, and EOF during a reader wait, render or cache operation. Verify the
record survives worker resumption and a later panel epoch. Check the linked
target for lock-free marker stores and bound their cost, including the row
cursor. If the diagnostic passes startup, retain the successful trace and
report the failure as unreproduced on that build. Implementation and hardware
execution await Smith's review.

**Approval and operator observation.** Smith approved the one-shot trace for
implementation, offline verification and an identified experimental build.
Freeze and push this plan before editing source. Prove that EOF seals the
record and that a later mode change preserves it. Smith saw the solid blue
Extender display return after several P4-PC resets. Remote keyboard commands
still worked. He could not run an Extender Nurples session and confirmed
Nurples works on the mainboard. He left the bench at a responsive Legacy MOS
prompt in the Nurples directory. These observations do not establish the fault
registers for each reset. This step is offline.

### One-shot P4 startup diagnostic

The plan freeze reached the remote at `704db2bc` before the firmware change.
Source `b9b430c57e2bfc0a4d7e0a7403aaa8e65c6dbf6d` on
`codex/hdmi02-size01` adds the opt-in `--native-startup-trace` build flag
to the r02 native row selection. The flag instruments the core-1 DMA driver
and stock row renderer. The existing HTTP scanout handler accepts
`/display/scanout?startup_trace=1` in this build.

The response is `{"available":false}` until the target rearm decision or
an earlier first fault. Once available, `elapsed_us` names the observed
milestones, measured from the third-last retirement in frame 1. An omitted
milestone was unseen. `site`, `retired`, `queue_depth`, `slot_frame`,
`slot_block`, `slot_ready` and `rearmed` report the driver's decision.
`fault_frame` and `fault_block` identify an earlier failure if present.
The row cursor retains its last render phase, with row 65535 before any
source row. A saved record lasts for the current boot, including carrier
replacement. A P4 reset begins a new capture.

The host handoff suite ran seven scenarios for each carrier: successful
publication, withheld work, interruption at each of the two reader-mutex
acquisitions, interruption in render or cache clean, and an underrun before
the target handoff. It compared the record when sealed with its bytes after
worker resumption, panel teardown, opposite-carrier allocation, the second
panel's own frame-2 wrap and a later fault. All 14 passed. The ordinary
handoff control passed as well. The C++ renderer check observed the lock
cursor at cropped source row 112 and expansion at row 127. The resulting
strip matched ordinary stock output byte for byte, including the expected
2×2 marker.

The clean experimental P4 build is
`hdmi-native-row-r03-b2026-11-22-00-59-15Z`. Target validation passed, all
85 artifact hashes verified, and the application embeds the linked ELF hash.
The 1,775,664-byte application SHA-256 is
`b8c0cda3255a4cf840e52d12b97fb448a6255e40cc2dd70a54fa8fe84b5209f6`.
The DMA driver, renderer and HTTP service each gained only the trace selection
among their Extender compiler flags compared with r02. Source, binary, ELF,
manifests and test evidence are retained in the local `trace-r03` build silo.

The HTTP host test linked the real C getter and C++ request handler with a
modeled HTTP transport. It verified an unavailable response before the
decision, then byte-identical JSON across mode replacement for both success
and a fault during rendering. The existing live-status and last-fault queries
continued to report their respective epochs.

Disassembly shows aligned RISC-V word stores for the row markers. The trace
uses 274 bytes of static internal data, including the 156-byte sealed record,
excluding alignment and the per-panel selection flag. For the traced block,
the renderer adds at most 97 cursor writes at 1:1 or 49 at exact 2×. The
no-wake, dirty, bound path adds at most 14 worker clock reads plus one each at
enqueue and the frame decision. The snapshot copies 27 timestamp words at
the decision. These are static operation counts. On-board timing and the
stage reached during the real blue-screen failure remain open. This work did
not access or flash the Olimex bench.

**Single Olimex startup capture.** Smith authorized one r03 install and boot.
The operator confirmed the Legacy prompt in the Nurples directory and verified
the startup and listener files. The entire 1,794,048-byte app0 extent matched
independent readback (SHA-256
`1ac06cdd528010be6fad7b8738cf7a8d1bf6ca838192a547ab7c51a579ebb7a4`).
The first boot reported the r03 build identity. The operator collected the
sealed trace, saved fault and live counters before issuing any mode change or
additional reset. The private receipts are in `trace-r03/bench/`.

Relative to retirement of frame 1 block 12, the interrupt enqueued frame 2
block 0 at +4 µs. The worker dequeued it at +13 µs, acquired its wake-decision
reader mutex at +25 µs, bypassed the sampling gate at +34 µs, acquired the
render reader mutex at +39 µs and entered the bound renderer at +47 µs. At
the rearm decision (+2,066 µs), the cursor still read **row_lock, source row
0**. The next marker, written just after acquisition of the stock native
drawing lock, was absent. All 15 blocks had retired. Slot 0 had the requested
generation but was unready. DMA rejected rearm. Both fault reports agreed on
30 total retirements, 27 publications, one rejection and zero invalid or
underrun interrupts. The 2,019 µs from renderer entry to EOF includes work
before the lock marker; the trace establishes neither exact lock wait duration
nor the holder or whether the worker was preempted. The operator stopped after
collection with r03 installed and custody retained for Smith's review.

After the r03 capture, Smith observed solid blue Extender video while the
mainboard MOS prompt continued to accept external keyboard input. The P4
also served the sealed trace over HTTP during collection. These observations
establish that the scanout failure can coexist with functioning P4 services.

### Released P4 handback and startup drawing-lock review

The operator restored the v0.3.0 P4 application in the original Olimex slot.
The 1,768,624 application bytes matched the released SHA-256
`539dc7176f079bc6c298c48352b7e94c54db654fb6fdbb9c42897370fb19834b`.
The independent readback of all 1,794,048 written bytes at `0x20000` matched
the padded release byte for byte, SHA-256
`071ac03fe4b6159df8e1b15f825d523e92fe55653e681571bb44496c2d0368c1`.
Handback verified the Legacy MOS prompt, keyboard ready with no keys held,
listener offline, transfers idle and serial handles free. The supervisor
joined its workers. The scheduler closed the reservation and reported the
FIFO empty. The r03 failure capture and restore receipts remain in the
private `trace-r03/bench` evidence directory.

**Startup ownership in the captured build.** At source `b9b430c57e2b`,
the P4 Arduino setup task starts the HDMI carrier and calls `changeMode(0)`
before starting the VDU command processor (`vdp/video/video.ino`). Mode 0
selects a 640×480 single-buffered, 16-colour controller. Source row 0 takes
the P4 global recursive drawing mutex before reading its pixels and signal
map (`stock_runtime_controller.hpp`, `traceNativeRow`).

| Possible owner | Relation to the frame 2, block 0 failure |
| --- | --- |
| P4 setup task preparing the viewport and FabGL default palette | Holds the mutex during `setResolution`. That call returns before the native row callback is bound. |
| P4 setup task restoring the Agon mode palette | `commitPreparedMode` activates the row service. Afterwards `changeMode` calls `restorePalette`. Each of 16 physical palette writes takes the row mutex briefly. Then `VGAPalettedController::updateRGB2PaletteLUT` holds it across 64 input colours and up to 16 HSV distance comparisons per input. This is the strongest candidate for a long hold. |
| P4 stock drawing worker or VDU parser | The live counter recorded zero draw wakes. Setup starts the parser after the mode change. The bench held the eZ80 in reset through P4 startup. The failure predates application drawing. |

The trace places the refill task at the first row's lock-acquisition marker
when DMA rejected block 0. It records neither the owner nor the scheduling
history at that marker. The 2,019 µs from renderer entry to the decision is
an elapsed interval, not a measured mutex hold. The ordering defect is
visible in source. The particular palette operation occupying that interval
is inferred. Stock mainboard VGA takes its per-line colours from the signal
map. The reverse RGB-to-palette table serves drawing. The P4 port couples the
two through the same mutex.

**Duplicate work.** FabGL already builds that reverse table in
`setResolution`. Comparing `COLOR2RGB888` with Agon's `defaultPalette10`
through the controller's actual RGB222 conversion gives 16 equal entries
in the same order. Mode 0 computes the same 64-entry table twice. Other
depths, including four colours, have different defaults. Any future
elimination of the duplicate must preserve Agon's 64 logical palette entries
and use the actual selected colours.

**Approved native row handoff.** On the P4 native row
path, let the new service supply live rows only after `changeMode` completes
the selected mode's palette setup. Have the existing row-zero check latch
readiness for the whole frame. During setup the callback supplies its existing
black DMA slots. The physical frame callback and stock drawing service keep
their normal cadence. A failed mode change must restore the former mode's
readiness when its palette is settled, including the official fallback path.
This changes the order of one handoff and needs no extra image buffer or
pixel copy.

For verification, hold palette initialization across two simulated wraps.
Require valid black publications throughout the hold, then the complete
expected pixel and palette output from row zero of the first live frame.
Exercise a mode with different defaults, teletext, and failed preparation
with an existing controller. Check the public frame count and the first live
block's publication as well as frame 2. On a subsequent authorized bench
run, require zero refused rearms and measure the first live refill against
the existing 1,600 µs limit. Sustained drawing and scrolling remain separate
load tests.

Smith authorized the P4 implementation, candidate build and offline checks.
Freeze this contract on the task branch before changing the r03 component
source. Build from that source with the same native row and startup trace
selections. Retain the candidate identity, image hashes, frame and pixel
results in this task. Return them to Smith before any Olimex reservation.

### Native row admission after palette setup — candidate r04

The plan reached the remote at `3e07e326974b109ee24279a31f8a10be1f181099`
before implementation. Candidate source `4c5a16a7e70b05221f8de78a48a09c05a5af4378`
adds a readiness flag to the native P4 display service. Setup clears the
flag before binding the row callback. The stock mode caller sets it after
palette or teletext setup, including after a failed allocation reattaches
the former controller. Row zero samples it once for the whole frame.
During double-buffered setup the drawing worker acknowledges its normal
wake immediately. Even an empty sprite pass would otherwise acquire the
palette mutex and delay DMA through the swap acknowledgement. Single-buffer
setup retains drawing opportunities, including those needed by teletext.

The clean P4 build is `hdmi-native-row-r04-b2026-11-22-02-00-35Z`.
The target validator passed, all 85 retained artifact hashes verified, and
the 1,856 compilation actions carry the same Extender definitions as r03.
Only three P4 files changed among the 5,575 archived source inputs.
The 1,775,776-byte application is 112 bytes larger than r03. Its SHA-256 is
`0dea7a3f6d3954ea3a55eb0c6af63683730eaeadee4152d7a6794bf2b188e77c`.
The RISC-V image calls the bitmap palette restore before its release-store
to the new flag. Target debug information places the flag in existing
padding. The display service occupies 1,184 bytes in both builds.

**Offline DMA and pixel results.** The host fixture exercised the native C
ring, stock P4 service, FabGL controllers, and the build's generated ESP-IDF
frame-complete callback. The host modeled the interrupt, DMA registers and
clock. It held the real drawing mutex on another thread through rearm into
frames 2 and 3, then finished installing the palette after frame 3 block 4.
Every consumed descriptor and slot was checked before retirement.

| Measurement on the 848×480 carrier | 640×480, 16 colours, single buffer | 320×240, 4 colours, double buffer |
| --- | ---: | ---: |
| Bound frames 2 and 3, black pixels matched | 814,080 / 814,080 | 814,080 / 814,080 |
| First live frame 4, pixel triplets matched, including borders | 407,040 / 407,040 at 1× | 407,040 / 407,040 at exact 2× |
| DMA rearms across bootstrap, setup and live output | 5 / 5 | 5 / 5 |
| Retired blocks / publications | 75 / 75 | 75 / 75 |
| Refused rearms / invalid descriptors / underruns | 0 / 0 / 0 | 0 / 0 / 0 |

Frame 2 block 0 sealed ready and black with no source row sampled. Frame 3
stayed black after setup completed partway down the image. The fixture
compared frame 4 against an independently calculated tile pattern using Agon
palette IDs and BGR byte order. The public frame counter reached four after
five physical rearms because the callback was bound after the first wrap.

Ten mode-lifecycle cases exercised the original mode and palette callers
with controlled allocation and teletext results. They covered successful
bitmap and teletext entry, failed preparation with the former controller,
failed teletext entry and previous/default-mode fallback. A separate real
drawing-worker check held the mutex during two double-buffered black-frame
wakes. Both completed, and the first queued live swap waited for its own
acknowledgement before the expected pixel appeared. Single-buffered drawing
continued while the output was black.

Under the identical held-mutex condition, the r03 service tried to sample
source row 0 at frame 2 block 0. The test caught it before publication. With
r04 the pixel, rearm and frame-count checks passed both with and without
the startup trace. The regression fixture is published at
`9fde0d8787f53c8cb412524b96a18aed23bf4d55` on the component branch. The
test-only commit follows the clean firmware build. Private target, host,
negative-control and compiler-release receipts are in `native-rows/palette-r04`.
The physical 1,600 µs refill limit and on-monitor startup still require a
bench run. Smith reviews these results before reservation.

**Olimex r04 first boot.** The candidate boot log identified the r04 build.
The independent flash readback matched all 1,794,048 written bytes at
`0x20000`, SHA-256
`42199f2399a5c0e02b1447d2f2de9ae89c124e959d413706dcd79eba651578c5`.
The operator verified a working Legacy CLI after installation.

| Hardware observation | Result |
| --- | --- |
| Frame 2 block 0 | Row sampling was inactive. The P4 published the black slot at +89 µs and accepted rearm at +2,067 µs, both relative to the retirement interrupt. The slot was ready 1,978 µs before the rearm decision. |
| Frame 3 block 0 | The P4 refused the next handoff. Both live and saved counters showed 2 successful frame rearms, 45 block retirements, 42 publications, 1 rejection, 0 invalid descriptors and 0 underrun interrupts. |
| First live refill against 1,600 µs | Unmeasured. Frame 3 was the first eligible live frame after the traced black frame. The one-shot captured no frame-3 row marker, and the sequence fault captured no completion timestamp. The 89 µs maximum covers completed refills only. |

The operator retained the sealed trace, both counter snapshots, the boot log,
flash readback and supervisor receipts in the private `palette-r04/bench`
directory. The failure alert completed. The run stopped with r04 installed
and bench custody retained for Smith.

### First live refill at startup — approved trace r05

The offline comparison reproduced the install receipt from the retained bytes.
At app address `0x20000`, the independent flash readback equals the retained
r04 application (1,775,776 bytes) followed by 18,272 bytes of `0xff`. Its
1,794,048-byte extent has the SHA-256 recorded above. The operator retains the
Olimex reservation with r04 installed.

#### Where frame 3 block 0 reached

| Event on the mode 0 boot | What the evidence establishes |
| --- | --- |
| Frame 2 block 12 retired | The three-slot ring assigned slot 0 to frame 3 block 0 and queued the refill. The preceding top block had taken the startup bypass and rearmed black. |
| Drawing wake returned, then frame 2 block 13 retired or had already retired | The worker could pass the gate once DMA entered the final block. The only counted drawing wake and the only recorded wake-to-ownership gap belong to frame 3 block 0. |
| Worker confirmed ownership of slot 0 | The worker had acquired the driver's reader mutex for the wake, released it, passed the gate, and acquired it again to refill. The measured **1,024 µs** runs from the wake callback's return to the ownership check. The retire-to-wake interval was additional. At most **576 µs** remained until the 1,600 µs limit, or **560 µs** until the pre-publication check that reserves 16 µs for arming the descriptor. |
| Frame 2 block 14 retired and the frame ended | DMA had consumed the three primed blocks and all 42 published refills. The next top block lacked a ready publication, so the P4 refused rearm into frame 3. The end-of-frame fault supplies no completion duration. |

Frame 3 is the first live *candidate*. r04 sealed its row cursor on frame 2,
so live admission and the last row reached on frame 3 are unknown. In mode 0 a
live top block reads 32 stock rows of 640 pixels and expands 20,480 pixels to
three bytes each. The driver then requests cache writeback over the 81,408-byte
physical slot (32 × 848 × 3). A wait for the stock drawing mutex, the accumulated
cost of processing those rows, and a later delay before descriptor publication
are all consistent with the capture. The 89 µs maximum describes completed
refills. The routine row profiler did not sample frame 3.

Reviewed in the flashed [r04 ring](https://github.com/bgates747/agon-extender/blob/4c5a16a7e70b05221f8de78a48a09c05a5af4378/vdp/video/extender/display/native_scanout/native_ring.h#L35)
and [DMA worker and frame interrupt](https://github.com/bgates747/agon-extender/blob/4c5a16a7e70b05221f8de78a48a09c05a5af4378/vdp/video/extender/display/native_scanout/native_runtime.inc#L265).

#### Smallest diagnostic change

Use the existing P4 startup trace flag, one scratch record and one frozen
record. The proposed change selects the first live top block dynamically.
The r04 host fixture already demonstrated that palette setup can put the first
live pixels on frame 4.

1. At the third-last retirement of each startup frame in epoch 1, the DMA
   interrupt arms scratch for the upcoming frame's block 0. It records the
   actual target tag, clears the row and timestamps to their unseen values,
   and uses the retirement timestamp as zero. Enqueue, worker and interrupt
   probes all use that tag. This captures a failure even before the worker
   calls the renderer.
2. The P4 service records its existing row-zero readiness decision. For a
   live refill the existing cursor identifies the logical row and the last
   boundary crossed. `row_lock(y)` precedes acquisition of the stock drawing
   mutex, `compose(y)` follows acquisition, and `expand(y)` follows release
   and precedes conversion of the stock row to BGR bytes. The driver already
   timestamps render entry/return, cache begin/end or skip, entry into the
   publication critical section, and successful publication after descriptor
   VALID. Use those markers and the existing worker/gate timestamps. The
   row loop needs only its existing cursor stores.
3. The frame interrupt uses the actual rearm result under the existing ring
   lock. Recycle scratch only after a successful rearm with explicit inactive
   admission or a confirmed unbound black path. Freeze on the first live
   rearm decision or any earlier fault. Save the target tag, actual fault
   tag/site, retired count, slot tag/readiness, cursor and event times together.
   An early fault can have unknown admission or no armed target. A live row
   of black pixels still counts as live. The status endpoint reports the
   saved target. Worker resumption and subsequent mode changes must preserve
   the frozen record.
4. On successful publication, report retirement-to-VALID in µs against
   1,600 and report rearm separately. On an unpublished EOF, report the last
   stage and row plus elapsed time to the decision as a **lower bound** on
   time to publication. At or below 1,600 µs an EOF refusal still proves a
   missed handoff. A single cursor locates the unfinished stage but cannot
   establish its total cost, a mutex owner or a deadlock. Formatting takes
   place when the host retrieves the record.

The existing [row-zero readiness latch](https://github.com/bgates747/agon-extender/blob/4c5a16a7e70b05221f8de78a48a09c05a5af4378/vdp/video/extender/display/stock_p4_service.cpp#L205),
[stock row cursor](https://github.com/bgates747/agon-extender/blob/4c5a16a7e70b05221f8de78a48a09c05a5af4378/vdp/video/extender/display/stock_runtime_controller.hpp#L239)
and [status formatter](https://github.com/bgates747/agon-extender/blob/4c5a16a7e70b05221f8de78a48a09c05a5af4378/vdp/video/extender/network/display_status.hpp#L55)
define the observation points. This change requires no extra DMA slot, pixel
copy, per-row clock read or serial logging in the refill path.

**Approved offline checks.** Use the existing ring, renderer
and frame-callback fixture to move live admission among frames 2, 3 and 4,
including a mid-frame palette release and an all-black live image. Exercise
pre-admission failure and interrupt the first live block at the drawing lock,
stock composition, expansion, cache writeback and publication. Check the
reported tag, row, missing milestones and time bound for each case. On success
check the expected pixels, publication timestamp and actual rearm. Exercise
the 1,584 µs pre-publication and 1,600 µs post-VALID boundaries. Resume the
worker, replace the mode, and read the sealed record again to verify identical
bytes. Smith approved this diagnostic plan, implementation, build and offline
verification. The operator holds the Olimex reservation for review before flashing.

### First live refill trace r05 — build and offline verification

The P4 diagnostic captured the first admitted live block on frames 2, 3 and 4
in separate host boots. The saved record survived replacement of the display
mode and panel in every case. A controlled frame-end interruption also located
the unfinished logical row and stage. The Olimex still has r04 installed. The
actual stall and its timing remain open until a physical r05 run.

The task plan was pushed at `28bf7e51` before implementation. The firmware
change is `b125e060` on `codex/hdmi02-size01`. The clean, built revision
`d5b5ad8919ae844af511539078413d4135c6841d` includes the regression fixtures.
Build `hdmi-native-row-r05-b2026-11-22-02-39-54Z` produced a 1,777,008-byte
application, 1,232 bytes larger than r04. Its SHA-256 is
`22794c82c988cbc51efde81eb708607be6dbe6e10c2cab85bbb901dbb8add9ff`.
The native target validator passed. All 85 artifact hashes and 5,575 archived
source inputs verified. Four firmware files differ from r04. All 1,856 compile
commands matched after normalizing the output directory and embedded project
version. An earlier compile received SIGTERM before linking. Its supervisor
joined its children, and a fresh supervised build completed in 538 seconds.

| First live block in the test boot | Live image, logical mode | Result after replacing the mode and panel |
| --- | --- | --- |
| Frame 2, block 0 | Colour tiles, 640×480 single buffer | Block published and rearmed. Frozen bytes matched throughout replacement. |
| Frame 3, block 0 | Entirely black live image, 640×480 single buffer | Explicitly admitted live. Earlier setup black skipped. Frozen bytes matched throughout replacement. |
| Frame 4, block 0 | Colour tiles, 320×240 double buffer, exact 2× | Setup completed partway through frame 3. Frame 4 was the first live frame. Frozen bytes matched throughout replacement. |

The host fixture used the stock P4 service, FabGL controllers, native ring and
the frame-complete callback from the r05 build. It checked all 407,040 BGR
pixels on each of 30 frames, including borders. Across the six model panels
DMA rearmed 30 times and retired 450 blocks, with zero refusals, invalid
descriptors or underruns in these success cases. The ordinary build of the
host fixture also passed, and the service fixture observed the lock cursor
while another thread held the actual stock drawing mutex.

1. The fault fixture ran 14 cases on each carrier. At an injected frame end
   on frame 3 block 0 it distinguished a wait for the stock drawing mutex
   on row 7, stock composition on row 7, expansion on row 7, cache writeback
   and waiting to publish. A separate case preserved an earlier descriptor
   fault with its own frame/block. The frozen bytes survived resumed workers,
   disposal of the old slots, opposite-carrier rearm and a subsequent fault.
2. With the modeled clock, the driver accepted a pre-VALID check at 1,584 µs
   and publication at 1,600 µs. It refused a pre-VALID check at 1,585 µs and
   revoked VALID at 1,601 µs. The status response distinguished successful
   publication, budget rejection and an unpublished frame-end decision. At
   1,400 µs the latter reported a lower bound and an unknown budget outcome.
   Eight HTTP cases returned byte-identical startup records after replacement.
3. The linked P4 image has a 168-byte frozen record and 108 bytes of scratch
   timestamps. Static trace objects occupy 290 bytes before alignment. The
   row cursor compiles to aligned word stores. The diagnostic reuses r04's
   pixel converter and three DMA slots.

The private `first-live-r05` evidence directory retains the application, ELF,
matched build inputs, archive verification, frozen example responses and host
test logs. All timing values from the host fixtures use a modeled clock.

### Olimex r05 — single physical startup

The first live refill was frame 3 block 0. At frame end the P4 worker had
processed logical rows 0–27 and reached the stock drawing mutex on row 28
of the 32-row block. The trace froze before the after-acquisition marker.
DMA refused rearm with the slot still unpublished. The cursor locates the
worker at frame end. It provides neither a row-specific wait duration nor
the identity of a lock holder.

| First live block event | µs since slot retirement |
| --- | ---: |
| Worker dequeued the request | 12 |
| Drawing wake returned | 25 |
| Sampling gate opened | 1,040 |
| Worker entered the live renderer | 1,048 |
| Refill deadline | 1,600 |
| Frame ended, rearm refused | 2,068 |

Only 552 µs of the refill budget remained when rendering began. At refusal,
1,020 µs had elapsed since render entry and the slot was at least 468 µs
over budget. Cache writeback and descriptor publication had no entry markers.
Both counter snapshots recorded two successful earlier rearms, 45 retired
blocks, 42 publications, one rearm refusal, zero invalid descriptors and
zero hardware underrun interrupts.

The independent app0 readback matched all 1,794,048 written bytes at
`0x20000`, SHA-256 `1b82f7b3cc335b34fdfe06795f00c4dfde4279574ab5ea6b045dd72132baccfd`.
The boot log identified r05 and the installer verified the Legacy CLI.
The private `first-live-r05/bench` capture contains the sealed response,
both counter snapshots, UART boot log, readback and supervisor receipts.
The sealed response SHA-256 is `e475777217d5666ce7708aaeb3001d58f76c6eff501c17b845caf20eb5ab3009`.
The operator stopped after this boot with r05 installed and the slot held.

### Why r05 waited at the frame boundary — offline fix for review

The P4 port deliberately gave the drawing task one 32-line DMA interval
before sampling next-frame row zero. On the retained boot that policy spent
1,011 µs waiting after slot 0 was already writable. The first live refill
ran out of time during row processing. Contention at row 28 remains possible,
but the trace establishes no duration for that particular acquisition.

| Event, measured from retirement of frame 2 block 12 | r05 |
| --- | ---: |
| The ring retags slot 0 for frame 3 block 0 | 0 µs |
| The core-1 worker returns from notifying core-0 drawing and then enters the sampling wait | 25 µs, then 29 µs |
| Block 13 retires, satisfying the port's gate; the worker observes it | 1,030 µs, then 1,040 µs |
| Rendering starts, leaving 536 µs until the pre-VALID check and 552 µs until the deadline | 1,048 µs |
| At the rearm decision, 28 rows are complete and row 28 has reached its pre-lock marker | 2,068 µs |

The three-slot ring advances the requested tag by three at each retirement.
Block 12's interrupt gave the worker a valid claim on the new slot. The
separate `nr_may_sample` test requires 14 of 15 old blocks to have retired
before admitting a next-frame request. Both P4 carriers use 1,104 pixel
clocks per line at 240/7 MHz, or 1,030.4 µs per 32 active lines. The 10 µs
from block 13's interrupt to the observed gate opening accounts for the
small remainder. The full-transfer callback checks the top slot before it
reenables DMA. Vertical blank on the HDMI signal supplies no additional
time before this software decision. [Ring](https://github.com/bgates747/agon-extender/blob/d5b5ad8919ae844af511539078413d4135c6841d/vdp/video/extender/display/native_scanout/native_ring.h#L35) · [Worker](https://github.com/bgates747/agon-extender/blob/d5b5ad8919ae844af511539078413d4135c6841d/vdp/video/extender/display/native_scanout/native_runtime.inc#L297)

Stock VDP v2.16.0 uses four signal-row buffers for 16-colour VGA and fills
two per interrupt. In mode 0 the interrupt for visible row 476 prepares rows
478–479 and then notifies drawing. The interrupt for row 478 prepares the
next frame's rows 0–1. The two interrupts are nominally 63.6 µs apart
(two lines of 800 clocks at 25.175 MHz). This is a raster interval. Actual
CPU time available to drawing depends on when the task runs. Stock permits
single-buffer drawing to overlap scanout. The P4 adopted the order but
stretched the interval by using 32-line strip retirements. [Stock descriptor placement](https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/dispdrivers/vgapalettedcontroller.cpp#L177) · [Row preparation and drawing notification](https://github.com/AgonPlatform/vdp-gl/blob/ac2dd5986daf496c43ae8e7fe41836274aec54a0/src/dispdrivers/vga16controller.cpp#L754)

**Row 28.** The 1,020 µs from render entry to refusal includes stock row
preparation and BGR expansion for all of rows 0–27, their lock acquisitions,
and any preemption. There is no per-row clock or owner in the frozen record.
The linked mode-0 inner loops alone execute 1,720 instructions per 640-pixel
row for packed 16-colour decoding and 7,360 for BGR expansion. These counts
describe work, not wall time. The startup palette restore had completed before
live admission. The core-0 drawing worker could still take the mutex in a
queued primitive or its final sprite pass. A single EOF cursor cannot assign
the missed time to a holder. The trace also never reached cache writeback.
[Row cursor](https://github.com/bgates747/agon-extender/blob/d5b5ad8919ae844af511539078413d4135c6841d/vdp/video/extender/display/stock_runtime_controller.hpp#L239) · [Drawing callback and swap acknowledgement](https://github.com/bgates747/agon-extender/blob/d5b5ad8919ae844af511539078413d4135c6841d/vdp/video/extender/display/stock_p4_service.cpp#L264)

**Proposed P4-only change.** Move the existing once-per-frame drawing wake
from entry to the incoming top-block job to the successful publication of
the outgoing final strip. On this carrier, block 11's retirement requests
that final strip (14). When block 12 retires, the same FIFO worker can start
the next top strip as soon as it owns slot 0. Remove the extra wait for block
13 on that top job. The old strip must already be DMA-visible before any
swap wait. Invoke the existing callback outside the ring critical section,
under the reader/binding lifetime protection and only for its valid binding.
Preserve startup black and palette admission, the single-buffer notification,
the double-buffer drain acknowledgement before row zero, the per-row stock
mutex, and the public frame tick at actual DMA rearm. Keep cache-before-VALID
and both budget checks. Carry the wake timestamp/tag across these two jobs
for the existing drawing-gap diagnostic. An early wake can precede the
refill origin, so report wake-to-sampling separately from retire-to-VALID.
This needs no extra pixel buffer, copy or timer.
The head start for single-buffer drawing is the interval between tail
publication and the first top-row read. It can be short if the worker is
already behind. The proposal reproduces stock ordering at strip granularity.
For modes with vertical borders, verify the last actual source row as well
as the final carrier strip.

**Verification if approved.** On both 12- and 15-block carriers, exercise
ordinary and backlogged tail publication, unbound/black and live transitions,
mode teardown, single-buffer scrolling, and a queued double-buffer swap.
Verify one wake after final publication, top pixels from the correct bank,
matching first/last rows and an immutable first-live trace. Then measure
retirement-to-VALID against 1,600 µs and wake-to-first-read separately.
Sustained active blocks arrive every 1,030.4 µs. A passing top block alone
cannot establish sustainable throughput. Check subsequent blocks, queue
growth and refused rearms. If row processing still misses, use a bounded
first-live measurement of lock wait, composition and expansion before
choosing a mutex or pixel-loop change. This proposal awaits review with
the Olimex reservation held and r05 installed.

### Two-row interrupt test for review

**Question.** Can the Olimex P4, with its DSI bridge controlling the transfer, retire exactly two physical rows at a time and refill their storage in the DMA interrupt through frame wrap? Use one 848×480 RGB888 carrier, the same 1104×517 totals and PLL240/7 clock as r05, and a fixed pattern. This isolates the hardware handoff before introducing any stock framebuffer, palette, Copper, sprites, drawing locks or RTOS refill task. Stock's interrupt-driven row preparation remains the implementation baseline.

1. **Show the reference first.** Use one standalone P4 diagnostic image. It boots idle. On an explicit operator command over the P4 USB console, immediately show the existing 848×480 HDMI timing card through its known-working full-frame path. The viewer should see labelled colour bars, a white border, corner labels and a centered 512×384 field, with a small amber reference marker. Hold it while the monitor locks, for at least one full second after settling and until the operator starts the live phase. Tell Smith as soon as the reference is available. The Pi operator owns both commands. Smith can watch without typing, taking measurements or confirming each step. The reference can stay up if Smith wants time to see it. This is an isolated P4 transport test. Its USB console stays available independently of the Agon keyboard and EVDP network services. [Existing timing card and fixture](../../../vdp/hdmi-timing-test/README.md) · [Existing mode-preview patterns for subsequent stock integration](SIZE01-VISUAL.md)

2. **Switch only the source of pixels.** Positively stop the reference DMA channel before reprogramming the transfer. Keep the carrier, LT8912B settings and monitor input. In the live phase fill the screen with the card's eight colours in their familiar order. Give every physical row an identifying mark in a narrow side strip encoding its absolute row and frame number. Add a wide green corner marker that changes position once per second, so Smith can recognize live output at a glance. Draw the bars and marks by writing both complete BGR rows into the retired slot in the interrupt. Only pairs 0 and 1 of the first frame are primed before DMA starts. They carry the colour bars with the reference marker colour. From the first wrap, even the top four rows must come from the interrupt. The reference framebuffer never supplies live pixels. Use a finite five-second viewing interval (300 complete live frames at the nominal 60.07 Hz). Time the first two frames separately from the rest. No mode matrix, game, SD payload or load generator.

3. **Program one observable handoff.** Select the DSI bridge as flow controller and the DW-GDMA channel's destination-peripheral flow mode, with hardware handshaking from memory to the DSI FIFO. Configure frame and block word counters and their reloads while stopped. Enable multiblock explicitly. Record the effective flow, counters, reload, credit and burst settings. At 64 bits per word the bridge must terminate each pair at **636 words** (5,088 bytes) and the frame at **152,640 words**. Use a compatible request size that divides 636. The old four-bit DMA-controlled count cannot encode 240. The bridge's block-end handshake is precisely what this experiment must demonstrate. The VDMA programmed block-size field alone cannot verify how many words the peripheral accepted. [P4 revision 1.3 VDMA manual, §§5.5.4–5.5.5](https://documentation.espressif.com/esp32-p4-chip-revision-v1.3_technical_reference_manual_en.pdf) · [Bridge flow registers](https://github.com/espressif/esp-idf/blob/v5.5.5/components/soc/esp32p4/register/hw_ver1/soc/mipi_dsi_bridge_reg.h) · [Earlier hardware review](../SCAN-001/S03-FEASIBILITY.md)

4. **Use stock's four physical rows of rolling storage.** Allocate two private, 64-byte-aligned 5,120-byte slots and 240 aligned internal descriptors, one per pair. Each descriptor transmits exactly 5,088 bytes. Only the first two descriptors start valid. At interrupt entry, check the expected descriptor through its uncached alias for *fresh* hardware completion, its actual transferred amount and the expected slot generation. Reject missing, out-of-order or merged events. An interrupt counter alone cannot identify the retired descriptor. Once pair p retires, the interrupt fills the same slot for p+2 modulo 240, advancing the frame tag on wrap. Finish stores, clean the private aligned range as needed, clear stale completion status for the incoming descriptor, fence, then publish VALID last. Keep future descriptors invalid until ready. The last pair alone carries LAST. Check the final block and full-transfer events, then rearm only with the correct next-frame top pairs ready. Record actual retirement of the ISR-produced pair 0. Frame-boundary ownership and writeback ordering require offline checks, including a coalesced event, a stale DONE and a withheld VALID. Check offline that every generated pixel matches an independent pattern oracle and that the linked ISR contains no queue, sleeping lock, allocation, logging or framebuffer-copy path.

5. **Score the evidence automatically.** Keep counters, worst callback-entry-to-VALID and full-handler times, minimum observed lead to reuse, and a small first-wrap record in internal RAM. Preserve entry, publication, actual hardware completion and channel-rearm evidence with pair/frame identities, especially 238, 239, 0 and 1. The Pi collects one compact serial result outside the ISR. A pass on this carrier requires 240 fresh 636-word completions per frame, full-transfer done only at 239, 300 complete frames (72,000 pairs), 299 successful wraps, correct final-slot pixels, no underrun, invalid descriptor or unexplained event, and refill service within the nominal **64.4 µs** active-pair interval. Record measured IRQ spacing separately. FIFO lookahead makes this a service-time comparison rather than a measurement of HDMI raster phase. Suppress refills for pairs outside the finite run so the final two slots retain the last frame's pairs 238 and 239 for independent readback after stop. A clean receipt establishes direct IRQ refill and DMA consumption for this fixed workload. Record monitor observation or native capture separately. A picture alone cannot certify all pair retirements, and serial telemetry alone cannot certify what Smith saw.

   Check interrupt context on the first live fill and count publications at that same ISR-only site. The expected split is two task-primed pairs and 71,998 ISR-produced pairs. Have the Pi compare the final two slot payloads over USB against the independent oracle after DMA has stopped. Report a timing miss separately if hardware still retired every pair correctly. A missing or ambiguous writeback makes the retirement result inconclusive. A first failure localizes the tested configuration and does not settle every possible bridge configuration.

6. **End predictably.** On the first fault freeze the last good pair, failing register/descriptor state and timing. A bounded no-progress timeout also ends collection if the peripheral never signals pair completion. Stop rearm, verify the channel is disabled before freeing or rebinding anything, and report over USB even if HDMI is black. On success, once the live channel is stopped, return to the known-working reference card and identify it as reference again. On failure retain the evidence and report the last visible phase before recovery. Reset boots idle. A later commissioned installation would use app-only write/readback and retain the exact restore image. The implementation gate was approved November 22. Preserve the reservation and separately record the installation and invocation boundary before any physical phase.


### Standalone two-row fixture — build and offline results

The approved plan was frozen in `46391edc`. The [fixture source](https://github.com/bgates747/agon-extender/tree/e4b97005120d48723db020f0ca9ebdd1992ee629/vdp/hdmi-timing-test) builds as `hdmi-pair-irq-r01-b2026-11-22-17-01-22Z`. The retained app is 294,912 bytes, SHA-256 `71479f5dde8caf39d97bb7a3ab555248eb16852583bc17c78258009222d36abc`. The app0 selection is `0x20000`; the independently checked 1,794,048-byte padded image covers the prior approved extent. The IDF 5.5.5 image header admits the installed P4 revision, its SHA-256 trailer verifies, and its partition table matches the recorded table. The standalone USB console boots idle after powering the P4-PC shared GPIO bank and checking all eleven Agon-facing pads for input mode with output and pulls disabled.

The Pi compared all 72,000 computed row pairs with an independent pixel oracle; all 366,336,000 payload bytes matched and the padding guards remained intact. A separate host test ran the actual DMA callbacks against simulated descriptor and channel registers. It verified two primed pairs, 71,998 interrupt publications, 299 rearms, final pixels retained in the last two slots, and a stopped channel before restoring the reference. Eight injected faults covered stale writeback, coalesced events, withheld top VALID, invalid descriptor, premature frame completion, short transfer, underrun and attempted refill in task context. The linked target contains the DMA interrupt dispatcher, pair completion, pixel stores, cache publication and ownership fence. These offline results leave the physical two-row handshake and interrupt residency open.

**Olimex reference card staged, November 22.** The Pi verified entry at the Legacy MOS prompt and checked the preserved startup files. It compared the installed r05 app0 extent before writing, checked the partition table and selector, and compared every byte of the new independent flash readback at `0x20000`. The 1,794,048-byte extent SHA-256 was `8aacbaa29db1c3b7671b9acb5e2b28e770c0980fac4cc53d22f1d0452c0ef6bc`. The P4 reported all eleven shared pads isolated and booted to its standalone USB command gate. The operator issued only `preview` and `status`. The bridge reported HDMI hot-plug detect high, the reference DMA count advanced from 60 to 61, and the P4 returned `state=reference ready=1`. The completed supervisor joined all children. Smith was alerted with the reference held and the Olimex reservation active. No live trial ran. Optical confirmation remains with Smith. EVDP networking and replacement keyboard service are absent while the standalone application is installed. The local `pair-irq-r01/bench/install-preview` record retains the readback, serial evidence and ready receipt.

### Olimex two-row interrupt trial, November 22

Smith saw the static reference card fill the screen with square pixels and no apparent scanout errors. Immediately before the trial, the standalone P4 reported 29,446 reference frames, HDMI hot-plug detect high and the reference ready. The Pi sent `live` once. The P4 stopped on frame 0, pair 0 (rows 0–1).

| Check | Expected | Observed |
| --- | ---: | ---: |
| Completed transfer count for pair 0 | 636 × 64-bit words | Descriptor field read 639 |
| Validated row pairs | 72,000 | 0 |
| Completed live frames / frame rearms | 300 / 299 | 0 / 0 |
| Primed pairs / interrupt refills | 2 / 71,998 | 2 / 0 |
| Worst refill, callback entry to VALID | ≤64.4 µs | No refill reached publication |
| Primed pixels, frame 0 rows 0–3 | 10,176 bytes | All matched the independent oracle after DMA stopped |

The DMA descriptor had BLOCK_DONE set, frame-done clear and VALID clear. The first failing check was the completed word count. Frozen descriptor status-high, status-low and control-high were `0x40000000`, `0x0000027f`, and `0x04048240`. The field disagreement alone does not establish the physical number of words transmitted. The interrupt handler that detected the fault and stopped the channel used 8,255 cycles (22.93 µs at 360 MHz). It exited before the first interrupt refill, so the 64.4 µs refill comparison remains open. The bridge recorded zero underruns up to the stop.

The P4 verified that live DMA had stopped and ended with `ESP_FAIL reference_ready=0`. It left the reference unrestored. The Pi preserved the raw 21,396-byte USB trace, SHA-256 `01f6f92a9dcdc03958e59c3bc15b21d52acf1cd425ef562d623e457bef2a66d1`, decoded counters, both slot payloads and their independent pixel check in the local `pair-irq-r01/bench/live-once` evidence directory. The supervisor joined the worker and delivered the failure alert. The Olimex reservation remains active.

### Why the first row pair reported 639 words — offline review

The P4 fixture read 639 from the documented DMA completion field. Its descriptors also contained a burst-length encoding error. The frozen evidence establishes both facts. It cannot establish that the DSI bridge accepted 639 words or that the encoding error caused exactly three excess words. Smith reported that the Extender screen was completely black after the fault. The fixture disabled live DMA and bridge pixel output on its first failed check, verified the channel stopped, and returned before restoring the reference. This explains the persistent black screen. It supplies no measurement of HDMI sync.

| Quantity on the installed fixture | Value and interpretation |
| --- | --- |
| Required pair payload | 848 pixels × 2 rows × 3 bytes = 5,088 bytes = 636 words of 64 bits, exactly 159 four-word requests |
| Programmed lengths | The bridge reported 636 words per block and 152,640 per frame. The DMA descriptor builder takes 636 and encodes 635 in its separate `BLOCK_TS` field. The bridge controls block termination in this configuration. |
| Completed descriptor | `STATUS_LO=0x0000027f`. Bits 21–0 encode the previous block’s completed count in source-width units according to the P4 manual. The pinned SDK accessor reads exactly this field. `STATUS_HI=0x40000000` shows block complete and zero words remaining in the DMA channel FIFO. Both endpoints use 64-bit words. Neither the length encoding nor the FIFO residue explains an apparent +3. |
| Burst sizes | The bridge requested four words and the descriptor specifies four items per handshake. In the captured `CTL_HI=0x04048240`, ARLEN and AWLEN are both enabled with raw value 4. These AXI fields encode beats minus one, so the bus permits five beats. IDF 5.5.5 copies the supplied value directly into each field. |
| Independent evidence | The USB pixel dump covers the two primed source buffers. The bridge exposes a FIFO depth, which can change as the display drains. The capture has no count of accepted destination writes at the pair boundary. The host handoff test writes 636 into its simulated completion register, so it cannot validate silicon count semantics. |

**Smallest correction for review.** Change only the standalone fixture’s source and destination AXI burst limits from raw 4 to raw 3. The four-word handshakes, 636-word pair and strict completion check stay as specified. The two corrected fields should decode to 3 with both enables set (first completed pair control-high `0x040381c0`, all other captured bits equal). A burst limit permits shorter actual bus transfers, so the configuration error alone cannot predict 639.

**Verification on a later approved run.** Capture the completed reference descriptor once while the existing reference channel is stopped, before switching to bridge-controlled flow. The full-frame reference transfers 152,640 known words. Save its programmed size, raw completion count and DONE/VALID bits. This calibrates the counter on the same silicon without adding a transfer or any work to live refills. Compare the first live completion with 636, then apply the existing pair, frame, timing and pixel gates. A repeat mismatch still fails the fixture. Determining how many words actually reached the bridge in that case needs an independent destination-side observation. The historical capture cannot provide it.

[Installed fixture source](https://github.com/bgates747/agon-extender/blob/e4b97005120d48723db020f0ca9ebdd1992ee629/vdp/hdmi-timing-test/pair/pair_runtime.inc#L291) · [P4 revision 1.3 manual, §§5.5.3–5.5.5, registers 5.10 and 5.27–28](https://documentation.espressif.com/esp32-p4-chip-revision-v1.3_technical_reference_manual_en.pdf) · [Pinned IDF DMA setters](https://github.com/espressif/esp-idf/blob/v5.5.5/components/hal/esp32p4/include/hal/dw_gdma_ll.h#L1127-L1144) · [Upstream DesignWare driver correction for these AXI fields](https://github.com/torvalds/linux/commit/0d59891c42e11c3840276d8a632dbc355d6ddc4f)

### Approved plan freeze — pair IRQ fixture r02

Smith authorized one live invocation on the reserved Olimex bench. Starting from fixture source `e4b97005`, encode the source and destination four-beat AXI limits as raw 3. Keep the bridge request and handshake at four words, with exactly 636 completed words required per pair. During the existing transition from the full-frame reference, the P4 will retain the stopped reference descriptor’s programmed size, completed count and ownership/completion flags. Report that snapshot outside the interrupt. The calibration consumes no additional transfer.

The Pi will verify the descriptor configuration and frozen reference capture offline, build the standalone app, flash only the P4 app0 extent and compare a fresh full-extent readback. It will establish reference readiness, issue `live` once, and preserve the unedited serial response. Report the reference count, verified live retirement count, IRQ publications and worst callback-entry-to-VALID time against 64.4 µs. A run that stops before a refill publishes supplies no refill time. Retain the first failure and the bench reservation.
