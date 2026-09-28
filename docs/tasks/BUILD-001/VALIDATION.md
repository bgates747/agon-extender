# BUILD-001 native host validation

State: host equivalence review in progress; no firmware in this document is
authorized for deployment. Date: 2026-09-28.

## Validated native profiles

The project wrapper built each accepted profile from a fresh output directory
with ESP-IDF v5.5.5 at commit
`b774170ff46c393eeb5e495ea37936038d3f4f4f`, Arduino-ESP32 3.3.11 and the
exact dependency versions declared by `vdp/build/p4-profiles.json`.

| Profile | Retained run | Selected project units | Result |
|---|---:|---:|---|
| `p4-console` with LCD | `native-console-07` | 35 | Build and graph validation pass |
| `p4-mos-recovery` | `native-recovery-02` | 1 | Build and graph validation pass |
| `p4-port008-nonrelease-qualification` | `native-port008-03` | 28 | Build and graph validation pass |

For every row, `scripts/validate_p4_build.py` read the actual
`compile_commands.json` and `build.ninja`, proved each declared unit compiled
exactly once, proved each forbidden unit compiled zero times, proved every
selected object entered `libagon_vdp.a`, and proved that archive entered the
ELF link. The validator also checked the declared feature definitions and the
C++17 boundary.

## Exact controls retained

1. B01-V01 [x] The native and hybrid generated configuration headers contain
   1,540 enabled `CONFIG_*` definitions. The only two textual differences are
   `CONFIG_PARTITION_TABLE_CUSTOM_FILENAME` and
   `CONFIG_PARTITION_TABLE_FILENAME`: native CMake records the absolute input
   path while the hybrid records `partitions.csv`.
2. B01-V02 [x] The resulting partition-table binaries are byte-identical:
   SHA-256
   `e29396a4f5ecc129c0e275d2df19d69adb5ee33389e3d5659e9a50932ac6864a`.
3. B01-V03 [x] All 24 dependencies in the hybrid lock retain the same versions.
   The native lock adds Arduino-ESP32 3.3.11 as an explicit managed component,
   replacing the hybrid build's separately acquired framework package.
4. B01-V04 [x] The five browser assets have start/end linker symbols owned by
   the native application archive.
5. B01-V05 [x] Two fresh native console builds with the same logical build ID
   have identical lengths and differ in 72 application-image bytes and 35
   bootloader-image bytes. `CONFIG_APP_REPRODUCIBLE_BUILD` remains disabled and
   `CONFIG_APP_COMPILE_TIME_DATE` remains enabled, exactly as in the hybrid
   configuration. The partition image is reproducible. This timestamp/checksum
   variance is bounded and is not presented as byte reproducibility.

## Material size differences

The table compares the preserved hybrid `p4-console`+LCD baseline against
`native-console-07`. Largest percentage increases are first; debug-only ELF
sections are excluded.

| Region/artifact (bytes) | Hybrid | Native | Difference | Difference % |
|---|---:|---:|---:|---:|
| DRAM1 BSS | 776 | 1,600 | +824 | +106.19% |
| Flash rodata | 310,836 | 388,588 | +77,752 | +25.01% |
| Application binary | 1,646,592 | 1,801,168 | +154,576 | +9.39% |
| ELF text total | 1,623,330 | 1,777,516 | +154,186 | +9.50% |
| Flash text | 1,203,844 | 1,279,834 | +75,990 | +6.31% |
| BSS total | 1,291,403 | 1,357,167 | +65,764 | +5.09% |
| DRAM data | 22,720 | 23,116 | +396 | +1.74% |
| IRAM text | 108,312 | 108,756 | +444 | +0.41% |
| DRAM0 BSS | 45,200 | 44,672 | -528 | -1.17% |

The principal explained difference is that native ESP-IDF honors
`esp_hosted` 2.12.12's `WHOLE_ARCHIVE TRUE` component property. The hybrid
PlatformIO outer link included the same archive but did not retain its full
component closure. Native-only symbols account for approximately 153,760 bytes
and are dominated by the hosted RPC/protobuf transport. This is a build-system
semantic correction, not an application-source expansion, but its flash and
memory impact is material and must be included in B01-06 hardware qualification.

## Compatibility findings

1. B01-F01 [x] `esp_hosted` 2.12.12 expands `ESP_IDF_VERSION` directly in
   Kconfig. ESP-IDF's activation script normally exports that value; the
   project wrapper now does the same in its isolated environment.
2. B01-F02 [x] Native ESP-IDF enables warnings that the hybrid outer driver did
   not enable. One pinned `esp-modbus` GCC 14 false positive is suppressed at
   the project boundary; four inherited application warning classes remain
   visible but are not errors. No downloaded component source is patched.
3. B01-F03 [x] The current PORT-008 PlatformIO invocation stops before CMake
   because `select_sources.py` requests a missing board option from the current
   PlatformIO host. Native compilation then exposed a non-stock accessor that
   erased `P4DisplayController` to its FabGL base before passing it to the
   concrete cursor seam. The bounded adapter preserves the owned concrete
   pointer type; ordinary base-class callers still convert normally. This path
   is absent from the accepted stock-runtime console composition.

## Remaining host gate

B01-V06 [ ] Run and record the accepted AUDIT-010 static-analysis smoke against
the canonical native compilation database. This host has `clang` but does not
currently provide `clang-tidy` or `cppcheck`; tool acquisition and commands must
follow AUDIT-010's accepted research rather than inventing a migration-local
scanner policy.

After B01-V06, present the exact B01-06 hardware run sheet and stop for Author
authorization. Do not flash, reset, deploy or alter production selection from
this host evidence.
