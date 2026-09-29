# BUILD-001 native host validation

Sequencing amendment: this document preserves the completed combined ExCom+LCD
host comparison and the candidate that later failed at boot. It no longer
satisfies BUILD-001's replacement baseline. B01-05e must repeat the applicable
controls for the retained working pre-LCD r61 source closure before AUDIT-010
freezes its baseline.

State: corrected pre-LCD host equivalence passed; hardware functional
equivalence remains subject to the amended procedure. Date: 2026-09-28.

## Pre-LCD replacement baseline

The corrected replacement baseline is the clean `codex/build001-prelcd` build
at `e7b35fd5bb5ab88b619a9a433a78ffa132119d19`. The earlier `d17cae79`
candidate proved at hardware that boot, Legacy, ExCom, keyboard and browser HTTP
worked, but also proved staged WebDAV absent. That result invalidated the prior
claim that source-closure equality alone reproduced r61's complete build
variant. Commits `01f067aa` and `e7b35fd5` make the staged service explicit in
the profile and restore the private reset asset as a machine-local wrapper
input.

| Profile | Retained run | Selected units | Application bytes | Result |
|---|---|---:|---:|---|
| `p4-console` | `native-output-e7b35fd5-console-prelcd` | 33 | 1,582,976 | Build and graph validation pass |
| `p4-mos-recovery` | `native-recovery-wired-03` | 1 | 461,440 | Build, generated-payload and graph validation pass |
| `p4-port008-nonrelease-qualification` | `native-port008-wired-02` | 28 | 1,181,008 | Build and graph validation pass |

B01-PV01 [x] The console validator inspected 1,842 actual compile actions,
selected all 33 declared units exactly once, rejected all 11 forbidden units,
proved the selected objects entered `libagon_vdp.a`, and proved that archive
entered the application ELF. The source set is the retained r61 closure's 22
project and 11 vendored units, with no LCD unit or dependency.

B01-PV02 [x] The recovery profile now generates its payload inside the isolated
native component from explicitly named, SHA-256-gated MOS and flash-agent
inputs. The wrapper retains both the generated header and its provenance JSON;
the generated header is not a hand-maintained second authority.

B01-PV03 [x] All project Python test programs passed in the aggregate retained
run `host-tests-d17cae79-r02.log`; the WebDAV runtime suite recorded its one
expected environment-dependent skip. The nested worktree required a temporary
ignored `agon-emos` adjacency symlink, which was removed by the runner and did
not alter either repository.

B01-PV04 [x] `scripts/prepare_p4_clang_database.py` validated and translated
exactly the console profile's 33 canonical GCC actions. Cppcheck 2.22.0 parsed
the representative presentation unit with no reported result. Clang-Tidy
23.1.2 parsed the same unit and reported review candidates, including adjacent
convertible parameters and signed bitwise operands. Those are AUDIT-010 inputs,
not migration repairs.

## Pre-LCD hybrid/native comparison

The hybrid control is hardware-tested r61 build
`uart-excom-console-r61-b2026-09-28-03-12-48Z` from source
`6c6bea3beb2f8abc89c5b1f40a0e7dd0890a084d`. Its application is 1,671,408
bytes with SHA-256
`7b53397f7261d547c61c4fc12e90f029d621d8e96a0f83577406a8c0064e2da2`;
its retained factory image has the task-contract SHA-256
`f794a8bba96f9afbfc1dae6eaa4554eb676880d76ffe74bda97bbebc7e160fea`.
The corrected native application SHA-256 is
`655565e602688204b926d957b034c02a0ae0befad19137f7cf38d034cbce69bc`.

Worst percentage changes are listed first. Debug-only ELF sections are
excluded.

| Region/artifact (bytes) | Hybrid r61 | Native pre-LCD | Difference | Difference % |
|---|---:|---:|---:|---:|
| Flash rodata | 295,776 | 243,764 | -52,012 | -17.59% |
| Application binary | 1,671,408 | 1,582,976 | -88,432 | -5.29% |
| Flash text | 1,250,120 | 1,214,140 | -35,980 | -2.88% |
| DRAM0 data | 21,116 | 20,840 | -276 | -1.31% |
| DRAM0 BSS | 47,960 | 47,608 | -352 | -0.73% |
| IRAM text | 103,516 | 103,342 | -174 | -0.17% |

B01-PV05 [x] The size reduction is explained by the only intentional product
configuration correction: the native profile explicitly disables unused
`CONFIG_ESP_WIFI_REMOTE_ENABLED` and `CONFIG_ESP_HOSTED_ENABLED`. The hybrid
outer link happened not to retain ESP-Hosted's whole-archive constructor;
native ESP-IDF correctly retained it, exposed its early SDIO allocation crash,
and now excludes that unused wired-product dependency by configuration. This
removes remote-Wi-Fi RPC/protobuf/SDIO code without removing maintained wired
Ethernet behavior.

B01-PV06 [x] The partition table remains byte-identical at SHA-256
`e29396a4f5ecc129c0e275d2df19d69adb5ee33389e3d5659e9a50932ac6864a`.
The five embedded browser assets retain their r61 behavior and linker ownership;
the source page remains generic while the wrapper embeds the machine-local reset
endpoint into an isolated generated copy and records only its digest. Native
CMake makes Arduino-ESP32 3.3.11 an explicit managed
component; all other retained managed dependency versions match the hybrid
lock. No unexplained source, partition, asset or material memory delta remains.

B01-PV07 [x] Corrected candidate `build001-eadc2925-wired-prelcd` already passed
the bounded hardware boot canary twice, initialized USB input and wired
Ethernet, and returned HTTP 200 without the assertion or a reset loop. This
supports the configuration explanation but does not substitute for B01-06's
functional-equivalence procedure.

B01-PV08 [x] Candidate `d17cae79` proved that the native profile had omitted
r61's staged-WebDAV variant: HTTP port 80 was ready but port 8081 refused the
connection. Candidate `e7b35fd5` compiles all 33 selected units with
`AGON_EXTENDER_STAGED_WEBDAV=1`; the graph validator passes, its application
contains exactly one configured reset endpoint, its manifest contains no
private URL, and two fresh builds retained the already documented timestamp
variance boundary. Hardware confirmation remains open.

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

## Static-analysis smoke

B01-V06 [x] The Author accepted AUDIT-010's recommended tool selections on
2026-09-28. LLVM 23.1.2 was installed in ignored project state from the official
Linux X64 release archive; its SHA-256
`6382de1c1a210ce5a5cc49d18bc8444d137742e7cbf9b19f4ae602bb1ab52534`
matches the release's signed provenance payload. Cppcheck 2.22.0 was built into
ignored project state from official tag commit
`a436ca35ed1887bee789765122b65ed2d7a7e045`.

Cppcheck imported the canonical database and parsed
`presentation_snapshot_pool.cpp` with no parser error or reported result under
the bounded warning/style/performance/portability smoke. The first Clang-Tidy
invocation correctly rejected GCC-only `xesppie`,
`-fstrict-volatile-bitfields` and `-fno-tree-switch-conversion` inputs; this was
retained as tool-integration evidence rather than misreported as source failure.
`scripts/prepare_p4_clang_database.py` now validates the exact 35 selected
actions and emits a report-only Clang view that removes only the two unsupported
GCC flags, removes the unsupported ISA suffix and supplies the pinned
Espressif C++ headers. Clang-Tidy then parsed the representative unit with exit
status zero. Its warnings are AUDIT-010 inputs and were not repaired here.

The remaining step is the separately authorized hardware procedure in
[HARDWARE-PROCEDURE.md](BUILD-001/HARDWARE-PROCEDURE.md). Do not flash, reset,
deploy or alter production selection from this host evidence.
