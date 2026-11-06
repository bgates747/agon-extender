# Application messages through an outbound P4 TCP connection

- Status: Accepted
- Completeness: Partial
- Date: 2026-11-04
- Related task: NET-003

Native Agon applications need persistent bidirectional messages to host services.
The Author selects one admitted application session with an ordered full-duplex
opaque-message channel. Each Agon's P4 connects outbound to a configured Pi
bridge/listener using TCP with explicit length-delimited binary records.

P4 owns sockets, network framing and bounded queues. EMOS retains application
admission, physical Extender transport, ordinary VDU routing and lifetime-safe
delivery. The application uses an admitted library interface and cannot seize
UART/GPIO. Network waiting must not block the console parser or hold display
locks. A successful local send admission does not prove remote consumption.

MechAgon owns game interpretation and the Pi-side Tank Royale WebSocket/JSON
adapter. Generic Extender firmware contains no game schema, bot logic or arena
rules. General service implementations remain reusable by other applications.
No CRC or substitute software checksum is added to processor-link traffic.

The Author accepts this connection direction through MechAgon on2026-11-04.
Implementation is developmental: the decision does not establish an installed
application socket API, a hardware capacity/deadline, or production acceptance.
Remaining decisions and implementation gates belong only in the linked task.

The Author requests on2026-11-04 that the first implementation move reply
storage, correlation and timeout policy into application space rather than
spending approximately2KiB of additional EMOS flash. The application library
therefore owns a static reply mailbox and a bounded copy during its existing
MOS callback. EMOS retains minimal caller/carrier admission, boot-local identity,
ordinary transport ownership and synchronous forwarding. Callback entry borrows
the complete receive owner's packet only until return; applications preserve
and restore prior callback ownership. No separate resident pointer registry or
game semantics is introduced. This is a source architecture decision, not a
physical timing or release-acceptance claim.

On2026-11-05 Smith requires parallel carriage of application network payloads
in both directions and delegates ABI agreement to Extender and MechAgon. Their
agreed explicit `ext.netp` service preserves outbound TCP/NM semantics and Legacy
mainboard UART0 graphics. Foreground TAKE replaces the NM interrupt callback for
this carrier; EMOS owns admission and shared-pin control, while application RAM
owns messages and correlation. UART1 retains keyboard and carrier control only,
with no payload fallback. The prior UART `ext.net` path remains separately
identified historical/development behavior. The experimental
[parallel contract](../protocols/application-network-parallel.md) records the ABI;
NET-004 owns implementation and remaining qualification. No installed parallel
network service or hardware performance is claimed by this decision.

Smith's2026-11-06 amendment selects one final MechAgon parallel attempt, then
an explicit supported UART1 application binding on failure, while Extender
continues separate fixture-based parallel qualification. The
[separation decision](ADR-2026-11-06-independent-parallel-qualification.md)
supersedes the earlier application-level parallel-only requirement. `ext.netp`
itself still has no automatic payload fallback or uncertain-message replay.
