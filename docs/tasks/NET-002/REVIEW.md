# Networking prior-art review

## Decision brief

Research completed 2026-09-23; implementation remains unapproved. No bench,
firmware or network-service changes were made. Community reports are not our
qualification results. Exact revisions are in [SOURCES.json](SOURCES.json).

**Keep our SD listener and recovery protocol. Borrow PerryZi's AT compatibility
knowledge for a separately scoped P4 network-service proposal.** GET/ZGET solve
Agon-initiated downloads; they do not replace host-initiated directory browsing,
uploads and recoverable file replacement. This review therefore informs
[REMOTE-005](../REMOTE-005.md), but does not block its independent UI/session work.

| Rank | Candidate and value | Concrete reuse and owner | Adaptation / limit | Next bounded validation, if approved |
|---|---|---|---|---|
| 1 | Preserve existing SD service; improve human access | Host client and P4 HTTP entry point retain existing EMOS/sdserve transactions | No new AT parser, TCP stack on eZ80, or replacement transfer engine needed | Restart/reconnect, interrupted transfer, directory paging, retained backup and CRC checks |
| 2 | PerryZi AT compatibility for existing Agon network applications | P4 could reuse MIT compatibility parsing/response idioms; P4 owns sockets; EMOS owns admission and transport | Arduino ESP8266 WiFi/socket calls must become P4 Ethernet calls. EMOS virtual UART versus adapted client API is unresolved; raw UART1 is not available | One TCP client, one UDP client; split replies, NUL/CR/LF/XON/XOFF payloads, timeout/close, simultaneous keyboard traffic |
| 3 | Agon-initiated HTTP fetch/catalog | Zimodem/PerryZi HTTP offload and GET catalog workflow; P4 fetches, EMOS-approved foreground client writes SD | Adopt an explicit offset/length/integrity contract; do not copy GET/ZGET storage loops unchanged | Binary corpus, truncation, retry after lost response, full destination verification |
| 4 | Snail as compatibility client | Assembly network adapter is relatively isolated; reuse application/interface idioms with attribution | Passive AT receive framing and 1.x response syntax matter; no whole-client compatibility proven | Fetch text and binary gopher content over a controlled peer |
| 5 | Diagnostics | Reuse command coverage and presentation ideas | Names do not imply full Unix semantics; licenses of individual Radiotux utilities need confirmation before copying | Check actual result ownership and failure reporting against controlled TCP/DNS/UDP endpoints |
| Defer | SLIP/PPP and whole modem port | Useful examples of serial framing and negotiation | Host requires its own IP/TCP stack. ESP8266 network hooks are not a drop-in P4 service and conflict with assuming ordinary shared modem traffic | Separate architecture proposal only if an identified application needs host-owned IP |

## What is actually implemented

### PerryZi and Zimodem

PerryZi 1.2.4 is one ESP8266 firmware source with target-specific builds. The
AGONLIGHT target selects Generic ESP8266, 115200 baud and Espressif 1.7.6 response
conventions. Its default non-Agon AT version differs. The README identifies a
21 July 2026, pre-4.0.3 Zimodem fork; an exact fork-point commit has **not** been
established. The separately pinned current Zimodem checkout is a reference, not
an asserted ancestor. This uncertainty blocks wholesale provenance claims, not
review of the separately attributed AT module.

The MIT `espressif.h`/`.ino` pair explicitly describes a new implementation from
published AT interfaces, not copied Espressif internals. It distinguishes 1.x
and 2.x passive-receive delimiters, suffixes, DNS formatting and error strings.
It supports one TCP/UDP connection (`CIPMUX=0`), not multiplexed sockets, TLS or
IPv6. Socket state is separate from Zimodem's packet engine. `CIPSEND` captures
an exact payload length before the line parser; the header declares a 2048-byte
send maximum, 10-second send timeout, 64-byte I/O chunks and 1460-byte IPD maximum.
These are inspected implementation limits, not measured throughput.

The general serial layer includes RTS/CTS and software flow-control modes;
that does not establish that a particular Agon cable/application enables them.
Binary send capture must precede interpretation of control bytes. Porting just
command spelling without these state transitions would not preserve compatibility.

AT socket mode: eZ80 application → MOS UART1 calls → ESP8266 AT parser → ESP8266
TCP/UDP socket stack → remote server. ESP8266 owns networking; eZ80 owns application
parsing and SD writes. Snail uses MOS UART wrappers, not a separate network stack.

SLIP/PPP mode is a different contract: the attached host supplies IP packets and
needs IP/TCP above the serial link. ESP8266 forwards them and hooks WiFi receive
traffic addressed to its own IP back to the serial host. This is not evidence of
a general NAT router or a ready-made Agon sockets API. PPP source implements FCS,
LCP and IPCP handling; the reviewed dispatch handles IP/LCP/IPCP, not PAP/CHAP.
Its LCP negotiation is small (including acknowledgement of supplied options), so
protocol completeness must not be inferred. Network hooks assume ESP8266/lwIP
packet layout. Neither PPP interoperability nor the proposed Discord LCP test
was validated here. Arduino ESP8266, WiFi/client/server, filesystem/serial support
and lwIP internals are dependencies; no reproducible dependency lock/build was
qualified during this source review.

### GET and ZGET: useful workflow, unsuitable replacement engine

GET's Python server pages files in 32 KiB portions using implicit per-client
progress. It advances progress before successful delivery is established; it
is not explicit-offset HTTP Range recovery. The first response has HTTP headers;
later portions use its custom convention. The C client has a 64 KiB receive array,
plus catalog and write buffers. Unchanged, that allocation alone excludes a
32 KiB MOSlet. GET opens/truncates the final destination and does not check every
write/close result or establish end-to-end CRC integrity.

The earlier GET concern is supported by source inspection: after skipping HTTP
headers, the first-page path resets an IPD parser that expects a fresh `+IPD,`.
For a response whose header and body share one IPD payload, the initial body
has no new IPD prefix and can be skipped. Control-byte skipping is also unsuitable
for arbitrary binary data. **This is a conditional source finding, not a newly
reproduced hardware failure.** Its README's throughput claim is not our benchmark.

ZGET offloads HTTP fetching with `AT&G`; it selects `ATS45=3` (normal binary,
no checksum in the inspected PerryZi enum) and `ATS44=10` (serial delay).
It also has a 64 KiB receive array. The client waits for a closing header bracket,
then discards bytes <=32 before accepting payload, which can drop valid leading
binary bytes. Completion messaging is not conditional on full verified length;
write results are unchecked. These source findings contradict treating the
README's bit-perfect wording as qualification. Offload and fewer per-page command
round trips plausibly explain the reported speed advantage; no comparable timing
or file-integrity evidence accompanies the transcript. Do not publish a speed ratio.

### Other applications

| Application | Inspected behavior | Qualification / reuse constraint |
|---|---|---|
| Snail | eZ80 assembly gopher/local-file browser; passive AT receive; MOS UART API | Coffee-ware attribution; useful isolated transport code, no P4 run here |
| Telnet (Sijnstra) | README recommends AT 1.7.x/115200; optional SSL and reconnect | Candidate matching transcript description, exact binary not identified by speaker. Source absent from its reviewed directory; README reports throughput crashes and no universal exit. PerryZi lacks its SSL path |
| ntpsync | Sends NTP packet using AT UDP socket | eZ80 owns NTP payload and clock update; no independent release qualification here |
| ping | Tries TCP connections to fallback ports | Not an ICMP echo implementation |
| route | Queries `CIPSTA?` | Displays configuration, not an editable routing table |
| arp | Queries own MAC/IP using `CIPSTAMAC?` / `CIPSTA?` | Not a neighbor-cache interrogation |
| ifconfig | Queries interface addresses | Transcript says ipconfig; exact named artifact unresolved; closest repository tool is ifconfig |
| nslookup | Delegates `CIPDOMAIN` | ESP8266 owns DNS resolution |

## Extender integration boundaries

The [existing SD contract](../../mainboard-sd.md) already provides directory
listing, explicit-offset reads and staged writes with integrity/recovery behavior.
P4 receives host requests; EMOS owns the Extender link; foreground sdserve owns
MOS filesystem calls. The provisional MOSlet does not make this a background
filesystem service during arbitrary games, and its admitted Legacy/input conditions
remain unchanged. See the [earlier comparison](../REMOTE-005/FEATURE-COMPARE.md).

Official MOS documents `mos_uopen`/`mos_ugetc`/`mos_uputc` as UART1 operations,
including interrupt-handler setup. Those are not a generic sockets interface.
Extender already uses that physical link for keyboard/display/service traffic;
a modem client cannot seize it while retaining those services. Any compatibility
adapter must preserve EMOS routing/admission, with P4 owning network sockets and
bounded queues. Unmodified-client compatibility would require a separately
reviewed virtual UART interface, including baud, blocking reads, close semantics
and clients which bypass MOS. An adapted application-side transport is a smaller
alternative, but is an Author decision, not a change made by this review.

Do not move a large AT interpreter into EMOS ROM. Current provisional MOSlet
results record only 16 bytes remaining in that candidate; this is a specific
build result, not a forecast. Code-size, heap and scheduling costs of P4 adaptation
are unmeasured. Neither Legacy nor ExCom support for new modem clients is proven.
WiFi setup commands need truthful Ethernet semantics, rather than fake successful
configuration. File access UX can advance independently of that compatibility work.

## License and evidence limits

PerryZi: Apache-2.0 plus MIT per-file components; preserve NOTICE and exact headers.
Zimodem: preserve its license/third-party notices; no whole-tree import proposed.
GET: GPL-3.0-or-later README, source header GPLv3. ZGET and individual diagnostics:
no license grant assumed merely because adjacent GET is GPL; resolve before copying.
Snail: custom coffee-ware permission/attribution. Sijnstra repository: MIT, but
Telnet source is not published in the inspected directory. No code was copied
into production, no upstream bugs filed, no firmware built and no speed measured.

Outstanding choices are which application/workflow to prioritize, whether to
adapt clients or provide virtual UART compatibility, and which transfers may
coexist with display traffic. None is needed to complete this research tranche.

## Pinned source navigation

- [PerryZi target and dependencies](https://github.com/SanPollo/PerryZi/blob/ec165814cd9a1b140aff65ac0786eac1a0b1a414/perryzi/perryzi.ino)
- [AT contract](https://github.com/SanPollo/PerryZi/blob/ec165814cd9a1b140aff65ac0786eac1a0b1a414/perryzi/espressif.h)
- [AT implementation](https://github.com/SanPollo/PerryZi/blob/ec165814cd9a1b140aff65ac0786eac1a0b1a414/perryzi/espressif.ino)
- [PPP](https://github.com/SanPollo/PerryZi/blob/ec165814cd9a1b140aff65ac0786eac1a0b1a414/perryzi/zpppmode.ino)
- [SLIP](https://github.com/SanPollo/PerryZi/blob/ec165814cd9a1b140aff65ac0786eac1a0b1a414/perryzi/zslipmode.ino)
- [Serial flow control](https://github.com/SanPollo/PerryZi/blob/ec165814cd9a1b140aff65ac0786eac1a0b1a414/perryzi/serout.ino)
- [S-registers](https://github.com/SanPollo/PerryZi/blob/ec165814cd9a1b140aff65ac0786eac1a0b1a414/perryzi/zcommand.ino)
- [Binary formats](https://github.com/SanPollo/PerryZi/blob/ec165814cd9a1b140aff65ac0786eac1a0b1a414/perryzi/zcommand.h)
- [GET client](https://github.com/Radiotux/Agon-Software/blob/e265db1de57c49142420324945c666049dc1ec53/get/src/get.c)
- [GET server](https://github.com/Radiotux/Agon-Software/blob/e265db1de57c49142420324945c666049dc1ec53/get/agon_server.py)
- [ZGET client](https://github.com/Radiotux/Agon-Software/blob/e265db1de57c49142420324945c666049dc1ec53/zget/src/zget.c)
- [Snail network adapter](https://github.com/nihirash/agon-snail/blob/66071373943a34024e38214b6d8346316b2ddce6/src/transport/network.inc)
- [Telnet documented limits](https://github.com/sijnstra/agon-projects/blob/ed135a709fc398929943658e7dbf1f1a2c28212c/telnet/readme.md)

Official MOS UART contract: [API reference](https://github.com/AgonPlatform/agon-docs/blob/f9806bd3cbff6ed5d1c08bef1d51fed11764b86b/docs/mos/API.md#mos_uopen). Source paths and revisions above distinguish inspected behavior from transcript claims.

Additional pinned sources: [claim inventory](CLAIMS.md).

- [ntpsync implementation](https://github.com/Radiotux/Agon-Software/blob/e265db1de57c49142420324945c666049dc1ec53/ntpsync/src/ntpsync.c)
- [ping implementation](https://github.com/Radiotux/Agon-Software/blob/e265db1de57c49142420324945c666049dc1ec53/ping/src/ping.c)
- [route implementation](https://github.com/Radiotux/Agon-Software/blob/e265db1de57c49142420324945c666049dc1ec53/route/src/route.c)
- [arp implementation](https://github.com/Radiotux/Agon-Software/blob/e265db1de57c49142420324945c666049dc1ec53/arp/src/arp.c)
- [ifconfig implementation](https://github.com/Radiotux/Agon-Software/blob/e265db1de57c49142420324945c666049dc1ec53/ifconfig/src/ifconfig.c)
- [nslookup implementation](https://github.com/Radiotux/Agon-Software/blob/e265db1de57c49142420324945c666049dc1ec53/nslookup/src/nslookup.c)
