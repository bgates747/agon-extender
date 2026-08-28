# Extender browser video assets

These project-owned assets implement the primary EDP video presentation path.
EDP/P4 serves them directly from firmware through PORT-006; no Pi, filesystem,
or external web server is a product runtime dependency.

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
