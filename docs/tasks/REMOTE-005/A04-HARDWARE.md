# A04 physical admission check

Author released the idle bench and requested deployment/testing on 2026-09-27.
This authorizes hardware review in place of the pending graphical emulator gate
and the candidate freeze needed for deployment. It does not accept production
promotion or authorize implementing the full file service.

H01 [x] Preserve actual P4 image; restore known normal Extender service to regain
keyboard control. Preserve actual EMOS ROM, SD startup and any colliding files.
H02 [x] Freeze/build EMOS v0.1.20 and optional r58 admission peer under existing
version preapproval. Normal r58 builds omit the diagnostic; identified peer builds
require explicit --admission-probe, recorded in their manifest. Verify full EMOS
ROM after flash and keep tested v0.1.19 rollback available.
H03 [x] On hardware with normal P4, prove prompt/input and manual SD operation;
new discovery must not disrupt the old peer. Preserve startup; no root clutter.
H04 [x] Install temporary P4 peer. It responds only to EMOS-initiated controls in
Legacy, never does filesystem work. HTTP may arm one synthetic offer only after
a fresh idle poll; armed intents expire in one second. Check corrupt offer,
missing utility, valid finite probe, key-before-ack cancellation. The race probe
injects one virtual-code-zero key-down; host Escape/key-up ends that test.
H05 [x] Verify 4096-byte application sentinel, ordinary public application editor,
return to prompt and unchanged manual listener. Capture independent evidence;
input delivery counters alone are not command completion proof.
H06 [x] Remove temporary probe/startup changes and restore normal P4 firmware.
Leave responsive keyboard and normal CLI. Record firmware identities, exact
rollback locations privately, retained results and any untested boundary.

No ExCom automatic-transfer claim: paired active parser is not implemented.
No file mutations under new admission: finite utility only exercises the
loader/editor/memory boundary. Existing manual listener handles deployment.
All host output, reset/flash actions and SD paths follow maintained guides.

## Deployment checkpoint — 2026-09-27

P4 restoration completed: actual incoming 16 MiB flash was preserved, then normal
`uart-excom-console-r57-b2026-09-26-22-46-38Z` was written and independently
verified. USB host startup and port-80 keyboard/status service respond.
Private rollback and deployment receipts are recorded in `HARDWARE.local.md`.

Prepared candidates:

| Component | Build/check result |
|---|---|
| EMOS | `agon-emos-v0.1.20-b2026-09-27-20-44-23Z`; SHA-256 `0549e3e103480ab39d83c91a04d7b75de8d709843ca71857446f77c1b26678cf`; ABI and VDU checks pass |
| P4 diagnostic | `uart-excom-console-r58-b2026-09-27-20-44-48Z`; explicit admission-probe build passes; source `2e2014f7` |
| EMOS host regression tests | 112 pass against prepared candidate source |
| Finite probe | Target compile/link pass; not yet deployed |

An ordinary Agon reset did not establish Extender keyboard readiness; the manual
SD service also remains offline. The Author was asked for the mainboard screen
state and SD-card presence. Neither candidate has been flashed onto its target;
Agon ROM/startup have not been altered. H01 is partial, and H02–H06 remain open.
Do not interpret P4 flash verification as an EMOS admission hardware pass.

The version-record validator also reports a pre-existing frozen
`light2-harness-r02` connectivity hash mismatch. No frozen hash was rewritten;
component build checks above do not resolve that separate discrepancy.

### Live continuation and first physical defect

Author subsequently observed Extender input enabled. P4 then reported ready;
manual EMOSlet startup and SD reads succeeded. Preserved actual v0.1.19 ROM and
startup, deployed the first v0.1.20 candidate, and verified all 131072 ROM bytes
against the padded candidate. Existing manual SD operation remained available.

The identified r58 diagnostic peer was independently flashed/verified. Missing
utility produced CLOSE 7 as intended, but subsequent idle polling revealed a
resident cleanup defect: `emos_admission_reset()` cleared the job ID/grant but
left `job_class` populated. A NO_WORK reply therefore caused repeated fresh
negotiation, and a later race offer was lost during that churn. This is a failed
initial run, not an admission pass. EMOS commit `01d07a9` clears the class; the
regression test now follows a completed dispatch with repeated empty polling.
112 host tests pass after correction. Corrected candidate:
`agon-emos-v0.1.20-b2026-09-27-21-03-57Z`, 127492 bytes,
SHA-256 `4e70bb1ddc54bb47dc7b5cf347361b36d3ef85cabcdafbec6ec257faea8ab742`.


## Final bounded physical result — 2026-09-27

All H01–H06 checks passed with the corrected EMOS build above. The first image
and failure remain evidence; they are not the passing candidate.

| Physical check | Outcome |
|---|---|
| Corrected installed EMOS | Full 128 KiB ROM matches candidate plus erased padding |
| Missing utility | CLOSE 7; subsequent idle polling stays stable |
| Corrupt offer | No provisional grant or utility dispatch |
| Key before acknowledgement | CLOSE 9; input wins and Escape clears the partial line |
| Finite utility | 4096 sentinel bytes preserved; nested dispatch rejected; ordinary public editor accepts `proof` |
| Application/manual editor isolation | No idle admission polling while either foreground utility owns execution |
| Durable result | `A04 memory nested-editor PASS` saved and independently downloaded |
| Cleanup | Probe archived under `/agents/extender/fixtures`; `/emos/sdjob.bin` removed; startup byte-identical |
| Normal P4 restored | r57 independently written/verified; temporary diagnostic endpoint removed with that image |
| Routing/input regression | ExCom echo output sampled; return to Legacy and manual SD read pass; listener exited; keyboard ready and neutral |

Final bench: corrected EMOS v0.1.20, normal P4 r57, Legacy MOS prompt.
No production promotion or automatic file-transfer capability is claimed.
[Machine-readable results](A04-RESULTS/hardware.json) retain the bounded receipts.
Private raw transcripts, images, rollback paths and host journals are in the
machine-local bench record. A host test helper initially tried to encode Escape
as text; corrected to the existing explicit Escape key API, then repeated the
race check successfully. That helper mistake did not change firmware.
