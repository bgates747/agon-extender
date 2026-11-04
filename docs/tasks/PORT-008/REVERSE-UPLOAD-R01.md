# Parallel uploads — reverse bulk and file-service integration r01

Improve host-to-mainboard deployment by reusing the staged upload service and
replacing its P4→eZ80 UART payload leg with a qualified eight-bit parallel path.
The Author authorizes this tranche on2026-11-03 after accepting BENCH-013's first
listener-adoption tranche. Keep the existing host workflow and UART baseline;
speed, scarce EMOS space and one admission per requested payload remain central.

## Authority and boundaries

1. Extender retains the Author-assigned physical checkout; other projects may
   queue but receive no automatic slot. Send no peer progress/instruction
   notifications until the Author opens the bench for their use. The Author
   receives completion/review questions directly in chat, following the current
   standing instruction against question-dialog tools.
2. Preserve the installed accepted sequential-reader utility and exact incoming
   firmware/startup/modes. Source assessment and host checks may proceed now.
   A new wire/admission or DMA-completion design must resolve the remaining
   architectural decision before dependent firmware implementation or flash.
3. Implementation owners remain Extender/P4 and agon-emos/eZ80. The public MOS
   API, ordinary VDU routing and native mainboard VDP are not replaced. EMOS
   retains all shared-pin/admission ownership. No raw application GPIO bypass,
   software CRC/checksum, per-byte acknowledgement or uncertain replay.

## Bounded research précis

1. Official read-only baseline: documentation
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, MOSv3.0.2
   `8336409351ee5314e02801a7b72a4f1bb5282519`, VDPv2.16.0
   `c7ac293d2aa81ddfa693390549bcd909069c8fc3`. MOS/VDP references are clean at
   those tags. [GPIO](../../../../../agon-docs/docs/GPIO.md) establishes physical
   sharing; [ffs_fwrite](../../../../../agon-docs/docs/mos/API.md#0x83-ffs_fwrite)
   supplies filesystem result and byte count. Do not replace this with a new
   resident filesystem implementation.
2. Source assessment starts from Extender `8aa3245d39f62202719226db64b67e305c91688b`
   and EMOS `08301e6d28f5cdd6a8bb01aa6806b6d4ddaf816c`, not an assumption that
   either HEAD equals installed firmware. Installed artifact identities and
   rollback evidence remain in the ignored bench record.
3. EMOS [native byte loop](../../../../agon-emos/src/emos_parallel_native_body.inc)
   generates CLOCK in both directions; reverse samples Port C after the edge
   pair. READY is sampled as an abort level, not a per-byte acknowledgement.
   The guard/coordinator bounds a call to4096 bytes and returns ownership to
   UART after each admitted block. It cannot be called repeatedly while
   claiming only one whole-file admission.
4. P4 [native adapter](../../../vdp/video/extender/transport/p4_native_payload.cpp)
   uses external-clock eight-bit PARLIO TX, one queued transaction and internal
   DMA payload storage. Its guard/egress cap is4096; ordinary return buffering
   and the current EMOS256-byte fetch policy are not a bulk-file contract.
   Preserve byte/VALID completion and pad-release distinctions.
5. The pinned ESP-IDF5.5.5 TX driver explicitly supports external PSRAM buffers
   in `components/esp_driver_parlio/src/parlio_tx.c`. Ordinary non-loop TX uses
   a0x7FFFF-bit frame limit on P4, so raising4096 alone cannot admit a65536-byte
   non-loop transaction. Loop TX can link the payload circularly and does not
   produce ordinary transaction-done completion. It requires a different,
   justified exact-length/VALID stop contract. Software support is not physical
   qualification; the earlier project PSRAM experiment remains unqualified.
6. [Official TX documentation](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32p4/api-reference/peripherals/parlio/parlio_tx.html)
   defines borrowed source lifetime through completion and loop-buffer behavior.
   Local pinned driver, P4 HAL and SoC capability files own exact implementation
   details; keep their hashes and excerpts in the ignored research receipt.
7. The accepted file utility has5277 bytes between BSS end and its MOSlet limit
   for shared heap/stack. A4096-byte extra buffer leaves1181 bytes before new
   code/runtime costs; a full upload cannot live there. The utility can write
   bounded slices through existing FatFS calls. Because EMOS generates CLOCK,
   it can stop clocking while the utility writes a slice without demanding a
   per-byte P4 acknowledgement; this requires a new retained transfer owner.

## Work and gates

1. [x] RU01 — Verify exact source/SDK limits, current reverse cores and relevant
   host failure/bounds checks. Retain no fabricated hardware rate or headroom
   claim. Quantify how many4096-byte admissions representative files need and
   the source-storage lower bound for a whole-file P4 DMA source.
2. [x] RU02 — Resolve BENCH-013 B13-D02 with a concrete recommendation before new
   carrier code: keep the existing host/staging/file semantics and choose the
   bounded whole-payload implementation below. Record an accepted material
   decision in its ADR/architecture owners. Allocate no new global MOS ABI or
   wire identifier until that contract is explicit.
3. [x] RU03 — After RU02, implement the selected carrier in the owning source
   checkouts. Keep P4 file I/O and EMOS utility file policy outside resident
   loops where practical. Bind logical payload length, buffer lifetime, busy
   refusal, exact finish, failure fencing and non-replay behavior. Report ROM,
   RAM, P4 storage and eZ80 CPU costs.
4. [x] RU04 — Exercise actual retained cores/SDK boundaries and linked eZ80 code:
   exact first/last bytes, short/tail lengths, filesystem pauses, DMA cleanup,
   owner/busy/refusal and partial failure. Then build identified matched
   candidates through owner wrappers and all mandatory link/ABI checks.
5. [x] RU05 — Prepare a finite physical comparison only after required protocol,
   deployment, reset/rollback, SD-layout and test-lifecycle review. Preserve and
   verify incoming components. Prove the reverse source and full received file
   bytes outside timing. Keep payload, admission, SD/HTTP and total deployment
   elapsed separate; compare matched UART and parallel variants.
6. [x] RU06 — Restore exact incoming components unless the Author explicitly adopts
   the tested change, restore normal CLI/cursor/input and idle services, and
   retain Extender checkout. Publish scoped results/limits; raise the requested
   attention message in chat. No full suite, peer notification or bench release follows
   automatically from completing this tranche.

## RU01 assessment results — 2026-11-03

| Upload size, bytes | Existing4096-byte admissions | Minimum whole-source P4 storage, bytes |
|---:|---:|---:|
| 1,100,000 | 269 | 1,100,000 |
| 65,537 | 17 | 65,537 |
| 4,096 | 1 | 4,096 |
| 256 | 1 | 256 |

Rows rank by largest existing admission count. Source-storage figures exclude
DMA descriptors, alignment and other live resources; they are not free-memory
measurements. The old two-second physical block deadline and single-block
completion cannot simply be relabelled as a large-file contract.

Unchanged maintained-source host checks pass:

| Check | Result | Limit |
|---|---|---|
| Paired reverse cores |48 cases pass|Modeled wires; no physical speed claim|
| Actual P4 adapter/handover/egress |213 cases pass|Fake SDK/peripheral boundary|
| Retained ExExt internal DMA payload |246 cases pass|Existing4096-byte behavior, not PSRAM or larger transfers|
| Paired block ownership/control |183 cases pass|Modeled physical lifecycle, no GPIO timing|

Native runs preserve AddressSanitizer/UndefinedBehaviorSanitizer checks. Initial
sandbox runs encountered LeakSanitizer's documented ptrace incompatibility;
unchanged native reruns pass without source or sanitizer suppression. This is
an execution-environment correction, not an Extender hardware fault.

The SDK source is pinned at `b774170ff46c393eeb5e495ea37936038d3f4f4f`.
Source hashes, resource arithmetic and complete logs are retained in ignored
`agents/port008-reverse-upload-r01/`. No firmware, listener, startup, mode or
other target state is changed by this assessment. Extender retains generation9.
The Author subsequently accepts RU02: whole-file P4 PSRAM source. No new file carrier is physically qualified yet.

## Accepted carrier decision — B13-D02, 2026-11-03

The Author selects the first prototype: P4 retains one complete admitted upload in aligned
PSRAM for DMA, while the eZ80 file utility receives small slices and writes them
to Agon SD between clocking intervals. One payload admission covers the file;
there is no per-slice UART negotiation or acknowledgement. The P4 validates
capacity before admission and never promises a file larger than its actual
retained source capacity. This spends P4 PSRAM to keep the first implementation
small and avoid streaming refill races. The exact-length loop-DMA stop, source
release and buffer lifetime require explicit implementation/qualification.

Deferred alternative: P4 fills/recycles bounded source buffers from its SD spool during
the same admitted file transfer. This saves whole-file PSRAM and handles larger
uploads, but needs a proved pause/refill protocol and protection against TX idle
data being clocked while a refill is late. Existing abort-only READY semantics
do not already implement that behavior. Do not silently use repeated4096-byte
OFFERs as the production alternative to the Author's whole-request requirement.

The [accepted decision](../../decisions/ADR-2026-11-03-whole-file-parallel-uploads.md) owns source storage and clock/SD policy. Preserve the shared UART/parallel semantic contract. RU03 now proceeds; exact private wire operations, length/VALID completion, progress bounds and cleanup are implementation obligations to prove before hardware use.

## RU03 implementation contract

1. The candidate utility explicitly selects `--fast --parallel`; omitting
   `--parallel` keeps the same binary on UART for matched comparison. A zero-
   length private begin query checks EMOS support before advertising presence.
   Candidate SD fast-v2 HELLO bit0x80 advertises SD_PARALLEL_WRITE(operation15).
   P4 retains the existing BEGIN/FINISH/ACTIVATE file policy. One operation15
   request binds the active upload ID and complete32-bit size; its one terminal
   response follows physical return and all utility SD writes. No per-slice
   UART request, ACK or automatic replay of that operation is permitted.
2. Candidate-only ext.sdlink operations7/8/9 let the admitted manual Legacy
   listener begin(total32), read(at most512 bytes) and end(abort flag). EMOS
   reserves its existing serializer and actual shared-pin parking across calls.
   The utility owns FatFS and suppresses UART presence while the pipe is parked.
3. P4 reserves whole-source PSRAM and loop-DMA resources before offering capacity.
   DMA source length rounds up to64 bytes for the pinned SDK; EMOS clocks only
   the logical file length. Padding never becomes received file data.
4. The existing reciprocal physical handover remains. During payload, P4 uses
   hardware CLOCK counting gated by VALID, plus the complete VALID pulse, to
   establish exact length before stopping loop DMA and releasing data pads.
   EMOS emits no inactive preamble/tail clocks for this reverse payload. Known
   partial-file failure never activates the stage; uncertain cleanup retains
   ownership/source and fences further admission until recovery.
5. P4's console core owns all driver/parking operations; its file worker owns
   PSRAM staging and the existing file queue. A private retained mailbox joins
   these owners. P4 suppresses the ordinary five-second presence expiry only
   for the physically admitted bounded bulk request, without manufacturing
   heartbeats. Ordinary traffic and the UART baseline preserve their policy.
6. P4 reports PSRAM/DMA preparation in microseconds and physical admission/return
   overhead in milliseconds. Its active interval includes eZ80 clocking and
   foreground SD-write pauses; it is not pure wire time. Existing staging and
   complete mainboard-job microseconds remain separate. Status exposes the
   retained carrier phase/outcome without adding per-byte eZ80 instrumentation.

## Implementation evidence — 2026-11-03

1. The experimental P4 carrier is committed at `f1d10e46`. Its physical-build
   source starts from the incoming r27 display/input revision `67dfc55b`, with
   the carrier applied at `336a17f3`; building the older root display branch
   would not preserve the incoming display implementation. The first full
   native P4 build and validation pass. The graphics-timing diagnostic is
   omitted because the existing parallel boot profile excludes it.
2. Linked eZ80 instruction checks pass1034 cases, covering lengths1..512,
   initial interrupt states, exact bytes/edges, READY abort and register/stack
   preservation. They are CPU models, not physical GPIO timing measurements.
3. The isolated EMOS profile passes the owner firmware wrapper and its complete
   linked ABI, UART divisor, pad and ROM checks. Its unversioned image uses
   128880 ROM bytes, leaving2192 bytes, with3230 BSS bytes. Against the retained
   older native-payload/controller profile this is250 additional ROM bytes and
   eight BSS bytes; these are different payload implementations, not an estimate
   of the entire parallel feature versus ordinary production. Excluding the
   unused older native payload/coordinator saves1270 ROM bytes compared with
   the first duplicate-kernel composition.
4. Preserve the source lifetime across all DMA cleanup. ESP-IDF5.5.5's TX-unit
   destructor can partially free resources before a later deletion fails;
   retrying that destructive call risks double free. The carrier fences a failed
   delete and retains its borrowed source until recovery. This is a pinned SDK
   cleanup constraint, not ordinary successful-transfer overhead.
5. Boot recovery intentionally reaches UART with a historical failed flag set.
   The existing handover begin operation clears it. Admission therefore checks
   actual UART phase and current ownership, rather than rejecting the historical
   flag before begin; active transfer failures and unrecovered phases still
   fence. Paired coordinator checks cover fresh boot and unrecovered refusal.
6. No target firmware, utility, startup file or physical mode has changed during
   these offline checks. Identified matched builds and finite physical comparison
   remain required before claiming throughput or working hardware.

## Finite physical comparison plan

1. Extender asserts its retained central lease before each target access. The
   Pi records fresh input/service/port state, invokes the canonical listener
   explicitly, reads startup and canonical utility, then uses a separate
   read-only SAVE batch to preserve full EMOS and entry mode bytes. Startup
   must contain no RUN/EXEC before any authorized reset/flash reboot.
2. The Pi stages and completely reads back candidate and rollback EMOS images
   under a fresh `/extender/install` directory. The private candidate MOSlet
   uses a distinct `/emos` name solely for comparison, leaving canonical
   sdserve unchanged; the Pi never writes/removes that renamed utility while
   it executes, because its inherited self-write guard protects sdserve.bin.
3. The Pi observes explicit FLASH of candidate EMOS through its automatic
   reboot, then holds Agon through the independently commissioned reset line.
   P4 installation first preserves fresh complete flash, verifies its incoming
   application identity, writes only the candidate application sectors and
   independently reads the complete flash back. Bytes outside those sectors
   must match. No native mainboard VDP flash or wiring change is permitted.
4. The Pi verifies P4 initialization before releasing Agon, then verifies fresh
   input admission, actual CLI/listener execution and complete candidate EMOS
   readback. Any uncertain flash, boot, job or ownership transition stops
   dispatch; standing recovery does not replay the uncertain operation.
5. Compare the same candidate utility using `--fast /` and `--fast --parallel /`
   with distinct scratch files, in ascending sizes0,1,257,65537,1100000 bytes.
   Host compares every returned byte outside upload timing. Zero bytes exercise
   the empty-file policy, not physical parallel throughput. Stop the cohort at
   its first unexplained defect and retain raw evidence for bounded repair.
6. Report complete mainboard-job microseconds and host elapsed seconds side by
   side; separately report HTTP staging, PSRAM preparation, active receive/SD
   writes and handover scopes. Rank results by worst parallel speedup first;
   percentage time reduction is100*(UART-parallel)/UART. No pure wire rate or
   optical pass follows from these counters.
7. Unless the Author explicitly adopts the result, restore exact incoming EMOS
   and P4 application sectors, independently read back and compare them, and
   verify unchanged canonical listener/startup. Restore entry route/modes,
   visible flashing CLI and neutral input, close readers/holds/jobs and retain
   the central checkout. No peer progress notification or automatic release.

## Identified owner build

EMOS source `6ececd56` produces experimental
`agon-emos-v0.1.27-b2026-11-03-22-15-34Z`:128918 ROM bytes,2154 free. Its full
128KiB padded ROM is
`855aa732ee9bd5def7cb92b52a1521d696330a6f260ad11288f7aeab7fe7dc57`.
All owner-wrapper link checks and1034 instruction-model cases pass against this
identified image. The extra38 bytes versus the earlier unversioned measurement
are identity strings, not another receive implementation.

The same owner commit produces private MOSlet
`sdserve-v0.3.0-b2026-11-03-22-15-36Z`,26449 bytes. Its BSS ends at0xB7404,
leaving3068 bytes shared by heap and stack before the0xB8000 limit. This is
linker headroom, not measured maximum runtime stack usage. Both builds retain
experimental task scope; the inherited utility manifest's draft label and
production selection are unchanged.

Final P4 experimental build `port-008-upload-r01-b2026-11-03-22-16-31Z` uses
clean source `18b81835748e9f148537371e9dfd7cb510a81487`. Full native build and
validation pass. The1850816-byte application is
`8d507a2ccd44f372ea34ef431df4fcd159f16dea1d61cde02a73ab7e01bb2518`.
Its partition bytes and selected display/input/power/reset configuration match
incoming r27, apart from the declared parallel boot/upload selection and omitted
graphics-timing diagnostic. Source differences within video are confined to
the carrier, console integration and SD service; display source is unchanged.

## Physical execution state

Fresh entry preservation and complete staging/readbacks pass. Startup and the
canonical accepted listener remain unchanged. Candidate EMOS FLASH completes
with its exact new identity observed through the proven passive printer mirror.
Matched P4 installation and complete flash verification pass; non-application
sectors are unchanged. Agon is released and full installed EMOS, actual CLI,
startup/canonical utility and neutral input pass. The first finite comparison
stops at the preparation refusal recorded below. Both known failed preparations
are reconciled; the listener is stopped and the candidate pair remains at an
idle CLI while the bounded fix builds. Detailed operations and private journals
remain in the ignored tranche directory; no whole-matrix acceptance is claimed.

### RU05-F01 — Large-source preparation refusal

The first finite cohort stops after the1.1MB parallel upload returns local
preparation error5. P4 reports one completed HELLO record, zero admitted/written
bytes and no active physical carrier; the foreground service and neutral input
remain live. All UART cases and parallel0/1/257/65537-byte complete readbacks pass.
This is a preparation failure, not a proved length/VALID or filesystem fault.

1. Preserve the terminal job and raw cohort. Verify the destination was never
   created, then deliberately discard that known failed P4 job without replay.
2. Inspect the pinned source and capture P4's actual driver error during one
   separately recorded preparation diagnostic using a new job/destination. A
   passive USB open must preserve the current boot; stop if it does not.
3. Correct only the demonstrated source/resource limit, add a meaningful
   regression at its actual boundary, and rebuild through the native wrapper.
   Keep all ownership, exact-count, startup and rollback checks.
4. Resume physical checks with new case identities only after reconciling the
   failure. Do not overwrite the first cohort or claim its whole matrix passed.

The separately named diagnostic confirms `gdma_new_link_list: no mem for link
list items`, reached from PARLIO TX DMA setup. It preserves the P4 boot and
again stops before BEGIN/admission; both known failed jobs are deliberately
reconciled and the listener exits normally. PSRAM still has over26MB available.
The carrier source allocation is not the exhausted resource.

The pinned SDK deliberately allocates both complete TX descriptor arrays from
internal DMA SRAM by default. P4 PARLIO uses AXI-GDMA, and that same SDK's
`components/esp_hw_support/test_apps/dma/main/test_gdma.c` explicitly exercises
AXI descriptor lists in external memory. The local remedy selects the existing
`items_in_ext_mem` flag in a hash-bound generated TX derivative for the explicit
upload profile only. SDK source, RX, DMA alignment/cache/encryption handling,
wire timing and ownership remain unchanged. Removal condition: a selected
upstream driver exposes equivalent storage selection, or this carrier is retired.
The native validator requires the exact derived bytes, sole compile action,
PARLIO archive membership and final ELF link; ordinary profiles reject it.

### RU05-F02 — Large-payload terminal proof disagreement

The descriptor-corrected image passes build/link validation and independent
installation verification. Its fresh cohort again passes UART all sizes and
parallel through65537 bytes. The1.1MB bulk now runs: EMOS returns success for
operation15 after roughly9.45s of receive/SD activity, but P4 rejects its terminal
proof with protocol error3. No FINISH/ACTIVATE follows. UART and input remain
healthy; the cohort stops. Do not label this a data or counter defect yet.

1. Preserve the failed job/status and independently copy/download the closed
   scratch stage through an explicitly invoked MOS batch, without activating
   its destination. Compare every byte outside timing.
2. Retain physical outcome and final CLOCK/VALID observations in P4 job status
   after resource retirement. Add no eZ80 diagnostic, wire checksum or byte ACK.
3. Exercise the actual polling race where VALID closes between CLOCK and VALID
   samples. Keep CLOCK freeze before VALID freeze and exact counts; fix only
   source-proved sequencing errors without weakening acceptance.
4. Build/verify the bounded correction, then use new paths for subsequent
   physical observations. Original cohorts and stages remain diagnostic evidence.

Normal Escape closes the utility's active stage; a new HELLO cannot take over
an active transaction. The subsequent explicit COPY/GET proof matches all
1100000 original bytes. No failed destination is activated. P4's disagreement
is therefore a false completion rejection in this observed case, not corrupted
payload bytes.

The host regression reproduces a real poll-order defect: the final CLOCK and
VALID closure can occur after the first CLOCK count read but before the VALID
count read, which the old code immediately labels short. Snapshotting physical
VALID closure before both reads defers freezing to a coherent poll. CLOCK still
freezes before VALID; exact counts and malformed/extra-pulse refusals remain.
The original fails the new deterministic regression; the correction passes154
leaf cases,15 paired coordinator cases and the retained counter/HTTP checks.
P4 job status also retains its physical outcome and the last count values used
by the proof after resource retirement, without extra peripheral reads or eZ80
traffic. Physical confirmation of the corrected large-file completion remains.

The next fresh cohort runs the previously failing parallel1.1MB case first,
followed by its smaller cases and all UART baselines on the same final P4 image.
Each nonempty parallel result must retain outcome complete, CLOCK count equal
to its requested bytes and VALID count2, in addition to independent full-file
readback. This changes diagnostic order, not the workload set or success gates.

## Final finite comparison — 2026-11-03

All ten upload/independent-download pairs pass full byte comparison. Every
nonempty parallel job reports complete, exactly its requested CLOCK count and
VALID count2 after resource retirement. Zero bytes exercises empty-file policy
without starting parallel DMA. There is one bulk operation per nonempty file,
not one per512-byte SD-write slice.

The exact experimental pair is P4
`port-008-upload-r01-b2026-11-03-23-15-49Z`, source
`b1a64b209e496f2b148f49989756d7581f684e74`,1851168-byte application
`429cd4cd3993ed16816daa8c7574e723d4959461ea7a51ef4dd4129647d3b348`,
with the identified EMOS/utility above. Native build, exact driver derivative,
compile/archive/ELF agreement and independent installation checks pass.

### Complete P4-to-mainboard job

Rows rank by lowest elapsed reduction first, excluding the empty-file control.
Positive reduction means less time:100*(UART-parallel)/UART. P4 job time includes
file/control operations, PSRAM preparation, receive/SD writes and UART return;
it excludes preceding HTTP staging and independent GET verification.

| Payload, bytes | UART job, seconds | Parallel job, seconds | Time reduction |
|---:|---:|---:|---:|
| 1 |1.782485|1.785766|−0.184%|
| 257 |1.787077|1.787267|−0.011%|
| 65537 |4.182436|2.361719|43.532%|
| 1100000 |42.199940|11.515378|72.712%|

Empty-file control:1.759897/1.756518 seconds UART/parallel-selected; neither uses
the physical parallel payload path. The tiny-file differences are single
observations, not evidence of a meaningful performance ranking.

### Host deployment elapsed

These include HTTP staging, the complete P4/mainboard job, client observation
and release. Independent GET/byte verification follows outside these intervals.
Rows rank by lowest host-time reduction first.

| Payload, bytes | UART host, seconds | Parallel host, seconds | Time reduction |
|---:|---:|---:|---:|
| 257 |2.132438|2.130480|0.092%|
| 1 |2.146112|2.129796|0.760%|
| 65537 |4.566449|2.763881|39.474%|
| 1100000 |44.630342|14.345858|67.856%|

The1.1MB host upload is3.111× faster. Its parallel preparation is233.031ms,
armed receive/SD-write interval9519ms and physical handover2ms. Across nonempty
cases handover is1..3ms. The active interval includes SD-write pauses; it is not
pure wire time and cannot be compared directly with retained forward VDU drain
rates. The large-file UART/parallel jobs use5193/5 protocol records respectively.
Download payloads still use UART; this tranche does not speed that direction.

The complete ten-case cohort takes189.220 wall seconds, including independent
GET verification (roughly45.4 seconds per1.1MB GET). Preparation/build/flash and
restoration are separate. P4 job/preparation use `esp_timer` microseconds;
physical subintervals use millisecond ticks; host individual jobs use the Pi's
monotonic seconds and250ms observation cadence. Overall start/end are Unix wall
seconds. No external clock calibration, latency distribution or optical pass
is claimed. Original failures, exact payload-copy proof, final rows and all
component receipts remain in the ignored tranche evidence directory.

This completes the bounded transfer experiment, not production acceptance,
canonical paired qualification, ExCom coverage or the broader PORT-008 task.
Exact incoming restoration passes. P4 application sectors are independently
read back and its complete expected flash image is freshly verified against
the preserved incoming image; full EMOS ROM is saved/read back byte-for-byte.
Canonical listener and complete startup are unchanged. The stopped owned
temporary MOSlet is removed; supporting payloads and informative evidence remain.
Actual Legacy CLI, entry mode0 on both displays, visible/flashing cursor controls,
neutral admitted input, idle job/listener and free serial ports pass. Cursor
controls are not an optical observation. No reset holder remains; SD stays
mounted and Extender retains its central checkout. No peer progress notification,
production selection/tag or downstream task follows automatically.

## Author-directed working trial installation and review gate

After reviewing the passing comparison, the Author authorizes installing the
exact tested P4/EMOS/private-listener combination and updating current operation
documentation. Extender must stop for Author review before granting Wolf time.
This changes the previous restoration endpoint; it does not select a production
release, authorize broader qualification, or authorize consumer execution.

1. Preserve and freshly verify the incoming component/startup identities; stage
   the exact identified experimental ROM and private MOSlet under fresh owned
   paths. Keep the accepted canonical UART listener unchanged.
2. Install only the matched experimental EMOS and P4 application, verify full
   ROM and P4 application independently, and verify preserved surrounding flash.
3. Perform one bounded parallel upload/readback readiness exchange; return to
   Legacy CLI with visible/flashing cursor controls and idle resources.
4. Update the current SD guide, handbook and machine-local installation record
   with precise invocation, limitations and rollback. Retain Extender custody;
   no mail/grant/consumer launch until the Author reviews the installed result.

## Parallel-upload trial installed; stopped for Author review

The Author authorizes installing the exact tested experimental pair and current
operation documentation, then explicitly requires a stop before Wolf receives
access. Installation is complete: full131072B EMOS ROM independently SAVE/GET
compares to855aa732; P4 app1851168B429cd4cd independently reads back and the
complete expected16MiB image61f50472 verifies, preserving all other sectors.
This complete-image verification is not a new whole-device host read. Exact
incoming P4r27/EMOS84da rollback is retained. Native VDP is not written.

Private `/emos/sdpu01.bin`26449Bf60f244f is independently read back. Canonical
`/emos/sdserve.bin`0566 and startup9e97 remain byte-exact. One fresh65537B
parallel upload completes with outcome3/CLOCK65537/VALID2 and an exact full GET;
host upload takes2.511s (a readiness observation, not a new matched ranking).
Actual CLI/listener/EXIT, Legacy mode0, neutral input, idle worker, offline
listener and both ownerless USB endpoints pass. Cursor/text/flash controls are
sent; no optical/sound qualification is claimed. No reset holder remains.

After EMOS-first flashing, old-P4 keyboard admission dropped while submitting
the pre-install listener command; P4 flash had not started and no listener/job
was active. The incomplete command was not replayed. The reviewed continuation
used freshly preserved safe startup and independent Agon hold to install P4,
then proved matched boot/input and CLI. This setup transition is documented in
the current installation guide; it is not a new controller-feature pass.

Current handbook, SD guide, installation guide, host-tool index and exact trial
component manifest provide invocation and rollback without reconstructing task
history. Whole-installation production selection, qualification and version/tag
remain unchanged. Extender retains generation9; Wolf remains queued and receives
no grant/mail/progress notification. Golem's resumed request is behind Wolf.
