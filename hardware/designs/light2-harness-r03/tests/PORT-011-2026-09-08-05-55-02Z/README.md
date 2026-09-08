# EMOS v0.4.0 installation confirmed

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

The preceding sequence records the original installer handover. The Author
subsequently reported **"flash successful"** and authorized continuation.
On SD remount, EMDONE.BIN matched the candidate SHA256
`552f7a22b06e84771e81def293f1127d5278d8fc5f17cefb32187fac881491f8`;
EMNEW.BIN was absent. Both rollback hashes remained unchanged. This is an
Author-reported installation corroborated by the consumed payload; no raw
flash-screen CRC/Done image was supplied for this installation.

The [separate smoke/flow preparation](../PORT-011-2026-09-08-06-05-59Z/README.md)
replaced the installer. Physical smoke and flow-control results remain pending.
The agent did not reset or flash the Agon, touch the onboard VDP or operate
the reset breakout. Both boards remained powered with the harness seated.
