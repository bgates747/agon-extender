# Controller state over UDP

- Status: Accepted
- Completeness: Complete
- Date: 2026-10-24
- Related task: [INPUT-001](../tasks/INPUT-001.md)

Oryx sends current controller state to P4 over UDP, retaining short button and
D-pad transitions until P4 acknowledges them. This decision covers the LAN
boundary only. It does not define the EMOS application API or assert installed
hardware support.

## Authority and decision

The Author selected UDP ("UDP it is. make it so.") and delegated packet layout,
cadence and timeout for later tuning. Following Author feedback about MOS's
nominal120Hz cadence, the sender defaults to event-driven Linux capture,
120Hz publication and a250ms freshness deadline, superseding the initial100Hz
choice. The sender can select another bounded rate/deadline without changing
the logical controls. Matching rates does not synchronize host and MOS clocks.

1. Oryx publishes complete latest-state snapshots. P4 rejects older snapshots;
   loss of an axis update does not block a newer one.
2. Oryx numbers and retains button/D-pad transitions. P4 acknowledges only a
   contiguous prefix stored in its bounded queue. This acknowledges P4 storage,
   not application consumption. Queue overflow invalidates the session.
3. The existing P4 Ethernet owner starts/stops one controller socket worker.
   HTTP admits a single sender, binds its IPv4/UDP endpoint and reports status.
   Receiver instances and session tokens reject previous-session traffic; they
   provide trusted-LAN identification, not authentication.
4. Oryx loss, source overflow, missing acknowledgements and receiver expiry stop
   the session. Recovery requires explicit sender invocation. Invalid state has
   neutral raw values and an explicit validity flag.
5. Oryx preserves native capture values. Exact eight-bit F310 lattice values use
   a compact reversible representation; other signed stick values use native
   width. The LAN envelope is not an eZ80 ABI.
6. The controller worker stores input without injecting keys or writing UART.
   EMOS retains ownership of Extender transports and the eventual application
   interface. Flight response, dead zones and throttle/rearm policy belong to
   the consumer. Direct P4 USB remains separate work.

The [LAN protocol](../protocols/controller-lan.md) defines the selected layout,
bounds and lifecycle. Changes remain developmental until separately qualified.

## Rationale and consequences

UDP permits each new snapshot to supersede missing axis state. A TCP/WebSocket
stream would supply ordered byte recovery but still require framing, bounded
backpressure, freshness and application-consumption rules. UDP instead requires
explicit packet/transition numbering, loss handling and timeout tests. No
measured physical latency advantage is claimed.

Separate controller and keyboard sessions preserve their ownership boundaries;
separate workers alone do not prove performance isolation under load. Offline
codec/session tests and a target build precede hardware qualification. EMOS
delivery and the target viewer remain tracked in INPUT-001.
