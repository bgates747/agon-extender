# Unattended regression suite

The maintained regression runner exercises the current Extender host, browser
and native `p4-console` build closure without flashing or resetting either
board, changing either SD card, launching a foreground application, or attaching
an extra browser consumer to the P4. The explicit case and exclusion inventory
is `tests/regression-suite.json`.

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
poll the run with an agent. On completion or detected failure, the terminal hook selects Legacy,
plays the accepted `/extender/attention.txt` spoken cue, and then prints the
final result so alert output cannot erase a failure message. The hook does not
reset either board.

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
