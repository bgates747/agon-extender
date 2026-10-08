# ADR-0024 — Centered HDMI presentation

- Status: Accepted
- Completeness: Complete
- Date: 2026-10-04
- Amended: 2026-10-07
- Related tasks: HDMI-001, HDMI-002

## Executive summary

The Author selects a centered image, unscaled by default, in a widescreen HDMI
presentation buffer. The initial carrier is1280×720; separately selected timing
experiments retain the same geometry rule. Black letterboxing and pillarboxing preserve logical
pixel geometry and avoid presentation resampling. This defines the product
adapter's intended geometry; implementation and qualification remain pending.

## Decision and rationale

P4 VDP retains each Agon mode's logical drawing dimensions and native storage.
Except for the explicitly selected 320×240 scaling exception below,
The P4 output adapter maps one logical
pixel to one output pixel, without enlargement, reduction or aspect correction
by resampling. It centers the image and fills all surrounding pixels black.
Images exceeding the output dimensions are centered and cropped for now.
For a W×H image and an output O×P, left and top offsets are floor((O−W)/2) and
floor((P−H)/2); an odd remaining border pixel belongs on the right or bottom.
Format conversion, palette/Copper interpretation and composition remain
necessary where the scanout representation differs from logical storage.

The HDMI representation is RGB888. Reuse the existing native row composition;
new indexed-mode and Copper work is deferred. The HDMI adapter uses double
buffering for double-buffered VDP modes where feasible, and single buffering
otherwise. Completed double buffers are published at a hardware frame boundary.

HDMI replaces browser video in this selection while retaining browser keyboard
and other web services. Later runtime output switching is owned by EMOS.

The P4 DSI peripheral and LT8912B bridge select a proven nominal60Hz carrier
at logical mode changes, independently of rendering rate. The Author's
2026-10-07 amendment replaces the initial fixed-carrier policy:512×384 fits
within684×384, while640×480 requires848×480. Smaller images use the smallest
proven fitting carrier without resampling; oversized modes retain explicit
center-cropping pending further qualification. Fixed experimental builds remain
available for controlled comparisons. EMOS retains
ownership of ordinary VDU routing and Extender activation/transports.
The Author also selects full-width480-line drawing on the proven848×480 carrier.
Extender-specific logical modes may expose the full carrier while stock modes
keep their original dimensions and centered placement. Initial experimental IDs
and qualification belong to HDMI-002; this decision does not allocate released
mode numbers or require a new physical timing.
VDP drawing opportunities, frame waits and counters follow the hardware frame
cadence rather than conversion completion. On pre-v3 silicon, IDF 5.5.5 exposes
DMA full-frame completion as emulated vblank. Original 70/75 Hz modes therefore
run at this fixed ~60 Hz physical cadence in the experimental HDMI selection.

The Author's2026-10-07 clarification makes512×384 a logical game canvas, always
pillarboxed in a widescreen HDMI carrier, rather than a4:3 physical HDMI target.
The P4 supplies the black sidebars; the monitor receives the wide signal.
This preserves game geometry while permitting future applications to use the
full wider logical area. The848×480 experiment centers512×384 at(168,48).
The proposed684×384 experiment would center it at(86,0), with0.1953% rounding
from exact16:9. Those numerical choices are experimental timings, not supported
mode declarations. [HDMI-002](../tasks/HDMI-002.md) owns their qualification.

## Authorized 320×240 scaling exception — 2026-10-07

After the native 428×240 trial produced no usable monitor picture, the Author
accepted a stable PPA-filtered static pattern and requested integration for
Rally. The experimental P4 output adapter may scale the completed 320×240 image
by exactly2×, centering640×480 at(104,0) in the proven848×480 carrier. Bilinear
softening is accepted for this trial. Other modes retain the unscaled policy.
This is an output transformation, not a change to logical mode IDs or VDU calls.

The P4 first composes a private visible-image snapshot including sprites/cursors;
PPA consumes that snapshot without borrowing the application's writable back
buffer. A copy spanning a logical swap is discarded. HDMI uses its own front/back
buffers even in a single-buffered logical mode, publishes only completed scales,
and does not reuse the old front before actual DMA acknowledgment. Stock logical
swap and frame-clock semantics remain unchanged. The scaling experiment's visual,
performance and lifecycle qualification belongs to HDMI-002, independently of
the unscaled accepted firmware and production selection.

## Implementation boundary

This decision does not claim a working product HDMI adapter, 60 rendered fps,
or complete mode qualification. HDMI-001 andHDMI-002 own implementation and validation.
