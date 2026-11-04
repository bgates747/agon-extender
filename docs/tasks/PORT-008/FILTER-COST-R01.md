# Parallel upload hardware-filter cost benchmark

State: Author-authorized; physical FIFO request e3aeddc79c73 is behind Wolf
and Golem. Matched retained artifacts and frozen payload hashes are verified;
execution awaits physical custody and Pi measurement-window coordination.
Parent: [PORT-008](../PORT-008.md). This is a bounded benchmark, not production
promotion or a change to the transport contract.

## Question and scope

Measure the incremental throughput and failure-rate effect of the P4 VALID pin
filter added during [consumer repair](UPLOAD-REPAIR-R01.md). Compare the exact
retained CLOCK-only and CLOCK+VALID application images. Both retain CLOCK
filtering, exact byte/edge checks and the same EMOS/listener. This comparison
does not measure the older CLOCK filter or the aggregate cost of every check.
No software checksum, per-byte acknowledgement or new eZ80 logic is introduced.

The pinned ESP-IDF 5.5.5 GPIO documentation defines the fixed pin filter as
rejecting pulses shorter than two IO_MUX sampling cycles. That hardware rule
is not a software delay per byte. Observe completed-job costs rather than infer
an elapsed-time penalty from the threshold. Electrical origin remains unproven.
Reference: ESP-IDF `docs/en/api-reference/peripherals/gpio.rst`, GPIO glitch
filter section; official Agon reference `agon-docs/docs/GPIO.md` for port context.
Exact private source/artifact locations remain in the ignored run record.

## Frozen variants

| Variant | P4 source | Application SHA256 | Bytes |
|---|---|---|---:|
| A: CLOCK+VALID filters | 9897b1d152f9df5a96e9292312bad6cc71bd5451 | 5db0c0a0c378ca80a7947150501f9b2a0fa44b12544873a691c4de94f2d8c527 | 1851248 |
| B: CLOCK filter only; baseline | b1a64b209e496f2b148f49989756d7581f684e74 | 429cd4cd3993ed16816daa8c7574e723d4959461ea7a51ef4dd4129647d3b348 | 1851168 |

Both use SDK configuration SHA256
`08852c8fd77e63af86dd208f57a0e1b751e4f3db7efce9005fc923e2ac78a91a`
and dependency lock SHA256
`a02df352a446db976bf1375db3de3eb7c6cdfd9603169c62ba84d30bccea78fc`.
Confirm partitions and source delta before deployment. Reuse verified retained
images; no new heavy build is required. The private parallel listener remains
SHA256 `f60f244fa4e0404792b7f91ac84fb23adbabd27a40b6f362ee5859f1716ffcf2`,
and EMOS remains `855aa732ee9bd5def7cb92b52a1521d696330a6f260ad11288f7aeab7fe7dc57`.
If entry components differ, reconcile compatibility before invoking any case.

## Finite execution and preservation

1. Extender reserves through the central physical FIFO after existing requests;
   assert the eventual current lease before every target operation. Finish host
   preparation first. Coordinate conflicting Pi workloads with Pi5 manager;
   light preparation does not reserve an idle physical bench or authorize a build.
2. Extender records the actual entry firmware, startup, route/modes, directory,
   listener/job state, attached devices and powered speakers. Preserve wiring,
   speaker state, both SD mounts, native VDP, EMOS and startup. Never edit
   autoexec. Confirm idle resources and a responsive CLI before each install.
3. Run A-before, B, A-after. Use safe P4-only installation with independently
   verified application bytes/expected flash and normal Agon reset lifecycle.
   Preserve exact incoming rollback. No native VDP flash or consumer app start.
4. In each block, the Pi client uploads immutable deterministic files of 65537,
   70472 and 1100000 bytes, three independent transactions per size, ascending
   size order. Then upload one immutable 2625992-byte asset as fault exposure.
   Thus the maximum is thirty uploads across three blocks. Every transaction
   gets a fresh destination under `/agents/extender`; retain a path manifest.
5. After each upload, the Pi client reads the complete destination outside the
   upload timer and compares exact bytes. Record P4 job identity, terminal status,
   CLOCK/VALID counts and available timing fields. No automatic uncertain replay.
6. Stop a block at its first failure, retain stage/meta/status/journals and report
   its completed prefix separately. Resolve a known terminal transaction using
   the maintained recovery procedure before the independently planned next arm.
   An unresolved operation stops the run. One failed B arm is enough exposure;
   do not repeatedly provoke the known missing-filter fault.
7. Restore the exact incoming P4 image even if it differs from A; verify it,
   restore entry route/modes/directory and visible cursor/CLI, neutral input,
   offline listener, idle job and free serial/reset resources. Preserve evidence
   before bounded recovery. Release physical custody before lengthy analysis.

Budget: approximately 30–45 minutes of physical custody including installs,
readbacks and restoration; this is an initial estimate, not an automatic reset
or collection deadline. Record actual preparation/run/retrieval durations.
No optical review or Author action is required for these byte/timing checks.

## Measurement and reporting

1. Primary comparisons: P4 `prepare_us`, `active_ms`, `handover_ms`, and
   `mainboard_us` when reported. Active receive includes SD pauses; it is not
   pure wire time. Do not sum overlapping scopes or mix microseconds/milliseconds.
2. Separately record Pi monotonic upload seconds, including HTTP staging and
   activation; full GET and verification seconds are outside that timer. Record
   host contention and keep heavy overlapping Pi work out of the comparison.
   Independent clocks are not synchronized; no one-way latency claim follows.
3. For each size and block report successes/attempts, median and range for
   comparable completed transfers, and A-before versus A-after drift. Show B
   beside both A blocks, largest payload first. Define elapsed difference as
   `(A - B) / B * 100%`; positive means filtered is slower. Do not rank a failed
   or incomplete B transfer as a speed result or silently omit failure costs.
4. Report failures, committed prefix and recovery elapsed separately. Ten or
   fewer trials per arm cannot establish a production failure probability.
   Timer quantization, uncalibrated device clocks, SD variability and host
   contention bound any small measured difference. Preserve raw receipts and
   produce a results document linked here; do not claim zero cost below resolution.

## Completion checklist

1. [x] Record source/config/artifact comparison and frozen payload manifest.
2. [ ] Reserve and receive physical custody; coordinate Pi measurement quietness.
3. [ ] Execute finite A/B/A, or retain explicit failure/stop boundary.
4. [ ] Verify restoration and release; publish raw-scope comparison and limits.
