# Keep asynchronous UART1 transmission in application space

- Status: Accepted
- Completeness: Partial
- Date: 2026-11-06
- Related task: NET-004
- Open-decision tracker: NET-004/UART1-APPLICATION-DRIVER-R01

Smith selects a reusable application-owned asynchronous UART1 driver, developed
and maintained by UART in its generic MOS project. EMOS does not acquire a
resident UART1 async engine or resident transfer buffers for this work. This
preserves scarce firmware space while applications such as MechAgon provide
their own execution/storage lifetime.

The driver follows UART0 async's call shape and completion model as closely as
practicable. Its public contract distinguishes admission, source release and
wire/peer completion, with bounded interrupt work and positive cleanup.

EMOS continues owning transport admission, ordinary VDU routing, shared-pin
handover and committed mode. Application placement does not authorize replacing
its receive path or silently taking UART1/vector ownership. Generic driver code,
Extender/EMOS integration and consumer adaptation retain separate owners.

This is an accepted placement and ownership decision, not an implemented driver,
frozen numeric ABI, firmware installation or qualification result. Current UART
network submission remains synchronous until separately integrated.
