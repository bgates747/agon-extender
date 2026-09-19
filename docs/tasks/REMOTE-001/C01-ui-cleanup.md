# Browser presentation cleanup — frozen work contract

The working keyboard path is preserved. The browser page needs presentation
corrections: unobscured video, fullscreen enlargement, fewer controls and only
resolution/presented fps in the ordinary status display. Author requested this
contract frozen on 2026-09-19. The Author subsequently authorized implementation;
local implementation and browser checks are complete, with build/review recorded
below. Removal of manual lock controls is included in the accepted scope.

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

## Implementation record

The Author's subsequent “proceed” authorized this increment. Browser code now
uses one toolbar in ordinary/fullscreen layouts; Connect owns its URL/status below
it, and Capture occupies the former URL position. Resolution/presented fps sit
beside the title. Other counters and the local pattern remain inside closed
Diagnostics. The extra shell background/border and inset focus outline are gone.

Fullscreen's previous `width: auto` override caused intrinsic-size presentation.
The page now measures the remaining video viewport after the real toolbar height,
and fits the existing 4:3 presentation into it. Resize and wrapped controls are
covered at 1280×900, 1920×1080 and 390×844. Tests assert enlargement, aspect,
containment and bottom reveal, rather than only successful fullscreen entry.

Manual selectors and their override state are removed. Host-reported Caps/Num
state is exercised, including Caps on/off and unknown Num blocking with concise
status. Input/video ownership and existing UART/P4 code are unchanged. Focused
Chromium input/video/layout checks pass; physical review remains pending.

The isolated build derives from the installed r01 composition, retaining codecs
and screen-text support. No new deployment is authorized by this implementation
instruction; installed firmware and hardware are untouched. Changes remain
uncommitted for review. Screenshots/build artifacts are retained in the ignored
local browser-ui record; the build manifest provides portable provenance.

The experimental P4 build passed. [Build provenance](C01-build.json) records
the exact image and comparison: only app.js, index.html and style.css differ from
the installed composition, excluding noncompiled patch backups. P4 input/rendering
sources and codec modules are byte-identical. Firmware installation and human
review remain pending.

Author subsequently authorized flashing. [Deployment receipt](C01-deployment.json)
records verified flash, USB startup, matching served assets and a successful
browser-protocol CLI round trip. Human visual acceptance remains pending.

## Fullscreen feedback diagnosis — 2026-09-19

**Diagnosis only, awaiting the Author's remaining feedback.** Capture loss is a
reproduced page focus-lifecycle defect. Escape exiting fullscreen is consistent
with native browser shortcut handling that this implementation does not acquire;
the exact host event sequence is not reproduced by headless input. Neither finding
implicates P4 UART latency. No product/test source, firmware, browser settings or
hardware was changed during this diagnosis; only local diagnostic harnesses and
these records were written. Existing uncommitted C01 changes predate this review.

| Finding | Evidence and confidence | Effect |
|---|---|---|
| C01-F01 — Capture revoked on fullscreen entry | Reproduced with the current page in headless Chromium 151.0.7922.34 and a simulated acknowledging P4 socket. Disabling only the button's explicit blur in a diagnostic runtime counterfactual preserves capture. | Page closes its input socket on its own focus transition; P4 would correctly release that session. |
| C01-F02 — Escape exits native fullscreen | Author-observed on the real browser; page has no Keyboard Lock request. Headless Playwright Escape instead reaches the canvas and sends usage 41 down/up while remaining fullscreen. | Local injected-key success does not qualify the real browser's reserved shortcut behaviour or prove whether EMOS also receives Escape. |
| C01-F03 — Validation gaps | Existing input test releases capture before entering fullscreen, then captures inside fullscreen. Its Escape check occurs before fullscreen. The layout test verifies dimensions rather than native shortcut handling. | Passing checks missed the Author's capture-first/fullscreen sequence and cannot establish native Escape capture. |

### C01-F01 causal trace

Affected source: `vdp/video/extender/web/app.js`, the Fullscreen click listener,
canvas blur listener, panel focusout listener and fullscreenchange focus restoration.

1. Clicking Fullscreen moves focus from canvas to the button inside the panel.
   Canvas blur releases any held keys, but panel containment initially preserves
   the browser session because the button is still inside the panel.
2. The click handler awaits `requestFullscreen()` and explicitly calls
   `fullscreenButton.blur()`. The recorded button focusout has a null related target.
3. `panel.contains(null)` is false, so the panel focusout handler calls `release()`.
   It closes the keyboard socket and clears `captured`, even though the document
   has not lost window focus. No window-blur event occurred in the reproduction.
4. The later fullscreenchange handler checks `captured` before restoring canvas
   focus. That flag is already false; it cannot repair the lost session.
5. Diagnostic-only counterfactual: replace that one button instance's `blur()`
   method with a no-op in memory. The same capture-then-fullscreen sequence retains
   the socket and shows Keyboard captured. Repository/served code is unchanged.

This establishes a specific page-owned causal path. It does not justify ignoring
all blur events: actual window/tab/session loss must still release keys. A later
fix needs to distinguish deliberate internal focus transfer from genuine loss,
and add a capture-before-fullscreen regression. No fix is authorized by this
writeup, and the counterfactual alone is not a complete cross-platform remedy.

### C01-F02 browser boundary

The current page forwards Escape and calls `preventDefault()` when a cancellable
key event reaches the focused canvas. Its Capture button requests **P4 input
ownership**, not a browser/OS keyboard lock. There is no call to
`navigator.keyboard.lock()` anywhere in this page.

Chrome's [fullscreen Escape explanation](https://developer.chrome.com/blog/better-full-screen-mode)
explains why fullscreen's native Escape action takes precedence without Keyboard
Lock. Its [Keyboard Lock documentation](https://developer.chrome.com/docs/capabilities/web-apis/keyboard-lock)
describes JavaScript-initiated fullscreen, permission requirements and a retained
long-Escape exit mechanism. The [API draft](https://wicg.github.io/keyboard-lock/)
restricts the interface to secure contexts and treats OS capture as best effort.

The deployed page is served over ordinary HTTP on a LAN address. Adding a lock
call alone would therefore not establish a supported remedy: secure-context
hosting, feature support, browser permission and real host behaviour would need
qualification. No HTTPS/proxy/browser-setting change was attempted or selected.
No conclusion is made here about the Author's exact browser version or whether
Escape reached EMOS before the native exit; neither was measured.

Headless Playwright generated both Escape transitions and stayed fullscreen,
which is a limitation of this reproduction, not evidence contradicting the user.
The diagnostic event trace listens in capture phase, before the application
handler, so its `defaultPrevented: false` entries do **not** prove that the page
failed to call preventDefault. The outgoing usage-41 packets demonstrate the
application handler ran in that local test.

### Evidence and disposition

Ignored local evidence: `agents/browser-ui/diagnosis/` contains the reproducible
harness, `fullscreen-events.json` and `fullscreen-no-button-blur.json`. Neither
harness connects to P4 or claims its video connection. All socket traffic is
simulated. C01 remains unaccepted; collect the Author's further feedback before
proposing or executing changes. Physical USB takeover remains separately untested.


## Authorized fullscreen-entry repair — 2026-09-19

The Author authorized C01-F01 repair and deferred a more elaborate native Escape
solution. This supersedes the diagnosis-only hold above for capture loss only.

1. After the fullscreen operation, the page explicitly focuses its canvas instead
   of blurring the button to no destination. Focus stays inside the panel, so the
   existing ownership session survives. Genuine window/panel loss still releases
   keys and ownership under the existing policy.
2. The browser regression now enters fullscreen while captured and asserts the
   same open keyboard socket and captured status both on entry and on exit.
3. Input/session and three-size layout checks pass in local headless Chromium.
   Native browser/OS fullscreen and physical hardware acceptance remain pending;
   the installed r02 image has not been changed by this repair.
4. Escape leaving native fullscreen remains an accepted present limitation. No
   Keyboard Lock, HTTPS, permission or host-browser configuration work is included.


## Additional UI requests — 2026-09-19, documentation only

The Author requested these additions to the pending work list, explicitly without
implementation yet. They extend the original resolution-only header requirement;
the implementation records above do not claim these changes are present.

1. The browser Connect button turns green while its video connection is connected,
   using the same active styling as Capture keyboard when keyboard capture is
   active. It returns to its inactive appearance when disconnected. Video
   connection and keyboard capture remain independently indicated.
2. The header beside the branding reports the current display mode number,
   resolution, color capacity, nominal refresh rate and buffering mode, followed
   by the existing Presented fps text. Example:
   `Mode 8 320x240 64 colors 60 Hz single-buffered`.
3. Nominal refresh describes the active Agon display mode; Presented fps remains
   the measured browser presentation rate. Color capacity and buffering describe
   the active display configuration, not the network pixel encoding or browser
   canvas storage. Report current metadata rather than hardcoding the example.
4. Before implementation, check which mode/configuration fields P4 already
   supplies to the browser; record any missing metadata requirement here. Do not
   guess a mode from resolution alone or claim an unknown field is established.

State: recorded, pending implementation authorization. No code, build or
deployment changes were made for these requests.


## C02 — Frozen connection/mode status and focus repair contract

Author authorized contract freeze, implementation and P4 flashing on 2026-09-19.
C02 implements the additional UI requests above and deploys the locally tested
fullscreen-entry focus repair. Native Escape remains deferred.

1. Browser Connect uses the capture button's active green styling only while its
   video socket is open; reconnect, close and local demo clear the indicator.
2. P4 publishes committed mode number, actual canvas dimensions, color capacity,
   nominal modeline refresh and actual buffering state via read-only
   `/display/status`. Only the VDU owner publishes configuration; HTTP copies a
   synchronized snapshot and never dereferences a changing display controller.
   Unavailable/changing metadata is reported explicitly. No video or input packet
   format changes; browser polling is bounded, non-overlapping and stops on video
   disconnect. Header shows P4 configuration, not network pixel storage.
3. Browser displays the requested mode sentence followed by existing Presented
   fps, preserving wrapping and the fullscreen layout. Unknown status is never
   filled with guessed mode data. Genuine focus loss still releases keyboard;
   entry and exit within the fullscreen panel preserve the same session.
4. Build browser-capture-r03 under standing identity approval; retain the exact
   installed r02 composition including codec/storage/input work. Prove the bounded
   source delta, run browser and metadata tests, preserve installed rollback,
   flash the identity-verified P4 and independently verify bytes/startup/assets.
   No EMOS flash, SD modification, Agon reset or reset-circuit implementation.
5. Human visual/fullscreen acceptance follows deployment. Local Chromium checks
   do not qualify native Escape interception or physical USB takeover.

Research: official `agon-docs/docs/vdp/Screen-Modes.md` specifies mode/color/Hz
tables and double-buffered variants, with old/default-mode fallback on failure.
Project `video/agon_screen.h` owns mode commit and actual controller state;
`extender/display/screen_facade_adapter.*` parses the official nominal modeline.
Existing EVF1 headers lack mode/color-capacity/buffering fields. These facts bound
the additive status endpoint rather than extending the frame format or guessing
from its dimensions.
