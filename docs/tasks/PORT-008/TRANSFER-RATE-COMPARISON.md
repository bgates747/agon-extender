# Transfer-rate comparison harness

An existing matched UART/parallel harness already measures identical ordinary
VDU uploads, validates received bytes and separates submission, transmission,
local completion and ordered replies. Refresh that harness to compare the old
and optimized parallel byte loops against freshly measured UART, with the P4
admission fix held constant. The original task-only hold is superseded by the
Author's 2026-11-02 instruction to commit/push and proceed, followed by an
explicit powered, exclusive bench reservation. Software preparation precedes
the authorized physical comparison and exact incoming restoration.

## Existing harness and gaps

1. Reuse `tests/performance/stream_timing/`: `main.cpp`, `counter.asm`,
   `build.py`, `payloads.py`, `analyze.py`, host contract tests and the actual
   linked ABI checks. Its [README](../../../tests/performance/stream_timing/README.md)
   and [original measurement contract](STREAM-TIMING-R01.md) document the
   implemented forward upload and timing endpoints. Historical deployment
   instructions are not current execution recipes.
2. The phase variant attributes block costs, but leaves `wire_prt` zero.
   The last admission comparison therefore does not supply a new wire-rate
   comparison. Reuse the existing final-forward-byte timing variant for the
   primary rate measurement; add phase attribution only if needed, as a
   separately identified diagnostic rather than merging incompatible scopes.
3. The latest native optimization has instruction-model evidence, not physical
   throughput evidence. Existing frozen ROM bindings/fixtures cannot be reused
   against a newly linked EMOS image without rebuilding and verifying them.
4. The existing ordinary-upload harness measures eZ80→P4 bulk traffic. Its
   small reverse query response is not a P4→eZ80 bulk-rate benchmark. Inventory
   existing reverse diagnostic fixtures separately before designing that
   extension; do not label echo round-trip time as one-way receive throughput.

## Controlled comparison

Use EMOS UART1 ExCom and the same P4's ExExt parallel endpoint. This is not a
comparison with the other project's mainboard UART0/onboard-VDP sender.

| Arm | EMOS native leaf | EMOS route to P4 | Purpose |
|---|---|---|---|
| U0 | Before byte-loop optimization | ExCom / UART1 | Fresh UART control for baseline image |
| P0 | Before byte-loop optimization | ExExt / parallel | Parallel baseline |
| U1 | Optimized native leaf | ExCom / UART1 | Check for unrelated image/layout effects on UART |
| P1 | Optimized native leaf | ExExt / parallel | Measure actual parallel improvement and compare with U1 |

1. Start with EMOS source before/after `08301e6`'s native-loop change. Compose
   matched clean inputs differing only in the reviewed native implementation,
   necessary exact linked guards and build identity. Freeze the source/config
   difference explicitly; do not compare the old phase build with a new
   differently instrumented timing build.
2. Hold one P4 application constant across all four arms. Preserve the qualified
   admission-progress change, exact matched display/USB composition and native
   transport; [its retained source and results](ADMISSION-PROGRESS-RESULTS.md)
   are the starting authority, not current root HEAD by assumption. Do not
   combine the byte-loop change with a P4 parser/renderer optimization.
3. Hold board/wiring, P4 parser workload, mode 0/single buffering, keyboard and
   controller conditions, SDK/compiler, cache/output configuration and background
   activity constant. Browser frame streaming and unrelated HTTP polling stay
   out of timed acquisition. Mainboard VDP remains unchanged and identified.
4. Use exact command-stream sizes 256, 4096, 4097 and 8192 bytes, retaining the
   existing eleven-byte inline buffer-SET header and deterministic data. Thus
   useful upload bytes are 245, 4085, 4086 and 8181. Allocation/poisoning, mode
   setup, diagnostic dumps, result writes and retrieval remain outside timing.
5. Retain one warm-up and five measured samples per arm/length: 96 rows total
   for the forward matrix. Alternate route order within each image; interleave
   baseline/optimized image groups sufficiently to expose order drift rather
   than confounding every optimized sample with a later bench condition.
   Record the actual order and all firmware installations.

## Required measurements and reporting

1. **Submission:** eZ80 elapsed time from the first ordinary EMOS output call
   through its final return. This may include waiting or leave queued bytes.
2. **Sender drain:** same start to the final forward-byte observation. UART
   requires actual shift-register-empty, not just FIFO-empty. Parallel uses
   its existing final-clock timestamp, with the optimized loop's new instruction
   offset documented. Software observation delay and interrupts remain included.
3. **Local parallel completion:** same start through native cleanup and reciprocal
   UART return. This is not a software receipt or remote execution fence. Show
   no invented equivalent UART acknowledgement.
4. **Ordered processing/reply:** same start through the existing ordered reply
   after synchronous buffer SET. Count its seven-byte request and six-byte
   response separately. This is not rendering or display scanout completion.
5. Report measured command-stream bytes/s as `N / drain_seconds` and useful
   upload bytes/s as `(N − 11) / drain_seconds`, clearly labelled. Show local-
   completion and ordered-reply times separately; do not call all endpoints
   "transfer rate." Isolated payload-loop time, if separately acquired, must
   exclude setup/handovers and must not masquerade as whole-transfer throughput.
6. Tables show U0/P0/U1/P1 side by side, explicit units, median and min/max,
   P1 versus P0 elapsed-time/rate differences and P1 versus U1 rate ratio.
   Define percentages as `100 × (candidate / baseline − 1)`, separately for
   time and rate. Rank lengths by slowest baseline elapsed time first. Retain
   all raw samples; exclude warm-ups only by their declared index.
7. Retain raw PRT1 counts, nominal 72,000 counts/s at the existing divisor,
   13.8889 µs/count resolution, calibration/read overhead and saturation checks.
   Reject overflow; never subtract absolute clocks from different processors.
   Instruction-count savings and theoretical UART baud calculations are context,
   not replacements for measured elapsed time. No CPU-headroom claim without
   a separate useful-work measurement.

## Implementation and execution checklist

1. [x] TR01 — Inventory the existing fixture/validator and finite Pi collectors;
   identify the smallest changes for four-arm reports, rate columns and durable
   start/end durations. Preserve frozen fixtures and evidence. Agree any new
   controlled fixture identity before producing it.
   Selection: retain the existing r01 source and automatic build timestamps;
   only exact-ROM bindings change. Add a host-only four-arm analyzer and reuse
   refreshed finite single-case/batch Pi recipes in the ignored run record.
2. [ ] TR02 — Prepare matched source/build manifests and rebuild through every
   owner ROM/divisor/link check. Rebind each fixture to its exact ELF/full ROM;
   verify the private ABI bridge and optimized final-clock timing offset.
   Measure actual ROM/RAM cost of unavoidable diagnostic hooks. Keep results,
   formatting and coordination outside resident EMOS wherever possible.
3. [ ] TR03 — Verify offline: byte/header accounting, first/last timestamps,
   warm-up/sample identity, incomplete/duplicate rows, timer saturation, matching
   endpoint scopes and rate arithmetic. Verify the Pi runner uses explicit
   individually invocable cases, never changes autoexec and never automatically
   replays an uncertain invocation.
4. [ ] TR04 — Prepare the later physical run only after fresh bench ownership,
   actual CLI/startup evidence, exact incoming rollback preservation and matched
   firmware/fixture readback. Runner records route and each display's mode,
   verifies preselection, waits at least one second after an actual mode change,
   identifies the active arm/length visibly, and restores entry route/modes and
   flashing visible CLI. Normal reset must boot without starting tests.
5. [ ] TR05 — Execute the four-arm forward matrix only when authorized. Prove
   all 8192 allocated receiver-buffer bytes after every sample outside timing.
   Verification is test-side byte comparison, not a wire CRC or substitute
   checksum. Reject short captures; preserve informative failures, original
   indices and integrity-only selection provenance. Follow the current capture-
   failure protocol and matched no-capture controls; controls do not supply
   missing byte proof. Continue independent cases only after verified recovery.
6. [ ] TR06 — Restore and independently verify the exact incoming firmware pair,
   unchanged startup/listener and usable input/CLI; release collectors and bench.
   Retain manifests, raw timing/data, selection decisions and side-by-side report.
   Record preparation, fixture runtime and retrieval durations separately and
   base advance estimates on retained comparable runs, never reset deadlines.
7. [ ] TR07 — Define reverse bulk coverage from existing admitted diagnostics.
   Specify who produces/stores bytes and the actual source/destination timing
   endpoints; keep one-way bulk, echo round trip and small query latency distinct.
   Bring any missing EMOS/P4 fixture capability back as an explicit extension
   before coding it. No new production protocol, public GPIO bypass or per-byte
   handshaking is presumed necessary for the benchmark.

## Gates and completion

The Author now authorizes implementation and grants the powered bench for this
task. The four-arm comparison follows successful preparation, exact installation
verification and CLI readiness; it does not start unrelated experiments. Follow
[test lifecycle](../../procedures/test-appliances.md),
[test execution](../../procedures/test-execution.md),
[capture handling](../../qualification/capture-failure-protocol.md) and the
current machine-local bench record when that work is authorized. Preserve the
standing Agon-first recovery order and explicit no-monitoring boundaries.

The forward comparison is complete only with all declared valid samples and
byte proofs, interpretable endpoints, exact restoration and a retained report.
Report reverse coverage separately if deferred; do not call the entire
bidirectional pipe qualified from forward uploads. Neither benchmark completion
nor a speed improvement promotes firmware or implements the pending async API.
