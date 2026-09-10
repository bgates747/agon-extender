# RGB222 r07 functional recovery; typing latency remains open

The Author confirms `emos excom` succeeded with browser video connected and
slideshow ran on Extender. The same recording shows keyboard admission and
accepted PREPARE, COMMIT and LEAVE. EMOS v0.1.12 and SD contents were unchanged.
This is a bounded functional PASS for the r07 request-coalescing correction.

The Author subsequently reports very laggy video refresh while typing. This
could arise before or after EMOS processes a key; no synchronized key-event trace
was collected. Responsiveness and broader performance/uptime remain unqualified.

The 411.131-second recording contains one P4 application startup, no panic,
UART blockage or USB fault, and regular periodic diagnostic output (maximum
10,009 ms interval). A single socket-send failure coincided with deliberately
closing the agent's browser around 44.3 seconds. The operator connected later,
around 278.7 seconds; the failure counter did not rise again. This is not a
claim that the entire recording contains no network errors. P4's LEAVE acceptance
is recorded separately from the user's explicit entry/slideshow observations.

`console-and-video.txt` contains filtered machine-neutral diagnostics.
`observation.yaml` preserves scope and the complete private log's hash. Capture
is stopped; the agent did not reset either board while recording this result.
