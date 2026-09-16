# RESEARCH-001 — P4 rendering/network pacing literature search

## Executive summary

Author requested a broad internet investigation of P02's variable composition
and web-streaming latency, starting with ESP32-P4 and widening to ESP-IDF and
Arduino-ESP32 where no specific match is found. This task researches causes;
it does not authorize firmware changes or new performance experiments.
Results rank documented matches, plausible mechanisms and non-matches,
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

1. [x] R01: Pin relevant local build facts and search vocabulary; freeze this
   contract and TODO entry before external research.
2. [x] R02: Search P4-specific official documentation, errata, issue trackers,
   examples and maintainer discussions: Ethernet/WebSocket stalls, dual-core
   contention, cache/PSRAM/internal RAM, DMA/coherency, scheduling, heap/order,
   power/clock behavior and graphics under network load. Log queries and hits.
3. [x] R03: Where no exact P4 match appears, extend to ESP-IDF/lwIP/FreeRTOS and
   Arduino-ESP32 HTTP/WebSocket throughput and task-affinity mechanisms. Prefer
   primary evidence; label other-chip reports and unverified user claims.
4. [x] R04: Compare promising explanations against P02 and selected local code;
   record supporting/contradictory facts, affected/fixed versions where known,
   and a falsifiable next check. Do not upgrade dependencies or implement fixes.
5. [x] R05: Write executive findings, source ledger and ranked investigation
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

## Research result

See [findings and ranked next checks](RESEARCH-001/FINDINGS.md),
[query ledger](RESEARCH-001/QUERIES.md) and
[exact local build facts](RESEARCH-001/LOCAL-FACTS.json). No confirmed upstream
root cause or drop-in fix found. Clarified that snapshot slots are explicitly
PSRAM; the framebuffer is internal. Investigate real affinity/priority/locks,
PSRAM/cache interactions, and HTTP/socket/credit pacing under the existing
QUAL-003 ownership. No new performance measurements or firmware changes.

Hardware closeout: accepted British voice invoked, fresh stage6/audio receipt
verified, original startup unchanged, SD service exited to Legacy MOS. See
[notification receipt](RESEARCH-001/notification.json). Human hearing/review
pending. All research steps complete; no hardware performance experiments.

## Implementation scouting — Author-authorized extension

The Author approved this extension after asking whether the search covered
contention outside HTTP, how to identify excellent implementations whose
quality is not advertised, and how to weigh Espressif examples. The accepted
approach is to follow implementations and evidence back to their authors;
reputation is supporting context, not proof of correctness or human authorship.
Espressif examples receive serious consideration for API/hardware contracts,
but may optimize isolated throughput or teaching rather than mixed workloads.
Apply the same correctness and reproducibility standards to independent work.

### Frozen plan (continuation; no sample firmware execution)

6. [x] R06: Record this discussion, evaluation rubric and scope; freeze before
   investigating candidates. Search beyond HTTP: concurrent P4 multimedia,
   low-latency audio, emulators/graphics, memory-copy and driver pipelines.
7. [x] R07: Discover a broad candidate pool, then inspect source/history/tests
   of approximately five promising P4 implementations. Include vendor and
   independent work. Pin revisions and separate code inspection, author claims,
   published measurements and independent replication. Track negative findings.
8. [x] R08: Rank by relevance and evidence, not stars, affiliation or impressive
   demos. Trace memory placement, buffer ownership, lock duration, task/IRQ
   placement, backpressure, overload behavior and instrumentation where present.
   Describe unresolved gaps rather than invent a complete audit.
9. [x] R09: Write a reviewable shortlist with exact source links, applicability
   to our silicon/SDK, limitations and one proposed reproducible experiment per
   candidate. Distinguish copying a diagnostic technique from changing VDP
   semantics. Reuse QUAL-003 follow-ups rather than duplicate implementation tasks.
10. [x] R10: Verify documentation/provenance, commit locally, deliver established
    hardware voice and record a fresh receipt, then stop for Author review.

### Rubric and authorization boundary

Prefer concurrent workloads, timing distributions/worst cases, explicit memory
and ownership, bounded locks, correctness under load and independently repeated
results. Average FPS, stars, screenshots, "optimized" claims and vendor branding
alone are weak evidence. Record absent evidence. No inference that an author is
human from writing style, and no use of AI-detection guesses as a quality filter.
Source inspection may identify flaws but cannot certify firmware correctness.

Read-only source acquisition into ignored local research material is allowed.
Do not build, flash, run, benchmark or test any sample firmware before Author
review. No dependency installation, SDK changes, production source edits, new
hardware experiments, reset, Golem work or experimental push. The sole hardware
action is the already accepted attention voice at completed review readiness.
Deliver `RESEARCH-001/CANDIDATES.md` plus query/provenance ledger; retain existing
findings and make the relationship clear for someone without the chat history.

### Scouting review checkpoint

[CANDIDATES.md](RESEARCH-001/CANDIDATES.md) records the discussion, five ranked
implementations, pinned source behavior, numerical caveats and proposed checks.
[CANDIDATE-SOURCES.json](RESEARCH-001/CANDIDATE-SOURCES.json) preserves revisions,
selected source hashes and history samples. First choices: adapter ownership
contracts and micro-mp3's concurrency measurement method; no drop-in fix found.
No sample built, run, flashed or tested. No dependency/source/bench changes.
R06 contract was frozen in7909347 before inspection. R07–R10 complete. Source hashes and document references verified. Hardware
voice returned a fresh audio receipt; startup unchanged and Legacy MOS restored.
See [scout notification](RESEARCH-001/scout-notification.json). Human hearing
and implementation review remain pending. Stopped; no experimental push.

Author reaction during scouting: expressed interest in a future Vectrex console
emulator project, then explicitly directed continuation of this research task.
That interest does not authorize running the external Vectrex firmware now.

Author-directed follow-up: inspected agon-utils AGM/RLE sources read-only.
[AGM-RLE.md](RESEARCH-001/AGM-RLE.md) records actual byte formats, non-expansion
proof, unused delta helper and proposed P06 integration checks. No utility or
firmware changes, build, execution or bench test.

### Author-directed sequencing — candidates before RLE

Exhaust the five initial candidates C1–C5 in CANDIDATES.md before resuming the
AGM/RLE investigation, including its proposed host-side prototype. The completed
scouting/source reads do not by themselves satisfy this dependency: record the
findings and disposition of each candidate's relevant avenue. RLE is deferred,
not discarded. Existing review gates still apply; this sequencing instruction
does not authorize sample firmware builds, flashes or tests. P06 owns any later
encoding experiment and retains the raw eight-bit full-frame performance goal.

### C1 investigation — authorized source-only review

Author selected medium effort and one candidate at a time. Investigate
esp_lvgl_adapter now; no build, firmware execution, flash or benchmark. Hardware
voice is the only bench action. Stop after C1 for review; do not start C2 or RLE.
Apply the same evaluation structure to each later authorized candidate:
question, mechanism trace, local comparison, discriminating check, measurements
if separately authorized, and evidence-based disposition.

11. [x] C1-01: Freeze scope and pin source/baseline; define the rendering/output
    contention question and distinguish LCD scheduling from web delivery.
12. [x] C1-02: Trace buffer ownership, locks/waits, task/ISR scheduling, memory,
    completion and overload through the adapter's relevant paths.
13. [x] C1-03: Compare with Extender and retained P02 source/configuration;
    identify already-present mechanisms, actionable differences and unknowns.
14. [x] C1-04: Write source-linked findings and disposition with the smallest
    proposed discriminating check. No invented performance numbers or build.
15. [ ] C1-05: Verify documentation, commit, hardware voice with fresh receipt,
    then stop for Author review. C2–C5 remain pending authorization.

C1 source findings: [review report](RESEARCH-001/C1/README.md). No immediate
throughput fix established; preserve useful ownership/LCD contracts and propose
P01c/d wait attribution. Source review complete, measurements not authorized.
