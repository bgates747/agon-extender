# Installing an Extender bundle

Use `production/current.yaml` in the source repository to select the approved
local installation and its immutable bundle record. Production **v0.1.0** selects
`extender-installation-r02`; the tag does not rename packaged components. The accepted combination is
P4 console r55, EMOS v0.1.19 and sdserve v0.2.0. Acceptance covers the recorded
DevKit checks, not other boards, every video mode or a public binary release.
Installing on another bench still requires identifying and preserving its current
state. No installer runs on archive extraction.

## Package and prerequisites

Receive the runtime archive, source/support archive and their separate SHA-256
checksums from the build owner. Verify the archive hashes, extract into a new
directory, then run `sha256sum -c SHA256SUMS` from the runtime root (macOS:
`shasum -a 256 -c SHA256SUMS`). `bundle.yaml` names the exact baseline and inputs;
`baseline.yaml` owns status. Never substitute a same-named binary from another
build. The matching source archive retains source commits, build recipes and
third-party notices; publication is not yet approved.

The runtime package contains `p4/`, `sd/`, `scripts/`, `reset/`, `builds/`,
`baseline.yaml`, `bundle.yaml`, `INSTALL.md`, `NOTICES.md` and `SHA256SUMS`.
Its P4 profile is the Olimex ESP32-P4 DevKit, not the future P4-PC. Keep the
installed onboard VDP unchanged. The retained mainboard image matches official VDP v2.16.0; that historical
match is not a fresh readback of another board. No mainboard VDP image or FLASH utility is shipped.

Host clients need Python 3 on Linux/macOS, with the standard library (`fcntl`
requires POSIX). They do not need a copied virtual environment. P4 builds use esptool 5.3; the physical deployment used esptool 4.12.
The examples below use the 5.x hyphenated CLI; 4.12 uses `write_flash` and
`verify_flash`. Select the syntax for your installed version. Optional reset uses an independently
commissioned Pi circuit, SSH where applicable, libgpiod v2 `gpioset`, `pinctrl`,
Bash and GNU timeout. Do not derive wiring, devices or credentials from this
package; keep those in private operator configuration.

## Operator sequence after deployment approval

I01 — Preserve the incoming state. Identify both boards, firmware, active
application, startup and SD contents. Stop active transfers cleanly. Retain
verified P4 readback/rollback, the full 128 KiB EMOS ROM, `/emos/sdserve.bin`,
`/autoexec.txt` and any local reset service/configuration before overwriting them.
A factory image is a flash prefix, not a full-device backup. Do not reset an
unknown application to make inspection convenient. Preserve user files.

I02 — Establish input independently. The current bench's mainboard keyboard port
is unavailable. Browser/agent input cannot type its own admission command while
that path is disabled. If admission is already healthy, use it at a verified MOS
prompt. Otherwise mount the SD on a host, back up `/autoexec.txt` under
`/agents/extender/backups/startup`, and deliberately prepare startup containing
`EMOS KEYINPUT extender` before requesting keystrokes. Do not assume a fresh P4
will be ready at the instant startup executes; readiness timeout is a failed
bootstrap, not permission to continue typing blindly. Use the commissioned
operator/recovery path to resolve it. No listener or display switch starts
implicitly from this package. Any fixture video mode belongs only in startup.

I03 — Install the P4 only on the verified DevKit through its serial programming
interface. Stop any serial observer. `p4/flash-layout.json` records esptool settings
and offsets: bootloader `0x2000`, partitions `0x8000`, OTA initializer `0xf000`,
application `0x20000`. The supplied `p4/firmware.factory.bin` is the matching
combined prefix and is written at **0x0**. Do not write the standalone application
at zero or perform a blanket erase. The combined prefix also overwrites any
mutable data lying within its address range (including NVS/OTA metadata); retain
a full readback and resolve any settings that must survive before proceeding.
Example commands, only after preflight:

```sh
python3 -m esptool --chip esp32p4 --port "$P4_SERIAL" --baud 460800 \
  write-flash --flash-mode dio --flash-freq 80m --flash-size 16MB \
  0x0 p4/firmware.factory.bin
python3 -m esptool --chip esp32p4 --port "$P4_SERIAL" \
  verify-flash 0x0 p4/firmware.factory.bin
```

Observe the exact startup identity and USB/network readiness separately from
flash verification. This local package preserves the accepted browser reset
endpoint in its firmware. It is specific to the commissioned bench. Do not assume
it is usable elsewhere or publish it. A different endpoint requires a new
identified build and validation, not an edited package. Templates remain
unconfigured; no private service configuration or credentials are distributed.

I04 — Install EMOS only if the existing ROM is not already the exact packaged
version. With the SD mounted on the host, stage
`sd/extender/install/em-v019.bin` at `/extender/install/em-v019.bin`. Keep the
standard existing FLASH utility, and from a verified **Legacy** MOS prompt use:

```text
FLASH mos /extender/install/em-v019.bin -f
```

Wait for FLASH's automatic reboot. Do not reset after a timer or repeat a command
because keyboard delivery was uncertain. Verify boot and full ROM independently;
the expected padded 131072-byte hash is in `bundle.yaml`. A normal MOS readback
can be saved using `SAVE /agents/extender/results/em-v019-rom.bin &0 &20000`
after creating its parent directory. Compare every byte, including erased padding.
If MOS cannot boot, use the maintained ZDI recovery protocol and a newly reviewed
payload; this package is not an automatic recovery tool.

I05 — With the SD mounted on a host and the listener stopped, install only
`sd/emos/sdserve.bin` as `/emos/sdserve.bin`. It is an **EMOSlet**, using 32 KiB
at B0000; do not LOAD/RUN it as an application or install it in `/mos` or `/bin`.
Do not overwrite it via its own running file service. Hash the copied bytes.
If the installed listener already matches, retain it. Leave user programs and
startup unchanged except the explicitly reviewed input bootstrap.

I06 — At an admitted MOS prompt select Legacy and start the foreground service:

```text
EMOS LEGACY
EMOS sdserve /
```

For fast mode, use `EMOS sdserve --fast /`; `/` is required to serve the whole
card rather than the no-argument default test directory. The listener occupies
the foreground, not a background task. A host can then use:

```sh
python3 scripts/sdcard.py --url "$P4_URL" --state "$HOME/agon-sd-session.json" list /
```

Use `--help` for transfer syntax. Both listener and host upload must opt into
`--fast`; it omits stored-file reread verification, so acceptance must independently
download and compare scratch bytes. Retain transaction journals until resolved.
Current transactions still use target-adjacent `.p17part`, `.p17meta`, `.p17bak`;
reserved `/tmp/extender` storage is not implemented. Stop with Escape or the
client EXIT operation only without an active transfer; verify the resulting prompt.

I07 — Validate the combination: USB/browser input and takeover, Legacy/ExCom
switching, display/reconnect, ExCom text readback, checked/fast file transfer,
listener exit/reentry and bounded familiar gameplay. Test reset only if the
optional bridge is deliberately configured. Browser fullscreen Escape remains
host-controlled; no FPS guarantee is made. Record passes, failures and omissions
against these exact identities before asking the Author to accept the bundle.

## Optional reset bridge

The templates under `reset/` are deliberately unconfigured. An operator installs
the existing `reset_bridge.py` plus `reset-pulse.sh` on the commissioned Pi,
sets a service user and fixed command, and supplies the exact GPIO chip/line,
allowed browser origin and bind/port. Default loopback binding is not reachable
from another host. Restrict any sudo permission to the reviewed pulse command;
no sudo policy or credentials are supplied. Do not enable a placeholder service.

The pulse helper preserves the existing 100 ms pulse and release trap; it has
passed local mocked release-path checks; the existing commissioned bridge
also passed the Author's reset test. Template installation on another Pi is untested. The bridge never pulses on startup.
A configured browser needs a matching P4 build with the bridge URL embedded.
Successful pulse response is not proof of Agon boot. The Pi drives the same
mainboard reset net as its physical button; it does not reset P4 or power-cycle
Agon. No automatic retry after uncertain delivery.

## Rollback and storage

On regression, stop promotion. Restore the verified incoming P4 image using its
recorded offsets and readback comparison, and the incoming compatible EMOS/EMOSlet
pair if those changed. Restore startup and optional reset configuration exactly;
confirm boot, prompt and input admission. Do not mix an old ROM lacking `/emos`
dispatch with this listener. Readback/backup filenames alone do not establish
compatibility. If the operator lacks a verified rollback, do not begin replacement.

Retain install/recovery payloads under `/extender`, evidence and backups under
`/agents/extender`, and only startup at `/autoexec.txt`. Never sweep SD root or
copy the entire package onto it. No unchanged mainboard VDP replacement is needed.
The canonical operational/recovery guides remain in the source repository's
`docs/README.md`, `docs/mainboard-sd.md` and `docs/mos-recovery.md`.
