# EVS1 v1 — negotiated SRLE2 frame envelope

## Executive summary

Client opts in with `/video?srle2=1`. Server may reply with EVF1 raw, EVR1 RLE2 or
EVS1 SRLE2. Existing raw/RLE2 meanings are unchanged; clients without negotiation
must never receive EVS1. Every message is an independent full frame.

EVS1 uses the existing little-endian EVF1 fields at offsets0–31, with magic EVS1,
version1, headerBytes40, pixelFormat2 (RGB222), FULL_FRAME flag required. Dimensions
are nonzero, at most512×384, stride=width, decodedBytes=width×height≤196608;
reserved offset28 remains zero. Offset32 is encoded payload length (u32), offset36
is intermediate RLE2 file length (u32,14..196622). Total message=40+encoded length,
encoded length14..2097152. CmpS header length must equal intermediate length;
its decoded Cmpr header count must equal final decodedBytes. szip1.12 order3,
recordsize1 subset. Composed frame pixels must be opaque; asset alpha semantics
are not expanded by this protocol.

Receiver normalizes to EVF1 after complete bounded decoding, then uses existing
parseFrame/palette/presenter. Invalid input rejects the entire frame, retains the
last displayed frame, closes the session and requires explicit reconnect. Worker
failure/timeout terminates and replaces the worker; no partial pixels published.

Use existing BrowserCreditState (one credit, no catch-up backlog), capped30Hz.
A server may select raw when compression does not reduce the complete message.
A diagnostic corpus can force a codec for comparison, identified in run metadata;
that is not production selection policy. Replay completion is recorded by the
harness; no new in-band text message is added to the production frame protocol.

Browser protocol rejection uses private close code4002. The inherited client
used1002, which browser WebSocket.close() rejects with InvalidAccessError;
server-originated1002 remains valid. See [WebSockets standard](https://websockets.spec.whatwg.org/#dom-websocket-close).
