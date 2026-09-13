# Mainboard SD service commissioning guide

Current candidate combination: EMOS v0.1.14, uart-excom-console r12 and
sdserve v0.1.0. Exact builds and qualification limits are in PROGRESS.md.
The initial card installation is described in BOOTSTRAP.md. Keep its rollback
payloads and original startup. Do not reinstall firmware on every session.

## Start and stop

The foreground service requires Legacy mode and the accepted Extender keyboard
path. At the ordinary MOS prompt:

```text
EMOS KEYINPUT extender
LOAD /extender/sdserve.bin
RUN . /
```

The argument is the absolute allowed filesystem root. `/` permits whole-card
development; the initial commissioning autoexec uses `/extender/sdtest` to
isolate tests. A root change requires stopping and restarting the application.
Video mode belongs in startup; the service does not switch modes.

Escape stops the service and returns to MOS, preserving an unfinished stage.
Host `exit` does the same only when no transfer is active. If the service is
still the loaded application, `RUN . /` restarts it without another LOAD.
Rally and this service run in the foreground at different times; this is not
background SD access while a game is running. No remote command execution or
board reset is part of the wire API.

## Host use

Use the repository's `.venv/bin/python`. Resolve the Extender address from the
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
PUT verifies the Agon-computed length/CRC and a complete host readback before
activation, then reads the active target back as well. Replacing an existing
target retains its previous bytes as `.p17bak`. After confirming the new file,
`recover PATH cleanup` removes that backup. A subsequent upload refuses any
pre-existing stage, journal or backup; it never silently overwrites recovery
evidence. `stat PATH`, `recover PATH inspect` and `list DIRECTORY` aid inspection.

Keep the same `--state` file between commands. One host process locks it at a
time. Its exact pending request is saved before transmission. After an uncertain
network timeout, `resume` retries those same bytes; do not issue a new transfer
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
removes a backup only after the active file can be read. Consult PROTOCOL.md
before recovering an unfamiliar state. FAT rename is not power-failure atomic.

A hung eZ80 cannot service SD requests. Automatic whole-Agon reset remains
unqualified; the old reset circuit must not be actuated. USB serial opens may
reset P4, so normal network file work must not open its serial monitor.

## Rebuild and repeat the checks

EMOS source and the ordinary C application belong to `agon-emos`. Its wrappers
are `scripts/prepare_boot_review.py` and `scripts/prepare_sdserve.py`; they
require clean committed candidates and record source/tool hashes. P4 uses this
repository's `scripts/prepare_console.py`. Supply project-local paths from the
environment guidance; do not edit generated MOS port worktrees or runtime
snapshots. Use new evidence directories for each identified build/run.

`scripts/qualify_sdcard.py --url ... --output agents/sd/new-run` runs ten
unattended cycles against fresh names under `/extender/sdtest`, retaining audit,
state and result files. It performs no reset, flash, game launch or automatic
cleanup after unexplained failure. The service must already be running and the
test directory must exist. QUALIFICATION.md defines its evidence and limits.
Headless tests use prepared project-local profiles and their mandatory
`./fab-agon-emulator` entry points. They do not substitute for physical testing
or the Author's native-keyboard observation.
