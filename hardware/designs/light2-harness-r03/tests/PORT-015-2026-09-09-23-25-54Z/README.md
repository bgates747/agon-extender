# Native USB CLI editing and source-return pass

The Author reports all requested continuation checks passed on the real Agon:

1. Agon reset, SD/CLOCK smoke, extender admission and the ordinary MOS prompt.
2. Backspace correction and Left/Right editing produced `usb cli`.
3. Holding `a` produced repeat; releasing it stopped repeat.
4. Neutral USB unplug/replug allowed `echo reconnected` without a board reset.
5. Mixed-case `EmOs KeYiNpUt` reported extender. Selecting mainboard excluded
   USB keystrokes; an Agon-only reset restored USB typing through autoexec.

This continues [usb-cli-probe-r01](../usb-cli-probe-r01.md) with the same
installed EMOS v0.1.10 and P4 candidate images. Initial mixed-case/shifted
typing and gameplay retain their earlier acceptance. No firmware or SD write
was performed for this run. Mainboard VGA supplied the operator observations;
no screen image or UART waveform was collected.

The P4 debug capture lasted 425.953 seconds and was stopped after the Author's
report. Opening serial showed one application startup, as previously observed;
the cause remains separate from this test. The expected image and keyboard
were ready before the operator's reset cue. There was no subsequent P4
application restart. Two USB connections, one removal and two native-input
admissions are present; the final P4 `keys_sent` counter is 283. That counter
counts serialization/enqueue attempts, not independently confirmed EMOS receipt.

The single error-level line occurs at unplug and matches the retained
[HID cleanup diagnostic](../usb-keyboard-unplug-review.md). Later, P4 reports
input-backlog releases, cancels blocked TX and awaits admission, then admits
input again and resumes its counter. This sequence is consistent with the
Author's mainboard-selection/reset checks and the candidate's documented
five-second blocked-TX recovery; individual operator actions were not timestamped.
No application fault, attached-operation USB error or recovery failure appears.

`serial-excerpt.txt` preserves all USB, firmware identity and error/warning
lines in order. Full serial and device metadata remain in the ignored local
capture; their hashes are in `result.yaml`. This bounded functional pass closes
PORT-015 W3's ordinary CLI proof. It does not establish exact latency/repeat
timing, working mainboard keyboard hardware, full layout/settings/LED parity,
or the remaining W1 power particulars. Artifact status remains candidate.
