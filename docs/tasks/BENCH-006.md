# BENCH-006 — Non-disruptive ExCom text readback

## Executive summary

Implement GET /screen/text on P4 using retained VDP glyph recognition, serviced
by the VDU owner rather than concurrently touching its context from HTTP.
The existing browser video client stays connected. No Agon helper or SD service.
Legacy follow-up: investigate EMOS service or MOSlet to preserve the loaded
application; a CLI MOSlet alone does not inspect a concurrently running app.

- [x] S01 Implement asynchronous bounded character capture and host retrieval.
- [x] S02 Compile and qualify on P4; preserve installed codec/UI and rollback.
- [x] S03 Replace Alex read-screen.md with terse direct retrieval instructions.
- [ ] S04 Legacy readback preserving loaded program: design EMOS/MOSlet/resident
  integration and catalogue other useful agent helpers. Deferred, not this change.

Author authorizes implementation. P4 flash interrupts its network during reboot;
no competing WebSocket viewer will be opened. Retain ExCom for human observation.
Official contract: agon-docs/docs/vdp/System-Commands.md VDU 23,0,&83 recognises
pixels against current font/colour, not an independent text buffer. Retain upstream
edge/unknown limitations. Capture spans time; disclose non-atomic results and
reject context/mode changes during collection. No changes to upstream references.

Legacy research note: official MOS Executables.md assigns MOSlets to 0xB0000,
32 KiB; Modules.md notes applications can themselves occupy that space. Preserve
application memory/loading metadata explicitly, not merely by assuming all apps
avoid it. Candidate helper family: screen text, directory/file inspection,
execution receipts and telemetry. Running-app observation needs a resident/EMOS
service, distinct from a CLI MOSlet. These are follow-up ideas, not implemented.

Author clarification: ordinary MOSlets are run-and-return disposable helpers,
confined to MOSlet space. Preserve the loaded application, not the previous
MOSlet. Prefer that model for Legacy CLI helpers; EMOS/resident machinery is
only needed for observation while the application is actively running. Do not
turn retention of a prior MOSlet into a design requirement.

ExCom work complete; results in BENCH-006/RESULTS.md. S04 remains deferred.
