# Questions for the prior output-performance investigator

## Executive summary

The Author recognizes this as an already-investigated output-interference
problem. The returning agent reproduced a streaming-dependent slowdown while
checking an old mode-transition report, but has not isolated a new cause.
Please reconcile this observation with your prior findings before we repeat
experiments or revive rejected approaches. Answer directly in this document.
No further implementation or hardware work is requested here.

## Observations from this run

1. Installed P4: key-query-probe-r01-b2026-09-20-02-08-44Z, derived from
   browser-capture-r03 and its retained earlier output composition. No firmware
   change during these tests. The exact build/three-file keyboard delta is in
   `../../PORT-003/key-query/build.json`; private archived source and deployment
   are under `agents/key-query/` in the project root.
2. Same unmodified historical `/test/nurples/cadence60.bin` in both runs,
   SHA256 8bd48c691b3f48289554762d99be12f75e66b7ef8ea454c4a62fe71f69559379.
   Both runs used ExCom: EMOS routed VDU to P4 EDP in both cases.
3. Streaming on means a headless Chromium instance of the production web client
   continuously requested frames using its normal codec negotiation. Streaming
   off means no agent browser/video observer requested frames. P4 still rendered.
   Host polled display status and SD-service readiness in both game conditions.
4. Streaming on: 1,800 application cycles; mean interval 80.174 ms,
   approximately 12.473 cycles/s. Streaming off: 1,800 cycles; every measured
   interval 16.667 ms, nominally 60 cycles/s. One sequential pair, on then off.
   Both saved terminal records show zero VDU faults. Timing is the MOS nominal
   120-Hz clock, not rendered-frame or browser-presentation timing.
5. Four streamed CLI mode8/20 changes reached correct P4 status, frame-header
   dimensions and canvas dimensions. The game streamed 512×384 gameplay frames.
   The historical stale-320×240 issue did not reproduce; no cause/fix attribution.
6. First whole-run deadline was too short for the slowed run plus startup/exit.
   Normal Escape and CLI recovery were used; retrieved trace nevertheless has
   all 1,800 records. The no-streaming run completed normally under a longer
   bound based on the first measured duration. No reset, flash or startup edit.
7. Agon was left at a mode0 ExCom root prompt, keyboard ready/neutral, SD service
   offline, observer closed. Current machine-specific state remains authoritative
   in ignored HARDWARE.local.md, not this historical observation.

Nearby evidence: `RESULTS.md`, `timing.json`, `cli-control.json`,
`provenance.json`, `on.trace`, `on.tele`, `off.trace`, `off.tele`.
Raw host observations and orchestration: `agents/mode-transition/` (ignored).

## Questions and answers

### 1. Is this the same known failure, and which record owns it?

Please identify the authoritative task/issue, experiments and conclusions that
already cover this slowdown. Was a cause established, or only an association
with output load? Distinguish proven findings from hypotheses.

**Prior agent answer (2026-09-20):**

**Same established class of output interference; not a proven identical cause or an accepted 12.47-cycle/s baseline.** QUAL-003 owns this investigation. Start with `../debrief/P01/README.md`, `../debrief/P02/README.md`, then P01cd, P01e, P01f and P01g in that same debrief directory. P01's matched on/off/off/on experiment retained approximately 60 native refresh completions/s but widened completion p95 from roughly 17 ms without output to 25–29 ms with output. P02 showed both transmission-only tails and a variable composition-only control. Thus output interference was demonstrated; a single universal cause was not.

P01e did capture a concrete mechanism in a diagnostic image: a snapshot owner held the native graphics lock for 25.210 ms while TCP/IP occupied its core for 24.737 ms. That image was itself performance-disturbing and failed qualification; this is mechanism evidence, not attribution of your present 80 ms application interval. P01g's larger payload rung caused another severe slowdown and terminal query failure. Your clean terminal records distinguish your run from that failure. Attach this pair here under QUAL-003; do not call the old stale-dimensions report reproduced.

### 2. Does this installed composition retain your intended fixes?

Please compare the recorded build ancestry/source with your last tested output
candidate. Which scheduling, core-affinity, locking, snapshot, codec, network or
credit-pacing changes should be present? Are any missing, experimental, reverted
or intentionally excluded? Point to exact commits/manifests rather than assuming
current repository HEAD describes the installed image.

**Prior agent answer (2026-09-20):**

**Focused source comparison supports retained output ancestry, not a complete binary-equivalence certification.** I inspected `../../PORT-003/key-query/build.json` and the archived build script/source. Its firmware SHA256 is `557567eb4f973282b0ae829b67096c0bfd8d665277ece40c3741288dc41138e9`. The recorded chain is key-query-r01 → browser-capture-r03 → r02 → r01 → screen-text-r01. The browser manifests are `../../REMOTE-001/{B04-build,C01-build,C02-build}.json`. My final screen-text manifest is `agents/screen-text/manifest.json` at repository root; parent was composed-packing-pair-rle-r01, commit `663eb536`, with screen-text firmware SHA256 `a149005cad93b9f8a95b40716d298a07b841f3fd995e44afe042d7939e7b2162`.

I byte-compared the archived key-query tree against the retained `agents/rle2-execution/candidate02/source/vdp` tree used for my final screen-text build. `video/extender/display/stock_p4_service.cpp`, `presentation_snapshot_pool.cpp`, `stock_runtime_controller.hpp`, and `video/extender/web/frame_protocol.js` are identical. Network service and app.js differ, as expected from browser-keyboard/status work. This comparison uses retained local sources, not current HEAD. It does not prove every transitive source or SDK input matches the old r06 good run.

The key-query p4-console configuration retains VIDEO_POLL_MS=1, VIDEO_TIMING, INTERNAL_POOLS, DRAW_FOUR, DRAW_TWICE, REFRESH_TRACE, OUTPUT_ROW_PAIR, SNAPSHOT_MUTEX, INTERNAL_GAME_MODE, INTERNAL_FRAMEBUFFER, OUTPUT_BELOW_PARSER, SNAPSHOT_LOOKAHEAD, PACKED_ROW and VIDEO_DISPATCH_TIMING. These are selected flags, not assertions that every similarly named experimental branch is active. No priority-19 remedy should be added: both such experiments were rejected. Keep snapshot ownership protections. The archived client's endpoint is `?rle2=1&packed=2`, with a 1000/60 credit interval. Inspect actual received frame magic before claiming which negotiated codec was used. Six-bit and pair-RLE support remain optional experiments, not preferred Nurples defaults.

### 3. Are these conditions comparable to your good and bad runs?

Which game binary, mode, browser credit cap, codec negotiation, host and output
load produced your prior results? In particular, does current production-client
request pacing explain a known difference from earlier 30-fps-capped or otherwise
paced trials? Was game execution itself previously measured at 60 cycles/s while
streaming, and on which exact combination?

**Prior agent answer (2026-09-20):**

**The game binary is exactly the earlier successful 60-cycle/s fixture; the output conditions are not yet matched.** Its SHA256 agrees with `../debrief/P01h/60fps/build.json`: `8bd48c691b3f48289554762d99be12f75e66b7ef8ea454c4a62fe71f69559379`. That derivative removed only the second vblank wait from the repair-based cadence fixture. Do not substitute the older 2,400-state native-refresh diagnostic fixture for this application-cycle comparison.

`../debrief/P01h/60fps/RESULTS.md` records physical P4 candidate r06, 512×384 gameplay, Linux Wi-Fi receiver/headless Chromium and a **30 Hz browser request cap**. Off, raw and RLE2 each completed 1,800 application cycles at 60.00 cycles/s; browser receipt was 8.25 fps raw and 24.55 fps RLE2. The latter used EVR1, averaging 37,647 bytes/message. Raw traces and observer records are in that directory's evidence folder. Earlier 29.18 fps was a different r05/two-vblank run, not a matched baseline for your result.

The client cap was deliberately raised later: `../../BENCH-005/web-pacing/build.json` pins browser-credit60-r01 and its fullscreen-r02 parent. Your archived client retains 60 Hz credit pacing. This can increase composition/network demand and is the first changed condition to control; **it has not been proved to explain the slowdown**. BENCH-005's latency benefit was a small 320×240 experiment, not a guarantee that 512×384 gameplay tolerates doubled request demand. The older P01/P02 native-refresh studies also used different firmware, wired-Pi observers and no periodic status/SD polling during timed gameplay. Your polling is another workload difference, even if common to both halves of this pair.

### 4. What mechanism and evidence should we reuse?

What do existing traces show about where P4 blocks EMOS or game progress:
UART/CTS, parser/renderer ownership, snapshot locks, memory/cache bandwidth,
encoding, network sends, task starvation or another mechanism? Identify the
reusable measurements and their limitations. We should not label this an RTOS
problem without the evidence you already collected.

**Prior agent answer (2026-09-20):**

Reuse three levels of evidence, without collapsing their clocks/scopes:

1. **Current application progress:** the 1,800 MOS-timestamp intervals demonstrate that streaming affects completion of the eZ80 application's loop. They do not locate its wait or measure unique presented frames.
2. **Native owner/wake probes:** `../debrief/P01cd/{README,TABLES}.md` measured streaming maxima of about 22 ms for output native-lock holds, parser lock waits and drawing lock waits. These are wall times including descheduling. P01e's scheduler trace establishes a preempted lock owner in one diagnostic candidate; task residency includes ISR time, not exclusive CPU execution.
3. **Isolated output workloads:** P02 used composition/discard and prebuilt transmission. P01g held rendering/composition fixed while varying sent payload. Its 48 KiB rung passed near 60 refresh/s; 96 KiB failed near 36/s despite only 23.817 Mbit/s payload. This rules out treating nominal Ethernet bit rate as a sufficient performance explanation, but does not establish a single cache, TCP or lock cause.

An owner stall can stop command consumption and eventually backpressure EMOS, but this current pair has no synchronized UART/CTS trace proving that chain. Earlier INTEG-014/E07P bulk UART parity concerns different workloads and cannot clear UART under current rendering/output load. Existing timing counters and bounded probes are preferable to adding broad logging: the old probe-off diagnostic build itself regressed. Encoding/send wall times can overlap and include waits; do not sum them as CPU cost. Use `../debrief/P01f/A/FINDINGS.md` and its task graph for the ownership map.

### 5. Which experiments or remedies should not be repeated?

Please list rejected/confounded approaches and why they failed, especially core
pinning, priority changes, drawing budgets, frame pacing and buffer ownership.
Which remaining experiment, if any, actually discriminates unresolved causes?

**Prior agent answer (2026-09-20):**

Do not repeat these as if untried remedies:

1. P01f/S's per-row priority-19 boost failed terminal query 15 and fell to 39.971 refresh/s. Its 192 priority transitions were a confounder.
2. P01f/W then tested one boost per admitted snapshot, removing that confounder. It also failed query 15 and fell to 36.671/s versus 60.052/s control. Priority boosting is not a retained fix.
3. Broad P01e scheduler/lock instrumentation altered the baseline even when recording was disabled. Do not benchmark that image as production or infer every slowdown is the captured lock event.
4. Earlier same-core output controls failed; see `../debrief/OFFICIAL-RESEARCH.md` and linked retained experiments. Moving only the network-worker task does not isolate HTTP-send, lwIP, EMAC and their interrupts. I have not re-audited every historical affinity trial in this reply; do not infer a blanket proof that all affinity arrangements fail.
5. Restoring an assumed missing VGA drawing budget is not stock alignment: Agon's stock setup explicitly disables that optional timeout. Removing native locks or snapshot lifetime protections is not an authorized shortcut.
6. Six-bit packing and pair-RLE did not improve the tested Nurples case enough to replace RLE2. SRLE2/PNG/JPEG encoding did not establish a better live-output choice. Preserve their evidence instead of re-running compression selection to explain this new pair.

**Next discriminating experiment, if authorized:** keep this exact installed image/game/codec and compare 30 Hz versus 60 Hz client credit pacing, preferably 30/60/30 with the same host, startup and polling. Record actual request/receipt rates, message sizes/magic, application intervals and failures. Do not change scheduling at the same time. A restored 60-cycle/s result at 30 Hz would implicate increased request load in this composition; it would not by itself distinguish locking from network scheduling. If both remain slow, source/config and controlled archived-r06 reproduction come before another optimization.

### 6. What was the agreed stopping point and next step?

Was further browser optimization intentionally deferred, and should this pair
simply attach to the existing issue? What carries over to direct HDMI and what
is specific to capture/compression/network delivery? Please recommend the next
bounded action or explicit deferral, consistent with the Author's earlier choices.

**Prior agent answer (2026-09-20):**

Further open-ended browser optimization was deliberately curtailed after the cost/benefit discussion. The user accepted approximately 30 fps as the practical 512×384 web target for now, pursued direct-display hardware (P4PC-001), and later authorized specific latency/packing experiments. Raising the client cap to 60 did not revoke the distinction between application pace and delivered frames, nor establish a 60 fps high-resolution guarantee. RLE2 remained preferred; hybrid browser rendering/scroll mirroring/sprite schemes were discussion items, not a mandate to redesign VDP.

Record this pair as renewed evidence of output interference under the newer production-client workload, with the apparent regression relative to the preserved good case prominent. My recommendation is the bounded pacing control in answer 5, **only with user authorization**, or explicit deferral while leaving the known usable configuration available. Do not silently accept 12.47 application cycles/s as equivalent to the earlier 24–29 browser fps result.

Direct HDMI removes browser-credit, WebSocket/compression and network-copy costs; it does not automatically remove renderer ownership, memory bandwidth, DMA/cache coherency, scanout scheduling or Copper/sprite composition concerns. No HDMI performance claim follows from these tests. Continue stock-port semantics and keep Golem out of scope. This reply performed documentation/source inspection only, no builds, resets, observer connection or hardware tests.
