# AUDIT-008 — Physical deployment, 2026-09-24 UTC

EMOS v0.1.19 is installed and its complete 128 KiB ROM matches the selected
candidate plus erased padding. The `/emos` dispatcher passes physical listener
loading, argument/case handling, transfer, return/reentry and a 4096-byte
application-memory sentinel. ExCom/Legacy and host-injected keyboard operation
pass. This is bounded hardware evidence, not full native-keyboard/gameplay
acceptance or a new firmware release.

| Item | Result |
|---|---|
| Build | `agon-emos-v0.1.19-b2026-09-24-02-02-56Z`, ordinary profile |
| Prior ROM | v0.1.18, retained completely on host and SD |
| Candidate | 124774 bytes, 6298 ROM bytes free; 6282 recovered |
| ROM check | All 131072 bytes exact, including erased tail |
| Reboot | FLASH utility automatic reboot; ready with new keyboard boot generation |
| ExCom | CLI echo observed through P4 screen-text capture |
| Legacy | Returned, then SD listener available through EMOS utility dispatch |
| Dispatcher | `EmOs SdSeRvE / --fast`, normal and fast reentry pass |
| Transfer | 1024-byte binary upload/readback in each mode pass |
| Application RAM | 4096-byte sentinel at 0x40000 retained byte-for-byte |
| Listener location | `/emos/sdserve.bin`; moved from `/mos/sdserve.bin` |
| Startup | Unchanged; keyboard selection only, no automatic listener |
| Other firmware | P4 and mainboard VDP unchanged |

The prior ROM is `/agents/extender/backups/firmware/em-pre-v019.bin` on SD.
The verified candidate is `/extender/install/em-v019.bin`; ROM readback evidence
is `/agents/extender/results/em-v019-rom.bin`. Fast-listener prior-version backup
and the original ordinary `/extender/sdserve.bin` remain available. No unrelated
user files changed. Final state is Legacy, `EMOS sdserve --fast /` online;
ordinary checked invocation is `EMOS sdserve /`.

The polling watcher missed the short not-ready interval but recorded the changed
boot generation and ready endpoint. No second flash or reset was sent; complete
ROM readback established the installed bytes independently. Treat generation
change as an alternative reboot observation when reusing this watcher.

[Exact identities and results](hardware-results.json). Local complete logs and
ROM images are under `agents/audit008/hardware`. Broad negative/ABI coverage
remains the local suite in [implementation results](IMPLEMENTATION.md). No
physical native-keyboard human check, exhaustive SD fault test, runtime stack
high-water check or game compatibility acceptance is implied by this run.
