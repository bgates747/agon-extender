# PORT-008 LC02 — Native coordinator integration results

## Executive summary

Private EMOS and P4 coordinators now bind the existing handover, UART parking,
native payload and matching completion exchange. Host and linked-eZ80 checks,
complete ordinary/private firmware builds and unchanged ownership/ROM guards
all pass. The private EMOS image has **599 ROM bytes free**. No flashing, reset,
SD deployment, device-network request, mode activation or production change
occurred. Pause for Author review before a separate physical activation fixture.

## Implementation and review findings

1. P4's sole UART/ISR-core owner drains the queued ACK and checks parser,
   software queue, RX ring/FIFO and TX shift-register boundaries before parking.
   EMOS must first hold CLOCK=0/VALID=0 after its own release. The retained
   descriptor and buffer reach the native PARLIO owner. Peripheral/ISR cleanup
   failure retains its DMA storage and callback context; boot recovery cannot
   take the pads until cleanup succeeds. Reciprocal return restores UART;
   received bytes remain provisional until matching completion status.
2. EMOS's private foreground coordinator uses the boot owner's same handover,
   serializer reservation, parking adapter, native assembly and bounded timer/
   stalled-clock fuse. Boot monitoring yields throughout the owned interval,
   including UART unpark and status exchange. IRQ-disabled, nested and invalid
   contenders are refused before physical mutation. A fault fences the pins,
   invalidates the session and retains the reservation until reset.
3. Review corrected three integration paths: private console timeout/fault
   recovery no longer calls the ordinary UART-rebinding cancellation helper;
   a normal console lease transition revokes only dormant parallel capability,
   preserving proven UART ownership and its queued reply; EMOS's refused final
   reservation release now enters the fault fence rather than returning from a
   partially closed transaction. Console transitions are refused while a
   parallel block or unconsumed completion receipt remains outstanding.
4. Normal queued input is retained during suspension; producers and key dequeue
   yield while the block is pending. Fault recovery invalidates the old input/
   parser epoch. No public ExExt command/API or automatic transfer caller was
   added. A future private qualification caller must provision P4 storage,
   negotiate capability, admit a block and consume its receipt. Unprovisioned
   P4 offers remain rejected.

## Validation boundaries

| Check | Result | What executes / what remains modeled |
|---|---:|---|
| P4 native coordinator | 264 cases pass | Actual coordinator, UART parking, native PARLIO adapter, handover and egress; SDK/IRQ events modeled |
| Paired EMOS/P4 native coordinators | 82 cases pass | Actual EMOS foreground/startup/console/status and native C guard plus actual P4 adapters; EMOS byte assembly, UART calls, timer scheduling and registers modeled |
| Linked private EMOS startup/runtime | 80 cases pass | Actual complete-image eZ80 instructions, including coordinator timeout/fence, real deadline/frozen-clock fuse, ownership hooks and boot-monitor exclusion; ports/clock modeled |
| Linked native payload | 124 cases pass | Actual private-image C guard and assembly, both directions, exact bounds, READY loss and IRQ interleavings; ports modeled |
| Linked ordinary UART reservation / parking / control | 22 / 289 / 65 cases pass | Actual complete ordinary-image instructions and packet/ISR handling; physical return inputs modeled |
| Existing paired boot / block control / session / handover | 722 / 689 / 1149 / 5208 cases pass | Retained actual owners/adapters with modeled physical inputs |
| Existing P4 payload / parking | 151 / 196 cases pass | Actual SDK adapters with failure injection |
| Console ownership / transport reset | 2 / 4 tests pass | Existing owner/parser/input boundaries |
| Isolated mutations / actual-ELF controls | 2 / 9 cases pass | Required refusal of missing matched status, IRQ-disabled ownership, wrong profile, corrupted native instructions and unreviewed activation |

Coordinator cases include both directions, repeated blocks, lengths 1/2/255/
256/4096, delayed packet/software/ring/FIFO/shift-register drain, wrong core,
held VALID completion, SDK start/stop/release/restore faults, repeated cleanup
failure with retained DMA, cancellation/timeouts across phases, a genuine
32-bit deadline wrap, stale publication refusal and ordinary UART capability
revocation. Paired cases add invalid descriptors/buffers, IRQ/nested refusal,
missing/corrupted completion replies, faults in each EMOS handover phase,
refused final release and running/frozen-clock stalls.

The existing ordinary UART instruction suites deliberately use the ordinary
image: their setup assumes UART already allowed and does not perform the private
boot handshake. Private startup/native suites use the private image. These are
complementary checks, not an assertion that an ordinary setup can bypass the
mandatory private release fence.

ASan/UBSan and LeakSanitizer stay enabled. Host sanitizer execution requires a
tracer-free run; no sanitizer was disabled. No full-system Fab/electrical timing,
physical first/last-byte, throughput or integrated live console-loop pass is
claimed. Reset is required after an uncertain private transfer; mainboard input follows
normal boot recovery. UART restoration and a matching status receipt cannot make
an uncertain payload replay safe; no replay or distributed atomicity is added.

## Complete builds and remaining gate

| Complete EMOS profile | Build identity | ROM used, bytes | ROM free, bytes | Static RAM, bytes |
|---|---|---:|---:|---:|
| Ordinary | `agon-emos-v0.1.24-b2026-10-09-19-15-06Z` | 128739 | 2333 | 4058 |
| Private native | `agon-emos-v0.1.24-b2026-10-09-19-15-33Z` | 130473 | 599 | 4064 |

Both maintained EMOS wrappers and all mandatory link inventories pass without
relaxing the 131072-byte ROM cap. The private coordinator adds **1149 bytes**
over the preceding 129324-byte native-leaf composition. The final release-fault
correction compiled 22 bytes smaller than the earlier partial checkpoint.
Neither build timestamp selects production or authorizes installation.

Both complete P4-PC/browser builds pass the maintained wrapper and validator.
The private build compiles the coordinator/native leaves; the ordinary build
excludes them. Both retain `UNVERSIONED-DO-NOT-DEPLOY` compile-only identities.
Source inputs match before/after both builds and their retained archives.
Installed HDMI/LCD behavior is not qualified by these browser-output builds.

| Host operation | Ordinary, seconds | Private native, seconds |
|---|---:|---:|
| Complete EMOS preparation | 0.320 | 0.269 |
| Complete EMOS wrapper/checks | 27.014 | 28.384 |
| Complete P4 wrapper/validation | 375.283 | 400.149 |

The final ten host suites take 42.414 seconds together. Linked checks and ELF
controls retain their individual durations in the result index. These are
monotonic host seconds, not transfer measurements or a bench timeout policy.
One preliminary P4 build was superseded when review corrected source during
validation; its logs remain separate. One EMOS build driver was interrupted
after its ordinary wrapper passed; fresh complete ordinary/private outputs
above replace that incomplete attempt.

[Portable result index](LIVE-COORDINATOR-LC02-RESULT.json) retains exact source
closure, artifact/log identities, ROM accounting and monotonic host durations.
Generated source archives, firmware and detailed provenance remain locally under
`agents/port008-live-coordinator/lc02/validation` and `validation-final`.
The earlier [partial checkpoint](LIVE-COORDINATOR-LC02-CHECKPOINT.json) remains
frozen evidence; its 577-byte headroom and 22-case count are superseded here.
All existing work remains uncommitted/unpushed for the required review boundary.
Unrelated EMOS `scripts/application_peer.py` is untouched.

The next gate is Author review and authorization for a separate bounded private
hardware fixture. It must provision storage, activate the private coordinator
under admitted ownership, exercise small exact blocks both ways and verify
UART/input recovery. Physical timing, first/last bytes, contention, reset cases
and throughput remain unproven. Refresh bench connectivity/ownership from the
ignored local record before that work; no live mode or SD integration follows
automatically from this software pass.
