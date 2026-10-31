# Firmware qualification suite

The canonical executable authority is [`../../qualification/`](../../qualification/README.md).
The current installed-pair workflow and output profiles are documented in the
canonical guide above. Offline retained-installation receipts do not require
reflashing accepted images merely to fit an older receipt schema. The separate
offline source suite remains available for development regressions. A host or
emulator pass is never described as hardware qualification.

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

Use the [canonical network instructions](https://github.com/bgates747/agon-dev-env/blob/feature/standardized-deployment/codex/environment.md#ssh-between-development-machines) to select and access the current regression host.
The host-local `agents/regression-suite.local.json` owns the Extender HTTP
endpoint and remains ignored. Once connected, invoke the installed application
launcher locally:

```sh
~/.local/bin/agon-extender-regression
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

## Installed-pair qualification workflow

Use the [canonical guide](../../qualification/README.md) for schema-2 evidence
receipts, offline fixture builds, browser-video/native-HDMI profiles and the
`--check-only`/later physical invocation boundary. Its current physical entry
contract is an independently verified idle Legacy CLI with single-buffered modes,
current paired identities and a commissioned reset bridge. Mode selection is
conditional, settling is at least one second, and both entry modes are restored.
Startup stays read-only; raw-SD tests run through explicit CLI LOAD/RUN.

Flashing remains an independently authorized operation under the installation
protocol. Do not use the old generic commit flasher to replace an accepted native
P4 or patched EMOS image simply to generate qualification paperwork. Exact
retained readbacks/source closure can instead be verified offline. Native
production installation still follows its selected component/board recipe.

The historical results below retain their original setup and timing. In
particular, old startup-mutating recipes and observer-present browser checks
are not current launch instructions for HDMI. The separate cadence runner is
disabled pending lifecycle migration; its analysis helpers remain available.

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
