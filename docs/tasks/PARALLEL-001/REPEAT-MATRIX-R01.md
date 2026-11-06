# Repeated parallel epochs and payload boundaries — source preparation

Prepare an independent owner fixture that can expose intermittent parallel
handover faults without a game or VDPlet module. Four-record controls pass but
cannot establish repeatability. This source tranche does not change the current
MechAgon replay, its frozen files, firmware, lease or restore obligation.

## Selected fixture

1. A separate native entry point uses the existing checked ext.netp SDK and
   mode lifecycle. Four explicit OPEN/connect/record/positive RELEASE sessions
   in ONE invocation; four rounds of eleven record lengths per session:
   0,1,2,17,63,64,65,75,79,127,128 bytes. Total176 records. No automatic reconnect
   after error: the next session exists only after positive prior cleanup.
2. Deterministic ramp, complemented ramp, alternating00/FF and walking-bit
   patterns vary by session/round/index. The Pi peer checks every received byte
   and echoes the exact record; the eZ80 checks every echoed byte. No CRC or
   checksum is added. Length/query/session witnesses remain separate from bytes.
3. Prepare two explicit builds: plain parallel, and parallel with the existing
   static67B guarded RFC25 draw/point cycle after each echo. The latter reuses
   only the four legal geometry indexes; source flag and ordered point reply
   both precede the next netp operation. No direct UART register/drain, callback
   ownership replacement, module, asset allocation, parser relaxation or filter.
4. Native elapsed/timing fields are nominal MOS120Hz counts, not calibrated
   rendering/wire latency. Durable output records exact sessions/records/first
   error/release/restoration and RFC source/receiver counts. Retain RAM with EI
   if ownership is uncertain; no cleanup/output call may revoke a borrowed
   source. Escape cancels through existing positive-cleanup rules.
5. One finite Pi peer accepts exactly four sequential clients and44 records
   each, validates declared sequence and each client close, and has an original
   whole150s deadline plus5s progress reads. No game/Java/emulator/listen loop
   beyond those admitted clients; output bounded to1MiB. Native/host admission
   and receiver completion remain distinct; no resubmission after timeout.

## Source and check tranche

Implement only project-owned fixture/peer/build selection and pure matrix
helpers. Preserve old binaries, closed evidence and source reconstruction by
Git revision. Existing default four-record appliance behavior remains available.
Host controls cover all176 payloads, all eight bits, true EOF/extra/short/changed
records, positive close, no second accept after failure and first-error retention.
Native compilation and ordinary checks use normal Pi FIFO: one compiler/child
at a time, expected<512MiB/under3min, whole5min stop including owned cleanup,
80C stop/512MiB available floor. All owned children joined before release.
No Oryx or target access during this tranche.

## Later physical gate

Only after source checks/builds and an exact owner/component/rollback/runner
freeze, reserve a fresh finite bench tranche. At most one plain and one RFC25
invocation, first unexpected result stops remaining dispatch. Each has its own
peer and original150s observation; no implicit replay/filter comparison. Current
mainboard profile8 is preserved; temporary unfiltered02addd/8270 and exact incoming
UART pair/full touched-span restoration use normal owner procedures. All selected
cleanup precedes normal release. This is not Wolf's mainboard VDPL integration
or a substitute for closing that endpoint contract.
