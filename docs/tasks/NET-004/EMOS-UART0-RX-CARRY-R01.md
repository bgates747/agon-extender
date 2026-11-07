# UART0 receive admission correction

EMOS must pass a byte to its VDP packet parser only when its UART0 receive
helper positively returns a byte. The selected handler ignores that carry
result, allowing a no-data entry to supply a synthetic zero. This correction
preserves real zero bytes and existing cleanup. It is not a finding that the
condition occurred in actual98 or caused its missing renderer reply.

## Authority and boundary

Smith's original human resume message was verified read-only in MechAgon thread
01a1a883-630e-7b52-85d8-6fbc07cc0ccb, turn
01a1b7c1-a092-7590-9d6e-0ab3cdd6b0fd, message
01a1b7c1-b296-7cf0-88cd-00e9af7b9494: “resume goal”. Mech's existing owner
assignment selects source/native correction and bounded validation only.
SIDEBAR-001 retains its queued serialized8de66 comparison. No firmware write,
new physical case, replay, P4 package/deployment or production change is selected.

## Research and exact baseline

1. Official documentation baseline f9806bd3cbff6ed5d1c08bef1d51fed11764b86b:
   `agon-docs/docs/vdp/System-Commands.md` VDP serial protocol and
   `agon-docs/docs/mos/API.md` callback interfaces. These describe packets and
   public callbacks; they do not turn an empty receive result into a character.
2. Official MOS clean tagged v3.0.2 source
   8336409351ee5314e02801a7b72a4f1bb5282519, `src/serial.asm`:
   UART0_serial_RX reads one LSR, masks DR, returns NC without RBR when empty;
   otherwise reads RBR and sets carry even for data zero. Official inherited
   `src/interrupts.asm` ignores carry. Both references remain read-only.
3. Selected project-owned source6cf7a6a756d30d99f7745e72d5c99b91c677db41
   produces full ROM47dadc290433850c0aa500f6c165defd821ad992bc484abe5e047fbe4b800155.
   [Retained assessment](../../../../agents/net004/uart1-rx-protect-r01/actual98-uart0-source/ASSESSMENT.md)
   and adjacent source-pins.json bind ten files and exact map. Candidate changes
   belong in an isolated EMOS-owned source checkout, not either official reference
   or generated build output.

## Implementation contract

1. Immediately after CALL UART0_serial_RX branch on NC to the existing common
   RX exit before diagnostic exit/UART1 cleanup. The call-to-branch interval
   must contain no instruction that changes flags. Only C admits parser data;
   never test A/Z because a real RBR zero is valid.
2. Empty receive leaves packet/session/callback state unchanged. It does not
   reset parser, clear an error, synthesize callback, retry receive or read LSR
   again. Carry does not report OE/PE/FE/BI: historical UART0 error limits remain.
3. Preserve DI, complete primary/alternate/index saves, common UART1 STOP/RX-first
   tail, TX-empty demultiplex and every EI/RETI exit. Add no resident data, timer,
   callback, SDK/event ABI, transport policy, source-release or drain change.
4. Keep the fix unconditional in the maintained receive path. Ordinary non-APP
   builds receive the same correctness fix; no production-facing opt-out flag.
   Parent is the explicit negative control, not a supported buggy mode.

## Finite qualification and stopping point

1. Isolate exact parent/candidate source, record product diff and common identity.
   Four paired native compositions: parent/candidate APP+RFC25 and ordinary
   non-APP+RFC25. Preserve all mandatory wrapper linked checks and add the
   carry-path linked guard to the candidate wrapper. One identified APP build
   follows for source/build/map/ROM-fit binding; no diagnostic fit assumption.
2. Execute a bounded host interpreter of the actual linked handler/helper bytes
   with peripheral and called-leaf stubs. Cover absent DR in a midpacket state,
   true RBR zero, arbitrary bytes, TX-only path and all context/tail preservation.
   Call this linked-byte contract execution, not a complete ISA/IRQ/peripheral
   emulator or hardware qualification. Fail closed on unsupported instructions.
   The original parent and wrong carry/zero/skip mutations must be rejected.
3. Compiler FIFO required. Serial make, <=180 seconds per native child,
   <=600 seconds total, sensor failure/80C/512MiB guards, original signal handling,
   owned process groups only, join then release and immediately notify an actual
   successor. No test/emulator/device launched from the compiler lease.
4. Retain exact source, outputs, ELF/map, mandatory and focused check evidence;
   report ROM/data/stack deltas, actual callback/mode/backend map and pinned SDK
   compatibility. Separate mathematical transfer-boundary reasoning from runtime
   measurement. Preserve informative first failures; don't loop qualification.
5. Return a finite owner-isolation proposal before any future physical selection.
   That proposal must distinguish controllable no-data stimulus from ordinary
   quiet-UART0 network integration and define positive zero-byte/parser/TX/U1
   cleanup evidence. Do not add a private IRQ or raw-status probe to consumer code.

## State

Source/native qualification completed after verified human resume; candidate retained uninstalled.
P4 first-connect-failure artifact remains retained and uninstalled. New packaging
is unnecessary for this UART0 source tranche and is not started.


## Checked result and limits

Clean isolated owner source9dd099fc3a120f0e9f84cecbef9c278bec48a34a adds the
immediate NC branch. Compiler439 completed34.164s and released20:55:53.266398UTC,
all owned children joined; automatic Mech440 handoff delivered immediately.
First438 stopped on a syntax typo in the new verifier after native linking;
all children joined/released, failure retained, checker corrected before fresh
qualification. Completed parent APP output was reused; no redundant parent rerun.

| Resource | Exact parent APP | Candidate APP | Difference |
|---|---:|---:|---:|
| ROM used, bytes | 130735 | 130737 | +2 |
| ROM free, bytes | 337 | 335 | -2 |
| Text, bytes | 118637 | 118639 | +2 |
| Initialized data, bytes | 802 | 802 | 0 |
| BSS, bytes | 3499 | 3499 | 0 |

Ordinary non-APP/RFC25 parent/candidate also pass mandatory native checks and
increase by exactly2 ROM bytes. Both candidate compositions execute524 focused
linked-byte cases; parent no-data and three wrong-branch controls fail, while
true zero remains admitted. Callee/peripheral stubs explicitly exclude a claim
that the complete parser, peripheral timing, IRQ priority or native CPU executed.
All previous receive-protection/RFC25/baud/startup/ABI checks remain mandatory.
The actual receive helper bytes and existing LSR read count are unchanged.

Identified APP `agon-emos-eirene-r05-b2026-11-07-20-55-43Z` full131072-byte ROM:
`c1047fae6de8915553f0efd055353884503502a8b376782d5cde928278b2c50f`;
ELF map `92b3c3a571948d41c83739f809cf297caac9cb783b8dc267c2f32999851426ff`.
CallbackBC38E/modeBC349/backendBCB25, OPEN4/events0,1,2 and optional notification
SDK ABI remain unchanged. No timer, new resident byte, additional stack push or
transport I/O is introduced. Whole-stack peak/timing remains unmeasured. Source
commits and native artifacts remain local; no remote publication or deployment.
The ignored source-native-result.json binds all actual outputs and receipts.

## Original finite isolation proposal — superseded by the selection below

1. Use a newly frozen owner fixture derived from the already checked176-record/
   four-session UART1 fixture, with the new exact candidate and same incominga25f
   rollback. Retain positive source/laterTEMT/NMreply/fourCLOSE/CLI, raw first-error
   and ordered Pi/native witnesses. Quiet-network replay alone is only lifecycle
   integration; it cannot prove this no-data branch ran on hardware.
2. For the smallest supported UART0 parser exercise, add bounded, one-at-a-time
   documented text-cursor queries `VDU23,0,130` after setting cursor coordinates
   through ordinary VDU31. Require matching supported MOS sysvar/response-flag
   completion for a real zero coordinate and a nonzero coordinate. Pin native
   VDP support/flags from exact owner source before implementation. Do not use
   startup-only general poll as an application test, direct UART register I/O,
   private interrupt entry, added line-status IRQ or raw LSR acknowledgement.
3. Exercise ordinary UART0 TX-only replies and interleave those small requests
   with admitted UART1 work within the same finite fixture; no frame benchmark
   or cadence target. The native/host fixture would need source/native closure
   and new immutable kit before any separately selected physical invocation.
4. Deterministic no-DR/midpacket behavior remains the linked-byte negative proof:
   no supported application operation guarantees a no-data UART0 IRQ. Do not
   manufacture that event with an unqualified diagnostic. Report hardware
   coverage honestly, retain first unexpected outcome and stop new dispatch.
5. Proposed bounds: one explicit invocation, <=60s native and120s original host
   observation, no retries, full original app RAM/status preservation before
   later LOAD where CLI permits, maintained recovery only if needed, exacta25f
   rollback/readback/fresh full handback/normal release. These are a proposal,
   not a bench reservation, live selection or performed test. Existing sidebar
   and queued Wolf profiling work retain their normal order.


## Follow-on selection

The resumed owner selected [one finite isolation preparation](EMOS-UART0-RX-CARRY-R01-ISOLATION.md) on2026-11-07, after protected sidebar100 and queued Wolfprofilingb230. That supersedes the unselected proposal's state only; new source/native/immutable-kit readiness and fresh normal custody still precede any physical invocation.


A subsequent source inspection found that the new checker assumes RFC25's IIR
TX demultiplexing, although its first Makefile placement also selected it for
ordinary non-RFC25 builds. The recipe was narrowed to RFC25 compositions only;
the UART0 correction remains unconditional. Runtime source and exactc1047 image
are untouched, produced at9dd099fc. Supplemental ordinary non-RFC25 wrapper validation passed compiler448 after
both sidebar measurements and original actors stopped. The new fixture and
actual controller checks also passed; a wrong final ELF inventory path was
corrected separately using the actual linker map without another compile.
Selected isolation preparation and its limits are recorded in the follow-on task.

## Selected physical isolation result

The [finite hardware isolation passed](EMOS-UART0-RX-CARRY-R01-ISOLATION-RESULT.md)
under actual102, with176 exact records/four closes/352 cursor replies and
originalRAM agreement. Incominga25f was restored/read back and the bench
cleanly released. Candidate retained but no longer installed. The frozen
preparation plan remains unchanged; the result records coverage and limits.
No actual98cause or mixed renderer acceptance follows from this case.
