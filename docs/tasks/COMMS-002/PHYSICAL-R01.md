# Matched forward VDU performance — physical r01

Smith selects execution now. Reuse the retained, physically exercised ordinary
VDU stream benchmark to measure UART1 versus eight-bit parallel on one identical
P4 renderer. This is a fresh forward comparison, separate from the accuracy
appliance, network-message tests, game rendering and historical measurements.

## Selected composition and scope

1. Temporarily install the retained PORT-008 optimized timing EMOS source
   `08301e6`, full 131072-byte ROM SHA256
   `b4e07568aa6ba25b1e7b872d97e81942343ca935f633543a9f0f6924563ded28`.
   Its exact-bound retained MOSlet is
   `port-008-stream-timing-r01-b2026-11-02-16-32-30Z`, SHA256
   `a0599d231f0da370f6773a934a3870800d16ae0b64e1491573f68bf677e6f417`.
   Reuse its passing private ABI/link provenance; no address rebinding or
   checksum-bearing transport modification. Host validators check fresh data.
2. P4 source `dddc10a2a31d993af577be436b5d14f6aee9de15`, identified
   `port-008-stream-r19-b2026-11-02-13-28-51Z`, application SHA256
   `102014003d771e1c917782e281bdde607da4632d7b255e0c2ba8285bd8c0fd45`,
   supplies both ExCom UART1 and ExExt format4 ordinary VDU paths, on P4-PC,
   at its retained configured360MHz (current network build is240MHz). Both
   arms share360MHz; this is not a current240MHz application comparison.
   The current network UART composition has ExExt disabled and is not silently
   treated as this matched pair. Both measured arms use this same diagnostic
   renderer/configuration; results do not qualify the current network carrier.
3. eZ80 sends identical RAM-resident 256/4096/4097/8192-byte buffer-update
   commands; P4 updates one preallocated 8192-byte buffer. Eleven header bytes
   count in stream length. Allocation, poison, complete byte dump, SD logging,
   route changes and mode checks remain outside the measured windows. Verify
   all 8192 receiver bytes per sample; missing capture is not a valid sample.
4. Eight explicit invocations, six records each (one declared warm-up plus five
   measured samples). Order U256/P256, P4096/U4096, U4097/P4097, P8192/U8192.
   All 48 raw records are retained; no successful-retry selection or speed-based
   exclusion. First unexpected failure stops this tranche and preserves evidence.
5. Local PRT1 /256 nominal 72000 counts/s at 18.432MHz, 13.8889 microseconds
   resolution, single-pass 0.9102s range; saturation invalidates samples. MOS
   coarse clock is nominal 120 counts/s. Retain calibration and overhead; no
   cross-processor subtraction or elapsed-time-as-CPU-utilisation claim.
6. Report submission, sender drain, local parallel cleanup, and ordered small
   query/reply separately. The query is an ordered processing fence, not scanout
   or bulk reverse throughput. No new CRC/retry protocol, sniffers, game case,
   async speed claim, CPU-headroom claim or rendering/FPS result.

## Installation, invocation and restoration

1. Obtain actual Wolf69 release, normal fresh reservation/admission/sole lease.
   Inspect current startup and whole listener through actual read/EXIT; preserve
   mainboard profile8 and its retained full app/tail span without rewriting it.
2. Rehash retained incoming UART P4 and full EMOS rollback artifacts with their
   installation provenance. Stage new isolated paths under `/extender` and
   `/agents/extender/results`. Preserve `/autoexec.txt` and `/emos/sdserve.bin`.
   Use an isolated retained matched diagnostic listener alias if necessary;
   never replace the ordinary listener merely to run an older diagnostic pair.
3. Install only the selected full EMOS ROM and P4 application sectors. Preserve
   bootloader, partition table, OTA selection and NVS. Read only any unresolved
   sector tail beyond the established retained rollback span, not another
   redundant full-device backup. Independently compare every newly written span.
4. Follow current startup/reset protocols. Inspect setup-only startup before
   reset, observe exact P4 initialization then Agon/input/actual CLI. No fixture
   invocation from reset. Select carrier explicitly with EMOS; query mode0,
   avoid redundant mode switches and wait at least one second after selection.
   Each standalone MOSlet has an explicit LOAD/RUN and a visible case label.
5. Passive P4 USB capture is outside transport ownership. Collect all dump bytes,
   stop the reader before active SD retrieval, prove application return/CLI,
   retrieve CSV through the isolated listener and validate it before dispatching
   another case. Preserve original journals and actual invocations. Runtime
   bound per invocation is 240s, followed by five seconds late-error observation;
   a bound never authorizes replay. Host preparations/collection are separate.
6. Restore exact incoming UART P4 application plus any additionally touched tail
   and full EMOS ROM, independently compare written bytes. Restore original
   Legacy route, both mode0 displays, flashing cursor, unchanged whole startup/
   listener, root CLI, neutral input, offline listener, idle worker and free USB.
   Stop all owned actors and perform normal fresh clean release before analysis.
7. Retain identified source/artifact/input hashes, fresh output namespaces,
   raw captures, CSV rows, correctness refusals, installation/restoration and
   release receipts in the ignored machine-local run directory. Prior physical
   records remain historical; no old result becomes a new sample.

## Preparation and limits

The [retained fixture](../../../tests/performance/stream_timing/README.md) and
[earlier optimized comparison](../PORT-008/TRANSFER-RATE-COMPARISON-RESULTS.md)
are donors, not permission to execute old startup or whole-flash recipes.
The new private runner must use current lease assertions, setup-only startup,
SD placement, joined-control passive serial opener and exact incoming rollback.
Expected acquisition is several minutes plus installation/collection/restoration;
allow a finite 60-minute tranche and stop new invocations with 15 minutes left
for cleanup. No automatic reset at that horizon. Source/validator checks use a
normal serial compiler reservation; no new emulator or firmware compilation is
needed for these exact retained binaries. Complete later corpus/reverse/CPU
bindings separately, rather than claiming this forward tranche completes them.

## Capture acquisition amendment — before further dispatch

The original host stopped at P4096: the application completed six zero-flag rows,
returned to the CLI, and left Legacy/normal listener EXIT/cursor, but USB dump1
contains8150 rather than8192 byte lines (the other five are complete). Preserve
this acquisition as invalid. This does not identify transport corruption.
The standing Author-selected [capture procedure](../../qualification/capture-failure-protocol.md)
supersedes the original stop-on-capture-failure rule above:

1. Retain original matrix STOP and captures; perform one current supported Agon
   recovery with fresh actual CLI/read/EXIT before the five remaining independent
   cases. An unrecoverable or non-capture fault stops all dispatch.
2. After independent acquisitions, install the already retained matched P4
   capture-absence control `d49d88e54879372db4e1f61252b83f67daf8be5d984f89b0284b285033e29927`,
   source `d74185caa47107b52bb2633eb9d27291f5f98c1e`, same360MHz/configuration,
   with the debug-dump routine absent. Keep the exact EMOS/MOSlet/workload/fences.
   Run one bounded60s control for each marked case; report separately, no byte
   proof or replacement performance sample. No new build required.
3. If time remains within the original60min horizon and15min cleanup reserve,
   one separately labelled fresh acquisition per marked, positively completed
   case may follow the controls after restoring the exact capture P4 and fresh
   CLI readiness. Never resubmit an uncertain invocation, overwrite the original,
   suppress failure, or select by elapsed time. A second incomplete acquisition
   remains unresolved; no further acquisition attempt in this tranche.
4. Preserve source freezes before corrections, named continuation records and
   component verification. The control uses the already preserved full touched
   P4 span; no new regions are written. Restore exact incoming UART pair/tail
   and normal full handback irrespective of acquisition completeness.

## Executed outcome

[Result r01](PHYSICAL-R01-RESULT.md) records three qualified paired size sets,
three retained invalid acquisitions, both capture-absence controls and the
unresolved 4097-byte pair. Exact incoming firmware/touched tail and full normal
state restored; generation 70 cleanly released at 2026-11-07T04:57:51UTC.
No invocation remains authorized by this completed plan.
