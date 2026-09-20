# Firmware updater &A1 — research and deferral

## Author disposition — 2026-09-20

Leave these handlers unchanged for now, including proposed discard-only repairs.
The application software presently under test does not use them. Revisit near
production for functional P4 EDP firmware updating from Agon SD, rather than
assuming permanent no-op handling. Present supported operation remains Legacy
mainboard VDP only; no ExCom updater support or safe containment is claimed.
This does not authorize flashing, partition changes or implementation now.

## Exact references

1. [agon-flash v1.9 main.c](https://github.com/AgonPlatform/agon-flash/blob/e670b5bd910dfe372c29aa9e896e6c24cc8530ec/src/main.c),
   commit e670b5bd910dfe372c29aa9e896e6c24cc8530ec: `vdp_ota_present`,
   `getCharAt`, `update_vdp`.
2. [agon-flash transfer assembly](https://github.com/AgonPlatform/agon-flash/blob/e670b5bd910dfe372c29aa9e896e6c24cc8530ec/src/flash.asm):
   `startVDPupdate`, `sendstartsequence`, `sendsize`, `senddata`, `sendchecksum`.
3. [Official VDP v2.16.0 updater](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/updater.h):
   `vdu_sys_updater`, `unlock`, `receiveFirmware`, `switchFirmware`.
4. Local selected stub: `vdp/video/extender/maintenance/unavailable_maintenance_adapter.hpp`.
   The adjacent command inventory records C-UP0/C-UP1/C-UP2/C-UP?.

## What the utility actually does

Jeroen Venema's agon-flash uses the &A1 commands; it does not supersede them.
The eZ80 program reads firmware from the Agon SD card and emits ordinary MOS
VDU output. On stock hardware MOS sends those bytes over UART to mainboard VDP;
VDP owns writing its own ESP32 flash. This is distinct from the utility's MOS
update path, which writes eZ80 flash.

| Command | Stock function and wire contract |
| --- | --- |
| `23,0,&A1,0` | Unlock: six literal bytes `unlock`, without a terminating NUL |
| `23,0,&A1,1` | Receive firmware: little-endian 24-bit length, image bytes, one checksum byte |
| `23,0,&A1,2` | Select alternate firmware partition and reboot if unlocked; no payload |

`vdp_ota_present()` sends the unlock command and reads characters from screen
row 3, starting at column 8, looking for `unlocked!`. Thus compatibility with the
unmodified utility includes displayed status and character-readback semantics,
not just accepting an image stream. These coordinates and text are observed
implementation dependencies, not a new protocol design.

`startVDPupdate()` sends selector 1 and the size, reads the SD file in 1,024-byte
chunks via MOS, and streams them via MOS output. It sends the two's complement
of the sum of image bytes modulo 256. Stock checks that the sum including this
byte is zero. This byte checksum is not a cryptographic image authenticity check.

Stock `receiveFirmware()` uses the ESP OTA API and an alternate application
partition. When locked, it discards the advertised image length plus checksum.
On its successful path it selects the updated boot partition and reboots itself;
the utility therefore need not issue selector 2 for that update. Selector 2 is
a separate switch/reboot operation. Stock also disables hardware sprites/cursors
during updating. None of this establishes P4 partition or renderer compatibility.

## Future implementation boundary

1. P4 EDP would receive a P4-compatible application image through EMOS-owned
   routing and perform its own update. Explicit target selection must prevent
   confusion between mainboard VDP and Extender EDP; ExCom must not silently
   forward maintenance requests to mainboard VDP.
2. Review P4 partition layout, image size/chip validation, OTA lifecycle,
   interrupted-write handling, boot validation/rollback and recovery before code.
   Reuse applicable upstream logic; do not assume the ESP32 layout or a merged
   factory image is a suitable P4 OTA application image.
3. Verify the utility's unlock display/readback dependency, transfer flow control,
   checksum, reboot/readiness behavior and EMOS keyboard readmission end to end.
4. Keep USB programming/recovery available. Users of this SD update path would
   not need Arduino/PlatformIO on a separate computer, once a compatible updater
   was installed. This is a proposed capability, not currently implemented.
5. Preserve the known empty-handler consumption defect until this work resumes;
   deferral is not evidence of safe accidental-command handling. HEX/YMODEM
   remain separately deferred Legacy-only facilities.
