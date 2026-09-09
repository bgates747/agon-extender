# Keyboard candidate installation media

The Author accepted the controlled graphical proof, requested source freeze
and continuation, and approved registry r39 candidate promotion. The reviewed
checkpoint is Extender `c8848e5` and EMOS `5d4ebfe`. Candidate metadata and
capture preparation are Extender `2426534` and EMOS `86bfe8e`.

EMOS `agon-emos-v0.1.8-b2026-09-09-03-07-18Z` passes all configured qualification and linked
checks, ordinary/bad-SD smoke, absent-peer command recovery, the paired twelve
key events and the admitted-but-silent application timeout. The resident EMOS
source is unchanged from the reviewed draft; the candidate uses new build
metadata. The SD observer is `uart-keyboard-probe-r01-b2026-09-09-03-09-38Z`.

A pre-existing generic portability check initially blocked candidate production.
Builder `85a3be5` replaces the UART emulator helper's implicit host-library
location with an explicit input. All 134 generic tests pass; generated runtime
sources and both executable hashes match the already reviewed runtime exactly.
The portability guard remains unchanged.

The guarded installer is staged and the SD safely unmounted. Working EMOS
v0.1.7 is verified both off-card and as `EMPREV.BIN`; the older v0.7.0 payload
is `EMV070.BIN`. Existing older rollback files remain intact. Autoexec renames
the new payload before `FLASH mos EMDONE.BIN -f`, so a subsequent reset stops
before attempting another flash.

P4 `uart-keyboard-probe-r01-b2026-09-09-03-01-48Z` is staged with matching remote hashes and verified
stable USB identity. It has **not** been flashed or reset; its prior counting
receiver remains installed. The paired capture launcher is prepared but is not
activated until both candidates are installed. It requests 24 MHz / 288M
samples and finishes after acquisition and five clean seconds after final PASS.

Next: the Author inserts the prepared SD, resets Agon once and confirms the
MOS flash result, then returns the card for separate smoke/keyboard-test media.
P4 deployment needs its separate authorization. Physical installation and
keyboard qualification remain pending; this record is preparation evidence.
