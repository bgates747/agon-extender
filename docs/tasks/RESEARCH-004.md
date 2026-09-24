# RESEARCH-004 — P4 HDMI hardware purchasing and compatibility

## Executive summary

Author requests a one-board P4 solution with onboard Ethernet, HDMI output via
MIPI bridge, and the GPIO access available on our Olimex DevKit. Fallback: a
compatible MIPI-to-HDMI adapter purchasable in the US without Olimex's reported
EUR5000 direct-order minimum. Research only, no orders or hardware changes.

## Contract

1. [x] H01: Establish existing header/harness and DSI connector requirements.
2. [x] H02: Search single-board products and manufacturer schematics; distinguish
   HDMI output from HDMI capture and generic DSI connectors.
3. [x] H03: Check adapter pinout, electrical/driver compatibility, US stock and
   separately overseas sellers serving US buyers. Do not equate listing with stock.
4. [x] H04: Record shortlist, disqualifiers, purchase links, uncertainties and
   recommended path; hardware voice notify when ready.

No firmware builds/flashes, purchases, or messages to vendors. Retain official
source links and retrieval date; no assumed shipping or unverified compatibility.

## Findings

[Assessment and purchasing shortlist](RESEARCH-004/RESULTS.md). No confirmed
unchanged solution; US-stocked M5Stack adapter is an interposer candidate.

Hardware spoken notification completed; fresh stage-6 audio-command receipt
verified. Left Legacy MOS prompt, installed firmware and startup unchanged.
Research complete; adapter engineering/purchasing is not performed or scheduled.

September 18 follow-up: broadened review-site and industrial-adapter search;
Toradex and Ezurio added to RESULTS.md with availability and compatibility limits.
No hardware work or purchases performed.

Author clarification: prioritize complete assembled drop-in or near-drop-in
adapters. Exclude chip-only sourcing leads; retain custom-interposer research
as unqualified historical alternatives, not purchasing recommendations.

## Queue closeout — 2026-09-20

The research entry was already marked completed in TODO. PLAN-001-T02 removes
that completed entry from the unfinished queue and retains this assessment.
The Author's selected/backordered board and future integration remain owned by
P4PC-001. No hardware compatibility or purchasing claim is added by this closure.
