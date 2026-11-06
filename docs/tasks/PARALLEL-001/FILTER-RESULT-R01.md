# Filtered real-module comparison — bench62

The fixed VALID filter passed the same bounded24-turn real-module replay that
failed after two completed frames without the filter. This is useful evidence
for the candidate, but one pass does not establish the electrical cause, long
reliability or Wolf integration. Extender restored the incoming working UART
pair and released the bench cleanly before admitting Wolf's next cohort.

## Matched result

Failures appear first. Both cases use the same native/client/module/assets and
24-pair corpus, EMOS8270, strict proof, byte counts and DMA/deadline contracts.
The P4 fixed two-IO-sample VALID filter is the selected candidate difference.

| Observation | Unfiltered60 | Filtered62 |
|---|---:|---:|
| Native decisions | 2 | 24 |
| Native completed FRAME returns | 2 | 24 |
| Module completed frames | 2 | 24 |
| Host intents received | 2 | 24 |
| Native first error | SUBMIT132 | 0 |
| Native result | Interrupted/fault; original RAM retained | 0 |
| Positive close / cleanup / end | Incomplete | 1 / 1 / 1 |
| Full24-pair workload | Failed | Passed |

The unfiltered P4 received all118 bytes/DMA complete but counted three VALID
edges against the unchanged strict two-edge proof. Native first trace retained
three unsent control-prefix bytes with peer CTS blocked for600 nominal120Hz
MOS counts. The filter result has no first pipe error, BUSY retry or RFC refusal.
This comparison does not establish which physical transition caused the earlier
extra edge. The original60 RAM, serial evidence and diagnosis remain immutable.

Filtered62 additionally records28 presentation records, ordered TCP close, joined
host/P4-reader tasks, and exact post-getter feature absence/callback retirement.
Its draw counter132 total/max10 nominal MOS ticks includes transport and is not
an isolated renderer measurement or optical FPS. Command stack minimum changed
from2644 to1956 bytes; module-load memory witness was valid7.

## Exact selected identities and retained evidence

1. Candidate app1764368B `37ba69e3648ea2e7663d071149acc057fab64f8546af3d784afa711505f8e38e`,
   build `net-004-r04-b2026-11-06-09-24-54Z`, source
   `f3a102d574df0d76a0bfab7676b9a5807cbdffd8`. Its composed1765376B app-sector
   span including the known1008-byte suffix is `bfb8962872bd832c5627a49cbf68d8a82bd3774b09aa30bf0eee5b2b9bcf2cbf`.
2. Full131072B EMOS `8270ecd709138fe5ae617a91d5d365eeede0738025d5043fc790541b19b8f281`;
   same native32011B/dcd737c8, modulef797, assets3cdf, corpusca052 and run.py
   a308 as the preceding unfiltered comparison. Exact remaining hashes are in
   the [frozen owner/consumer selection](FILTER-ASSIST-FREEZE-R01.json).
3. Native983B result SHA `185c5b4d0188155f40ad4d340287bb683aeafc1d3a473f14c87c13d545ab4c1c`;
   runner161B receipt `16c3fa6d9c3f672388045a5ea8fe33dc0eac4c310f3498bcc7cc2ea35c33c348`;
   P4 passive1439B capture `92eb2eb963a863841dea85caee66cf6dc1c0dd44c912a27f5abf265b3e341ca5`.
   Owner-local result pins retain the complete collected/host/getter/stopped
   evidence. Consumer paths remain in its immutable filtered-r01 run directory.

## Restoration and actual custody disposition

Extender resumed only after MechAgon's actual stopped return. The full incoming
UART EMOSa25f/131072B and UART P4d9bcb/maximum1765376B touched span629a were restored
and independently compared. Mainboard5d657/profile8, bootloader, partitions,
NVS, startuped403 and listener0566 were unchanged. Final getter4999 confirmed
exact feature absence, ordered clear, callback restoration and no retained
buffer; fresh raw mode0/callback0/Legacy0, actual CLI/cursor, files, neutral input,
offline listener, idle worker, free USB and joined actors passed.

Actual62 release: **2026-11-06T22:15:09.627226UTC**. SD remained mounted, RAM holds
the getter. Wolf's167-pin hardware03 cohort received a fresh normal63 grant and
sole-operator handoff; no62 token or temporary filter pair was reused. Extender
stopped all target access at that grant. The next independent
[repeatability tranche](REPEAT-PHYSICAL-R01.md) is preparation under a separate
normal reservation, with no second test added to62.
