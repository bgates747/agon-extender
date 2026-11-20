# BENCH-024 — Verify mainboard VDP updates from SD before reboot

**Plan approved on November 20, 2026. Offline work authorized.** Adapt Jeroen Venema's Agon Flash so an operator
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

- BENCH-024-001 [ ] Freeze the two-part update and activation contract with
  VDPlet. Smith assigned the eZ80 utility to Extender. Pin the
  supported MOS-managed reply, receiver capability, boot-identity witnesses,
  timeout and failure outcomes, and exact prototype and production artifacts
  before selecting a physical run.

- BENCH-024-002 [ ] VDPlet implements the receiver and separate activation.
  Verify offline that a bad digest or invalid target leaves the boot selection
  untouched and that the terminal success result follows the target-side hash.

- BENCH-024-003 [ ] Implement the Agon Flash command and Pi5 phases. Verify
  offline that they require no keypresses, capture the flash result, reject
  stale or missing receipts, and wake the owner on success or failure. Check
  that the runner can complete a verified write phase with the activation
  phase still pending.

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

- BENCH-024-005 [ ] Preserve the exact production USB recovery packet and the
  known PlatformIO-bundled and standalone esptool procedures. If Agon Flash
  fails or the mainboard VDP cannot run it, retain the failure and select the
  appropriate recovery under the ordinary bench stop procedure. A fallback
  run is a separate recorded operation and leaves the original result intact.
  [Olimex bench procedure](../operations/olimex-bench/README.md)
