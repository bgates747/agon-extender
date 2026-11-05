# NET-003 — First matched application endpoint integration

Implement the existing generic message framework through a minimal admitted
EMOS endpoint and P4 worker, so MechAgon's native mainboard application can
exchange compact records with its Pi bridge. Keep game interpretation out of
resident EMOS/P4, preserve Legacy graphics and existing input/storage behavior.

## Authority and source boundaries

N03-MATCH-001 [x] Verify the all-owner accepted overnight coordination freeze:
MechAgon7681255 with plansb4ef6a2, exact contract hash retained privately.
The Author's verified driver/assistant mandate allows matched component work,
but physical/compute grants and existing policies remain separate.

N03-MATCH-002 [ ] Publish this owner scope before code. Use maintained P4 source
and a separate agon-emos-owned Git worktree based on corrected Eirene16ec1f78.
Keep old branches, production selections, historical fixtures and private data.
The component task INTEG-019 owns EMOS implementation and mandatory link checks.

N03-MATCH-003 [ ] Negotiate the concrete application/wire proposal with MechAgon
before dependent consumer code. Initial requested profile:128-byte opaque record,
two queued complete records per direction, normally10 per second each direction
with bounded lifecycle bursts; numeric IPv4/port supplied by the application.
Pi port7670 is consumer configuration, not a firmware constant. No observer JSON,
CRC/checksum, automatic replay or takeover of SD/controller identities.

## Proposed endpoint, pending peer disposition

1. Existing MOS0x51/getfunction0x20 gateway, namespace ext, new provider net.
   A small C application include and documented raw gateway layout support both
   native C and assembly. Static ordinary application buffers, foreground and
   enabled IRQs only. No application ISR or callback is required.
2. Local OPEN returns a nonzero boot-local token; SUBMIT sends one correlated
   complete request at a time; TAKE returns one immutable complete correlated
   response without waiting; RELEASE revokes local admission immediately.
   Existing EMOS serializer and receive owner retain physical UART ownership.
3. Request kinds CONNECT, POLL and SEND. CONNECT carries IPv4/port, POLL yields
   current connect status or one complete RX record, SEND admits one complete
   record into P4 TX storage. A local/transport result never proves Pi game-turn
   execution. BUSY means not accepted and leaves the caller useful foreground
   work. A response timeout is uncertain and must not cause automatic replay.
4. A separate private variable-length VDU carrier and reply packet identify the
   new endpoint. Application library owns encoding/result validation. EMOS only
   checks fixed endpoint/version/length/caller/token/query and safely copies.
   Proposed header12 bytes: NM, version1, kind, token32LE, query16LE,
   payload length8, request reserved0/response status. Reply kind has bit7 set.
   CONNECT payload6 bytes (IPv4 octets, port16LE); POLL0; SEND0..128.
   P4 TCP framing remains length32LE plus opaque payload; no per-byte handshake.
5. P4 has fixed request/reply mailboxes and a worker-owned Channel<128,2>.
   Console only copies complete commands/replies under short synchronization;
   it never waits on socket I/O. Only the console owner emits UART packets.
   Worker owns connect deadline/cancel/link loss and per-pump operation budgets.
   No automatic reconnect. Experimental idle lease bounds abandoned sessions;
   exact timeout/configuration and renewed-session behavior require peer agreement.
6. Explicit local release or application exit must remain possible after fault.
   P4 worker revokes abandoned socket/session on its bounded lease; a new admitted
   CONNECT explicitly replaces prior incarnation without replaying queued work.
   No app pointer survives a resident call. Query exhaustion requires new local
   admission, not wrap/reuse. Actual ROM/static RAM cost is measured before flash.

## Implementation and evidence

N03-MATCH-004 [ ] Implement shared constants, platform-neutral P4 appliance and
nonblocking worker integration behind an explicit default-off build option.
Preserve the current Ethernet owner, keyboard/VDU packet ordering and Legacy
mainboard routing. Never change monitor modes merely to initialize networking.

N03-MATCH-005 [ ] Implement EMOS fixed endpoint and app-owned C codec/gateway
include. Reuse existing caller admission, serializer, ISR buffer, exit/fault
cleanup and controller-shaped host pipeline tests; do not import its semantic
code or allocate a game decoder. Keep official MOS/VDP references read-only.
Official MOS API baseline remains agon-docsf9806bd3, existing product gateway
contract and native Eirene source/linked UART-divisor checks control this work.

N03-MATCH-006 [ ] Under Pi compile FIFO, run actual P4 peer + actual EMOS C +
actual application-client host pipeline with fake transport, unsafe-buffer,
backpressure, empty/full-binary, stale/wrong-query, failure and exit cases.
Compile native C application binding and full EMOS wrapper mandatory checks;
compile P4 source with actual SDK, then identified matched full build separately.
Record start/end, source/build pins, ROM/RAM and exact qualification limits.

N03-MATCH-007 [ ] Publish logical checked source checkpoints. Preserve previous
accepted/installed bytes, task evidence and unrelated dirty work. Report the
actual usable interface and unsupported boundary to MechAgon immediately.

N03-MATCH-008 [ ] Before physical work, read current install/reset/SD/test protocols,
reconcile the post-manual-test bench/card/component state and obtain actual
exclusive custody. Freeze component-specific full backups, selective flashing,
independent readback and exact restoration or explicitly selected live handoff.
No autoexec edit, test-on-reset, Oryx use, premature graphical cue or uncertain replay.

N03-MATCH-009 [ ] Qualify finite generic endpoint echo and concurrent keyboard/
mainboard rendering before consumer integration under separately admitted plans.
No live arena/heavy run follows from a compile grant. MechAgon/Pi manager retain
consumer proof and live-demo duration/resource decisions. Never release a running
demo with idle checks; no production adoption or human optical pass is inferred.

## Current stop boundary

Publish the scope and negotiate the interface, then implement and verify software.
No actual device/network target, firmware write, reset, demo or heavy arena is
admitted by this document alone. Escalate only unresolved dependent choices;
continue independent authorized source preparation.
