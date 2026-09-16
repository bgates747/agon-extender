# P01g diagnostic payload protocol r01

Frozen before build. Retained P02 eight-byte nonce: bytes0..2=P02, byte3=existing
output mode (0 normal,1 off,2 discard), byte4=1 enables ladder; byte5 selects
payload in12288-byte units (0..16), bytes6..7 random. Non-ladder marker preserves
normal EVF behavior. All timed ladder rungs independently request full snapshot
composition at each logical output opportunity. Only network rungs connect a
receiver. Compose-only selects discard with ladder enabled and zero payload.

WebSocket route/request remain existing /video and text frame credit (confirm
route from source before receiver invocation). Diagnostic binary message:
32-byte little-endian header followed by N bytes. Header offsets:0 LDR1 magic;
4 version1 u32;8 fixture nonce8;16 send sequence u32 starting1;20 payload length
u32;24 sender monotonic microseconds low32;28 payload CRC32 u32. Payload[i]=i&255.
CRC is calculated once during preparation, outside the timed window, for each
allowed prefix. P4 allocates one196608-byte PSRAM pattern outside the window in
all variants. Receiver validates length, nonce, strictly consecutive send IDs,
CRC and all bytes. Snapshot generations may be skipped by design; send IDs may
not. No compression. Ordinary EVF frames outside marker window are ignored by
the diagnostic receiver, but still credited.

One send admission per16667us bucket; no catch-up queue. Existing single-client
credit and one outstanding lease remain. Intended opportunities are duration /
16667, actual sends/compositions measured separately. This is not guaranteed
60Hz composition: scheduling may coalesce notifications. The artificial fixed
pattern does not reproduce changing-image cache locality; normal EVF endpoint
is separately measured. No protocol extension in production builds.
