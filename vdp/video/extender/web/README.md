# Extender browser assets

EDP/P4 embeds and serves these assets; no separate npm build is required.
The browser presents final P4-composed pixels and forwards captured keyboard
transitions. It does not reproduce VDP palette, Copper, sprite or cursor logic.
Network services use plain HTTP/WebSocket on a trusted LAN without authentication.

**Maintained builds and the installed image remain distinct.**
RELEASE-001 consolidated the retained raw, RLE2, packed and pair-RLE decoders
here. `prepare_console.py` builds this composition from clean committed inputs;
`tests/browser_bundle_test.py` verifies the actual embedded assets, requested
compression and paired codecs. The corrected client requests `?rle2=1&packed=2`
without changing presentation-credit pacing. These drafts have not been flashed
or hardware-equivalence accepted. Consult the
[build guide](../../../../docs/building.md) before replacing installed firmware.

| Subject | Maintained authority |
|---|---|
| Operation, prerequisites and platform limits | [Using Extender](../../../../docs/using-extender.md) |
| Video wire format, RLE2 default, pacing and measurement scope | [Browser video contract](../../../../docs/protocols/browser-video.md) |
| Host/browser/USB arbitration, lock state and capture | [Keyboard guide](../../../../docs/remote-keyboard.md) |
| Optional browser reset button and Pi bridge | [Reset guide](../../../../docs/bench-reset.md) |
| Exact browser-capture candidate checks | [REMOTE-001 implementation](../../../../docs/tasks/REMOTE-001/B04-implementation.md) |

The source selection in `vdp/pio/p4-console-source-selection.json` identifies
embedded files. `app.js` connects the page, presenter, credit flow, display status
and browser input. `frame_protocol.js` decodes the selected wire formats and validates frames/credits;
`webgl2_presenter.js` handles final RGB888/RGB222 pixels with nearest-neighbour
sampling. `index.html` and `style.css` own page layout. The build manifest identifies the exact embedded asset hashes.

For a browser-only asset check, serve this directory over HTTP and open
`/?demo`. That exercises its parser/presenter, not P4 transport, MOS keyboard
admission or every deployed codec. Repository tests include
`tests/browser_rgb222_test.py`, `tests/browser_capture_ui_test.py` and
`tests/browser_video_ui_test.py`; read each test's scope before using its result
as evidence for an installed candidate.

## Display status

While video is connected the page polls `GET /display/status` once per second,
with one request in flight and a two-second timeout. P4 publishes `available`,
`mode`, `width`, `height`, `colors`, `refresh_hz`, `double_buffered`; unavailable
returns HTTP 503. The header describes P4's committed display configuration,
not Legacy mainboard output, not the EVF1 storage format, and not an atomic
association with a particular queued frame. Nominal refresh and Presented fps
are different values. This read does not acquire keyboard ownership.
