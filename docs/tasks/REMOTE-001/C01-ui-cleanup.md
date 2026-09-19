# Browser presentation cleanup — frozen work contract

The working keyboard path is preserved. The browser page needs presentation
corrections: unobscured video, fullscreen enlargement, fewer controls and only
resolution/presented fps in the ordinary status display. Author requested this
contract frozen on 2026-09-19; implementation has not started. Author subsequently directed removal of manual lock controls; that decision is
now included in this freeze.

## Scope and ownership

1. Browser CSS must remove the inset green focus outline from the video canvas.
   Capture remains visibly indicated by its button/status outside the pixels.
   No border, focus decoration or control may cover any Agon edge pixel or text.
2. Browser fullscreen layout must enlarge the presented image to fit the available
   viewport, preserving its intended aspect ratio without cropping or distortion.
   Do not stop at the canvas's intrinsic pixel dimensions. Preserve nearest/pixel
   presentation and keep release/exit controls accessible at the bottom as agreed.
   Reserve only necessary control space; avoid a conspicuous unused secondary panel.
3. Browser layout must present one clear video surface. Inspect the user's apparent
   second canvas and remove confusing container backgrounds, framing or empty
   control regions. Current markup contains one actual canvas; do not describe the
   reported visual effect as a confirmed duplicate framebuffer or renderer.
4. In the ordinary controls row, place Capture keyboard / Release keyboard where
   the connected-to-URL information currently appears. Put connection state and
   URL directly beneath Connect, grouped with that button. Consolidate normal and
   fullscreen control placement so the page does not display duplicate control sets.
5. Move screen resolution and presented fps into the header's unused space beside
   Agon Extender branding, above the image. Labels must distinguish presented fps
   from P4 rendering or application fps. Preserve usable wrapping on narrow windows.
6. Remove the full debug/statistics block from the ordinary page. Keep underlying
   diagnostics available to tooling; this is a display simplification, not deletion
   of counters or protocol fields. Keep test-only controls out of the primary flow;
   the local test-pattern action may remain available in secondary diagnostics.
7. Do not change P4 input arbitration, keyboard packets, repeat, locale mapping,
   UART flow, codecs, screen-text access or EMOS. Preserve the accepted typing
   behaviour. No new display canvas, rendering path or performance experiment.

## Lock controls — accepted removal

Remove all manual Caps Lock, Num Lock and Scroll Lock selectors and their
software override state. Do not move them into another menu or diagnostics panel.
Browser input follows host-reported lock state; P4 physical USB state remains
independent. Preserve the working keyboard Caps Lock toggle. Unknown reporting
must remain distinguishable from off: retain a concise input-status explanation
when a lock-sensitive key cannot safely be translated, without adding replacement
widgets or guessing a value. Test unavailable reporting as well as working host
state. This supersedes the earlier manual fallback decision B03-D08.

## Verification and review

1. Test focus/capture with edge text: no Agon pixel is covered, all text remains
   visible, and the capture indicator is outside the video surface.
2. Test fullscreen with a source smaller than the window at two viewport sizes.
   Assert actual enlargement, aspect preservation and containment, not merely
   that the fullscreen API succeeded. Check bottom mouse reveal and exit/release
   without a second apparent video panel or capture loss from mouse reveal alone.
3. Test ordinary and narrow-window layout: one primary capture toggle, connection
   status directly under Connect, resolution/fps beside branding where space
   permits, no expanded debug block, and no manual lock controls in any layout.
4. Re-run focused browser input/video regressions: typing, Caps handling, repeat
   suppression, release/focus loss and independent input/video connection lifetimes.
   Verify reported/unknown lock state without manual overrides or guessed-off state.
5. Build from the preserved installed composition with these UI edits. Compare
   served assets after separately authorized deployment. Obtain human visual
   review before marking the UI work accepted. Physical USB takeover remains
   an independent pending acceptance item; this contract does not claim it passed.

This freeze authorizes no implementation or deployment by itself. Stop after
committing the progress checkpoint and this contract; await the Author's next step.
