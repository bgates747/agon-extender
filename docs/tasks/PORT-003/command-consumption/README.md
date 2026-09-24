# UC01 — Unavailable-command consumption inventory

## Executive summary

The selected P4 parser still reaches an **empty firmware-updater handler**:
its subcommand and payload can become ordinary VDU bytes. A separate confirmed
source-level gap is **virtual-key query &99**: its byte is consumed, but the
unavailable keyboard object never injects the expected reply event. Mouse
commands consume their fields; several reply obligations need disposition.
Audio framing is already repaired. No handler was changed or firmware tested
in this inventory. The next recommended chunk is UC02/UC03 contract work,
starting with updater consumption and explicitly separating interactive transfers.

## Coverage and identities

1. Official source: Agon VDP v2.16.0,
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`, verified clean/tagged. Official
   docs at `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`: `System-Commands.md`,
   `VDU-Commands.md`, `Enhanced-Audio-API.md` under `docs/vdp/`. Documentation
   alone does not specify updater or all maintenance handshakes; source resolves
   them below. Paths naming `video/` refer to that official tree unless prefixed
   `vdp/`, which denotes the project copy.
2. Installed candidate: `uart-excom-console-r22-b2026-09-15-07-01-47Z`.
   All 45 inspected headers/adapters/entry points and selection fingerprints
   match its archived source, recorded in [source-review.json](source-review.json).
   The archive contains a `vdp/` root; the comparison was corrected to use it.
   This is a bounded manual reachability review, not a newly compiled call graph.
3. `p4_console.cpp` defines processed-keyboard and console binding, includes
   `p4_browser_vdp.cpp`; retained `video.ino` and `vdu_stream_processor.h` reach
   `vdu.h`, `vdu_sys.h`, buffered/fonts/sprites/context/layers dispatch. `vdu.h`
   includes the repaired audio parser despite the older selector's audio exclusion
   claim. The declaration drift remains recorded, not silently regenerated.
4. The three unavailable adapters are audio, input and maintenance. Console/
   terminal overrides in `video.ino`, printer output, and feature-gated retained
   branches were also reviewed. Retained bitmap, sprite, font, buffered, copper,
   layer, viewport and screen-query code is functional code, not blanket stubs.
   RTC uses retained ESP32Time; processed keyboard FIFO/layout state is functional.
   This inventory does not claim every graphics operation is fully qualified.
5. Wire values below use decimal unless prefixed `&`; u16/u24/u32 are little
   endian. Packet notation denotes stock `send_packet` framing: code+&80, length,
   payload. EMOS remains route/reply authority.

## Command inventory

| ID | Command and exact ordinary-stream grammar | Current P4 behavior / reply | Disposition |
|---|---|---|---|
| C-AUDIO | `23,0,&85,channel:u8,op:u8,args` | Retained dispatcher consumes known grammar; unavailable backend returns failure. Packet &85 length2: channel,status, except documented no-reply branches | Already repaired; preserve all conditional lengths in linked audio table |
| C-BELL | `7`, no operands | Calls unavailable playNote; no reply | Safe framed no-op |
| C-UP0 | `23,0,&A1,0` + six bytes (`unlock` for successful stock unlock) | P4 reads **none** of subcommand/payload. Stock reads6 then compares; no VDP reply packet, only displayed diagnostics | Confirmed consumption defect |
| C-UP1 | `23,0,&A1,1,size:u24,data[size],checksum:u8` | Same empty P4 handler. Stock locked-updater path already discards size+1 after reading size; unlocked path attempts OTA | Retain locked/failure-style consumption without OTA; freeze contract before code |
| C-UP2 | `23,0,&A1,2`, no further bytes | P4 even leaves selector2; stock switches/reboots only if unlocked, no packet | Consume selector, preserve unavailable execution |
| C-UP? | `23,0,&A1,unknown:u8` | Stock consumes selector only; P4 does not | Do not invent unknown payload lengths |
| C-HEX | `23,28` followed by selector timeout (not a fixed trailing byte) | Empty adapter; stock starts external USB/debug-UART Intel HEX session | Not an inline HEX payload. Separate abort/release contract required |
| C-YRX | `23,28,1` | Empty adapter; stock sends keyboard-packet byte `C`, receives external YMODEM files then hands them to MOS | Caller may wait forever; interactive endpoint contract required |
| C-YTX | `23,28,2` | Empty adapter; stock sends `C`, receives MOS file records, then external YMODEM transmission | No bounded total length immediately after selector; separate contract |
| C-TERM | `23,0,&FF`, no operands | P4 stays Disabled; no reply | Entry framed, subsequent terminal bytes not promised safe VDU payload; deferred with [serial printer/console bucket](printer.md) |
| C-CONSOLE | `23,0,&FE,n:u8` | n consumed; consoleMode forced false; no reply | Framed no-op; preserve ExCom route; deferred with [serial printer/terminal bucket](printer.md) |
| C-PRINT | `1,char:u8`; `2` on; `3` off | Retained parser consumes fields, writes DBGSerial when enabled. P4 skips DBGSerial.begin; output is unavailable/unqualified, not a proven bounded discard sink | No framing gap identified; retain intended debugging output, research/implementation deferred ([details](printer.md)) |
| C-KLAY | `23,0,&81,layout:u8` | Logical layout/native console update retained; no direct reply | Supported state; no blanket stub |
| C-KSTATE | `23,0,&88,delay:u16,rate:u16,LEDs:u8` | Reads all5 bytes; retained logical state/ranges, packet &88 length5 delay,rate,LEDs | No physical LED/repeat-generation claim; preserve reply |
| C-KQUERY | `23,0,&99,virtualKey:u8` | Reads key, but isVKDown returns false and injectVirtualKey does nothing; no event | Confirmed missing requested key reply; normal stock event packet &81 length4 keycode,modifiers,VK,down |
| C-MOUSE | `23,0,&89,op:u8,args` | Retained parser, absent physical backend; see subcommands below | Framing complete; reply/availability issues separate |
| C-MCURSOR | `23,27,&40,hotX:u8,hotY:u8` | Reads both; current bitmap lookup retained, makeMouseCursor empty; no reply | Safe consumption; no physical cursor creation |
| C-VARS | `23,0,&F8,id:u16,value:u16`; `&F9,id:u16` | Reads full fields before variable dispatch; mouse/keyboard adapters may receive updates. Some variables enqueue packets | Preserve logical state and event semantics; do not discard whole variable command |

### Updater research and current deferral

C-UP0/C-UP1/C-UP2/C-UP? are deferred, including discard-only changes.
[Updater research](updater.md) records agon-flash v1.9's actual &A1 use,
screen-readback dependency and future P4 update requirements. The Author now
intends revisiting functional EDP updating near production; current applications
do not use it. This supersedes the recommendation to work on updater consumption
next, without claiming the existing empty handler is safe.

### Audio grammar (existing authority)

Use [PORT-004's complete opcode/action/envelope table](../../PORT-004/audio-framing/PLAN.md#grammar-and-implementation-policy)
for opcodes0–14, sample actions0–8/16, optional sample format/rate, variable
sample lengths, envelope counts, unknown-command behavior and exact statuses.
The stock `vdu_audio.h` dispatcher and selected unavailable backend are included
in the source fingerprint. The 64-byte sample sink avoids payload-sized
allocation. This inventory also includes bell7, which has no payload or reply.
The existing audio evidence is not a new test run or a synthesis claim.

### Mouse subcommands

Lengths exclude the common `23,0,&89,op` prefix. Owner is retained
`vdu_sys_mouse` in `vdp/video/vdu_sys.h`. Mouse packets are &89 length10:
x:u16,y:u16,buttons:u8,wheel:u8,deltaX:u16,deltaY:u16. Events are queued and may
coalesce; do not promise one packet per nested buffered command.

| op | Fields | Selected behavior and queued reply |
|---|---|---|
|0 enable |none | enable fails; zero-delta variable writes still queue mouse event |
|1 disable |none | disabled state; zero-delta writes queue event |
|2 reset |none | reset fails; zero-delta writes queue event |
|3 cursor |cursor:u16 | absent mouse means cursor selection skipped; zero-delta writes queue event |
|4 position |x:u16,y:u16 | logical cursor adapter/clamping and zero deltas queue event |
|5 area |x:u16,y:u16,x2:u16,y2:u16 | stock itself reads then does nothing; no event |
|6 sample rate |rate:u8 | adapter false; success-only event skipped |
|7 resolution |resolution:u8 | adapter false; success-only event skipped |
|8 scaling |scaling:u8 | adapter false; success-only event skipped |
|9 acceleration |acceleration:u16 | adapter false; success-only event skipped |
|10 wheel acceleration |acceleration:u24 | adapter false; success-only event skipped |
|unknown |none known | selector consumed; no invented payload or reply |

System-Commands.md says mouse data follows all these commands. Stock source
itself contradicts that for area and failure paths. UC03 must disposition this
before any new reply behavior; do not automatically invent successful mouse
availability. Physical motion acquisition and actual cursor creation remain absent.

## Interactive maintenance contracts

These are two endpoints, not an arbitrary file blob embedded in VDU traffic.

1. **Intel HEX:** stock `hexload.h` reads colon-marked ASCII records from
   DBGSerial, not the VDU input stream. Records have byte count/address/type,
   data and checksum; extended format adds its own acknowledgments/checksums.
   On the VDU/MOS side it sends PACKET_KEYCODE length2 `{byte,0}` records,
   optionally waiting for a raw acknowledgment byte. Data records carry1,
   address24, count8, data then consume MOS checksum feedback; EOF/abort sends0
   with acknowledgment. See `sendKeycodeByte`, `consumeHexMarker`,
   `vdu_sys_hexload` and the official VDU-Commands.md internal-record contract.
   The dispatcher selects HEX only after the next-byte timeout; a following
   ordinary VDU byte can be consumed as a selector. This is inherited ambiguity,
   not permission to guess its intended boundary.
2. **YMODEM common:** `MOS_YmodemSession::open` sends keycode byte `C`;
   close sends0. Each emitted byte uses PACKET_KEYCODE length2, distinct from
   ordinary key events. `receiveKeycodeUINT32` reads four raw VDU-stream bytes.
3. **Transmit from MOS:** after selector2/open, `readFiles` loops over count:u32;
   zero ends the list. Each nonzero count record reads filenameLength:u32,
   filename bytes, fileSize:u32, file bytes and CRC32:u32. Count is a record
   presence value here, not a loop count. Only then does stock send external
   YMODEM blocks and await external ACK/NAK/CAN responses.
4. **Receive to MOS:** selector1/open starts external YMODEM acquisition. After
   external file completion, `writeFiles` sends byte1, nameLength:u32, name,
   size:u32 and waits for raw `S1`; chunks send2,length:u32,data and await `S2`;
   CRC phase sends3,CRC32 and awaits `SV`; completion sends4 and awaits `S4`.
   Close sends0. No complete MOS payload length exists at entry.
5. **External YMODEM framing:** stock `ymodem.h` owns SOH/STX128/1024-byte
   blocks, sequence/complement, CRC16, EOT and cancellation/retry handshake.
   That external stream is not the selected ordinary ExCom ingress. Do not drain
   hypothetical external bytes from the MOS stream. Choosing immediate0 as an
   unavailable release needs caller-side review; it is a proposal, not yet a
   proven compatible rejection. Do not send `C` unless the ensuing protocol
   has an implemented owner.

## Inherited gates and exclusions

The unavailable-maintenance header's old comment calls these references
unreachable. That was a Gate-F assumption; live `vdu_sys` proves it stale.
The source remains unchanged during this inventory.

Stock feature-gated affine &96 and copper &C4 can return before consuming later
fields when their test flag is off. This is inherited behavior, not a newly
unimplemented P4 backend; record rather than silently repair it. Reserved/unknown
VDU commands have no general length envelope. A timed-out partial command cannot
be resynchronized reliably by scanning for a byte that resembles a command.
RTC, normal graphics/buffers, processed key events and EMOS transport controls
must not be disabled by a generic discard layer. ZDI/updater physical tools are
not selected stock maintenance backends in this console; project recovery tools
remain separate and were not exercised.

## Next decisions and evidence limits

1. Author scope update (2026-09-19): updater and HEX/YMODEM operations are
   strictly Legacy-only; no EDP functionality is planned. UC02/UC03 concerns
   accidental-delivery containment only for these families. The earlier proposed
   updater discard grammar remains a candidate, not an approved implementation:
   consume selector, six-byte unlock payload,
   or u24-sized body plus checksum with bounded storage; never flash/reboot or
   claim update success. Unknown selectors consume only themselves as stock.
2. Decide key-query reply semantics using actual processed-key state; neither
   silence nor fabricated key-up should be mistaken for compatible behavior.
3. Review unavailable mouse replies. Treat interactive loader handling only as
   unsupported-command containment, not an EDP transfer-session implementation. Preserve existing correctly consumed commands.
4. Add deterministic sentinel/reply tests only after those contracts are frozen.
   This source audit alone does not establish runtime timeouts, memory bounds,
   call-site behavior of all client programs or hardware qualification.

This completes UC01's selected unavailable-function inventory. UC02–UC07 remain
open; existing audio work is retained as scoped prior evidence. No runtime code,
mainboard/Extender firmware, startup or benchmark was changed. Notify and stop.

Hardware voice notification completed with a fresh audio_commands=pass receipt;
original startup reverified unchanged; SD service exited to Legacy MOS.
Human hearing is separate. All changes committed locally; no push.

## Firmware bug register cross-reference — 2026-09-20

[FWBUG-006](../../../firmware-bugs.md#fwbug-006). These stable bug identities supplement the original
finding IDs and evidence. Registration does not authorize repairs or turn
source-only findings into hardware reproductions. Use the same FWBUG ID for
any future dedicated disposal task; current dispositions remain in the register.
