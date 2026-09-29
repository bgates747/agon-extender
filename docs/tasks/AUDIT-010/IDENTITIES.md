# AUDIT-010 baseline identities

## Executive summary

A10-02 binds the exhaustive review to the pre-LCD Extender P4 build at
`755d6f37`, EMOS v0.1.23 at `21a9ba27`, and the AgonDev MOS builder at
`90034c23`. The ordinary EMOS checkout has advanced and is therefore not the
audit source; an ignored detached worktree exposes the pinned commit without
altering that checkout. Official MOS v3.0.2 and VDP v2.16.0 are read-only
semantic references. Production v0.1.0/r02 and the installed diagnostic remain
bounded comparisons, not alternate exhaustive targets.

## Repository ledger

| ID | Repository actor and role | Frozen identity | Worktree condition / review rule |
|---|---|---|---|
| A10-ID01 | Agon Extender: exhaustive P4, maintained host/build configuration and active fixture owner | Product/build source `755d6f37d332ba95b09519f86b24d352ebb03660`; host/test baseline `b75aae35313985e76e5e689cd78793a16600fff1` | `main` was clean at A10-02 start. No product or `scripts/` changes exist between the two commits; only the native browser harness and task/closeout documents changed. Review P4 source as built at `755d6f37` and maintained host/test source at `b75aae35`. |
| A10-ID02 | EMOS: exhaustive eZ80 resident services, `sdserve`, `sdjob`, and owned support code | `21a9ba27f1f346473d767c2c3053ee18e8911335`; `EMOS_SOURCE_IDENTITY=agon-emos-v0.1.23` | The normal `../agon-emos` checkout was at `8f29bf81…` with untracked `scripts/application_peer.py`, so it is not the audit tree. Read the pinned detached worktree under ignored `agents/audit010/emos-baseline`; do not modify either tree during review. |
| A10-ID03 | AgonDev MOS builder: exhaustive only where it selects, translates, compiles, links, or validates EMOS | `90034c2348761c42bab4217ce5b0f906922dc0e4` | Clean ordinary checkout at A10-02 freeze. Generic compiler/runtime internals enter detailed review only when an active EMOS path or finding makes them material. |
| A10-ID04 | Official Agon documentation: primary semantic authority | `f9806bd3cbff6ed5d1c08bef1d51fed11764b86b` | Read-only. One untracked Finder metadata file was present and is irrelevant to tracked content. Primary documents include `docs/vdp/Screen-Modes.md`, `VDU-Commands.md`, `Buffered-Commands-API.md`, and `docs/mos/Keyboard.md`, `API.md`, `System-Variables.md`. |
| A10-ID05 | Official MOS source: fallback implementation reference | tag `v3.0.2`, commit `8336409351ee5314e02801a7b72a4f1bb5282519` | Clean and read-only. Consult only where official documentation is insufficient or exact implementation detail is material. |
| A10-ID06 | Official VDP source: fallback implementation reference | tag `v2.16.0`, commit `c7ac293d2aa81ddfa693390549bcd909069c8fc3` | Clean and read-only. Untouched upstream/FabGL internals are not a second exhaustive audit target. |

The official screen-mode contract expressly permits a requested mode change to
fail for insufficient VDP memory, falling back first to the current mode and
then mode 1. It identifies mode 8 as 320×240×64 and mode 20 as 512×384×64.
A10-03/A10-05 must distinguish this documented stock behavior from truthful
Extender state publication, resource ownership, and the observed late-mode20
failure; the existence of a documented fallback is not a defect disposition.

## Build, artifact, production and installed identities

| ID | Record | Frozen identity and boundary |
|---|---|---|
| A10-ID07 | Native P4 build | Profile `p4-console`; build `build001-755d6f37-console-prelcd`; ESP-IDF 5.5.5 commit `b774170ff46c393eeb5e495ea37936038d3f4f4f`; Arduino-ESP32 3.3.11. Exact hashes and graph evidence are in `BASELINE.md`. |
| A10-ID08 | EMOS installed/audit image | `agon-emos-v0.1.23-b2026-09-28-02-43-51Z`, source `21a9ba27…`, 128,574 bytes, SHA-256 `8cbb123cfc9fb0dbfc6ff592ab03ccbb99fb469f8df9702f95c013f71eb08cfd`. This is development evidence, not selected production. |
| A10-ID09 | Installed P4 diagnostic | `build001-e7b35fd5-console-prelcd`, source `e7b35fd5…`, ELF identity prefix `887af158d`; restored and independently verified after the exact hybrid control. This is hardware-equivalence evidence, not the exhaustive source commit or production selection. |
| A10-ID10 | Selected production | `v0.1.0`, baseline `extender-installation-r02`, selected by `production/current.yaml` SHA-256 `6f75e49d701f32c5079e94da12c38271cfb004439d78e2417350c70d57bf0382`. It contains P4 r55 and EMOS v0.1.19 and remains a bounded comparison only. |
| A10-ID11 | Retained hybrid comparison | `uart-excom-console-r61-b2026-09-28-03-12-48Z`, factory SHA-256 `f794a8bba96f9afbfc1dae6eaa4554eb676880d76ffe74bda97bbebc7e160fea`. Use only for the already accepted A10-H02/A10-H04 comparison; no new historical search is authorized. |
| A10-ID12 | Deferred LCD delta | Preserved by LCD-001 outside the baseline. No LCD source or dependency is selected by `p4-console`; post-audit reintroduction owns its own diff and regressions. |

## Analysis-tool identities

| ID | Accepted A10-04 role | Identity at A10-02 freeze |
|---|---|---|
| A10-TID01 | Target build and host checks | Native GCC/IDF actions and validated database in `BASELINE.md`; existing host harnesses are inventoried by coverage row before execution. |
| A10-TID02 | LLVM static pass | LLVM/Clang-Tidy 23.1.2, ignored project-local binary SHA-256 `f14e3665520c2b38e01c1f36a8bf20e37f5b629fd796bfa275095d20b5a51bfd`. |
| A10-TID03 | Complementary C/C++ parser | Cppcheck 2.22.0, ignored project-local binary SHA-256 `6b532e512931187d9621a9be2618a6fc156f626ecfc90fbf88a39d59087c14e3`. |
| A10-TID04 | Python and shell pass | Accepted versions: Ruff 0.16.9, mypy 2.3.1, ShellCheck 0.11.0. Not yet provisioned in the project-local A10 tool area; installation and exact executable hashes remain A10-04 work. |
| A10-TID05 | Local semantic-policy pass | Semgrep CE 1.178.0 accepted but not yet provisioned. Only reviewed local rules with canaries and disabled network/metrics are authorized. |
| A10-TID06 | Dependency inventory | OSV-Scanner 2.6.0 accepted for offline use but not yet provisioned. Ecosystem coverage and unmatched pins must be reported. |
| A10-TID07 | Manual review | Accepted A10-01 risk set and official contracts; no executable can substitute for cross-repository ownership, allocation, rollback, assembly, or externally truthful state review. |

Tool absence at A10-02 is an installation-state fact, not a reduction of the
accepted A10-04 set. A10-04 must pin the remaining executables before running
them and must not update any globally installed developer package.
