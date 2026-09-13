# Speaking network deployment result — 2026-09-13 UTC

Both distinct hello executables ran on the physical Agon and returned their
expected stage/audio-command receipts. The host verified the first execution,
replaced `/extender/hello.bin` through the existing SD API, read back its exact
bytes and original `.p17bak`, then sent EXIT. The already-running MOS batch
loaded and executed build two. There was no second keyboard action or reset.
The final service incarnation is online and idle.

The Author replied "done. bonus points for the british accent" after the initial
handover. This confirms audible first speech; it is stored separately from the
machine result's immutable pending-human field. Do not expand that statement
into an explicit human report about the later second screen or voice. Both
second-stage execution and VDP audio acknowledgements pass independently.

`/extender/before-hello.txt` preserves the original startup. The current autoexec
is the verified 186-byte finite hello/service/hello/service batch. On subsequent
boots the current second executable speaks before returning to sdserve; another
batch launch occurs only if that service exits. `/extender/hello.bin.p17bak`
retains the first binary. The commissioning `/autoexec.txt.p17bak` also remains
untouched. No firmware, Rally binary or track files changed.

Payload and build hashes are in the adjacent JSON records. Full local state,
logs, both WAVs, source/header snapshots and raw headless evidence remain in
ignored `agents/network-hello` and `.emulator/network-hello*`. New helper source
is deliberately uncommitted pending the normal human review/commit gate.


Discord closeout: discord-deployment.json describes the verified third build
and preservation of both predecessors. discord-hardware.json records the
Author's corrected ground and successful filmed reset/greeting, plus a fresh
stage3 execution/audio receipt. Earlier second-build/current-backup statements
above describe that earlier run. The Author approved committing this body of
work on 2026-09-13 before starting the separate remote keyboard goal.
