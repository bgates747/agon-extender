# Extender browser video assets

These project-owned assets implement the primary EDP video presentation path.
EDP/P4 serves them directly from firmware through PORT-006; no Pi, filesystem,
or external web server is a product runtime dependency.

The Author retired browser keyboard capture on 2026-09-09. The active page is
restored byte-for-byte from the pre-input video baseline (`a53dffd`): video
connection, frame statistics and the local test pattern only. Keyboard input
comes from the separately selected mainboard or P4 USB device. The shared HTTP
service provides no keyboard or timing endpoint. Earlier browser-input source
and UI tests remain reproducible at their recorded Git commits; REMOTE-001
retains the evidence and unresolved findings.

The current first-tranche firmware serves plain HTTP and WebSocket only on the
trusted bench LAN. Open `http://<observed-dhcp-address>/`; `https://` is not
implemented. TLS, authentication, and wider network exposure remain explicitly
deferred.

`frame_protocol.js` is the strict browser authority for EVF1 v1 and its
one-credit browser state machine. `webgl2_presenter.js` uploads only final
P4-composed RGB888 pixels. It does not reproduce palette, Copper, sprite,
cursor, or other VDP behavior. `app.js` binds those pieces to the page and
grants the next `frame` credit only after the animation loop presents the
preceding accepted frame.

For a browser-only check, serve this directory over ordinary HTTP and open
`/?demo`. The generated test pattern traverses the same strict EVF1 parser and
WebGL2 presenter as network frames.

The wire authority and bounds are frozen in
`docs/tasks/PORT-003/phase-f/fixtures/evf1-contract.yaml`. Firmware embedding
and HTTP/WebSocket ownership belong to PORT-006.

### Display status header

The page polls the additive read-only `GET /display/status` endpoint once per
second while its video WebSocket is open, with one request in flight and a two
second timeout. It neither claims input ownership nor changes a display mode.
P4's VDU owner publishes a coherent snapshot after a successful mode commit:
`available`, `mode`, `width`, `height`, `colors`, `refresh_hz`, `double_buffered`.
During unavailability/change the endpoint returns HTTP 503 with
`{"available":false}`; the page shows unavailable rather than guessed fields.
Dimensions/colors/buffering describe the P4 display, not EVF1 pixel storage.
Refresh is the official modeline's nominal rate, independent of Presented fps.
Metadata describes the current committed configuration, not an atomic association
with a particular queued video frame. Legacy mainboard output is not observed.
