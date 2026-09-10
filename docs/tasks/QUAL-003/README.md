# Paired graphics comparison

Bounded implementation silo for [QUAL-003](../QUAL-003.md). `suite/` contains a
vendored working copy of agon-utils `examples/extender`: Shapes, Bitmaps and
their build inputs/reference tests. Original file hashes and source status are
in `upstream-snapshot.json`; changes here do not modify the source checkout.
Preserve nested vendor provenance and licensing. Generated build/review/media
outputs are local, not part of this import.

The original README and task documents under `suite/` describe its upstream
single-display behavior. QUAL-003 is authoritative for this paired adaptation.
Expected rendering discrepancies remain visible; they are not silently fixed
or removed from the comparison suite.

Local baseline build/check (does not deploy or launch the upstream emulator):

```sh
make -C docs/tasks/QUAL-003/suite PYTHON="$PWD/.venv/bin/python" all check
```

## Paired operation

Each stage selects mainboard output through `EMOS LEGACY --keep-display`,
draws and records its samples, then selects EDP through
`EMOS EXCOM --keep-display` and repeats the same stage. The keypress pause is
on EDP, with both images retained. Space or another ordinary key advances;
Escape finishes the fixture and returns to the ExCom MOS prompt. Native USB
keyboard selection is independent of these display requests.

Shapes contains 24 pages. Bitmaps contains 32 pages with 123 individual
keypress stages. Optional `RUN . N` selects one page. The bitmap suite preserves
resources and staged sprite changes independently on each renderer. The test
reports sample mismatches as observations, including known stock discrepancies;
a successful program return is not a blanket graphics-fidelity PASS.

The startup sequence is owned by autoexec:

```text
VDU 22 3
LOAD /bin/EMBOOT.BIN
RUN
SET KEYBOARD 1
EMOS KEYINPUT extender
VDU 22 20
EMOS EXCOM
VDU 22 20
CD /extender
LOAD shapes.bin
RUN
```

The first mode-20 command configures mainboard VDP; the second configures EDP.
Use `LOAD bitmaps.bin` for the other tour. Each fixture requires the new paired
EMOS/P4 keep-display implementation; it stops on a nonzero switch status.
No test program selects a video mode. Runtime files are the chosen `.bin`,
`/bin/EMBOOT.BIN`, and (for Bitmaps) generated `/extender/assets/bitmaps/` files.
Source, emulator libraries and build directories do not belong on the bench SD.

## Isolated emulator review

`prepare_review.py` validates a guarded EMOS build bundle and the existing
UART1-capable runtime, builds fixtures and prepares a frozen profile under this
project's `.emulator/`. Its media manifest records exact inputs and outputs.
It launches nothing and writes no removable media. Supply local EMOS bundle,
Fab and runtime paths through its required command arguments; `--help` lists
options. `--app shapes` or `--app bitmaps` selects the tour; `--page N` restricts
it to one page and `--stages N` can exercise an early Escape. `--human` prepares
an attention review that stays at its last paired pause and opens both captured
images together. Launch only from the generated `profile/` directory using
`./fab-agon-emulator`.

The peer executes actual EMOS against two native stock VDP instances and the
maintained P4 control/key mapper. Automated checks compare independent pixel
replies, reject timeouts and verify ExCom exit. Captures include mainboard SDL
presentation and the peer's actual framebuffer. These are application/routing
checks; they do not prove P4 pixels, physical UART timing or browser performance.
The separate retained P4 control/mode-lifecycle test exercises the production
prepare-keep handler. Hardware comparison follows human review and candidate
freeze.

Provenance adjustments: original absolute workstation paths were reduced to
repository-relative source references, and the source TODO was renamed
`UPSTREAM-TODO.md` and marked historical. `upstream-snapshot.json` retains the
original source hashes; review manifests identify this adapted copy separately.
