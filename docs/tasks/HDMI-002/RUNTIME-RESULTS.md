# Runtime HDMI carrier selection — 2026-10-07

## Result and scope

The P4 now selects the proven HDMI timing when an ordinary EMOS-routed VDU22
changes logical mode. Both Nurples binaries complete title, game and exit with
the correct carrier. The 480-line prompt no longer has a vertical crop in the
output geometry. After the final short handback run, the Author confirms the
upper text is visible on the actual monitor. This is separate physical evidence;
logical text readback is not a photograph of HDMI scanout.

| Logical image | HDMI carrier | Image origin | Rendering |
|---|---|---|---|
| 640×480, modes0/1/2 | 848×480 | 104,0 | Existing native compositor, full-frame DMA |
| 512×384, mode20 | 684×384 | 86,0 | Existing RGB888 renderer and rolling sprite scanout |
| 320×240, mode8 title | 684×384 | 182,72 | Centered unscaled image; no new physical 240-line timing |

Both carriers retain the proven 34.285714MHz pixel clock, two480Mbps DSI lanes,
1104×517 totals and calculated60.069438Hz cadence. The adapter selects by logical
dimensions, independently of color depth and buffering. Other fitting modes use
the same rule; oversized images retain the explicit crop fallback. This is not
an inventory or qualification of every Agon mode.

## Installed candidate and failure remedy

Experimental build **rgb-001-r05-b2026-10-07-19-33-12Z**, factory SHA256
`54b56697c81a74049a617906113da62250863eaca2b8a8c3c266b831a62fb2ca`.
The factory image compiled and validated; independent readback verified all four
flash segments. Exact source archive, generated driver, SDK/component identities,
ELF, maps and receipt are retained in the local evidence silo.

The first deployed r05 candidate failed its first848→684 transition. Its third
65,664-byte internal SRAM slot could not be allocated:131,735 bytes were free,
but the largest contiguous block was59,392 bytes. A secondary palette restore
then dereferenced the controller already retired for the carrier change. That
candidate is rejected; its serial log and decoded backtrace remain evidence.

The corrected build reserves three684-wide SRAM slots during first startup,
before network/tasks fragment the internal heap, and retains them across carrier
changes. DSI DMA and asynchronous DMA2D are still stopped/joined before old panel
planes are freed. The persistent core1 output task recreates DSI, bridge and
panel resources; no active descriptors or clocks are edited underneath scanout.
A guard skips palette restoration on a retired controller so the existing
requested/old/default-mode fallback can proceed. Exhaustive allocation-failure
injection remains outside this bounded run.

## Checks

| Check | Evidence | Result |
|---|---|---|
| Carrier selection/centering and buffer ownership | Five host configurations, address/undefined-behavior checks | Pass |
| Build selection/provenance | 12 host tests; complete P4 build validator | Pass |
| Renderer/scroll/sprite semantics | Existing native comparison and three rolling-scene geometries | Pass |
| Ordinary software-sprite Nurples | 10s game; mode0→8→20→0; Escape then CLI ECHO | Pass |
| Ordinary hardware-sprite Nurples | 10s game; same transitions and CLI checks | Pass |
| Repeated hardware-sprite entry | 60s game; another full carrier round trip | Pass |

The three ordinary game cycles share one unchanged P4 boot identity. Their
11 sampled rolling reports have zero invalid blocks, underruns, sequence errors,
late/overlapping refills or reported faults. Minimum reported free internal RAM
is23,323 bytes. Neither game binary, its assets nor EMOS was modified. These are
bounded ordinary-game smokes, not deterministic PRT benchmark comparisons or
proof that the previously observed slight update tearing has disappeared.

The low-color check reuses **render-load-r04-b2026-10-05-05-58-59Z**, SHA256
`55f4bb13eb561ac1f3fda98c6ed8b18d479ec0f34d3ddc601b9784935c0b571d`.
Only three small parameter files are new (**hdmi-carrier-sprite-data-r01**):
the existing case54, sixteen paced hardware sprites, at640×480 in modes0/1/2.
The host selects the mode only in temporary startup, before invoking the
unchanged fixture. Returned records, correlated P4 windows and runtime carrier
metadata establish execution and progress; they do not verify each visible pixel.

All three checks pass: no bad or truncated fixture records, closed matching P4
windows, zero invalid image markers, and848×480 reported during rendering.
Ranked below by slowest P4 image production, not by physical refresh rate:

| Mode/colors | Application updates recorded | P4 image updates/s | DMA scanouts/s | Measured window |
|---|---:|---:|---:|---:|
| 0 /16 | 521 | 18.756 | 60.065 | 8.691s |
| 1 /4 | 444 | 19.461 | 60.006 | 7.399s |
| 2 /2 | 449 | 19.762 | 60.087 | 7.489s |

P4 rates divide each counter by its correlated `esp_timer` window in seconds;
they are not eZ80 loop rates. The five-second minimum test window includes host
readiness/key-delivery overhead before completion. No reference performance
baseline was run, so no improvement percentage is claimed. These checks expose
the retained480-line compositor limit rather than establish60 new images/s.
Runs are `BENCH-009-2026-10-07-19-49-18Z`, `19-51-10Z` and `19-52-41Z` respectively.

## Remaining boundaries and evidence

1. Sprites remain enabled through the existing renderer in every supported mode.
   The 848 carrier still uses native row composition, so equivalent sprite speed
   to the684 rolling path is not claimed. Background palette behavior is unchanged.
2. Stock `rawDrawSpriteScanline` writes the hardware sprite's6-bit RGB after
   expanding background pixels. Source therefore suggests hardware sprites can
   already retain64 colors over an indexed background. This is an observation,
   not a new feature or completed color qualification. Software sprites paint
   into the background representation.
3. The original38-byte startup and both ordinary game binaries were independently
   read back with their original hashes after the sprite checks. The local
   restore helper initially tried typing before boot finished; one verified
   Agon reset and a fresh input session corrected that setup race. Test files,
   result records and startup backups belong under `/agents/extender/results/hdmi02-r05`;
   the resident executable stays under `/extender/render-load-r04`.
4. The Author's visual approval closes this bounded remedy. Production selection
   is unchanged: promotion still requires the canonical firmware qualification
   suite for the exact installed bytes and an agreed production version; neither
   is replaced by these mode/sprite smokes. Exact fixed684 rollback
   `rgb-001-r04-b2026-10-07-15-27-40Z` remains retained; it has the diagnosed
   mode0 crop. New native240-line and full-width modes await a separate inventory.

Local evidence: `agents/hdmi002/runtime`, including `cycles-01` (rejected image),
`cycles-02`, `cycles-03`, `serial-r05.log`, `serial-reserved.log`, build receipts,
host checks, `final-readback`, `handback`, `serial-handback.log` and
`palette-sprites/evidence`. The final handback has mode0/848×480, admitted neutral
input, an offline idle listener and closed timing windows. Machine endpoints, installed-state
receipts and final bench state belong in ignored `HARDWARE.local.md`.
