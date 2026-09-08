# EMOS UART candidate — installation, smoke and no-reply case passed

The workstation prepared `agon-emos-v0.3.0-b2026-09-08-04-04-00Z` from
clean EMOS/builder inputs. The full configured gate and the exact candidate's
ordinary, bad-SD and combined smoke/no-peer emulator checks pass. Its
implementation matches the Author-accepted draft; only identity/status
metadata changed. The [build manifest](build-manifest.yaml) identifies inputs.

The [preparation record](sd-preparation.yaml) preserves the initial partial
state. Subsequent installation and timeout observations are recorded below.
The SD was safely unmounted after writing and verifying `/EMNEW.BIN` and the
[two-line installation script](install-autoexec.txt). The prior working v0.2.0
payload remains as `/EMBACK.BIN`, with a verified off-card backup.

The operator inserts SD into the powered Agon and presses/releases reset once.
The updater should report `Checking CRC... OK`, `Done`, then reset. The next
boot stops at the missing `/EMNEW.BIN`; that rename error prevents reflashing.
Do not interpret that stop as the UART test. After installation, the operator
remounts SD locally for the combined SD/clock and no-peer timeout script.

Both boards remain powered, the harness remains seated, and the P4 remains
receive-only. No WROOM or reset-breakout operation occurred.

## Installation report and second SD handover — 2026-09-08

The Author reported a good flash and remounted the card. The workstation
found EMNEW.BIN absent and the renamed EMDONE.BIN matching the exact v0.3.0
candidate hash. [Installation result](installation-result.yaml) distinguishes
the Author report from a raw flash capture or separately reported CRC display.

After verified backups, the workstation staged the same candidate's ordinary
smoke program and [combined test autoexec](test-autoexec.txt), verified the
files against the checked emulator profile and safely unmounted the card.
The next Agon reset should show SD/CLOCK PASS, then the intentional no-reply
timeout and prompt return. The hardware test outcome remains pending.

## Physical timeout result — 2026-09-08

The Author supplied a physical Agon screenshot confirming the exact v0.3.0
candidate identity, SD/CLOCK PASS, expected missing-reply failure and final MOS
prompt. The [timeout result](timeout-result.yaml) records this as a passing
negative case. The screenshot does not measure elapsed time and has no archived
file in this bundle. The P4 remains the receive-only predecessor; successful
acknowledgement remains untested. The inherited Volume timeout text follows
the UART failure; it does not contradict the SD PASS.
