# INPUT-002 — Deterministic controller traffic and latency attribution

The controller now works, but the Author observes excessive delay. A repeatable
Oryx packet source will let us measure host scheduling and P4 acknowledgement
separately from EMOS delivery, application polling and visible drawing. Clock
alignment must report its uncertainty before we use cross-processor timestamps
as one-way latency measurements.

## State and authorization

On 2026-10-26 the Author authorized a small Oryx background application generating
deterministic timed packets, followed by the largest useful unattended tranche
of the proposed latency investigation. The Author required this task and a
commit/push before implementation. This task extends [INPUT-001](INPUT-001.md);
it does not replace that task's transport, admission or acceptance contract.

The controller viewer was reported working by the Author after the corrected
installation. The Author subsequently approved r14's scheduling comparison.
That bounded comparison passed and the bench was released. No calibrated
end-to-end latency result exists; future bench work still needs fresh ownership
and state checks.

## Scope and ownership

1. The Oryx Python source generates repeatable axis trajectories and optional
   ordered button transitions through the existing host-to-P4 controller UDP
   protocol. It does not synthesize Linux input events or require the F310.
2. The Oryx source records monotonic intended deadlines, actual sends, datagram
   identities and ACK receipt times. The Pi coordinates bounded campaigns and
   retains provenance, start/end duration, completion and failure results.
3. The P4 receiver admits one source through its existing HTTP interface, stores
   latest axes and ordered transitions, and acknowledges reception. Existing
   ACKs prove P4 storage, not EMOS consumption or visible output.
4. Extender MOS continues to own processor transport and application access.
   The eZ80 application uses the supported gateway, never raw UART/register
   access. Mainboard VDP and normal startup remain unchanged.
5. The investigation distinguishes Oryx scheduling, network/P4 acknowledgement,
   P4-to-EMOS delivery, application sampling and presentation. It reports
   non-comparable scopes separately, including rates versus latency.

## Bounded research précis

1. [LAN controller contract](../protocols/controller-lan.md) and
   `scripts/controller_udp.py` own the admitted sender and packet codec. Existing
   STATE/ACK datagram sequences permit host round-trip correlation. Existing
   ACKs contain no P4 timestamp, so they cannot establish clock offset or
   one-way Oryx-to-P4 latency. An HTTP status observation is not a packet-arrival
   timestamp.
2. [EMOS controller contract](../protocols/controller-emos.md) and
   `tests/fixtures/controller/` own the gateway/viewer. The viewer requests at
   most every two raw MOS clock units and redraws every six: nominally 60 and
   20 Hz in mode 20. A 20 Hz redraw can add up to 50 ms before visible output.
   Source inspection and measurements must distinguish that from transport lag.
3. P4 receiver implementation is under `vdp/video/extender/input/controller/`.
   The exact installed composition is identified in the ignored bench record;
   compare it with maintained source before attributing behavior to installed
   firmware. Inspect task/socket scheduling and cache age at each boundary.
4. Consult official `../../agon-docs` before eZ80 API/timer changes, then
   read-only `../../agon-mos` or `../../agon-vdp` where implementation matters.
   [Game timing](../testing/game-timing.md) and
   [render timing](../testing/render-load.md) retain PRT1 ownership and wrap
   constraints. The nominal MOS clock is not a fine timestamp: it advances
   two units per physical VBlank, not once every 1/120 second independently.
5. Clock alignment follows the four-timestamp exchange described by
   [RFC 5905](https://www.rfc-editor.org/rfc/rfc5905.html). Fit monotonic offset
   and drift without setting any participant's clock. Report timer resolution,
   responder processing, residual round trip, path-asymmetry bounds and drift
   uncertainty. P4's [ESP timer](https://docs.espressif.com/projects/esp-idf/en/latest/esp32p4/api-reference/system/esp_timer.html)
   has microsecond resolution; that is not microsecond synchronization accuracy.
   Chaining Oryx–P4 and P4–eZ80 mappings adds uncertainty.

## Work items and validation

1. Implement a finite, explicitly invoked Oryx source with a deterministic
   schedule. Skip missed slots instead of sending catch-up bursts. Default to
   axes-only traffic so an idle EMOS consumer cannot fill the P4 edge queue.
   Expose rate, duration, pattern and timeout explicitly; preserve the admitted
   source's exclusivity and fail on rejected admission or stale ACKs.
2. Reuse the existing packet codec. Record sequence/deadline/send/ACK events,
   missed deadlines, source state and effective cadence. Reject impossible or
   mismatched ACKs. Handle signals with bounded shutdown and explicit close;
   never automatically reconnect, restart or take over another source.
3. Add proportionate deterministic tests for pattern repeatability, missed-slot
   behavior, admission/fault/timeout handling and ACK correlation. Exercise a
   local UDP/HTTP receiver for transport semantics and timing plumbing. Do not
   label the local receiver as physical P4 evidence.
4. Deploy a fingerprinted source package to Oryx without replacing the physical
   sender or user input services. Run finite host-only/loopback measurements,
   retain logs and summarize median, p95 and worst timing in milliseconds.
   Write a reproducible background launch/stop recipe; no boot service/autostart.
5. Review the exact installed receiver/viewer sources and identify measurable
   scheduling limits. After exclusive bench availability is established,
   compare the same deterministic traffic at selected rates against existing
   P4 firmware, restoring source ownership afterward. Do not reset, flash or
   run an Agon application merely to obtain these host/P4 ACK measurements.
6. Implement and test offline clock-fit/uncertainty analysis where useful.
   Specify the smallest timestamp probes needed for the remaining processor
   boundaries. Existing packet formats must not be silently extended. EMOS
   has only 270 resident ROM bytes free in the latest installed build; prefer
   bounded application-owned diagnostics over resident growth. Firmware/API
   changes require a concrete reviewed design and identified candidate before
   deployment; no new deployed version is inferred from this task.
7. Update this task, current controller guidance and the dated development log
   with findings, exact source identities, test scopes, retained evidence and
   remaining gates. Keep raw machine endpoints and device identities ignored.

## Decisions and execution boundaries

| ID | Decision | State / reason |
|---|---|---|
| I2-D01 | Reuse admitted UDP controller traffic; start axes-only | Selected implementation choice; isolates latency without unconsumed button overflow |
| I2-D02 | Use monotonic timestamps and report uncertainty; do not set clocks | Selected investigation method; wall-clock synchronization is unnecessary |
| I2-D03 | Finite explicit background runs, no service/autostart or automatic takeover | Selected implementation choice; preserves source and bench ownership |
| I2-D04 | Further timestamp probe layout and eZ80 timebase | Unresolved until installed-source review and initial measurements; propose the smallest justified extension |
| I2-D05 | Compare a priority4 UDP worker as a bounded scheduling control | Author says proceed on2026-10-26 after reviewing the r14 naming request and starvation explanation; approved experimental identity `indexed-hdmi-r14`, build/verified P4-only deployment and finite comparison under existing investigation authority. Preserve eight-packet budget/2ms block and all wire formats |

Follow the [test lifecycle](../procedures/test-appliances.md) and
[execution protocol](../procedures/test-execution.md). Never edit `/autoexec.txt`.
No CRC or substitute software checksum is added to E/VDP–EMOS traffic. Do not
claim end-to-end or photon latency from ACKs. Do not disturb another application's
bench reservation, replace mainboard VDP, silently upgrade selected production,
or leave an indefinite synthetic controller source running after a campaign.

## Results

The task and preceding owned dirt were committed/pushed before implementation
in Extender `b96c8d52` and EMOS `1dafee0`; installed P4 source `27d93dcc` was
also published on its retained branch. The finite source/campaign and offline
clock-bound analyzer are implemented. Forty-one host/core checks pass, with
fourteen new probe/clock checks also passing on Oryx. Local socket controls and
bounded Oryx/Pi-to-P4 campaigns completed; no Agon application was invoked.

[First results](INPUT-002/RESULTS-2026-10-26.md) identify substantial delay/loss
before EMOS. The exact P4 blocking/scheduling point remains unproven. A minimal
priority4 source control is committed against the installed P4 composition.
The canonical indexed-PPA builder requires an approved `indexed-hdmi` revision
even for compilation and refuses the unversioned sentinel. Its build therefore
was initially paused at the version decision. The Author subsequently says
proceed: `indexed-hdmi-r14` is approved for the exact prepared scheduling
comparison. Build/backup/selective P4 installation/independent verification and
finite comparison now proceed; no production selection or downstream timing
claim is implied.

The [r14 comparison](INPUT-002/R14-COMPARISON.md) now passes: same Oryx120Hz
source,3600/3600 ACKs, median1.794ms versus fresh-boot r13's261.703ms (−99.31%).
The60/240Hz cases, independent Pi120Hz case and real keyboard/fast-SD coexistence
also pass. Exact application-only install/full readback and unchanged surrounding
flash sectors are verified. All sources stopped, actual CLI handed back, r14
retained experimentally; no production promotion or Agon visual-latency pass.

Remaining work is EMOS/application/presentation attribution and Author review.
The demonstrated priority correction makes additional P4 stall instrumentation
optional unless a remaining symptom warrants it. Cross-clock timestamp probes
and the eZ80 fine timebase remain separate unresolved preparation decisions.

## Interactive retry — unresolved freeze,2026-10-26

1. The Author invoked the unchanged viewer-r03 after its SD bytes were read
   back exactly. A physical F310 sender was explicitly admitted at120Hz/250ms.
   Initial P4 input was valid, queue empty, with the fast SD listener exited.
   The Author subsequently reported the application frozen and still running.
2. Read-only HTTP and source-log observations retained in ignored
   `agents/input002/viewer-freeze-observation.json` show the sender stopped
   after581.018s:69719 sends,69718 ACKs, final receiver fault4 (transition
   overflow). P4's last stored transition sequence is128. With a128-entry
   queue and contiguous source transitions, this indicates no transitions
   were retired before the next transition overflowed the session. The
   overflow may follow an earlier EMOS/application stall or link failure;
   it does not establish the initial fault or a repeat of the old IRQ defect.
3. P4 instance and keyboard boot epoch stayed unchanged, keyboard status
   remained ready/neutral and scanout advanced with zero reported faults.
   P4 output mode remained0; the active Legacy mainboard display is distinct.
   These observations do not prove the eZ80 foreground or its keyboard path
   is responsive. No input, reset, source restart, flash or SD operation was
   issued against the running viewer during this observation.
4. Remaining diagnosis: establish the visible viewer status and whether Escape
   returns to the CLI, then isolate app loop/rendering, resident request/reply
   progress and UART/keyboard health using the smallest justified probe. Do
   not restart the source or replay the viewer merely to clear its evidence.
5. The Author requests application-owned mode selection for this interactive
   test. Installed viewer-r03 already captures entry mode, conditionally selects
   and verifies mode20, waits for monitor settling and restores entry mode on
   handled exit. Interactive guidance now omits the external VDU preselection,
   which otherwise makes mode20 the captured entry mode. No executable rebuild
   or new firmware identity is needed for that invocation correction.
6. The Author subsequently identifies the visible message as "Waiting for
   controller" and confirms Escape exited the application. This rules out
   an unresponsive foreground in that observation. The installed renderer
   uses the same waiting message before any valid sample and for an invalid
   source received through an otherwise healthy EMOS carrier. Its label alone
   therefore cannot identify absence of replies or an eZ80 stall. Establish
   whether valid controls appeared before loss before attributing the queue
   overflow to a regression; a source that filled before viewer invocation
   also produces a responsive waiting viewer. No source restart or reset has
   followed this clarification.
7. After the old sender was confirmed stopped, the agent explicitly admitted
   a fresh physical F310 source at120Hz/250ms and verified P4 valid/fault0.
   The Author reports the resulting viewer usable: right-stick analog plotting
   works, while the left stick changes the D-pad labels rather than its analog
   marker. This is partial interactive evidence, not a complete handling pass.
   Logitech's F310 quick-start guide describes the front Mode button swapping
   the left analog stick and D-pad in sports mode. That is the leading
   explanation; confirmation by toggling the Mode button remains pending.
   No software remapping, controller setting or firmware change was made.
8. The Author confirms the D-pad and left stick are swapped. This matches
   the documented F310 Mode-button setting; do not compensate with a software
   axis remap. Return to ordinary left-stick analog operation by selecting
   the controller's flight setting. Corrected handling after that physical
   selection has not yet been reported.
9. The Author then confirms the front Mode button restored normal left-stick
   operation. The reported swap was the controller's hardware setting, not a
   demonstrated software axis defect. The Author delegates consumer questions
   to fsim; Extender sent the exact contract/source/build identities, foreground
   polling and expiry constraints, test references and current bench boundary
   through the mailbox. No hardware operation accompanied that handoff.
10. Fsim's proposed asynchronous foreground consumer policy is compatible,
    subject to continued polling while paused and fresh-sample validation after
    explicit close/open rearm. Offline artifact inspection confirms the recorded
    installed mainboard SDK/wireframe image is distinct from fsim's accepted
    flight-compositor image. The consumer owns that renderer dependency and its
    eventual physical gate; no controller-driven firmware replacement was
    authorized or performed. The compatibility answer was sent by mailbox.
11. Extender reviewed fsim's concrete adapter read-only. Wire bytes, gateway
    bindings and static-lifetime storage match. A bounded native reproduction
    shows failed explicit rearm falling back to keyboard flight without a fresh
    neutral controller sample; entry/exit mode changes also lack a fresh query
    confirming the selected mode. Both findings and suggested checks were sent
    through the mailbox for fsim-owned correction. No fsim source, emulator or
    hardware state was changed during review; physical gates remain open.
12. Revised fsim source closes both findings; Extender independently ran the
    updated native controller checks successfully and matched the retained
    target-replay source identity. A new notice-path defect remains: Waiting/
    Lost text is drawn in double-buffered mode after compositor shutdown without
    presenting that page. Extender returned the supported stock-swap remedy and
    requested bounded visible-status replay coverage through the mailbox.
13. Retained actual-application images now show both notices on the presented
    page; the matching source/app manifest and labelled replay receipt verify
    the reviewed identity. All three original concrete findings are closed.
    Extender also noted that failed compositor-stop acknowledgement must remain
    blocked during fsim's existing handled-error work. Final fsim regressions,
    actual controller/flight review and renderer-installation authority remain
    independent; no hardware or emulator operation accompanied this closeout.
14. Fsim's physical handback reports independently verified compositor
    restoration and real-stream neutral flights in both editions:120physics
    ticks/242polls each, maximum service gap2nominal MOS units, no reported
    drops/controller/flight errors. Pause/reset/rearm/exit also pass in a separate
    finite check. Extender inspected the retained restoration/result receipts
    offline and acknowledged the handback. The normal flight app is loaded but
    stopped for Author review. These polling observations do not measure actual
    input latency or close the Author's gameplay/handling gate.
