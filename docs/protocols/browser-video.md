# Browser video

This is the current browser-video encoding and pacing contract. It promotes
the recurring interface from PORT-003 Phase F; the 2026-09-10 Author-requested
RGB222 increment supersedes that phase's RGB888-only wire restriction and
200 ms first-bench snapshot interval. Historical qualification records remain
evidence for their recorded builds.

## Default encoding — accepted 2026-09-19

The accepted browser-video default is **RLE2 compression**, requesting `?rle2=1` in
clients using the current negotiation interface. This is full-frame compression,
not frame differencing. Retain raw compatibility/fallback and explicit test codec
overrides. This decision does not change pacing or expand supported formats.
Client replacements and firmware deployments must preserve and verify this default.
Authority: [ADR-0021](../decisions/ADR-0021-rle2-browser-default.md).

The selected production r55 browser requests `?rle2=1&packed=2`. The earlier
reset-only build accidentally requested raw `/video`; that discrepancy was
corrected in [RELEASE-001](../tasks/RELEASE-001/R01-07.md) and is not the current
selected behavior. The P4 may still select raw fallback when compression is
ineligible or larger. Restoring codec negotiation did not add a pacing limiter.


## Accepted web-output ceiling — 2026-09-16

At512×384, the supported web-output target is **30 complete frames per second**.
Normal fixtures must pace output requests, snapshot admission/composition and
transmission to no more than30fps, using absolute deadlines without catch-up
bursts. Do not compose60 frames/s and discard half after doing the work.
Bound pending output; slower clients must not accumulate an unbounded backlog.

This does not cap native VDP rendering, application physics or display timing:
those may remain60Hz and must be measured separately. Preserve all VDU command
semantics. Thirty web frames/s is the current product contract, not a claim that
all production scenes/browser paths are already qualified at that rate.
Higher-rate output is outside normal acceptance and requires an explicitly
approved stress experiment. The earlier60fps web target is deferred; eventual
256-colour/one-byte-per-pixel support remains a goal.

Authority: [ADR-0020](../decisions/ADR-0020-web-output-30fps.md).

### Implementation and later experiment boundary

| Scope | Authority or observed source behavior |
|---|---|
| Normal policy at 512×384 | ADR-0020 specifies a 30 complete-frame/s ceiling, including output admission; it does not claim implementation |
| Earlier controlled client | BENCH-005 K01 used an explicit 30 credits/s limiter; this describes that historical test |
| Authorized later experiment | BENCH-005 W01–W02 raised the explicit client ceiling to 60/s; this did not replace the policy |
| Selected production r55 | Browser sends the first credit on connection, then returns one after presentation in `requestAnimationFrame`; no explicit 30/60-fps time limiter |
| P4-local SD candidate r57 | Same browser `app.js` bytes as r55; storage qualification did not change pacing |

The selected client follows browser presentation opportunities and one-frame
credit/backpressure. A browser's refresh cadence is not a guaranteed 60-Hz clock,
nor a P4 output-admission ceiling. Network, encoding, rendering and browser load
can each reduce observed presentation rate. Frame-header nominal period, presented
fps and application loop cycles/s are distinct measurements.

Source comparison: selected r55 commit
`b835307270d3f0fac1be01b587e62163cc392dac` and r57 source commit
`1ebef276bd435be44625f046d115fec90503c3c3` share `app.js` SHA-256
`5401574eeabc069b11ba65cd49c46510a6133ef31cdebae446401a1f4aa2fb28`.
The maintained [animation loop](../../vdp/video/extender/web/app.js) calls
`credit.presented(sendCredit)` after presenting; the
[credit state](../../vdp/video/extender/web/frame_protocol.js) sends `frame`
without a rate timer. This is source evidence, not a fresh throughput test.

**Remaining limitation:** the selected ordinary browser path does not enforce
ADR-0020's normal ceiling. Bounded installation acceptance is not evidence that
the ceiling was implemented or replaced. QUAL-003/BENCH-005 retain the policy
versus implementation follow-up (A09-F008); this documentation audit neither
changes the rate nor authorizes a new output policy. The
[cross-agent comparison](../tasks/QUAL-003/mode-transition/AGENT-QUESTIONS.md)
remains historical evidence distinguishing the earlier capped and later trials.

Historical codec/pacing experiments used isolated overlays. The current selected
composition is now maintained and reproducible through the
[build guide](../building.md); do not treat old overlay requirements as the
current build procedure. Verify a specific historical build by its own receipt.

## Ownership and presentation

EDP on P4 interprets VDU commands and composes the complete displayed image,
including palette, Copper, sprites and cursors. The browser decodes final
pixel colours and presents them with WebGL2 nearest-neighbour sampling. It
does not implement VDP rendering semantics. EMOS owns Agon output routing.

The accepted original-controller backend allocates three fixed-capacity PSRAM
snapshot slots of one byte per pixel, up to 1024×768 RGB222 each (2.25 MiB
combined). StockP4Service prepares native scanlines and normalizes directly into
an exclusive mutable RGB222 slot before publication. Network leases never
observe mutable bytes. This is the current stock-backend-r2/r3 implementation;
the earlier generic compositor used an RGB888 intermediate and larger slots.
That older interface remains available to its separate consumers but does not
describe the selected ordinary console's allocation or conversion cost.

## EVF1 wire format

One binary WebSocket message contains this 32-byte header and one complete
frame. Multibyte integers are unsigned little endian.

| Offset | Bytes | Value |
| --- | --- | --- |
| 0 | 4 | ASCII `EVF1` |
| 4 | 1 | Header version 1 |
| 5 | 1 | Header length 32 |
| 6 | 1 | Pixel format: 1 = RGB888, 2 = RGB222 |
| 7 | 1 | Bit 0 full frame; bit 1 presentation boundary; other bits zero |
| 8 | 4 | Low 32 bits of snapshot generation |
| 12 | 2 | Width, 1–1024 |
| 14 | 2 | Height, 1–768 |
| 16 | 4 | Row stride in bytes |
| 20 | 4 | Payload bytes, exactly stride × height |
| 24 | 4 | Logical presentation period in microseconds |
| 28 | 4 | Reserved, zero |

RGB888 uses three bytes per pixel in R, G, B order. RGB222 uses one byte,
`00BBGGRR`: red bits 1:0, green 3:2, blue 5:4. Each component expands to
0, 85, 170 or 255. The P4 emits zero upper bits; the browser ignores those
two bits. No VGA synchronization or alpha bits are transmitted.

The P4 emits tightly packed rows. The browser accepts row padding when the
stride is at least width × bytes per pixel, the exact message length agrees,
and payload is no larger than 2,359,296 bytes. It rejects unknown formats,
unknown header flags, missing full-frame indication, invalid dimensions,
reserved header data, truncation and trailing bytes.

The r06 console producer selects RGB222. The updated browser also accepts
older RGB888 frames. Earlier browser code rejects RGB222; reload the page
from the updated P4 after deployment. Assets are served with `Cache-Control:
no-store`. The header layout and version stay unchanged; pixel format 2 is
an explicit new encoding, not a reinterpretation of format 1.

At 640×480, RGB222 payload is 307,200 bytes rather than 921,600; either has
the same 32-byte header. Packing is lossless for the existing P4 compositor's
64-colour output, including its already-quantized overlays.

## Pacing and bounded delivery

P4 snapshots are admitted by browser demand and may be produced at each logical
frame boundary. The active console has no fixed 200 ms interval. A consumer
request with no fresh snapshot schedules composition; repeated polls while that
composition is in progress wait for the same frame without scheduling another.
After cancellation, a later poll may request a new attempt; an idle or stalled browser
does not cause continuous full-surface work. The frame service still progresses
without requests. Logical frame timing and VDU execution do not
wait for browser presentation or a socket send.

PORT-006 transports opaque bytes for one video client. The browser sends the
exact text `frame` to grant one credit, validates and presents the returned
frame in its animation loop, then grants the next credit. One snapshot may
be leased for sending; unsent generations collapse to the latest. Duplicate
credits are errors. Pool pressure skips a snapshot instead of growing a queue
or blocking drawing. Existing complete-send and disconnect containment apply.

The browser's “Presented fps” is measured from local presentation calls over
at least one second; it is not P4 rendering speed, monitor scanout timing or
end-to-end latency. The “Period” field remains logical VDP time. Sequence gaps
can reflect deliberately skipped intermediate snapshots rather than packet loss.
Actual throughput and sustained stability require hardware qualification.

## Viewer ownership and errors

The P4 service admits one video viewer. A new successful WebSocket handshake
replaces the old viewer, closing its socket with code 1000 and reason
`Viewer replaced`; old credits and leases do not transfer to the new client.
The old page stays open and requires an explicit Connect to reclaim video.
Video ownership is distinct from keyboard capture ownership.

Malformed frame/credit handling uses protocol error 1002. A refused busy
admission uses 1013; browser presentation failure uses 1011. A disconnected
socket must not be treated as an acknowledged presentation. Static page assets
close their HTTP connections after sending, freeing slots for viewer admission.
The service is for a trusted LAN; it provides neither TLS nor authentication.
Source ownership: [P4 network service](../../vdp/video/extender/network/wired_network_service.cpp)
and [browser client](../../vdp/video/extender/web/app.js), with the candidate
codecs/pacing boundary described above.

## Negotiated complete-frame encodings

The deployed candidate family adds the formats below to the original EVF1
contract. This section promotes recurring wire details from the linked task
records. Exact availability and selection still belong to the candidate's
build/deployment receipt; the base checkout does not include every overlay.
All listed frames are self-contained, not XOR/subtraction deltas. The later
differencing experiment was rolled back; [BENCH-008](../tasks/BENCH-008.md)
retains its correct-image but worse-performance result.

| Request capability | Permitted selected format | Meaning |
|---|---|---|
| Plain `/video` | EVF1 | Raw complete frame |
| `rle2=1` | EVR1 or raw fallback | Complete RLE2 v1.0 file after the 32-byte frame header |
| `packed=1` | EVP1 or raw fallback | Frame-local palette with 1/2/4-bit indices |
| `packed=2` | EVP1 or raw fallback | Palette form plus direct six-bit RGB222 |
| `pair=1` | EVQ1 or raw fallback | Optional experimental pair-RLE; not the ordinary default |

The selected production browser default combines `rle2=1&packed=2`: the server chooses an
eligible smaller representation. Requesting a codec is not proof it was sent;
record actual magic and bytes. Earlier RLE2 candidates limited decoded frames
to 512×384; the composed-packing candidate enlarged that bound to 1024×768.
Do not apply the newer limit to an old deployed image. SRLE2/TurboVega experiments
have separate envelopes and are not silently substituted into EVR1.

### Shared compressed-frame header

EVR1/EVP1/EVQ1 retain the EVF1 32-byte metadata layout with their own magic,
version 1 and RGB222 pixel-format 2. Width/height, sequence, flags and logical
period retain their meanings. Stride must equal width. `payloadBytes` means
**decoded** width × height, not compressed WebSocket payload size. Encoded
length is the message length minus 32. Decoders reconstruct canonical EVF1
metadata and RGB222 pixels and then apply the normal header/size/flag checks.
No receiver needs an earlier frame to recover after reconnect or mode change.

### EVR1 RLE2 payload

Payload is the complete 14-byte-header RLE2 v1.0 file, including `Cmpr`, decoded
size, `RLE2` and version 1.0. Final framebuffer RGB222 values are mapped to the
codec's opaque RGBA2222 domain and converted back on decode; do not reinterpret
native packed palette indices as those colours. The decoder checks the file
header, declared size, token/input/output bounds and exact decoded length.
Raw fallback applies when ineligible, allocation fails or the complete encoded
message is not smaller. The default does not imply arbitrary-alpha asset parity.
[Original contract and bounded implementation](../tasks/QUAL-003/debrief/P01h/CONTRACT.md#web-candidate-protocol--evr1-v1-iteration3)
retain provenance and the earlier size/pacing bounds.

### EVP1 payload

Offsets below are relative to the byte immediately after the frame header.

| Offset | Bytes | Palette form | Direct six-bit form |
|---|---|---|---|
| 0 | 1 | Bits/index: 1, 2 or 4 | 6 |
| 1 | 1 | Palette count: 1..2^bits | 0 |
| 2 | 2 | Reserved zero | Reserved zero |
| 4 | Variable | Unique RGB222 palette bytes, then packed indices | Packed RGB222 samples, no palette |

Samples/indices are MSB-first across the complete raster, crossing row boundaries.
Unused final low bits are zero. Palette indices must be in range and palette
entries unique values 0..63. Direct six-bit form packs four pixels into three
bytes. Encoded payload size is `4 + palette_count + ceil(width*height*bits/8)`.
Malformed lengths, reserved bits, palette values/indices and nonzero padding
reject the frame. Full decoded colours are retained without quantization.
[Palette experiment](../tasks/BENCH-005/composed-packing/PROTOCOL.md) and
[six-bit extension](../tasks/BENCH-005/composed-packing/sixbit/PROTOCOL.md)
retain selection/allocation evidence; smaller packets do not guarantee lower
total CPU cost or better gameplay.

### EVQ1 optional pair payload

Each little-endian 16-bit token contains count-minus-one in bits 15:12,
first RGB222 colour in 11:6 and second in 5:0. Repeat the pair 1–16 times,
starting at raster offset zero and crossing rows. An odd final pixel is one
RGB222 byte after the pair tokens. Payload is at most one byte per decoded
pixel. Reject truncation, overrun, excess bytes and an out-of-range odd tail.
The proposed literal-flag variant was not deployed and is not this format.
[Experiment/selection record](../tasks/BENCH-005/composed-packing/pair-rle/PLAN.md)
retains the revisions: ordinary selection was restored without `pair=1`.

## Local validation

Run `.venv/bin/python tests/browser_rgb222_test.py` for C++ sanitizer coverage,
all 64 colours through actual WebGL, format/size/stride changes, malformed
frames, leases and browser credit. `tests/browser_video_ui_test.py` covers the
page's video reconnect behavior. For a prepared current bundle, use
`tests/browser_bundle_test.py --bundle <directory>` as described in the
[build guide](../building.md); the older base tests alone do not validate every
compressed envelope. Historical overlays require their own retained checks.
These local checks do not contact the P4 or Agon.
