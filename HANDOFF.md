# Current checkpoint — experimental ordinary ExExt

The ordinary parallel adapter runs unchanged VDU applications and returns real
VDP/keyboard packets. Bounded CLI, cached-input, Nurples, Aginvadors, Rally and
Lode Runner checks pass; **game performance remains below UART and reset
admission is not reliable**. This is experimental work, outside selected
production. The eight-hour goal ends2026-10-11 at18:25:14UTC; active physical
work and current reservation are recorded only in `HARDWARE.local.md`.

## Start here

1. Follow `AGENTS.md`, the handbook, selected production manifests and local
   hardware/bench constraints before any operation. The Author requires work
   to stop at a question until a reply arrives. Do not infer hardware changes.
2. [Current work contract](docs/tasks/PORT-008/EXEXT-STREAM-R01.md) owns EX01–EX07
   and the bounded correction gates. [Results](docs/tasks/PORT-008/EXEXT-STREAM-R01-RESULTS.md)
   own measurements, exact firmware identities and their scope/limits.
3. The [experimental protocol](docs/protocols/exext-stream.md) describes ownership,
   batching, real-ISR publication, SD-selected deferral and recovery boundaries.
   UART control coordinates each block; ordinary ExExt VDU/reply payload uses
   eight-bit parallel. Legacy/ExCom keep their existing UART behavior.

## Current verified pair and active comparison

1. Installed P4 is `port-008-stream-r14-b2026-10-11-16-29-33Z`, full HDMI,
   app SHA256 `5833c4aa3a54e734c91b855b37271c43c7e5db8b7b2269a3410bddb7f5e1c4ad`.
   All four flash segments independently verify.
2. Installed EMOS is `agon-emos-v0.1.24-b2026-10-11-16-52-19Z`, source
   `2b75451b37402bfc0eb5fee8cd22fd8b8f3fd4ea`,130968bytes/104free.
   Complete128KiB ROM SHA256
   `e44c60b60359f64cc3a48a4559ce7ab4090fff0a7b742e4d4fd70adb517b6578` matches.
3. Mainboard VDP remains the preceding fsim consumer's custom image; it is not
   stock. No wire/probe change or firmware backup was required. Machine-local
   receipts, exact recovery helpers and installed records remain under ignored
   `agents/exext-stream-r01` and the existing bench records.
4. A normal full-HDMI P4stream-r15 candidate compiles/validates, **not installed**.
   It only avoids one-tick sleeps during pending handshakes inside split-upload
   reads. Actual maintained-read negative/positive tests pass; physical benefit
   remains unproved. Finish the active Choplifter run and restore startup before
   any installation. Do not interrupt or replay an uncertain invocation.

## Practical findings

1. Frozen Nurples T09 completes120measured updates at14.55/s with the paired
   CLOCK helper, versus13.33/s before that optimization and earlier ExCom60/s.
   The roughly31% instruction reduction is only a9.09% observed update-rate gain.
   Pacing intervals include preempting synchronous transport, not spare CPU.
2. Matched empty-loop controls yield Legacy60.00/ExExt59.02updates/s. Idle POLL
   alone does not explain the large nonempty-workload slowdown.
3. Lode Runner's fixed524288instruction test, all256pixel samples and one DOS
   read pass on both routes. ExExt takes34.233s versusLegacy6.383s, with different
   adaptive presentation counts; this is not an isolated bandwidth comparison.
4. The Nurples loader failure was FR_DISK_ERR, resolved in the bounded repeat
   by deferring physical ExExt ISR work while stock SD PB4 is selected. Actual
   linked-eZ80 tests caught a missing volatile PB_DR facade before flashing;
   the owning MOS builder correction is committed separately.
5. Required release acknowledgement remains mandatory. Neither HTTP readiness
   nor the USB boot-fence marker is a UART grant. Later deliberate Agon resets
   recover some failed admissions; reset/power-loss qualification stays open.

## Remaining boundary

Finish the frozen physical comparisons, latest input/recovery controls and final
startup/input restoration. Commit/push only owned changes; unrelated HOST-001,
external consumer and other agent changes remain untouched. Preserve passing
and informative failure evidence. Do not promote/tag without Author acceptance
and an agreed version. Prior checkpoint narrative remains in Git/task evidence;
this file is the current handoff, not a second operating manual or task queue.
