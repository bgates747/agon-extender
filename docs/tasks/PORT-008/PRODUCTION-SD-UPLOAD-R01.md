# Production PARLIO upload candidate r01

This packet qualifies a single canonical SD listener with the current EMOS
receiver, a PARLIO-enabled EVDP sender and the generic Pi5 staging runner.
The candidate carries the proven upload behavior into the accepted sequential
reader lineage. The qualification uses the normal `/emos/sdserve.bin` name.
The current production bench procedure remains the custody and failure authority.

The first tranche starts from the [frozen PORT-008 plan](../PORT-008.md) at
`a5d249e3220a6ab836d4f471e25bd04e67f0050e`.

## Source and component selection

| Component | Selected inputs and decision |
| --- | --- |
| EMOS | Keep `a25f1612`, source `2c79c600`. Its linked `ext.sdlink` gateway implements operations 7, 8 and 9 and owns the receive buffer and handover. The trial and retained EMOS revisions have identical `emos_sdlink.c`. The receiver implementation has changed, so physical compatibility is still part of the test. |
| `sdserve.bin` | Start from accepted sequential reader `b8e72c91`. Apply the listener's upload-only source delta from trial `6ececd56`. The regular build includes the upload code. `EMOS sdserve --fast --parallel /` checks the resident gateway and advertises HELLO `0x80`. `EMOS sdserve --fast /` keeps the existing checksum-free UART path and sequential reader. |
| EVDP | Start from production sender-disabled build source `e14e0b8a`. The retained source for the PARLIO upload sender, VALID filter, DMA driver adaptation and file engine already matches the repaired trial at `9897b1d1`. Enable the upload build option and preserve the production reset/boot, UART application networking, controller, USB and HDMI choices. Keep the standard EMOS and VDPlet pins. |
| Host | The schema-2 runner uses an exclusive direct metadata session, then individual P4-staged uploads, then a new direct session for EXIT. Each staged POST asks P4 to require PARLIO. P4 refuses before creating the Agon upload if the listener lacks the capability. The host refuses an older P4 that does not advertise support for that request. |

The [mainboard SD contract](../../protocols/mainboard-sd-staged.md) supplies the
worker and HELLO behavior. EMOS owns the link and receiver. The listener owns
FatFS writes and the bounded MOSlet memory. EVDP owns the sender and P4 staging.
The candidate adds no public MOS ABI or new hardware wiring.

## First-tranche result

The listener branch `codex/port008-production-sdserve` is at `da50ee1`. The
native listener is 26,449 bytes. Linked BSS ends at `0xB7404`, leaving 3,068
bytes below the MOSlet ceiling for heap and stack. The EVDP build branch
`codex/port008-production-sd-p4` is at `665a4911`. Its native wrapper passed
source, SDK derivative, partition and final image checks. The SDK config
differs from the standard only in the source path of the byte-identical
partition table. The other board and feature selections compare equal apart
from enabling the upload sender. The original EMOS ROM was rehashed and kept.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| EVDP candidate application | 1,766,384 | `e9fdde0cd28d7da370814705173073c53ea5db60448dcd5b672497f831e51bef` |
| P4 candidate app0 write | 1,769,472 | `d707e0a5cfdd4c4e85eea06cc9f6b8db32054875b2275e46e4239931a285551d` |
| P4 production restore write | 1,769,472 | `9e0814bcca05118758df25b244c489a010e795b603941feaeb62dc964a0890ca` |
| `sdserve.bin` candidate | 26,449 | `9ac92f197a279f13cfe31d3080a953a0c4862839a247100e6664f7a5ae0903bf` |
| Accepted `sdserve.bin` restore | 24,753 | `0566e17f18747c2e625d2450ce5324a2b1097bce323a5e4d70fad6dcb41cdff2` |
| Retained production EMOS | 131,072 | `a25f1612f4aaa542c5488cf3266d968ad3d1d61e9df3b5ce2c680650f5d7a2ca` |
| Fresh worked fixture | 8,194 | `5f98c1b68f496817702b50b46b49dc06042c9417be72345e5d2d667348d74826` |

The partition table matches the qualified app0 layout. Candidate and restore
are padded with `0xff` to `0x1B0000` at offset `0x20000`. The Pi5 packet
under `agents/port008-production-upload-r01/qualification-r01/` has SHA-256
`ada62438096850894dcdc01c68f1f77c8ce658536986847a91afcea6e60cefde`.
Offline preflight verifies the inputs and prints all eight phases.

The paired P4/real listener file-policy test passed 19 cases, including one
bulk request per nonempty file, zero CRC calls, empty controls, refusal before
Agon file mutation without either capability and no incomplete activation.
The modeled sender passed 156 cases. The ordinary listener regression passed
58 checks. Its three sibling-checkout codec checks were skipped in the
isolated worktree and the canonical codec was compared byte for byte
separately. The staged worker test passed. The 18 bench runner, 12 staged
client and 15 direct client regressions also passed. Compiler lease 943 was
released after the owned jobs joined. Physical qualification remains open.

## Candidate phase sequence

The local packet pins the candidate and restore P4 images and common FF-padded
app0 extent, the approved partition table, both canonical listener artifacts,
the retained EMOS ROM and the fresh worked-example inputs. The host fixture
uses the existing C example with a new absolute result path so it leaves the
earlier example and its evidence intact.

| Phase | Parent deadline | Expected evidence |
| --- | ---: | --- |
| `install-p4` | 650 s | Pinned app0 partition and write extent verified. Joined paired boot and working CLI through the current listener. |
| `install-listener` | 300 s | Candidate provisioned to a temporary name via the existing checksum-free service. Service EXIT. Two observed MOS `RENAME` commands preserve the outgoing listener and establish the canonical candidate. Exact installed listener bytes and CLI checked once. |
| `stage` | 300 s | The standard schema-2 runner stages the worked program and 24 scratch inputs. Each nonempty transfer returns PARLIO completion. The empty file uses control records only. No payload verification or readback is part of this phase. |
| `verify-scratch` | 480 s | The qualification operator retrieves the scratch files through a separate checksum-free UART session and independently compares them with the retained inputs. These comparisons qualify the transport and are outside routine or timed staging. |
| `run` | 240 s | One explicit worked-example `LOAD` and `RUN`. Require `OLIMTEST PASS`, the returned CLI and exactly 20 result bytes ending in one LF. |
| `restore-listener` | 240 s | Preserve the candidate at the job's evidence path. Restore the saved standard to the canonical path and verify it. |
| `restore-p4` | 650 s | Restore and independently compare the full production app0 extent. Joined paired boot and working CLI. |
| `handback` | 90 s | Working Legacy CLI, idle transfer services, free serial ports and joined workers. The operator checks in through the scheduler. |

Use the full Extender checkout and the commissioned local configuration
bound in the packet handoff. The command below is offline and prints the phase
order. `PACKET_SHA256` is the recorded hash of the complete JSON.

```bash
.venv/bin/python docs/tasks/PORT-008/qualify_parallel_upload.py \
  --packet PACKET.json --sha256 PACKET_SHA256 preflight
```

Once physical qualification is selected and the scheduler opens the slot,
use the identical packet and configuration for each phase in order.

```bash
.venv/bin/python docs/tasks/PORT-008/qualify_parallel_upload.py \
  --packet PACKET.json --sha256 PACKET_SHA256 --config BENCH.local.json \
  --out RUN_EVIDENCE --operator OPERATOR_CHAT_ID PHASE
```

A nonzero result stops the candidate sequence. Follow the
[Olimex bench stop rule](../../operations/olimex-bench/README.md), preserve the
first failure and the original phase receipts, and retain custody for recovery.
The packet does not replay a failed action or choose a different carrier.

## Generic runner interface

Schema `2` keeps the existing single program and result contract and adds an
optional `fixture.inputs` array. Each entry has an absolute `sd_path` under
`/test` and a `source` pin with local `path`, `bytes` and `sha256`. Use fresh
input and output paths. A zero-byte local file creates an empty marker. The
runner records the actual carrier in each `stage-file-NN.receipt.json`.
Schema `1` remains readable for prior jobs. The two-arm invocation and result
collector for CADENCE02 are separate work.
