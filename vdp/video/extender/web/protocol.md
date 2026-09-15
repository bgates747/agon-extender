# EVF1 browser-video protocol

EVF1 is the PORT-003 presentation-surface protocol. It is neither the Agon
transport nor the retained VDU byte vocabulary. EDP/P4 composes final pixels
before publication; the browser does not interpret logical VDP state.

Each binary WebSocket message contains one 32-byte little-endian header and one
complete RGB888 frame.

| Offset | Size | Field | v1 rule |
|---:|---:|---|---|
| 0 | 4 | magic | ASCII `EVF1` |
| 4 | 1 | version | `1` |
| 5 | 1 | header_bytes | exactly `32` |
| 6 | 1 | pixel_format | `1`, RGB888 |
| 7 | 1 | flags | known mask `0x03`; full-frame bit required |
| 8 | 4 | sequence | low 32 bits of the 64-bit snapshot generation |
| 12 | 2 | width | 1 through 1024 |
| 14 | 2 | height | 1 through 768 |
| 16 | 4 | stride_bytes | at least `width * 3` |
| 20 | 4 | payload_bytes | exactly `stride_bytes * height`, at most 2,359,296 |
| 24 | 4 | present_period_us | logical frame period metadata |
| 28 | 4 | reserved | zero |
| 32 | ... | payload | complete red, green, blue byte rows |

The message length must be exactly `32 + payload_bytes`. Producers in version
1 emit packed rows and both known flags: full frame and present boundary.

The browser sends the exact five-byte text message `frame` to grant one credit.
It accepts and presents at most one frame, then grants the next credit only
after `requestAnimationFrame` actually invokes the presenter. A slow browser
therefore causes intermediate P4 generations to collapse into the newest
snapshot; it cannot create a browser or server frame queue.

Malformed data closes only that WebSocket connection with protocol error 1002.
The service admits one video client. A new successful WebSocket handshake
replaces the existing viewer, closing the previous socket with code 1000 and
reason `Viewer replaced`. The old webpage stays open; reconnect explicitly
with Connect to become the active viewer again. There is no automatic reconnect.
Pending old frame credit/leases are discarded, not transferred to the newcomer. Internal service failure uses 1011. The trusted private bench-LAN service
has no TLS or authentication claim.
