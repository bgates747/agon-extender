# Mainboard SD service operating guide

The current recorded installation uses EMOS v0.1.19 and the sdserve v0.2.0
**foreground EMOSlet** at `/emos/sdserve.bin`. Checked and opt-in fast transfers
pass bounded physical checks; see the [latest deployment](tasks/AUDIT-008/HARDWARE.md)
and [fast comparison](tasks/REMOTE-005/FAST-TRANSFER.md). These are development
builds, not a general firmware release. This guide does not assert that the
service is running now: consult the installation owner and current status.

## SD locations

Follow the [SD layout policy](sd-layout.md). Retained backups and results belong under
`/agents/extender`; the [relocation manifest](storage/sd-relocation-2026-09-21.json)
locates old evidence when needed.
The current service still creates sibling transaction files; `/tmp/extender`
support is pending, not an implemented feature.

## Start and stop

The service requires Legacy display routing and an already admitted Extender
keyboard path. An operator with a working keyboard, or prepared autoexec, must
have selected `EMOS KEYINPUT extender` beforehand. A remote agent cannot send
that command through an input path that is still disabled. Establish a verified
MOS prompt before typing anything; see [starting state](using-extender.md#establish-the-starting-state).

Once input is available, at that prompt:

```text
EMOS LEGACY
EMOS sdserve /
```

For fast mode, substitute `EMOS sdserve --fast /` on the second line. Do not
blindly inject both lines while the first command is still executing.

The argument is the absolute allowed filesystem root. `/` permits whole-card
development. These services have no authentication; use only on a trusted LAN.
The installation owner chooses the root explicitly. The no-argument default
is `/extender/sdtest`, which confines access to that test directory. A root change requires stopping and restarting the application.
Video mode belongs in startup; the service does not switch modes.

Escape stops the service and returns to its caller, preserving an unfinished
stage. If invoked from EXEC/autoexec, remaining batch commands may run; return
is not necessarily an idle MOS prompt.
Host `exit` does the same only when no transfer is active. Restart the utility
with `EMOS sdserve /` (or `EMOS sdserve --fast /`).
Applications and this service run in the foreground at different times; this is not
background SD access while a game is running. No remote command execution or
board reset is part of the wire API.

## Current MOSlet installation

EMOS v0.1.19 dispatches `EMOS sdserve [--fast] /` to `/emos/sdserve.bin`.
The maintained listener moved from `/mos` to `/emos`; bare `sdserve` is no longer
its installed invocation. Host-injected keyboard, ExCom/Legacy, listener transfer,
return/reentry and a 4096-byte application sentinel passed physical checks.
[Deployment record](tasks/AUDIT-008/HARDWARE.md). The ordinary listener
`/extender/sdserve.bin` remains a fallback using `LOAD /extender/sdserve.bin`
followed by `RUN . /`. Unlike the EMOSlet, LOAD replaces ordinary application
memory. Neither form is a background service.

## Host use

On the maintained Linux host use the repository's `.venv/bin/python`; on macOS
use its local `python3` (standard-library client with POSIX file locking). Resolve the Extender address from the
local bench guidance; do not put credentials or private addresses into tracked
examples. These examples use a placeholder address:

```sh
.venv/bin/python scripts/sdcard.py --url http://EXTENDER_ADDRESS --state agents/sd/client.json status
.venv/bin/python scripts/sdcard.py --url http://EXTENDER_ADDRESS --state agents/sd/client.json list /mystuff/arcade/rally
.venv/bin/python scripts/sdcard.py --url http://EXTENDER_ADDRESS --state agents/sd/client.json get /mystuff/arcade/rally/rally.bin agents/sd/rally-original.bin
.venv/bin/python scripts/sdcard.py --url http://EXTENDER_ADDRESS --state agents/sd/client.json put path/to/candidate.bin /mystuff/arcade/rally/rally.bin --activate
```

GET refuses to overwrite its local output. PUT without `--activate` leaves the
candidate staged and prints the transfer ID for `activate ID` or `cancel ID`.
Normal PUT verifies the Agon-computed length/CRC and a complete host stage
readback. With `put --activate`, it also reads the activated target back. The
standalone `activate ID` command sends only ACTIVATE; it does not add that host
readback. Use GET and compare independently if that is required after a separate
activation. Replacing an existing
target retains its previous bytes as `.p17bak`. After confirming the new file,
`recover PATH cleanup` removes that backup. A subsequent upload refuses any
pre-existing stage, journal or backup; it never silently overwrites recovery
evidence. `stat PATH`, `recover PATH inspect` and `list DIRECTORY` aid inspection.

Keep the same `--state` file between commands. One host process locks it at a
time. Its exact pending request is saved before transmission. After an uncertain
network timeout, `resume` retries those same bytes, not the remaining upload
workflow. Inspect its result and the retained transaction before deciding whether
to finish, cancel or recover; do not issue a new transfer
or discard the state because an acknowledgement was lost. Default request
timeout is 60 seconds; `--timeout SECONDS` changes it.

After a service restart, retain the old state and use a new state filename.
Inspect the journal explicitly. The boot value is an advisory time-derived
incarnation identifier, not persistent uniqueness across processor resets;
stale-session rejection and staged-file verification remain necessary. It is
not authentication. Another caller cannot seize an actively owned transfer.

## File ownership and recovery

Preserve the executable's canonical filename `sdserve.bin`; write/activation
targets with that basename are rejected. Journal siblings `.p17part`, `.p17meta`
and `.p17bak` are reserved. Paths are absolute ASCII, without traversal; READ
paths allow 120 bytes and staged targets allow 112 to leave room for suffixes.

Do not replace a file being executed or held open. In particular, MOS keeps an
EXEC/OBEY batch file open while its child application runs. Exit the startup
service and start it directly at the CLI before replacing that startup file.
Stock FatFS in this EMOS build has `FF_FS_LOCK=0`; the service is cooperative
foreground access, not a global open-file monitor.

`recover PATH inspect` returns state bits: target 1, part 2, metadata 4,
backup 8 and invalid metadata 16. `restore` moves a backup back only when the
target is absent. `abandon` discards a permitted unfinished stage/journal while
preserving a target or backup; ambiguous/damaged metadata is retained. `cleanup`
removes a backup only after the active file can be read. Consult the
[wire contract](protocols/mainboard-sd.md) before recovering an unfamiliar state. FAT rename is not power-failure atomic.

A hung eZ80 cannot service SD requests. The independently authorized
[Pi reset bridge](bench-reset.md) uses the corrected reset circuit; reset is not
an SD protocol operation or an automatic recovery step. Preserve uncertain
transaction evidence before deciding to interrupt Agon. USB serial opens may
reset P4, so normal network file work must not open its serial monitor.

## Rebuild and repeat the checks

EMOS source and both listener layouts belong to `agon-emos`. See the
[build guide](building.md#building-emos-and-the-sd-application) for the MOSlet versus
ordinary application build distinction. Its wrappers
are `scripts/prepare_boot_review.py` and `scripts/prepare_sdserve.py`; they
require clean committed candidates and record source/tool hashes. P4 uses this
repository's `scripts/prepare_console.py`. Supply project-local paths from the
environment guidance; do not edit generated MOS port worktrees or runtime
snapshots. Use new evidence directories for each identified build/run.

`scripts/qualify_sdcard.py --url ... --output agents/sd/new-run` runs ten
unattended cycles against fresh names under `/extender/sdtest`, retaining audit,
state and result files. It performs no reset, flash, game launch or automatic
cleanup after unexplained failure. The service must already be running and the
test directory must exist. Start the listener in normal checked mode for this
qualifier; it does not opt into fast uploads. The retained
[r01 qualification procedure](procedures/mainboard-sd-qualification-r01.md)
is historical evidence, not a current deployment recipe: its application
startup and reset restrictions predate the EMOSlet and supported reset bridge.
Before a new qualification, the owning task must refresh the procedure against
this guide and the [bench constraints](qualification/bench-constraints.md),
with an appropriate new identity. Do not silently reuse the old procedure or
claim that a normal-mode run qualifies fast mode.
Headless tests use prepared project-local profiles and their mandatory
`./fab-agon-emulator` entry points. They do not substitute for physical testing
or the Author's native-keyboard observation.

## Detached host deployment jobs

For an already prepared service, run the existing verified deployment command
through `scripts/bench_job.py`, using the project-local Python for both commands:

```sh
.venv/bin/python scripts/bench_job.py --output agents/my-deployment-job -- \
  .venv/bin/python scripts/sdcard.py --url "$EXTENDER_URL" \
  --state agents/my-deployment-state.json put /path/to/input.bin /target.bin --activate
```

Use a fresh ignored job directory and preserve the SD recovery journal. Launch
returns immediately. Stop monitoring; inspect `result.json` and `output.log` on
later Author follow-up. The worker records start/end UTC and monotonic elapsed
seconds, return code and success/failure; `request.json` preserves exact argv
and working directory. Success means the wrapped command returned zero; the SD
client in the normal-mode example verifies staged and activated bytes before
doing so. Adding `--fast` removes that verification guarantee. There is no automatic
retry, cleanup, service exit, reset, firmware flash or game launch. Wrap a prepared
deployment script when additional verified steps are required. A running record
without a terminal result after host interruption is unknown, not success.
Only one SD client may use the service at a time, even with different journals.

## Opt-in fast transfer — bounded physical pass

The deployed draft sdserve v0.2.0 uses the same executable and transport. Start
it with `--fast` to omit whole-file stage/target CRC rereads; supply `--fast` to
the host `put` command to omit its two full downloads. Both ends must agree.
Normal invocation remains fully checked. Packet checks, checked writes and
sync/close, staging, backups and recovery remain; fast uploads do **not** verify
the stored file contents. A bounded physical comparison measured 5.00× throughput
for 8192-byte activated uploads (two runs per mode, EMOS v0.1.18, independent
readbacks outside timing); see the linked results. That is end-to-end replacement
throughput for this fixture, not raw SD speed or a general fivefold guarantee.

With EMOS v0.1.19 and the MOSlet installed at
`/emos/sdserve.bin`, the invocation is:

```text
EMOS sdserve --fast /
```

The scope may precede the switch. The service must be restarted to change modes.
For a prepared host session, append `--fast` to the ordinary upload command:

```sh
python3 scripts/sdcard.py --url "$EXTENDER_URL" --state "$SESSION_FILE" put local.bin /games/example.bin --activate --fast
```

Stop the listener and restart without `--fast` for normal verification. Query
current service state rather than assuming that an earlier task's final mode is
still running. The host rejects a normal/fast mode mismatch before BEGIN.
[Tasklet and validation](tasks/REMOTE-005/FAST-TRANSFER.md).
