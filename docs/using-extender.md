# Using an existing Extender installation

For people and agents working on other projects. This is an entry point to the
maintained procedures, not permission to use an occupied bench. Identify the
operator, current owner and intended files before sending input, transferring,
resetting or flashing. Read-only status is not proof that a running application
can be interrupted.

## Establish the starting state

1. Obtain the P4 URL, host paths, current installed-build receipt and bench
   access rules from the installation owner. Maintainers use the ignored
   `HARDWARE.local.md`; a public clone deliberately does not contain those
   machine-specific values. A Git checkout is not evidence of flashed firmware.
2. Establish whether Agon is at a MOS prompt, running a program or serving SD.
   Do not type CLI commands into an unknown application. Keyboard delivery
   counters acknowledge input handling, not completion of a MOS command.
3. **Remote typing requires Extender input to be enabled already.** An operator
   using a working keyboard, or prepared `/autoexec.txt`, must select
   `EMOS KEYINPUT extender`. A remote agent cannot bootstrap that same keyboard
   path by typing the command through a path that is still disabled. Stop for
   the operator if there is no admitted input path or prepared startup.
4. Input and display are independent. `EMOS LEGACY` routes display to mainboard
   VDP; `EMOS EXCOM` routes it to EDP. Either can use Extender input. Mainboard
   output is not mirrored into the browser in Legacy.

For unattended keyboard control, read the [keyboard guide](remote-keyboard.md)
first. Check `/keyboard/status` through the maintained client, ensure admission
and neutral keys, and preserve its journal. Following a reset, wait for a new
admission epoch and readiness; do not reuse an old ready indication. Explicit
browser capture overrides agent input, and a physical USB keypress takes over
from both. Coordinate with the person at the keyboard.

## Choose the job

| Job | Procedure and boundary |
|---|---|
| View EDP / type interactively | Open the P4's HTTP page, Connect for video, Capture keyboard for input. [Browser/input behavior and platform limits](remote-keyboard.md#browser-keyboard-capture). Capturing does not admit a disabled EMOS input path. |
| Send bounded agent input | [Host commands](remote-keyboard.md#host-commands), using `scripts/keyboard.py`. Its journal differs from the SD journal. Do not paste a sequence of dependent CLI commands and infer completion from sleeps. |
| List, retrieve or replace mainboard SD files | [SD operating guide](mainboard-sd.md). At a verified controllable prompt, select Legacy and run the foreground `/emos/sdserve.bin` through `EMOS sdserve [--fast] /`. It occupies the MOSlet region, not the ordinary application's load region. |
| Observe CLI text | `python3 scripts/screen_text.py --url "$EXTENDER_URL"` reads P4's pixel-derived text diagnostic. It observes ExCom output, not MOS command-buffer RAM or the Legacy screen. Recognition depends on the displayed font/image and is not an atomic command-completion receipt. [Scope and evidence](tasks/BENCH-006.md). |
| Reset a stuck Agon | [Reset guide](bench-reset.md). The browser button uses an optional Pi bridge, not the SD listener or a native P4 GPIO service. Reset interrupts the running program; use only with authorization and known consequences for open files. |
| Recover failed MOS firmware | [MOS recovery](mos-recovery.md). A normal reset cannot repair a bad ROM. Recovery tooling has its own readiness and authorization requirements. |
| Build / install | [Build guide](building.md), [version policy](versions/README.md), and the applicable deployment/qualification record. A compile is not a flash or qualification. |

## Host and SD paths

Run host commands from this repository root, or supply an absolute script path.
On the maintained Linux checkout use `.venv/bin/python`. On macOS the SD,
keyboard and screen-text clients use Python 3's standard library; their local
journal locking uses POSIX `fcntl`. Use the Mac's Python interpreter, not a
Linux virtual-environment executable through a shared filesystem. Native Windows
is not covered by these client instructions.

Set `EXTENDER_URL` to the owner-provided HTTP origin and use a writable local
journal path such as `SESSION_FILE` for SD operations. The SD guide owns exact
commands and restart/recovery handling. The listener's normal/fast mode and the
host upload option must agree. Fast success does not assert a verified copy.
No network service described here authenticates the caller; keep it on the
trusted LAN. The listener root `/` permits access to the whole Agon card.

Follow [SD layout](sd-layout.md): application files stay in their project/game
location; maintained Extender support belongs under `/extender`; evidence and
old backups under `/agents/extender`. `/emos` is for prefixed EMOS utilities.
Do not overwrite `sdserve.bin`, running executables or an open EXEC/autoexec file
through the listener. Preserve unknown user files.

An EMOSlet returning preserves ordinary application memory in its documented
bounds; it is still a foreground program. Escape or SD EXIT returns to the
caller, which may be a batch with more commands, not necessarily an idle prompt.
The ordinary LOAD/RUN listener fallback replaces application memory. Consult
[EMOS utility rules](https://github.com/bgates747/agon-emos/blob/main/docs/emos-utilities.md)
before making another project's program an EMOSlet.

## Stop and report

Leave the input released and report the observed final mode/program/service,
changed files, retained backups and uncertain requests. Do not silently reset,
reflash or discard journals to clear an error. The [bug register](firmware-bugs.md)
and [task queue](../TODO.md) distinguish known limitations from new failures.

Video presentation fps, native EDP rendering, game-loop pacing and keyboard
latency are different measurements. Streaming can affect gameplay; a high
browser fps alone does not prove responsive gameplay. Compare like-for-like
builds, modes and streaming states, and retain the test's stated scope.
