# AUDIT-010 pre-LCD review baseline

## Executive summary

AUDIT-010's exhaustive P4 target is the accepted native `p4-console` pre-LCD
closure at Extender commit `755d6f37d332ba95b09519f86b24d352ebb03660`.
BUILD-001 proved that the native graph compiled and linked all 33 selected
project/vendor translation units exactly once, excluded all 11 forbidden
alternatives, passed the browser/codec and detached-consumer controls, and can
be consumed by the accepted Clang/Cppcheck tools. The selected production
bundle remains v0.1.0/r02; this development baseline is not a promotion.

## Immutable identities

| Actor / record | Accepted identity |
|---|---|
| Extender source and native build authority | `755d6f37d332ba95b09519f86b24d352ebb03660` (`source_dirty: false`) |
| Product lineage reproduced | pre-LCD r61 closure originating at `6c6bea3beb2f8abc89c5b1f40a0e7dd0890a084d` |
| Profile / build | `p4-console` / `build001-755d6f37-console-prelcd` |
| Profile manifest SHA-256 | `94610d8768c603c7116478f7b14f0a9d713df8ccb7b9c838d8d115783f67cf16` |
| ESP-IDF | 5.5.5 at `b774170ff46c393eeb5e495ea37936038d3f4f4f` |
| Arduino-ESP32 | managed component 3.3.11 |
| Dependency lock SHA-256 | `542fa22729fa25dd84e19bd2891f626c15ae4b8c4a088904af6e5afd31cf92ad` |
| Effective sdkconfig SHA-256 | `2fcfda86dbf8c7b8d011d02c8fd3df1d9cf06427a3754d09507c99d9da806015` |
| Paired EMOS audit source | v0.1.23 at `21a9ba27f1f346473d767c2c3053ee18e8911335` |
| Selected production comparison | v0.1.0/r02; unchanged |

## Artifact and graph ledger

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Application image | 1,582,848 | `116368382d2ec2e43b1e9cc29a7bfc9914ae3e5314561bdc38e52a5bc7c41d76` |
| Offset-zero factory image | 1,713,920 | `723631f86c0f0ff8d0e5249cdf01733c5519cdae3f0f6ee3cd5c0c81a51c48fb` |
| ELF | 34,274,116 | `9fd09784de8bdb4182157ce9650a81268a5c36f979e738fec4e92fd27d09dbe0` |
| Link map | 13,278,684 | `6415ad2538ed6e5787d4ecdd43180a931782274ff2bea21ea43ae6c27f2c37ec` |
| Canonical GCC compilation database | 24,821,915 | `8da3c8a087171802fe39737c797c35161d2e8c158a51f3d11e47428f89a3d8e2` |
| Graph-validation report | 288 | `99f4136b321fa9298780278bae1ccc06621eaaa62cae3c2a4af9b82d7e39e5b3` |
| Validated Clang database view | — | `c450387d9f904b1b40107c80cbbfeb3033866c2cdad966beebc14e27a4430513` |

The canonical database contains 1,842 total IDF/component actions. The graph
validator selected 33 declared P4 actions, found exactly one action for each,
confirmed their objects in `esp-idf/agon_vdp/libagon_vdp.a`, and confirmed that
archive on the `agon_extender.elf` link edge. The Clang translation revalidated
those same 33 actions before changing only the recorded unsupported GCC flags
and ISA suffix; its translation report SHA-256 is
`06de17e7b556c0a26f6eaae8dec30e4c570c3946fe220c20fa153f089db19730`.

## Accepted analysis entry points

1. A10-BL01 — Treat `<native-output>/build/compile_commands.json` as canonical
   only when `scripts/validate_p4_build.py` passes for the same output/profile.
2. A10-BL02 — Generate Clang's report-only view with
   `scripts/prepare_p4_clang_database.py`; do not substitute generated but
   unlinked CMake descriptions.
3. A10-BL03 — LLVM/Clang-Tidy 23.1.2 parsed the representative presentation
   unit with exit status zero and retained review candidates. Cppcheck 2.22.0
   imported the canonical database, parsed the same unit with exit status zero,
   and reported no bounded smoke findings. These are integration checks, not
   completion of A10-04 or dispositions of the retained warnings.
4. A10-BL04 — `tests/browser_bundle_test.py --build-output <native-output>`
   passed embedded-byte checks, compressed negotiation and 48 vectors across
   EVF1/EVR1/EVP1/EVQ1. The detached HTTP consumer compiled against an actual
   native action from the same database.

## Deferred integration evidence

LCD source is absent from this baseline. LCD-001 retains the working panel
implementation and the demonstrated late-mode20/browser resource behavior for
post-audit reintroduction. The pre-LCD baseline itself preserves the inherited
ExCom Nurples late-mode20 failure: after significant VDP assets are loaded, the
mode request can retain 320×240 geometry; the exact hybrid r61 control showed
the same symptom. AUDIT-010 may analyze the baseline cause, but it must not fold
the later LCD implementation into exhaustive baseline coverage.
