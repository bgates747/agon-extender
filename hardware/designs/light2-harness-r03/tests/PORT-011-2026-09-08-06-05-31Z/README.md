# Analyzer acquisition preflight — FAIL

PORT-011-2026-09-08-06-05-31Z requested 2 MHz, 120,000,000 samples (60 seconds),
channels D1/D3/D4/D6. The process exited zero but retained only 15.84128
seconds. No processor was reset and no UARTFLOW exchange was invoked; this
is an informative acquisition failure, not an endpoint test.

The [original trace](logic.sr), [metadata and hashes](acquisition.json) and
[brief timeout excerpt](timeout-excerpt.txt) preserve the observation. Full
commands and logs remain in ignored bench storage. The selected probe names
occupy their original physical bit positions despite selecting four channels.

A [second preflight](../PORT-011-2026-09-08-06-12-01Z/README.md) reproduced
the early stop at 20.85888 seconds.

Logs show repeated empty LIBUSB_TRANSFER_TIMED_OUT completions immediately
before SR_DF_END. In the installed libsigrok 0.5.2,
[receive_transfer](https://raw.githubusercontent.com/sigrokproject/libsigrok/libsigrok-0.5.2/src/hardware/fx2lafw/protocol.c)
ends acquisition after too many empty transfers. This explains why the
capture can end short; it does not identify why the USB stream stopped.
USB autosuspend was already disabled; the inspected kernel tail had no
corresponding disconnect. The firmware images and requested capture settings
remain unchanged. Resolve acquisition reliability before the powered-reset
flow test; do not equate exit zero with the requested sample extent.
