# PORT-008 — Pinwalk with clock and handshake probes r02

The captured payload clock counts and handshake levels are correct in both
directions. Four observed return data bits match, but D7 is corrupted early in
the echo. Its first byte is already wrong on the physical wire before the Agon
samples it. Focus the next investigation on P4 reception, retained bytes and
transmission; this result does not justify another data-wire rearrangement.

## Frozen comparison

1. Author moved three analyzer probes onto nearby READY_N/CLOCK/VALID_N contacts
   on the same Agon header, then authorized this run. Five data bits remain
   observed: D2,D4,D5,D6,D7. Private exact channel assignments and attachment
   details remain in the ignored local bench record.
2. Reused the [adapted existing HW-002 pinwalk](PINWALK-R01.md) without any
   executable change: `header-pinwalk-native-r01-b2026-10-10-03-37-59Z`,
   SHA256 `11b2bea54e85fe54af2ebd984a8546ecc519827873a3fae5e38bde79f99f4f29`.
   One3456-byte Agon-to-P4 block, then one same-length P4 echo. EMOS owns both
   directions, GPIO, clock and handshake; the MOSlet supplies/compares bytes.
3. Installed full HDMI EDP and EMOS are unchanged from
   [data-only control r01](DATA-ONLY-CONTROL-R01.md). No firmware flash, new
   counter/instrumentation code, mode change or startup change. The existing
   fixture was read back; only a fresh invocation batch was uploaded.
4. Initial preparation was blocked by a physically displaced mainboard SD card.
   The Author reseated it, restoring startup and keyboard admission. That
   resolved setup mistake is not another established boot-release defect;
   its setup-only capture was discarded. Two earlier preparation resets
   preceded the correction. No reset or payload replay occurred during this run.

## Results

| Measurement | Agon → P4 | P4 → Agon echo |
|---|---:|---:|
| Intended payload | 3456 bytes | 3456 bytes |
| CLOCK falling edges while VALID_N low | 3456 | 3456 |
| READY_N high at payload falling edges | 0 | 0 |
| Payload VALID_N low interval | 1 uninterrupted | 1 uninterrupted |
| VALID_N interval duration | 19.893792 ms | 19.893625 ms |
| Observed D2,D4,D5,D6 mismatches | 0 each | 0 each |
| Observed D7 mismatches, one µs after CLOCK rise | 0 | 633 |
| First D7 mismatch at that sampling position | None | Byte0 |
| Last D7 mismatch at that sampling position | None | Byte768 |
| MOSlet service status / buffer guards | 0 / pass | 0 / pass |
| Whole returned-byte comparison | Not independently read at P4 | Fail at byte0 |

D7 mismatch counts are relative to the expected pinwalk, not comparison with
independently inspected P4 memory. Reverse output shifts on the falling edge,
so the principal data check samples24 analyzer ticks/one µs after the rising
edge. The Agon uses an IN0 after its rising-edge control helper returns. This
sample position is an analysis reference, not an exact instruction trace of
the Agon's read. A second check two sample ticks after each falling edge also
finds D7 corruption (431 sampled mismatches, last at832); the four other observed
data bits still match. These differences reveal intra-cycle changes in part of
the corrupted region, not two different application runs.

The decisive first-byte check is independent of that offset choice: D7 stays
low for the entire first reverse falling-to-falling cycle, although the expected
byte is0xFF. CLOCK rises55 analyzer samples after that first falling edge; the
next falling edge is138 samples after it. Thus the wrong first bit exists on
the wire before the Agon's sampling operation. This rules out an exclusively
Agon software-read explanation for this occurrence. It does not distinguish
P4 RX/DMA/retained storage from P4 TX/pad output, nor prove analogue integrity.
Unprobed D0,D1,D3 cannot be judged from this capture.

## Evidence and handback

1. Acquisition:24MHz ×480million samples,20seconds, all eight analyzer channels,
   exact saved extent, successful capture exit and verified archival extraction.
   Digital sample clock is nominal/uncalibrated;41.67ns sample spacing limits
   edge resolution. No claim that these counts invalidate the earlier different
   strict-counter/255-byte experiment.
2. Complete raw sample SHA256:
   `4c084c08585c88ed07072abcdc5c5f75c8ed1f94a3019f74914d06406ac79105`.
   Forward VALID window:164792875–165270326;
   reverse:166489037–166966484. Full raw channels are retained in `logic.sr`.
3. Ignored evidence: `agents/port008-live-qualification/pinwalk-r02/` contains
   exact map, manifest, staging verification, capture command/receipt, complete
   trace, reproducible analysis and Agon CSV. Fresh SD files:
   `/extender/install/p8walk02.txt`, `/agents/extender/results/P8W02.CSV`.
   Result names are consumed; do not replay these invocations as a fresh run.
4. Capture/invocation/retrieval:20.86 host wall seconds; staging/preparation
   separate. Original38-byte startup read back unchanged, listener exited,
   keyboard ready/neutral with no held or pending keys. No ongoing host action.
   Mainboard VDP and production unchanged; no further remedy started here.
