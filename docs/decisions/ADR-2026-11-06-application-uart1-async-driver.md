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

Smith subsequently selects vanilla MOS as UART's default driver target, with
the TX/RX-only Console8 ESP8266 as its initial test device. Extender owns a
separate EMOS adaptation and any required ownership hooks; EMOS integration
does not gate the vanilla driver. The EMOS ownership rule above applies to
that adaptation, not to a stock-MOS machine without EMOS.

This accepted placement and ownership decision does not itself qualify a driver
or select a firmware installation. UART has since supplied a host-tested/native-linked vanilla application driver
and its first bounded Console8 small-command hardware pass. That result does
not qualify full-FIFO TX, CTS, sustained performance or the EMOS adapter. Extender
integration remains separate and current UART network submission remains
synchronous until that adaptation is implemented and qualified.
