# DIAG-003 — Extract remaining EMOS diagnostics

EMOS has only 270 ROM bytes free in the retained installed v0.1.27 composition.
Move the remaining text-test algorithms and reporting to SD utilities, retire
fake-adapter scaffolding from ordinary firmware, and measure complete-image
savings. EMOS retains admitted transport ownership and cleanup. The Author
authorizes this task, plan publication/commit/push, then implementation.

## Scope and state

1. Plan prepared on 2026-10-30. Publish existing controller-audit notes with
   this plan before implementation. Component implementation belongs to
   `../agon-emos`, tracked there as INTEG-017; this task owns cross-component
   compatibility, ROM comparison and the Extender documentation boundary.
2. Installed baseline: `agon-emos-v0.1.27-b2026-10-26-01-06-54Z`, 130,802 ROM
   bytes / 270 free. Retained manifests, ELF/map, source and binary identities
   are recorded in ignored local evidence. Preserve those artifacts before
   reusing any builder output directory.
3. `emos_uart_probe.o` occupies 1,587 ROM bytes; the UART diagnostic gateway
   occupies 538. Fake-adapter code also remains in command/mode handling.
   These are occupied costs, not promised savings. UARTTEST/VDPPOLL/UARTFLOW
   algorithms are already external; telemetry/stock debug tests are compiled
   out and contribute no savings to this task.
4. Work is offline implementation, utility/full-ROM builds and meaningful
   host/linked checks. Keep installed P4, EMOS, mainboard VDP, SD and startup
   unchanged. No physical test, emulator launch, new production version/tag or
   acceptance is implied. Preserve the separate INPUT-004 USB work.

## Decision register

| ID | State | Decision / consequence |
|---|---|---|
| D3-01 | Author accepted | Put diagnostic sequences, grammar, timing policy and reporting in external utilities where practical; EMOS retains minimum UART routing/admission, bounded transport and abandoned-lease cleanup. |
| D3-02 | Implementation choice | Keep `EMOS VDPTEXT` through `/emos/vdptext.bin`, reusing existing `ext.uartdiag` without new resident operations. Retire the diagnostic-only `edu.text-probe` service and document historical consumers; ordinary applications use the admitted MOS/VDU route. |
| D3-03 | Implementation choice | Remove the fake adapter and its selection command from ordinary EMOS. Preserve model/host qualification externally; an SD utility must not require a new resident fake-route hook. Retired FAKE remains refused rather than loading an unrelated utility. |
| D3-04 | Constraint | No new CRC or substitute checksum on EMOS–P4 traffic; no raw application UART/GPIO bypass. Preserve controller, keyboard, SD and display contracts. |

## Cross-component gates

1. Publish this task and the component task before source work. Record exact
   baseline and candidate inputs; preserve frozen evidence and unrelated work.
2. Have EMOS build the external text diagnostic in the established B0000..B7FFF
   utility slot. Preserve the fixed text/poll wire exchange, deadlines and
   cleanup through the existing resident diagnostic transport.
3. Inventory old text/fake consumers. Retire historical recipes explicitly;
   do not rewrite frozen runs or silently retain a firmware hook to satisfy an
   obsolete emulator fixture. Any emulator-coupled edits remain uncommitted
   until Author validation under the workspace instructions.
4. Measure ordinary and controller-enabled complete images through maintained
   EMOS wrappers and mandatory profile checks. Compare the same identity/config
   before/after, state ROM/RAM deltas, utility size and remaining flash. Preserve
   the controller wire/client bytes; do not attribute unrelated changes as savings.
5. Reuse actual utility/transport harnesses for success, wrong/extra/partial
   replies, CTS blocking, stopped clocks, deadlines, acquisition refusal and
   cleanup. Run relevant gateway/mode/input/SD checks and linked guards.
6. Update maintained contracts and dated logs with implementation limits and
   measured evidence. Finish with a reviewable offline candidate and explicit
   unperformed physical/emulator validation; choose deployment identity only
   when that next operation is requested.

## Research boundary

Read-only official executable/API contracts are in `../../agon-docs/docs/mos/`
resolved from Extender root. MOSlets occupy B0000 and must fit 32 KiB; ordinary
MOS headers do not prove their link address. EMOS's maintained utility launcher
and `ext.uartdiag` already provide the required load/admission mechanism.
See [prior extraction results](PORT-008/DIAGNOSTIC-ROM-RECOVERY-RESULTS.md),
[controller audit](INPUT-004/EMOS-CONTROLLER-AUDIT.md) and the component's current
utility/resident contracts. No upstream reference source change is needed.
