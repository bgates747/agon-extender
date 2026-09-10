# ExCom EMOS installation and repeatable startup

The Author reports successful EMOS v0.1.11 flashing. The returned card has
consumed EMNEW.BIN; EMDONE.BIN matches the exact candidate and the v0.1.10,
v0.1.9 and v0.1.8 rollback payloads retain their expected hashes. This combines
an Author installation report with SD integrity verification; it is not an
independent readback of eZ80 flash.

Replaced the installer with the candidate's matching EMBOOT/check data and
the non-flashing autoexec from uart-excom-console-r01. The current card files
were backed up first and autoexec was published last. The card is safely
unmounted. The already verified P4 candidate remains running; no new P4 serial,
reset, flash or network operation was performed. The Author's ordinary ExCom
console test is next; no physical console PASS is claimed.
