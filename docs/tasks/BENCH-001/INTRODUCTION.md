# Initial experiments — Starting position

Recorded 2026-09-13 UTC. This is the introduction to
[BENCH-001](../BENCH-001.md), an interactive series of practical Agon CLI
experiments whose direction will be chosen with the Author.

## Why this task exists

The preceding work established network access to the mainboard SD card,
spoken hardware notifications, Pi-controlled reset, and host-controlled typing
through the Extender keyboard path. After returning for review, the Author
said, "I'm convinced you can type. I want to see you use the CLI." They selected
a separate, ad hoc task bucket rather than another rehearsed typing demo.

No first experiment has been selected. Creating this document does not execute
anything on the hardware or resume the previous unattended goal.

## Capabilities available at intake

1. The host SD client talks over Ethernet to the P4; the established EMOS
   gateway and foreground `sdserve` program perform mainboard SD operations.
   Earlier physical testing included writes, readback and interrupted-transfer
   recovery. See [SD operations](../../mainboard-sd.md) and
   [commissioning evidence](../../qualification/mainboard-sd/2026-09-13.md).
2. The host keyboard client sends bounded input over Ethernet to the P4. Its
   console owner serializes admitted events through the existing keyboard UART
   path; EMOS receives ordinary keyboard input. Physical USB input has priority.
   See [keyboard operations](../../remote-keyboard.md).
3. The host can ask the Pi to pulse the existing transistor reset circuit.
   This is ordinary mainboard reset-pin actuation, not ZDI programming. The P4
   does not control mainboard reset. The Author corrected a ground connection
   and confirmed the reset worked. See [reset operations](../../bench-reset.md).
4. Ordinary eZ80 programs can play AgonJukebox-compatible speech staged on the
   SD card. The Author previously confirmed audible speech. A newer review cue
   has a machine-readable audio-command success receipt; that receipt alone
   does not prove what a person heard.

## Last recorded hardware and software state

These are retained observations, not fresh measurements during this
documentation-only intake. Recheck relevant live state before the first action.

The installed P4 development build is
`uart-excom-console-r15-b2026-09-13-04-55-55Z`, independently flashed and verified.
EMOS remains `agon-emos-v0.1.14-b2026-09-13-01-07-47Z`; the SD service remains
`sdserve-v0.1.0-b2026-09-13-01-07-48Z`. Remote keyboard work did not change onboard
VDP firmware; do not infer a fresh stock-VDP identity from older work.

At the last recorded cue completion, 05:21:54 UTC, the stage5 program reported
`audio_commands=pass`, a fresh final SD service was online, and keyboard
admission was ready with no held or pending remote keys. Root startup selected
mode 3, UK keyboard layout and `EMOS KEYINPUT extender`, ran
`/extender/key-fixed.bin`, then loaded `sdserve` with `RUN . /`.
The final service therefore still holds its parent startup batch open until it
returns. Previous startup and payload backups were preserved.

Rally and its track data remain available on the card. A verified finite
`/extender/key-fuji-demo.txt` helper was staged for a possible later launch;
it has not been invoked as part of the renewed demonstration or this task.
Its presence is not an instruction to run it.

Machine addresses, SSH configuration, journals and local staging paths belong
in ignored `HARDWARE.local.md` and `agents/remote-keyboard/RESUME.md`, not here.

## Evidence and lessons carried forward

The r15 physical check passed 28 receiver events, cancellation/expiry releases,
80 separate cursor requests, an edited COPY, typed EXEC launching a verified
LOAD/RUN batch, and a 536-byte SD write/read. Headless actual eZ80/EMOS testing
also passed, including an intentionally lost SD response. See
[the retained evidence](../REMOTE-002/evidence/qualification-r15.json).

The initial attended demonstration received positive feedback but exposed a
clock error: a console timestamp sampled before a newer HTTP renewal could
falsely expire that renewal. Signed modular comparison fixed it. A separate
fix preserves minimum event spacing between adjacent input batches.

MOS does not queue arbitrary future CLI commands while a command is executing.
A stock-VDP screen capture showed `XEC` instead of `EXEC` after COPY: the first
letter arrived too early. A two-second pause repaired that bounded test, but
it is not a universal command-completion acknowledgement. Use execution
evidence and verified finite batches for dependent LOAD/RUN operations.

Escape or network EXIT returns from an application to its caller; a parent
batch may continue. Do not assume that Escape means a direct CLI or that an
open batch can safely be replaced. After mainboard reset, wait for fresh EMOS
keyboard admission: the P4 can briefly retain an old ready state.

## Review and repository boundaries

The Author now accepts that typing works and prefers practical CLI use.
That statement does not itself record a new physical-keyboard takeover test,
authorize a commit, or close every REMOTE-002 review item. Its implementation
and evidence remain uncommitted after the earlier contract freeze. Preserve
them; disposition remains with [REMOTE-002](../REMOTE-002.md).

Other agents are updating the Extender remote in different files and task
namespaces. BENCH-001 intake performs no fetch, merge, push or commit and no
firmware, SD, emulator or hardware action. Subsequent experiments will record
their own observations rather than treating historical passes as new evidence.
