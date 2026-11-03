# Staged fast files: measured results

P4 staging plus a correctly scheduled file worker improves both directions.
For one 1.1 MB file, upload falls from 283.4 s to 43.24 s and download from 507.4 s to
243.20 s. Files match exactly, error handback passes and no resident EMOS change
is needed. These are bounded Legacy-mode results, not production promotion,
raw UART rates or all-mode/fault-recovery qualification.

## Comparable file operations

Worst final elapsed time first. All rows use 1,100,000 payload bytes.
Speedup is `old_seconds/final_seconds`; elapsed change is
`100*(final_seconds/old_seconds-1)`. Negative change means less time.

| Direction | Original RPC client, s | Staged priority 1, s | Staged priority 4, s | Final speedup | Elapsed change |
|---|---:|---:|---:|---:|---:|
| Agon SD to P4 SD to host |507.445 |308.909 |243.200 |2.087x |-52.07% |
| Host to P4 SD to Agon SD |283.396 |301.930 |43.240 |6.554x |-84.74% |

The original client uses per-record HTTP requests and host journal persistence.
The final client times one whole staged call, including job journals, bulk HTTP,
P4 worker and completed-spool release. Its HELLO/STAT controls are included;
baseline connection/preflight are excluded. Verification compares bytes after
timing. These operational scopes differ slightly, so do not treat the ratios
as isolated UART/software instruction benchmarks. The original baseline predates
P4 card reseating; successful staging necessarily uses mounted P4 media.

## Why the first candidate was slow

The first P4 file worker ran at priority 1, below the continuously runnable
priority 3 UART owner. Raising this blocked worker to priority 4 is the sole
executable source change in the control. Renderer, UART, installed EMOS and
listener stay fixed. Drawing remains priority 5 and this HDMI output priority 6;
the file worker still sleeps while waiting for a reply.

At 65,537 B, upload changes from 20.170 to 3.272 s and download from 20.116 to 15.001 s, with exact
bytes. This clears the predeclared 10% gate for a large confirmation. The 1.1 MB
confirmation also passes. This supports scheduling delay as a major upload cost;
it does not independently identify every remaining download delay. The complete
[first run](STAGED-FIRST-MOUNTED.md) remains frozen, including its slower upload.

## Timings have distinct scopes

| Direction | Final host call, s | P4 worker, s | Bulk HTTP, s |
|---|---:|---:|---:|
| Download |243.200 |241.709 |1.269 |
| Upload |43.240 |40.814 |2.287 |

P4 worker timing includes UART exchanges and local-file I/O/close/sync; it is
not mainboard CPU time or wire-drain time. Bulk upload includes pre-worker
staging. Bulk download serves a fully completed snapshot. Host monotonic seconds
and P4 esp_timer microseconds have no independent oscillator calibration.

Per212/216-byte UART request/reply records remain. Existing sdserve opens,
seeks and closes the source for each READ; the current counters do not separate
that mainboard cost from packet processing and P4 scheduling/I/O. No CRC,
substitute checksum or upload verification reread is added. This is not the
future continuous bulk UART carrier or a claim of Jukebox throughput.

## Validation and identities

1. 56 offline checks and both identified native builds pass. Actual engine/HTTP
   source tests cover queue/media ownership, bytes, errors and uncertain results;
   those tests do not model the physical RTOS scheduler.
2. Both physical variants pass eight operations: upload/download of 0, 257, 65,537
   and 1,100,000 B, plus missing-file terminal failure, explicit spool discard,
   fresh RPC session and listener EXIT. Byte comparison stays outside timing.
3. The priority control's reusable suite duration is 328.606 s, versus 683.770 s for
   priority 1. These durations include suite preflight/banners, exclude firmware
   installation and separate ROM retrieval, and are estimates for comparable
   runs only, never automatic reset/collection deadlines.
4. Final candidate is `indexed-hdmi-r27-b2026-11-03-00-02-51Z`, clean matched
   source `67dfc55bedae6655ed0b6bd5d9bae4905153de9d`, 1,803,024 B app SHA-256
   `fb8283f7f57abb6b86e936ed41936b7cd545fc3f768a8a50590ab35095e0733d`.
   Native review verifies unchanged SDK/partition/HDMI/USB/transport inputs;
   independent installed readback verifies the app and untouched outside bytes.
5. EMOS remains the accepted incoming ROM, SHA-256
   `84da2c5ac3cebb1c470bab201f797a936296a6bfc33b6ebdbcf5d1dd3a1d1d79`.
   Its full readback, startup and entry-mode proof are retained. No EMOS,
   native mainboard VDP, listener, startup or physical wiring is replaced.
6. Exact incoming P4 is restored and verified by full 16 MiB readback, SHA-256
   `006397a5a8b0f0e47d350e4a63b4f849c4a75635e7f5569a02f2b8a57871f84b`.
   Original startup/listener, actual Legacy CLI, mounted P4 card, ready/neutral
   input and valid controller pass. All USB readers and reset holders release;
   no test or transfer remains. Completion/cursor controls are sent without
   inferring an optical pass.
   The candidate remains a retained development image pending Author review;
   production selection and tags stay unchanged.

[Portable evidence](STAGED-EVIDENCE.json) includes final restoration proof. Raw builds,
readbacks, client journals and source proof remain in the machine-local bench
record. Private reset configuration remains embedded in local-only binaries;
Git records identify them without publishing those binaries.
