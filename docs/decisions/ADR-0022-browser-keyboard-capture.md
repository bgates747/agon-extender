# ADR-0022 — Explicit browser keyboard capture

- Status: Accepted
- Completeness: Complete
- Date: 2026-09-19
- Related task: REMOTE-001

The browser starts with keyboard input released. An explicit Capture keyboard /
Release keyboard control requests or relinquishes P4 input ownership. An active
indicator reflects P4 admission. Focus loss, hidden page and disconnect release
browser-held keys; reconnect/focus return requires explicit capture again.

P4 forwards admitted browser events through the existing processed-key path and
stock-compatible serializer to EMOS. EMOS retains input admission and VDU routing.
Capturing input does not change display mode. Controls stay outside the video.
The screen-text endpoint does not acquire video or keyboard ownership.

Browser input uses its own WebSocket to P4, separate from the video connection.
Capture requires EMOS input admission but does not require a connected video
viewer. Losing the input connection releases browser-held keys; losing only
the video connection does not revoke otherwise valid capture.

With Extender input admitted, browser key events remain available in Legacy
and ExCom. In Legacy, mainboard VDP displays ordinary output while the browser
retains P4's image; it does not mirror mainboard output. The operator can type
`emos excom` at the MOS prompt to restore P4 output. Mode switching does not
itself change keyboard capture. Focus loss and input-session loss still release
keys as defined above. Separate sockets do not imply separate P4 execution or
guaranteed latency.

A physical USB keyboard press takes precedence over browser capture. P4 revokes
browser ownership, discards its unsent events and emits releases for its held
keys before delivering the physical press. The browser requires explicit
recapture afterward; input sources do not compete in the shared held-key map.

Explicit browser Capture overrides host-agent keyboard automation. P4 cancels
queued agent input and releases agent-held keys before admitting browser input.
While browser capture is active, agent keyboard acquisition receives busy.
After capture ends, an agent may request a fresh session; cancelled input is not
automatically replayed. Physical USB input retains precedence over both.

Among browsers, the latest explicit Capture takes ownership, subject to physical
USB precedence and input admission. P4 revokes the previous browser, discards
its queued input and releases its held keys before admitting the new browser.
Events from the displaced session cannot regain ownership; it must explicitly
request capture again. Merely opening or reconnecting a page does not take control.

`EMOS KEYINPUT extender` selects the common P4 keyboard source, including USB,
browser and host-agent providers. P4 owns their arbitration; EMOS receives the
same stock-compatible keyboard packets with no provider identifier. Browser
capture neither issues nor requires the historical `EMOS KEYINPUT browser`
selector. This decision does not remove that historical command implementation.

P4 generates held-key repeat for browser input using the Agon's configured
keyboard repeat delay and rate, following the existing USB repeat policy.
The browser sends press/release transitions and suppresses its own automatic
repeated key-down events. Input revocation stops repeat and releases held keys.

Human key transitions are not subject to host-agent automation's fixed 20 ms
event spacing. P4 delivers browser transitions promptly through its console
owner while retaining event ordering, bounded queues and UART flow control.
Agent automation retains its existing pacing. Configured repeat timing remains
separate from initial press/release delivery.

Browser events identify physical key positions. P4 maps them using the Agon's
selected `SET KEYBOARD` locale, consistent with USB input, rather than accepting
characters already interpreted under the browser host's layout. Initial support
uses the existing UK/US mappings; broader locale support is not implied.

Caps Lock follows the active input provider. Browser capture uses the hosting
machine's reported Caps Lock state where available, and subsequent browser key
events keep that state current. Browser support is cross-platform, not specific
to macOS. Physical USB takeover restores the USB provider's own Caps state,
rather than inheriting the displaced browser's state. P4 maintains that USB
state and drives its LED to match; effective state and the active keyboard's
indication must agree. The interface must not describe unknown browser state as
known off. Browser reporting limitations do not establish current qualification.

If Capture cannot obtain Caps Lock state, the browser shows it as unknown until
the first reliable keyboard event supplies it. P4 synchronizes that state before
translating and delivering the key from that event.

Num Lock and Scroll Lock follow the active input provider's state on the same
basis as Caps Lock. Numeric-keypad behaviour follows Num Lock. P4 maintains the
physical USB provider's lock states and corresponding indicators separately from
browser providers. Unknown browser lock state must not be silently treated as off.

Where the browser cannot reliably report a lock state, the control strip offers
an explicitly labelled manual setting. This keeps input usable without claiming
that the chosen state was observed on the host keyboard. Manual state and
host-reported state remain visibly distinct.

While capture is active, Tab and Escape are Agon application keys. The browser
forwards them and prevents their normal browser actions wherever it receives
cancellable events; neither is a capture-release shortcut. Explicit Release,
focus loss and input-session loss retain their defined cleanup behaviour. Browser
or OS actions that withhold events from the page are platform limitations, not
intended passthrough policy.

In fullscreen, moving the mouse to the bottom edge reveals a normally hidden
control strip with Release keyboard and Exit fullscreen. The controls belong
inside the fullscreen container but outside the Agon video image. Do not use
the top edge, where browser fullscreen notices can conflict. Placing the controls
beside the video is the fallback. Revealing the strip alone does not release
capture; explicit release or actual focus/session loss retains its normal effect.

This records accepted behaviour, not completed implementation. The earlier browser
candidate remains historical evidence; the working Extender route is the new basis.
