# ADR-0024 — Centered unscaled HDMI presentation

- Status: Accepted
- Completeness: Complete
- Date: 2026-10-04
- Related task: HDMI-001

## Executive summary

The Author selects a centered, unscaled image in the fixed 1280×720 HDMI
presentation buffer. Black letterboxing and pillarboxing preserve logical
pixel geometry and avoid presentation resampling. This defines the product
adapter's intended geometry; implementation and qualification remain pending.

## Decision and rationale

P4 VDP retains each Agon mode's logical drawing dimensions and native storage.
The P4 output adapter maps one logical
pixel to one output pixel, without enlargement, reduction or aspect correction
by resampling. It centers the image and fills all surrounding pixels black.
Images exceeding the output dimensions are centered and cropped for now.
For a W×H image, left and top offsets are floor((1280−W)/2) and
floor((720−H)/2); an odd remaining border pixel belongs on the right or bottom.
Format conversion, palette/Copper interpretation and composition remain
necessary where the scanout representation differs from logical storage.

The HDMI representation is RGB888. Reuse the existing native row composition;
new indexed-mode and Copper work is deferred. The HDMI adapter uses double
buffering for double-buffered VDP modes where feasible, and single buffering
otherwise. Completed double buffers are published at a hardware frame boundary.

HDMI replaces browser video in this selection while retaining browser keyboard
and other web services. Later runtime output switching is owned by EMOS.

The P4 DSI peripheral and LT8912B bridge retain fixed nominal 60 Hz 720p
scanout independently of logical mode changes and rendering rate. EMOS retains
ownership of ordinary VDU routing and Extender activation/transports.
VDP drawing opportunities, frame waits and counters follow the hardware frame
cadence rather than conversion completion. On pre-v3 silicon, IDF 5.5.5 exposes
DMA full-frame completion as emulated vblank. Original 70/75 Hz modes therefore
run at this fixed ~60 Hz physical cadence in the experimental HDMI selection.

## Implementation boundary

This decision does not claim a working product HDMI adapter, 60 rendered fps,
or complete mode qualification. HDMI-001 owns implementation and validation.
