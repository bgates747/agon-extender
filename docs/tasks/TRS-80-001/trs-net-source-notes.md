# TRS-NET source pointers and initial host baseline

Source inspection: 2026-09-13. These observations apply to the pinned archives
in [reference-archives.json](reference-archives.json), obtained from Daniel Paul
Martin's [downloads page](https://danielpaulmartin.com/home/my-downloads/).
They do not identify a current guest release or establish physical compatibility.

## Source map

| Archive member | Useful starting point |
| --- | --- |
| `TRS-NET.zip` → `TRS-NET.py` | Actual Python/pyserial host server: volume selection at lines 69–83, serial setup at 107–160, read/reread at 195–237, write/rewrite at 240–289, bind/ping at 304–323, echo at 363–373 |
| `TRSDOS_7.zip` → `TRSDOS_7/SYS0_IPL/ipl_net_bind.s`, `ipl_net_ping.s`, `ipl_net_echo.s`, `ipl_net_qserv.s` | Guest startup/network utility entry points; inspect with their macro definitions before deriving framing |
| `TRSDOS_7.zip` → `TRSDOS_GLOBAL/macros/network_macros/` | Named BIND/ECHO/PING/QUERY/STATS macro sources |
| `TRSDOS_7.zip` → `TRSDOS_7/SYSRES/drivers/driver-UART1.S` | UART receive/transmit, software-controlled RTS/DTR, CTS polling and timeout handling |
| `TRSDOS_7.zip` → `TRSDOS_GLOBAL/macros/D_language_macros/D_language_UART1.s` | Actual UART1 register/bit operations behind the driver macros |
| `TRSDOS_7.zip` → `TRSDOS_7/SYSRES/drivers/driver-NETDVR.S` | A disk-driver source lead, not proof of the active Agon disk implementation; its read loop includes a commented-out UART call. Trace build inclusion and guest revision before treating it as the matching peer. |

The host script SHA-256 is
`f45b34e0b9899b06d04ed67c045ccc9d624c8a5a4f60c5ef712ce555a8d1665b`.
Archives remain on the Linux reference host. The probe reads the script directly
from the ZIP without unpacking or changing its bundled media.

## What the host server actually does

1. The backing file begins with a 256-byte header. Sector N starts at
   `256 + 256*N`. The script opens that file with `rb+`; this is not a directory
   exported through MOS FatFS and is not Extender's mainboard SD endpoint.
2. `@ping\n` returns `@pong\n`. `@bind\n` returns `@bound\n` followed by the
   256-byte volume header. `@echo\n` followed by 256 bytes returns those bytes.
3. `<` plus five decimal digits and newline requests a sector; backslash uses
   the reread branch. Both return the sector bytes followed by their sum modulo
   256 encoded as a four-byte big-endian integer. This is not Extender CRC32.
4. The server's default selection requests 115200 baud, eight data bits, one
   stop bit, RTS/CTS and a one-second pyserial read timeout. The source's
   configuration request is distinct from measuring an actual UART connection.
5. The host probe in [TRS-80-002](../TRS-80-002.md) runs this unchanged script
   with simulated serial input and a generated temporary volume. Six exact-reply
   cases pass; that only establishes this small host read/control baseline.

## Integration constraints exposed by this snapshot

1. **Host portability.** The default directory strings use Windows backslashes,
   and port selection takes the first five characters of `str(port)`. A Linux
   `/dev/...` name cannot be passed through that selection intact. The probe
   supplies an explicit temporary directory and a five-character synthetic
   port name; it does not fix or validate real host-port discovery.
2. **Writes need separate work.** In the normal write branch, checksum comparison
   is commented out and the file is written after the server returns its own
   calculated checksum. The rewrite branch references undefined `chksum1`.
   Fixed-size serial reads are not checked for short returns. These are source
   observations, not results of a physical corruption test; the sample probe
   sends no writes and makes no durability claim.
3. **No guest pairing yet.** The older source archive's UART routines and disk
   driver must be reconciled with the loader/OS binaries actually used by the
   community. Having source names is not sufficient evidence of a matching
   build. No bootable volume, new guest driver or P4 relay is produced here.
4. **Preserve upstream terms.** The host script displays Daniel's attribution
   and a conditional copying/distribution notice. The OS source archive also
   contains a proprietary-source notice in
   `TRSDOS_GLOBAL/copyright_messages.s`. Record the intended upstream terms
   before selecting code for vendoring; the Extender license cannot settle
   those terms. The sample kit contains only our probe and requires the user
   to supply the unmodified upstream archive.

TRS-80-001 remains the design task for resolving these boundaries. This note
does not select a transport or create a second implementation backlog.
