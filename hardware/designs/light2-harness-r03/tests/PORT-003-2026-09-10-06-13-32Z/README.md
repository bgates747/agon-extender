# RGB222 r06 keyboard and display-admission investigation

Run `PORT-003-2026-09-10-06-13-32Z` records the installed console r06 during
Author-operated Agon resets and a manual ExCom request. Opening the serial
recording restarted P4; the agent did not reset Agon or change firmware/SD.

1. After the initial unrecorded keyboard-readiness failure, keyboard admission
   worked with browser video disconnected following the P4 restart.
2. Keyboard admission also worked after browser connection and an Agon reset.
3. The Author manually requested `emos excom`; display switching failed with
   Legacy retained. Keyboard and mainboard slideshow remained usable.
4. P4 recorded PREPARE (`op=1`) and ABORT (`op=4`), no accepted COMMIT, no panic
   or UART fault, and continuing browser frames. Lower-priority periodic
   diagnostics had long gaps while video was active.

`console-and-video.txt` is a filtered, machine-neutral serial excerpt.
`observation.yaml` records the original log hash and scope. Full private capture
and device provenance remain in the ignored bench records. A host regression
subsequently identified duplicate in-flight snapshot requests; r07 corrects that
defect. This record alone does not prove the entire cause of either timeout.
