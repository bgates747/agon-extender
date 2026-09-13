# Host-controlled keyboard input

This accepted contract is implemented provisionally in REMOTE-002. Hardware
qualification and attended review are recorded separately in the task.

The PC sends bounded, numbered keyboard requests to the P4 over Ethernet. A
separate automation input source joins the existing processed-key path after
USB acquisition. The P4 console owner uses the retained stock-compatible
serializer and existing UART1 wiring. EMOS admits the Extender keyboard source
and owns the keyboard map, sysvars and normal application/CLI behavior.

The physical USB keyboard remains available. Automation starts only while it
is neutral; a physical press cancels remote input and takes precedence. Remote
held keys, cancellation and disconnect releases are source-specific. Requests
are paced, bounded and idempotent within their admitted session; stale sessions
and conflicting duplicates are rejected. Layout/admission loss invalidates the
session. The host reports the difference between request acceptance, UART
emission and separately observed eZ80 command/application completion.

## Host API and timing

`GET /keyboard/status` returns JSON. `POST /keyboard/rpc` accepts a binary
request with `X-Agon-Keyboard: 1`; browser Origin requests are rejected. These
are trusted local bench controls, like the SD endpoint, not an authenticated
Internet service. Network handlers never access the UART.

All integers are little endian. The 24-byte header is: magic `KY` (2), version
1 (1), operation (1), boot epoch (4), session (4), sequence (4), body length
(2), reserved zero (2), CRC32 (4). CRC32 uses the ordinary reflected polynomial
over header and body with the CRC field zeroed. Boot, session and sequence
must be nonzero. Operations: 1 opens a session at sequence 1; 2 submits events;
3 cancels; 4 renews the lease. Only operation 2 has a body: 1–96 pairs of USB
usage/down bytes. Down is 0 or 1. Unsupported usages, CapsLock automation,
unmatched transitions and more than six ordinary held keys reject the entire
batch. UK/US mappings and modifiers use the retained physical-key mapper.

One session owns automation. Subsequent requests advance sequence by one. An
exact retry of the latest accepted request returns its current progress without
re-enqueuing. Conflicting retries or stale epochs return 409; temporary admission
or pending-batch conditions return 503; malformed requests return 400. Layout or
transport admission loss advances the boot epoch even without a P4 reboot.

The console owner takes at most one event every 20 ms, behind physical input and
pending output. No catch-up burst or autonomous remote typematic occurs. A
session expires 5000 ms after its last new accepted request; retrying the same
request does not renew that lease. Cancellation discards unsent events and
releases only remotely held keys, ordinary keys before modifiers. Physical
press, USB disconnect, network-service loss and transport failure cancel it.

Status distinguishes cumulative `accepted`, `emitted` (handed to the console
owner for stock serialization), `discarded`, current `pending` and `held`.
`accepted = emitted + discarded + pending` modulo 32-bit counters. Generated
cleanup releases are reflected in held-state, not counted as submitted events.
These counters do not prove UART delivery or MOS execution. Reason values are
0 active, 1 explicit cancellation, 2 physical takeover, 3 timeout, 4 admission
boundary, 5 disconnect, 6 transport failure. Physical neutrality and layout are
also reported. Actual execution requires an eZ80 receipt or human observation.

## Host commands

Use the project Python environment and an ignored persistent journal:

```sh
.venv/bin/python scripts/keyboard.py --url http://EXTENDER --state agents/keys.json status
.venv/bin/python scripts/keyboard.py --url http://EXTENDER --state agents/keys.json type 'DIR /' --enter
.venv/bin/python scripts/keyboard.py --url http://EXTENDER --state agents/keys.json key left backspace enter
.venv/bin/python scripts/keyboard.py --url http://EXTENDER --state agents/keys.json hold left --seconds 1
```

Text is fully validated against the observed layout before any submission.
Printable ASCII, CR/LF, Tab and the UK pound symbol are supported; named editing,
arrow, function and modifier keys are available. A normal command opens and
cancels its own session. The Python API supports multiple batches and explicit
transitions within a session. Held tests renew the lease, up to 60 seconds.

The journal is locked and the exact request written before HTTP submission.
After an uncertain reply use `recover` with the same journal. It only replays
that request; remaining text is not automatically resumed. Use `cancel` to
release a known session. After reboot/admission loss, retain the old journal as
evidence and use a new journal only after inspecting neutral terminal state;
never rerun an uncertain command merely because the connection returned.

The maintained reset wrapper is `scripts/reset_agon.py --config LOCAL.json`.
Its ignored configuration supplies the SSH argv, gpiochip and GPIO number.
It uses the previously accepted 100 ms active-high transistor-base pulse and
restores input/pull-down through a shell exit trap. Successful GPIO actuation
is distinct from observing an actual mainboard boot.

After a Pi-controlled mainboard reset, the P4 may still report its old admitted
state until EMOS performs fresh keyboard setup. Record the old epoch and wait
for `ready` with a different epoch before automation; a fixed delay or old
`ready=true` is insufficient. The qualification helper accepts `--after-boot`
for this purpose. It never replays the cancelled pre-reset batch.

Both Escape in sdserve and its network EXIT return to its caller. If the caller
is autoexec or another MOS batch, the next command runs. Only a known final
batch command returning establishes EOF and closes that batch. Do not replace
startup while it is held open, or assume that Escape alone establishes a CLI.

The network handler enqueues input; it never writes UART or MOS memory. This
does not restore browser keyboard focus/leases, add a remote shell to the SD
wire API, or grant the P4 independent mainboard-control authority. The PC is
the initiating operator. Ordinary application commands execute through MOS.

Bench reset is independent: the Pi drives the existing transistor actuator to
pull the mainboard reset signal low. The Extender does not reset the mainboard.
The Author may authorize unattended fixture commands and resets; the live
review demonstration remains gated by the requested spoken alert and chat reply.


Lease comparisons use signed modular elapsed time so a console timestamp
sampled just before an HTTP renewal cannot underflow into a false expiry.
Pacing deadlines survive consecutive event batches within the session.

For unattended multi-command launches, upload and verify a finite MOS batch,
then type EXEC for that path. MOS itself orders LOAD completion before RUN.
A keyboard progress counter or a short host sleep cannot establish that a file
load has finished. Do not replace the helper batch while its final service is
running; exiting that final invocation closes it normally.

MOS command entry does not buffer arbitrary keystrokes while a command runs.
A stock-VDP screen readback captured `XEC` instead of `EXEC` when the qualifier
started the next command too soon after COPY. The file edit itself was correct.
The bounded fixture now allows two seconds for the prompt to return, and its
complete physical retest passes. This delay is a conservative fixture setting,
not a general completion acknowledgement for arbitrary commands. Keep dependent
commands inside the verified finite batch; establish prompt readiness separately
before typing its EXEC command. The optional text readback diagnostic is in
`examples/keyboard-screen`; it observes rendered characters, not MOS memory.
