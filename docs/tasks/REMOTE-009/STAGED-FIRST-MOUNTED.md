# First mounted staged-file comparison

The staged worker passes file correctness and clean handback, but does not yet
improve both directions. A1.1MB download is39.12% shorter than the old client;
upload takes6.54% longer. Most measured time remains inside the P4 worker's
UART/local-file phase. A scheduling control is pending; do not promote this
candidate or infer a cause from the priority inspection alone.

## End-to-end comparison

One1100000B deterministic file per direction, exact byte comparison outside
timing. Worst elapsed-time change first. Percentage is
`100*(staged_seconds/old_seconds-1)`; speedup is `old_seconds/staged_seconds`.

| Direction and endpoints | Old client, s | Staged client, s | Elapsed change | Speedup |
|---|---:|---:|---:|---:|
| Host to P4 SD to Agon SD |283.396 |301.930 |+6.54% |0.939x |
| Agon SD to P4 SD to host |507.445 |308.909 |-39.12% |1.643x |

Old upload begins with payload prepared and connected/preflight complete;
FINISH/ACTIVATE are included. Old download times its download call. New times the
whole staged client call, including job journals, bulk HTTP, worker and release.
New worker HELLO/STAT control work is included. These are useful operational
comparisons, not isolated UART wire rates or identical instruction workloads.
The original baseline predates reseating P4 media; the staged path necessarily
uses the now-mounted P4 card. EMOS, foreground listener, mainboard card/payload,
Legacy route, HDMI and USB composition remain fixed.

## Separate P4 and HTTP phases

| Direction | P4 worker, s | Bulk HTTP, s | Scope |
|---|---:|---:|---|
| Upload |298.504 |2.272 | HTTP includes P4 staging before worker admission |
| Download |306.410 |1.255 | HTTP serves the completed P4 snapshot |

P4 worker microseconds include local spool I/O and close/sync around the UART
record loop; they do not isolate mainboard execution, CPU scheduling or wire time.
Host timers use monotonic seconds; P4 uses esp_timer microseconds. Neither clock
is independently calibrated. Status observations do not gate P4 UART progress.
There is no CRC, substitute checksum or verification reread in this fast path.

## Correctness and state

1. Eight operations pass: upload/download of0,257,65537 and1100000B files.
   Each pair is byte-identical after timing.
2. Missing mainboard source produces the expected terminal file error, leaves
   no host output, requires explicit failed-spool discard and releases ownership.
3. Fresh ordinary RPC session reads unchanged startup and exits the foreground
   listener. P4 job returns idle. Completion output and flashing-cursor controls
   are sent; input remains admitted/neutral. No optical pass is claimed.
4. Full128KiB EMOS readback still matches incoming84da2c5a; mainboard mode0 and
   startup remain unchanged. P4 installation and exact-source/configuration
   review pass; mainboard VDP/EMOS/listener are not replaced.
5. Runtime683.770s covers the reusable four-size suite, including preflight and
   completion typing; installation, separate ROM retrieval and restoration are
   outside it. Use this as a bounded estimate for this priority1 composition,
   not a collection/reset deadline or estimate of the priority control.

[Portable evidence](STAGED-FIRST-MOUNTED.json) retains every size, timer and byte
identity. Local raw records remain in the machine-local bench record. Exact
candidate is indexed-hdmi-r27-b2026-11-02-23-11-45Z, sourcef4633a16,
application SHA12636b9e. Production is unchanged. The authorized next-step scope
is the priority-only control in the parent task, followed by exact restoration.
