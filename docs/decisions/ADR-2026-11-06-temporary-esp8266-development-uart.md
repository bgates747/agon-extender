# Temporary ESP8266 development with a separate P4 UART

- Status: Accepted
- Completeness: Partial
- Date: 2026-11-06
- Related task: NET-008
- Open-decision tracker: NET-008

Smith selects a temporary on-hardware development aid for software ultimately
running on ESP8266-only Agons. The P4 keeps its current mainboard UART link and
uses a separate UART with separately allocated lines to the real ESP8266.
EMOS owns mainboard service selection and transport lifecycle; the P4 owns the
modem-facing peripheral. Extender tools remain available for iterative deployment
and debugging. The application has a vanilla-MOS deployment without an Extender
runtime dependency; identical binaries are not presumed for raw-register code.

The accepted separate-UART choice supersedes the initial optional74-series mux
proposal. This is not permanent wireless-backend adoption, a production operating
mode, or authority to rewire/flash an occupied bench. The work is secondary to
the parallel goal and current support for other agents. Exact board pins,
resource costs and compatibility depend on the task's bounded owner review.
