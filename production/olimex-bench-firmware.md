# Olimex bench production firmware maintenance

Extender owns EMOS and the Extender VDP on the P4. VDPlet owns the mainboard
VDP. The owners supply the exact restore images and coordinate changes so that
ordinary operators can rely on the bench's production baseline at checkout.
The [operator procedure](../docs/operations/olimex-bench/README.md) lists the current artifacts.

1. Confirm the production build for each affected processor with its owner.
   The owner retains the binary at a durable location with its exact SHA-256,
   source revision, and write scope. Check that operators can fetch it using
   the same access they have for bench work.
2. Between test slots, establish the intended baseline under exclusive
   custody. Install the affected production images, verify the writes and
   startup, and record the resulting baseline.
3. Publish the current direct binary links and hashes in the bench procedure
   before the next ordinary slot opens.

The [current release](current.yaml) selects the qualified Olimex bundle and
the current mainboard companion. The [bundle manifest](bundles/olimex-parlio-v0.3.0/bundle.yaml)
records the original qualification and immutable artifacts. The
[mainboard companion manifest](companions/olimex-mainboard-vdplet-v0.1.4-alpha.yaml)
records the mainboard application update, its physical smoke and the
retained v0.1.3-alpha rollback.

Keep an executing job's frozen pins. Before dispatching a prepared exception
job after a mainboard standard change, verify the current OTA slot at checkout, rebind the raw FLASH restore app
and slot to the new standard, and rerun preflight. Retained padded files
serve legacy records and expressly authorized recovery procedures. A deliberate
old-firmware comparison keeps its selected test image.

## Provision the SD recovery copies

Before handing back a new production selection or a replacement SD card,
the Extender owner ensures the standard and previous-standard raw images are
available under `/extender/recovery/vdp`. Upload each newly deployed image
and read it back once over P4-staged UART for a byte-for-byte comparison with
the pinned release on the Pi. Retain the joined handback and the image's
`*-verified.json` receipt. Publish the SD path, byte count, release SHA-256,
verification date and method, evidence run, and receipt SHA-256 in
[current SD firmware receipts](olimex-sd-firmware.json) before using the copy
as the standard or rollback.

Reuse existing receipts when the card and files are unchanged. A version
moved from standard to rollback keeps its original receipt. Subsequent checks
use file metadata and, during FLASH itself, the utility's on-card CRC. Repeat
a full SD readback only for a documented reason such as a replaced card,
lost file, or evidence of corruption. Reconcile the affected receipt first.
For interrupted initial deployment, recover an existing verification receipt
if available. If the upload finished and the file is still unrecorded, document
that reason and use `--verify-existing SD_PATH` to complete that file's
initial verification.

For ordinary VDP FLASH, a retained SD receipt establishes the identity of the
resident file and FLASH's CRC checks its contents before confirmation. After
the write, the USB programmer reads small layout and selector records and the
ESP32 returns a digest of the written range. This establishes the installed
image separately from the SD file proof. The [bench procedure](../docs/operations/olimex-bench/README.md)
describes how to record the digest, selected slot and subsequent MOS witness.

## Reuse resident SD tools

The same current-card record holds the commissioned identities for
`/emos/sdserve.bin` and `/mos/flash.bin`. Routine jobs preserve both files.
The runner checks their type and size and records the earlier verification
it relied on. After card replacement, file changes, or evidence of corruption,
verify the affected tool against the pinned artifact once and publish its new
receipt before using it again.

Use the commissioned checkout, local bench config and its SHA-256, operator
chat ID, live scheduler-state path and a fresh output directory. Run the same
command first with `preflight` and then with `provision` under the granted slot
and normal joined process procedure.

```bash
.venv/bin/python scripts/olimex_vdp_cache.py \
  --config BENCH.local.json --config-sha256 CONFIG_SHA256 \
  --lease-state SCHEDULER_STATE --operator OPERATOR_CHAT_ID \
  --out EVIDENCE_DIR preflight
```

During `provision`, the tool verifies MOS on entry and handback and checks
that the transfer listener is stopped and ports are free. Apply the normal
bench stop procedure on failure. Provisioning prepares SD files. FLASH runs
only during an authorized installation or restore.
