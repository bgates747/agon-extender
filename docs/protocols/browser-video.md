# Browser video

This is the current browser-video encoding and pacing contract. It promotes
the recurring interface from PORT-003 Phase F; the 2026-09-10 Author-requested
RGB222 increment supersedes that phase's RGB888-only wire restriction and
200 ms first-bench snapshot interval. Historical qualification records remain
evidence for their recorded builds.

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

## Local validation

Run `.venv/bin/python tests/browser_rgb222_test.py` for C++ sanitizer coverage,
all 64 colours through actual WebGL, format/size/stride changes, malformed
frames, leases and browser credit. `tests/browser_video_ui_test.py` covers the
production page's reconnect and video-only behavior. These checks use loopback
and do not contact the P4 or Agon.
