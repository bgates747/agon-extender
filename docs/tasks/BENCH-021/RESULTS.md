# Olimex fast file transfer audit

The reviewed records contain no confirmed byte mismatch after a completed
upload with the matched PARLIO file service. They do contain reported transfer
failures and confirmed bad bytes in older raw parallel diagnostics. The
curated guide now states Smith's policy. The commissioned runner still uses
UART and reads back the staged inputs. Applying the policy to real jobs needs
a matching bench profile and runner change.

The review used the baseline frozen at
`469b233710291c84787006f74077e345b0ab0084` and the retained operator checkout
at `7637baa6a340b0ff3575ee1e3235b05af168819b`. This audit used files and source
only.

## What the retained runs show

| Evidence | What completed | Integrity finding |
| --- | --- | --- |
| [Wolf parallel upload, first repair](../PORT-008/UPLOAD-REPAIR-R01.md) | Two attempts stopped on extra VALID edges before activation. The retained 704,512-byte stage matched the corresponding source prefix. The filtered P4 replacement later completed two 2,625,992-byte uploads and a 65,537-byte control. | All three completed uploads matched an independent full GET. The partial attempts show a signalled failure. |
| [Wolf parallel upload, second repair](../PORT-008/UPLOAD-REPAIR-R02.md) | After thirteen completed uploads, the 70,472-byte job lost its session after HELLO and BEGIN. Target absent and partial file empty. Twenty same-firmware controls subsequently completed. | All twenty controls matched full GETs. The original cause remains open. |
| [Parallel upload development comparison](../PORT-008/REVERSE-UPLOAD-R01.md#final-finite-comparison--2026-11-03) | Ten UART and parallel upload/download comparison cases, through 1.1 MB. An earlier 1.1 MB transfer had been refused before activation even though the entire stored stage matched. | All ten comparisons matched. The earlier refusal was traced to the order in which the P4 sampled completion. |
| Moon Patrol CADENCE02, lease 182, operator record `CADENCE182-UNRUN.md` | Four full-arm files uploaded and matched their readbacks. The direct client then reused its session after staged jobs and got a stale-session refusal. Both arms were unrun. | Session management failure. The operator found no mismatch in the four files that completed. |
| [Curated bench rehearsal](../BENCH-020/EVIDENCE.md) and [worked example](../UPSTREAM-002.md) | Commissioned UART staging passed input readbacks. The old worked example produced a 21-byte result where 20 bytes were expected. Linked AgonDev `fputs` emitted a second LF and its corrected version produced exactly 20 bytes. | The output discrepancy came from the app's library. The fixture staged correctly. |
| [Older raw parallel echo control](../PORT-008/DATA-ONLY-CONTROL-R01.md) | Both legs of a 255-byte echo reported completion. The returned data first differed at offset 2. The follow-up capture saw an incorrect reverse D7 value on the wire. | Confirmed byte corruption on the raw experimental transport. That build did not use PARLIO for SD files and predates the matched file-transfer profile. |

The [staged UART transfer](../REMOTE-009/STAGED-RESULTS.md) and
[sequential reader](../REMOTE-009/DOWNLOAD-RESULTS.md) comparisons also report
exact bytes. These bounded records cannot prove an absence of corruption in
runs without a comparison. They support skipping routine content checks and
keeping diagnostic readback available after a failure.

## Curated instructions

The PARLIO trial and its VALID filter repair were already recorded on November
3 (`9e8a0dfc`). The initial rehearsal runner on November 16 (`60dd9f10`)
hard-coded the production `sdserve --fast` UART listener and added explicit
input comparisons. The rehearsal and subsequent curation (`aa89ad05`)
treated successful readbacks as part of the proven procedure. The cold run
qualified checkout, firmware changes, the fixture and handback under that
procedure. Its acceptance never checked the selected file carrier or the
absence of payload readbacks. The observed staging interval was 158.833 seconds
including independent readbacks. The records do not isolate their share of
that interval. [Rehearsal findings](../BENCH-019/REHEARSAL-R01-RESULT.md) ·
[Cold-run evidence](../BENCH-020/EVIDENCE.md#qualified-cold-run)

The sparse checkout starts at its local `AGENTS.md`, which links the bench
procedure and authoring guide. Before the correction, the procedure's staging
section and command table called for staged-byte verification. The general
execution procedure repeated that rule for staging and human-start readiness.
The authoring guide and example led to the same runner. The remaining curated
appliance, capture, reset, layout and completion documents contain no competing
routine fixture transfer directive. The reset and completion documents cover
startup state and changed firmware bytes separately.

The [bench procedure](../../operations/olimex-bench/README.md#stage-the-fixtures)
now owns the staging policy. The authoring and execution guides refer directly
to it, and the general SD operating guide refers commissioned jobs back to it.
The operator handles a failed transfer or test through the existing stop and
Smith notification route. The policy leaves generated result checks and
independent processor flash verification in place.

## Runner findings and disposition

| Source | Behavior observed | Disposition |
| --- | --- | --- |
| [`olimex_bench.py`, `LISTENER`, `Bench.listener`, `Bench.stage`](../../../scripts/olimex_bench.py#L167) | Both production and custom jobs start `EMOS sdserve --fast /` and use the direct `sdcard.Client`. Its `WRITE` loop sends 212-byte blocks over UART. The runner has no PARLIO selector or staged client. `stage` precedes every firmware install. | Carrier policy violation. Extender needs the matched parallel stack available at staging time and a runner route that requires it. A job's later firmware install cannot supply it to `stage`. |
| [`olimex_bench.py`, `Bench.stage`](../../../scripts/olimex_bench.py#L221) | Existing inputs are downloaded and compared before deciding whether to upload. Every staged input is then downloaded and compared again, including the generated EMOS command files and SD copies of the two ROMs. | Routine fixture upload verification violates the policy. The replacement route should use fresh job paths or reject an existing input by metadata, then use the successful activation receipt. Diagnose suspected corruption after a failure. Keep separate verification of actual ROM flash writes. |
| [`sdcard.py`, `connect`, `upload` and framing](../../../scripts/sdcard.py#L110) | `require_fast=True` refuses version 1. Version 2 uses a zero reserved field and fast uploads skip built-in digest and download checks. The generic checked CLI supports CRC and readback when called without `--fast`. | No wire CRC violation in the commissioned fast path. Keep the checked CLI for separately scoped diagnostics and avoid it in routine commissioning. |
| [`olimex_bench.py`, `pinned`, `listener`, result collection](../../../scripts/olimex_bench.py#L37) | The host hashes its local job and source pins. Each foreground listener session downloads and hashes existing `/autoexec.txt` and `/emos/sdserve.bin`. Collection retrieves the app's report and checks its expected lines. | Local pins identify commissioned inputs. The protected-file GETs validate bench state, add two reads per listener session and provide no proof about uploaded fixtures. Review their frequency separately from payload-validation removal. Prior result archiving and new result checks have their own purpose. |
| [`sdcard_staged.py`](../../../scripts/sdcard_staged.py#L81) and [P4 worker](../../../vdp/video/extender/storage/fast/engine.hpp#L82) | Staged transfers use checksum-free framing and no stored-payload readback. The worker selects PARLIO for nonempty uploads when HELLO advertises `0x80` and the P4 build supports it. Otherwise the current worker selects UART. A failure after PARLIO selection returns an error. Downloads use UART, and empty uploads use control records only. The staged client is absent from the curated path list. | A future commissioned parallel route must require the capability before mutation and record which carrier ran. Serialize metadata and staged jobs with deliberate session boundaries. A plain staged `put` does not by itself guarantee PARLIO. |
| [`olimex_bench.py`, phase execution](../../../scripts/olimex_bench.py#L382) | The parent retains phase and child-exit evidence. The runner does not raise the human attention dialog. | The operator follows the documented stop rule and alerts Smith. The scheduler remains outside troubleshooting. |

The [parallel trial selector](../../mainboard-sd-parallel-trial.json) identifies
P4 `5db0c0a0`, EMOS `855aa732` and `/emos/sdpu01.bin` `f60f244f`. Its listener
command is `EMOS sdpu01 --fast --parallel /`. The curated production images,
P4 `d9bcb1a2` and EMOS `a25f1612`, differ from that trial.

Extender rehashed the production P4 application against the retained owner
build `net-003-r02-b2026-11-06-09-03-07Z`. Its build manifest has
`parallel_upload_candidate: false`, which excludes the SD PARLIO sender.
The production EMOS ROM includes the SD upload gateway and receiver. Its
retained link map matches manifest SHA-256 `11a296f0…` and contains
`emos_sdlink_gateway` and `emos_parallel_upload_begin/read/end`. EMOS source
`2c79c600` enables `EMOS_PARALLEL_UPLOAD=1`. The `network_parallel` setting
controls application networking. The earlier audit conflated those features.

The P4 build and default listener selection explain the missing production
file route. Extender still needs to qualify the current EMOS with a
PARLIO-enabled P4 and matching listener before commissioning that route.
The reviewed evidence establishes no need to replace EMOS just to enable
the feature. The download carrier and multi-input runner remain implementation
work.
