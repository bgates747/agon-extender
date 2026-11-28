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
the Extender owner checks the standard and previous-standard recovery files
under `/extender/recovery/vdp`. The maintained tool checks existing file
metadata and uploads only missing files over P4-staged UART. Keep the joined
handback and both `*-provisioned.json` receipts. The operator or runner
verifies the SD contents using FLASH's on-card CRC at the confirmation prompt
during the restore. The recovery image never needs to be sent back over UART.

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
bench stop procedure on failure. This procedure prepares SD files and never
invokes FLASH.
