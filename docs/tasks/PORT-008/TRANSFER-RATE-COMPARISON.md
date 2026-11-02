# Transfer-rate comparison harness

An existing matched UART/parallel harness already measures identical ordinary
VDU uploads, validates received bytes and separates submission, transmission,
local completion and ordered replies. Refresh that harness to compare the old
and optimized parallel byte loops against freshly measured UART, with the P4
admission fix held constant. The original task-only hold is superseded by the
Author's 2026-11-02 instruction to commit/push and proceed, followed by an
explicit powered, exclusive bench reservation. Software preparation precedes
the authorized physical comparison and exact incoming restoration.

**State:** Forward comparison complete; see the
[results and restoration](TRANSFER-RATE-COMPARISON-RESULTS.md). The reverse
inventory returns a separate extension boundary, without reverse bulk qualification.

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
2. [x] TR02 — Prepare matched source/build manifests and rebuild through every
   owner ROM/divisor/link check. Rebind each fixture to its exact ELF/full ROM;
   verify the private ABI bridge and optimized final-clock timing offset.
   Measure actual ROM/RAM cost of unavoidable diagnostic hooks. Keep results,
   formatting and coordination outside resident EMOS wherever possible.
3. [x] TR03 — Verify offline: byte/header accounting, first/last timestamps,
   warm-up/sample identity, incomplete/duplicate rows, timer saturation, matching
   endpoint scopes and rate arithmetic. Verify the Pi runner uses explicit
   individually invocable cases, never changes autoexec and never automatically
   replays an uncertain invocation.
4. [x] TR04 — Prepare the later physical run only after fresh bench ownership,
   actual CLI/startup evidence, exact incoming rollback preservation and matched
   firmware/fixture readback. Runner records route and each display's mode,
   verifies preselection, waits at least one second after an actual mode change,
   identifies the active arm/length visibly, and restores entry route/modes and
   flashing visible CLI. Normal reset must boot without starting tests.
5. [x] TR05 — Execute the four-arm forward matrix only when authorized. Prove
   all 8192 allocated receiver-buffer bytes after every sample outside timing.
   Verification is test-side byte comparison, not a wire CRC or substitute
   checksum. Reject short captures; preserve informative failures, original
   indices and integrity-only selection provenance. Follow the current capture-
   failure protocol and matched no-capture controls; controls do not supply
   missing byte proof. Continue independent cases only after verified recovery.
6. [x] TR06 — Restore and independently verify the exact incoming firmware pair,
   unchanged startup/listener and usable input/CLI; release collectors and bench.
   Retain manifests, raw timing/data, selection decisions and side-by-side report.
   Record preparation, fixture runtime and retrieval durations separately and
   base advance estimates on retained comparable runs, never reset deadlines.
7. [x] TR07 — Define reverse bulk coverage from existing admitted diagnostics.
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

## Prepared software checkpoint — 2026-11-02

The four-arm analyzer and documentation are committed as `11de9fe9`; current
bench authorization is recorded in `9bceb0a2`. Fifteen host checks pass. Clean
EMOS builds use source `2fc7b269` / `08301e6`, the same controller/timing profile
and builder; only the native assembly body differs among firmware source inputs.
Both exact-ROM fixtures pass the existing linked ABI bridge and native checks.
The fixed P4 partner is the retained admission-qualified source `dddc10a2`,
application SHA256 `102014003d771e1c917782e281bdde607da4632d7b255e0c2ba8285bd8c0fd45`.
No P4 rebuild or new display change is part of the comparison.

Two initial fixture builds completed within one UTC second and consequently
received a duplicate generated build ID for different ROM bindings. Neither
was invoked. The optimized preparation is marked invalid and retained; its
replacement has a unique timestamp and fresh ABI check, and is deployed under
another filename with exact readback. The refreshed batch recipe waits across
timestamp granularity and asserts uniqueness. This corrects preparation, not a
transport failure or benchmark result.

Execution order groups are baseline small lengths, optimized small lengths,
baseline large lengths, then optimized large lengths. Routes alternate inside
each group. Each individual invocation records host UTC start/end/monotonic
duration; batch calls those same independent entry points. Collectors use host
RAM-backed temporary storage; no active HTTP observations occur during timed
samples. Fresh verification preserves incoming modes 0/0 and unchanged startup;
all later cases retain those modes and explicitly settle after route selection.

The first baseline parallel 4096-byte invocation completed six zero-flag rows
and returned to the CLI, but one USB dump contained 8150 of 8192 byte lines.
It is retained as an incomplete acquisition, with no transport-corruption claim.
One Agon reset and two actual listener/read/EXIT exchanges recovered readiness;
the independent UART 4096-byte case then passed. Any later labelled acquisition
keeps the original failure and requires the matching capture-absence control.
Review also corrected the host loader to use the verified fixture pathname from
the active-pair receipt, rather than infer a sibling name; this happened before
any optimized fixture invocation.

Two later short dumps affected optimized parallel 256 bytes and optimized UART
4096 bytes; both applications completed without reported transport faults and
with actual CLI handback. The host performs the same Agon-first recovery and
retains their no-dump-control requirements. After these acquisitions, the Pi
collector defers per-byte log interpretation until closure and scans only
completion/panic markers while receiving. Thirty-two retained-log chunking
checks and every marker split pass. This is a host acquisition change, not an
EMOS/P4/fixture change or evidence establishing the cause of prior USB loss.

## Reverse inventory and separate extension boundary

The existing EMOS `projects/parprobe` MOSlet supplies private two-way
1/2/255/256/4096-byte qualification blocks. It requires the separate probe
composition, reports coarse MOS service-call time, includes admission/control
costs and retains historical CRC-based diagnostics. It is not a drop-in reverse
bulk-rate control for this ordinary format4 stream, and its historical checksum
work must not be reintroduced under current Author instructions.

A later reverse comparison needs an admitted P4 source for the same deterministic
N bytes under UART and parallel, exact eZ80 receive start/last-byte observations,
and out-of-interval byte comparisons without wire CRC/checksum additions. No
such matched ordinary-UART reverse producer is supplied by this forward fixture.
TR07 therefore remains an explicit extension boundary; the current campaign
measures forward uploads and the separately labelled small ordered reverse reply.

The proposed reverse extension assigns the deterministic source buffer and bulk
reply production to P4 test code, ordinary UART1/parallel admission and reception
to EMOS, and destination RAM, reporting and out-of-interval byte comparison to
the eZ80 application. Pi Python stages exact inputs and collects results; it
does not subtract P4 timestamps from eZ80 timestamps. A matched receive timing
binding must observe application request start and the last actual received byte
on the same eZ80 PRT clock, keeping admission, drain and echo/reply scopes
separate. The P4 admitted bulk-producer command and matching UART/parallel EMOS
receive binding are missing capabilities, not existing public contracts. TR07
therefore returns that concrete extension boundary before coding it; no wire
command, resident-byte budget or physical reverse qualification is selected by
the forward work.

## Completed forward comparison — 2026-11-02

[Results](TRANSFER-RATE-COMPARISON-RESULTS.md) and
[portable evidence](TRANSFER-RATE-EVIDENCE.json) retain the full four-arm result.
At 8192 command-stream bytes, optimized parallel measures 340.35 kB/s versus
220.83 kB/s baseline parallel (+54.13%) and 100.60 kB/s matched UART (3.383×).
UART remains faster at 256 bytes. Larger parallel rates improve 44.5–58.7%; the
4096→4097 internal-block boundary penalty remains. Ordered-reply improvement
is separately reported, without rendering or autonomous-CPU claims.

All 96 selected full 8192-byte buffers pass. 22 acquisitions retain 132 zero-flag
timing rows and 7 short USB acquisitions across 6 distinct cases. Six selected rows
use labelled acquisitions by integrity only. Every marked case passes its
60-second no-dump control with the same bound EMOS/fixture, actual CLI and no
panic; the fresh-control boot/history difference and lack of byte proof are
explicit. Negative controls do not establish the cause of USB acquisition loss.

The exact incoming full 16 MiB P4 and 128 KiB EMOS are independently restored and
compared byte-for-byte. Startup/listener, modes 0/0, admitted neutral input,
valid USB controller and Legacy CLI pass; cursor commands are sent to both
displays. No reader, listener or reset holder remains; SD stays in Agon. The
generated local archive is identified and verified in
[its archive record](TRANSFER-RATE-ARCHIVE.json).

TR07 completes the inventory and returns the missing matched reverse producer/
receive-timing capability as the explicit extension above; it does not implement
or qualify reverse bulk. The parent retains async admission, whole-request burst
capacity, reverse extension, P08-D02/warm-reset and production work. No promotion
or release tag is made by this benchmark closeout.
