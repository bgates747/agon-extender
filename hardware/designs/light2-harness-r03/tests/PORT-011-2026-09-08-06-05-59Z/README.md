# Same-build smoke/UARTFLOW SD prepared

Preparation PORT-011-2026-09-08-06-05-59Z follows the Author-confirmed
[EMOS v0.4.0 installation](../PORT-011-2026-09-08-05-55-02Z/README.md).
The workstation verified the consumed firmware and both rollback payloads,
backed up the previous test files, copied the frozen candidate review media,
published autoexec last and verified all copied hashes. The SD was safely
unmounted. See the [preparation record](preparation.json) and original
[CRLF autoexec](autoexec.txt).

EMBOOT/check.txt match agon-emos-v0.4.0-b2026-09-08-05-51-31Z. Autoexec selects
mode 3, runs SD/clock smoke and invokes EMOS UARTFLOW. No flash command remains.
Physical smoke, flow stages and final prompt observation are pending.

The combined capture launcher is prepared in ignored bench storage, but the
powered-reset handover awaits resolution of the
[analyzer acquisition failure](../PORT-011-2026-09-08-06-05-31Z/README.md).
No processor reset, flash or wiring change occurred during this preparation.
