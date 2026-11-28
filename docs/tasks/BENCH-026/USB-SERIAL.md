# USB serial transfer audit

The ordinary mainboard FLASH operation returns an exact application-sized copy
to the Pi after every candidate write and every production restore. This is the
largest avoidable USB transfer on the ordinary path. The ESP32 can independently
read its own flash and report a digest instead. This removes the application
byte stream while retaining an independently checked address, extent and
selected image. It does not remove the current USB port's intermittent ROM
entry and synchronisation risk.

This is based on the live checkout at `4fc1ac7c`, published worker source at
`9a57534e`, and installed esptool 5.1.0. No tool opened a device for this audit.
The mainboard USB link is USB through a CH341 bridge to the classic ESP32
UART. The P4 programming endpoint uses native USB Serial/JTAG. The baud flags
used by P4 tools are recorded here as settings. The mainboard's 8N1 serial-rate
calculation does not establish P4 native-USB transfer time.

## Mainboard USB link

| ID | Transfer and caller | Payload, frequency and cost | Purpose and recommendation |
| --- | --- | --- | --- |
| USB-M1 | Pi5 ↔ classic ESP32 ROM over mainboard USB. Ordinary post-FLASH verification uses `app_readback`; explicitly commissioned legacy USB writes use `program_mainboard`. | ROM reset/SYNC, chip identity reply and SPI attach. The SYNC command payload is 36 bytes. A normal stub session uploads 3,464 B text + 156 B data for the bundled esp32 v1 stub, plus framing and commands. One new ROM session after each ordinary FLASH write. | Retain the identity check as long as this port is the verifier. The stub adds a small transfer and enables the existing practical flash reads. Check whether a ROM-only compact route can establish the table and selector before considering removing the stub. ROM SYNC failures occur before any application transfer and a digest will not fix them. |
| USB-M2 | Mainboard ESP32 → Pi5, `olimex_vdp_ota.app_readback` after each ordinary candidate write and restore, including recover-after-run restores. | 4,096 B at `0x8000` for the partition sector and 8,192 B at `0xe000` for two OTA sectors. At 115,200 baud the 12,288 B take at least 1.07 s of 8N1 serialization, before SLIP and checks. | Keep layout and selected-slot proof. The existing selector parser checks two 32-byte entries, valid sequence/state/CRC and the fully erased selector case. Keep the current metadata read initially. Reading only the headers would require a separately established erased-sector rule and yields little compared with removing the app stream. |
| USB-M3 | Mainboard ESP32 → Pi5, last operation in `app_readback`, after both slot/layout checks. | One complete selected app per write. Production v0.1.4-alpha is 1,117,392 B (97.0 s 8N1 payload floor at 115,200); VDPL-054 baseline candidate is 1,118,288 B (97.1 s). Two app reads save about 194 s of wire payload time if replaced. An ordinary two-job candidate/restore pair can incur four such reads. | The guarantee is actual bytes written at the selected address, independent of FLASH's input CRC and its updater acknowledgement. Replace the bulk reply with target-computed flash digest and preserve layout, selector, exact extent, fresh MOS and the immutable host pin. Keep a full dump for a specific diagnostic, requested byte-exact qualification or preservation of an unknown artifact. |
| USB-M4 | Pi5 → classic ESP32 flash over USB, legacy writer `olimex_flash.session_operations` when a separate historical or incident procedure authorizes it. | 3,072 B pinned table and 8,192 B selector device → Pi first. A padded application (commonly 1,138,688 B) Pi → ESP32 via compressed writes at 460,800 after 115,200 ROM entry. Stock esptool then fetches a digest and the wrapper reads the same extent back again. The post-write read alone has a 24.7 s 8N1 payload floor at 460,800. Matching retry may also read a full pinned entry extent first. | Mainboard writes use FLASH in current routine work. For an expressly authorized USB incident, keep the safety metadata and actual writer, use esptool's digest evidence where it is emitted and pinned, and reserve extra full entry/readback copies for explicit proof or preservation needs. Retries must distinguish pre-dispatch failures from uncertain writes. |
| USB-M5 | Flash store/partition or unknown firmware pre/post snapshots in incident adapters, including the frozen VDPL-057 restore and Sprite R30 stock recovery. | An F060-derived VDPL-057 snapshot reads both 1,164,592 B app extents plus the 1,441,792 B store at `0x290000` and the 12,288 B layout/selector. That is 3,783,264 B per snapshot, with another full-store read after a conditional 196,608 B slot cleanup write. The basic snapshot has an 82.1 s 8N1 payload floor at 460,800 and 328.4 s at 115,200. The Sprite recovery compares the prior recorded app write extent. | These are exceptional state-preservation/attribution actions. Preserve unique mutable contents before destructive work. An already-known erased store or pinned inactive app only needs a digest if the bytes are not needed as rollback. A region outside the proposed write is an invariance check, not a default backup. Require region, purpose, and write scope in the incident packet. |
| USB-M6 | Mainboard VDP → Pi5 over passive debug/USB serial, `olimex_bench.invoke`, `olimex_vdp_ota.invoke_flash`/ `mos_witness`, `serial_monitor`, targeted capture scripts and verification-only continuations. | Serial text/markers, native diagnostics and logs, saved in host files. `Observer.receive` caps a command window at 65,536 B. A separate passive monitor is time-bounded (default 30 s, configurable up to 7,200 s), without a total byte cap, so volume depends on producer. VDPL-054's original command transcript was 450 B. | Retain the bounded command/window and native measurement records. Observe the fresh nonce/prompt and requested marker. A capture filename on the Pi does not make it a target file download. For broad/high-volume diagnostic captures, require a purpose and explicit bound. Do not substitute an open-port marker or silence for a CLI witness. |
| USB-M7 | Pi5 → CH341 modem controls in `reset_agon_usb.hold/pulse`; P4 HTTP status following release. | Zero UART file bytes. Two joined-control operations and observations; reset is an out-of-band line action. HTTP boot/input evidence is metadata. | Retain separately from byte verification. A passive open must keep joined DTR/RTS controls; ordinary pyserial separate transitions previously reset Agon. Shorter digest replies do not remove control-line risk. |

Implementation and requirements: [ordinary OTA verifier](../../../scripts/olimex_vdp_ota.py#L263), [slot parser and receipt ingestion](../../../scripts/olimex_vdp_ota.py#L113), [legacy USB writer](../../../scripts/olimex_flash.py#L53), [runner install and evidence](../../../scripts/olimex_bench.py#L709), [passive capture guide](../../serial-monitor.md), [reset implementation](../../../scripts/reset_agon_usb.py#L43), [older verified-OTA bootstrap](../BENCH-024/ota_runner.py), [ordinary FLASH policy](../../operations/olimex-bench/README.md). The legacy USB path is rejected by normal current manifested bench preflight. Treat direct and frozen incident entry points separately.

The VDPL-054 production-restore records preserve the 4,096 B sector, 8,192 B
selector, 1,117,392 B app0 and fresh MOS. The retained selector file completed
at 21:53:17.506 EST, the app readback at 21:55:01.083, and the final verification
receipt at 21:55:13.614. The interval from the selector file to the app
file was approximately **103.6 s**, including serial framing and host file
completion. FLASH announced reboot at 21:52:52.479. The first MOS proof was at
21:53:15.381, before ROM readback. These are retained file timestamps, not
instrumented wire-only time. The task silo for this timing job is VDPL-054,
and the ignored evidence path is
`build/vdpl054-olimex-v014/evidence/baseline/recover-after-run-scanline/restore-mainboard`
in the owner checkout.

A recorded BENCH-023 run at 460,800 already printed esptool's
`Hash of data verified.` before a separate block read received 4,052 B
instead of 4,096 B. Another batch hit ROM SYNC before flash access at
115,200 and a later ten-write series completed. The retained records establish
both failure stages and intermittency. They do not identify a physical root
cause, and the short block alone does not establish corrupt flash.
[BENCH-023 observations](../BENCH-023.md#repeat-the-batch-with-standalone-esptool-510).

VDPL-057's frozen adapter imports the F060 owner's `olimex_stock_startup.py`
and calls `ota_snapshot()`. The initial snapshot and candidate verification
retain both app files and the entire store at the byte counts above. The
existing diagnostic explicitly comparing app0 at 115,200 was scoped to that
app, not the store. The distinct F060 partition-transition packet reads the
table, retains or checks named affected app/store regions, and reads back
each extent it writes. Its purpose is qualifying a custom flash map.
[VDPL-057 adapter](../../../../agon-vdplet/docs/tasks/VDPL-057/prepare_olimex.py) · [F060 snapshot implementation](../../../../agon-fsim/utilities/f060-owner/olimex_stock_startup.py) · [F060 partition transition](../../../../agon-vdplet/docs/tasks/VDPL-052/OLIMEX-F060-TRANSITION-02.patch).

## P4 and external recovery USB links

| ID | Transfer and caller | Payload, frequency and cost | Purpose and recommendation |
| --- | --- | --- | --- |
| USB-P1 | P4 USB Serial/JTAG programming via `olimex_p4_app.stock/replace`, with Agon held in reset. | A separate `read-flash` for 4,096 B table at `0x8000` and 8,192 B selector at `0xf000`; then conditional retry entry read, application write, and app readback. Separate esptool commands use 460,800 nominal and can upload the small stub on their own connection (bundled esp32p4 v1 has 5,296 B text + 160 B data). | Keep port identity, table, app0 and supervised reset/boot checks. Consider having one compensated/bounded programming session once the correct P4 reset method is qualified. Native USB time is measured, not inferred from nominal baud. |
| USB-P2 | Pi5 → P4 application write, P4 → Pi post-write read in `olimex_p4_app.replace`; a joined retry can also read the production write extent first. | 1,769,472 B in the current production padded artifact, variable for candidates. The layout caps it at 7 MiB. esptool may compress the wire write. Without a known required-entry proof the regular path has no full entry read. | Full write is necessary to change P4. Stock esptool 5.1.0 already compares a target-computed digest for supported unencrypted writes. Require an explicit receiving-mode/digest verdict and exact pinned extent, then qualify using that proof or a compact follow-up command instead of the separate full read. For retry, compare target digest on the known prior extent where appropriate. |
| USB-P3 | Full factory installer outside the routine sparse phases. `flash_firmware_commit.py` stages images via SSH/SCP to Pi5; `p4_flash_remote.py` uses P4 USB then opens a console. | Whole flash backup (default 16,777,216 B), factory image write from address 0, digest-based `verify_flash` without `--diff`, then 15 s of boot text. Reset-only path has no image transfer. | Whole backup may be necessary when the authorized factory write would overwrite unknown/mutable regions. Use bounded app-only programming for routine application changes. Retain this path as explicit installation/recovery and changeset provenance, not as a standard bench fallback. Probe boot text as evidence. |
| USB-P4 | P4 → Pi5 boot console from `olimex_p4_app.reset_until_pads_release` or `native_bootstrap`. | Boot messages, no target file. Standard paired reboot caps at 4 MiB/50 s and stops at the pad-release marker. The VDPL-054 restore retained a 5,811 B P4 boot log. The older helper uses both boot lines and status polling. | Keep the pad release before the Pi releases Agon reset, plus fresh admitted boot. In any future timing change retain bounded proof rather than adding serial screenshots or payload reads. |
| USB-P5 | Diagnostic benchmark peer control in `net009_p4_peer.P4Peer`, called by `net009_pi_uart`. | P4 native USB carries STATUS, one nonce-bound ARM plus event lines, saved as `p4-usb.log`. Raw benchmark frames use Pi5 RP1 header UART0 to ESP8266 and on to a TCP peer. The header routine rejects USB ttys. | Keep the control replies for a finite diagnostic. Do not count binary benchmark traffic as P4 USB serial or add this route to ordinary commissioning. Reopening the P4 console can reset the special fixture, so its runner can lend one open handle across arms. |
| USB-P6 | Historical RESEARCH-003 app-only deployment `deploy_on_pi.py`. | P4 → Pi USB read of the first 2 MiB from address 0, then Pi → P4 candidate write at `0x20000` and `verify_flash`. | Historical state proof. The code only compares known app and partition slices of the backup. Future bounded app-only work should use a digest and the necessary table/selector metadata, and preserve unique state only if the write would overwrite it. |
| USB-R1 | Optional WROOM recovery via its own USB serial console plus eZ80 ZDI clock/data. | WROOM commissioning flashes the utility and SPIFFS containing the recovery payload and agent. The documented booted WROOM USB console is a 115,200 8N1 menu. The full MOS payload and agent subsequently cross ZDI from WROOM to eZ80, with WROOM-side CRC checks over ZDI reads. The bench policy also requires preserving the existing ROM and comparing all 131,072 B independently after the write. Default `FLASH mos` verifies through the SD path instead. | Keep the explicit exceptional recovery gate. Current P4-PC cannot stand in for WROOM. The pinned upstream menu and its ZDI CRCs do not establish an independent host dump; commission the actual read route and encoding before any recovery write. |
| USB-R2 | Historical P4 ZDI console tool `mos_recovery_console.py` and host-only `prepare_mos_recovery.py`. | Each ROM read is 131,072 B decoded, sent in 512 lines of 256 B in printable hex. At least 262,144 serial data characters per before/after dump, or 22.8 s each at 115,200 before labels, framing and the ZDI time. RESTORE is a short hash-bound command; the ROM and 90 B flash agent are embedded when building the programmer. | Historical only for current P4-PC. Retain as evidence about actual transfer inflation. A WROOM packet cannot silently use this P4 worker. |

Sources: [P4 app programmer](../../../scripts/olimex_p4_app.py), [factory worker](../../../scripts/p4_flash_remote.py), [factory launcher](../../../scripts/flash_firmware_commit.py#L316), [P4 bootstrap](../../../scripts/native_bootstrap.py), [WROOM recovery policy](../../mos-recovery.md), [historical P4 console](../../../scripts/mos_recovery_console.py), [recovery payload embedding](../../../scripts/prepare_mos_recovery.py), [rollback controls](../../procedures/rollback.md). The bound applies to the existing scripts, not an estimate for tests which have no comparable wire timing.

The specialized `capture_general_poll.py`, `capture_keyboard.py`,
`capture_uart_flow.py`, `capture_uart_roundtrip.py` and
`capture_visible_text.py` call the same passive opener and write diagnostic
console bytes to local files. Their normal observation default is 90 s, with
a 15 s prompt-on-ready variant. They do not download files through the
console. Their selected fixture deployers, when used, are a distinct SD
service operation. `modem_bw.py`, `modem_join.py`,
`modem_rx_control.py`, `modem_sniffer.py` and `run_modem_probe.py` use a
diagnostic console for commands and event logs. The throughput tests send
generated patterns on the selected modem UART and TCP data path. They are
deliberate benchmark payloads and do not justify any production copy.
[P4 peer console](../../../scripts/net009_p4_peer.py) · [RP1 header path](../../../scripts/net009_pi_uart.py) · [Historical P4 deploy](../RESEARCH-003/deploy_on_pi.py).

The WROOM source documentation describes the SPIFFS payload, USB menu and
ZDI-side CRC checks. USB preparation/image deployment and ZDI recovery are
separate links. The full independent eZ80 dump required by this bench still
needs an exact commissioned receipt. [Pinned Agon Recovery documentation](https://raw.githubusercontent.com/AgonPlatform/agon-recovery/95d68464afd049945e1dfd780c1c07621d565450/README.md).

## Compact, independently verified write receipt

The installed esptool 5.1.0 `ESPLoader.flash_md5sum(address,size)` sends
`SPI_FLASH_MD5` with the exact region. The ESP32 reads actual flash locally.
The stub replies with **16 binary digest bytes**, the classic ESP32 ROM with
32 hexadecimal characters, plus normal protocol overhead. Stock
`verify_flash(..., diff=False)` also uses the digest; `--diff` causes
a full read on mismatch and is unsuitable as an automatic fallback.
That CLI helper may pad inputs to four bytes or rewrite flash parameters.
For the current exact OTA scope, use the existing bound address and raw
extent and compute the expected digest over the same pinned release bytes.
All these details are present in the installed package's `loader.py` and
`cmds.py`. [Espressif Serial Protocol](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/serial-protocol.html#verifying-uploaded-data) · [Espressif verification options](https://docs.espressif.com/projects/esptool/en/latest/esp32/esptool/advanced-commands.html#verify-flash-data-verify-flash).

Recommended first tranche for the mainboard:

1. Keep the commissioned read-only programmer session, MAC, table, actual
   selector, expected app slot/address and exact length. Use the bundled
   target digest at that address and compare with an independently computed
   local digest. SHA-256 continues identifying the release file; record MD5
   as the actual on-device verification algorithm and do not represent it
   as a device SHA-256 or a retained full dump. This is an accidental-error
   check for an owned bench, not an authenticity claim.
2. Give the receipt an explicit method/extent and distinct success state.
   Preserve existing full-read evidence for frozen runs. Update
   `olimex_vdp_ota.installed/require_image`, inventory and handback,
   promotion scripts and incident proof consumers that require `readback`
   or its actual bytes. Older padded entry receipts use an exact raw prefix
   plus all-FF tail, so admit the existing artifacts under their existing
   contract. Never manufacture a dump, padded-prefix proof or fresh receipt
   from the expected input file alone. [Examples of strict readers](../../../scripts/olimex_vdp_ota.py#L133)
3. Bench-qualify against a known-good retained case and controlled wrong
   byte/pin, wrong slot/layout, truncated or missing digest, post-read reset
   and MOS failure. Prove no implicit reflash, retry or full read after a
   mismatch. A first matched digest can be compared with one explicitly
   commissioned full qualification capture. Keep serial traffic, elapsed
   time and first-stop stage separate in the evidence.
4. If ROM SYNC remains the blocker, investigate compact self-verification in
   the running controller or receiver as a separate tranche. This can avoid
   ROM entry but depends on a new firmware/protocol and proof of which
   partition and bytes it actually inspected. The earlier BENCH-024 verified
   receiver provides limited precedent, not capability of ordinary stock
   FLASH v1.9. A working version banner and input CRC alone are insufficient
   for independent newly written bytes or selected-slot proof.
