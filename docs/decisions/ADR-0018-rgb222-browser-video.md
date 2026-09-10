# ADR-0018 — RGB222 browser video and bounded frame pacing

- Status: Accepted
- Completeness: Complete
- Date: 2026-09-10
- Related task: PORT-003

The Author requested that the browser decode RGB222 and that the initial
5 fps throttle be removed. The existing P4 compositor already produces final
64-colour pixels, so transmitting three expanded bytes per pixel is redundant.

EDP on P4 retains ownership of all composition. Its browser producer packs the
completed image as one byte per pixel; browser WebGL expands RGB222 for display.
The updated browser retains RGB888 decoding. The explicit EVF1 pixel-format
field distinguishes the encodings; older browser assets require a reload from
the updated P4. The [browser-video contract](../protocols/browser-video.md)
defines the byte layout and compatibility boundary.

Remove the fixed snapshot interval while retaining bounded storage, latest-frame
selection and one browser credit per presented frame. Network delivery remains
independent of logical VDP time and uses PORT-006's opaque transport. The browser
reports measured presentation rate separately from the logical frame period.

This decision reduces transmitted pixel payload by three without moving VDP
semantics into the browser. It does not promise a particular physical frame
rate, reduce the composition-slot allocation, or authorize interrupting the
Author's running hardware uptime test.
