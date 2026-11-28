# Onboard Agon UART and firmware updates

The byte stream from the eZ80 to the mainboard VDP is the ordinary FLASH
write itself. The separate Pi USB readback after that write is the expensive
verification transfer. Removing the latter requires another witness for the
selected flash contents. A reported SD CRC or a MOS prompt alone carries
different information.

## Exact source used

The Agon upstream firmware guide distinguishes the eZ80 MOS ROM from the
mainboard ESP32 VDP app and calls FLASH from the Agon SD card. The sealed
v0.1.4-alpha release source archive, at VDPlet commit
`77ad7a1d28c0d44fd2cd2cf4aa4cded10f770485`, contains
`firmware-src/video/updater.h`. Its stock update handler receives bytes,
accumulates an 8-bit sum, calls `esp_ota_write`, checks the incoming sum,
selects the updated partition and restarts. The retained Bistromathics
v2.16.0 reference `c7ac293d2aa81ddfa693390549bcd909069c8fc3` has the
same stock route. FLASH v1.9 tag `e670b5bd910dfe372c29aa9e896e6c24cc8530ec`
defines the sender and pre-confirmation CRC. [Agon firmware guide](https://github.com/AgonPlatform/agon-docs/blob/main/docs/Updating-Firmware.md) · [FLASH v1.9 sender](https://github.com/AgonPlatform/agon-flash/tree/v1.9/src) · [Bistromathics updater](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/updater.h) · [VDPlet release source listing](https://github.com/bgates747/agon-vdplet/releases/tag/v0.1.4-alpha)

## Transfer ledger

| Operation and caller | Direction and bytes | Frequency | Justification and disposition |
| --- | --- | --- | --- |
| Ordinary `FLASH vdp`, `src/main.c` `update_vdp` and `src/flash.asm` `_startVDPupdate`; called by `olimex_vdp_ota.invoke_flash` or the MOS operator | Raw app from Agon SD through eZ80 RAM, then eZ80 → mainboard VDP on the onboard UART. One image of declared length, a four-byte update command, a three-byte length and one checksum-complement byte, plus unlock and progress control. Current standard 1,117,392 B. | Once per new app write. Normally one candidate and one production restore per mainboard-firmware job. | Keep when an image actually needs installation. The running VDP is physically on the other side of this UART and must receive the new bytes. Confirm firmware and planned slot at checkout so a job that needs no image change sends nothing. A resident SD image avoids Pi→P4→Agon traffic but still crosses the onboard UART when FLASH writes it. |
| FLASH SD-file CRC; `calculateCRC32`, `showCRC32`, observer `confirmation` | The eZ80 scans the SD file locally and prints a hex CRC. A small console record reaches the Pi via the mirror on mainboard USB serial. The image stays on the Agon during the check. | Once per FLASH invocation with interactive confirmation, before a write. | Keep. It checks the candidate or restore input without returning that file. The Pi compares with the CRC of the pinned local image and sends the one permitted confirmation. |
| Stock OTA receive status, `video/updater.h` | The VDP reports progress, checksum, reboot and status as display/serial output. Retained transcripts for a 1.1 MB write are about 1.7 KB. The checksum is over received bytes. | Per stock FLASH write. | Keep the small outcome records. They establish the stock receiver reached the expected stage. They do not attest an exact flash extent after writing. |
| Ordinary fixture execution `Bench.invoke`, fixture programs, native capture | eZ80 → mainboard VDP ordinary VDU screen, bitmap, audio or native payloads produced by the fixture. Bound by the fixture, using the app's ordinary execution route. The observer receives bounded result text over USB serial, for example the two VDPL-054 timing rows and one terminator. | Per requested run. | This is the workload under test. Keep the traffic specified by the fixture. Do not add a second payload stream to confirm that a diagnostic line arrived. Structured reports fetched from the SD card appear in the separate SD ledger. |
| Historical BENCH-024 / VDPL-060 verified OTA receiver; `docs/tasks/BENCH-024/ota_runner.py`, matched FLASH utility and special receiver | Full app eZ80 → VDP, in explicit 1–1,024 B chunks. Receiver reads the new flash locally. Return channel carries correlated control replies and one 80 B status record when requested, retrieved as 40 words. Replying 40 times costs framing and round trips, while the image bytes never return. | Only in a separately commissioned receiver-qualified job. | The earlier physical result proves a route can verify the exact declared extent on the ESP32 without USB ROM entry. Keep as design evidence and specialist fallback. The tested receiver is a different firmware from ordinary production; changing standard firmware to require it is a separate decision. |
| `FLASH mos` eZ80 local write and CRC, FLASH v1.9 `update_mos` | The eZ80 reads the ROM file from SD and writes its own on-chip flash. No ROM bytes cross the onboard eZ80↔VDP UART for this write. It emits small progress and result messages and checks a CRC of its written bytes locally. | Per explicit EMOS install/restore. | Keep the local CRC and MOS restart proof. The current runner's separate `SAVE` and UART download of the entire 128 KiB installed ROM is in the SD ledger. It exists for exact host comparison, and its removal requires a replacement that attests the expected extent and identity. |

The active P4-staging route hits a different UART and ends on SD. The
onboard FLASH stream starts from SD. A PC-staged card saves the first
transfer and leaves the flash-writing stream intact. The P4 ESP32's own
programmer and the mainboard ESP32 programmer use separate USB connections.

## Retained measurements

The VDP's own upload timer covers its receive/write loop. USB app-read
durations below are the differences between the saved OTA selector and
full app file modification times. They approximate the *application read
portion*, including protocol and local file write overhead. They exclude
the preceding USB ROM entry/table/selector and following startup witness.
The records share the relevant filesystem clock. Use them as observed
intervals, without inferring unlogged wire activity or a guaranteed deadline.

| VDPL-054 baseline phase | App bytes | Native FLASH receive/write | Full USB application read | USB versus native |
| --- | ---: | ---: | ---: | ---: |
| Install timing image on app1 | 1,118,288 | 18.735 s | ~103.718 s | 5.54× the native time |
| Restore v0.1.4-alpha on app0 | 1,117,392 | 19.127 s | ~103.577 s | 5.42× the native time |
| Pair total | 2,235,680 | 37.862 s | ~207.295 s | 5.48× the native time |

The USB path also reads 4,096 B of table and 8,192 B of OTA selector per
operation. At 115,200 baud with 8N1, the app bytes alone account for a
194.07 s serialization floor for this pair. The retained v0.1.4-alpha
promotion independently shows an 18.947 s stock write and ~103.650 s USB
application read. Evidence is in the VDPlet working tree
`build/vdpl054-olimex-v014/evidence/baseline/{install-mainboard,recover-after-run-scanline/restore-mainboard}`
and `build/releases/v0.1.4-alpha/default-promotion/evidence-r01/install-mainboard`
under each operation's `vdp-usb.bin`, `ota-selector.bin`, `readback.bin` and
`independent-verification.json`.

## Smaller independent verification

1. **Existing esptool route.** Bind the expected board, table, selected slot,
   app offset and exact extent. Have the ESP32 calculate the digest directly
   from flash and return it. Installed esptool 5.1.0 exposes
   `ESPLoader.flash_md5sum(addr, size)` and the stub returns 16 digest bytes.
   Compare against the digest derived from the locally pinned raw app. Keep
   the release SHA-256 as the artifact identity and record which algorithm
   attested the actual flash. The current `readback.bin` and SHA-256 receipt
   consumers must understand the new method explicitly. This preserves
   verification against accidental byte errors and does not claim that an
   MD5 match is a retained byte-for-byte copy or a signature check.
   The USB reset and ROM SYNC remain, including their intermittent failure
   modes. Qualify successful and unsuccessful replies, exact range and wrong
   slot, wrong identity, restart and MOS, and compare to one full readback in
   a bounded hardware qualification. No automatic bulk fallback or retry.
   [Espressif serial protocol](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/serial-protocol.html)
2. **Avoid the programmer on ordinary writes.** A future supported VDP
   receiver can report a fresh boot or transaction witness, actual selected
   and running slots, image length and the digest it computed over the exact
   flash range. BENCH-024 is the prototype. The stock v0.1.4-alpha handler's
   additive checksum and a banner cannot supply that proof. An ESP-IDF
   app-description ELF hash or an embedded image digest has a different
   extent from an exact raw release file. Use an explicit bounded flash read
   on the ESP32 when exact raw-image comparison is required. A production
   interface or release change needs separate review and qualification.
   [Historical BENCH-024](../BENCH-024.md) · [Espressif partition API](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/storage/partition.html)
