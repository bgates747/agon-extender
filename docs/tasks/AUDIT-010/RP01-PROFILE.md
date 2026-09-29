# AUDIT-010 RP01 — Minimal product-development profile

## Executive summary

RP01 reduces the maintained native `p4-console` definition set from 21 to ten
explicit product requirements. It removes three timing/refresh diagnostics and
eight rejected/no-op experiments from ordinary builds while retaining the
selected stock-shaped display owner, browser/video services, SD/WebDAV,
keyboard, telemetry, one-millisecond network poll, the snapshot mutex safety
correction, bounded snapshot lookahead and packed-row conversion.

The 33 selected translation units and eleven forbidden alternative-display
units do not change. The profile records diagnostic and rejected definitions as
disjoint policy, and both the builder and graph validator reject overlap or an
excluded definition on an actual compile action. No new maintained diagnostic
profile is created: the removed probes remain default-off source facilities and
frozen task evidence, not an accepted recurring configuration.

State: implementation and host/build validation complete; Author acceptance
pending before RP02.
Finding: `AUDIT-010-F005`. Plan item: `A10-RP01`.

## Definition disposition

| Definition | Disposition | Reason |
|---|---|---|
| `AGON_EXTENDER_P4_BOOT=1` | Required | Selects the P4 compatibility and boot boundary throughout the retained VDP code. |
| `AGON_EXTENDER_STOCK_RUNTIME=1` | Required | Selects the sole stock-shaped product display owner frozen by the audit. |
| `AGON_EXTENDER_SD_SERVICE=1` | Required | Enables the maintained EMOS/P4 SD service integration. |
| `AGON_EXTENDER_STAGED_WEBDAV=1` | Required | Enables the maintained staged WebDAV service; its startup defect remains separately owned by F003/RP10. |
| `AGON_EXTENDER_REMOTE_KEYBOARD=1` | Required | Enables the accepted browser/Extender keyboard path. |
| `AGON_EXTENDER_TELEMETRY=1` | Required | Enables the active P4/EMOS status and admission telemetry contract. |
| `AGON_EXTENDER_VIDEO_POLL_MS=1` | Required | Makes the selected one-millisecond network worker poll explicit instead of inheriting the ten-millisecond source default. |
| `AGON_EXTENDER_SNAPSHOT_MUTEX=1` | Required | Retains the blocking mutex correction for the demonstrated priority-inversion spin hazard. |
| `AGON_EXTENDER_SNAPSHOT_LOOKAHEAD=1` | Required | Retains the bounded one-frame, demand-driven lookahead with measured output benefit and fixed slot ownership. F002/RP09 may later revise allocation policy, not silently remove demand semantics here. |
| `AGON_EXTENDER_PACKED_ROW=1` | Required | Retains byte-equivalent direct RGB222 row production and its measured reduction in snapshot work. |
| `AGON_EXTENDER_VIDEO_TIMING=1` | Diagnostic, default off | QUAL-003 aggregate timing instrumentation; not ordinary product behavior. |
| `AGON_EXTENDER_REFRESH_TRACE=1` | Diagnostic, default off | QUAL-003 refresh enqueue/completion tracing; not ordinary product behavior. |
| `AGON_EXTENDER_VIDEO_DISPATCH_TIMING=1` | Diagnostic, default off | HTTP dispatch timing instrumentation; not ordinary product behavior. |
| `AGON_EXTENDER_CANARY=1` | Rejected from `p4-console` | Historical build label with no active source consumer; native build identity is generated separately. This does not alter the recovery profile. |
| `AGON_EXTENDER_INTERNAL_POOLS=1` | Rejected experiment | Bounded mode20 pool experiment did not establish a consistent product benefit and changes allocation policy needed by later F001/F002 repairs. |
| `AGON_EXTENDER_DRAW_FOUR=1` | Rejected experiment | Four drawing opportunities did not repeatably close the timing gap. |
| `AGON_EXTENDER_DRAW_TWICE=1` | Rejected experiment | Conflicted with `DRAW_FOUR`; source precedence silently ignored it. Twice-per-frame testing also did not establish a retained product requirement. |
| `AGON_EXTENDER_OUTPUT_ROW_PAIR=1` | Rejected experiment | Row-pair lock batching did not establish parity and changes native exclusion granularity. |
| `AGON_EXTENDER_INTERNAL_GAME_MODE=1` | Rejected experiment | Mode-specific internal-memory eligibility was part of the inconclusive allocation experiment. |
| `AGON_EXTENDER_INTERNAL_FRAMEBUFFER=1` | Rejected experiment | Internal framebuffer selection did not consistently improve spacing and changes allocator behavior. |
| `AGON_EXTENDER_OUTPUT_BELOW_PARSER=1` | Rejected experiment | Priority-two output scheduling did not produce a repeatable product benefit; ordinary source policy is no longer hidden by this experiment. |

## Source and dependency disposition

`A10-RP01-SRC01` — All 33 `p4-console` translation units remain required. RP01
does not add, remove or substitute a display, network, storage, input, browser
or vendored implementation.

`A10-RP01-SRC02` — All eleven forbidden sources remain rejected from the
ordinary profile. They are the mutually exclusive nonrelease display family
owned by RP02; RP01 does not decide their final archive/removal boundary.

`A10-RP01-SRC03` — Embedded assets, include paths, exact managed-component
versions, SDK configuration, partition table, DSP derivative and task-context
selection remain unchanged.

`A10-RP01-SRC04` — No named diagnostic profile is retained. The three
diagnostic definitions remain compilable default-off source seams and frozen
historical evidence. A future recurring diagnostic requires its own explicit
profile/task contract instead of entering `p4-console` by accumulation.

## Regression manifest

`A10-RP01-T01` [x] The JSON authority parses and the native-profile unit tests
prove the exact ten required, three diagnostic and eight rejected definitions
with no duplicates or overlap.

`A10-RP01-T02` [x] Builder policy validation rejects a definition classified in
more than one group and unsafe definition syntax.

`A10-RP01-T03` [x] A fresh `UNVERSIONED-DO-NOT-DEPLOY` native `p4-console` build
passes the actual-action graph validator: 33 selected sources compile once,
eleven forbidden sources do not compile, required definitions reach every
selected action and all diagnostic/rejected definitions are absent.

`A10-RP01-T04` [x] The linked native build retains the required browser/video,
SD/WebDAV, remote-keyboard and telemetry service symbols/definitions and one
stock-shaped display family.

`A10-RP01-T05` [x] Embedded browser/codec validation passes the actual built
assets and all retained codec vectors.

`A10-RP01-T06` [x] Existing native build, USB source-selection and applicable
profile/asset tests pass. Documentation identifies `p4-console` as minimal and
the historical PlatformIO path as non-authoritative.

`A10-RP01-T07` — No hardware build, flash, reset or physical run is required for
this build-authority item. RP01 makes no claim about target performance or mode
behavior; those remain with their later finding owners.

## Result

The ignored candidate output is
`agents/builds/audit010-rp01-minimal`. It is explicitly
`UNVERSIONED-DO-NOT-DEPLOY`, was built from freeze commit `937abfc0` plus the
dirty RP01 candidate, and was not flashed.

| Evidence | Result |
|---|---|
| Profile-policy/native/USB tests | PASS; nine native/USB checks, including exact required/diagnostic/rejected sets, overlap rejection and unsafe-definition rejection. |
| Native build and action graph | PASS; 33 selected sources compiled once, eleven forbidden sources absent, zero required-definition misses and zero excluded-definition hits. |
| Profile authority SHA-256 | `8e77b2ce6a27def7ee1f2d1a2e7659f98eb5463d318b377ff013e938cb7e98f2` |
| Application image | 1,576,352 bytes; SHA-256 `be3c67bb7e1d43e26c5ba3f24f06de94db15cdad053bec8c396531c0bde54918` |
| Offset-zero factory image | 1,707,424 bytes; SHA-256 `bcb57356c440171791bab2d6a46aec87550122bba388bff4b542dd0a59387197` |
| Linked ELF | 34,157,280 bytes; SHA-256 `f2e5ce2b93aae8253136706885fc92a9f5ef33dc233d172fa73340761401c79a` |
| Linked service/display inspection | PASS; stock display, WebDAV, SD, remote-keyboard and telemetry symbols present; alternative display-family symbols absent. |
| Embedded browser/codec suite | PASS; exact embedded assets, compressed negotiation and 48 vectors across EVF1/EVP1/EVQ1/EVR1. |
| Neighbor regressions | PASS; mode lifecycle, video timing seam, remote keyboard, telemetry, SD service, WebDAV runtime/adapter and RGB222/snapshot C++ checks. |

`A10-RP01-L01` [x] — The broader `browser_rgb222_test.py` initially reached and
passed its C++ RGB222/snapshot/network checks, then timed out because it clicked
`#demo` while the enclosing diagnostics `<details>` was closed. The Author
directed correction because a broken regression would affect the ongoing audit.
The test now exercises the user-visible diagnostics summary before clicking the
pattern control, matching the already-correct video UI test, and asserts the
current separate surface geometry and RGB222 state fields instead of the former
combined status literal. The companion video UI oracle now validates the `/video`
path and accepted `rle2=1`/`packed=2` negotiation parameters instead of requiring
the URL to end before its query. Both complete browser suites pass; no product
asset or behavior changed.

No physical hardware state changed. RP01 now stops for Author acceptance under
`A10-RP-C02`; RP02 has not started.
