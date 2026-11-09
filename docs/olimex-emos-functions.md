# Olimex standard EMOS — Eirene function inventory

The standard is the retained integrated EMOS Eirene r04 build, complete ROM
SHA-256 `a25f1612f4aaa542c5488cf3266d968ad3d1d61e9df3b5ce2c680650f5d7a2ca`.
The [selector](olimex-firmware-standard.json) pins the source/profile/map and
retained bytes. This inventory makes “latest Eirene functions” concrete without
treating every open proposal or private experiment as a released requirement.

## Selected baseline

1. Source `2c79c6006d6bcb0c2b3f9d8d6aae3ef4b36c730a`, build
   `agon-emos-eirene-r04-b2026-11-06-09-02-21Z`, full ROM 131,072 bytes;
   `EMOS_UART0_RFC25=1`, `network_parallel=false`.
2. Retains Eirene/MOS/FatFS populated public API slots and the EMOS gateway,
   synchronous RST10/RST18, startup-vector initialization after BSS, and EMOS
   transport/routing/input ownership. It includes guarded async output 25h
   using the RC3-style borrowed-buffer/OTIRX mechanism.
3. MOS owner compared populated syscall slots against merged Eirene main
   `3a7259c58bfa6f34f58afe24087f418cef0148e0`: none was replaced by an
   unimplemented slot. This proves table presence, not complete source or
   behavioral parity for every function. Retained build and consumer evidence
   applies to its declared cases; no new exhaustive conformance pass is claimed.
4. The published fork async baseline is
   [RC3 / 97311c437093e416342a6c836cf9914f2ced027d](https://github.com/bgates747/eirene-mos/releases/tag/3.1.0_uart0_rc_3).
   Bare RC3 is not an EMOS image. Old donor include/documentation references to
   42h/43h are historical and are not the selected profile's actual public ABI.

| Facility | Selected EMOS status |
|---|---|
| Current merged Eirene/MOS/FatFS API slots | Retained; per-function exhaustive behavioral parity not claimed |
| RC3-style async output 25h | Included, with real EMOS context/admission result codes; do not use bare RC3's IER-derived A as the EMOS contract |
| Ordinary RST10/RST18 | Synchronous compatibility retained |
| EMOS 51h gateway and route/input/boot ownership | Retained |
| Application-owned controller gateway | Operations4–7,98-byte application reply; matched public client required. Old0–3/96-byte viewer is refused; P4 CI2/CIS2 wire stays96 bytes |
| Old experimental 42h/43h submit/finish | Excluded in this profile; not the latest released RC3 ABI |
| Reset-vector setter 61h | Open, unmerged Eirene proposal at owner review; not implemented or silently required here |
| Buffered keyboard poll 62h | Open, unmerged Eirene proposal at owner review; not implemented or silently required here |
| Counted receive 26h / raw90h | Separate private receive experiment, not part of merged/released Eirene baseline |
| Generic public local drain/finish | Not supplied by this EMOS profile; do not invent one from callbacks or private flags |

The callback releases source storage after FIFO admission; wire drain and VDP
execution are separate. Existing narrow source-callback plus genuinely fresh
ordered POINT reply policy retains its sole-producer and lifetime constraints;
it is not a universal TEMT, renderer-success or optical fence. Firmware/API
comparisons bind the exact consumer contract and do not use a raw-C8 adapter on
this guarded EMOS image.

## Alternatives and future updates

The retained 171c counted-receive composition adds 26h/raw90h to a25f but still
does not implement 61h/62h. Its temporary RX006 qualification against an older
producer does not select it as the default or prove compatibility with VDPlet
v0.1.2-alpha. CPU-accounting and diagnostic compositions likewise remain
purpose-specific. A test of those versions is an explicit firmware/compatibility
exception with current-standard restoration afterward.

When the component owner supplies a newer integrated Eirene/EMOS baseline,
Extender updates the exact selector and this inventory once, retaining its
artifact and declared feature/ABI changes. Operators then reuse it across jobs.
Neither a moving upstream HEAD nor the date of a private build automatically
changes the standard. If Smith explicitly selects open proposals as required
functions, integrate and identify them rather than relabel a25f as containing
them. The no-hacks/controller research boundary is unaffected by this inventory.

Owner evidence:2026-11-08 source return
`olimex-standard-eirene-function-inventory-return-one`; exact ROM/map were
locally rehashed for selection. VDPlet v0.1.2-alpha pairing remains a new testing
combination until its actual installation/operation is recorded.
