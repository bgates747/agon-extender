# PORT-008 — Completion-removal r01 results

## Executive summary

EMOS and P4 EDP no longer exchange COMPLETE/ACK after a parallel block. Successful
native completion, DMA cleanup and reciprocal UART return now establish the local
completion boundary. Existing physical handshakes and failure fences remain.
Full firmware builds and offline owner/linked-instruction checks pass. ExExt EMOS
reclaims another 264 bytes, leaving 738 bytes free. No hardware was accessed and
no speedup is claimed; fsim retains the bench and production is unchanged.

## Scope and implementation

1. [Contract](COMPLETION-REMOVAL-R01.md) CP01–CP05 complete. Contract commits
   Extender `0982d567` and EMOS `273e48a` were pushed before code. The preceding
   [CRC-free baseline](CRC-REMOVAL-R01-RESULTS.md) remains frozen evidence.
   Official references, other-agent work, games and renderer source were untouched.
2. Both endpoints select experimental wire4. Format2/3 peers cannot admit it;
   operation4 (the obsolete COMPLETE request) cannot succeed. The sixteen-byte
   carrier remains, with bytes14–15 transmitted zero and ignored. No transport
   CRC, replacement checksum, retry or replay is introduced. Ordinary version1
   ExCom activation and SD file verification retain their existing behavior.
3. P4's physical coordinator stages the completed descriptor/buffer **before**
   final READY-high. The same owner finishes that poll before its consumer can
   take the result. Failed READY publication cancels staging and retains cleanup
   ownership. Until consumption, a new offer, reprovisioning or mode transition
   cannot reuse the storage. Fault/cancel/reset cannot publish a received prefix.
4. EMOS retires a successful block after actual EPH_LIVE, local restore and
   reservation release. Native runner, reciprocal return and late-release failure
   fencing remain. No timer or serial receipt substitutes for physical progress.
   This supplies no endpoint-wide atomic-commit guarantee after an asymmetric fault.
5. One nineteen-byte request and eighteen-byte reply are removed per successful
   block. This is a framing count, **not** a measured elapsed-time saving. OFFER,
   session, START/POLL/STOP, queue sizes and existing VBlank/input scheduling
   remain. The known stock-behavior departures remain unresolved under P08-D02.
6. The private data-check endpoint and MOSlet harness now retire at physical
   completion. Independent payload proof stays in diagnostics. The evidence
   reader accepts historical formats2/3 and current format4 without rewriting
   old captures. No private diagnostic enters ordinary firmware.

## Offline verification

Host tests exercise actual C/C++ owners against modeled SDK/register/peer
boundaries. Linked eZ80 tests execute the new ELF's instructions with modeled
registers and interrupts. Neither proves physical wiring, throughput or FPS.

| Check | Result / scope |
|---|---|
| Control/session/admission/stream and private evidence suite |10 host tests pass; 17,969 admission, 765 session, 138 foreground/ISR, 17 stream and11 MOSlet cases, plus mirrored-header/evidence checks |
| Physical coordinator and local publication |7 host tests pass;183 block-control,315 P4 coordinator,24 retained-block reuse,80 ordinary/108 private paired-native,754 boot/runtime-adapter and25 data-check cases |
| Peripheral/physical adapters |6 host tests pass;246 retained-storage,213 native payload,196 UART,70 PCNT,5,208 handover and48 reverse-core cases |
| Actual EMOS queue/console owner |3 host tests pass; ordinary and timing compositions each exercise 4,096 split-return/header/body/STOP cases plus batching, full flush, idle input, nested IRQ refusal and failure fencing |
| ExCom regressions |4 P4 tests pass; parser progress, console sessions and mode lifecycle; EMOS console regression included above |
| Linked admission / session |18,234 /950 vectors pass; exact new ELF, ABI/IX/SP/IFF/memory and reservation guards |
| Linked controls |135 cases pass; actual UART/framer/ISR, session/OFFER/START/POLL/STOP, physical handover scripting, ignored padding, deadlines and failure paths; no COMPLETE symbol or transmitted request |
| Linked output / VBlank |1,000-byte counted/byte output agrees; nested/non-nested input, callbacks, SD deferral and register/IFF checks pass |
| Full builds |Ordinary/ExExt EMOS pass all profile-owned ROM/baud/ABI/VDU/keyboard/link guards; private parprobe MOSlet compiles; full P4-PC HDMI source/graph validation passes (43 selected sources,1,855 compile actions) |

The five host groups above contain **30 passing test invocations**; case counts
describe different scopes and must not be summed as independent coverage.
Failure injection includes final READY publication, cancellation, phase deadlines,
cleanup refusal and missing peer progress. Repeated lengths 1,2,255,256,4,095 and
4,096 cover both directions. Completion needs no extra UART request/reply; lost
or corrupt nonexistent post-return receipts cannot delay it.

Retained old tests that assumed a receipt wait were adapted to the new boundary;
ordinary tool-argument/module setup mistakes were corrected and their failed logs
discarded. No unresolved product failure was hidden by changing expectations.
The unrelated, previously reported light2-harness-r02 connectivity-hash mismatch
remains unaddressed. No blanket repository-wide validation pass is asserted.

## Build identity and ROM

Same-profile CRC-free builds are the baseline. Percentage is
`(new ROM bytes − baseline ROM bytes) / baseline ROM bytes × 100`.

| EMOS composition | Wire3 baseline (bytes) | Wire4 build (bytes) | Free of 131,072 bytes | ROM change |
|---|---:|---:|---:|---:|
| ExExt stream |130,598|130,334|738|−264 bytes (−0.202%) |
| Ordinary |128,695|128,482|2,590|−213 bytes (−0.166%) |

1. ExExt `agon-emos-v0.1.24-b2026-10-11-22-37-47Z`, MOS.bin SHA256
   `e2410607a33ee73f9140b0e7fc734cdf861f0d791f5a299d3b14e56f48b292ff`.
   Together with CRC removal, this is 634 bytes below the 130,968-byte pre-cut
   ExExt control. The ordinary reduction comes from deleting shared console
   completion code; it does not enable ExExt in ordinary firmware.
2. Ordinary `agon-emos-v0.1.24-b2026-10-11-22-39-58Z`, MOS.bin SHA256
   `1f68a335d4082b57da83de33d846dac3f085dfba55e06d1ee9835cf26a2428ca`.
3. P4 `port-008-stream-r17-b2026-10-11-22-37-46Z`, application 1,780,560 bytes,
   SHA256 `963737f032817cfa97af12ed4d4466d6f4748d8800305a9ce05b469c32ae6c2e`.
   P4-PC HDMI/rolling/PPA/USB composition uses the retained r16 dependency lock.
   Display-input manifest, SDK configuration and dependency-lock hashes match r16.
   No private reset endpoint is configured in this compile.
4. These are **exploratory dirty-source builds** from the frozen contract commits
   plus the retained implementation snapshots, not clean-input qualification or
   install-ready releases. Local `agents/completion-removal-r01` retains build
   requests, generated sources, source archive/inventories, compiler provenance,
   ELF/maps/images and logs. `evidence-index.json` binds retained evidence hashes.
   Linked tests use its copied `emos-image`, independent of later builder output.
   No generated output, version tag or production selection was published.

## Next boundary

Stop for Author discussion before another control/scheduling cut or deployment.
A later free-bench contract must install a **matched** format4 pair and rerun the
retained 256/4,096/4,097/8,192-byte proof/timing workload. Format3 cannot pair with
this source. The old diagnostic completion-phase probes now have no callsites;
any new phase fixture must be rebuilt and bound to its exact new ELF/ROM rather
than reusing an old fingerprint or comparing absent phases as measured intervals.

No gameplay, direct ExCom ↔ ExExt transition, persistent UART shutdown, production
promotion or broad-goal resumption follows from these offline passes. This tranche
made no device, startup, SD, serial/network-probe, reset or power changes. Fsim's
bench use and the last verified UART rollback receipts remain undisturbed.
