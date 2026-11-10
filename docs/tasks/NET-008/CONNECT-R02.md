# NET-008 — Runtime credential provisioning and real modem connection

Smith requests another exclusive bench lease and an actual ESP8266 connection,
then explicitly holds the new lease until he asks for release. Pi5 owns the
verified private keyring entry. Finish host/source preparation while the sole
scheduler reconciles existing occupancy; a quiet bench is not a checkout.

## Scope and sequence

1. Reserve normal Olimex custody for this connection iteration; scheduler grants
   before physical admission and designates one operator. Preserve queued peers.
   Do not touch the previous Mech lease or treat the new request as preemption.
   Hold the new NET-008 lease after completion/failure until Smith releases it.
2. Reuse the tested TX48/RX47 UART wiring at1152008N1. Retain the exact incoming
   installed identities and supported product rollback bytes. Install only an
   independently built/verified stopped P4 UART appliance when custody/admission
   is complete. Preserve mainboard firmware, startup, bootloader, partitions,
   NVS and ESP8266 firmware. No test autorun or startup change.
3. Add explicit JOIN to the existing USB diagnostic CLI. Pi5's OS Python reads
   only the exact MOD-WIFI keyring entry; the project host runner receives its
   checked packet over a private stdout pipe, never a file/argument/log. P4 gets
   length-bounded runtime SSID/password bytes only after positive input-ready.
   Do not compile credentials into P4, persist them in the modem, or record them
   in USB/UART logs, command journals, captures, core dumps or failure traces.
4. P4 validates lengths/characters, disables AT echo, selects station mode with
   AT+CWMODE_CUR=1, sends one correctly escaped AT+CWJAP_CUR command, then checks
   current association and station address. Reuse the accepted C8 escaping and
   old AT1.3 behavior; do not assume modern ESP-AT APIs. Keep a60s original join
   bound and finite DHCP query window, report safe phase/progress/IP-ready status
   only. Wipe private buffers after use. A timeout stops without join replay.
5. After successful association, run the existing two-second bidirectional
   CRC-checked Pi5 TCP case at115200 to prove the actual ESP8266 data route.
   The prior TORTURE-R01 baud ladder remains authorized, but no rate result is
   claimed from association alone. Keep endpoint CRC/byte/sequence results and
   cleanup separate. Disable analyzer acquisition throughout credential setup.
6. Retire UART safely and join every owned process/socket/reset holder after
   each bounded phase. Keep identified development firmware installed and the
   actual bench hold; no automatic product restoration or release. Preserve
   useful failures and actual modem baud for deliberate continuation.

## Qualification and readiness

1. Host controls cover escaping, invalid private packet rejection, and safe
   output on failures. Native build remains strict; reserve Pi compiler FIFO
   for build/checks, expected under120s and finite600s, under2GiB.
2. Existing codec/peer acceptance checks remain unchanged. An isolated fake
   private credential may exercise framing/log suppression; do not read real
   keyring values for source tests. Real keyring availability is checked without
   displaying values; the actual connection retrieves them only in memory.
3. First physical result must identify the exact P4 app/source, actual lease,
   modem response/association/IP and real TCP result. No Wi-Fi success inferred
   from keyring presence or AT command transmission.

## Existing references

1. [Earlier protocol and qualification](TORTURE-R01.md) and the task's full wiring
   diagram retain physical mapping and historical evidence.
2. `tools/wifi-setup/src/setup.c` owns the already-used old-AT escape and CUR-only
   join behavior. The retained2016 Espressif AT reference in TORTURE-R01 bounds
   the grammar. P4 UART/USB behavior uses the pinned IDF5.5.5 source there.
3. The Pi5 manager's verified keyring repair preserves the MWJ1 private entry
   schema and encrypted collection. Read its exact entry through the retained
   helper; no whole-keyring migration or plaintext fallback.

## Source preparation result

The runtime JOIN implementation is frozen at `c4f0faaf`. Strict native escaping
checks and four synthetic private-packet controls pass, alongside the unchanged
bandwidth codec/real loopback peer controls. The identified P4 build completed
in68.463 host seconds:239968 bytes, SHA256
`fe1299f896bcd9b2276c77fbfb286f3cdb84722e7014bb62fed95719841b5e85`.
Its immutable manifest and joined compiler receipts are in the ignored local
`agents/net008/connect-r02/` record. This is a stopped appliance build, not an
installation, Wi-Fi association or bandwidth result.

The maintained private operator is `scripts/modem_join.py`; OS Python supplies
the exact libsecret entry over a bounded private pipe. The host and P4 suppress
raw credential replies and wipe mutable packet buffers. No credential supplier
is invoked during source checks. P4 emits safe association progress once per
second and retires UART after its finite result. Native escaping includes
quotes, backslashes, commas, maximum lengths and control-character refusal.

Physical readiness remains false: the sole scheduler reports MechAgon165 active,
6502 next, then NET-008 request9fdfecfe6ccb. No preemption or hardware operation
was performed. The new lease, once granted, stays held until Smith releases it.

## Actual168 first installation and diagnostic correction

The first239968B appliance installed and independently compared successfully.
The explicit INFO received AT/status responses at115200, then P4 main-task stack
protection halted during CIFSR reply hex formatting. No credentials were loaded
or JOIN submitted. Preserve the failure/serial and original wait1; this is an
appliance defect, not a modem/Wi-Fi association failure. Mainboard reset holder
remains intentionally asserted while P4 is halted. The same held lease permits
a separately identified corrected build:16KiB main stack plus main-task-only
static2048B AT reply scratch, still wiped after command. Retain stack guards and
verify effective build config. Replace only diagnostic application, independently
compare new bytes and explicit stopped boot, then run a deliberate INFO before
first JOIN. No automatic fault replay, standard restoration or lease release.

## Actual168 association and first short baud ladder

Corrected diagnostic380b4ea6 passes installation/readback/stopped boot and INFO.
Private first JOIN succeeds in5.979host seconds, nonzeroIP, UART retired; no
credentials captured. Short bidirectional endpoint CRC/byte/frame checks pass
115200 and230400. First384000 arm fails with145 P4 UART errors (FIFO overrun),
zero recorded CRC/frame errors before stop, and unresolved immediate cleanup.
Original peer/processes joined. A separate explicit384000 INFO then passes,
establishing positive AT/status command-mode reconciliation without replay.
Host --qualify-baud selects deliberate lower-rate short+10/30/60qualification
without resubmitting the failed384000arm. P4 image unchanged; this is a separately
identified host continuation, not a silent firmware/source repin. No rate is
one-minute qualified yet. User-held lease168 remains occupied.
