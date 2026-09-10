# ExCom activation crash — PORT-008-2026-09-10-02-01-27Z

Informative failure, retained. The Author attempted ExCom entry three times.
Each attempt retained mainboard output with the switch-failed message and
blinking cursor, lost USB keyboard service, and stopped browser video updates.
The serial record contains three matching load-access panics after PREPARE
and COMMIT acknowledgements, followed by P4 restarts. The browser need not
receive a clean WebSocket close when its P4 peer crashes.

Installed pair: EMOS `agon-emos-v0.1.11-b2026-09-10-01-22-40Z` and P4
`uart-excom-console-r02-b2026-09-10-01-58-58Z`, source `840c052`.
`crash.txt` contains the first matching panic; `decoded.txt` resolves its
addresses using the exact installed ELF. Full raw capture and capture metadata
remain in the ignored local deployment record.

The ExCom PREPARE implementation called raw `changeMode(0)`, which replaces
Canvas without selecting a font. It skipped retained `vdu_mode()` context/font
initialization. On the first post-COMMIT VDU 26, `vdu_resetViewports()` calls
`cursorHome()` and dereferences `getFont()->width` at address 0x00000002.
This is a local integration defect, not an upstream VDP defect. P4 restart
also explains loss of its USB keyboard admission. EMOS retaining Legacy
output does not restore a crashed keyboard provider.

Repair: invoke retained `VDUStreamProcessor::vdu_mode(0)` before acknowledging
PREPARE. This preserves the complete upstream lifecycle. Its early mode reply
is ignored by EMOS while Legacy is selected; post-COMMIT mode/cursor queries
still govern EMOS publication. No EMOS or browser-input change is involved.
The new host regression executes the actual control and retained mode bodies,
checks reset-before-reply and repeated transitions, and rejects the former
raw-call implementation. It does not replace a physical retry.
