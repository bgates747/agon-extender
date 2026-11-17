# UPSTREAM-002 — Correct AgonDev fputs newline handling

**Status — Patched original fixture passed on Olimex on 2026-11-17.**
The host regression and physical single-LF comparison pass.
Upstream submission remains pending.

The original fixture supplied `"Result file example\n"` to `fputs` and
the hardware result ended in `0a 0a`. Its linker map identifies
`libagon.a(fputs.o)`. Disassembly of the installed object shows a call
to `fputc(0x0a, stream)` after it reaches the string terminator. The
worked example switched to `fprintf` and passed with one trailing LF.
See the [Olimex qualification record](BENCH-020.md).

## Subtasks

- [x] **UPSTREAM-002-01.** Record the affected AgonDev SDK build and trace `fputs.o` to the owning
  source in the [AgonDev upstream repository](https://github.com/AgonPlatform/agondev)
  or the C library repository it uses. Check the current upstream revision
  and existing issues or patches before choosing the PR target. Confirm
  that the defect comes from the library routine linked into the fixture.

- [x] **UPSTREAM-002-02.** Reproduce it with a minimal Agon program that writes a string to a file
  and compares the saved bytes. Retain the build identity, linker map and
  failing output. Confirm whether the current upstream version reproduces it.

- [x] **UPSTREAM-002-03.** Patch the owning C library source on a focused branch in Smith's AgonDev fork. Make
  `fputs` write the supplied bytes through the string terminator, excluding
  the terminator itself, and preserve standard success and write-error
  reporting. Verify that `puts` still appends its newline. Keep the
  qualified Extender fixture and installed SDK as the comparison baseline.

- [x] **UPSTREAM-002-04.** Build the patched library and link the reproducer against it. Verify
  byte-for-byte output for an empty string, a string without a newline,
  and a string already ending in one newline. Check the write-error path
  and run the owning repository’s relevant tests. Record the affected
  and fixed results and which environment produced them.

- [ ] **UPSTREAM-002-05.** Submit the patch and regression coverage to the owning upstream
  repository. In the PR, describe the observed extra LF, the standard
  behavior, the affected revision, and how to reproduce and verify the
  fix. Record the PR link and validation results here.

- [x] **UPSTREAM-002-06.** Create or verify Smith's GitHub fork of
  AgonPlatform/agondev and use a separate project-owned checkout. Configure
  the fork as `origin` and AgonPlatform/agondev as `upstream`. Keep the
  existing upstream reference checkout read-only and record the verified
  fork and checkout identities.

## Fork and local SDK releases

GitHub identifies [bgates747/agondev](https://github.com/bgates747/agondev)
as a fork of AgonPlatform/agondev. The project-owned sibling `agondev`
checkout uses the fork as `origin` and the parent as `upstream`. The
`upstream` remote is configured for fetch only. The checkout, fork
`master`, and parent `master` all resolved to
`80a2f3db67bda0224e725e90226d0cfe4d0e1f74` at setup.

Base each upstream PR on a focused fork branch from `upstream/master`.
Maintain a separate deployment branch for the exact patch set approved for
local use. Before selecting a fork-built SDK for deployment, record the
upstream base, fork commit, build configuration, and artifact hashes. Keep
the prior SDK available for comparison and rollback. Once an upstream SDK
release contains a local fix, remove the corresponding carried patch when
updating the deployment branch.

## UPSTREAM-002-01 evidence

The original worked example's job manifest pins `OLIMTEST.bin` at
SHA-256 `775b974e4d725a2f7478e8f28fc0301e9d80f23b7528a2e02e3414d890324038`.
That hash matches the retained build. The operator log records an AgonDev
SDK whose `agondev-config --version` reports `1.0`; the archive and member
hashes identify the relevant installed bytes more precisely than that
version string.

| Retained artifact | Identity |
| --- | --- |
| `build/bin/OLIMTEST.map` | SHA-256 `aad11a440c20f9c194eef64b1537eba5f9f0097db60c95ade3cb640b8ceafa6b`. Resolves the fixture's `_fputs` to `libagon.a(fputs.o)` at `0x0404c7`, size `0x62`. |
| Installed `libagon.a` | SHA-256 `5de7878342ab6780593fbf8d54d8005960e2471bd0e34c0e307fbcfe42fef28a`. |
| Extracted `fputs.o` | SHA-256 `9669584e226fb6c764030ed48ed1b520344d57861f17ff8e93517b5f24c23d54`. Its 98 `.text` bytes match the linked image after resolving the three call relocations from the linker map. |
| `evidence-retry/run/result.txt` | 21 bytes, exactly `Result file example\n\n`. |
| `evidence-corrected/run/result.txt` | 20 bytes, exactly `Result file example\n`, using the [worked example's `fprintf` implementation](../operations/olimex-bench/example/src/main.c). |

In the linked binary, the branch taken at the string terminator reaches
`0x04050b` with `0x0a` loaded as the character argument. The call at
`0x04050d` writes it through `_fputc` at `0x040529`. This matches the
unconditional newline call after the character loop in the library source.

The owning repository is AgonPlatform/agondev. Its default branch and
[inspected upstream commit `80a2f3db`](https://github.com/AgonPlatform/agondev/blob/80a2f3db67bda0224e725e90226d0cfe4d0e1f74/src/lib/libc/fputs.c#L26-L34)
both returned the same `src/lib/libc/fputs.c` blob
`72e4048794be17214691c6a4a755fac168430ab8`. The local upstream `v0.22`
tag resolves to the same source blob. This establishes source equivalence
for this file. The full source revision used to build the installed SDK
archive remains unverified. GitHub issue and PR searches in that repository
for `fputs` and `"extra newline"` returned no matches on 2026-11-17.

Target AgonPlatform/agondev's `master` for the eventual PR. Its separate
[`puts.src`](https://github.com/AgonPlatform/agondev/blob/80a2f3db67bda0224e725e90226d0cfe4d0e1f74/src/lib/libc/puts.src)
already emits its own newline. The regression should cover both routines
and preserve `fputs` returning `EOF` when a character write fails.
This tranche examined retained hardware evidence and upstream source.
The standalone reproducer and execution against an upstream build belong
to UPSTREAM-002-02.

## Fork patch and validation

The [fork commit `89b4ff1`](https://github.com/bgates747/agondev/commit/89b4ff1bd190fbf214df9eb628eef1aa562c6882)
removes the unconditional newline from `fputs` and makes AgonDev's
`fileio` example write its line separator explicitly. The host regression
failed against the parent source and passed against the patch for empty
input, plain input, input ending in LF, and an `EOF` result on a
read-only stream. The host regression uses host stdio streams and
`fputc` to exercise the AgonDev `fputs` implementation.

The Pi build replaced only `fputs.o` in a copy of the installed AgonDev
archive and relinked the original `OLIMTEST` source without edits. The
unpatched rebuild matched the retained fixture byte for byte. The patched
linker map selects the replacement object and the original `puts.o`
member remains byte-identical. The updated `fileio` example also built.
This is a test SDK overlay. Selecting a fork-built SDK for deployment
remains separate work.

| Build artifact | SHA-256 |
| --- | --- |
| Patched archive | `50c6e6e265521caf7f7af2eda115b6aa3c68c5da8577b4e40a49df1909be28ad` |
| Patched `OLIMTEST.bin` (2,674 bytes) | `38b3f1f8eada422bdc234ba432bab5a82665dd1ac266e1b89a44b7c0b8844b79` |
| Patched `OLIMTEST.map` | `c1fe0f25f461ed7464db7f7664e034a63ae19e52e04ee0985541577a5a790d83` |

The Agon validation should run the relinked original fixture once and
collect the result file. The fixture uses `fputs` for the file and
`puts` for the console status. Require `OLIMTEST PASS`, a working CLI
on return, and exactly 20 result bytes with a single trailing `0a`.

The fresh GPT-6.1 Sol Light operator completed that physical check with one
explicit LOAD/RUN. Extender independently rechecked the retrieved bytes
against `b"Result file example\n"` and reviewed all three phase receipts.
Stage, run, and handback each returned zero with the worker joined and no
live process-group members. Handback records a working CLI, offline listener,
idle transfers, and free serial handles. The result SHA-256 is
`ab0d8b9c5c3da3b3a2f7263d85c7b8724f065bbe5d29d3f3b694742643555810`.
Empty-input, plain-input, and write-error coverage was performed on the host.
The hardware run covered the original LF-terminated file and console status.
The operator retained the full log and independent comparison in the ignored
task evidence directory. The operator reported successful routine check-in.

## Operator result notification follow-up

- [ ] **UPSTREAM-002-07.** Investigate the result sender's two automatic
  approval rejections. The reviewer rejected private paths and evidence in a
  report to the commissioning Extender chat, including after the operator
  retrieved the commissioning instruction and verified CHAT-AUTH-001.
  Smith's subsequent direct approval in the operator chat allowed the same
  sender to succeed. Compare actual retained sender calls and approval
  settings with the preceding cold run before attributing a cause. The
  preceding operator log contains no matching rejection narrative, which
  alone does not establish why the review outcomes differed. Preserve the
  evidence before deleting the temporary operator chat.

### UPSTREAM-002-07 execution amendment — 2026-11-17

Smith directs Extender to resolve the result-reporting failure, including a
specific standing authorization where needed. The retained failure concerns
the immediate send-to-thread tool and project paths, hashes and bench evidence
sent to the commissioning Extender chat.

- UPSTREAM-002-08 [ ] Correct Extender's local reviewer environment profile
  to identify Smith-owned project chats as trusted internal destinations for
  routine project results and evidence. Preserve the general reviewer policy
  and apply the same explicit scope to agent startup guidance.

- UPSTREAM-002-09 [ ] Verify configuration support and the policy's effective
  load, then use a fresh operator context to report the already-retained
  fixture result through the same immediate sender. Retain receipt, settings,
  payload and any rejection. This verification requires no new bench work.

- UPSTREAM-002-10 [ ] Compare the previous retained sender outcome, document
  observed differences and limits, publish the maintained correction, and
  delete the temporary verification chat after saving its evidence.

Keep this amendment limited to routine coordination among Smith's own project
chats. Result payloads may include project paths, hashes, run status, commands,
logs and evidence references needed by the receiving project owner. Credentials,
authentication tokens and third-party destinations retain their existing rules.
The task is complete when a fresh operator sends this class of report through
the original tool without a per-message human intervention and the effective
configuration and instructions are retained for future operators.
