# Operator capture rejection — 2026-09-09

The Author reported immediate capture failure after r03 handoff. The saved P4
recorder contains 984 records with no overwrite: repeated sockets open and
close within milliseconds, without keyboard_open or key_message. Retrieval
froze recording but did not reset either board or alter Agon.

Pinned ESP-IDF 5.5.5 `httpd_uri.c` lines 334–363 dispatches WebSocket
pre/post-handshake callbacks and explicitly skips the initial GET URI handler.
r02/r03 allocated diagnostic context in that skipped handler; the first
message consequently had no context. The r04 correction initializes context
in the registered post-handshake callback and records any missing-context
failure explicitly. This new-instrumentation regression is separate from the
original r01 latency and later disconnects.

`tests/browser_keyboard_dispatch_test.py` consumes the selected IDF source
branch, actual endpoint registration and target handlers. It reproduces the
old failure, then checks capture/heartbeat/key admission, context persistence
and cleanup under the correction. HTTP parsing/sends are test substitutes;
physical callback/first-message verification must follow before handoff.
