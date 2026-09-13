# Mainboard SD qualification

Identity: `mainboard-sd-qualification-r01`. Status: candidate. Scope is the
owned transport and foreground storage service. These steps define evidence;
[PORT-017](../tasks/PORT-017.md) records phase completion and the
[2026-09-13 acceptance](../qualification/mainboard-sd/2026-09-13.md) composes its
separate physical, keyboard and delivery observations. Promotion to this path
changes navigation only; the procedure identity and candidate status remain.

1. Freeze EMOS, P4 console, service, client and procedure source commits. Build
   identified candidates from clean inputs, retain manifests and full profile
   link guards, then run host regressions and an isolated headless raw-FAT
   smoke with the exact EMOS/application images. No graphical summons yet.
2. Follow the [commissioning bootstrap](../tasks/PORT-017/BOOTSTRAP.md). Preserve rollback payloads and card startup. Verify the
   stable P4 USB identity, stage and hash-check its candidate, flash through
   the established USB procedure, independently verify flash, and capture the
   exact build identity plus USB-host readiness. Reject boot faults. Keep
   onboard VDP stock; never actuate the unresolved Agon reset circuit.
3. Hash-check the card's one-shot installer, application, candidate EMOS and
   preserved Rally files. Sync and unmount. Summon the Author only now to
   return the card and reset Agon. Record physical boot separately from any
   emulator proof. Missing readiness, repeated restart or failed admission is
   a failed commissioning attempt, not grounds for blind reflash loops.
4. Require a live SD presence through P4 HTTP. Record session/boot identity and
   every request/result. Use only `/extender/sdtest` initially. Exercise STAT,
   LIST, zero-byte files, payload boundaries 212/213, a file larger than 64KiB
   and the accepted Rally binary's size. For each upload, require Agon CRC and
   complete host comparison of both stage and activated target. Check old
   target retention and explicit backup cleanup. Never overwrite live Rally.
5. Exercise identical-request retry, duplicate/conflict handling, denied paths,
   invalid transfers, interrupted staging, explicit journal inspection and
   recovery. Preserve ambiguous files. Host fault injection and raw FAT prove
   software paths only; distinguish them from physical network interruption,
   reset recovery and media-error observations. Do not deliberately remove a
   powered card or damage FAT for a test. Bound waits and stop on unexplained
   transport or integrity faults.
6. Run ten consecutive unattended upload/verify/activate/readback cycles to a
   test target, retaining previous-version backups until validated cleanup.
   Log byte sizes, hashes, durations, responses and failures. A failure breaks
   the acceptance sequence; repair/rebuild with fresh identities and rerun as
   appropriate. Do not report emulator timings as physical throughput.
7. Confirm native Extender keyboard input during active transfers and after
   service exit, using the Author's accepted USB path and a bounded requested
   observation when automation cannot establish it. Demonstrate Escape/MOS
   return and subsequent service startup/recovery. No unsupported remote shell
   or UART takeover is permitted to avoid that observation.
8. Preserve completed evidence with source/build hashes and limitations, then
   commit phase completion only when its requirements pass. Human acceptance
   remains explicit; candidate build success is not qualification. No push or
   downstream Rally/Golem optimization is authorized by a partial result.

The committed physical-run controller is `scripts/qualify_sdcard.py`. Supply a
local `--url`, a new ignored `--output` directory and optional per-request
`--timeout` (30 seconds by default). It leaves the service running and preserves
client state/audit after failures. Its ten sizes are 0, 1, 211, 212, 213, 4096,
65535, 65536, 65537 and 131731. Fresh timestamped test targets prevent reuse of
old evidence. It verifies previous-version backups before explicit cleanup.

The controller tests wire CRC rejection, request conflicts, unknown sessions,
sequence gaps, path denial, invalid transfer, active-transfer busy/EXIT guards,
out-of-order writes, early FINISH, cancellation and content-CRC failure with
explicit orphan recovery. It deliberately discards one successful HTTP WRITE
response before durable client acknowledgement and replays the exact saved
request. This proves the host/P4 cache recovery path on real hardware; it does
not represent a physical UART loss. The separate headless peer drops a reply
before the P4 queue receives it, exercising actual eZ80 replay. Its
`--qualification-smoke` profile option runs the controller against actual
eZ80/EMOS/raw FAT using ten smaller files before a physical run.

After the ten-cycle test, `scripts/qualify_sd_keyboard.py` prepares a fresh
old target and streams a longer staged file while waiting for Escape. Publish
its readiness marker before the emulator cue. The Author then types `RUN . /`
at MOS: the already loaded service restarts with whole-card scope for subsequent
authorized development. Its host observer verifies a changed incarnation, exact
partial prefix, preserved old target, explicit orphan recovery and a new verified
upload. The host never sends keys or commands to hardware. Require the Author
to confirm that native USB Escape and typed RUN worked without a reset.

The observer bounds each human action to 180 seconds (configurable 10..600).
If Escape never arrives it cancels its own staged transfer and records partial
evidence. An unexplained transport error is preserved, not counted as a keyboard
pass. The headless keyboard smoke uses packets from the maintained USB mapper.

A service launched by a MOS EXEC/OBEY file runs while that batch file remains
open: MOS closes it only after the application returns. Do not replace that
active batch file. The requested Escape then direct CLI RUN closes the initial
autoexec and permits a later explicitly verified startup update. Preserve the
service filename exclusion and do not overwrite other files known to be held
open. The protocol is cooperative file access, not an OS-wide file-lock monitor.
