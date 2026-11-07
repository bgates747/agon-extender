# Optional application UART1 wake notification

Add one optional application-owned notification at source release and real UART1
phase/fault transitions so a later foreground wait helper can avoid sleeping past
published work. The existing adapter, generic UART core, EMOS ROM and current
physical diagnostic stay unchanged. This is source/native-build qualification,
not a new physical case or a claimed fix for receiver overrun.

## Scope and source précis

1. Smith's ongoing MechAgon GOAL delegates the application SDK seam to Extender.
   Source consultation and selection are retained in the private owner record;
   the consumer owns its application callbacks, while UART owns the reusable
   atomic begin/wait assembly leaf. No new resident function, vector or syscall.
2. Preserve the exact current root SDK used by the frozen diagnostic. Implement
   in an isolated owner branch/source namespace and return a new checked package.
   No compiler launch while the current consumer's timed case is active.
3. Existing `include/agon/net_async.h` owns the ordinary C application service
   and source callback. Its source-release flag, UART core phase/fault/error and
   later positive TEMT remain separate from NM reply and positive CLOSE.
   Reuse the already pinned UART core/emitter without edits.
4. Official MOS API research remains the baseline in
   [the provisional adapter plan](EMOS-ASYNC-R01.md): MOSv3.0.2 and VDPv2.16.0
   references are read-only. The CPU manual's EI delay informs the later app
   helper, but this task adds no instruction-level wait or IRQ takeover.
5. The proposed macro is `AGON_NETA_NOTIFY(client_pointer)`, undefined/default
   no-op. After source release publishes its flag, notify with the retained
   active client. In the private service, capture phase/fault/error before its
   existing work and notify only if one actually changes, after publication and
   before returning unchanged demand. Source plus phase notifications may
   coalesce in the consumer's sticky byte; no progress must not produce wakes.
6. Undefined notification must compile out all new snapshot/comparison paths.
   Preserve ordinary default generated code and storage, checking actual native
   bytes with debug/path/identity differences stated explicitly.
7. The macro must be bounded and IRQ-safe: no EI, MOS/gateway, allocation, log,
   sleep, transport access, reentry, detach or source reuse. It is a scheduling
   hint, not a completion/ownership primitive. Publish-before-notify compiler
   order is mandatory. Callback-before-SUBMIT-return remains legal.
8. Silent owner revocation and wire-only CTS/TEMT transitions still use existing
   owner checks and periodic tick fallback. Default timeouts, reciprocal gates,
   refused CLOSE/quarantine and immutable first-fault behavior stay unchanged.

## Implementation and validation

NW-001 [x] Commit this plan, create isolated source branch and preserve frozen
root SDK/diagnostic input identities.

NW-002 [x] Add the smallest opt-in header splice, comments and focused actual-C
checks. Verify source-release publication/client identity; source-before-return;
real SOURCE/TAIL/IDLE/fault/error notifications; quiet/no-progress calls produce
none; repeated retained fault produces none; failed CLOSE preserves association.

NW-003 [ ] Under normal Pi FIFO, compile actual unchanged core plus adapter
checks with sanitizers and paired native control/OFF/ON application probes.
Inspect target symbols/listing and default code/data identity, report ON text/
BSS/stack limits without inventing IRQ/runtime cost. Retain finite commands and
joined descendants, release compiler and immediately notify its successor.

NW-004 [ ] Return exact source/package/member hashes and limits to MechAgon and
UART. Do not change the frozen physical diagnostic or perform a bench run.
Root owns any later consumer selection/freeze/qualification.

## Prepared candidate

The opt-in splice and actual-C notification controls are prepared in the isolated
source branch. No compiler or target execution has occurred. Existing root SDK
and frozen diagnostic remain unchanged. Native/host check runner requires an
exact baseline header and explicit owner/core/toolchain paths, preserving all
paired outputs and failing on changed default application bytes.

## Host model correction before the next build

The first isolated compiler tranche stopped at link time because the old generic
lifetime harness lacks the current owner's scoped lock/unlock and RX-resume
substitutes. No candidate notification test or native probe executed. Select the
already maintained actual RX-scope harness for this newer owner composition;
only test-model selection changes, with the SDK candidate unchanged. The old
header negative control must compile and fail at its notification assertion,
not pass through an unused-hook compile failure. Retain the brief failed-link
receipt and use a fresh qualification output/normal compiler grant.
