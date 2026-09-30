# Firmware qualification suite

The canonical executable authority is [`../../qualification/`](../../qualification/README.md).
The maintained workflow has two independent commands. The first command builds
and flashes one exact component commit and independently verifies the installed
bytes and boot identity; run it separately for P4 and EMOS. The second command accepts both receipts,
runs every applicable installed-hardware case. The separate offline source
suite remains available for development regressions. A host or emulator pass is never described as
hardware validation or firmware acceptance. Acceptance requires a successful
complete canonical run against verified installed bytes.

The maintained regression runner exercises the current Extender host, browser
and native `p4-console` build closure without flashing or resetting either
board, changing either SD card, launching a foreground application, or attaching
an extra browser consumer to the P4. The explicit case and exclusion inventory
is `qualification/manifests/offline.json`. Physical additions are registered in
`qualification/manifests/hardware.json`. They do not weaken or replace any retained
case. `qualification/run.py` consumes the hardware inventory and refuses
to run a physical case without the matching verified component receipt.

The launcher resolves the selected Extender commit once and materializes it in
an ignored local shared clone. The suite runs only from that pinned snapshot and
the selected clean EMOS commit, checking both identities before every case and
at completion. The ordinary development checkouts may therefore change while
the suite runs; no separate Git worktree is required and those edits cannot
silently enter the active run.

Performance measurements and physical/manual cases are not part of this run.
In particular, Nurples and other loaded-asset mode-switch cases remain at the
end of the automated passes for manual testing under the Author's accepted
AUDIT-010 disposition.

## Launch from another computer

The Pop!_OS host has a machine-local `agents/regression-suite.local.json` with
the current Extender HTTP endpoint. It is ignored and must not be copied into
tracked documentation. From an SSH client, run:

```sh
ssh smith@POP_OS_HOST /home/smith/.local/bin/agon-extender-regression
```

The launcher prints the fresh job path, then streams concise phase, current-case
and case-result lines to the SSH console. The actual worker is detached: closing
SSH or pressing Ctrl-C stops only the status stream and does not stop the suite.
`--detach` returns immediately when no live console display is wanted. Do not
poll the run with an agent. On completion or detected failure, the terminal hook
selects Legacy, plays the accepted `/extender/attention.txt` spoken cue,
explicitly exits the listener started by that batch, and then prints the final
result so alert output cannot erase a failure message. The hook does not reset
either board.

The printed paths identify these durable records:

1. `result.json` — detached command and notification-hook status and durations.
2. `suite/progress.json` — last durable phase/case or terminal state.
3. `suite/events.jsonl` — fsynced UTC transition history.
4. `suite/summary.json` — source identities, case results, separate preparation,
   fixture-runtime and retrieval durations, and stated coverage limits.
5. `suite/cases/*.log` — one combined stdout/stderr log per case.
6. `notification.json` — cue execution receipt, separate from whether a human
   heard it or observed the Legacy pixels.

The suite deliberately does not write progress to the mainboard for each host
case: it does not own the foreground, and taking that ownership could alter a
concurrent physical workload. The durable host records are its progress channel.
Only the terminal notification interacts with the admitted Extender keyboard.

## Commit-pinned hardware workflow

The machine-local `agents/hardware-validation.local.json` follows
`qualification/config.example.json`. It identifies the component-owner
checkouts, exact P4 USB identity and remote flashing tool, Extender endpoint,
and the independently commissioned Agon reset controller. It remains ignored;
tracked files contain no bench addresses, credentials or unique device values.

The flash command is independent of the test command:

```sh
.venv/bin/python scripts/flash_firmware_commit.py \
  --target emos --commit EMOS_COMMIT
```

Use `--target p4 --commit EXTENDER_COMMIT` for an Extender/P4 repair. The
command resolves the revision to a full commit, builds from a fresh detached
snapshot, performs exactly one component-appropriate flash, verifies the full
EMOS ROM or P4 flash plus observed boot identity, and prints the durable local
receipt path. It never accepts a dirty working tree as the requested firmware.

The hardware test command is separately invoked with that receipt:

```sh
.venv/bin/python qualification/run.py \
  --flash-receipt /absolute/path/to/p4-flash-receipt.json \
  --flash-receipt /absolute/path/to/emos-flash-receipt.json
```

It streams every named check and pass/fail status to the invoking SSH console.
The full run requires verified P4 and EMOS receipts and runs all applicable
physical cases against the already installed firmware. It
does not rebuild or reflash. It writes an overall `summary.json`, restores each
case's startup state, sends the accepted Legacy spoken cue, and leaves a failure
verdict on the Legacy screen after alert playback. The operator does not need an
agent to monitor the run.

The mandatory integrated smoke exercises the installed P4 web assets, browser
reset bridge, P4-to-EMOS keyboard path, ExCom display/status/text capture, and a
temporary exact-byte mainboard-SD round trip, then restores the ordinary startup
state. The additional EMOS physical case is `a10-rp04-raw-sd-write`. Its eZ80 fixture
refuses to write unless the card has a valid MBR whose first partition begins
after sector 2. It retains sector 2 in RAM, exercises the repaired RST `0x08`
write API, independently reads the result, restores through MOS's distinct C
write dispatch, and independently verifies the exact preimage before reporting.
An unverified restoration is an infrastructure failure and stops advancement.

## First complete RP04 hardware run

Exact EMOS commit `8ecea5bc6cb4f9f563bc570316afbdaa08648632` was
built, flashed and verified by full installed-ROM readback. Exact Extender
runner commit `1b79083038b83fc4a60265b3d05db1e554e51c15` then
produced the retained local run
`agents/hardware-validation/regression-2026-09-29-23-07-38Z-1b79083038b8/`.

| Field | Result |
| --- | --- |
| EMOS artifact | 128,579 bytes; SHA-256 `7c7ac79fcbdb4a9d67885aede552e808e0111bcc7e2d54b012c43add0305317a` |
| Installed ROM | 131,072 bytes; exact padded match; SHA-256 `4fab4a413ff3e7d163ee8bd605ef9390503ba25db116a5c9e6137e300932a729` |
| Retained closure | 55 passed; zero failure, infrastructure error, timeout or blocked; 150.491329 monotonic seconds |
| Physical fixture | pass; 142.566509 monotonic seconds; fixture SHA-256 `9ed1064702f339ca8b6f3bb4ba852cdb9ccf724b59446ff4859b69eb85a47ce3` |
| Card safety | sector 2; first partition LBA 8192 |
| Test oracle | write/read pattern CRC32 `3b3befd6`; test status 0 |
| Restoration oracle | preimage/restored CRC32 `b2aa7578`; restore and verification statuses 0 |
| Startup | exact original 85-byte `/autoexec.txt` restored; final ready reset observed |
| Overall summary | success; SHA-256 `b3a2124ed85416e4788570b956a73dca8bb4239e35a3fdfe500d39f5ba9bf04a` |

The spoken Legacy cue ran. The run exposed that the retained attention batch
leaves its SD listener in the foreground; the maintained notifier now exits
that listener before printing its durable verdict. That follow-up has a
targeted structural test and was manually exercised against the run's actual
listener without replaying the already-heard alert.

## Bounded development checks

`--case CASE_ID` or repeated `--phase host|browser|build` options select a
subset. `--no-notify` exists only for runner development; a run using it does
not satisfy the unattended hardware-notification contract. The default launch
is the full manifest at the commit resolved from `HEAD`, with notification.
`--commit COMMIT` selects another existing commit explicitly.

An output folder is never reused. Success means every selected independent case
passed, the native source identities stayed fixed and clean, and the terminal
notification hook succeeded. A missing terminal `result.json` after a host
interruption is unknown, not success.

## First retained complete pre-hardware run

The Author launched the first full pinned run from the Lenovo on 2026-09-29.
The ignored local evidence directory is
`agents/regression-runs/2026-09-29-21-25-50Z-a8e6c5dc549f/`.

| Field | Result |
| --- | --- |
| Extender source | `a8e6c5dc549f355f2264c1423609d2b147410a60`, clean and unchanged |
| EMOS source | `21a9ba27f1f346473d767c2c3053ee18e8911335`, clean and unchanged |
| Cases | 54 passed; zero failure, infrastructure error, timeout or blocked |
| Suite duration | 143.542507419 seconds monotonic |
| Phase duration | host 35.843347309 s; browser 24.551770785 s; build 82.770066925 s |
| Terminal hook | success; 19.632202248 seconds; 108 keyboard events accepted, zero discarded/pending/held |
| Complete detached job | success; 163.236620222 seconds |
| `suite/summary.json` SHA-256 | `798f69c986f301b4d91bfec01adee98e046ca8cfb80e363e24be83d173b6db5f` |
| `result.json` SHA-256 | `4a21029917fff5357344ba11ce80298617704df8e23233f9b47456db40ad0241` |

The terminal-hook receipt proves accepted keyboard injection, not that the
Author heard the cue or observed Legacy pixels. This run establishes the pinned
pre-RP04 host/browser/native baseline; its EMOS commit predates the uncommitted
RP04 raw-SD repair and therefore is not RP04 acceptance evidence.
