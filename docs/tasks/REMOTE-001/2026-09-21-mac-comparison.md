# Mac and Linux comparison — September 19 checkpoint

## Executive summary

Author identifies newer P4/browser performance as regressed relative to the
September 19 checkpoint. Manual tests of that older checkpoint show broadly
matching Mode 0 prompt rates on Mac and Linux, better Linux Nurples playability,
and poor Rally gameplay on both hosts despite high presented fps. Classic
Jukebox freezes in ExCom but works after reset in Legacy. No cause was isolated.
Presented fps is not application-cycle rate or measured keyboard latency.
Mac host contention remains a possible contributor because another application
also types poorly while browser streaming is active.

2026-09-21. Author clarification: the latest firmware/browser is a regression
relative to restored browser-capture-r01-b2026-09-19-21-26-56Z. The numbers below
belong to that restored EARLIER checkpoint, not the later build.

| Mode/workload | Presented fps | Input |
| --- | --- | --- |
| 20 MOS | 30–40 | Acceptable typing |
| 20 Nurples | 25–30, varies with active sprites | In-game keyboard remains awful |
| 8 MOS | 48–55 | Acceptable typing, slightly better than mode20 |
| 8 Rally demo | Similar to48–55 | In-game keyboard remains awful |
| 8 Rally waiting for race entry | Approaches60, observed57 | No separate timing |
| 0 MOS | 28–30 | Similar typing latency to mode20 |
| 3 MOS | 38–42 | Acceptable typing |

No games tested in modes0/3. Human observations, not controlled timed samples.
Typing in the ChatGPT app also becomes choppy while Mac browser receives frames
and improves when streaming stops: host CPU/memory contention is a possible
contributor, not isolated or measured. Game input trouble remains on the older
checkpoint; it is distinct from the newer build's video-performance regression.
The comparison sequence and final installed state are recorded below.

## Scope and follow-up

The reported latest-firmware regression is the Author's comparative assessment.
The current table is exclusively the older checkpoint. The earlier approximately
6fps Mode0 Mac report concerned the newer firmware, but was not a controlled
matched-duration run. Linux headless Chromium achieved37.36 presented fps over
10.01seconds on that newer build at the Mode0 prompt; this did not test gameplay,
Firefox, browser keyboard latency or physical monitor presentation.

The Author subsequently corrected the comparison order: Linux tests use the
same older `browser-capture-r01-b2026-09-19-21-26-56Z` checkpoint as the Mac.
The newer image was briefly restored, then r01 restored again before these tests.
No claim that a particular commit, codec, browser or host resource caused the
regression; no performance fix or new benchmark campaign authorized here.

## Linux Firefox — same September19 checkpoint

| Workload | Presented fps | Keyboard response |
| --- | --- | --- |
| Mode0 MOS prompt | 28–32 | Acceptable with browser capture and Extender-attached keyboard |

Author feels browser keyboard may be slightly more responsive, but notes the
host keyboard is nicer/easier to type on than the Extender-attached keyboard.
This is subjective input feel, not measured transport latency. Mac Mode0 was
28–30fps on this same checkpoint; the observed ranges overlap. No new automated
test, configuration change or firmware deployment accompanies this report.

### Linux Mode8 follow-up — same older checkpoint

| Workload | Presented fps | Input / playability |
| --- | --- | --- |
| MOS prompt | 48–60;58–60 common,60 not rare | Almost imperceptible typing latency on both keyboards |
| Rally demo | 55–60 | Game remains unplayable with Extender-attached keyboard or Linux browser capture |

These are Author observations. High browser presentation rate does not establish
application-cycle pace or responsive gameplay. Failure with both input sources
means browser capture alone cannot explain all observed game trouble; cause
remains unisolated. No firmware changes or new automated tests performed.

Author clarification: Rally responds better to the Extender-attached Agon
keyboard than to browser-captured Linux input, but remains unplayable with
either. Do not interpret the preceding report as equal latency for both paths.

### Linux Mode20 MOS — rate changes during interaction

On the same September19 checkpoint, Author initially observed presented fps in
the40s, approaching50 after switching to Mode20. During interaction with browser
and Extender-attached keyboards, the rate dropped and settled near30fps. Retain
this temporal observation rather than treating30fps as the whole run. Whether
changed screen content, elapsed time, host load or another factor accounts for
the drop is unresolved; interaction is correlation, not an established cause.

### Linux Firefox Mode20 refresh sequence

Author refreshed the browser and reconnected: presented rate rose from about30
to about40fps. Further interaction brought it back to about30fps. A second
refresh left it at about30fps. All observations are Firefox on Linux, at the
MOS prompt on the restored September19 checkpoint. Refresh is not a repeatable
recovery in this observation; no cause established and no automated test run.

### Linux Firefox Mode20 Nurples and return to MOS

Author reports Nurples28–30 presented fps, dipping to25 when many sprites spawn
and then recovering. Gameplay is playable and significantly better than Mac.
Browser-captured and Extender-attached keyboards make little perceived difference
in this game (unlike Rally). After quitting, presented rate rose to45–48fps and
stayed there before further interaction; brief60fps readings also occurred.
Treat45–48 as the reported sustained post-exit range and60 as transient, not a
sustained result. Same restored September19 build; no new agent bench action.

### Jukebox freeze report and read-only status

Author reports Jukebox launches but responds to neither keyboard. On restored
r01, HTTP and screen-text remain responsive; screen shows Jukebox v0.9.6-beta
at album selection. Two P4 timing snapshots show58 additional sends over2.048s
(about28.3 frames/s). Keyboard admission ready, physical neutral, no pending or
held host-injection events. These counters do not prove physical/browser keys
reach or are consumed by the application. No reset or input sent; application
wait/deadlock versus input-path failure remains unresolved. Local raw status
is retained under agents/jukebox-status.

### Jukebox Legacy control — Author report

After reset, Jukebox v0.9.6-beta ran correctly in Legacy mode: correct audio and
smooth input response. This is the classic text-based UI, not the newer skinned
Jukebox. Earlier ExCom observation was a launch followed by apparent freeze and
no response to either keyboard. The successful Legacy control establishes that
this version can operate on the bench; reset and route both changed, so it does
not isolate the failing subsystem or prove a specific missing EDP command.

## Final restoration after human comparison

At Author request, restored latest pre-rollback P4 image
`key-query-probe-r01-b2026-09-20-02-08-44Z`, browser-capture-r03 parent. Independent
flash verification, boot identity/USB startup and all four served browser assets
pass. One normal Agon reset restored keyboard readiness. EMOS and SD contents
unchanged; no agent video observer remains. No post-restoration game performance
claim. All comparison notes remain uncommitted, as requested.

## Latest-build Jukebox retest — Author report

After restoration of key-query-probe-r01-b2026-09-20-02-08-44Z, the same classic
text-UI Jukebox v0.9.6-beta again runs in Legacy and freezes in ExCom. Thus the
route-dependent symptom reproduces on both the September19 browser-capture-r01
checkpoint and the latest restored build; it is not confined to the older image.
This does not identify the failing command/input path or establish whether it
shares a cause with the separate browser performance regression. No new agent
test or firmware change; investigation remains unstarted.

Clarified failure: full GUI and current directory appear, but keyboard input is not acted upon. [Read-only vector review](JUKEBOX-INPUT-REVIEW.md) finds separate Timer1 and UART1 slots in reviewed code; latest-tag provenance differs from tested v0.9.6-beta.

## Jukebox v0.11.0-beta follow-up

The tagged executable was installed and verified, with the duplicate /bin copy
removed at Author request. Author confirms the same input failure in ExCom and
correct operation in Legacy after reset. See [source/vector review](JUKEBOX-INPUT-REVIEW.md).
The original classic v0.9.6-beta observations remain separately identified above.
