# BENCH-024 — Verify mainboard VDP updates from SD before reboot

**Plan approved on November 20, 2026. Offline tranche complete.** Adapt
Jeroen Venema's Agon Flash so an operator
can update the Olimex mainboard VDP from SD without keypresses. The Pi5 runner
collects the flash verification result and wakes the operator chat while the
current VDP is still running. Qualify one update and return to production.
Keep the PlatformIO and standalone esptool USB paths available for recovery.

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

## Proposed operation

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

- BENCH-024-004 [ ] Qualify one Olimex round trip. Pin two receiver-enabled
  test builds for the outgoing and return legs and the exact production app0
  restore. An explicitly approved setup phase may provision the initial test
  receiver in app0 before the round trip starts. From the test receiver in
  app0, write the second build to app1. Save and check the app1 flash hash and
  prove that the mainboard boot identity, running build and configured slot
  are unchanged before activation. Activate app1 and prove its build and MOS.
  From app1, write the exact production image to app0 and capture the same
  pre-reboot proof. Activate production app0, prove its running build and MOS,
  then verify normal handback and check in. Bind both pre-reboot results and
  subsequent boot witnesses to the run identifiers. Stop on the first failure.
  Smith has requested a stop before this hardware phase.

- BENCH-024-005 [x] The offline packet pins the exact production USB restore
  and links both known USB procedures. If Agon Flash
  fails or the mainboard VDP cannot run it, retain the failure and select the
  appropriate recovery under the ordinary bench stop procedure. A fallback
  run is a separate recorded operation and leaves the original result intact.
  [Olimex bench procedure](../operations/olimex-bench/README.md)

- BENCH-024-006 [ ] Pin the production boot and handback witness before
  commissioning. Production predates the receiver's nonce, running-slot and
  ELF identity query. The return leg can already prove the exact production
  app0 bytes and configured selector before reboot. A fresh MOS prompt shows
  startup. It does not independently identify the running slot. During
  commissioning, select a production identity observation and decide whether
  a separate read-only USB witness is required for the full handback.

## Offline packet

Agon Flash source is on the fork's local `codex/bench-024-agent-flash`
branch at `f219b8b504e33d0570eee370d329a9535484a270`. The linked eZ80
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
to supervise the phases. The candidate packet permits offline preflight and
refuses physical dispatch. Hardware qualification remains pending.
