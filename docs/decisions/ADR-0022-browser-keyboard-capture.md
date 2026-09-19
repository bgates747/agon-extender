# ADR-0022 — Explicit browser keyboard capture

- Status: Accepted
- Completeness: Partial
- Date: 2026-09-19
- Related task: REMOTE-001
- Open-decision tracker: REMOTE-001 B02/B03

The browser starts with keyboard input released. An explicit Capture keyboard /
Release keyboard control requests or relinquishes P4 input ownership. An active
indicator reflects P4 admission. Focus loss, hidden page and disconnect release
browser-held keys; reconnect/focus return requires explicit capture again.

P4 forwards admitted browser events through the existing processed-key path and
stock-compatible serializer to EMOS. EMOS retains input admission and VDU routing.
Capturing input does not change display mode. Controls stay outside the video.
The screen-text endpoint does not acquire video or keyboard ownership.

This records accepted behaviour, not completed implementation. The earlier browser
candidate remains historical evidence; the working Extender route is the new basis.
