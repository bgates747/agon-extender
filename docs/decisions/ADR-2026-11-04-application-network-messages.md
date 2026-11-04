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
