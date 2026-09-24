# BENCH-006 — Non-disruptive ExCom text readback

## Executive summary

ExCom text readback is implemented and has bounded physical evidence.
[Current operation and limits](../screen-text.md) are maintained outside this
completed implementation record; [results](BENCH-006/RESULTS.md) retain the test.
P4's VDU owner samples glyphs from pixels without taking browser video ownership.
No Agon helper or SD service is involved. Only S04, Legacy readback preserving
the loaded program, remains deferred; this task is not a new flash request.

- [x] S01 Implement asynchronous bounded character capture and host retrieval.
- [x] S02 Compile and qualify on P4; preserve installed codec/UI and rollback.
- [x] S03 Replace Alex read-screen.md with terse direct retrieval instructions.
- [ ] S04 Legacy readback preserving loaded program: design EMOS/MOSlet/resident
  integration and catalogue other useful agent helpers. Deferred, not this change.

The original implementation authorization permitted a P4 flash, interrupting its
network during reboot;
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

ExCom work is complete; S04 remains deferred.
