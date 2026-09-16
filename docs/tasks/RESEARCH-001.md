# RESEARCH-001 — P4 rendering/network pacing literature search

## Executive summary

Author requested a broad internet investigation of P02's variable composition
and web-streaming latency, starting with ESP32-P4 and widening to ESP-IDF and
Arduino-ESP32 where no specific match is found. This task researches causes;
it does not authorize firmware changes or new performance experiments.
Results will rank documented matches, plausible mechanisms and non-matches,
with primary-source links, version applicability and next discriminating checks.
Hardware voice notification closes the task for review. Golem is excluded.

## Frozen scope and evidence

P02 r45 controls: historical mainboard p9517.063ms; P4 normal29.238ms;
off17.049ms; discard17.318/45.509ms; prebuilt25.026/21.428ms. Six accepted
2400-state SW runs, one pre-marker query failure. Normal/prebuilt sends roughly
27–29 full512×384 RGB222 frames/s, mean17–18ms socket scope. Discard composition
mean6.429/13.537ms, with no admitted network sends. Game framebuffer internal;
snapshot-pool placement and boot/order differences unresolved. Do not collapse
render completion, snapshot, socket acceptance and browser presentation.

Selected local packages report ESP-IDF5.5.5 and Arduino-ESP32 3.3.11; verify
compiled configuration/provenance before assigning an upstream bug to this build.
No specific known upstream cause is assumed. P02 details remain authoritative.

## Itemized execution plan

1. [ ] R01: Pin relevant local build facts and search vocabulary; freeze this
   contract and TODO entry before external research.
2. [ ] R02: Search P4-specific official documentation, errata, issue trackers,
   examples and maintainer discussions: Ethernet/WebSocket stalls, dual-core
   contention, cache/PSRAM/internal RAM, DMA/coherency, scheduling, heap/order,
   power/clock behavior and graphics under network load. Log queries and hits.
3. [ ] R03: Where no exact P4 match appears, extend to ESP-IDF/lwIP/FreeRTOS and
   Arduino-ESP32 HTTP/WebSocket throughput and task-affinity mechanisms. Prefer
   primary evidence; label other-chip reports and unverified user claims.
4. [ ] R04: Compare promising explanations against P02 and selected local code;
   record supporting/contradictory facts, affected/fixed versions where known,
   and a falsifiable next check. Do not upgrade dependencies or implement fixes.
5. [ ] R05: Write executive findings, source ledger and ranked investigation
   sequence; deduplicate against P00/P01/P02/P06 and AUDIT-007. Commit research,
   deliver accepted hardware voice, record receipt, then stop for review.

## Deliverables and boundaries

Research in `RESEARCH-001/FINDINGS.md`, query/source ledger alongside it. Preserve
short paraphrases and links, not copied articles. Search failure does not prove
absence of a bug. Distinguish source publication time, access date and applicable
SDK versions. General API guidance is not proof of the observed mechanism.
No hardware testing, reset or flash; use the established voice path only at
completion. No emulator changes, source edits, experimental push or Golem.
Further experiments are recommendations for review, not silently self-authorized.
