# Mainboard SD service operating guide

Two mainboard transfer methods exist. **Selected production v0.1.0** provides
checked/fast transfers through the foreground `sdserve` EMOSlet in Legacy mode.
The **newer development candidate** adds automatic, P4-card-staged WebDAV jobs
at the idle MOS prompt in Legacy and negotiated ExCom, plus application-initiated
card transfers. Bounded hardware checks pass; this candidate has not been promoted
to production. Verify the installed component receipt rather than assuming Git
HEAD or the selected bundle describes the bench.

| Method | Client / endpoint | Agon requirement | Status |
|---|---|---|---|
| Foreground checked/fast listener | `scripts/sdcard.py`, P4 HTTP origin | Manually start `/emos/sdserve.bin`; Legacy only | Selected production; instructions below |
| Automatic staged mainboard files | HTTP/WebDAV, port 8081 | Eligible idle CLI; paired resident EMOS and `/emos/sdjob.bin`; mounted P4 staging card | Development; bounded Legacy/ExCom hardware pass |
| Application-owned card transfer | Linked `emos_file_transfer()` helper | Application explicitly initiates its own transfer | Development; bounded bidirectional Legacy/ExCom hardware pass |
| P4-local card management | `scripts/p4sd.py` or curl, port 8080 | No Agon listener or EMOS required | Separate development service; [P4 SD guide](p4-sd.md) |

The [production bundle](../production/README.md) pins accepted binaries and host
tools. [Qualification results](tasks/REMOTE-005/A09-A11-QUALIFICATION.md) pin the
newer tested combination: EMOS v0.1.23, finite sdjob v0.1.0 and P4 r61 with the
explicit staged-WebDAV composition. Later builds need their own installation
receipt; this guide does not assert a service is currently running.

## Automatic staged transfers — development candidate

No `EMOS sdserve` invocation is needed. P4 accepts the network request and stages
file data on its own SD card; EMOS authorizes the mainboard operation at an
eligible idle CLI and invokes `/emos/sdjob.bin` for the finite job. Mainboard data
uses the existing P4–eZ80 UART transport, not the parallel pipe. A running ordinary
application or manual listener excludes external jobs; rejected work is not
queued to run later. Do not type commands or launch an application during a job.

The paired components and finite utility must already be installed. Legacy
capability negotiation must have completed before using ExCom transfers. Jobs do
not switch displays. Obtain the installed service address from the operator and
set `AGON_DAV_URL` to `http://P4_HOST:8081` (no trailing slash). Unlike `sdcard.py`,
these HTTP requests need no host session JSON file and have no `--fast` option.
They use checked staging. The exposed root is the Agon card, subject to protected
service paths; it is not the P4 card.

Examples below operate on a deliberately chosen scratch directory. Run them
individually and inspect each result before the next dependent operation:

```sh
curl --fail-with-body -X PROPFIND -H 'Depth: 1' "$AGON_DAV_URL/"
curl --fail-with-body -X MKCOL "$AGON_DAV_URL/transfer-demo"
curl --fail-with-body -T local.bin "$AGON_DAV_URL/transfer-demo/example.bin"
curl --fail-with-body -o downloaded.bin "$AGON_DAV_URL/transfer-demo/example.bin"
curl --fail-with-body -X MOVE -H "Destination: $AGON_DAV_URL/transfer-demo/renamed.bin" -H 'Overwrite: F' "$AGON_DAV_URL/transfer-demo/example.bin"
curl --fail-with-body -X DELETE "$AGON_DAV_URL/transfer-demo/renamed.bin"
```

GET/HEAD, directory listing, MKCOL, file/directory COPY, MOVE and recursive DELETE
are supported within the [adapter limits](../vdp/video/extender/storage/webdav/README.md).
DELETE on a directory is recursive. MOVE never replaces an existing destination;
directory COPY does not merge. Ordinary PUT may replace a file and retains the
existing sibling backup; another replacement can fail until that backup has been
reviewed and explicitly resolved. A recursive operation can partially complete:
inspect HTTP 207 bodies, not just curl's exit status. No whole-tree or power-loss
atomicity is promised. Never automatically replay an uncertain mutation.

Linux file managers can try `dav://P4_HOST:8081/`; Finder's Connect to Server uses
`http://P4_HOST:8081/`. Bounded Linux GVfs transfers passed, but the full Pop!_OS,
Lenovo and Finder acceptance matrix remains open. This limited API is not a claim
of full WebDAV conformance: no locks, property updates, authentication or TLS.
Use the trusted LAN only. Paths are bounded ASCII; see the adapter contract for
length and directory-size limits.

A busy/ineligible request may return 503; it is not evidence of permission to
reset Agon. Verify the active program/service and wait for a known idle CLI.
Clean cancelled uploads passed recovery in ExCom without switching modes;
poisoned exchanges, failed cleanup or unfinished Agon write stages still require
deliberate recovery and Legacy renegotiation. Preserve uncertain staging evidence.
Large-file deadlines, absent/full media, reset/interruption and retained-stage
recovery remain incompletely qualified. Do not delete recovery files to make a
retry appear successful.

## Application-initiated transfers — development candidate

A running application may explicitly call `emos_file_transfer()` to SEND from
Agon SD to P4 SD or RECEIVE in the reverse direction. External clients remain
excluded throughout the application's lifetime, including outside its transfer.
This does not provide background execution or overwrite the caller with sdjob.
Both directions passed 4,097-byte exact-readback checks in Legacy and negotiated
ExCom, with caller-memory preservation and CLI service recovery. Linking and
result semantics belong to the component owner's
[application helper guide](https://github.com/bgates747/agon-emos/blob/main/lib/sdapp/README.md);
the [protocol guide](protocols/staged-webdav.md) explains ownership.

## Foreground listener — selected production

The following instructions apply to `sdserve`/`sdcard.py`, not the automatic
WebDAV endpoint. EMOS v0.1.19 and sdserve v0.2.0 provide the selected production
baseline. Checked and fast transfers passed bounded physical checks; see the
[deployment](tasks/AUDIT-008/HARDWARE.md) and
[fast comparison](tasks/REMOTE-005/FAST-TRANSFER.md).

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
or discard the state because an acknowledgement was lost. The default
RPC retry deadline is 60 seconds; `--timeout SECONDS` changes that deadline
per request, not the duration of a whole transfer. The separate `/sd/status`
query uses a fixed three-second network timeout. The host loads uploads and
downloads into memory as complete files; this client is not a streaming or
whole-file-resume tool.

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

## Build ownership and qualification reuse boundary

EMOS source and both listener layouts belong to `agon-emos`. See the
[build guide](building.md#building-emos-and-the-sd-application) for the MOSlet versus
ordinary application build distinction. Its wrappers
are `scripts/prepare_boot_review.py` and `scripts/prepare_sdserve.py`; they
require clean committed candidates and record source/tool hashes. Supply
project-local paths from the environment guidance; do not edit generated MOS
port worktrees or runtime snapshots. P4 uses this repository's canonical
`scripts/build_p4.py` native
wrapper with the `p4-console` profile. Use new evidence directories for each
identified build/run.

The retained `scripts/qualify_sdcard.py` controller implements ten
unattended cycles against fresh names under `/extender/sdtest`, retaining audit,
state and result files. It performs no reset, flash, game launch or automatic
cleanup after unexplained failure. The service must already be running and the
test directory must exist. Start the listener in normal checked mode for this
qualifier; it does not opt into fast uploads. The retained
[r01 qualification procedure](procedures/mainboard-sd-qualification-r01.md)
is historical evidence, not a current deployment recipe: its application
startup and reset restrictions predate the EMOSlet and supported reset bridge.
Before a new qualification, [REMOTE-005 R05-10](tasks/REMOTE-005.md) owns refreshing
the procedure against this guide and the
[bench constraints](qualification/bench-constraints.md), with an appropriate new
identity. The retained keyboard observer also prints `RUN . /` and describes
an already-loaded ordinary application. That restart instruction must become
`EMOS sdserve /` for the current EMOSlet, after verified Legacy/input readiness;
reusing the old observer unchanged would give the operator the wrong instruction.
Review both controllers and their test-target/evidence placement before reuse. Do not silently reuse the old procedure or
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

An authorized unattended qualification may pass `--terminal-hooks` before the
`--` separator. The named JSON file contains optional `success` and `failure`
argv arrays; the worker invokes exactly one after the wrapped command returns,
without a shell. Hooks are notifications, not result reporters. A hardware
test driver must record its failure identity durably before returning nonzero.
Because an alert player may print status text, the failure hook must restore
that recorded identity as the final visible Legacy result after playing the
cue. A failed success hook makes the job status `failure` while preserving the
primary command's separate status and exit code.

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

## Development-only directory commands

The development client adds `mkdir PATH --parents`, `move SOURCE DESTINATION`,
`remove PATH --recursive`, and `copy SOURCE DESTINATION --recursive`. These
require a new listener capability and are **not available on the installed
v0.2.0 listener**. Do not replace production artifacts from a development build.

COPY accepts explicit `--replace` for files and `--fast` with the existing
fast-mode limitations. MOVE never overwrites; directory COPY never merges.
Checked replacement retains backup siblings. Successful entries print JSON
receipts; failure/cancellation leaves previously completed entries in place.
Recursive depth is limited to 16; the host buffers one copied file at a time.
Keep the existing session journal for uncertain operations. These foreground-client additions are distinct from the automatic staged API
above; their local evidence is in [A07 results](tasks/REMOTE-005/A07-RESULTS.md).

Automatic staged WebDAV now has bounded physical coverage as described above.
The earlier [A08 results](tasks/REMOTE-005/A08-RESULTS.md) are historical local-test
evidence, not the current deployment boundary.
