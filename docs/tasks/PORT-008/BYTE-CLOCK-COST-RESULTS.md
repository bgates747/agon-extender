# Native parallel byte-clock results

The shared UART/Extender request and completion contract is agreed. The first
Extender implementation removes repeated bookkeeping from the existing eZ80
parallel clock loop: a guarded 4096-byte call executes about 40% fewer
instructions with interrupts enabled, for 128 additional ROM bytes and no
static RAM increase. Offline byte/edge/IFF tests and all full-build guards pass.
Actual hardware speed and generalized asynchronous admission remain untested
and unimplemented, respectively; no physical firmware is changed.

## What changed and why

1. Source inspection corrects the prior chat explanation: neither direction
   waits for a fresh acknowledgement per byte. EMOS generates the byte clocks;
   P4 uses PARLIO/DMA. The eZ80 samples READY once per byte as an abort level.
2. EMOS previously called an IFF-saving clock helper per payload byte, then
   decremented/tested a general length counter. The private assembly leaf now
   chooses an enabled or masked loop once, inlines the clock pair and uses a
   partial-first-page/256-byte inner count. Two loop variants per direction
   avoid branching on the entry IFF state for every byte.
3. Enabled loops retain a short DI/EI pair around each fresh Port D RMW,
   preserving current unrelated ISR-owned bits and admitting interrupts between
   bytes. Already-masked callers remain masked. READY abort, exact bytes,
   VALID/clock ordering, start/tail clocks, sole C guard/coordinator and maximum
   block length are unchanged. No per-byte trace or wire exchange is added.
4. UART and Extender's [shared contract](../../../../agon-dev-env/cross-agent/parallel_uart_async/contract.md)
   distinguishes accepted/BUSY, borrowed-source release, local drain and remote
   execution, plus foreground event and session lifetime. This byte-loop patch
   introduces no new application callback, descriptor queue or public MOS ABI.

## Linked instruction comparison

Ranked by baseline instruction count, largest first. These counts include the
actual C guard, native payload, inactive clocks and cleanup for one 4096-byte
call under the same instruction/register model. Difference is
`100 × (optimized − baseline) / baseline`; negative means fewer instructions.
The timing wrapper adds its existing final-forward PRT snapshot to both arms.

| Direction | Entry interrupts | Baseline instructions | Optimized instructions | Difference |
|---|---|---:|---:|---:|
| eZ80 → P4 | Enabled | 103,084 | 62,164 | −39.70% |
| P4 → eZ80 | Enabled | 102,820 | 61,900 | −39.80% |
| eZ80 → P4 | Masked | 98,954 | 53,937 | −45.49% |
| P4 → eZ80 | Masked | 98,706 | 53,689 | −45.61% |

Instructions have different cycle costs. The model does not simulate electrical
capture margins or actual preempting ISR execution; these are not elapsed-time,
calibrated-cycle, useful-CPU or physical-throughput improvements. Nonblocking
admission alone would not make the eZ80-generated payload clocks autonomous.

## Full-build space comparison

Both arms use the same toolchain/builder and profile; timestamped identity
strings have equal length. Only `.startup` grows, by 128 bytes. The data/BSS
sizes remain identical. All images are offline development outputs, without
hardware qualification or permission to deploy them.

| Profile | Baseline ROM bytes | Optimized ROM bytes | Growth | Optimized free ROM | Data + BSS, unchanged |
|---|---:|---:|---:|---:|---:|
| ExExt/controller, native timing wrapper | 128,871 | 128,999 | 128 bytes | 2,073 bytes | 8,589 bytes |
| Native coordinator, non-timing wrapper | 127,234 | 127,362 | 128 bytes | 3,710 bytes | 3,872 bytes |

The ordinary EMOS profile also passes its full wrapper at 125,558 bytes, with
the private native leaf excluded. Its source behavior is unchanged; it is an
exclusion/control build, not another speed comparison. Matched native/timing
builds take approximately 29.6–32.4 host seconds each in the isolated Pi builder;
these are build durations, not fixture runtime estimates.

## Validation and retained evidence

1. Actual linked C/assembly passes **16,492 cases**: every length 1..4096 in
   both directions and entry IFF states, raw-call ABI preservation, buffer
   boundaries, invalid ownership/arguments, READY withdrawal before the first
   payload byte and at page/late boundaries, exact start/payload/tail edges and
   fresh unrelated Port D changes. The non-timing native image separately
   passes 148 focused cases; the extended baseline passes those same 148 cases.
2. Actual-ELF checks pass two valid compositions and reject twelve invalid
   profiles/mutations, including lost inline DI, corrupted page counts,
   helper corruption, wrong Port C writes and unguarded/misdirected calls.
   The exact writer inventory is extended only for the added masked TX loop.
3. Ten parallel host tests pass. All five retained builds complete through
   owner wrappers and their ROM, UART divisor, linked owner, console and
   keyboard checks. No maintained generic builder/toolchain code is changed.
4. The initial new READY-loss test accidentally withdrew READY before the C
   guard admitted the payload, correctly causing ownership refusal. Its model
   now withdraws after VALID assertion to exercise the intended first-byte
   abort. No native implementation change was needed for this test correction.
5. [Portable evidence](BYTE-CLOCK-COST-EVIDENCE.json) retains exact image/build
   identities, source hashes, model counts, test output and space data. Full
   images, build provenance, source snapshots and raw logs remain in the ignored
   machine-local work record. The source implementation is not a physical
   qualification candidate; no hardware/autoexec/SD/wiring operation occurs.

## Remaining work

The parent task still owns nonblocking transfer admission, advisory readiness
events, the application-side foreground dispatcher and a feasible whole-request
burst capacity. Existing 4096-byte internal block admission is not redefined
as satisfying one handshake for an arbitrarily larger application request.
Physical clock/capture and actual interrupt/input behavior must be checked in
a separately prepared hardware continuation before a throughput claim or
installation recommendation. P08-D02, warm-reset reliability and production
promotion are not closed by these offline results.
