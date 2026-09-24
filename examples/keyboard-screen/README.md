# Stock VDP text readback diagnostic

## Reuse boundary

This retained fixture is not a current deployment recipe. The source still writes `/extender/key-screen.txt`, and the old handover below loads the ordinary application listener. REMOTE-002 owns a path/EMOSlet handover refresh before a new run.
Use [SD layout](../../docs/sd-layout.md),
[current SD operation](../../docs/mainboard-sd.md) and the
[example index](../README.md). The original instructions below explain its
retained source/evidence; do not execute them unchanged against today's bench.

## Retained fixture contract


This bounded development fixture helped diagnose a lost first command letter
during REMOTE-002. It requests each text cell using `VDU 23,0,&83,x16,y16`,
waits for the MOS screen-character reply flag, and saves printable ASCII in
`/extender/key-screen.txt`. It does not select a video mode or draw before
capturing. Its maximum dimensions are 80 columns by 60 rows, with a one-second
per-query and 60-second overall timeout. Readback recognises rendered font
characters; graphics, alternate fonts and cursor overlays can affect results.

The reference contract is Agon documentation `vdp/System-Commands.md`,
"Get screen character"; stock VDP 2.16.0 `video/vdu_sys.h` handles command
0x83. AgonDev supplies `sysvar_scrchar` and `vdp_pflag_scrchar`. These upstream
checkouts are read-only references. The tested build is
`keyboard-screen-r01-b2026-09-13-05-06-54Z`, 1896 bytes, SHA-256
`45d75610545ea7d00d92c8e11ac889d14f149cbd10e9933d6e2baef7ca6e8021`.
It is an experimental diagnostic, not a qualified product.

From the repository root, generate an ignored identity header for each new
build, then compile. Set `AGONDEV_TOOLCHAIN` when `agondev-config` is unavailable.
Preserve the generated identity, source hashes and executable hash with any
new evidence; do not reuse the historical timestamp for changed bytes.

```sh
.venv/bin/python - <<'PY'
from datetime import datetime, timezone
from pathlib import Path
import json
source = json.loads(Path('examples/keyboard-screen/identity.json').read_text())
identity = source['source_identity'] + '-b' + datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
directory = Path('examples/keyboard-screen/build')
directory.mkdir(exist_ok=True)
(directory / 'identity.h').write_text(
    '// Generated build identity; do not edit.\n'
    '#define KEYSCREEN_BUILD_ID "' + identity + '"\n')
print(identity)
PY
make -C examples/keyboard-screen
sha256sum examples/keyboard-screen/bin/keyscreen.bin
```

Stage the binary at `/extender/keyscreen.bin`, then invoke a verified finite
batch through the ordinary CLI:

```text
LOAD /extender/keyscreen.bin
RUN
LOAD /extender/sdserve.bin
RUN . /
```

After that final SD service starts, download `/extender/key-screen.txt`. Root
autoexec or a separate setup batch owns mode 3 and `EMOS KEYINPUT extender`.
Allow the CLI prompt to return before typing EXEC; the input path does not
provide a queue for commands typed while MOS is still executing a previous one.
Do not overwrite the helper batch while its final service holds it open.
