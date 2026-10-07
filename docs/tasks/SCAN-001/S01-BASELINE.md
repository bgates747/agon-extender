# SCAN01-S01 — Comparison input freeze

## Executive summary

**S01 complete.** Retained P4 images, source archives and compiler verify. A fresh
read of the Author-mounted Agon card on Lenovo confirms all 12 resident fixture
files, original startup, and the latest compiled `nurples-repair` game/assets.
Full-game Rally and both tracks also match the pinned inputs. The card remains
mounted and unchanged. Current source and runtime inputs are preserved without
changing existing work. S02 has not begun.

The Author-approved performance priority is Nurples: partial vertical scrolling
at least as fast as mainboard, or sufficiently close to leave frame time for
stable sprites and snappy input. Synthetic results support this criterion; they
do not substitute for it. Execute one SCAN subtask per authorization and pause.

## Verified retained comparison inputs

| Role | Identity | S01 result and limit |
|---|---|---|
| Ordinary HDMI rollback / playable baseline | `hdmi-001-r03-b2026-10-05-01-47-13Z` | All recorded artifacts and complete source archive match; exact Author installation receipt retained |
| Failed direct RGB888 experiment | `rgb-001-r01-b2026-10-05-23-30-11Z` | All recorded artifacts and complete source archive match; current maintained build-source scope matches every recorded file |
| Matched instrumented native comparison | `bench-009-r01-b2026-10-05-23-46-18Z` | All recorded artifacts and complete source archive match; same current maintained source scope, different selected configuration |
| EMOS | `agon-emos-v0.1.23-b2026-09-28-02-43-51Z`, source `21a9ba27f1f346473d767c2c3053ee18e8911335` | Retained binary and prior full-ROM readback both match; not a fresh installed-ROM check |
| Mainboard VDP reference | Official v2.16.0, source `c7ac293d2aa81ddfa693390549bcd909069c8fc3` | Clean reference and [verified stock installation evidence](../QUAL-004/sprite-scroll/stock-control/RESULTS.md); live identity must still be reconciled before timing |
| Resident suite | `resident-render-suite-r01` | All 12 catalogue hashes match both the retained snapshot and fresh mounted-card read |
| Primary game source | `nurples-repair`, HEAD `0c741d5` plus preserved local inputs | 81 source/config files and exact executable, symbols, AGNB assets and font retained; existing game checkout untouched |
| Secondary game source | `AgonDefender/rally-game` | 71 source/config files plus exact runtime binary and two tracks retained; no substitution of old Rally product |

Factory-image SHA-256 values:

| Image | SHA-256 |
|---|---|
| Ordinary HDMI | `facab1a27574d8476be64ee19c2fe1b809f581f74ff6fd7c528958230b2c53c8` |
| Direct RGB888 | `913f8a34af1180ffde67272d337c7f4b998c6202e6f2a502163978d766760fa7` |
| Instrumented native | `d4ff7ad7c427cc47cd7ee19eda20b442b2525931b65150fe5f40e6ea51674ff9` |

The ordinary image differs from 17 currently maintained input files in its
recorded scope. Rebuilding today's checkout with a native-output flag would not
recreate ordinary r03; use its retained exact image/source for rollback. The
instrumented native/direct pair is suitable for matched historical diagnostics,
not proof that the ordinary gameplay reports had matched instrumentation.

## Build and reference boundary

P4 build inputs pin ESP-IDF 5.5.5 at
`b774170ff46c393eeb5e495ea37936038d3f4f4f`, the same compiler bytes, P4-PC board
configuration, 360 MHz CPU and 200 MHz PSRAM selections, 128 KiB L2/64-byte cache
lines, pre-v3 silicon range 100–199 and the HDMI component inputs. These are
configuration/receipt facts, not measurements of effective memory bandwidth.
The live silicon v1.3 assertion remains grounded in the prior boot capture.

Official MOS v3.0.2, VDP v2.16.0 and pinned IDF checkouts remain clean.
Official documentation HEAD remains `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b`;
its only dirt is an unrelated untracked `._.DS_Store`, left untouched.

## Game identity and verification limits

1. Current repaired Nurples executable and both AGNB files match this agent's
   retained October 3 `/mystuff/arcade` deployment receipt **and the fresh card
   read**. Current full-game Rally and its tracks also match the card and later
   corrective receipt. The card contains just one `nurples.bin`, in
   `/mystuff/arcade`; its binary, both AGNB assets and font match the maintained
   `nurples-repair/tgt` outputs. No replacement or rebuild was necessary.
2. Nurples executable SHA-256 is
   `63c89d2676f6645631b2240f23002b8b68d45069979a4804ca7d14f34e720088`;
   full-game Rally is
   `4be88dd1c8efbb6f7cddbdce1b98ee8805572f47550cda5d8c0ef3207189395b`.
   Source/asset snapshots are not a new rebuild or a demonstrated source-to-binary
   reproducibility check. The later derivative must establish that itself.
3. Read-only P4 HTTP queries return HDMI mode0, input admitted with no held/pending
   keys, foreground SD offline/no pending job, and diagnostics endpoint404.
   This is consistent with ordinary r03 but is not a full build identifier or
   evidence of a MOS prompt. No serial port, video stream or keyboard session
   was opened, and no reset, file job or benchmark was started.
4. At the initial check no card was mounted. The Author then mounted it on
   Lenovo. Fresh read-only inventory verifies the recorded Agon FAT volume before
   and after hashing; 24 selected files include all runtime assets, 12 resident
   files, service utilities and startup. Startup matches the original 38-byte
   `SET KEYBOARD 1` / `EMOS KEYINPUT extender` file byte-for-byte.
5. S01 pins retained installation evidence and current card inputs. Fresh hardware
   run preflight must still reconcile live firmware/route/readiness against those
   identities. HTTP status alone is not firmware attestation; no routine ROM
   backup, reset, flash or program execution was added to this inventory step.

## Ownership and preserved evidence

| Input / action | Owner and authoritative location |
|---|---|
| VDU routing, transport admission, committed mode | EMOS in the sibling `agon-emos` project; unchanged |
| Drawing, logical storage and HDMI adaptation | Extender maintained `vdp/`; preserved source snapshot, not an editable generated build |
| HDMI DMA implementation reference | Pinned IDF 5.5.5; inspect in S02/S03, no SDK edits |
| Nurples game and art | `nurples-repair`; read-only source for an isolated later test derivative |
| Resident benchmark selection | [Catalogue and operating guide](../../testing/resident-render-suite.md); frozen fixture bytes |
| Bench endpoints, source closures, build receipts, raw inventory | Ignored `agents/scan001/s01/baseline.json`, `http-status.json`, `card-current.json`, `reconciliation.json` and per-source records/archives |
| Current hardware restrictions | Ignored `HARDWARE.local.md`; Author retains flashing control |

The local freeze covers 5,510 Extender/build/test source files. Archives are
verified against the bytes read, and original game/Extender working trees are
not reset or committed. No test result or firmware acceptance has been added.
No unrelated audit, game repair or second SCAN subtask was executed.
