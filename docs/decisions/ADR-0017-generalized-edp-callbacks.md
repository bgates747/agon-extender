# ADR-0017 — Generalized EDP callbacks

- Status: Accepted
- Completeness: Partial
- Date: 2026-09-10
- Related tasks: QUAL-003, PORT-008
- Open-decision tracker: QUAL-003

## Context

The paired graphics benchmark discussion raised Pingo's render-completion
callback, previously developed and tested on the mainboard ESP32. The Author
clarified that the product goal is broader: generalized EDP callbacks, allowing
applications to receive useful feedback about EDP work and state. Rendering
completion is one use case within that goal.

## Decision

Generalized callbacks are a production EDP requirement. The implementation must
provide applications a documented return path for EDP events, results and state
information. Acceptance does not establish that this general interface exists
today; the consequences below retain that implementation boundary.
The goal is meaningful interaction with EDP beyond submitting display commands.
Render-completion notification and its benchmark consumer are initial use
cases, not the definition or limit of the facility.

EMOS retains transport, application mediation and committed-route ownership
under the existing EDU service contracts. The Pingo callback supplies
implementation experience; its Pingo-specific event encoding and keyboard
callback carrier do not implicitly define the general EDP wire or application
ABI.

Render completion and output-sink presentation remain distinct. A completion
notification does not certify browser receipt, browser display or physical
scanout. This additive facility does not silently redefine the retained stock
VDU queue/completion behavior selected by ADR-0015.

## Consequences

The public contract and recurring implementation belong in durable service
documentation and production code, with benchmark code consuming that contract.
QUAL-003 tracks the initial design discussion; PORT-008 retains transport
integration and compatibility qualification. Acceptance establishes the product
direction, not a finalized callback mechanism, implemented service or benchmark
result. It does not authorize replacing stock mainboard VDP.
