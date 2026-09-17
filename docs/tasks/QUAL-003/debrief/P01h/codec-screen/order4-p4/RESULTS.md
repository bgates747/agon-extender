# Order4 SRLE2 on physical P4 — assessment

## Executive summary

**Order4 is materially better than order3 on this P4, and two Nurples trials
actually beat RLE2 delivery. It is promising, but not a reliable replacement yet.**
The first order4 trial was much slower, and a reset-before-run extension later
encountered an unplanned P4 reboot while testing RLE2. Do not promote this
candidate or hide the variation in its average. The known-good baseline has been restored and verified.

All three codecs ran in one firmware with unchanged graphics/scheduler settings,
on the same fixed-mode512×384 cadence60 Nurples fixture. Three interleaved trials:

| Codec | Received fps, mean | Individual trials | vs RLE2 mean | Extra entropy encoding |
|---|---:|---|---:|---:|
| RLE2 | 17.26 | 16.43 / 17.72 / 17.62 | baseline | none |
| SRLE2 order3 | 12.40 | 12.50 / 12.33 / 12.35 | −28.2% | 20.90 ms |
| SRLE2 order4 | 16.83 | 12.45 / 18.89 / 19.14 | −2.5% | 18.53 ms |

Order4 reduced the mean extra encoding cost about11.4% relative to order3,
while mean receipt cadence improved about35.7%. The relationship is clearly not
linear. We have not established why the first order4 trial differed so much.
The two faster trials cannot be ignored, but neither can the slower one.

All nine application traces recorded1800 cycles at60 cycles/s without the
fixture's VDU fault flag. Browser submission rates followed receipt rates.
These are application-cycle and browser-delivery measurements, not proof of
60 fully rendered or physically displayed game frames per second. Compression
counters reported zero failures in every completed game trial.

## Static scenes and standalone encoder checks

Order4 also improved the deliberately RLE-incompressible **periodic** scene:
extra entropy encoding fell from174.94ms to98.31ms, with output delivery rising
from4.00 to5.06fps. RLE2 still delivered7.92fps. This fixture is not random noise:
szip compresses its periodic pattern very well, while RLE2 cannot.

On the frozen sprite scene, RLE2 delivered28.23fps; both SRLE2 variants delivered
about12.00fps despite order4 reducing entropy encoding from10.96 to9.85ms.
The static bitmap case similarly showed little delivery gain. Output savings
alone still do not guarantee higher frame rate.

Standalone device RPC, with already-RLE2-encoded input and no connected browser:

| Input | Order3 encoding | Order4 encoding | Difference |
|---|---:|---:|---:|
| Random noise | 676.11 ms | 678.38 ms | +0.3% |
| Synthetic sprite pattern | 10.830 ms | 9.142 ms | −15.6% |
| Captured sprite scene | 9.036 ms | 8.284 ms | −8.3% |

The original CLI goldens matched both device encoders exactly. Both39-check
codec suites passed, including decode/unpack and invalid-input recovery.
See [TABLES.md](TABLES.md) and the tracked evidence for all inputs and timing scopes.

## Unplanned reboot and qualification limit

1. After the complete nine-run series, the agent added a bounded reset-before-run
   check to investigate prior-state dependence: one RLE2, one order3 and two
   order4 trials, with the same startup reapplied before each.
2. Its first actual RLE2 run lost HTTP responsiveness and the P4 rebooted. No
   completed reset-control result is claimed. The changed P4 boot identity and
   captured boot output corroborate the restart. It was not a successful timing
   trial, and no order4 operation was requested in that run.
3. The captured ROM saved PCs resolve to `xQueueGenericSend` and
   `esp_cpu_wait_for_intr`. Those are saved execution locations, not a sufficient
   crash backtrace or a root-cause diagnosis. Do not attribute this to the scheduler,
   szip or hardware wiring on that evidence alone. The beginning of the reset
   banner/reason was not captured.
4. A normal mainboard reset restored admitted keyboard/SD service. The agent
   stopped the reset extension and successfully completed the nine corrected
   static-scene controls afterward. No firmware fix or unbounded investigation
   was attempted. Preserve the failed-run logs and before-image for follow-up.
5. This failure occurred under an RLE2 control, so it does not establish an order4
   algorithm fault. It does prevent calling the experimental candidate fully
   reliable. Its relationship to earlier mode-transition issues is unproven.

## Setup corrections and comparability

1. The first static attempt inherited mode3/640×480, outside the compressed-output
   path. Frame metadata exposed this; those measurements are excluded. The valid
   static series used startup-selected mode20 and asserted512×384 for every frame.
2. Reflashing P4 required a normal mainboard reset to re-establish keyboard/SD
   admission. Two other failed invocations were ordinary setup issues: attempting
   an offline SD connection and reusing a host CLI evidence-directory name.
   Neither is treated as a codec or gameplay failure.
3. Order selection is explicit per codec call; the legacy API remains order3.
   `srle2=4` selects order4 and `srle2=1` selects order3. Both use record1, no
   differencing and full-input blocks. RLE2, graphics locks, priorities, affinity,
  16KiB task stacks and the30Hz web ceiling are unchanged across controls.
4. The Worker uses the previously qualified generalized decoder. Original CmpS
   and EVS1 wire formats are unchanged. No small-block memory adaptation was
   applied to the physical encoder. Source/fixture/build hashes are retained.
5. Codec counters cover the full invocation; browser metrics use the central
  15-second window ending5 seconds before the final receipt. The scope difference
   is explicit. We did not prove that every received snapshot is a distinct,
   completely rendered game frame. Host browser performance and device rendering
   can both affect delivery; these measurements do not isolate every cause.

## Review decision and follow-up

Keep order4 as a serious candidate for optional SRLE2 streaming, rather than
rejecting it on the earlier Linux prediction. Retain RLE2 as the established
live-streaming baseline. Before promotion, investigate the12.45-versus19fps
variation and the reset-control reboot in a separate approved work item, then
repeat cleanly controlled starts. This task stops here; no scheduler rewrite,
EMOS change, mainboard VDP flash or production promotion is included.

See [REPRODUCE.md](REPRODUCE.md). Raw machine-local evidence is retained under
`agents/order4-p4`; compact measurements and identities are committed here.
Restoration and hardware notification receipts are recorded at closeout.

## Closeout

Original P4 factory prefix SHA256
`22d22c530d643ac2896aa624eba802eb8b3c0ad695f2f6425036d3f130f50604`
was independently verified after flashing. The original 48-byte startup was
restored and read back exactly. EMOS and stock mainboard VDP were unchanged;
the host-mounted MOS-suite card was untouched. The experimental before-prefix
is preserved privately, including its diagnostic partition.

Hardware British female voice notification returned a fresh service receipt
(`stage=6`, `audio_commands=pass`); human hearing is not assumed. Final state:
Legacy MOS prompt, keyboard ready and neutral, SD service exited. See
[evidence/restored-final.json](evidence/restored-final.json) and
[evidence/notification-final.json](evidence/notification-final.json).
