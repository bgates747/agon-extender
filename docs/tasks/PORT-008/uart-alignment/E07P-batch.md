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

1. [ ] **B02a — Implement and check scope.** Build-time rounds may be16,31 or128,
   default16. Record rounds and retained useful bytes in the build manifest and
   require matching analyzer scope explicitly. Preserve every returned byte
   until validation outside the timed interval.31 fits existing65535-byte
   storage;128 uses262144 bytes of ordinary application RAM. The old app's
   bss_end is0x547dd, stack0xb0000; the projected128 variant leaves about178KiB
   between BSS and stack. Require the actual map to retain at least128KiB and
   bound the storage product at compile time. No MOS/on-chip reserved-memory
   changes, online CRC substitute, SD output or observer within the interval.
   Check analyzer deliberate wrong-scope, corruption, timing and terminal cases.
   Canonically build clean16 and128 variants and preserve maps/hashes.
2. [ ] **B02b — Use only to resolve a close result.** Keep six alternating paired
   intervals and the exact same request/arming/mailbox-copy work per transfer.
   First preserve the existing16-transfer result on the selected ROM/ESP pair.
   Then run the explicit longer variant on both routes, verify every retained
   byte and recovery, and apply non-overlapping conservative bounds. Record
   length, duration, RAM use and limits; never turn an overlapping bound into a
   pass. Original app05 matrices and independent wire captures remain required.

This is a diagnostic application change under the parent's unattended authority;
no production firmware/protocol change and no new emulator profile.
