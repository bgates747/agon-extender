# Parallel transport resumption

## Executive summary

The Author releases the bench on 2026-11-01 and authorizes resuming the existing
parallel plan after committing and pushing pending work. Resume at the completed
format4 cut: compose and build a fresh matched EMOS/P4 pair, prove byte delivery,
and compare the retained four payload lengths against UART. Use the working
keyboard/controller composition; the October exploratory images are not an
installation plan. Production selection stays unchanged.

## Scope and source authority

1. The parent task and completion-removal results own the transport contract.
   No CRC, replacement checksum, COMPLETE/ACK, retransmission, new wiring,
   persistent UART shutdown or application bypass is introduced. EMOS owns
   routing and both endpoints retain the existing electrical handover fences.
2. Preserve the exact incoming P4, complete EMOS ROM, listener, startup and
   mainboard VDP. Record actual identities in the ignored bench record and
   receipts. The current P4 R25 build has a known wide-mode failure; this work
   does not repair or qualify it. Use its exact committed source composition
   for the transport variant, with no display implementation changes. Omit
   the unrelated graphics timing diagnostic, whose build contract excludes
   parallel operation. Keep the direct keyboard, hub controller, reset bridge,
   dependency lock and accepted display configuration.
3. The P4 wrapper currently excludes indexed display plus ExExt. Admit only
   a clean, explicitly identified PORT-008 stream build with the native owner;
   retain rejection of dirty inputs, private probe/data profiles and ordinary
   release identities. Keep one stock-shaped display owner. Verify the actual
   selected, compiled and linked composition before considering deployment.
4. Build the current canonical EMOS source with its existing
   `exext-stream-timing.mk` profile through every mandatory wrapper/link check.
   Preserve its exact source commit, ELF, ROM and map. Old private addresses,
   phase CALL sites and fingerprints must not be reused.
5. Official references remain agon-docs
   `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`, MOS v3.0.2 and VDP v2.16.0.
   RST10/RST18 retain their ordinary byte-output contracts. The workload uses
   buffered command5/&C2 inline updates of an allocated buffer and an ordered
   pixel reply, as established by the retained timing contract. Reference MOS
   and VDP are clean tagged checkouts. A pre-existing untracked metadata file
   in agon-docs is preserved. No upstream source edit is authorized or needed.

## Bounded work

1. Freeze and push pending documentation, then this resumption contract before
   source changes. Keep source preparation separate from live installation.
2. Adapt the P4 build identity/composition guard and exercise positive and
   negative combinations. Carry only that reviewed patch into an isolated
   checkout of the exact installed P4 source; do not copy whole current files
   over the controlled source or import unrelated development.
3. Build both matched components and bind a newly built timing appliance to
   the exact EMOS ELF/ROM. Verify owner tests, ROM capacity and required link
   guards. Identify any incompatibility before flashing.
4. Refresh the historical appliance/runner to the current test lifecycle and
   SD layout before execution. Startup is read-only. The Pi runner queries
   and records route/mode, preselects through EMOS, verifies the response,
   waits at least one second, explicitly invokes each individual case, and
   restores entry route/modes and a visible CLI. The appliance verifies its
   entry mode and must refuse an unsupported setup without invoking its
   private timing hooks. Neither reset nor autoexec launches a test.
5. Before installation, retain exact rollback bytes, prove an actual CLI and
   inspect startup. Install only the matched P4 application and EMOS; preserve
   mainboard VDP, listener and unrelated SD content. Verify installed bytes
   independently, then fresh input admission and actual command execution.
6. Run the retained 256/4096/4097/8192-byte UART/parallel workload, one warm-up
   plus five measured samples per route/length, alternating route order.
   Verify every final buffer byte outside timing. Reject saturation, faults
   and incomplete captures. Preserve informative failures and do not replay
   an uncertain operation automatically. A full performance result requires
   all declared cases; partial results remain explicitly partial.
7. Restore the exact incoming firmware pair and verify CLI/input/startup.
   Tabulate transport timing separately from ordered reply latency and from
   display rendering. This is not gameplay or final production qualification.
   Update task results, owner records and the dated log; commit and push.
   Present the next control/scheduling cut with measured evidence before
   selecting unresolved architectural changes.

## Decisions and gates

1. Accepted: resume the existing format4 proof/comparison, preserving stock
   APIs and the established eight-bit harness. UART1/Port C multiplexing is
   an existing design constraint dating to extender-legacy.
2. Unresolved P08-D02: later carrier/control/scheduling simplification remains
   in the phase-timing decision register. This tranche does not settle it.
3. Deployment gate: clean composed builds, offline checks, current lifecycle
   appliance and exact rollback must all be ready. If composition or safe
   execution cannot be established, stop with concrete evidence and the
   smallest required Author decision; do not install an older renderer or
   silently drop the working USB devices to obtain a build.

## State

Preparation started. Safety commit `49c44bbd` preserves the pre-existing MOS
recovery diagram/documentation changes under the Author's all-dirt instruction.
The clean matched pair and offline checks now pass; see
[bounded results](RESUMPTION-RESULTS.md). No parallel firmware has been installed
or parallel test invoked at that preparation checkpoint.

## Acquisition failure controls

The current capture-failure procedure applies to an incomplete USB buffer dump.
Retain completed rows and partial dumps, recover through the standing Agon-first
sequence, prove actual CLI and continue independent cases. Never infer a bad
parallel payload from missing USB log lines. A complete dump with wrong data
remains a transport/data failure and stops this campaign for diagnosis.

For a marked Extender case, prepare one isolated, clean P4 control source at
the exact matched candidate commit. Remove only the body of buffered command128
(BUFFERED_DEBUG_INFO) in that control, consuming the opcode as a no-op. The
capture routine is then absent from compiled execution; ordinary firmware and
the maintained product source keep the complete stock command. No renderer,
transport, USB, timing or mode operation changes. This temporary debug-API
deviation is solely the capture-absence control required by the standing
procedure, not a supported product API change or another transport code cut.
Keep this branch separate; do not merge its disabled debug command into product.

Official Buffered Commands API documents command128 as dumping the complete
first buffer block to USB. The retained8192-byte allocation does not shrink
during command5 updates. Thus a short serial record is an incomplete acquisition,
not proof of a shorter stored buffer. Record exact source/binary differences and
keep ordinary and capture-absence results separate. The same frozen ROM-bound
fixture bytes send the same commands and completion fences in both variants.

After the initial capture cases, deliberate repeats of completed marked cases
may recover complete byte proof using the retained host-tmpfs collection method.
Retain originals, label repeats and select solely by complete data integrity,
never elapsed time. Do not replay an uncertain invocation. Uncaptured controls
do not supply missing byte proof or qualify unseen output.

The capture-absence control observes ordinary serial panic output for60 seconds
after the one explicit RUN, then requires completed CLI text and all six saved
CSV rows with zero flags. This is a bounded functional control, not performance
selection. Its bound covers the unchanged fixture's six240-MOS-unit poisoned
buffer fences and six240-unit measured reply fences, setup and mode-query
timeouts, calibration and final SD output, with margin at the observed nominal
120 MOS units/s. With command128's body absent, its7200-unit diagnostic-dump
wait has no bulk logging work; the unchanged seven-byte fence must still reply.
If that bound does not yield positive completion, retain an inconclusive control;
do not reset or dispatch another case merely because the timer expired.
