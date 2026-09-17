# SRLE2 browser decoder and Linux replay tasklet

## Executive summary

Build the browser decoder we intend to retain, and exercise it by sending encoded
bitmap frames directly from Linux. The Linux server substitutes for the P4 frame
producer, while the real browser decoder and presenter remain the code under
test. This provides reusable correctness and browser-cost testing without bench
access; it cannot establish P4 encoding cost or embedded networking performance.

Status: Author approved execution as a one-hour goal; stop on unexpected conditions or questions.
Parent task: P01h, SRLE2 iteration. No new top-level task namespace.

## Authorization and boundaries

The Author requested this tasklet while another agent owns the bench. Linux/browser
work and an emulator attention cue are the proposed independent path. This
supersedes the prior blanket host-test restriction for this tasklet only when
execution proceeds; P4/mainboard flashing, serial access, network connections to
the bench, resets and hardware notifications remain prohibited until release.
The emulator is an attention cue only, not the codec under test. No Golem.

## Itemized work plan

1. [ ] W01 — Pin fixtures and decoder boundary. Reuse SOURCE.json's original szip
   source and the historical CmpS + SZ1.12 wrapper, order3/recordsize1 subset.
   Gather existing generated/owned bitmap fixtures plus deterministic synthetic
   all-colour, solid, stripes, scrolling, sprite-heavy and incompressible scenes.
   Record width, height, stride, format, exact raw bytes, SHA256, seed and source.
   Keep third-party reference footage out of tracked fixtures.
2. [ ] W02 — Freeze browser negotiation and frame envelope before implementation.
   Existing EVF1 raw and EVR1 RLE2 retain their exact meaning. Specify a distinct
   negotiated SRLE2 envelope with encoded and decoded sizes, dimensions, sequence,
   version and maximum lengths. Payload is a complete CmpS-wrapped RLE2 file.
   Define rejection, raw fallback and reconnect behaviour. Initially independent
   full frames, no deltas or inferred transparency. Reuse existing 30Hz credit
   pacing, with deterministic single-frame stepping as a separate harness option.
3. [ ] W03 — Implement a reusable browser decoder module, independent of the
   replay server. Preferred starting point: compile the pinned original C decoder
   to WebAssembly with bounded memory I/O, adapting the P4 allocation shim rather
   than translating the entropy algorithm by hand. Inspect available tooling first;
   document any justified alternative before changing approach. Keep ownership,
   error return and allocation limits explicit. Run decode in a Worker with an
   enforceable deadline; reject malformed streams without freezing the webpage.
   Decode szip to the complete RLE2 file, then use the retained RLE2 decoder and
   existing pixel/palette presenter. Retain original license notices and source.
4. [ ] W04 — Build a loopback-only Linux HTTP/WebSocket replay server. Serve the
   actual candidate web client/modules, answer its negotiation/credit protocol,
   and transmit prerecorded raw/RLE2/SRLE2 messages. Do not implement a separate
   demonstration viewer that later has to be replaced. No board addresses in
   defaults; fail closed on accidental bench endpoints. Provide one documented
   CLI for named corpus, output directory, pace, count and optional browser path.
5. [ ] W05 — Independent correctness controls. Compare browser-decoded bytes to
   the retained uncompressed originals, not merely a same-code round trip. Generate
   golden encoded files with the pinned original Linux szip CLI (-b41o3), checking
   its locally modified decoder's known output-path issue before relying on it.
   Cross-check the P4-adapted codec compiled for host only where feasible; this is
   not a RISC-V execution claim. Check all64 colours, sizes, tiny/stored blocks,
   alpha rules for assets versus opaque composed frames, raw fallback, consecutive
   frames, reconnect and client takeover. Capture exact mismatch coordinates and
   byte hashes; screenshots supplement, never replace, byte comparisons.
6. [ ] W06 — Negative cases and resource limits. Exercise truncation, corrupt
   headers/version/length, invalid sort index/order/record size, oversized output,
   partial messages at the correct transport layer, slow consumers and decode
   timeout. WebSocket messages may span transport fragments; the browser API emits
   complete messages, so do not incorrectly treat TCP fragments as independent
   frames. Preserve last valid frame and recover deliberately after rejection.
7. [ ] W07 — Measure separately: encoded bytes, worker decode ms, RLE2 expansion
   ms, palette conversion/presenter submission ms, receipt cadence and allocation
   high-water where measurable. Warm up and repeat; record browser/build/machine,
   loopback versus network and sample count. Never call loopback throughput a P4
   Ethernet result, nor WebGL submission a physical-monitor refresh measurement.
   Keep raw/RLE2/SRLE2 inputs identical and use tabular comparisons.
8. [ ] W08 — Package reusable protocol, fixtures, runner and results with one-command
   reproduction; retain the same decoder for eventual firmware-hosted web use.
   Start in this task silo, then promote accepted infrastructure to a role-named
   location under the project documentation/testing structure. Add links, not a
   duplicate procedure. Report remaining hardware-only gates and notify via the
   accepted emulator spoken cue. No experimental push.

## Planned reusable run protocol

1. Generate or select a manifest of raw and encoded frame files; verify hashes.
2. Start the loopback server with a unique run ID and durable event log.
3. Launch headless Chromium against that server, using production decoder/presenter
   modules with diagnostic observation hooks; optionally provide a visible viewer.
4. For each case, record request, send, receive, decode, comparison and submission
   outcomes. Save mismatches and bounded timing samples. Enforce an overall test
   deadline and individual worker deadlines; terminate only owned processes.
5. Write results.json plus an executive-summary Markdown table, including wall
   duration and explicit incomplete/failed cases. Exit nonzero on correctness
   failure. A completed suite must not leave a silent hung browser/server.

## Acceptance and later hardware bridge

Acceptance requires exact decoded pixels on all supported valid fixtures, bounded
failure/recovery on negative cases, unchanged raw/RLE2 compatibility and a reusable
browser implementation exercised through the same envelope as future P4 output.
Performance is measured, not prescribed by desktop results. Once bench is released,
reuse the corpus/client against the P4, verify its encoded output and compare
actual P4 codec/network timings. No desktop pass substitutes for that bridge.

## Execution authorization

Author approved W01–W08 with a one-hour wall limit on2026-09-17 UTC. Linux/browser
tests are now authorized; bench remains unavailable. Missing WebAssembly tooling
is an anticipated W03 setup item: install an isolated pinned official SDK locally.
Notify with emulator spoken cue on success or unexpected stop. No hardware actions.

## Unexpected stop

Execution paused at the first W01 golden mismatch; see [RESULTS.md](RESULTS.md).
Compiled P4 candidate is unsuitable for deployment pending the identified output
path correction. Awaiting Author direction; no hardware access or silent fix.
