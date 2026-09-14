# E07P symmetric reverse batch measurement

## Executive summary

This bounded companion to the unchanged app05 pure-data controls measures both
return routes with the same eZ80 clock. It resolves individual-transfer tick
quantization without comparing P4 queue admission against stock blocking output.
It implements the frozen timing decision in agon-emos INTEG-014/E07-parity.md;
that task remains the execution/authorization authority.

1. Preserve the original app05 fixture and protocol unchanged. A separately
   built experimental batch variant adds one launch argument, `batch`.
2. Each interval requests sixteen 256-packet returns, preserving all 32,768
   useful bytes in the existing data array. Include request/arming and mailbox
   copies equally on both routes; verify every byte outside the interval.
3. No SD I/O, screen updates or host observer occurs inside an interval. Use the
   same callback, packet token/order guards, timeout and public routing APIs.
4. Six paired repetitions alternate route order. Record expected/actual bytes,
   errors, status and total eZ80 ticks, then restore Legacy mode and SD service.
5. At the frozen 60 Hz mode the clock advances two units per 16.667 ms. Convert
   total ticks with that actual cadence and report +/-16.667 ms interval
   uncertainty (+/-1.042 ms per transfer), rather than invented microseconds.
   Require non-overlapping conservative timing bounds before close parity claims.
6. Runtime identity/source hash and exact firmware pair accompany every result.
   This measures repeated end-to-end transfers including common setup/copies,
   not UART-only wire occupancy or graphics performance. Existing exact/mixed
   and three wire captures remain separate required controls.

Build from committed clean inputs using the existing isolated builder:

```sh
.venv/bin/python docs/tasks/PORT-008/uart-alignment/scripts/build.py app --batch --output agents/integ-014/E07P/batch01
```

Run `UARTDATA.bin` with argument `batch`, using the same preselected 60 Hz modes
and post-run Legacy/SD recovery batch as the original control. The analyzer
`analyze_batch.py CSV --output result.json` rejects incomplete, duplicate,
wrong-scope or corrupt records and reports conservative timing bounds. A passed
byte check with overlapping bounds is explicitly not a parity pass.


## B02 — finer symmetric intervals, frozen before implementation

The remaining return gap is now comparable to the16-transfer interval's
±1.042ms per-transfer quantization bound. Preserve batch01 and all its evidence;
do not change the baseline clock, packet or useful work. Prepare explicit
31- and128-transfer build variants, used only if the final composition's short
interval cannot establish the close result.128 reduces the same conservative
bound to±0.130208ms per transfer; it does not change the parity threshold.

1. [x] **B02a — Implement and check scope.** Build-time rounds may be16,31 or128,
   default16. Record rounds and retained useful bytes in the build manifest and
   require matching analyzer scope explicitly. Preserve every returned byte
   until validation outside the timed interval.31 fits existing65535-byte
   storage;128 uses262144 bytes of ordinary application RAM. The old app's
   bss_end is0x547dd, stack0xb0000; the projected128 variant leaves about174KiB
   between BSS and stack. Require the actual map to retain at least128KiB and
   bound the storage product at compile time. No MOS/on-chip reserved-memory
   changes, online CRC substitute, SD output or observer within the interval.
   Check analyzer deliberate wrong-scope, corruption, timing and terminal cases.
   Canonically build clean16 and128 variants and preserve maps/hashes.
2. [x] **B02b — Use only to resolve a close result.** Keep six alternating paired
   intervals and the exact same request/arming/mailbox-copy work per transfer.
   First preserve the existing16-transfer result on the selected ROM/ESP pair.
   Then run the explicit longer variant on both routes, verify every retained
   byte and recovery, and apply non-overlapping conservative bounds. Record
   length, duration, RAM use and limits; never turn an overlapping bound into a
   pass. Original app05 matrices and independent wire captures remain required.

This is a diagnostic application change under the parent's unattended authority;
no production firmware/protocol change and no new emulator profile.


## B02 source freeze

The builder now records explicit16/31/128 rounds and retained byte count; only
the batch variant receives that compile-time scope. The analyzer requires a
matching `--transfers` selection (default16). Four host tests cover all three
scopes, exact byte counts, wrong scope, corrupt/status/odd-clock/output/terminal
controls and overlapping bounds. The128 variant retains262144 useful bytes per
interval; the link-map guard requires128KiB free between BSS and stack. Clean
16/128 builds and actual map evidence follow before B02a is checked.


## B02a build proof

Both clean variants pass. The rebuilt default16 binary is byte-identical to
the original frozen batch01 after replacing only its build identity string.
The128 build ends BSS at0x847de, leaving178210 bytes (174.03KiB) below the
0xb0000 stack top, exceeding the128KiB guard. It retains262144 useful bytes
per interval and3145728 across twelve exact rows. No reserved MOS memory is
used. The final long-interval image is15575 bytes, identityuart-data-probe-r01-b2026-09-14-16-06-09Z,
SHA256 `991e0dc1e0c4e295ceee22c6008407631fc5eba6f7525cc9e83ab07a73f336d5`.
Build/run with `--batch --batch-rounds 128` and the unchanged `batch` launch
argument; analyze with `--transfers 128`. Old app05/batch01 stay frozen and are
still the primary controls. B02b remains unused until a close selected result.


## B02b first physical result

RX05 on the fixed owner01/mainboard01 pair first passed the original16-transfer
byte checks but retained overlapping bounds (P4 85.417ms, mainboard85.938ms).
The explicit128-transfer follow-up passes all12 exact rows and3145728 useful
bytes, with Legacy/SD recovery. P4 median85.286ms (85.286–85.417), mainboard
86.068ms, elapsed difference−0.91%. P4 upper bound85.417ms is below mainboard
lower85.938ms; conservative parity passes. This is the matched return target,
not a UART0 wire capture or graphics claim. Parent EMOS P07/P08 still own final
repeats, ordinary-profile checks and exact original bench restoration.
Evidence: EMOS E07P-results/ep5rlong-analysis.json and ep5rlong.csv; ignored
Extender E07P retains the original result, stage/readback and recovery receipts.
