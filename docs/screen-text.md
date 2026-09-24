# Read text from the Extender display

The host can sample visible ExCom text without taking the browser's video
connection or loading an Agon program. P4 recognizes glyphs in its display
pixels; this is not MOS text-buffer access, Legacy-screen readback or an atomic
receipt that a command completed.

## Use

Use the owner-provided P4 HTTP origin. From the repository root on Linux:

```sh
.venv/bin/python scripts/screen_text.py --url "$EXTENDER_URL"
```

On macOS use `python3`, with the script available locally or through the shared
checkout. The client uses Python's standard library. `--timeout` defaults to
30 seconds; it is used for network requests and the polling deadline, not a
guaranteed hard wall-clock bound on the complete command.

No keyboard capture, SD listener or eZ80 helper is required. The command does
not connect to `/video`, reset Agon or switch its display mode. It only observes
P4's display: Legacy routes ordinary output to mainboard VDP, so this endpoint
cannot establish what the Legacy screen or application is doing. Use one text
reader at a time; captures are shared rather than private per client.

## Result and failures

Successful output begins with `cols=... rows=...` and a sampling notice, followed
by text rows. Printable ASCII is preserved; other glyph codes or failed glyph
recognition become `?`. Fonts, colours, graphics, cursor changes and inherited
edge-cell restrictions affect recognition. Sampling spans time while normal
processing continues; even an unchanged display context does not make it an
instantaneous snapshot.

If the context, font or dimensions change during sampling, P4 returns HTTP 409.
Unsupported dimensions also return 409. The client exposes HTTP/network errors
rather than silently interpreting their bodies as screen contents. Retry after
the display stabilizes. If polling expires with a pending capture, a later
request can retrieve it; do not assume the client cancelled the P4 request.
Another reader may consume the shared result first. No reset or automatic
mode change is part of recovery.

The helper exits after printing the result. Seeing a command echoed is not
proof that it ran successfully: observe its expected output or a separate
execution receipt before sending a dependent operation. See
[Using Extender](using-extender.md) for readiness and input ownership.

## HTTP and processor ownership

| Operation | Implemented behavior |
|---|---|
| `GET /screen/text`, idle | HTTP handler queues capture and returns 202, plain text, `Retry-After: 1` |
| Capture pending | Further requests return 202; the VDU owner samples at most eight cells per parser iteration |
| Capture complete | Next request receives 200 and consumes the shared result |
| Capture invalidated / unsupported dimensions | Next request receives 409 and consumes the error result |
| Dimensions | Nonzero cell width/height counts, at most 255 columns, 255 rows and 8192 cells |

Responses use `Cache-Control: no-store`. The maintained helper polls at 0.2-second
intervals. P4's HTTP handler does not read VDP context/font/canvas concurrently;
the VDU owner performs that work. No text request is sent over the UART to EMOS.
The endpoint inherits the installation's trusted-LAN boundary; it is not an
authenticated remote-access service.

Implementation: [host client](../scripts/screen_text.py),
[capture service](../vdp/video/extender/network/screen_text.hpp), and
[HTTP registration](../vdp/video/extender/network/wired_network_service.cpp).
[Retained qualification](tasks/BENCH-006/RESULTS.md) records one 80×60 capture
at 2.20 seconds; that is not a general throughput guarantee. The
[build guide](building.md) distinguishes the deployed composition from base
source. Legacy readback remains deferred under [BENCH-006](tasks/BENCH-006.md).
