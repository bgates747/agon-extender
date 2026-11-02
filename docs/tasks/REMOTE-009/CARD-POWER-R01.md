# P4-PC card power correction and blocked transfer comparison

The matched staged-transfer P4 application was installed and independently
flash-verified, including a missing board power-enable step. P4 SD still times
out before card identification, so successful staged-file cases and the speed
comparison remain blocked. The earlier1.1MB baseline remains valid evidence;
there is no measured staged speedup. No acceptance or promotion is claimed.

## Evidence and scope

| Item | Result |
|---|---|
| Author handoff | Both boards power cycled; Legacy prompt responds to P4 keyboard; continuation authorized |
| Fresh pre-install mount | ESP_ERR_TIMEOUT, no card capacity, format disabled |
| Manufacturer reference | Clean OLIMEX/ESP32-P4-PC04032d68e5c727870f9d40beb9e37b7ab3a66916, Rev C |
| Missing initialization | GPIO45/SD1_PWR_EN drives FET1; manufacturer selects active-low power and100ms stabilization |
| Corrected source | Main project26809eba; matched application sourcef4633a168ee08e6c064d7955e9337862754a73d2 |
| Installed experimental build | indexed-hdmi-r27-b2026-11-02-23-11-45Z |
| Application |1803024B; SHA-25612636b9efd715515257b5ca2d3216e11cd456c6f2939e80aef95eac001c991e1 |
| Incoming full16MiB | SHA-256006397a5a8b0f0e47d350e4a63b4f849c4a75635e7f5569a02f2b8a57871f84b |
| Installed full16MiB | SHA-25644307099526d95a1504c3ef24a5a180ae3162429ea4f02a0e97e20408acc995b |
| Flash verification | Application exact; bytes outside written application sectors unchanged |
| Native build | PASS; same HDMI/dual-USB/controller/compiler/partition configuration; only declared source delta |
| Offline regression |56 checks pass, including board mapping/conflict and existing engine/client/native checks |
| Initial P4 health | Correct build booted once; five clean seconds, display available, zero rolling faults, USB controller valid |
| Post-install P4 SD | ESP_ERR_TIMEOUT persists; formatting disabled |
| Unavailable-media admission | HTTP503; no UART worker/records, job stays idle, no output published; ordinary RPC/startup read and EXIT pass |

The earlier r27 build at22:32:18Z remains uninstalled and unchanged. The installed
build uses a new UTC build timestamp, not a renamed earlier binary. The card
power correction is an identified omission; these results do **not** prove it
was the sole cause of the timeout or establish that the physical card is faulty.
No filesystem repair, formatting, unmount, card removal, wiring change or
software power-cycle retry was performed.

The candidate includes the new worker but is not selected production. After the
blocked qualification, the agent restores the exact incoming P4 image rather
than leave the unqualified application installed. EMOS and mainboard VDP were
not flashed. Full128KiB EMOS still matches incoming SHA-256
`84da2c5ac3cebb1c470bab201f797a936296a6bfc33b6ebdbcf5d1dd3a1d1d79`;
startup is unchanged and the mainboard remains mode0. Exact final restoration
and resource handback are separate receipts in the local bench record.

No successful staged job or new speed result is claimed. Physical P4-PC card
presence/seating remains the next prerequisite; do not confuse this with the
working Agon SD card. The card-power omission is proven in source, but whether
the installed card is present, connected, powered and responsive remains
unresolved; no voltage or card-detect measurement is claimed.

Raw source/build/readback/admission and handback records remain in the ignored
REMOTE-009 bench run, indexed by the machine-local bench record. The private
reset endpoint embedded in the application makes the generated binary local-only.

## Final restoration and handback

Independent full16MiB readback equals the exact incoming P4 bytes, SHA-256
`006397a5a8b0f0e47d350e4a63b4f849c4a75635e7f5569a02f2b8a57871f84b`.
Original r25 boots cleanly, ordinary Legacy listener/read/EXIT passes, and startup
and listener remain byte-identical. Final input is ready/neutral, listener is
offline with no pending exchange, both USB devices have no reader, and both
deliberate reset holders have released and exited. Visible/flashing cursor
controls are sent; no optical pass is inferred. No test or transfer remains.
The [portable evidence](CARD-POWER-EVIDENCE.json) records these bounded results.
The bench reservation is released; further card work awaits the Author's handoff.

## Card reseat follow-up

The Author found the P4-PC card jarred loose, reseated it, power cycled the P4-PC
and reset mainboard. Fresh original r25 mounts with ESP_OK: raw capacity
31914983424B, filesystem31902400512B, free31899942912B, formatting disabled.
Finite Legacy listener/startup/listener-binary read and EXIT verify the normal
CLI. No flash, reset or staged job is issued by this follow-up.

This success on original r25, without the source power-enable correction,
identifies physical seating as the observed timeout's cause. The missing
explicit initialization remains a source finding, not a demonstrated cause of
the failure. Golem claimed its next bench slot during preflight; Extender yields
with listener exited. Successful staged-file cases and comparison await that
slot's verified restoration/release. The prior failed-run evidence stays frozen.
