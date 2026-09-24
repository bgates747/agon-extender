# AUDIT-008 — First-tranche implementation results

Local implementation and validation completed 2026-09-24 UTC, within the
Author's one-hour limit. The original local-only run touched no hardware. Subsequent Author-authorized
[physical deployment and bounded checks](HARDWARE.md) now pass.

## Measured result

Baseline: unchanged ordinary EMOS v0.1.18, source `f047b6a`, build
`agon-emos-v0.1.18-b2026-09-24-01-29-36Z`.
Candidate: ordinary draft EMOS v0.1.19, implementation source `49cbd36`, build
`agon-emos-v0.1.19-b2026-09-24-02-02-56Z`.
Same compiler/linker, ordinary profile and port revision for both measurements.

| Measure | Before | After | Change |
|---|---:|---:|---:|
| ROM occupied | 131,056 bytes | 124,774 bytes | **6,282 bytes recovered** (4.79% of previous occupancy) |
| ROM headroom | 16 bytes | **6,298 bytes** | +6,282 bytes |
| Free share of 128 KiB ROM | 0.0122% | **4.8050%** | +4.7928 percentage points |
| Static RAM | 6,826 bytes | 3,671 bytes | **3,155 bytes recovered** |
| Calculated heap arena | 7,510 bytes | 10,665 bytes | +3,155 bytes |
| Reserved stack | 2,048 bytes | 2,048 bytes | unchanged; no high-water measurement |

The result exceeds the frozen 4,096-byte net ROM target by 2,186 bytes. It is
still 16,284 bytes (15.01%) larger than the retained 108,490-byte official stock
MOS image. That stock-image comparison is descriptive, not a same-toolchain
optimization measurement. Do not confuse it with the older 102,055-byte
AgonDev-stock measurement in the research report.

The final image is nine bytes larger than the first locally linked candidate:
it explicitly preserves the old zero output-length result for an absent external
service. Only the final candidate above is the reference for these results.

## What changed

Resident EMOS no longer contains the cancelled external `.emo` discovery,
registry, CRC/load/invoke, swap-file preservation or arbitrary-command fallback.
`DISCOVER` and `CLEAR` remain reserved names returning unavailable. Unknown
external services return not found. Historical container tools and their own
format tests remain historical evidence, not current firmware acceptance gates.

Resident commands win over `/emos/<name>.bin` lookup. The launcher accepts a
bounded ASCII leaf, lowercases it and uses stock `mos_LOAD` / `mos_runBin` at
`0xB0000`. It preflights the 32 KiB bound and basic header extent and rejects
nested disk launches from an application or MOSlet. Global MOS search paths and
application memory are preserved. Utilities use the stock executable ABI, not
relocation or a new provider format.

API 0x51, C function slot 0x20, resident sdlink/text-probe services, busy checks,
application lifecycle resets, mode coordination, keyboard and UART mechanisms
remain resident. The listener already lives on disk; moving it saves no ROM.
No installed listener paths were migrated. The ordinary profile retains its UART
diagnostics; the optional telemetry profile remains a separate qualification
scope and was not rebuilt or physically exercised in this run.

## Validation

| Check | Result and scope |
|---|---|
| Changed artifact registry | r104 validation passes. Full repository version sweep remains blocked by a pre-existing light2-harness-r02 connectivity hash mismatch; unchanged since contract commit cf23ce77, outside this task. |
| Canonical compile/link and all selected profile guards | Pass: source provenance, runtime/linker/layout, firmware descriptor, UART divisor, parallel ownership, keyboard, console, gateway and VDU dispatch |
| Repository host tests | **91 tests passed** with both port root and prepared-source root pointing to the isolated candidate |
| Launcher host tests | Production helper executed with injected file errors, name/size boundaries, load/run results, busy/nested denial and mapped memory |
| Resident gateway host tests | Actual frontend validates request identity/ABI/ranges, retains MOSlet sdlink admission, rejects other MOSlet services, keeps Legacy text-probe admission and zero-length not-found result |
| Official Fab 1.2.5 CLI run | Pass: autoexec plus 28 commands, **39.3 host seconds**, fake VDP; loader/CLI evidence only |
| Target positive paths | Case-insensitive names; arguments; built-in precedence over a same-named disk file; six MOSlet starts including autoexec/re-entry; stock return code 7; 4096-byte application sentinel retained |
| Target negative paths | Overlength/path/extension names, missing/short/bad/oversized/directory/wrong-mode executables; no stale probe execution; nested application and MOSlet dispatch denied |
| Resident behavior exercised | Status from MOSlet and application, fake Dual then Legacy round-trip, retired provider errors |
| Existing sdserve MOSlet | Launches and returns expected EMOS 35 without Extender keyboard/transport; **not a file-transfer pass** |
| Media integrity | Isolated host directory contents unchanged after run |

The first emulator attempt used a decimal CLI address for the hexadecimal
sentinel location; corrected to `0x40000`. No firmware fix was needed. Earlier
broad-test provenance failures came from inconsistent port/build roots; the
final fresh prepared checkout with consistent roots passes all 91 tests. The
parallel source guard needed its deleted-provider boundary updated while
retaining the resident diagnostic guard assertions.

AgonDev's existing startup parser splits quoted whitespace into separate argv
entries. The launcher preserves that stock behavior; it does not add a second
argument parser. The standard executable header does not authenticate bytes,
prove a link address or encode a minimum EMOS version. Arbitrary corrupt code,
stack/heap sufficiency and physical card behavior are not certified here.

## Evidence and reproduction

1. [Measurements](implementation/MEASUREMENTS.json),
   [object costs](implementation/OBJECTS.csv),
   [function costs](implementation/FUNCTIONS.csv),
   [map](implementation/MOS.map).
2. [Exact sources, tool hashes, build commands and limits](implementation/SOURCES.json).
3. [Host test transcript](implementation/HOST-TESTS.txt).
4. [Emulator run/input hashes](implementation/EMULATOR.json) and
   [complete transcript](implementation/EMULATOR.txt).
5. Maintained regression fixture: agon-emos `projects/emos-utility/`, including
   its build instructions and `verify.py`. Maintained utility contract:
   agon-emos `docs/emos-utilities.md`.

The exact baseline and final candidate binaries remain in ignored local audit
build storage. This is not authority to flash either image. Physical keyboard,
ExCom, SD utility loading and live listener transfer checks remain in A08-09,
only after bench access is released and deployment is authorized. No user
review or hardware gate is silently counted as complete.
