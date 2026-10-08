# Native active HDMI timing experiments

## Current result

The first standalone512×384 signal **fails physical review**: the Author reports
flicker and repeated picture disappearance/return after a few seconds. The P4
continues approximately60Hz DMA progress with HDMI hot-plug detected. Successful
flash/readback and pixel checks did not establish monitor synchronization.

The Author clarifies that512×384 is the game canvas, always centered inside a
widescreen HDMI carrier. The684×384 pattern is now flashed/readback-verified;
512-wide HDMI is no longer the target. A centered512-wide game would have86-pixel
black sidebars.384-line timing acceptance remains separate from full integration.

| Candidate | Clock and total timing | Build / physical result |
|---|---|---|
| 512×384,4:3 | PLL240/7;1104×517 totals; calculated60.069440Hz | Flash/readback pass; Author reports flicker and repeated loss of picture |
| 684×384,wide | Same clock/totals;0.1953% aspect rounding | Author confirms steady output, correct circle/square aspect and full outer border; misplaced fixture labels identified |
| 320×240,4:3 | Same clock/totals | Compiled/validated; not flashed |
| 428×240,wide | Same clock/totals;0.3125% aspect rounding | Compiled/validated; not flashed |

All four frozen build identities and factory hashes are retained in
[NATIVE-BUILDS.json](NATIVE-BUILDS.json).512×384 and684×384 have been flashed;
the240-line candidates remain unflashed. The684-wide centered-layout follow-up
passes Author review. The successful carrier alone does not qualify full
Extender services, scanout sprites or gameplay; the subsequent experiment is
recorded separately in [full integration results](FULL-WIDE-RESULTS.md).

## Widescreen trial

Build `hdmi-timing-r03-b2026-10-07-07-17-01Z`, factory SHA256
`0aaa31da76792382d94686d91b095706a3653268eeb7f6d0c6797e86e98df226`,
is installed at13:31:04Z. All three flash segments independently verify.
The P4 reports684×384, DPI selector1/divider7 and1202 DMA completions in
20.006369 seconds (60.081/s), with HPD1. No panic or restart is observed in the
25-second startup capture. [Machine-readable result](NATIVE-WIDE-RESULT.json).

The pattern covers the wide active area to test signal stability, edges, colors
and aspect before centered game integration. It is not a game or a new logical
VDU mode. No source rebuild, bridge change, Agon reset or SD edit occurred.
The Author initially reports “Visible, but geometry looks wrong,” then clarifies
that the circle and square have correct proportions, output stays continuously
visible without flicker, and the white border surrounds the entire screen.
The concern is color labels not lining up with bars: a confirmed fixture defect.
The r03 pattern spaces labels36 pixels apart regardless of actual bar width.
This establishes bounded physical acceptance of the684-wide carrier, not a
monitor-distortion failure. Its driver and timing remain unchanged.

The r04 follow-up corrects labels using each bar's own center and places the
512×384 image inside black86-pixel sidebars. The outer white border remains a
diagnostic edge marker; an inner outline marks the game canvas. ASan/UBSan
checks verify the exact sidebar pixels, per-bar label locations, channels and
allocation boundaries at all prepared geometries. A newly identified image
preserves the earlier tested bytes; the r03 manifest is not rewritten.

That centered pattern is now installed as
`hdmi-timing-r04-b2026-10-07-13-36-36Z`, factory SHA256
`4de6bd549cb6fa11a6f7996802c0a062b2779319ce33f8478cc413931afd62cd`.
All three segments verify; startup reports1202 DMA completions in20.006151s,
HPD1 and no panic/restart. Source comparison confirms identical timing, main
loop, SDK configuration and bridge. [Result](CENTERED-WIDE-RESULT.json).
The Author confirms the centered layout is correct and steady. The changed
artwork compared with640×480 is disorienting, so subsequent comparisons should
reuse this layout where dimensions permit. Both signal and centered-pattern
gates pass within this bounded experiment. The standalone image was held at the
end of this review; full services, sprite integration and gameplay require their
own tests, now recorded in the integration results linked above.
No game integration, Agon reset, SD edit, commit, push or production selection
occurred in this follow-up.

## Failure follow-up

A passive30.007-second USB capture at13:27:58Z reports six successive samples
between59.964 and60.176 DMA completions/s, HPD1 throughout, and P4 uptime beyond
five hours. No restart or panic is observed. The bridge reports unchanged input
timing register bytes. The capture sent no serial commands and requested no
reset. This rules against a reboot in that observed interval, not against a
DSI/bridge/monitor synchronization fault; no optical lock measurement was taken.
The long front porch is within the bridge driver's16-bit register writes; no
simple8-bit porch truncation was found. Do not diagnose the remaining fault from
HPD or DMA alone. Local evidence is the ignored native512-passive capture.

## First512×384 candidate

Build `hdmi-timing-r03-b2026-10-07-06-49-32Z`, factory SHA256
`8abd17f99d48c7fa7e2cbd17cc1148840080557aa6072a84d891e486fadcf731`.
ESP-IDF5.5.5 remains pinned to commit
`b774170ff46c393eeb5e495ea37936038d3f4f4f`; its checkout is unchanged.
The source and bridge closures, generated timing header, image headers, factory
segments and build inputs are retained in the build manifest.

1. Active pixels are512×384 with no larger active canvas. Extra front porch is
   blanking. P4 memory holds589824 RGB888 bytes for the pattern.
2. Two480Mbps DSI lanes feed the existing LT8912B bridge. The bridge receives
   custom timing/VIC0 and4:3 aspect metadata. PLL selection/divider read back as
   selector1/divider7; no unsupported custom oscillator was introduced.
3. Flash and all three segment readbacks pass on the selected P4 silicon1.3.
   A25-second startup capture has300,601,901,1202 cumulative DMA completions
   over its four reporting intervals. Rates span59.976–60.176/s owing to integer
   frame counts in roughly5-second windows;1202 frames over20.007359s is60.078/s.
   HDMI HPD stays1. No panic or restart occurs in that capture.
4. Host ASan/UBSan pattern tests pass for512×384,684×384,320×240 and428×240,
   along with the earlier carrier patterns. Tests cover channel ordering, edges,
   checker geometry, stride padding and allocation canaries. These establish
   pixel generation, not the monitor's treatment of the signal.
5. The standalone image has no network, keyboard or Agon SD services. It does
   not reset or communicate with Agon. Original38-byte Agon startup is retained;
   the failed sprite-service preflight changed no fixture configuration.

Local evidence: ignored `agents/hdmi002/native512-r03-build2`, with the installed
first receipt and startup log dated07:12:34Z. The same exact image was
reinstalled at08:09:23Z after restoring the original Agon startup and verifying
normal input/services on the known working full image; the later sprite
integration attempt failed before benchmark measurement. That512-wide pattern
has since been replaced by the684-wide trial above. The known working848×480 full image is
retained for recovery. This experiment does not select production or allocate
new logical VDU modes. Advancement gates remain in the parent task.

## Superseded512-wide integration preparation, not a measured result

The prepared full-firmware 512×384 rolling selection uses three 32-row RGB888
slots requiring 147456 internal bytes, versus 244224 at 848 pixels wide: 96768
bytes (39.6%) less. Twelve 32-row blocks cover 384 active lines and fit the proven
block-count range. Host geometry and sprite checks pass; physical integration
has not been tested. The default and 848-wide selections remain available.
This calculation applies only to the512-wide preparation, which remains
unflashed. The selected684-wide direction instead requires196992 bytes for three
32-row slots,47232 bytes (19.3%) less than848-wide. Its service headroom and
picture correctness are unproven; do not transfer the512-wide result to it.
