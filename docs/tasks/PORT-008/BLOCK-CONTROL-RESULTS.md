# PORT-008 — Block-control transaction results

The bounded [contract](BLOCK-CONTROL.md) is complete off bench. EMOS and P4 now
check the entire admitted descriptor in block ACK/result transactions and
withhold successful publication until local and peer results agree after
physical UART return. Actual UART drain and native GPIO execution are still
unbound. The combined native EMOS image no longer fits; it was not emitted or
deployed. Source changes remain uncommitted for Author review.

## ROM boundary

Worst capacity result first. Units are bytes; delta compares each composition
with its retained ROM-fit checkpoint, using the unchanged AUDIT-008 accountant
for the successful image and the unchanged linker's map for the refused image.

| Composition | ROM-fit baseline | New ROM | Delta | Capacity remaining | Outcome |
|---|---:|---:|---:|---:|---|
| Private native EMOS | 130763 | 131262 | +499 | −190 | Link refused; no oversized firmware |
| Ordinary EMOS | 130178 | 130677 | +499 | 395 | Complete wrapper and mandatory checks pass |

Capacity is 131072 bytes. Ordinary static RAM remains 4058 bytes; no new EMOS
static request buffer was added. The private native image has no successful ELF
for a full-image RAM ledger or its subsequent mandatory linked checks.
The earlier fitting native image remains retained; production/installed
firmware are untouched. The reviewed ordinary build identity is recorded in
the [hashed evidence index](BLOCK-CONTROL-RESULT.json).

## Implementation and correctness

| Check | Result | What it proves |
|---|---|---|
| Actual paired EMOS foreground/ISR and P4 owner | 689 cases pass | Both directions/bounds, repeated blocks, exact identity/CRC, malformed/stale/duplicate results, failures, deadlines, provisional receipts and cancellation |
| Complete-image eZ80 instruction execution | 65 cases pass | Real reserved UART TX, receive framer and reply ISR, session/block transactions, compiled handover steps, local/remote failures, bounded waits and memory/IX/SP/IFF preservation |
| Existing paired control / session / admission | 218 /1149 /18097 cases pass | Existing session lifecycle and strict offer gate remain intact |
| Existing boot/runtime adapter / handover | 718 /5208 cases pass | Existing held recovery, reset/cancel behavior, ownership model and queued input regressions |
| Ordinary console / keyboard harnesses | Both pass | Existing console effects and ordinary/telemetry keyboard scenarios remain intact |
| P4 profile checks | 12 tests pass | Ordinary/private source selection remains explicit |
| P4-PC private target | Compile/validator pass | Pinned IDF target accepts the final source; source closure and generated artifacts verified |

The new paired suite takes 1.231 host seconds including compilation. The final
instruction suite takes 1.568 host seconds excluding Rust compilation. The final
P4 incremental compile/validation takes 36.916 host seconds after the initial
full dependency build. These are host preparation/correctness durations, not
calibrated eZ80/P4 throughput or fixture runtime estimates. Their retained logs
include start/end clock values. No Agon workload was run.

P4 requires a provisioned buffer before accepting an offer, retains its exact
descriptor, rejects nested work and prevents buffer reuse until the successful
receipt is consumed. Per-phase/result waits expire with unsigned clock wrap.
Cancellation and observed handover failure invalidate pending work; a reset
also prevents delivery of an unread receipt. The caller retains buffer/DMA
lifetime until real cleanup completes, even after logical cancellation.

EMOS captures a matched failure reply as failure immediately. Its own recorded
handover failure is included in the outgoing result even if the caller supplied
success. P4 retains already-restored UART while a matched payload-failure reply
drains; requesting another physical fence first would strand that reply. A
physical fault instead cancels capability and requests release recovery.

The P4 wrapper correctly rejected a source change during the initial build.
Final reviewed sources were archived, compiled again and validated with an
unchanged source-closure check. This was a development compile, not a release
manifest or a qualification claim. No hardware operation followed it.

## Next integration boundary

1. Recover enough resident ROM for the coordinator. The existing ROM review
   identifies UARTTEST/VDPPOLL as diagnostic MOSlet candidates; UARTFLOW has
   already been extracted and cannot supply those savings again. No additional
   extraction was performed in this bounded increment.
2. Join the boot recovery and block handover owners. Drain the actual complete
   UART queues/FIFOs/shift registers; preserve parser/key state during ordinary
   suspension; keep reset monitoring from misclassifying admitted handover.
3. Bind parking, phase deadlines, native arm/run/cleanup and UART restoration to
   completed adapter actions. No requested operation, ACK or timeout is release
   proof. Neither a native caller nor a public ExExt entry is enabled here.
4. Only then prepare/deploy the paired bench fixture. First/last-byte alignment,
   physical contention, reset cleanup, input recovery and throughput remain
   hardware gates. The Lenovo-mounted SD card was not accessed or changed.

A lost final UART reply can leave agreement uncertain; EMOS reports failure and
invalidates the session rather than replaying the old sequence. This control
transaction is not a guarantee of atomic application/file publication.

Exact source bases, hashes, artifacts and local evidence locations are in the
[machine-readable result](BLOCK-CONTROL-RESULT.json). Unrelated EMOS
`scripts/application_peer.py` was preserved untouched.
