# EMOS installation confirmed; paired graphics ready

The Author reports a successful EMOS v0.1.12 flash. The returned SD has consumed
`EMNEW.BIN`, and `EMDONE.BIN` matches the candidate payload. Working v0.1.11
and older v0.1.10 rollback images remain intact. This combines the Author's
installation observation with media integrity; it is not independent eZ80
flash readback.

The workstation verified all 29 previously staged runtime files and replaced
only the installer autoexec with the committed paired-graphics startup. The
card was safely unmounted. Shapes starts automatically with native USB input,
mode 20 on both displays and ExCom selected. P4 console r04 remains deployed;
no P4 reset, flash, serial or network operation accompanied this handover.

Physical paired rendering, program exit and repeat observations remain pending
under [paired-graphics-probe-r01](../paired-graphics-probe-r01.md).
