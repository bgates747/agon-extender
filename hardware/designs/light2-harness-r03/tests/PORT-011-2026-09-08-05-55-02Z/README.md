# EMOS v0.4.0 installation media prepared

Clean candidate `agon-emos-v0.4.0-b2026-09-08-05-51-31Z` passed the complete configured
build/linked/runtime gate, 68 host tests, ordinary/bad-SD smoke and the
combined smoke/no-peer check. The implementation matches the Author-reviewed
draft; its [manifest](build-manifest.yaml) records the frozen inputs.

The [preparation record](sd-preparation.yaml) confirms verified installer
media and safe SD unmount. Both working EMOS payloads are retained on-card
and in verified off-card backups: v0.3.0 as EMPREV.BIN, older v0.2.0 as
EMBACK.BIN. P4 deployment [PORT-011-2026-09-08-05-54-22Z](../PORT-011-2026-09-08-05-54-22Z/README.md) passed.

The operator inserts this SD into the powered Agon and presses/releases reset
once. Expect the flash utility's CRC check and Done, followed by reboot. The
next boot stops because EMNEW.BIN has already been renamed to EMDONE.BIN;
that error is the reflash guard, not the flow test. After success, remount
SD on the workstation for the separate same-build smoke/UARTFLOW script.

Agon installation and physical flow-control results are pending. The agent
did not reset or flash the Agon, touch the onboard VDP or operate the reset
breakout. Both boards remained powered with the harness seated.
