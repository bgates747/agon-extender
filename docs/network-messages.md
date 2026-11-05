# Experimental application network messages

The source implementation lets an admitted Agon application exchange opaque
binary records through P4 to a numeric IPv4 TCP peer. It is a matched development
interface: installation and hardware qualification are pending. It is not in the
selected production bundle. MechAgon is the first consumer; its game protocol,
JSON/WebSocket bridge and drawing remain outside Extender.

## Application ownership

Use `include/agon/net.h` from native C or the documented gateway from assembly.
Keep one zero-initialized `static agon_net_client` in ordinary application RAM
(address range0x40000 through0xAFFFF). All calls run in foreground with IRQs
enabled. Complete graphics/asset uploads before connecting. The application
owns its bounded polling loop, decisions, deadlines and exit cleanup.

1. `agon_net_begin(&client)` obtains local admission. It does not connect TCP.
2. `agon_net_submit(&client, AGON_NET_CONNECT, address, 6)` asks P4 to connect;
   address is four IPv4 octets followed by a little-endian16-bit port.
3. `agon_net_take(&client)` polls the one pending exchange;31 means not ready.
   A zero return makes status/size/data accessors valid until the next exchange.
4. SEND submits0..128 opaque bytes. ACCEPTED means stored in P4 TX queue;
   it does not prove Pi consumption or execution. BUSY means not accepted.
5. POLL returns CONNECTING, CONNECTED or one complete RECEIVED record, including
   an empty record. A received record cannot exceed128 bytes.
6. Release on completion, cancellation and fault with `agon_net_release`.
   Release revokes resident admission without waiting on TCP. EMOS application
   exit/fault cleanup also revokes local state. P4 closes an abandoned connection
   after2000ms without a valid request; there is no reconnect or replay.

A zero function result means local success.31 is local busy/not-ready,35 is
unavailable; ordinary MOS errors retain their meaning.128 reports malformed
peer response and129 query exhaustion. Treat an uncertain timeout as terminal
for that session; do not silently retry a SEND. Explicitly starting a new
connection discards old uncertain queues. A valid request refreshes the P4 lease;
the accepted experimental connect deadline is1500ms and resident exchange deadline
is250ms. These are software bounds pending physical qualification.

## Transport and gateway

EMOS retains ordinary VDU routing, physical UART serialization and packet
reception. The app library never accesses UART/GPIO. P4 console copies complete
requests to fixed mailboxes; its separate worker alone owns nonblocking TCP.
P4 has two complete128-byte slots per direction, ordered and without overwrite.
TCP framing is four-byte unsigned little-endian length plus opaque payload.
No CRC or substitute checksum is added to processor traffic.

| Field | Byte offset | Size |
|---|---:|---:|
| NM magic/version1 | 0 | 3 |
| Request kind1 CONNECT/2 POLL/3 SEND; reply sets bit7 | 3 | 1 |
| Nonzero boot-local token, high byte zero | 4 | 4 |
| Nonzero monotonic query, never wrap/reuse | 8 | 4 |
| Payload length0..128 | 12 | 1 |
| Request reserved0; reply status | 13 | 1 |
| Opaque payload | 14 | 0..128 |

Forward carrier is `23,0,0xF4,bodyLength,body`; return packet is
`0x8F,bodyLength,body`. Maximum body142 bytes. Reply statuses0..7 are CONNECTED,
CONNECTING, RECEIVED, ACCEPTED, BUSY, FAULT, CLOSED and INVALID respectively.
FAULT carries one stable reason byte:1 peer closed,2 connect failed,3 connect
expired,4 bad TCP frame,5 IO failed,6 abandoned lease expired.

The existing66-byte gateway ABI1 uses MOS0x51 (discoverable function slot0x20),
operation2, namespace `ext`, provider `net`. All names are lowercase/zero-padded;
unused/reserved bytes remain zero. Input byte0 selects the local operation:

| Local operation | Input bytes | Output capacity | Result on success |
|---|---:|---:|---|
| 0 OPEN | 1 | 4 | Token32LE |
| 1 TAKE | 1 | 142 | Complete14..142-byte response |
| 2 SUBMIT | 19..147 | 0 | Input after operation contains full forward VDU carrier |
| 3 RELEASE | 1 | 0 | Admission revoked |

EMOS validates ordinary application buffers, fixed framing and correlation;
application code validates and interprets response semantics. No application
pointer survives a call and no application callback is installed. The public
header holds request/reply storage and codec logic outside resident firmware.

## Build and evidence scope

P4 selection requires explicit `scripts/build_p4.py --network-messages` with
`p4-console`; default builds omit the endpoint. EMOS owner task INTEG-019 adds
the fixed provider to the corrected Eirene composition. NET-003 owns the matched
integration and deployment gates. Source/host checks, native compilation and
real device qualification are distinct; none selects production automatically.
