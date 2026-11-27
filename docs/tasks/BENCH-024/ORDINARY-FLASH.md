# Ordinary FLASH v1.9 in the standard Olimex runner

VDPL-059 needs the standard bench runner to stage the original Earth pair,
install the repair candidate with stock Agon Flash, run both named arms,
and restore production with the same utility. The commissioned runner's
mainboard phases currently write via USB and assume app0. This proposed
extension uses FLASH as the sole writer and verifies each selected image
independently before proceeding. Extender owns the reusable runner.
VDPlet owns the job packet, reservation, physical run and scheduler check-in.

Smith directed VDPlet to work with Extender on a FLASH-compatible plan with
standard runners, then to book and run the original Nurples pair when ready
(VDPlet chat message `01a21edd-10dc-7d33-9d81-e52a1930bd81`). This records the
plan for review. The [commissioned bench guide](../../operations/olimex-bench/README.md)
currently requires FLASH for mainboard firmware changes.

## Proposed manifest

Keep named schema-3 fixture fields and phase names. For the initial backend,
use a mainboard-only firmware change. In `firmware.mainboard`, set:

| Field | Meaning |
| --- | --- |
| `method` | `agon-flash`, selecting installed ordinary Agon Flash v1.9. |
| `candidate_app`, `restore_app` | Raw application file pins with `path`, `bytes` and `sha256`. |
| `partition_table` | Pinned local partition table with `path`, `bytes` and `sha256`. Compare its FF-padded 4 KiB against the actual flash table during each read. |
| `candidate_slot`, `restore_slot` | Explicit alternate slots, each 0 or 1 and distinct. Initial production slot must equal `restore_slot`. VDPL-059 proposes candidate slot 0 and restore slot 1. |

Existing mainboard USB manifests keep their current schema and behavior when
admitted by the applicable guide. The FLASH variant uses raw apps and has no
`candidate_write` or `restore_write` extent fields. A job cannot fall back to
the USB writer if FLASH or verification fails. Use the ordinary bench config
and commissioned interpreter, device identities, lock, reset binding and
inventory. There is no new device or network configuration.

For offline preflight, verify artifact bytes and digests, the two OTA slots
and address bounds in the pinned partition table, distinct slots, safe staged
filenames, the original schema-3 fixture manifests and the capable local
reader. Preflight does not query targets. On the VDPL-059 inputs it must print:

```text
stage
install-mainboard
run-control
run-aligned
restore-mainboard
handback
```

## Phase behavior to qualify

1. **Stage.** Require an established, current production entry receipt for the
   declared restore slot. Compare its application hash and slot, current
   inventory, checkout handoff and joined status. A stale, ambiguous or
   contradictory entry blocks install. If checkout cannot establish the
   actual entry state, identify it as a separate bounded preparation step
   before allowing a write. The Pi stages the fixtures and both pinned raw
   apps through the usual schema-3 path. Stage the apps in the job's
   `/extender/install/<namespace>/` directory. Capture the transfer receipts
   and keep the ordinary checksum-free PARLIO policy.
2. **Install and restore.** Under the existing operation lock, the Pi checks
   the expected entry identity, the startup and listener pins and installed
   `/mos/flash.bin` v1.9 (15,624 bytes, SHA-256
   `480b476703b798cf8d93294cac42d77cad93f7747003b061520b86685c75eb57`).
   Use the existing passive CLI observer for the lowercase
   `flash vdp /extender/install/<namespace>/<app>.bin` command. Require the
   v1.9 identity and confirmation prompt, journal pending operation and
   intent before one `y`, then require `checksum ok!` and the reboot
   notice. Witness fresh, command-responsive MOS. Use the qualified paired
   reset sequence after the VDP-only reboot where required by that path.
3. **Independent proof.** After each FLASH write, the Pi performs one bounded,
   read-only 115,200-baud USB ROM/stub session on the pinned mainboard MAC.
   Save the flash table at `0x8000`, the 8 KiB OTA selector at `0xe000` and
   the selected application's exact raw byte count. Reject an ambiguous or
   wrong slot before accepting the application. Compare the raw application
   bytes with their local pin. Preserve all evidence. Close the programmer,
   use the commissioned Agon reset and require a fresh boot and real MOS
   response. Record slot, address, raw length and SHA-256, write and read
   evidence, and post-read UI admission in `independent-verification.json`.
   Verify unchanged P4 and EMOS identities. Reconcile the inventory under the
   lock before clearing the pending operation.
4. **Run and handback.** The original `run-control` and `run-aligned` each
   require the verified install receipt and the normal command-correlated
   completion line and MOS prompt. Use the original result validators.
   The joined restore receipt must establish the production digest on its
   declared slot. Follow normal CLI, idle services, free ports and process
   join checks before check-in. For app1, explicitly record the confirmed
   boot slot in inventory and handback. Keep app0-only jobs aware of the
   slot difference. Stop on the first unexpected failure and keep custody
   and the original records.

The source precedents are the November 26 ordinary FLASH recovery's
`check_flash`, `run_ota`, `selected_slot` and `verify_board` helpers and
the November 27 VDPL-059 app1 recovery receipt. Port the reusable behavior
into maintained source. Preserve the shared checkout while qualifying the
candidate in an isolated Extender worktree.

## Approval and offline checks

Section 2 of the current guide makes install, verification, restore and
check-in part of an authorized and scoped bench job. The temporary rule
expressly limits the firmware writer. The two read-only USB sessions and
their resets must be explicit in this new packet. The one-shot approval for
the previous recovery was consumed. The guide identifies no separate
approval per read once this exact commissioned cycle is covered by the
run instruction. Existing tool reviews and any narrower direction from
Smith still apply. The earlier approval for an app1 check-in belonged to
that recovery. Include the app1 return explicitly in this packet.

- BENCH-024-012 [x] Check the original Earth input pins and produce the
  standard-runner plan. All 16 local file pins in the owner input bundle
  checked, including both raw images, the partition table, and both arms.

- BENCH-024-013 [ ] Review and freeze the plan, then implement the minimum
  reusable backend in an isolated Extender worktree. Exercise the ordinary
  CLI and recorded receipt chain. Prove wrong entry or post-write slot and
  image refusals, missing prompt or reboot witnesses, read failure requiring
  a stop, and the absence of any USB write call. Run existing named-run,
  USB, recovery and handback regressions offline. Return the candidate
  revision, preflight output and commissioning path.

- BENCH-024-014 [ ] Commission and qualify the exact reviewed packet as a
  distinct live run. VDPlet owns that reservation and all target access.
  Promote the shared runner only under the applicable review and deployment
  authorization.
