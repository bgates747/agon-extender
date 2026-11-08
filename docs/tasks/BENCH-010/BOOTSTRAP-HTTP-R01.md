# Native bootstrap read-only timeout handling

The original temporary RX-006 installation stopped after independently verified
firmware writes because one display-status HTTP timeout escaped its readiness
loop. The prepared host correction treats that timeout as a missing observation
within the original deadline. Eleven host controls pass; no corrected physical
bootstrap or consumer test has run.

1. The maintained candidate is `scripts/native_bootstrap.py`. It retains the
   explicit experimental P4 source signature and caller-owned lease, source,
   startup and port checks. It is not a production selection or a general reset
   command. Existing frozen callers and their old bootstrap source are unchanged.
2. During the first P4 initialization observation only, a direct timeout or
   `URLError` wrapping a timeout resets the five-second stability interval and
   produces a durable missing-sample record. The original sixty-second deadline
   remains. Other HTTP, connection, schema and serial-startup failures propagate.
3. The owner still performs one P4 reset, requires the correct serial signature
   and positive stable display, then performs one commissioned Agon reset and
   requires positive console/input evidence. The caller separately proves the
   actual CLI, state, whole files and idle resources. No test starts on reset.
4. `tests/network/native_bootstrap_test.py` covers healthy readiness, direct and
   wrapped timeouts, stability reset, repeated timeouts, unavailable/faulted
   display, missing signature, fatal serial evidence and unrelated HTTP,
   connection and JSON errors. These fake-clock controls open no port or network
   connection and execute no reset, firmware operation or application.
5. The original failed installation and exact restoration remain immutable.
   Any future RX-006 attempt needs a new normal reservation, exact helper and
   component pins, fresh owner admission and the original cleanup reserve.
   Current consumers and FIFO order remain protected. This correction does not
   diagnose the underlying HTTP timeout or establish physical reliability.

Scope follows the existing RX-006 error-resolution request and BENCH-010 owner
recovery responsibility. Machine-local logs, selected source hashes and host
control receipts remain in the ignored bench scheduler evidence.
