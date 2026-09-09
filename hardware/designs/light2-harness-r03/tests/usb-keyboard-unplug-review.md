# USB keyboard unplug diagnostic review

Recorded 2026-09-09 for PORT-015 W2. Installed candidate:
`usb-keyboard-probe-r01-b2026-09-09-19-58-58Z`, clean source `bee69b2`.

## Finding

The observed `USB HOST: EP command error: ESP_ERR_INVALID_STATE` is expected
logging from the pinned driver's physical-disconnect cleanup. It does not
indicate lost keyboard input or a failed application close in these captures.
No executable patch, log suppression, library upgrade or reflash is needed.

## Source trace

1. In ESP-IDF 5.5.5, `_intr_hdlr_hprt()` clears `conn_dev_ena` at physical
   disconnect. USBH halts/flushes endpoints before notifying the HID client.
2. HID 1.2.1's `hid_host_device_disconnected()` calls its disconnect-specific
   close helper. `hid_host_disable_interface_disconnect()` calls endpoint
   halt, flush and clear, then continues cleanup.
3. IDF's halt accepts an already halted endpoint; flush accepts its halted
   state. Clear means making the pipe active again. `_pipe_cmd_clear()`
   rejects that operation because no enabled device remains on the port.
4. `usb_host_endpoint_clear()` logs the returned invalid-state error. HID
   continues releasing the interface/transfer and issues DISCONNECTED. Its
   retained interface awaits the application's second close, which removes
   that object without another endpoint command.
5. Our application releases held keys and closes that retained interface.
   The error precedes this callback path; moving or deleting our close would
   not fix its source and would interfere with the driver's lifetime contract.

The exact call attribution follows the pinned source and captured ordering;
these runs did not instrument a live call stack. The HID source hash matches
the candidate build manifest. HID, USB host and HCD files were independently
compared byte-for-byte with these upstream sources:

- [HID 1.2.1 source at e3c35b8](https://github.com/espressif/esp-usb/blob/e3c35b840b9fc9969b981011c9ff782c01168433/host/class/hid/usb_host_hid/hid_host.c)
- [IDF 5.5.5 USB host wrappers](https://github.com/espressif/esp-idf/blob/v5.5.5/components/usb/usb_host.c)
- [IDF 5.5.5 host-controller commands](https://github.com/espressif/esp-idf/blob/v5.5.5/components/usb/hcd_dwc.c)

## Captured checks

| Run | Connections | Removals / diagnostic lines | Key transitions |
|---|---:|---:|---:|
| [20:50:31Z](PORT-015-2026-09-09-20-50-31Z/README.md) | 1 | 1 / 1 | 22 |
| [20:53:16Z](PORT-015-2026-09-09-20-53-16Z/README.md) | 3 | 2 / 2 | 6 |
| [20:59:38Z](PORT-015-2026-09-09-20-59-38Z/README.md) | 2 | 1 / 1 | 14 |

Original raw-log hashes verify. Every press has one matching release identity,
including synthesized releases after held Shift+A removal. Each error is
followed by the disconnect notice, with only synthesized releases intervening
where needed. No other error-level line, input/host fault, invalid-report notice
or application restart after host readiness appears. Replug succeeds within
the second and third recordings. Opening each serial recording did observe
startup; its cause is separate and remains unestablished.

## Disposition and limits

The diagnostic no longer blocks the bounded W2 acquisition result. Original
partial run records and observations remain intact, with dated review addenda;
artifact lifecycle status stays candidate. This is not a blanket exemption for
invalid-state errors. Errors during attached operation, failed cleanup or
reconnection, and other USB errors remain actionable. Recheck this explanation
when HID or IDF changes; retire the note when upstream omits the disconnected
endpoint-clear call or its misleading error log.

W1 power/current particulars and the run-specific Agon harness observations
remain as recorded. W3 must still implement USB-to-EMOS source admission and
ordinary CLI input. These captures establish USB acquisition, not simultaneous
UART traffic, keyboard layout/repeat/LED parity or broader physical qualification.
