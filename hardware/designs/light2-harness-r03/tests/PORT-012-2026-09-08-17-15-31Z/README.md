# Target-baud smoke/flow media prepared

The Author reported a successful EMOS v0.5.0 flash. The consumed EMDONE.BIN
matches the exact candidate manifest, EMNEW.BIN is absent, and the working
v0.4.0 and v0.2.0 rollback hashes remain intact.

The card now contains same-build EMBOOT, check.txt and the attached autoexec:
mode 3, SD/clock smoke, then EMOS UARTFLOW at 1,152,000 baud. The installer
has been replaced and the card safely unmounted. Physical smoke/flow results
remain pending. P4 still needs the staged r02 candidate flashed before a paired
run; no P4 mutation occurred during this preparation.
