# Extender browser assets

EDP/P4 embeds and serves these assets; no separate npm build is required.
The browser presents final P4-composed pixels and forwards captured keyboard
transitions. It does not reproduce VDP palette, Copper, sprite or cursor logic.
Network services use plain HTTP/WebSocket on a trusted LAN without authentication.

**Checkout assets and deployed assets are not interchangeable baselines.**
This directory contains the maintained base assets. Later deployed candidates
also use retained source snapshots and task-local codec/pacing transformations.
For example, the base `frame_protocol.js` parses EVF1 RGB888/RGB222, whereas
recorded installed candidates also decode RLE2/packed frames. The ordinary
`prepare_console.py` builder does not reconstruct every such overlay. Consult
[build provenance limits](../../../../docs/building.md#deployed-candidates-versus-the-base-target)
before replacing installed firmware or claiming exact reproduction.

| Subject | Maintained authority |
|---|---|
| Operation, prerequisites and platform limits | [Using Extender](../../../../docs/using-extender.md) |
| Video wire format, RLE2 default, pacing and measurement scope | [Browser video contract](../../../../docs/protocols/browser-video.md) |
| Host/browser/USB arbitration, lock state and capture | [Keyboard guide](../../../../docs/remote-keyboard.md) |
| Optional browser reset button and Pi bridge | [Reset guide](../../../../docs/bench-reset.md) |
| Exact browser-capture candidate checks | [REMOTE-001 implementation](../../../../docs/tasks/REMOTE-001/B04-implementation.md) |

The source selection in `vdp/pio/p4-console-source-selection.json` identifies
embedded files. `app.js` connects the page, presenter, credit flow, display status
and browser input. `frame_protocol.js` validates base frames and credit state;
`webgl2_presenter.js` handles final RGB888/RGB222 pixels with nearest-neighbour
sampling. `index.html` and `style.css` own page layout. Codec additions in an
identified deployment must be traced through that build's parent/overlay record.

For a browser-only **base-asset** check, serve this directory over HTTP and open
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
