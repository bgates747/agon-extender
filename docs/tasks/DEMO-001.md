# DEMO-001 — Visible network replacement with spoken boot alerts

Completed demonstration; accepted and commit-authorized on 2026-09-13 UTC.

Historical request: prepare a British-accented greeting for the Author's friends
on the Agon Discord, stage it for boot, then use a standard non-voice emulator
attention cue. Hardware playback/reset must wait for the Author's explicit
filming clearance. The Author selected Pi-controlled mainboard reset, with no
P4 involvement: the mainboard may control the Extender, not the reverse. The
latest four-wire description matches the existing GPIO17 transistor reset
actuator recorded in SETUP-006.1.1, superseding the provisional direct-ZDI
proposal. Preserve the existing GPIO assignment. Wiring verification is still
needed before any actuation, particularly the previously unresolved emitter
ground. No GPIO or USB serial port has been driven/opened in this increment.

The Author requests a new hello-world executable deployed to the mainboard SD,
startup changed to run it, then a changed executable deployed and launched after
a short interval. Produce AgonJukebox-compatible WAV speech with a female voice.
The Author confirmed the hardware startup beep works and sdserve is running
after a reset. Prefer hardware speech for attention; an emulator is the fallback.

1. [x] Prepare two visibly different builds from maintained example source and
   two preloaded speech clips. Use official MOS/VDP APIs and unchanged firmware.
2. [x] Run a headless smoke, validate both WAVs with AgonJukebox's converter and
   verify deployment/readback over the accepted SD service.
3. [x] Arrange one initial keyboard handover, then let the existing service EXIT
   resume a finite MOS batch between the two executions. The host must wait for
   the first execution receipt before replacing the executable, verify the new
   bytes and request EXIT only after successful activation/readback.
4. [x] Record actual hardware receipts and the Author's visual/audio observation.
   Preserve startup, executable and firmware rollback; do not claim sound was
   heard solely because the VDP acknowledged a playback command. Leave source
   changes uncommitted until the applicable human validation/commit gate.

## Contract and research boundary

The accepted SD API intentionally has no remote shell or game-launch operation.
After the Author's reset the service's parent autoexec remains open. Do not
overwrite it. Stage a separate initial installer; the Author exits sdserve and
executes that installer at the MOS CLI once. The installer renames the closed old
startup to a retained backup (MOS COPY refuses existing targets) and installs the verified new boot sequence after its old handle closes.
The second launch follows an ordinary batch continuation after network EXIT;
no reset, firmware patch, browser input restoration or UART ownership bypass.

Read references: official agon-docs `docs/mos/Star-Commands.md` (EXEC stops on
command failure; LOAD/RUN; COPY), `docs/mos/API.md` (file handles, sysvars,
RST18), `docs/vdp/Enhanced-Audio-API.md` (buffer sample, unsigned PCM, explicit
sample rate and command status). Source `agon-emos/src/mos.c:mos_EXEC` confirms
the batch remains open while a child runs. Stock agon-vdp v2.16.0 is read-only;
its serial/ZDI monitor requires console mode and is not an established remote
launch path on this bench. The unresolved reset circuit remains untouched.

AgonJukebox `README.md` and `scripts/make_wav.py` define mono unsigned 8-bit
RIFF/WAVE, sample rate 1..65535 Hz. Use that maintained converter at 16000 Hz.
This bounded example plays its generated PCM subset; it does not fork the
Jukebox UI or its general WAV reader. Speech uses gTTS 2.5.4 English/co.uk:
https://github.com/pndurette/gTTS and https://gtts.readthedocs.io/en/v2.5.4/module.html.
That service has no explicit gender parameter; generated voice must be auditioned.

Generated binaries, WAVs, host transfer state and run evidence stay in ignored
`agents/network-hello` and `.emulator/network-hello`. They are development
demonstrations, not a new firmware release or an artifact-qualification claim.
Rally, P4, EMOS and onboard VDP executable bytes remain unchanged.

## Preparation checkpoint — 2026-09-13 UTC

Two executables compile with warnings as errors: build one is 10439 bytes,
build two 10453 bytes; their SHA-256 values and exact source hashes are retained
in ignored `agents/network-hello/builds.json`. Speech clips are 7.32 and 7.68
seconds at 16000 Hz; AgonJukebox's own validator accepts both RIFF files.

The actual eZ80/EMOS/raw-FAT and maintained P4 queue headless smoke passes both
execution receipts, sample-create/select/play acknowledgements, replacement
readbacks and EXIT/batch continuation. A separate initial-installer run replays
mapped native Escape and typed EXEC, verifies the preserved startup and newly
installed autoexec, then passes the same two executions. One WRITE response is
withheld before the P4 queue in each test; exact replay recovers. Headless sound
acknowledgements are not a human listening result. Profiles and results are in
`.emulator/network-hello` and `.emulator/network-hello-installer`.

Physical payload staging is in progress through the unchanged accepted service.
The open startup remains untouched; no board serial port or firmware is opened.
The network observer is `scripts/run_hello_demo.py`; it must not be armed until
all initial payloads and readbacks finish. It waits for a changed incarnation
and the first expected execution receipt, uploads the distinct second binary,
checks its prior-version backup, requests EXIT, then checks the second receipt.
It stops on unexpected state instead of guessing. All changes remain uncommitted.


All five initial payloads have now been uploaded, activated and completely read
back on the physical card: hello build one, both WAVs, boot sequence and initial
installer. The original open autoexec still matches its preserved hash. The
observer is armed; the labelled fallback emulator requests one native Escape /
`EXEC /extender/hello-start.txt` handover. It is an attention cue only, not test
execution. The subsequent host replacement and EXIT/batch launch are automatic.
Machine-local PIDs, state and recovery are in `agents/network-hello/RESUME.md`.
Hardware execution and the Author's visual/listening confirmation remain pending.


## Physical result — 2026-09-13 UTC

Both hardware execution receipts pass. The Author completed the initial CLI
handover and confirmed the British-accented speech. The host read back the
installed startup and its preserved predecessor, verified build one, uploaded
and activated the distinct build two, checked the first-version backup and sent
EXIT. The finite batch then launched build two; its stage and audio-command
receipt pass and the service is online again. No second keyboard action, card
movement or reset was requested. See [the evidence](DEMO-001/evidence/README.md).

The Author's first listening confirmation is recorded exactly and separately
from the machine results. No explicit second-stage visual/listening response
or commit approval is inferred. Implementation and headless/hardware execution
are complete; the final review/commit gate remains open. No firmware or Rally
changes, no push, and no further attention cue is needed for this result.

## Filming increment

Prepare a third literal-message build and `discord.wav` using the same accepted
gTTS British English selection and Jukebox converter. Headless smoke is allowed;
do not trigger hardware playback. Preserve the current executable and the older
`.p17bak` before replacing the boot-selected `/extender/hello.bin`. Existing
autoexec already loads that pathname and is open in its final sdserve call, so
leave its bytes alone. Verify all payloads over the SD API, then prepare the
normal emulator attention cue and wait for explicit filming clearance.


## Discord greeting ready; reset wiring pending — 2026-09-13 UTC

The stage-three 10440-byte executable and 243534-byte, 15.216-second WAV pass
headless execution/sample acknowledgements and physical network activation
with complete readbacks. Both older executables are preserved: first build at
/extender/hello-one.bin and second build at /extender/hello.bin.p17bak. Startup
is unchanged and still selects /extender/hello.bin. No hardware playback, reset,
EXIT, firmware change or Rally change was requested. Selected evidence is in
DEMO-001/evidence/discord-{headless,deployment}.json. All changes stay uncommitted.

Existing reset lead intent: Pi white physical11/GPIO17 through 10 kohm to base;
Pi black physical9/GND and Agon-bound black share emitter ground; Agon-bound
white comes from collector. The legacy document's P4 ESP_EN endpoint is an
alternate historical attachment, not the current requested mainboard target.
Olimex AgonLight2 Rev B schematic page3 identifies ZDI1 pin2 as RST\EN and
pins3/5 as GND. Confirm the actual board/header orientation and continuity
before applying that schematic to the loose leads. GPIO17 is currently unused
input with pull-down; no pin configuration was changed. The 2026-08-24 report
of an apparently missing emitter-ground bridge remains unresolved, rather than
being treated as a proven current fault. Await a present photo/trace.

The proposed direct Pi GPIO23/24 ZDI candidate was never deployed or driven;
it is preserved only in ignored research, superseded by the existing actuator.
The standard attention emulator must show notification-only text and no voice.
Hardware playback remains held for explicit filming clearance after wiring is
verified. A reboot, including repowering after wiring, runs the staged greeting.


## Accepted closeout — 2026-09-13 UTC

The Author corrected a ground connection on the existing transistor actuator,
requested immediate reset while filming, and confirmed success with "yay".
Subsequent SD readback reports a fresh service incarnation and
`stage=3 / audio_commands=pass`. See evidence/discord-hardware.json and the
promoted docs/bench-reset.md. The Author explicitly authorized freezing all
current progress before the next keyboard goal. This closes DEMO-001; remaining
remote typing and its distinct review cue belong to REMOTE-002. Historical
pending-review statements above describe earlier checkpoints, not current gates.

## Fixture reuse documentation review — 2026-09-24

The retained hello installer/service continuation and receipt placement predate current SD layout and the EMOSlet. Refresh them before replay; original acceptance remains valid for its recorded candidate. See [AUDIT-009 finding A09-F035](AUDIT-009/FINDINGS.md) and the
[current example index](../../examples/README.md). This is a precondition for
future reuse, not authorization to change code or repeat the bench test.
