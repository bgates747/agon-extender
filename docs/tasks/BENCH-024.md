# BENCH-024 — Verify mainboard VDP updates from SD before reboot

**Closed on November 21, 2026. Retain as a fallback.** Smith
selected USB esptool as the default for Olimex mainboard VDPlet installation
and restore. The Agon Flash round trip passed two SD-to-flash writes, verified
both before reboot and returned the bench to production app0. Keep the exact
Agon Flash utility, receiver variants, phase runner and evidence for a
separately commissioned recovery. Production VDPlet predates the verified OTA
receiver and requires no changes for routine USB flashing.
[Olimex bench procedure](../operations/olimex-bench/README.md)

## Ownership and starting point

| Owner | Deliverable |
| --- | --- |
| VDPlet | Mainboard ESP32 receiver changes for writing and verifying the inactive slot, reporting the result, and selecting a verified slot on a separate request. |
| Extender | Pi5 runner, durable logs and receipts, owner-chat wake-up, and the commissioned restart and handback sequence. |
| Extender | Adapt the eZ80 Agon Flash utility in the existing fork and agree the request and reply format with VDPlet. |

The stock utility reads the image from SD and sends it via MOS VDU output
over the onboard UART to the running mainboard VDP. Its `-f` option already
skips confirmation and suppresses the input-file CRC display. The stock VDP
receiver writes the alternate app slot, changes the boot selection and
restarts. The new behavior therefore requires changes at both ends. Prior
Olimex work demonstrated the ordinary SD update and boot from the alternate
slot. The pending USB programmer incident remains under BENCH-023.
[Agon Flash v1.9](https://github.com/AgonPlatform/agon-flash/releases/tag/v1.9) · [Stock updater source](https://github.com/AgonPlatform/agon-vdp/blob/c7ac293d2aa81ddfa693390549bcd909069c8fc3/video/updater.h) · [Olimex SD update evidence](../../../agon-fsim/docs/tasks/PINGO-083/STOCK-OLIMEX-06.md) · [USB programmer investigation](BENCH-023.md)

VDPlet built two private qualification variants, A and B, from the sealed
v0.1.3-alpha source. They add opt-in commands to write and verify the inactive
app slot, report the result, and select the verified slot separately. The
ordinary updater commands remain available. The selected production image is
the original v0.1.3-alpha release. Both variants passed offline checks and
the physical round trip used both with the production EMOS and SD listener.
[VDPlet offline results](../../../agon-vdplet/docs/tasks/VDPL-060/RESULTS.md)

## Qualified fallback operation

1. The Pi5 runner stages the pinned image on the Agon SD card using the
   commissioned PARLIO route. It invokes the explicit Agon Flash command at
   Legacy MOS with a run identifier, expected image length and SHA-256. The
   eZ80 utility logs progress and terminal errors without waiting for a key.
2. The mainboard VDP validates the target slot and image extent, completes the
   write to the inactive app slot, then reads and hashes the exact image bytes
   from flash. It returns a structured result with the run identifier, target
   slot, byte count, written-image SHA-256 and verdict. The current VDP keeps
   running and the configured boot slot stays put. The eZ80 utility obtains
   the result through a bounded MOS-managed reply, closes its result file on
   SD and returns to the CLI.
3. The Pi5 runner collects the result through the commissioned bench route
   and compares it with its pinned input. It saves the write result and the
   evidence of the current boot before its service exits and wakes the owning
   chat. The Pi5 owns the notification. The P4 supplies the existing bench
   transport. [Bench completion procedure](../procedures/bench-completion.md)
4. The operator invokes a separate activation phase for the verified image.
   The mainboard VDP selects that slot, the Pi5 runner requests the normal
   restart, and the Pi5 records the new running slot and build plus a fresh
   working MOS prompt. A failed or missing result stops the sequence before
   activation and follows the bench procedure's alert and custody rules.

Keep the bootloader, partition table, application store, normal startup and
unrelated files intact. Verification covers the VDP application write. The
ordinary checksum-free PARLIO policy still governs staging and result retrieval.

## Work and qualification

- BENCH-024-001 [x] Freeze the two-part update and activation contract with
  VDPlet. The approved plan checkpoint is
  `41bcbc37eeb5b8d93300a5db595764eb3d2a358f`. Wire v1 uses the committed
  onboard EMOS route and the ten-byte callback record. The offline packet
  pins both receivers, the production app, bootstrap and restore data.
  [Receiver protocol](../../../agon-vdplet/docs/tasks/VDPL-060/PROTOCOL.md)

- BENCH-024-002 [x] VDPlet built both receiver variants and passed the
  dispatcher and transaction-model tests. A successful target-side readback
  hash allows selection. Bad digests and invalid targets leave the selector
  untouched. [VDPlet offline results](../../../agon-vdplet/docs/tasks/VDPL-060/RESULTS.md)

- BENCH-024-003 [x] Cross-linked the Agon Flash utility with noninteractive
  stage, select and status commands. Five sender model cases passed.
  The Pi5 runner stages the inputs, collects SD logs and result snapshots,
  gates each selection on the verified write, and checks the candidate reboot.
  Ten host tests passed, including prompt/transfer ordering with printer
  mirroring off and refusals for incorrect, stale and missing receipt fields.
  A host-only Pi service verified wake-up requests on success and failure.

- BENCH-024-004 [x] Qualify one Olimex round trip. Pin two receiver-enabled
  test builds for the outgoing and return legs and the exact production app0
  restore. An explicitly approved setup phase may provision the initial test
  receiver in app0 before the round trip starts. From the test receiver in
  app0, write the second build to app1. Save and check the app1 flash hash and
  prove that the mainboard boot identity, running build and configured slot
  are unchanged before activation. Activate app1 and prove its build and MOS.
  From app1, write the exact production image to app0 and capture the same
  pre-reboot proof. Activate production app0, prove its running build and MOS,
  then verify bench readiness. Bind both pre-reboot results and
  subsequent boot witnesses to the run identifiers. Stop on the first failure.
  Smith approved one hardware round trip with the two pinned builds. Keep
  Extender's existing reservation active through the flash investigation,
  including after a successful restore.

- BENCH-024-005 [x] The offline packet pins the exact production USB restore
  and links both known USB procedures. If Agon Flash
  fails or the mainboard VDP cannot run it, retain the failure and select the
  appropriate recovery under the ordinary bench stop procedure. A fallback
  run is a separate recorded operation and leaves the original result intact.
  [Olimex bench procedure](../operations/olimex-bench/README.md)

- BENCH-024-006 [x] Review and pin the production boot witness below
  before commissioning. The proposed round trip uses the stock production
  image and requires a positive post-reboot observation of which build ran.

## Production boot proof for the first round trip

Use the known contents of both app slots and the VDP's own startup banner.
The pinned partition table has exactly two application partitions, app0 at
`0x10000` and app1 at `0x150000`. The retained Olimex bootloader binary lacks
the partition-load log string. Production v0.1.3-alpha predates the new
running-slot query. The distinguishable display banners are printed by the
running app at startup. [Production boot screen source](https://github.com/bgates747/agon-vdplet/blob/v0.1.3-alpha/tools/build_firmware.py) · [Receiver build evidence](../../../agon-vdplet/docs/tasks/VDPL-060/RESULTS.md)

1. Before returning to production, the Pi saves the live app1 snapshot from
   receiver B. It requires B's pinned ELF identity and running slot 1. The
   return write targets app0. The Pi matches the full production image hash
   reported by the mainboard's flash readback, then saves the separate
   activation receipt. That receipt must show B still running from app1 and
   app0 configured for the next boot. App1 keeps B through this leg.
2. The Pi performs one normal paired restart. For the first qualification,
   Smith observes the mainboard monitor during that restart and records the
   full fresh `VDPlet Version` line in chat or a photo. Exact production prints
   `VDPlet Version 0.1.3-alpha`. Receiver B prints
   `VDPlet Version 0.1.3-alpha BENCH-024-B`. Compare the whole line. The
   B banner identifies a fallback to app1 even if MOS starts successfully.
3. The Pi requires fresh MOS admission and working CLI after the same reset.
   The exact production banner, the two known slot contents and the saved
   pre-reboot receipts identify app0 by elimination. Retain all three with
   the handback. If the banner is missing, ambiguous or from B, stop with
   custody retained and report the observed state. USB programming remains a
   separate recovery option.

**Optional follow-up if needed.** VDPlet could add a read-only boot-status
reply to a future production release so the Pi can query the actual running
partition and build over the normal MOS path. This is deferred. The proposed
round trip uses the existing production image and the banner witness above.

## Offline packet

Agon Flash source is retained at
[`f219b8b504e33d0570eee370d329a9535484a270`](https://github.com/bgates747/agon-flash/tree/f219b8b504e33d0570eee370d329a9535484a270)
on the fork's `codex/bench-024-agent-flash` branch. The linked eZ80
utility is 23,324 bytes with SHA-256
`07ad0634bedcfb14a03ba38387d963b4bdc67fe114fa041e4c87eb47def6c831`.
The ignored `agents/bench-024/offline-packet/` holds the binary, link map,
manifest and the preflight and wake-up receipts.

The [Pi phase runner](BENCH-024/ota_runner.py) keeps write and selection
separate. The write phase exits after collecting the flash digest and proving
the existing VDP boot and selector. The runner turns printer mirroring off
before Agon Flash runs and retrieves the utility's SD progress log and binary
receipt through PARLIO after MOS starts the foreground listener. Use the
maintained [Pi service and chat wake-up](../procedures/bench-completion.md)
to supervise the phases. The offline packet remains sealed and refuses
physical dispatch. The first physical packet pinned the swapped USB setup.
It starts from the joined BENCH-023 short-read failure, with one
app0 bootstrap write and independent readback using the commissioned
mainboard programmer. The verified OTA legs follow under Pi service
supervision. Pause after proving the return write so Smith can watch the
restart to production.

## First physical attempt

The Pi service stopped during bootstrap when the USB reset adapter identity
reported by udev differed from the pinned configuration. The check failed
before the helper opened the port. There was no reset, programmer session,
flash write or SD transfer. Neither OTA leg ran. The bootstrap worker joined
with exit 1, the Oryx player completed, and Extender retained the reservation.
The prior BENCH-023 short-read entry is still pending in the inventory.
Evidence is in `agents/bench-024/bench024-ota-20261121t002006z/`.

Smith confirmed he had restored the original USB cabling and authorized one
retry. The mainboard adapter's stable serial endpoint, vendor and model and
the P4's serial matched. Only the mainboard adapter's USB topology path had
changed. The retry pins that path in a separate job-local configuration and
keeps the same firmware, runner and first-failure stop. Evidence is in
`agents/bench-024/bench024-ota-20261121t002425z/`.

The retry installed receiver A in app0. The full 1,138,688-byte USB
readback matched and MOS returned to a working prompt. Six PARLIO uploads
completed, including both firmware binaries. The seventh upload, the
177-byte `write-production.txt` command file, was still pending when the
client timed out after 300 seconds. Staging had not reached listener EXIT.
The stage worker joined, and the Oryx player completed. Neither Agon Flash
write ran. Receiver A remains the last verified mainboard image. Extender
retains the reservation and leaves the in-flight transfer state for
diagnosis.

## Diagnose the 177-byte PARLIO upload separately

The original run evidence follows. PORT-008 owns the open transport
investigation and the [next-failure capture checklist](PORT-008/PARLIO-UPLOAD-STALL.md).

The pre-reset snapshot from the subsequent USB flash series preserves the
same P4 job and listener boot identities. The P4 reported terminal
transport error 2 about 612 seconds into its worker. It accepted HELLO
and BEGIN and recorded no confirmed payload or parallel completion
counters. In the production P4 source, that record count and error
localize the failure to the PARALLEL_WRITE request or its return. The
610-second request deadline explains why the Pi first reported a pending
job at its 300-second timeout. The retained data cannot establish whether
the physical payload phase ran or whether its UART reply was lost.

- BENCH-024-007 [x] Run two upload-only controls with the existing parallel
  staging command and separate fresh SD directories. Compare the exact
  177-byte input alone with the original seven payloads in order. Use the
  installed production VDPlet, P4, EMOS and listener. Preserve the original
  transaction. Collect completion records, stop on a fresh failure and
  retain the reservation. This does not invoke Agon Flash or modify firmware.

Both controls passed. The 177-byte file completed alone and at position
seven after the original six inputs. All eight uploads reported PARLIO with
the exact byte clock count and two VALID edges. The P4 worker completed
the two 177-byte uploads in 0.957 s and 1.058 s respectively. Both listeners
exited and both workers joined. The controls used production VDPlet and
fresh SD paths after the bench restart, so they establish that neither the
file nor its position always causes the failure. The original failure's
cause remains open. Evidence is in
`agents/bench-024/parlio-control-20261121t012352z/`.

### Repeat the seven-file transfer sequence

- BENCH-024-008 [x] Repeat all seven pinned uploads in the original order
  on production VDPlet, P4, EMOS and the foreground listener. Give each
  attempt a fresh SD directory. Count each complete sequence once and stop
  at ten successes or ten failures. Do not run the staged commands or
  change firmware.
- BENCH-024-009 [x] After each failure, save the P4 staged-job state,
  EMOS listener and keyboard status as reported by the P4, and any
  available cached EMOS telemetry before reset or cleanup. Retain the
  failed attempt and its transaction files. If a failed attempt leaves
  the bench busy, use the normal paired reset before a fresh attempt.
  If the reset fails to recover a working bench, stop with the tally
  and evidence. Keep Extender's reservation.

The series stopped at ten successful sequences and zero failures. All 70
uploads had PARLIO completion receipts with exact byte clock counts and
two VALID edges. All ten listeners exited and workers joined. The 177-byte
file completed ten times at position seven. No failure recovery or reset
ran. The original fault did not reproduce on production VDPlet with fresh
SD paths and a fresh listener per sequence. Production firmware remains
selected and installed, and Extender still holds the slot. Evidence is in
`agents/bench-024/parlio-series-20261121t012930z/`.

### Resume the Agon Flash round trip

- BENCH-024-010 [x] Reinstall exact receiver A from the verified production
  app0 baseline. Use the standalone esptool 5.1.0 method that passed the
  ten-flash series and production restore. Verify the full USB write extent
  and working MOS. Use a fresh SD namespace and distinct OTA transaction
  IDs for the same pinned A, B, utility and production images.
- BENCH-024-011 [x] Run A to B and verify the production return write while
  B is still running. At the first failure, save the P4 staged-job state,
  EMOS listener and keyboard state and available cached telemetry before any
  recovery reset. Preserve the original phase evidence and retain custody.
  On success, pause before selecting production and invite Smith to watch
  for the full production startup banner during the normal paired reboot.

Receiver A's USB bootstrap passed the full 1,138,688-byte readback and
MOS check. All eight PARLIO inputs staged. From app0, A wrote and verified
all 1,123,040 bytes of B in app1, then B booted with a fresh nonce and the
pinned build identity. From app1, B wrote and verified all 1,117,040 bytes
of production v0.1.3-alpha in app0. Both writes preserved the running boot
and the boot selection until separate activation. All six workers joined.
The runner paused with B running and app1 still selected while waiting for
Smith to watch the production boot.
Evidence is in `agents/bench-024/bench024-roundtrip-20261121t014021z/`.

The return to production passed. While B was still running from app1,
the Pi verified the production app0 digest and the separate app0 selection
receipt, then restarted the bench once. Smith saw the fresh
`VDPlet Version 0.1.3-alpha` banner on the mainboard monitor. The Pi tied
that observation to the new MOS boot, confirmed the same boot at a working
prompt, and verified the listener offline, transfers idle and serial
handles free. All nine workers joined. The installed inventory now records
production with no pending operation. Smith then directed release. The
scheduler accepted check-in and cleared the slot, with no operators waiting
at that time. The receipt is `checkin-delivery.json` in the round-trip
evidence directory. The earlier PARLIO stall remains unexplained.
