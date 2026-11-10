# NET-008 — Short wire captures to locate high-baud byte loss

Smith authorizes short, direction-separated modem tests with the already wired
logic analyzer. The purpose is to distinguish actual UART wire loss from loss
inside the ESP8266/TCP path. Freeze and push this contract before implementation
and physical execution. Prior results and failed streams remain historical.

## Selected work

1. Extender prepares a finite host runner and, only if needed, a separately
   identified diagnostic appliance continuation for one-direction transfers.
   Reuse the corrected P4 UART service settings and existing deterministic frame,
   sequence, payload and CRC oracles. No pacing introduced to make rates pass.
2. Pi5 receives P4-origin data through the real ESP8266 while the analyzer
   records P4 TX → ESP8266 RX. Then Pi5 sends the deterministic stream through
   the ESP8266 while the analyzer records ESP8266 TX → P4 RX. Endpoint records
   identify direction, baud, nonce, frame counts and terminal/cleanup results.
   One direction means the other sends protocol control only, not a second
   concurrent bulk producer. It is a diagnostic workload, not a duplex rerating.
3. Use the existing two UART probe wires only; do not acquire or reconfigure
   other probes. Bind exact channel mapping from the current ignored wiring
   record, not color assumptions. Acquire both UART lines when useful to
   distinguish modem control from payload. No capture during credential setup.
4. First validate capture/decoder completeness at the known-good384000baud,
   then short576000 and1152000baud arms, each at most3seconds bulk production.
   Arm acquisition before the transfer's first byte; use at most12seconds at
   24MHz per arm initially, with measured file-size/sample-count checks and a
   maximum six captures total. Stop if capture cannot cover the relevant data;
   do not infer receiver loss from an incomplete/incorrectly decoded trace.
   No minute-long waveform acquisition is selected.
5. Compare decoded physical UART bytes against deterministic expected bytes and
   actual endpoint captures, including the first mismatch and byte offsets.
   Separate UART decode/framing uncertainty from endpoint CRC errors. If P4's
   correct stream is on the wire but missing at Pi5, localize loss downstream of
   that probe; do not claim ESP8266 silicon alone is proved responsible. If wire
   bytes differ, investigate the transmitter/electrical/decoder boundary.
6. Each selected arm executes once. A fault is retained, not silently retried.
   A deliberate next arm requires known command mode/baud and retired/joined
   prior actors. Failure to establish that state stops dispatch. No blind baud
   probing, persistent AT settings, ESP8266 reflash, wiring change, or eZ80 UART1
   test is part of this contract. A newly identified corrective change gets its
   own traceable continuation before retesting; no original failure relabelling.
7. Prepare and verify host controls before normal fresh scheduler booking.
   Scheduler owns grant-first admission and queue mutations; Extender operates
   only after actual joined sole handoff. Fresh whole ceiling3600seconds:
   admission180, install360, direction/capture/analysis operations2100,
   restore/fresh handback720, margin240. Each transfer has a finite terminal
   bound; notify Smith promptly on an unexpected fault or blocked recovery.
8. Reuse the retained corrected P4 candidate when possible. App-only installation
   preserves bootloader, partition tables, NVS, EMOS, native VDP and startup;
   independently verify written bytes and bind the rounded changed-prefix span.
   Restore the retained current normal P4 product, independently verify the
   changed prefix, obtain fresh physical/process handback and ask scheduler for
   normal release before extended offline analysis. This creates no indefinite
   hold and revives no historical lease. No test autorun or SD startup change.

## Deliverables and limits

1. Identified runner/appliance source and meaningful direction/decoder controls.
2. Actual sample rate, duration, acquired channels, sample counts, raw hashes,
   decoder settings, UART bytes and endpoint results for each executed arm.
3. First divergence comparison and explicit unresolved localization limits.
4. Actual joined actors, restored product identity and normal scheduler release.

The prior384000duplexminute remains the highest qualified external operating
point. P4's internal1152000minute is a peripheral control only. A short directed
capture neither establishes a new full-minute rate nor qualifies the eZ80.
