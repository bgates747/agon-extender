# Two-way PARLIO SD candidate r02

The candidate adds parallel downloads to the existing parallel upload path.
The Pi5 runner can stage an input file and collect a generated result through
the same foreground SD listener with PARLIO required in both directions.
The Olimex still needs a physical qualification before this stack can replace
the production bench configuration.

The [approved amendment](../PORT-008.md) was frozen at
`4e4e5f20cac833f6b8137e01c140d974a4fe90d1`. The
[staged file protocol](../../protocols/mainboard-sd-staged.md) defines the
candidate wire and HTTP contract.

## Source and ownership

| Component | Starting point and change |
| --- | --- |
| EMOS | Retained production ROM source `2c79c6006d6bcb0c2b3f9d8d6aae3ef4b36c730a`. Enable the existing native eZ80 byte sender for the private foreground SD gateway only. Keep guarded UART0 and UART1 application networking. EMOS owns admission, UART parking, the eZ80 shared pads and reciprocal return. |
| Canonical listener | Upload candidate `da50ee125b0d358311e5b81fe9e48927961bf4d5`. Reuse the sequential FatFS reader and the existing 512-byte upload buffer, with one additional gateway operation byte. Each required GET block must read exactly the requested bytes before physical admission. |
| EVDP | Upload candidate `665a4911a07f4444802ba7718aab9e95b0816fe1`. Reuse its single console-owned physical mailbox, the existing native P4 receiver and the pinned finite-RX driver fix. The P4 worker owns the private staged snapshot and never passes file bytes to the VDU decoder. |
| Pi5 | The staged client selects and checks the direction-specific capability. Schema 3 stages and collects through the same commissioned runner, records actual carrier and checks the fixture's expected output. |

Native source pins are `abefa2f943eb3089c08d85bf39e48ebb4938f4bd` (ROM),
`b949b7505f121b58623a94b31bb9b53a75b7819f` (listener), and
`cd3835d62189f2013634e574224cc9223882d894` (P4). These are identified
candidate branches based on the preceding stack. The native P4 branch keeps
an unrelated, retained TX diagnostic difference from the runner checkout.
The RX leaf and modified transport sources match.

The official MOS API documentation at `f9806bd3cbff` describes the foreground
FatFS calls and resolved-path requirement. The listener keeps its existing
FatFS calls and absolute root checks. The extension adds a private
`ext.sdlink` operation and leaves the official MOS call table alone.

The eZ80 clocks the eight P4 data wires. The P4 console task retains the
512-byte destination and owns a bounded DMA receive until it has stopped the
driver and released the shared pads. A failed driver stop retains the DMA and
callback context. The worker writes each block only after both physical return
and the corresponding UART reply. It publishes the entire file after sync and
close. A failed job remains private. The first version uses one handover per
512-byte block. It avoids a whole-file eZ80 allocation and leaves upload's
one-admission-per-file design in place.

The P4 bounds native receive to two seconds, preparation to five seconds, each
download RPC to 30 seconds and mailbox retirement to ten seconds. The unchanged
upload path retains its separate long payload allowance for Agon SD writes.
The ROM's existing keyboard deadlines bound eZ80 handover and recovery. File
contents use no CRC, digest or routine verification GET. Mandatory size,
framing and physical completion checks detect partial transfers.

The candidate uses 129,922 bytes of the EMOS ROM, leaving 1,150 bytes free.
The listener binary is 26,127 bytes. Its linked code, data and BSS leave
3,388 bytes for stack and heap in the 32 KiB MOSlet region.

## Offline results

The identified EMOS, P4 and listener builds passed. The P4 validator confirmed
the matching RX and TX SDK derivatives in the application link. The original
P4 attempt received SIGTERM and joined. The resumed build reused the generated
project and existing objects after rechecking the source closure. The standard
validator and artifact manifest ran on the completed build.

- The paired file test passed 33 cases. It used the real staged engine and
  listener with a modeled physical transfer. It covered empty input and output,
  block boundaries and tails, a 1.1 MB file, missing capability, source EOF,
  local spool write failure and loss of physical or control completion. The
  test observed zero CRC calls in both directions.
- The paired coordinators passed 20 cases, including short receive and a stop
  fault that retained the callback and DMA. The native payload model passed 213
  strict cases and the upload model passed 156. The HTTP worker refused access
  to a failed snapshot.
- The staged client, direct client and bench runner passed 47 Python checks.
  The listener regression passed 58 checks. Two isolated-worktree codec checks
  were covered by a separate byte comparison. One check was fast-only and
  skipped in checked mode. Both schema 2 and schema 3 packet preflights passed.
- Pi5 compiler slot 944 was released after the owned work joined. Physical
  transfers, electrical timing and throughput await the bench run.

## Artifact pins

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| P4 candidate application | 1,768,544 | `ed9f3ad7b78b5582f32901aeb88209c80bae97514b83309df79325c218cb8a00` |
| P4 candidate app0 write | 1,769,472 | `8675dea4b9d80f9a35c42a69f4a60d64a00a6fc46630de9ca6572412efb6d01b` |
| P4 production app0 restore | 1,769,472 | `9e0814bcca05118758df25b244c489a010e795b603941feaeb62dc964a0890ca` |
| EMOS candidate ROM | 131,072 | `9b90b5d94ec6888d85ef1fa1acf23a82b2e0eb1f179b75f549863fbd72343673` |
| EMOS production ROM | 131,072 | `a25f1612f4aaa542c5488cf3266d968ad3d1d61e9df3b5ce2c680650f5d7a2ca` |
| Candidate listener | 26,127 | `98492acc7dcd29e484ef76c69026e8801375738c33c617ba61a94d8481151f08` |
| Production listener restore | 24,753 | `0566e17f18747c2e625d2450ce5324a2b1097bce323a5e4d70fad6dcb41cdff2` |
| Worked example fixture | 8,196 | `0160bd88c689f43a1c3773901889de258289eaa745515d9173e516fce7abfa5d` |

The packet pins the P4 partition table and the two FF-padded app0 files for
`0x20000` and a `0x1B0000` write extent. The local packet is
`agents/port008-production-parallel-r02/qualification-r02/qualification.json`
with SHA-256 `0ea12083cd0d7d172341d27e5998e64d5eec6f7f704b70ae6dc6b1325bd7ddee`.

## Physical packet

Use the pinned local packet and operator handoff for the exact config and
commands. The same operator retains the slot through the normal check-in. VDPlet
stays in its production state. The launcher preserves the first failed phase
and requires the preceding parent-verified joined receipts.

| Phase | Limit | Required effect |
| --- | ---: | --- |
| `prepare-emos` | 360 s | Stage only the two ROMs and verification commands through the existing checksum-free UART bootstrap, then exit the listener. |
| `install-p4` | 650 s | Write and independently verify the pinned app0 extent. Paired start returns to Legacy CLI. |
| `install-emos` | 420 s | Write the candidate ROM, independently compare 128 KiB and return to a working CLI. |
| `install-listener` | 300 s | Install and verify the candidate at `/emos/sdserve.bin`. Preserve the pinned standard for restoration. |
| `stage` | 600 s | Stage the worked example and all fresh scratch inputs, including the empty case, with required PARLIO and no fixture readbacks. |
| `verify-scratch` | 720 s | Retrieve the same scratch cases with required PARLIO. Compare local bytes for this transport qualification and record GET receipts. |
| `run` | 240 s | One observed `LOAD` and `RUN`. Require `OLIMTEST PASS`, a returned prompt and the exact 20-byte result with one LF, retrieved through PARLIO. |
| `restore-listener` | 240 s | Restore the pinned standard listener and verify that it works. |
| `restore-emos` | 420 s | Restore the pinned production ROM and independently verify 128 KiB and CLI. |
| `restore-p4` | 650 s | Restore and independently verify the production P4 app0 extent. |
| `handback` | 90 s | Working CLI, idle listener and transfers, free serial handles and joined workers. |

The total phase ceiling is 4,690 seconds. Scratch case sizes are 0, 1, 511, 512,
513, 4097, 65,537 and 1,100,000 bytes. The checksum-free UART bootstrap and
independent firmware verification are for candidate installation only. Scratch
comparisons qualify the path and remain outside normal or timed staging.

### Listener install continuation

The original physical run verified the P4 and EMOS candidate installs. Its
listener install stopped on MOS's informational `Moving …` line before the
second rename. The joined CLI inspection observed the production listener
under `previous.bin`, the staged candidate under `next.bin`, and the canonical
slot vacant. Smith authorized inspection and continuation. The amended
observer accepts the matching banner and requires a fresh returned prompt.
The continuation runs just the unfinished rename and verifies both listener
identities. The failed worker and its inspection stay in the original run
evidence. After recovery, the remaining phases use the same packet and bounds.
