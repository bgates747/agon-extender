# Counted-point UART/CTS capture

Procedure: **uart-path-capture-r01**. State: prepared; two complete passive acquisition checks pass; physical
workload waveform and returned SD comparison pass. Author authorized W6 on 2026-09-10,
after freezing the 48-row baseline in `c630c86`. Standing identity preapproval
covers this procedure and registry r62.

## Fixed inputs and purpose

1. The Agon runs the existing
   `uart-path-benchmark-r03-b2026-09-10-18-21-38Z` executable, SHA256
   `a4307f487666ede3cb347c9f1e37343c4fae41c1bee53b4e0bb0fc5a7ffb7c1c`.
2. Installed firmware remains
   `agon-emos-v0.1.12-b2026-09-10-03-50-35Z` and
   `uart-excom-console-r07-b2026-09-10-06-31-58Z`; mainboard VDP is 2.16.0.
   The [baseline](hardware-baseline.md) records provenance and limitations.
3. EMOS owns ExCom routing and UART1. The SD application invokes
   `trace count points`: 512 counted writes of 64 bytes, totalling 32,768
   bytes and 4,096 point commands. Neither firmware nor the payload changes.
4. The operator leaves one connected browser video client visible and all
   keyboard keys released. Browser presentation is not the completion boundary.
5. Measure eZ80 TX gaps against P4 RTS/eZ80 CTS permission. The capture can
   separate withheld receiver permission from gaps while permission is granted;
   it cannot assign an exact CPU cost or name the software cause of those gaps.

## Probes and acquisition

| Analyzer physical input / lead | Agon signal | Direction and P4 endpoint |
| --- | --- | --- |
| D1 / yellow | PC0, UART1 TX | eZ80 → P4 GPIO22 RX |
| D6 / gray | PC1, UART1 RX | P4 GPIO12 TX → eZ80 |
| D3 / orange | PC2, UART1 RTS | eZ80 → P4 GPIO23 CTS |
| D4 / purple | PC3, UART1 CTS | P4 GPIO11 RTS → eZ80 |

Keep common ground and the r03 ribbons seated. High on PC3 withholds eZ80
transmit permission; high on PC2 withholds P4 transmit permission. A byte
already in flight can finish after CTS rises.

The Pi acquires **24 MHz, 720,000,000 samples, 30 seconds**, untriggered.
This replaces the broad plan's provisional 12-second window for this selected
case: allow up to five seconds for the operator, two-to-three-second boot,
mode/setup/marker queries, approximately 5.3 seconds measured workload plus
reply, and margin. Acquisition begins before the reset cue. Coverage is checked
from actual bytes, never inferred from nominal duration. If the selected case
extends beyond the window, retain the incomplete capture and revise the
procedure before recapture; do not shorten its payload.

The Pi writes raw one-byte samples during acquisition, then losslessly packs
an SR archive afterward and verifies its extracted SHA256 against the raw
stream before removing the temporary raw copy. Physical channel bits retain
their positions. This avoids archive compression competing with USB servicing.
The [libsigrok 0.5.2 binary output implementation](https://github.com/sigrokproject/libsigrok/blob/libsigrok-0.5.2/src/output/binary.c)
passes the original logic sample bytes unchanged. The generated SR metadata
records the explicit fixed samplerate, channel map and one-byte packing.

## Preparation performed by the agent

1. Read the current ignored bench record. Verify analyzer discovery and Pi
   tools without opening P4 serial, resetting boards or starting a browser.
2. Run the passive acquisition check without an Agon reset. Record its exact
   helper hash, requested/actual extent and archive integrity. This validates
   capture mechanics only; it is not a UART workload run or evidence of speed.
3. Check the synthetic decoder cases and independent sigrok agreement. Verify
   that missing/corrupt payloads, replies and framing errors are rejected.
4. Review the unchanged binary's trace invocation in the isolated raw-FAT
   emulator. Its measured times are not P4 performance evidence.
5. Back up `/autoexec.txt`, verify the deployed binary against the selected
   manifest, and deploy the exact startup below. Preserve every earlier CSV
   and unrelated SD application. Record hashes, then safely unmount the SD.
6. Stage an immutable copy of the capture helper and its preparation record
   under the ignored bench paths. The local launcher checks the helper hash;
   remote commands, identity and paths are supplied through ignored JSON.
7. Only after these preparations finish, give the operator the launcher and
   a notification-only emulator cue. No screenshot is required.

Exact SD startup (mode selection occurs here, never inside the application):

```text
VDU 22 3
LOAD /bin/EMBOOT.BIN
RUN
EMOS KEYINPUT extender
VDU 22 0
EMOS EXCOM --keep-display
VDU 22 0
CD /extender/uartbench
LOAD UPBENCH.BIN
RUN . trace count points
```

## Operator run

1. Insert the prepared SD into Agon. Keep both boards powered and ribbons
   seated. Connect one browser video client and keep it visible.
2. Run the prepared workstation launcher and press Enter when ready. Do not
   reset Agon yet. The launcher arms only the analyzer; the P4 keeps running.
3. When the launcher says **Reset Agon now**, press and release reset once
   within five seconds. It issues that cue only after at least 65,536 sample
   bytes have actually arrived and the analyzer is still running.
4. Leave keys released. Acquisition stops after the requested samples, then
   the Pi packs/checks the archive and the workstation retrieves it. A
   60-second acquisition watchdog handles missing progress; successful runs
   do not wait for it. There is no serial PASS condition or 90-second hold.
5. Wait for the Agon's final result and MOS prompt before removing its SD.
   Return the card for collection of the new CSV. A one-row trace is expected,
   even though the unchanged application's banner says `1/48`.
6. If acquisition fails before the cue, do not reset Agon. If it fails after
   the cue, let Agon finish and return the SD anyway. A bad capture does not
   erase an independently valid CSV result. Do not silently retry a workload.

## Offline analysis and acceptance

The workstation runs `scripts/analyze_trace.py <logic.sr> --output <new-folder>`
using the project virtual environment with numpy and local sigrok-cli.
It records tool versions, script/input hashes, sample counts and decoder logs.

1. Require the selected 24 MHz channel map, one-byte packing, archive CRC and
   exactly 720,000,000 samples for acquisition PASS.
2. Locate exactly one complete marker query `17 00 84 C8 00 90 01`, its
   black-pixel reply, the complete known 32,768-byte payload and final query
   `17 00 84 40 00 18 00`. Require the corresponding white-pixel reply
   `84 04 FF FF FF 0F` and coverage beyond its final stop bit.
3. Decode each UART at 1,152,000 baud, 8N1. Require independent sigrok byte and
   timestamp agreement and no framing warnings inside the measured window.
   Startup/outside-window errors are counted separately.
4. Measure payload wire span, estimated time occupied by bytes, inter-byte
   idle with CTS high and low, longest gaps, marker-reply-to-first-byte delay,
   final query/reply latency and reverse flow-control state. Preserve raw
   intervals and do not subtract presumed fixed software overhead.
5. Validate the returned one-row CSV with `analyze.py`; require the selected
   build/case, mode/pixels, 512 chunks, correct clock arithmetic, successful
   final status and Legacy return. Associate it explicitly with this capture;
   an offline file ordinal is not a guessed UTC start time.
6. Compare clock intervals with wire observations, allowing clock quantization
   and the different software/wire boundaries. CTS-high overlap is evidence
   of P4 backpressure, not an exact eZ80 stall measurement. CTS-low gaps alone
   do not distinguish caller, interrupt or transmitter implementation cost.
7. Retain the full private capture bundle and promote a sanitized comparison
   plus source CSV/hash into task evidence. Report limitations and recommend
   one smallest repair for Author review. W6 does not authorize that repair.

## Preparation observations

Two initial passive checks using sigrok's live SR output stopped after only
42,022,400 and 10,565,632 samples, with exit status zero. No reset cue was issued.
The raw-output path with reduced logging then passed two complete 30-second
checks, each retaining exactly 720,000,000 samples. Both changes were applied
together; this does not isolate compression as the cause or establish future
reliability. [Sanitized preparation evidence](evidence/capture-preparation/checks.json)
records the four attempts and functional checks. Original bundles and helper
revisions remain in the ignored preparation record. Six synthetic tests,
five CSV validation tests and the unchanged executable's one-row emulator
review pass. The SD startup and binary match that review; previous results
are retained. The subsequent actual [benchmark waveform](uart-cts-findings.md) passes
coverage and the returned SD comparison; W6 measurement is complete.
