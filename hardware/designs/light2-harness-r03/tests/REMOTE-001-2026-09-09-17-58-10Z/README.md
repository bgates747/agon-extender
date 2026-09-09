# Corrected keyboard diagnostic initialization deployed

The r04 candidate from clean commit 1ce96dc was written, independently verified
and observed starting with its matching identity and expected UART declaration.
EMOS, the SD sample and wiring were unchanged.

The subsequent real browser/P4 check received six video frames and exported
records. A separate keyboard WebSocket performed a non-owner heartbeat without
taking keyboard control or sending keys. The P4 records show keyboard_open,
key_message (session 424242, ordinal 1, byte 72) and the expected non-owner
key_rejected. No key_context_missing occurred. This proves the new callback
initializes the physical endpoint and its first message reaches normal input
admission. It does not claim operator capture, a UART round trip, or resolution
of the original r01 latency/disconnection.

The agent closed its browser connections. The Author must reset Agon to restart
its bounded sample, reload the timing page, Connect and Capture keyboard, then
continue the planned measurement. P4 rejection records from the broken r03
initialization remain beside the earlier deployment as informative evidence.
