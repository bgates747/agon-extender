# SCAN-001 — Author observations and discussion

## Executive summary

These are selected verbatim Author messages from the originating chat, retained
as a navigable handoff. Human observations are qualitative unless explicitly
identified otherwise; none is a measured whole-frame video rate. The receiving
agent should read them alongside the [task](../SCAN-001.md) and retained results.
Original chat message URLs are unavailable. The headings below provide stable
local links; punctuation and spelling within quotes are preserved.

## Initial ordinary HDMI review

Recorded contemporaneously in [HDMI-001](../HDMI-001.md#r03-author-gameplay-review-and-passive-timing--2026-10-04-local):

> it works. nurples appeared to be playing at full speed with perhaps a frame skip here and there. sprites flickered more than they do on mainboard, especially when drawing many of them. (mainboard hardly flickers at all, maybe one or two flickers per second when things get busy).

> 320x240 modes also worked (aginvadors and rally). i did not fully exercise all screen modes.

> mode 0, 3, 8 and 20 all work at an emos prompt.

## Direct RGB888 gameplay regression

Reported on 2026-10-06 after the Author flashed
`rgb-001-r01-b2026-10-05-23-30-11Z`; contemporaneous record:
[RGB-001](../RGB-001.md#author-gameplay-regression-2026-10-06).

> major regression. the top down scroll seems to be just keeping pace, but there might be an odd frame skip in the. difficult to tell. but the sprites flicker like mad, like every frame, and the game is unresponsive to controls until the game ends ... which means the background stops scrolling. rally has no obvious flickering but keyboard response is impaired ... it still takes it but has a lot of latency. it seems like keypresses are being queued as well, which is possible given how vdp command strings queue. aginvadors runs without too much obvious impairment, but might be a tetch slower. if so, it's subtle.

## Ordinary HDMI rollback comparison

Reported on 2026-10-06 after the Author restored
`hdmi-001-r03-b2026-10-05-01-47-13Z`; contemporaneous record:
[RGB-001](../RGB-001.md#author-ordinary-r03-comparison-2026-10-06).

> ok nurples is playable. scrolling is just a little jerky, meaning we get an odd frame skip here and there. sprite flicker is evident but not an every frame deal. keyboard is fully responsive. rally still has input issues. it basically does not at all respond to steering input. i can exit the game with an esc press, whereas i could not in the draw direct rgb888 mode. aginvadors is about the same. in fact, in either firmware aginvadors behaves the same in legacy and excom mode. it always fools me a little because in either mode the game slows down when the fire key is held down, even though it is fully capable of managing the workload of multiple missiles being fired. that is a bug of the application , not firmware.

Rally's Legacy/ExCom route was not specified in this report. The explicit
cross-route comparison concerns Aginvadors.

## Output and validation requirements

These messages occurred earlier in the same chat; their contracts are recorded
in [HDMI-001](../HDMI-001.md), [ADR-0024](../../decisions/ADR-0024-centered-unscaled-hdmi.md),
[RGB-001](../RGB-001.md) and the [bench constraints](../../qualification/bench-constraints.md).

> 60 Hz video is the ultimate target for backward compatiblity with the agon ... and most monitors.

> yes preserve aspect ratio. use letter- and pillar-boxing to center the unscaled image on the screen.

> 1) crop for now 2) i need to discus further 3) double-buffered when in a double-buffered VDP mode, if possible, otherwise single-buffered 4) this will take the place of browser output for now. eventually we will make it switchable via emos.

> stock VDP marches to the vblank signal. i would not want to change that behavior if we can at all help it.

> use a static test pattern for each mode, exercising all the colors, so we can verify correct color output.

> in summaries you should also translate millis into effective frames per seconds

> there is no usable picture now, but the way you are doing this in real time makes it so that i may miss events. you should do and experiment and stop to ask me what i see before continuing on with something else.

> these tests should run for more than 32 frames. for visual inspection i will want fixtures which run indefinitely until i manually select the next one, or escape out of the fixture entirely.

> use assets from nurples and agonwolf3d, because i know what those are supposed to look like

> ah. holdover from when we were rendering rgba2222 pixels expanding to rgb888. well, let's write directly to the hdmi out buffer.

## Motivation and handoff

Messages immediately preceding this task request on 2026-10-06:

> is there any way to emulate stock's pointer swapping method for partial screen scrolling with three bytes per pixel instead of stock's one?

> do you propose 2 such that it is transparent to legacy applicatioins?

Here "2" referred to making P4 HDMI DMA follow row pointers, rather than restoring
a presentation copy or physically copying the scrolling rectangle.

> i'm trying to understand how that would work on extender vdp. actually, i never really understood how partial screen scrolling works in stock vdp. it seems like on both boards, each frame we define a scrolling area and send the scroll command, which means it has to organize the pointers each frame? much cleaner would be to organize the scrolling area once. but i don't think that's how it's currently done.

In response to the proposed independent mapping for a scrolling region:

> it might be the only way we can get enough performance out of this board to make it worth doing. if all i want is network connection, remote file transfer, and external keyboard, i may as well go back to using the wroom board.

The Author then requests the handoff:

> this sounds like a new task to me. write up all the background on it we've discussed, including relevannt performance metrics. link to my observations. basically write it as a handoff, because I'm going to give it to 6.0 Astra in a separate chat (I ccan't switch to 6.0 Astra in this chat because it will degrade performance.)

> do not write up a detailed subtask list, the astra agent will be tasked with that

These last instructions select documentation only. They do not constitute a
completed feasibility assessment, implementation approval or measured performance
claim. The receiving agent owns the proposed breakdown and subsequent review.
