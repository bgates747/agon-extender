# Human observations — Mac/Linux browser and game comparison

The Author reports a video-performance regression in the newer P4/browser build.
On the restored September 19 checkpoint, Linux Firefox generally delivered better
gameplay than Mac Chrome, but Rally remained unplayable despite high presented
fps. Both tested Jukebox versions work in Legacy and stop responding to input in
ExCom. These observations identify symptoms; they do not isolate their causes.

This consolidates the recent 2026-09-21 conversation, including the initial
reports that motivated rollback. Exact observation timestamps and run durations
were not recorded. Numbers are human-observed **browser presented frames/s**, not
measured game-loop rates, input latency, or physical display refresh. Ranges are
not averages. No percentage delta is calculated from unmatched ranges.

## Build and test conditions

| Label | P4/browser identity | Conditions |
| --- | --- | --- |
| Earlier checkpoint | `browser-capture-r01-b2026-09-19-21-26-56Z` | Restored for both Mac and Linux comparisons below. |
| Newer pre-rollback build | `key-query-probe-r01-b2026-09-20-02-08-44Z`, browser-capture-r03 parent | Initial regression reports; restored for later Jukebox retests. |
| Mac | Chrome on macOS | Browser capture and Extender USB keyboard observations as specified; host resource pressure not measured. |
| Linux | Firefox; wired router connection | Human tests; distinct from the separate headless Chromium check. |

The Author's clarification is decisive: **newer regressed relative to earlier**.
The good rollback readings must not be attributed to the newer build.

## Earlier checkpoint: Mac versus Linux

Rows put application failures first, then prompt observations. “Not reported”
means no corresponding observation, not a failed test.

| Workload / mode | Mac presented fps | Linux presented fps | Mac input / usability | Linux input / usability |
| --- | --- | --- | --- | --- |
| Jukebox v0.9.6-beta, ExCom | Not reported | Not reported by Author | Not separately tested/reported | Full GUI and directory appear; neither keyboard produces a response. See route controls below. |
| Rally gameplay, mode 8 | No separate gameplay rate | No separate gameplay rate | In-game keyboard response awful | Unplayable with either keyboard; Extender USB responds better than browser capture, but still inadequate. |
| Rally demo, mode 8 | Similar to MOS range, approximately 48–55 | 55–60 | Demo throughput does not establish gameplay responsiveness | Same limitation; high presented fps coexists with poor gameplay. |
| Rally waiting for race entry, mode 8 | Approaches 60; highest noted 57 | Not reported | Not separately assessed | Not reported |
| Nurples, mode 20 | 25–30 depending on active sprites | 28–30; dips to 25 with many sprites, then recovers | Poor in-game input; worse than Linux | Playable, significantly better than Mac. Little perceived difference between browser and Extender USB input. |
| MOS prompt, mode 0 | 28–30 | 28–32 | Acceptable typing; similar to mode 20 | Acceptable on both keyboards. Browser perhaps slightly more responsive, confounded by the nicer/easier host keyboard. |
| MOS prompt, mode 20 | 30–40 | Initially 40s, approaching 50; later about 30 | Acceptable typing | Interaction-associated changes; detailed sequence below. |
| MOS prompt, mode 3 | 38–42 | Not reported | Acceptable typing | Not reported |
| MOS prompt, mode 8 | 48–55 | 48–60; 58–60 common, 60 not rare | Slightly better typing than mode 20 | Almost imperceptible typing latency with either keyboard. |

No games were tested in modes 0 or 3 during this comparison.

## Linux Firefox mode 20: observed sequence

| Step | Action / state | Presented fps | Interpretation limit |
| --- | --- | --- | --- |
| L20-01 | First switched to mode 20 at MOS prompt | In the 40s, approaching 50 | Initial reading, not sustained benchmark. |
| L20-02 | Interacted through browser and Extender USB keyboards | Dropped to about 30 and stayed there | Correlation with interaction; cause unknown. |
| L20-03 | Refreshed browser and reconnected | Rose to about 40 | One recovery observation. |
| L20-04 | Interacted again | Returned to about 30 | No isolated variable. |
| L20-05 | Refreshed again | Remained about 30 | Refresh was not a reliable recovery. |
| L20-06 | Ran Nurples | 28–30; temporary 25 with many sprites | Gameplay remained playable. |
| L20-07 | Quit Nurples; no further interaction yet | Sustained 45–48; brief readings of 60 | Transient 60 must not be represented as sustained performance. |

## Newer-build observations before rollback

| Host / workload | Presented fps | Author observation | Limits |
| --- | --- | --- | --- |
| Mac, mode 0 MOS prompt | About 6 | Motivated the quick Linux comparison and subsequent rollback | No matched-duration sample. |
| Linux Firefox, gameplay (title/mode not specified in that report) | About 30 | Huge lagouts and nearly unresponsive browser input; Extender USB input better, but game still rough | Do not assign this report to a specific game or infer game-loop fps. |

The Author also observed choppy typing in the ChatGPT application on Mac while
browser video was connected, improving when frames stopped. This supports
investigating host load/memory pressure, but neither was measured or isolated.

## Jukebox route and version controls

| P4 build | Jukebox version | ExCom result | Legacy result | What this establishes |
| --- | --- | --- | --- | --- |
| Earlier checkpoint | v0.9.6-beta, classic text UI | GUI and current directory display; no response to either keyboard | After reset, correct audio and smoothly responsive input | Route-dependent symptom on the older P4/browser. |
| Newer pre-rollback build, restored | v0.9.6-beta | Same symptom | Runs correctly | Failure is not exclusive to the rollback image. |
| Newer pre-rollback build, restored | v0.11.0-beta, tagged release | Same full-GUI/directory but no-input symptom | Runs correctly after reset | Reproduces with a tagged, source-reviewable version. |

The v0.11.0-beta test replaced only `/jukebox/tgt/jukebox.bin` and removed the
conflicting `/bin/jukebox.bin`, as requested. Legacy controls followed resets;
reset and route therefore changed together. No interrupt-vector fault, missing
VDU implementation or deadlock has been established.

## Separate agent checks — not human performance measurements

| Check | Result | Scope / limit |
| --- | --- | --- |
| Newer build, Linux headless Chromium, mode 0 prompt | 37.36 presented fps over 10.01 s | Not Firefox, physical monitor presentation, gameplay, or keyboard-latency evidence. |
| Earlier build, Jukebox apparent freeze | 58 additional P4 sends over 2.048 s, approximately 28.3 sends/s; HTTP/screen text responsive | P4 send rate, not human-observed presented fps. Does not prove application input consumption. |
| Same Jukebox status check | Keyboard ready and physically neutral; no pending/held host-injection events | Does not prove keys reached the application's input loop. |
| Read-only tagged Jukebox/EMOS review | Timer1 and UART1 occupy different reviewed vector slots | No direct collision found; not a root-cause diagnosis. |

## Subsequent functional acceptance

| Change | Author result | Performance claim |
| --- | --- | --- |
| Browser Reset Agon, moved to top-right header; success message removed | “Excellent”; authorized commit and push | Functional/UI acceptance only; no new fps comparison. |

The reset upgrade followed these comparisons and is not one of their measured
builds. It is recorded in [REMOTE-003](../REMOTE-003.md).

## Evidence and follow-up ownership

1. [Detailed chronological comparison](2026-09-21-mac-comparison.md) retains the
   original observations, corrections and deployment sequence.
2. [Jukebox source/input review](JUKEBOX-INPUT-REVIEW.md) records provenance,
   vector findings and tagged-release controls.
3. [REMOTE-001](../REMOTE-001.md) owns browser/input follow-up. This summary
   authorizes no new benchmark, firmware change or diagnostic campaign.
