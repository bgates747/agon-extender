# R05-A05 development results

Application-owned transfers pass host, eZ80 and bounded physical tests. EMOS
v0.1.21 adds 207 ROM bytes; the checked file engine stays linked into the caller.
The hardware fixture received and sent 1027 bytes and preserved its 4096-byte
sentinel. A competing external request was rejected. This establishes the caller
boundary, not a usable automatic network service: P4 SD spooling is still A06,
and this helper currently requires Legacy mode.

The resident image initially measured 127699 bytes: +207 over the passing A04
image, leaving 3373 bytes below 128 KiB. File-engine code stays in the application.
Host tests exercise both directions, binary boundaries, descriptor fragmentation,
nested calls, busy/unsupported, malformed/stale replies, cancellation, overwrite
refusal and a lost activation acknowledgement. No uncertain mutation is retried.

The retained directory-backed emulator does not implement f_sync and incorrectly
maps CREATE_NEW to nonexclusive create. Its send-only caller result does not
qualify receive-side FAT durability. Hardware verification supplies the missing
paired mainboard-filesystem evidence; the physical test peer itself stores only RAM bytes.

## Identified candidates and deployment observation

Frozen sources: EMOS `7cd480e`, Extender `da0e47d3`. EMOS v0.1.21
is 127699 bytes, SHA256
`222918ac31f4e97dfdb59aab4479089681c36432d8b060a8f7f4281276d259da`.
The 27015-byte app-transfer-probe-r01 fixture has SHA256
`481e11056bfa5c45044a2883f9d94c20577db3ad26bbe0a1068efa19b4c57f7b`.
The exact final ROM/fixture also pass the retained eZ80 send-only harness
(1027 bytes, 1.347 seconds host wall time; not a performance benchmark).

After the physical flash automatically rebooted, Author observed “Invalid
executable” on the mainboard. The first manual-listener startup did not become
online. A subsequent directory listing found the listener, and executing it in
ExCom loaded its own banner and correctly rejected the unsupported route.
Returning explicitly to Legacy and invoking it again brought the service online.
The initial message's precise command/cause remains unproven; retain this as an
informative deployment anomaly, not a clean first-start pass. The ROM readback
and paired application result are separate checks.


## Physical results

| Check | Outcome | Scope |
|---|---|---|
| EMOS installation | PASS | Entire 131072-byte flash matches candidate plus erased padding |
| P4 diagnostic installation | PASS | r59 factory independently verified; build identity and USB startup observed |
| P4 → Agon | PASS | 1027-byte deterministic binary file, actual mainboard FAT, host readback exact |
| Agon → P4 | PASS | Same 1027 bytes verified by the controlled RAM peer |
| Caller preservation | PASS | 4096-byte sentinel and durable result; ordinary return to idle CLI |
| External request during application lease | PASS | HTTP 503 and peer rejection counter; no external dispatch |
| Immediate cancellation | PASS | Fixture observes CANCELLED before transfer |
| Follow-on manual listener | PASS | Starts after explicit fresh idle-CLI poll; host retrieves saved results |
| Startup and fixture cleanup | PASS | Original startup unchanged; fixture archived out of support path |

Two paired executions completed their data transfer. Only the second run has a
clean automated completion/collection sequence. The first collection was premature:
P4 FINISH/CLOSE establishes transfer completion, not that the application has
finished saving its result and returned to the prompt. The corrected harness waits
for a fresh resident idle POLL before typing another command. That run then starts
the listener successfully. Three additional listener stop/start cycles and a small
SAVE/start sequence also pass. This supports a harness timing explanation for the
post-application error; it does not retrospectively prove the cause of the earlier
post-flash message. No speculative loader patch or firmware retry was added.

The second observed run spans 4.387 seconds of host wall time from initial probe
sampling through return to CLI (90 samples). This includes invocation and polling,
not an isolated transfer-speed measurement. Deployment and evidence retrieval are
separate and substantially longer. The eZ80 fixture also prints MOS clock ticks;
that printed duration was not independently captured on the mainboard.

Retained local evidence is under `agents/remote005-application/`: exact images,
build manifests, final-send.json, hardware/flash-result.json, application-result.json,
application-observations.json, first-attempt observations, loader header capture,
restart-checks.json and cleanup.json. Generated artifacts are ignored, not current
production packages. On Agon, results are under `/agents/extender/results/a05-*`;
fixture is `/agents/extender/fixtures/a05-app.bin`; installed candidate and rollback
remain under `/extender/install/`. No unrelated files or startup settings changed.

## Final bench restoration

Normal P4 r57 factory was independently verified on restoration. The final
ExCom echo, return to Legacy, manual SD readback and neutral keyboard checks
are retained in hardware/final-result.json. EMOS v0.1.21 remains installed;
manual listener is stopped at the Legacy prompt. This is a development
qualification, not Author acceptance or production promotion.

## Remaining boundary

R05-A05 is complete for the frozen controlled-peer scope. Real P4 card snapshots,
spooling, reset recovery, directory operations, finite external utility and ExCom
transport integration remain in their existing downstream subtasks. Do not enable
application capability in normal P4 firmware based on this RAM-only test. The
production bundle remains unchanged. The new emulator-peer driver remains
uncommitted pending the separate human emulator-validation gate.
