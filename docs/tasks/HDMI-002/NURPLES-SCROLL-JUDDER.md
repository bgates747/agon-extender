# HDMI02-SIZE01e — Stock-compatible P4 presentation timing, with Nurples as the scrolling reproducer

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
