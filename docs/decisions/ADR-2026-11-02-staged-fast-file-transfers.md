# Separate HTTP turnaround from mainboard file transfer

- Status: Accepted
- Completeness: Complete
- Date: 2026-11-02
- Related task: REMOTE-009

P4 owns network turnaround and uses its own SD card to separate HTTP traffic
from mainboard file transfers. This prevents host polling, HTTP acknowledgement
and host journal writes from gating each eZ80 payload record.

## Decision

1. For uploads, P4 stages host data locally before it sends file data through
   the EMOS-admitted mainboard transport. The eZ80 writes its own destination.
2. For downloads, the eZ80 sends its mainboard file through the admitted
   transport into P4 SD staging. A separate P4 task/HTTP path serves that file
   to the host. HTTP backpressure does not gate the mainboard file loop.
3. P4 owns staging capacity, received-versus-stored completion, network
   delivery and cleanup. EMOS retains admission/routing ownership; file
   algorithms remain in SD-loaded utilities, not added resident firmware.
4. Use existing transport backpressure and explicit terminal/error handling.
   No processor-link CRC or substitute checksum is part of this decision.

Complete staging before the next phase is a valid initial implementation;
concurrent prefix draining is not required. Reusing the current framed UART
protocol does not establish continuous streaming or a performance result.

## Consequences

P4 local media is required for this staged fast path, while normal EMOS/CLI
operation remains independent of that card. Host/P4 job identity and error
state must survive ambiguous network replies without automatically repeating
mainboard mutations. Implementation, hardware validation and carrier follow-up
remain in the linked task; this decision is not production qualification.
