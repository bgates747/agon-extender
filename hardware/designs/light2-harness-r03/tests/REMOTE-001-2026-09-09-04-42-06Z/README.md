# Guarded EMOS installation media ready

The Author confirmed the expected graphical typing result. Source checkpoints
are Extender `5e8ebf5` and EMOS `a8cd361`; clean candidate builds and their
ordinary boot/typing checks pass. This record covers SD preparation only.

The existing v0.1.8 image is verified as EMPREV.BIN and backed up off-card.
The older v0.1.7 rollback is preserved as EMV017.BIN. The installer publishes
its autoexec only after all payload/rollback checks pass, renames EMNEW.BIN
before invoking the lowercase `mos` flash target and stops on subsequent
boots when the rename source is absent. The card is safely unmounted.

The Author inserts the SD in Agon and presses/releases reset once. After a
successful flash, return the SD for the same-build EMBOOT/BTYPE test autoexec.
P4 candidate files are staged and verified but its firmware is unchanged.
There is no physical typing result and no new analyzer claim here.
