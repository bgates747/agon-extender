# Mainboard SD service operating guide

EMOS v0.1.14, uart-excom-console r12 and sdserve v0.1.0 passed the scoped
physical file-transfer and native-keyboard checks. See the
[acceptance record](qualification/mainboard-sd/2026-09-13.md) for exact builds
and limits. The [initial installation](tasks/PORT-017/BOOTSTRAP.md) preserves
rollback payloads and original startup. Keep those copies; routine use does not
require a firmware reinstall. Artifact identities remain candidates in the
registry; this milestone is not a general firmware release.

## Start and stop

The foreground service requires Legacy mode and the accepted Extender keyboard
path. At the ordinary MOS prompt:

```text
EMOS KEYINPUT extender
LOAD /extender/sdserve.bin
RUN . /
```

The argument is the absolute allowed filesystem root. `/` permits whole-card
development; normal service startup now uses this root. Initial commissioning
used `/extender/sdtest` to isolate tests, and that remains the application's
no-argument default. A root change requires stopping and restarting the application.
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
removes a backup only after the active file can be read. Consult the
[wire contract](protocols/mainboard-sd.md) before recovering an unfamiliar state. FAT rename is not power-failure atomic.

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
test directory must exist. The [qualification procedure](procedures/mainboard-sd-qualification-r01.md)
defines its evidence and limits.
Headless tests use prepared project-local profiles and their mandatory
`./fab-agon-emulator` entry points. They do not substitute for physical testing
or the Author's native-keyboard observation.

## Measured cost and current delivery

The ten physical cycles covered 0..131731 bytes and totalled 951.187 seconds
of measured cycle time. The largest cycle took 360.381 seconds, or about 365.5
new payload bytes per second including staging, multiple complete readbacks,
activation, old-version verification and audit/state writes. This is a fully
verified replacement rate, not isolated upload or UART throughput.

Normal startup selects mode 3, enables Extender keyboard, loads the service and
runs it with `/`. The consumed one-shot EMOS installer remains guarded. The
previous startup is retained as `/autoexec.txt.p17bak`; its network replacement
was fully read back after closing the old MOS batch. The final scope change was
not rebooted again; the same command had passed the native CLI restart check.
The accepted Rally binary was read in full and is unchanged. See the acceptance
record for hashes, recovery evidence and the firmware rollback identity.

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
client verifies staged and activated bytes before doing so. There is no automatic
retry, cleanup, service exit, reset, firmware flash or game launch. Wrap a prepared
deployment script when additional verified steps are required. A running record
without a terminal result after host interruption is unknown, not success.
Only one SD client may use the service at a time, even with different journals.
