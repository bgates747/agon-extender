# PORT-008 — Full EDP data-only control r01

The Author-requested comparison confirms that a failure remains without the
special diagnostic counters or phase tracing. One-byte forward/reverse readback
passes. Both 255-byte operations complete, but the echoed data first differs at
zero-based offset 2 (the third byte). The fixture stops there; 4096-byte cases
are not run. This does not identify the failing direction or establish a wiring
fault. Input is recovered; startup, mainboard VDP and production are unchanged.

## Composition and evidence

1. Full working EDP base, including HDMI automatic carriers, rolling scanout,
   320-pixel scaling, USB FS/LS host, browser keyboard/paste/reset and services.
   Maintained source was frozen in the identified build archive. Comparison-only
   native transport/echo endpoint is explicitly selected; ordinary file services
   still use UART. This is not public parallel SD support or formal ExExt.
2. P4 `port-008-data-r01-b2026-10-10-03-07-07Z`, application SHA256
   `c6ee15085de8dd9a2a81c9ab5e28d82971a4b6c9bb4339cc74d0377a7981144c`.
   Four flash segments independently verified. Final ELF has no `pcnt_new_unit`,
   `pcnt_new_channel` or private pattern-probe symbols. No special serial
   collector, edge counter, phase trace or timing instrumentation was used.
3. Existing installed EMOS
   `agon-emos-v0.1.24-b2026-10-10-01-48-39Z` retained. Its full-ROM verification
   from the preceding installation remains the identity authority; no intervening
   EMOS change or redundant reflash. Its private gateway supplies native transfer
   access to the MOSlet without raw application GPIO/register/vector access.
4. Comparison-specific native completion requires the real matched fixed-length
   DMA callback and inactive VALID, retaining reciprocal handshake, cleanup and
   UART return. It deliberately does **not** establish exact edge counts or
   asynchronous-reset fault recovery. The strict composition remains unchanged.
5. `/emos/parcheck.bin`: 9420 bytes, SHA256
   `f144d58df1dbe20494a291f1dbf6c179098bdcfd4691cf13986854d27269f56a`.
   Three planned echo pairs: 1,255,4096. MOSlet writes a position-dependent
   pattern, reads it back and compares every byte and guards. P4 only retains
   and echoes the block; no P4 pattern generator or per-byte tracing.
6. Durable result `/agents/extender/results/P8D01.CSV`; invocation batch
   `/extender/install/p8data01.txt`. Both fixture and batch were staged/read back
   over the ordinary UART listener; that staging is not parallel evidence.
   Known files remain evidence, not automatic retry scripts.

## Results

Worst case first, ranked by integrity failure, then unperformed, then passing.

| Block length | Agon → P4 native status | P4 → Agon native status | Whole roundtrip comparison | Guards |
|---|---:|---:|---|---|
| 255 bytes | 0, completed | 0, completed | Fail: first differing byte at offset2 | Pass both operations |
| 4096 bytes | Not run | Not run | Not run after first mismatch | Not measured |
| 1 byte | 0, completed | 0, completed | Pass, exact match | Pass both operations |

Status0 establishes the comparison service's matched completion, **not** byte
integrity at the P4 receiver. The echo mismatch can originate on either leg.
Unlike the earlier strict probe, this comparison completes the 255-byte block;
that change does not prove the extra counter readings were erroneous, and the
full-HDMI/output composition is another changed variable. No throughput or
fault qualification is claimed from these few operations.

The fixture's nonzero exit aborts its batch before the listener line. A separate
recovery reset encountered the previously reproduced boot-release stall; a second
recovery reset restored admission. Neither reset replayed parallel data. CSV,
fixture and original38-byte startup were read back; listener exited and input
was ready/neutral. No startup edits, firmware backups or mainboard VDP flashes.

## Software and prior-art checks

1. Nine data-only native cases pass with ASan/UBSan: both directions and all
   selected sizes, real callback identity/length, inactive VALID, timeout, no
   PCNT allocation and retained data on rejected publication.
2. Existing strict native209 cases and build-selector14 cases remain passing.
3. Original DevKit receiver recovered from legacy commit `4626fcc`,
   `src/prx_receiver.c`; SHA256
   `0e0f76c0b252ebba0f61ebd74390ec086e95a163b1ba32c4c57e294a1a0969c5`
   matches its retained fixture manifest. It used external-clock/falling-edge,
   active-low VALID, free clock and positive fixed byte-count EOF without PCNT.
   Original queue10/max10KiB/fixed1024 differs from current queue1/exact admitted
   size. This was mechanism reuse, not an exact repeat on the P4-PC; original
   evidence never qualified direct reverse parallel.

Ignored local evidence under `agents/port008-live-qualification/data-check-r01`
contains frozen source/build, final validation, installation receipt, staged
fixture source/binary, CSV, first recovery failure and successful handback.
The [earlier strict probe](LIVE-QUALIFICATION-BLOCK-R04.md) remains frozen.

Next investigation requires distinguishing forward from reverse corruption,
preferably against the original1024-byte forward case and physical harness
checks. No larger repair campaign or additional run is started by this record.

## Follow-up data-wire attribution

The Author-requested [adapted existing pinwalk](PINWALK-R01.md) verifies all
eight forward data-wire assignments. Reverse waveform/readback corruption
remains; static wire attribution is not link qualification.

The subsequent [clock/handshake capture](PINWALK-R02.md) has exact3456 payload
clocks in both directions and READY continuously asserted. Observed reverse
D7 is already wrong on the wire during the first byte; the other four probed
data bits match. No P4 memory attribution or remedy is claimed yet.

The subsequent [bounded P4 memory snapshot](DATA-SNAPSHOT-R01.md) separates
pre-echo retained-buffer corruption from an additional first-byte output
discrepancy. The previous uninstrumented traces remain controls; no remedy yet.
