# Mainboard SD service wire contract

Protocol major 1, initially frozen on 2026-09-12 in commit 51917e6. This is the
maintained contract for the EMOS-owned gateway, P4 service and foreground
`sdserve` application. The unchanged candidate combination passed the scoped
physical acceptance on 2026-09-13 UTC; see the
[acceptance record](../qualification/mainboard-sd/2026-09-13.md) and
[operating guide](../mainboard-sd.md). Record contract revisions before changing
the wire layout. Artifact lifecycle/release status is separate from that result.

## Actors and ownership

1. The developer host initiates operations through P4 Ethernet HTTP. P4 owns a
   single outstanding request and a retained last result. Its HTTP handler only
   copies bounded messages into the service queue; it never writes UART.
2. The existing P4 console process is the sole UART1 owner. It multiplexes the
   service with stock keyboard traffic at whole-packet boundaries, prioritizing
   pending keyboard events. RTS/CTS remains enabled at 1152000 8N1.
3. EMOS owns the resident gateway service, `ext.sdlink`, behind the existing
   gateway ABI. It admits the foreground ordinary application or supported
   `ext.sdlink` MOSlet caller only in Legacy with Extender
   keyboard selected and healthy. It does not select ExCom, disable input or
   expose UART registers/interrupt vectors. It resets application admission on
   application entry/exit, transport fault and explicit close.
4. The `sdserve` eZ80 application/EMOSlet owns file operations in foreground context.
   EMOS does not run a filesystem server in its ISR. Normal Rally execution
   does not include this service; first qualification occurs at the MOS CLI.
5. P4-local SD and onboard VDP are not endpoints. Stock VDP firmware remains.

## Packet layout

All integers are unsigned little endian. Maximum record length 240 bytes;
header 20 bytes, payload 0..220 bytes. No native C structure packing on wire.

| Offset | Width | Meaning |
| --- | --- | --- |
| 0 | 2 | ASCII SD |
| 2 | 1 | Protocol major, 1 |
| 3 | 1 | Kind: 1 request, 2 response, 3 service presence |
| 4 | 4 | Nonzero session ID chosen by host; presence uses application boot ID |
| 8 | 4 | Request sequence; starts at 1, strictly increases, no wrap within session |
| 12 | 1 | Operation |
| 13 | 1 | Status; zero in requests |
| 14 | 2 | Payload length |
| 16 | 4 | CRC32/ISO-HDLC of header bytes 0..15 followed by payload |
| 20 | variable | Payload |

CRC starts FFFFFFFF, reflected polynomial EDB88320, final XOR FFFFFFFF. Empty
payloads remain CRC protected. Validate full length/magic/version/kind before
queueing or interpreting an operation. CRC is corruption detection, not sender
authentication. The service is deliberately launched on this development LAN;
it is not an Internet-facing file server.

EMOS -> P4: private owned envelope `23,0,F6,length,record`. P4 -> EMOS:
`8D,length,record`. F6/8D are local Extender service selectors, never sent to
stock onboard VDP. Existing F7 console control, 81 keyboard, 88 settings and
8C/QTG diagnostics retain their meanings. No file bytes become keyboard events.
An incomplete envelope has a 250ms total assembly deadline. No interleaving
inside a record; a full 240-byte return record takes about 2.1ms on this UART.

EMOS admission/copy must be bounded, including pointer/capacity checks in
the permitted caller region. Current `emos_sdlink.c` bounds complete buffers to
`0x040000 <= address < 0x0B8000`, including the MOSlet region, with containment
checks for their lengths. This is the resident SD service's supported MOSlet
exception, not admission of external `.emo` providers. See the
[EMOS utility contract](https://github.com/bgates747/agon-emos/blob/main/docs/emos-utilities.md)
and [deployment evidence](../tasks/AUDIT-008/HARDWARE.md).
The receive ISR stores at most one admitted record;
the foreground copies it under a bounded interrupt lock. CRC/file semantics
belong in the application; valid keyboard packets never wait for filesystem I/O.
Oversized/unowned frames are consumed by declared length, not scanned as keys.
Malformed service records cannot acquire filesystem access. Transport framing
loss follows explicit fault/re-admission, not silent byte-stream continuation.

## Gateway and local lifecycle

Existing 66-byte EMOS gateway request, ABI 1.0, operation SERVICE=2 and reserved
provider `ext.sdlink`. The first input byte selects OPEN=0, RECEIVE=1, SEND=2,
CLOSE=3. SEND carries one complete record after the selector. RECEIVE copies a
whole record to the caller's bounded output; outputLength=0 means no message.
OPEN/CLOSE have no payload. Reject unsupported combinations before UART access.
This extends an owned Core service; transient modules cannot take over UART1.

Presence messages announce an active application and refresh its lease once a
second; absence for five seconds makes P4 report offline. Boot identity changes
invalidate pending/cached results. Requests while offline are not transmitted.
Presence/session IDs describe incarnation, not a reset guarantee or security key.
CLOSE/normal exit marks the service unavailable. P4 reset requires fresh service
presence and session handshake; it must not discard physical keyboard admission
without following the existing keyboard lifecycle.

## Host request lifecycle

1. GET `/sd/status` returns local capability, online/pending state and boot ID.
2. POST `/sd/rpc` submits one binary request (Content-Length required, <=240).
   Return HTTP 202 while pending, HTTP 200 with the binary completed response,
   409 for another outstanding/conflicting request, 400 for malformed input and
   503 while the agent is offline. The handler does not block waiting for SD.
3. The host repeats the identical POST to poll/retry. P4 retains the completed
   response until the next accepted request. Same session/sequence with different
   bytes is a conflict. Retransmission never silently advances a file offset.
4. The application also caches its last request identity and response. Repeated
   requests return that response; stale or skipped sequences are rejected.
   A new session begins with HELLO while no transfer needs recovery. Host loss
   does not grant a new caller permission to discard a pending staged write.
5. Single outstanding request is the credit limit. At most one whole record is
   queued per direction; no unlimited network or interrupt backlog. The host
   deadline is bounded and reports uncertain completion explicitly; it does not
   report a timeout as proof that an operation did not execute.

## File operations and persistence

Operations: HELLO=1, STAT=2, LIST=3, READ=4, BEGIN_WRITE=5, WRITE=6,
FINISH_WRITE=7, ACTIVATE=8, CANCEL=9, RECOVER=10, EXIT=11.
The following payload layouts are frozen. `path` is a one-byte byte-count
followed by 1..120 ASCII bytes; `u16`/`u32` have the endian convention above.
No implicit terminator or structure padding is transmitted.

Staged target paths are at most 112 bytes, leaving eight bytes for `.p17part`
and `.p17meta` within the general 120-byte READ path limit. Reject longer write
or recovery targets before creating any sibling files.

| Operation | Request payload | Successful response payload |
| --- | --- | --- |
| HELLO | empty | boot:u32, max-data:u16, features:u16 |
| STAT | path | size:u32, attributes:u8 |
| LIST | cursor:u32, path | next-cursor:u32, eof:u8, optionally attributes:u8,size:u32,name-length:u8,name |
| READ | offset:u32, count:u16 (<=216), path | total-size:u32, actual data (0..count bytes) |
| BEGIN_WRITE | transfer:u32, length:u32, expected-crc:u32, path | transfer:u32, next-offset:u32 |
| WRITE | transfer:u32, offset:u32, data (1..212 bytes) | transfer:u32, next-offset:u32 |
| FINISH_WRITE | transfer:u32 | size:u32, crc:u32 (measured normally; declared identity in fast mode) |
| ACTIVATE | transfer:u32 | empty |
| CANCEL | transfer:u32 | empty |
| RECOVER | action:u8, path | state:u8 |
| EXIT | empty | empty, then close service and return to MOS |

HELLO features bit0 read, bit1 staged write, bit2 listing, bit3 recovery.
Bit4 (0x10), added by sdserve v0.2.0, means the listener was explicitly started
with `--fast`: FINISH/ACTIVATE omit whole-file digest rereads. Protocol major,
packet CRC, framing and operation payload sizes remain unchanged. The updated
host queries HELLO before BEGIN and rejects mismatched listener/`put --fast`
selections. Without bit4, normal verification semantics apply.

LIST
returns at most one entry, advances a zero-based filesystem enumeration cursor,
and skips dot entries; a concurrent directory change invalidates a stable-list
assumption. Names too long for a record return an error, not a truncated path.
READ count=0 returns size without file data. Presence has empty payload;
operation 0 online, operation 1 closing. Status codes: 0 OK, 1 bad request,
2 unsupported, 3 busy, 4 stale session, 5 sequence conflict, 6 filesystem error,
7 integrity failure, 8 recovery required. Error payload optionally carries one
byte underlying FatFS result; otherwise it is empty. Sequence validation errors
do not advance the expected sequence. Other accepted operations, including
filesystem failures, do advance and are cached. CRC-invalid records are dropped.
Status 4 is exclusively a stale session. An invalid/inactive transfer ID within
the current session returns bad request (1), advancing and caching normally;
it must not be confused with a session rejection that did not execute.

Pre-deployment clarification, 2026-09-13: the staged-path bound and transfer-ID
status above prevent unreadable long-named stages and ambiguity in the client's
retry/sequence recovery. Wire fields and numeric statuses remain unchanged.

Paths use bounded ASCII byte strings, resolved to absolute MOS paths;
reject embedded NUL, traversal and overlength rather than truncating. The
application has an explicitly configured root. Avoid interpretation as MOS
commands. Paths and hashes are data; no arbitrary host shell execution endpoint.

READ includes explicit offset/count and returns actual bytes with EOF/size.
LIST is paginated with an explicit cursor. BEGIN_WRITE includes transfer ID,
target path, expected length and CRC32; it creates a new staged sibling without
truncating the current target. WRITE includes transfer ID and exact next offset.
Check filesystem return codes and byte counts. ACK of WRITE means accepted into
the open staged file, not power-failure durability.

FINISH_WRITE requires the complete declared byte count and syncs/closes with
checked results. Normally it then rereads the stage and verifies length/CRC.
With bit4 set, it instead echoes the declared size/CRC without measuring them.
The internal state is finished, not necessarily verified. ACTIVATE is separate and preserves
a recoverable old target. For target T, siblings are T.p17part (staged data),
T.p17meta (fixed metadata) and T.p17bak (previous target). BEGIN rejects any
pre-existing sibling rather than overwriting a prior transaction. Metadata is
magic SDT1, transfer:u32, expected-size:u32, expected-crc:u32, metadata-crc:u32;
the last CRC covers its first 16 bytes. Write/sync/close metadata before data
admission. Its immutable expected identity is used for post-restart recovery.
These sidecar suffixes are reserved and cannot themselves be client targets.

In normal mode activation validates the staged contents against their declared
identity; fast mode omits that reread. Activation closes every target handle, moves an
existing target to backup, then renames the stage to target. On failure retain
all recoverable copies and report RECOVERY_REQUIRED. Verify the final target
before success in normal mode; fast mode skips only that whole-file digest.
Then remove metadata; retain the backup for explicit recovery
cleanup. There is no automatic execution or deletion of the previous version.

RECOVER action 0 inspects (state bits: target=1, part=2, metadata=4, backup=8;
metadata-invalid=16), action 1 restores backup only when the target is absent,
action 2 explicitly abandons a stage/metadata when no transfer is active and
either the target is present or valid metadata exists with both target and
backup absent, and action 3 removes a previous backup only after the current
target can be opened/read and the host explicitly requests cleanup. Never remove
an existing target as a side effect of recovery. Invalid/ambiguous metadata
reports recovery required and preserves files. The absent-target action-2 case
allows an interrupted first upload to be discarded and retried; it never removes
a target or backup. Missing target plus valid backup
is recoverable even if power failed before the new target rename. If a new
target exists alongside metadata, compare its identity before retiring metadata;
never infer success just from filename presence. This is a recoverable scheme,
not a guarantee against physical media failure. FAT rename is not assumed atomic
against power failure. Do not delete the only good copy or report ACTIVE on an
uncertain close/rename. Cancellation cleans only the identified stage; recovery
never follows an unvalidated pointer/path from a damaged record.

Pre-deployment clarification, 2026-09-13: action 2 includes the explicit
absent-target/no-backup case above. Otherwise interrupting a first upload would
leave an unrecoverable orphan despite the host retaining its original bytes.
The wire layout and action numbers do not change; no deployed implementation
has consumed the earlier wording.

Service responses identify bad input, unsupported operation, busy, stale session,
sequence conflict, file error, integrity failure and recovery-required distinctly.
Include the underlying MOS/FatFS error where available. No raw POSIX success
assumptions for MOS handles: use the documented API and filesystem result values.

## Bootstrap, bounds and acceptance

An initial service binary and possibly updated EMOS must reach the SD before
network servicing exists. Inspect installed supported loaders before proposing
a single commissioning card transfer. Typed commands cannot create a nonexistent
loader. Do not patch resident addresses to avoid the ownership contract.

The pre-implementation EMOS baseline was 130344 bytes against a 131072-byte
ROM limit. The accepted v0.1.14 build is 130919 bytes (153 spare); the 18974-byte
foreground application keeps bulk file/CRC code out of ROM. All wrapper/link
guards pass for that exact build. Core static RAM ends at BDAAA, below the BF800
stack boundary; this is a linker bound, not a stack high-water measurement.
Steady state includes one 240-byte EMOS mailbox, a 244-byte transmit buffer,
bounded parser storage, one P4 pending/result pair and <=256-byte application
I/O chunks, in addition to ordinary firmware queues. Recheck fit for new builds.

Host fixtures must cover arbitrary binary starts, empty files, >64KiB transfers,
lost ACKs, duplicate/conflicting requests, truncation, bad CRC, stale sessions,
disk errors and interrupted activation. Physical qualification checks readback,
keyboard coexistence and ten unattended cycles. Timing offload, graphics and
Golem do not belong to this gate. Hard-hang recovery is unproven; never toggle
the unresolved reset circuit or conflate VDP USB reset with whole-Agon reset.

References: official MOS API.md filesystem/UART sections; EMOS
src/emos_keyboard.c, src/emos.c and docs/emos-v1-contract.md; P4
console_hardware.inc/console_stream.hpp and wired_network_service.cpp. Source
baseline EMOS e48d431; Extender 7e21dfe. Exact accepted build/source identities
are recorded in the linked acceptance record; consult current source for changes.

## Opt-in fast upload (bounded physical validation)

The listener selects fast mode for its whole foreground invocation. The host
`put --fast` skips its independent stage and activated-target READ comparisons,
and reports activation without verification, never a verified SHA256. It still
computes the expected CRC for immutable recovery metadata. Packet CRC, exact
write counts, sync/close errors, sequence/replay, path/root/self protection,
staging and backups are unchanged. Recovery's existing checks are unchanged.
An older host still performs its own full readbacks, but does not know about the
missing listener checks; use the paired updated host for explicit mode selection.

This can accept corruption that full readback catches. It does not promise
power-atomic replacement. Downloads and directory operations are unchanged.
See [implementation and evidence](../tasks/REMOTE-005/FAST-TRANSFER.md).
