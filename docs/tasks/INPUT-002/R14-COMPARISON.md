# P4 scheduling comparison — 2026-10-26

Raising the P4 controller worker above the parser removed the measured UDP
backlog. With the same Oryx source at120 Hz, every packet was acknowledged and
median round trip fell from261.703 ms to1.794 ms (99.31% lower). Resetting r13
alone had left the backlog intact. These results strongly support worker
starvation as the cause of that backlog; EMOS/application/display latency is
still unmeasured.

## Matched primary comparison

Both cases used the same fingerprinted Oryx source, triangle pattern,120 Hz,
30 seconds of traffic,250 ms timeout and P4 HDMI mode 0 after fresh P4/Agon boots.
No ordinary Agon application ran. Packet counts include the source's bounded
final ACK drain. Rank is lower ACK round trip; r13 is the baseline. Percentage
change is `100*(r14−r13)/r13`; delivery change uses percentage points.

| Measurement | r13, priority 2 | r14, priority 4 | Change |
|---|---:|---:|---:|
| Worst ACK round trip | 523.846 ms | 3.732 ms | −99.29% |
| p95 ACK round trip | 373.989 ms | 2.787 ms | −99.25% |
| Median ACK round trip | 261.703 ms | 1.794 ms | −99.31% |
| Acknowledged / sent | 669 /3600 | 3600 /3600 | +2931 ACKs |
| ACK delivery | 18.583% | 100% | +81.417 percentage points |

The pre-reset r13 repeat had708/3600 ACKs and253.377 ms median. The fresh-boot
r13 result above shows that a reset alone did not explain the improvement.
Individual elapsed durations, including admission/close, were30.283s for that
fresh r13 case and30.034s for r14. Neither duration is a rendering measurement.

The single functional source change is controller worker priority 2→4. Its
eight-packet receive budget and2 ms block remain. The parser is priority 3/core0;
drawing/output remain higher priority. Source/compiled ELF agree on priority 4.
Clock quantization, exact wake/mutex/socket durations and the rendering worker's
individual execution spans were not instrumented. Do not infer a new RTOS tick
rate from the former53 ms ACK-gap pattern.

## Additional cases

These are separate offered workloads, not a ranking of game performance.
All round trips are host pre-send to host post-receive ACK, in milliseconds.

| Source / workload | ACKs / sends | Median | p95 | Worst |
|---|---:|---:|---:|---:|
| Oryx120 Hz with CLI/SD coexistence | 2400 /2400 | 1.829 | 2.673 | 7.389 |
| Pi120 Hz,15s | 1800 /1800 | 1.902 | 3.050 | 6.945 |
| Oryx120 Hz,30s matched case | 3600 /3600 | 1.794 | 2.787 | 3.732 |
| Oryx60 Hz,30s | 1800 /1800 | 1.854 | 2.799 | 3.627 |
| Oryx240 Hz,30s | 7200 /7200 | 1.658 | 2.676 | 3.611 |

Rows are ordered by worst ACK round trip, worst first. The Oryx three-rate
campaign acknowledged12600/12600 packets and lasted90.157s including setup and
close. The independent Pi case lasted15.025s; the previous r13 Pi case had
368/1800 ACKs and248.937 ms median at the same rate/duration/timeout. Pi and Oryx
were sequential, not competing controller sources.

During the separate20s coexistence case, an admitted keyboard command started
the real EMOS fast-major2 SD listener. The Pi read the unchanged99-byte startup
file, acknowledged listener EXIT, and verified actual CLI/service handback.
The same valid controller session advanced from sequence 132 to332 during that
1.679s host-observed operation. All2400 packets were acknowledged. No SD file
was written, and no mainboard mode or application was selected. This is bounded
keyboard/SD coexistence, not complete stress or lifecycle qualification.

## Built and installed identity

1. Author approval: after the r14 naming request and starvation explanation,
   the Author said "ok proceed." This released the identified scheduling
   comparison under the existing investigation authority.
2. Build: `indexed-hdmi-r14-b2026-10-26-19-39-14Z`, experimental, exact source
   `0c007438c1180078a5c9b7a838db0eec1b420caf`, parent installed-source
   `27d93dccdadf8482cf1dddb8944e7893b3172e47`. The source worktree was clean.
   The dependency lock, build selections, IDF revision and embedded reset
   endpoint match r13; SDK differences are generated path fields only.
3. The canonical native builder and action validator passed. The completed
   detached build lasted546.475s. An earlier command-session build stopped
   before linking; no partial output was installed. That interruption did not
   change source or firmware. Generated archives retain their own timestamps.
4. Application1770144 bytes, SHA256
   `990478a4337c1fef87ea2b29eb57362d24333758da6ada20f8a5e2f41ef1f5d0`.
   Only the application at flash offset 0x20000 was written, once. No factory
   prefix, bootloader, partition table, NVS or OTA initializer was written.
5. The incoming full16 MiB backup was independently verified and its r13 app,
   bootloader and partition table matched exactly. The initialized live OTA
   record differs normally from erased `ota_data_initial.bin`; its actual
   bytes were retained. A pre-write check was corrected to distinguish that
   mutable boot state from immutable package bytes. Deliberate continuation
   reverified the existing backup before the first/only application write.
6. Full independent after-readback matched the r14 application; all bytes
   outside the written erase range `[0x20000,0x1d1000)` were unchanged.
   Before full-flash SHA256:
   `6ed424bb6039833f2fdebb3aa1b8a5b678ae28f14ecde02e680c632780e574da`.
   After SHA256:
   `ca6e75f748fb2a84039f135d76d93ffcbf484da8d209bc58d1f328a68cd9cc17`.
7. The exact startup identity was captured, P4 display/controller services
   initialized, and normal Agon reset release established fresh input admission.
   Actual listener start, checksum-free read and EXIT verified command execution.
   No EMOS or mainboard VDP flash occurred. No test modified `/autoexec.txt`.

Forty-one host/controller checks pass, including the existing actual-core/
EMOS/app software pipeline. Those and this bounded physical comparison do not
qualify every mode, game or reset/fault lifecycle, and do not promote selected
production. Author review of perceived input latency remains open.

## Evidence and terminal state

Ignored evidence is under `agents/input002/`: `p4-r14-final`, `r14-build-job`,
`r14-install` (incoming backup), `r14-install-continuation` (single write and
after-readback), `r14-flash-continuation-verified-job`, `r14-comparison`,
`r14-pi-120`, `r14-coexistence`, `r14-primary-comparison.json`, compiled-start
disassembly and terminal-state receipt. Host hashes identify retained bytes;
they do not add processor-link checksums.

The primary r14 case is `INPUT-002-2026-10-26-19-57-57Z`, compared with fresh
r13 `INPUT-002-2026-10-26-19-35-58Z`. Other starts/durations remain in their
immutable per-case/campaign records. Host clocks were not synchronized with P4
or eZ80, so no one-way or physical input-to-photon timing is claimed.

Terminal observations: r14 retained, controller closed/invalid/neutral with zero
queued edges; all Oryx/Pi source processes ended; keyboard admitted/neutral with
stable epoch; listener offline/idle after acknowledged EXIT; P4 mode 0 retained
with scanout advancing and rolling fault counter 0; reset actuator released.
The startup file still matches its verified99 bytes. The bench is released.
EMOSv27/mainboard VDP and selected production remain unchanged.

Remaining latency work belongs to [the task](../INPUT-002.md): measure actual
EMOS/application delivery and viewer drawing, which currently paints at nominal
20 Hz. Fine application intervals can be measured without clock synchronization;
cross-processor one-way attribution still needs justified timestamp probes,
timer ownership and uncertainty bounds.
