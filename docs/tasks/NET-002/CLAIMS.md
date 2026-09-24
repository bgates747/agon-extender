# Transcript claim register

Read alongside [review and pinned sources](REVIEW.md). Message dates are 2026-09-23; times follow the supplied transcript. No attachment contents were used.

| ID | Speaker / time | Claim | Disposition |
|---|---|---|---|
| C01 | [pollito 15:49](https://discord.com/channels/1158535358624039014/1158753764224802877/1552406628589109308) | MOD-WIFI compatibility; Espressif AT plus SLIP/PPP | AGONLIGHT target and AT/SLIP/PPP source exist. Scoped subset, not full official AT equivalence; no independent hardware qualification. |
| C02 | [rafd 16:55](https://discord.com/channels/1158535358624039014/1158753764224802877/1552423232336953474) | Stock AT/UART1 applications and module memory concern; two firmwares | Inspected clients use MOS UART1 AT calls. One source tree with target builds, not two concurrent firmwares. Module flash-size sufficiency and user adoption not established; attachments uninspected. |
| C03 | [pollito 17:33](https://discord.com/channels/1158535358624039014/1158753764224802877/1552432752131842139) | One firmware; target builds; AgonLight2 Snail/Radiotux success | Target selection confirmed. Reported hardware compatibility remains author testimony; no precise binary hashes/test corpus supplied. |
| C04 | [rafd 17:39](https://discord.com/channels/1158535358624039014/1158753764224802877/1552434178254176307) | ZGET uses Zimodem at 115200 | Confirmed by client UART setup and AT&G path; not a transfer-speed measurement. |
| C05 | [pollito 17:41](https://discord.com/channels/1158535358624039014/1158753764224802877/1552434804778213460) | ZGET much faster than GET | Subjective report only. Different HTTP ownership and command overhead explain a plausible advantage; no comparable measured ratio. |
| C06 | [rafd 17:44](https://discord.com/channels/1158535358624039014/1158753764224802877/1552435461279060042) | Will test PPP/LCP | Future intent, not evidence of a passing test. Code implements a limited negotiation path. |
| C07 | [pollito 17:49](https://discord.com/channels/1158535358624039014/1158753764224802877/1552436725547008171) | Neo6502 test remains; seeks more clients | Explicitly untested at transcript time. Neo6502 hardware outside this review. |
| C08 | [rafd 18:13](https://discord.com/channels/1158535358624039014/1158753764224802877/1552442733506068610) | Application list | Located Snail, candidate Sijnstra Telnet, and Radiotux sources; ifconfig is closest match to named ipconfig. Exact Telnet binary identity unresolved. |
| C09 | [pollito 18:16](https://discord.com/channels/1158535358624039014/1158753764224802877/1552443600330301491) | All listed tools tested before release | Retained as independent author report, not reproduced evidence or proof of every option (e.g. Telnet SSL). |
