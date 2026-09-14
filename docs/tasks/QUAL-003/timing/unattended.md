# Unattended paired graphics fixture

## Executive summary

The Author requested a fixture that can run without an attached host collector.
The mainboard SD is the progress authority; a scrolling mainboard text log shows
P4 work and an audio cue reports completion or detected failure. Preparation
ends with a hardware alert and a stop before launching the matrix. E09 remains
unqualified pending a complete run. Historical evidence is unchanged.

## Preparation contract

1. [x] Keep the 39-case framebuffer corpus, payloads, ordering, four repeats and
   interval boundaries. Add opt-in `unattended` mode, stamped r02 with a new build.
2. [x] Before preload/setup/draw/output/probe, append a CSV comment with raw
   clock, repeat, route, case, next phase and completed/expected interval count.
   Sync and close before proceeding. Preserve every metric and terminal record.
3. [x] During P4 cases only, EMOS routes text to the mainboard using public
   `legacy --keep-display`, then returns to `excom --keep-display`. Never clear,
   home or reposition the text cursor. Allow ordinary scrolling. Mainboard
   graphics cases necessarily draw over that display during their own portions.
4. [x] Keep status, SD and audio work outside all measured intervals. Keep the
   existing per-operation deadlines; remove the host whole-run watchdog from
   this launch procedure. No browser framebuffer output in the first pass.
5. [x] Return to the batch even on detected failure; CSV status owns the verdict.
   The batch plays a non-clearing adaptation of the accepted British voice
   recording, then starts SD service. No host remains necessary for completion.
6. [x] Verify host control-flow/error paths, build, compare exact payload hashes,
   stage/read back the binaries and batch, preserve root startup and firmware.
7. [ ] Send a preparation voice alert on hardware and stop. Do not run matrix.

## Invocation and observation

After installing/verifying the same E09 diagnostic trio, with SD service exited
and an admitted keyboard session, execute `/extender/gqt/gqtun.txt`. The tracked
`unattended-run.txt` is its exact source. The batch selects the modes externally
before loading the fixture, as in the earlier accepted framebuffer procedure;
the C fixture never selects a mode. This preserves the historical launch setup
exception to the general autoexec-only convention without editing root startup.

The eZ80 writes a fresh `GQTnnn.CSV` in `/extender/gqt`, never truncating prior
runs. `# progress` comments identify the next attempted operation, rather than
claiming it completed. A terminal record distinguishes normal completion from a
reported error; absence means incomplete evidence. File creation/write failures
remain visible in the final screen report and still continue to audio if control
returns. No software can promise a completion cue after a hard hang or power loss.

The mainboard shows `P4 test <repeat>/4 <case> <phase> [saved/624]` while P4
renders. Mainboard cases use that screen for their actual graphics; it cannot
also preserve a text overlay without changing the workload. During P4 intervals,
mainboard status does not change, and browser video stays off. Added between-case
routing/text/disk overhead changes total wall time, not the named timed scope;
validate timer/probe behaviour physically before asserting comparability.

The Author will set a 30-minute phone timer after the future launch and report
an apparent stall. There is no host collector deadline or automatic reset.
After the cue, download the CSV through foreground SD service and validate the
full 624-interval sequence using `scripts/read_results.py`. Known probe differences
remain explicit. Timing conclusions require the full matrix.

## References and implementation limits

Official read-only `agon-docs/docs/mos/API.md`: public `mos_oscli` 0x10 and
`ffs_fsync` 0x86; sync then close establishes the durable checkpoint boundary.
Official `docs/vdp/Enhanced-Audio-API.md`: unsigned 8-bit mono sample with explicit
sample rate. The notification player is adapted from the already accepted
hardware attention player; it uses the same `/extender/attention.wav` and does
not clear the screen. It saves `/extender/gqt/voice.txt` and always returns for
SD service. A speech-command receipt is not proof the Author heard it.

No firmware, renderer, EMOS transport, GPIO, recovery procedure, or emulator
changes are part of this revision. Original diagnostic images remain pinned in
EMOS E09; setup and eventual rollback are separate from autonomous execution.

## Prepared candidate

Fixture `graphics-timing-probe-r02-unattended-b2026-09-14-22-25-41Z`,
15,687 bytes, built from e33ffce. All 39 case records and media bytes compare
exactly with the prior framebuffer baseline. Three host control-flow cases pass:
normal completion, SD checkpoint write failure, and detected VDP failure. Both
Agon C17 builds pass with warnings treated as errors. No emulator was changed.

SD files are activated and independently read back: `GQTUN.BIN`, `GQTVOICE.BIN`,
`gqtun.txt`, and preparation-only `ready.txt`, all under `/extender/gqt`.
`staging.json` records their hashes. The original firmware trio and root startup
remain unchanged. The diagnostic trio must still be installed and verified as
part of the future authorized launch; this is staged preparation, not a running
benchmark. Start the phone timer only when the agent reports the matrix launched.
