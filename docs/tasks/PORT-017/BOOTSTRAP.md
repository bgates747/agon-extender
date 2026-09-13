# Initial commissioning and recovery boundary

The foreground service and the new owned EMOS gateway are not yet installed on
the physical Agon. Current startup enables Extender keyboard and stops at MOS;
the Author subsequently launched Rally Fuji demo manually. Do not interrupt it
until the commissioning handover is ready.

## One initial card handover

No existing network-to-SD service or supported RAM loader over this owned
UART1 path has been identified. MOS LOAD reads files already on the SD; the
Extender's current keyboard and graphics diagnostics do not create files.
Do not seize UART1 or patch resident addresses to bypass EMOS ownership.
The initial gateway firmware and `sdserve.bin` therefore need one commissioning
card handover. Subsequent qualified transfers use Ethernet and leave the card
in the Agon. A service must be running in foreground for those transfers.

1. After the Author quits Rally and mounts the card on the developer host,
   identify the AGON volume and preserve its current autoexec, accepted game,
   runtime tracks and existing EMOS rollback image before editing anything.
2. Prepare a new identified EMOS build, a matching identified P4 console build,
   and the foreground service from the reviewed sources. The exploratory
   UNVERSIONED binaries are not commissioning payloads. Commissioning identities: EMOS v0.1.14, uart-excom-console r12, new `sdserve`
   v0.1.0, and `mainboard-sd-qualification` r01. These were proposed with the
   commissioning/commit request. The Author then directed preparation of the
   returned card; proceeding under that instruction, without claiming physical
   or graphical validation.
3. Install the service at `/extender/sdserve.bin` and create
   `/extender/sdtest`. Preserve the canonical filename: the service refuses
   write/activation operations aimed at `sdserve.bin`. Initial tests use only
   the isolated test directory, not the accepted Rally runtime paths.
4. Stage the EMOS update using the already qualified MOS FLASH utility and
   one-shot rename-before-flash startup pattern. Preserve its exact rollback
   payload and a recovery autoexec. Inspect the installed utility/version and
   supported options on the returned card before generating the actual script.
   Do not invent an unverified FLASH command or make a reboot flash loop.
5. Deploy the matching P4 image through its existing Pi USB flash workflow,
   preserving and independently verifying the current r11 rollback. Its USB
   open resets P4 and temporarily disrupts keyboard admission, so schedule this
   with the agreed Agon commissioning restart. Keep onboard VDP stock 2.16.0.
6. Normal service startup after the firmware installation is:

       VDU 22 3
       SET KEYBOARD 1
       IFTHERE /ESDNEW.BIN THEN EXEC /extender/sd-install.txt
       EMOS KEYINPUT extender
       LOAD /extender/sdserve.bin
       RUN . /extender/sdtest

   Use CRLF. Video mode is selected here, never inside the fixture/application.
   Keep the accepted Rally files and its normal launch commands available.

## Host control

Use the project `.venv/bin/python scripts/sdcard.py`. Supply `--url` with the
machine-local Extender HTTP address and `--state` with an ignored local JSON
path. The client retains session/sequence and the exact pending request before
network transmission; keep that file between commands. An exclusive local lock
prevents two processes from trampling the same state. No private address belongs
in a tracked example.

Commands: `status`; `stat PATH`; `list PATH`; `get PATH NEW-LOCAL-FILE`;
`put LOCAL-FILE PATH [--activate]`; `activate TRANSFER`; `cancel TRANSFER`;
`recover PATH [inspect|restore|abandon|cleanup]`; `resume`; `exit`.
`--timeout SECONDS` bounds each request (default 60). Paths are absolute ASCII
and remain under the explicitly selected service root.

`put` verifies the stage by both Agon readback CRC and a complete host readback.
Without `--activate`, the old target remains active and the command prints the
transfer ID. Activation preserves the old file as `.p17bak`; explicit recovery
cleanup removes it only after the current file can be fully read. A later upload
rejects existing journal/backup siblings. It never silently overwrites them.

After an uncertain network result, `resume` retries the exact saved request.
It does not assume a timed-out write failed. After an application incarnation
change, preserve the old state, use a new state file and inspect the journal.
An active transfer remains owned by its existing session; losing that session
does not let another caller silently abandon it. Escape stops the foreground
program while preserving an unfinished stage for subsequent explicit recovery.

## Limits and acceptance

Rally and this foreground service do not run concurrently. EXIT returns to MOS;
it does not execute a game or expose an arbitrary remote shell. Automating the
later game/fixture launch-return cycle belongs to the dependent bench work.
Protocol framing faults use owned fault/re-admission paths; a completely hung
eZ80 cannot service SD requests. Automatic whole-Agon reset remains unqualified;
do not actuate the unresolved transistor circuit. Resetting P4/VDP over USB is
not a substitute for resetting the eZ80.

Commissioning continuation, 2026-09-13 UTC: after the concrete identity and
candidate-freeze proposal, the Author replied, "you have the card. ping me wth
teh emulator again when you're ready for me to move it back to the agon".
Proceed with the proposed candidate freeze and commissioning preparation under
that instruction. This is authorization to prepare/deploy, not a claim of human
visual validation or hardware acceptance. No automatic push.

The one-shot installer contains:

    RENAME /ESDNEW.BIN /ESDDONE.BIN
    FLASH mos /ESDDONE.BIN -f

MOS 3.0.2 documents IFTHERE and the maintained command dispatcher implements it.
The installed FLASH utility is the previously used, hash-verified utility and
supports `FLASH mos <filename> -f`. Consume the trigger before flashing. Its
restart then skips installation and runs the service, avoiding a second card
handover. Keep an off-card backup of the original autoexec, EMOS v0.1.13 payload,
FLASH utility and accepted Rally files. Do not overwrite historical EMDONE.BIN.
If installation fails, retain the displayed failure and recover with the saved
payload/startup; never automatically retry a flash on every reset.

Hardware acceptance still requires exact binary readback, keyboard coexistence,
failure/recovery exercises and ten unattended cycles. Headless emulator results
are supporting evidence only and cannot close those task phases.
