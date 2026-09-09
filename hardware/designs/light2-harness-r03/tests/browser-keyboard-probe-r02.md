# Browser typing timing — browser-keyboard-probe-r02

Status: candidate after automated instrumentation checks. Version preapproval applies; EMOS and
BTYPE remain the previously installed candidates. This is the measurement
increment in REMOTE-001 I001/I002, not a typing-latency repair or qualification.

## Article and boundaries

1. P4: identified browser-keyboard-probe-r02 build, 1152000/8N1, existing r03
   UART wiring and flow control. No timeout, snapshot cadence or wire packet
   changes. P4/browser HTTP query metadata identifies diagnostic sessions.
2. EMOS: installed v0.1.9 candidate. BTYPE and EMBOOT remain the identified
   r01 SD sample and matching boot smoke. Record their hashes with evidence;
   do not rename existing executables to imply they were rebuilt.
3. Autoexec remains mode selection (`VDU 22 3`), EMBOOT, BTYPE, then
   `EMOS KEYINPUT`. BTYPE runs for five minutes or until Escape. No flash
   command is present. The existing hardware keyboard constraint applies.
4. The operator uses the P4 page with `?timing=on`. P4 and browser retain
   bounded timing records; UART reception/echo and rendered pixels remain the
   existing functional path. An `off` comparison disables P4 recording but
   retains browser records. No diagnostic requests run during typing.

## Operator observation

1. Insert the verified SD in Agon and press/release its reset button. Leave
   both boards powered and the ribbons seated. Wait for the sample banner.
2. Open the bench browser address from the local record with `?timing=on`.
   Reload an old page to load this build's assets. Click Connect, then Capture
   keyboard. The first Connect clears/enables P4 records once for this page;
   subsequent reconnects preserve them. Use only one diagnostic browser page.
3. Type `abcdefg`, leaving about a second between characters. Then try normal
   typing, Enter and Backspace, and leave the page idle for one or two minutes.
   Note any visible delay, keyboard release or video disconnection. Keep the
   initial isolated keys distinct from the later editing sequence.
4. If a connection closes, reconnect/recapture on the same page and try another
   character. Do not reload the page before saving its records. Distinguish
   the sample's five-minute exit from a network failure.
5. Click **Finish and download timing records**. This intentionally releases
   keyboard/video and retrieves the P4 records after observation. Retain the
   JSON download even if P4 retrieval fails; browser evidence is still saved.
   Tell the agent where the download is. The agent then analyzes it with
   `scripts/analyze_browser_timing.py`. Do not press Escape until the timing
   observation is complete; report any deliberate Escape/MOS return separately.
6. If overhead comparison is needed, after saving the first result, reset Agon,
   reload the page with `?timing=off`, and repeat the same isolated input. This
   is a separately identified observation, not part of the first run. Do not
   infer negligible P4 overhead solely from host timing or the recorder's
   internal cost counters.

## Meaning and limits

Browser timestamps are monotonic milliseconds; P4 timestamps are monotonic
microseconds. Never subtract across them. Browser key acknowledgement measures
P4 admission, not EMOS receipt. P4 UART submit is a driver call boundary;
`uart_done_observed` is a later software observation, not an exact final-bit
measurement. Browser `frame_submitted` records WebGL submission in an animation
callback, not physical monitor scanout.

The snapshot pool currently limits browser publication to one snapshot per
200000 microseconds. EVF's 16667-microsecond period describes the logical frame
service, not the rate of browser updates. Instrumentation preserves this policy.
A snapshot whose composition begins after drawing-flush completion and finishes
before the next drawing command is guaranteed to include the isolated echoed
character. The first such presented frame gives a conservative visible-latency
bound; earlier snapshots may already include it. Ambiguous or missing matches
are excluded, not treated as zero latency or a transport failure.

P4 and browser rings each retain 8192 records with explicit overwrite counts.
P4 records are allocated in PSRAM before measurement; failed allocation is
reported and timing setup fails visibly. Export freezes the P4 recorder without
stopping application traffic. Do not measure the export itself or reset/reload
before retaining evidence. No hot-path serial printing or diagnostic polling is
added. Cost counters measure recorder locking/clock/storage overhead, not all
instrumentation effects. Event records contain the test's key values.

Relevant source checkpoints: `browser_trace.hpp`, `browser_typing_hardware.inc`,
`browser_keyboard.hpp`, `presentation_snapshot_pool.cpp`,
`wired_network_service.cpp` and browser `app.js` under `vdp/video/extender/`.
The analysis program documents correlation rules. Owner-revocation reason codes:
1 readiness withdrawn, 2 takeover, 3 two-second lease expiry, 4 socket close or
explicit release, 5 invalid event or queue overflow. Socket file descriptors may
be reused; consult open/close records and explicit browser session IDs.

Retain exact build/source identity, SD hashes, operator observations, raw JSON
and analysis together beside this design's tests. Keep machine-private details
in ignored local evidence. Stop after findings and a proposed bounded repair;
this procedure does not authorize silently changing timeout or display policy.
