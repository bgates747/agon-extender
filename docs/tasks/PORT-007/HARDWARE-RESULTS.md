# P4-local SD hardware results

**Pass for the bounded file-management checks.** Candidate
`uart-excom-console-r57-b2026-09-26-22-46-38Z` is installed on the local DevKit.
Production selection remains v0.1.0/r55 pending Author acceptance/promotion.

## Identity and preservation

Source commit `1ebef276bd435be44625f046d115fec90503c3c3`, clean identified build,
ESP-IDF 5.5.5. Full incoming r55 flash was saved before r56; the overwritten r56
prefix was saved before r57. Independent flash verification and expected boot/USB
host startup passed for both. No EMOS, mainboard VDP or Agon SD files changed.
Two normal Agon resets restored input admission after the P4 flashes.

| Artifact | SHA-256 |
|---|---|
| `uart-excom-console-r57-b2026-09-26-22-46-38Z.bin` | `e4aa32d225303331355cf774cf7e98abc508df9079e5c803db8dd124a01e0507` |
| `uart-excom-console-r57-b2026-09-26-22-46-38Z.factory.bin` | `06ec2ef817f38e3d62dc28869d9267be3b8f8b39637f6e51e988c70f40bf5697` |

## Results

| Check | Observation |
|---|---|
| Mount | Passed; no formatting; 31,914,983,424 raw card bytes |
| Filesystem | 31,902,957,568 bytes; initially 31,902,924,800 free |
| Main card suite | 25 checks completed in 6.22 host wall-clock seconds, excluding build/flash/reset |
| Binary upload/download | 1,048,598 bytes compared exactly |
| Replacement | New bytes verified; interrupted replacement preserved old bytes |
| Directory operations | Parents, recursive list/copy, move, recursive removal and absence checks passed |
| Search | Wildcard basename and literal content matches passed |
| Rejections | Existing destination 409; descendant copy 400; root deletion 403 |
| Nonrecursive nonempty directory delete | Refused with 403: ESP-IDF FatFS maps FR_DENIED to EACCES |
| Video coexistence | 4,194,304 byte transfer verified with 183 compressed video messages received; no errors |
| Input/display | Ready/neutral keyboard; typed echo output read back from ExCom screen |
| curl | Separate upload/download byte comparison and recursive cleanup passed |
| Cleanup | Only new timestamped test trees were mutated; test files removed; parent agent directories retained |

Video messages were checked for expected framing, not measured as a gameplay
benchmark. No claim of unchanged frame rate, physical-keyboard switch coverage,
all card types, hotplug, power-loss recovery or exhaustive fault injection.
Host tests separately cover depth guards and failed-installation rename rollback.

## Informative failure and correction

r56's first new-file round trip passed. The existing-destination test exposed a
TCP reset while the client was still transmitting, hiding HTTP409. r57 consumes
bounded fixed-length request data before early rejection. The full r57 rerun
received the intended 409 and passed. Interrupted clients still abort staging;
there is no automatic retry or replay of mutations.

## Reproduction and evidence

Follow [the operator guide](../../p4-sd.md) against a new directory under
`/agents/extender`. [The contract](NETWORK-CONTRACT.md) specifies the bounded
procedure and deployment gate. Local build manifests, full/prefix backups,
flash/boot receipts, test scripts, checks, curl proof and coexistence records are
retained in the ignored `agents/p4-sd/` silo. No private endpoints are published.

Final state: r57 running, ExCom CLI responsive, keyboard ready/neutral, no agent
video viewer left connected, no foreground Agon SD listener required. User files
and selected production bundle remain unchanged. Await Author review.
