# Legacy finite-job qualification

The Author released the bench for autonomous qualification. Local target and host
checks pass. The first physical tranche is limited to automatic external jobs in
Legacy mode; ExCom and application-origin staged file jobs remain unfinished.
Production v0.1.0 is not replaced by these candidate builds.

## Selected candidates

| Component | Identity | Source |
| --- | --- | --- |
| Resident EMOS | agon-emos-v0.1.22-b2026-09-28-00-04-04Z | agon-emos 70a4908 |
| Finite utility | sdjob-v0.1.0-b2026-09-27-23-45-52Z | agon-emos e6a23cb |
| P4 | uart-excom-console-r60-b2026-09-28-00-35-51Z | Extender c820550c; explicit staged-WebDAV export |

Registry r118 and these draft identities use the Author's standing version
preapproval. No new production version/tag is selected.

## Local evidence

| Check | Result and boundary |
| --- | --- |
| Actual eZ80 utility + actual P4 Peer | PASS: HELLO/STAT/READ, exact bytes, FINISH/CLOSE, return to prompt |
| Missing utility, absent peer, corrupt reply, key-before-grant race | PASS in maintained UART-peer emulator harness |
| EMOS tests and linked guards | PASS: 129 tests, ABI/VDU/UART/parallel/keyboard checks |
| Target firmware | 128,397-byte corrected EMOS ROM; identified 23,230-byte finite utility; P4 clean exported build passed |
| Actual HTTP/Channel/Peer/finite utility/checked engine | PASS with host FatFS/gateway substitutions and sanitizers |
| Adapter and media tests | PASS; target-object-only test skipped without optional compiler setting, superseded here by complete identified P4 build |

The broad historical `prepare_boot_review.py` gate encountered two independent
local setup problems: generated worktrees were not ignored, and its shared
emulator profile expects a different pinned runtime from the current system
installation. Generated worktrees were preserved and locally excluded; builder
unit tests passed using an isolated pinned reference. Target build and owner
linked checks passed separately. The actual eZ80 runtime check uses the retained
project UART harness. No blanket graphical emulator qualification is claimed;
no shared emulator installation was changed to force that result.

## Completion receipt correction

EMOS sends a new HELLO immediately after resident CLOSE. P4 previously reset its
phase to idle on that HELLO, potentially hiding a completed result from its HTTP
worker. P4 now retains the closed receipt until the worker retires it. A regression
includes HELLO and POLL arriving before worker retirement. It does not replay an
operation or treat loss of a live grant as success.

## Physical evidence

The bounded Legacy physical tranche below has completed. Exact manifests, logs and rollback bytes are
retained under ignored `agents/remote005-webdav-runtime`. The actual incoming P4
full flash was saved before replacement; mainboard ROM and unchanged startup were
also preserved. This is candidate evidence, not production acceptance.

The first physical sequence exposed a handback gap: HEAD of an absent path
returned 404, then an immediate MKCOL received 503. A separately spaced diagnostic
created the directory and activated a checked 4096-byte upload, but its next GET
also encountered busy. These are failures, not native-client qualification.

Two corrections are now regression-tested: resident EMOS filters stale control
operation/session/sequence before copying into its one reply slot (CRC remains
foreground); P4 completes error-response cancellation before sending headers and
waits up to 200 ms for the previous job's idle return before responding. That wait
does not admit/queue a new request, retry a mutation or change a known committed
result when a human/application takes control. The cross-component host test no
longer waits artificially between requests. Corrective builds retain distinct
build timestamps; original candidate evidence is preserved.

Author observed an invalid-command error immediately after the EMOS flash/reset.
The whole ROM subsequently matched the candidate and unchanged startup was read
back. The first listener invocation failed; a later settled invocation succeeded.
The exact rejected command is not known. Keyboard readiness alone is insufficient
as a CLI-ready deployment gate. Do not classify this as a corrupt flash or silently
reissue FLASH. The next deployment waits for an admitted read-only WebDAV request
before injecting post-boot commands.

## CLI error reporting observed during physical tests

The Author observed three `EMOS backend unavailable` messages separated by many
linefeeds. Source inspection confirms that the finite utility returns MOS error
35 on cancellation/failure; the resident main loop prints that result using the
ordinary MOS error formatter. The P4 adapter currently cancels admitted jobs even
for ordinary HTTP results such as missing-file 404 and overwrite-precondition
412. Both occurred in the retained run, alongside a later failed directory
request. Thus this message alone does not establish that the P4 disconnected.
The exact three screen messages are not individually correlated to requests.

Expected HTTP rejections need clean job completion rather than a generic CLI
backend-failure report when no transport failure or unfinished write exists.
Actual transport failures must remain distinguishable. Repeated prompt/linefeed
output during automatic jobs also requires correction before ordinary-use
acceptance; the Author's report is retained as a usability failure.

The corrected hardware pair passed checked 4096-byte upload/download, HEAD,
byte-range retrieval, overwrite rejection, COPY and MOVE. A following GET still
returned 503, and a repeated tiny MOVE/GET test reproduced that admission failure.
Thirty consecutive HEAD requests passed. These results do not constitute full
suite acceptance. Native Linux discovery also rejected the missing DAV header;
a local diagnostic proxy supplying a non-class capability URI allowed mount and
listing, but direct native-client qualification remains open.

## September 28 timing correction under qualification

A host regression reproduces spurious expiry when the UART caller supplies a
one-millisecond older sample than the HTTP caller that just activated a grant.
Unsigned subtraction interpreted that ordering as nearly 49 days elapsed. The
P4 now samples shared-queue time inside the lock and bounds elapsed ordering
across older samples and clock wrap. Real five-second expiry remains tested.
This is a demonstrated code defect; hardware causality awaits the corrected run.
Normal missing-path and precondition responses now finish their admitted job
cleanly instead of cancelling it. Incomplete stages still fail terminal checks.

## Corrected physical results — September 28 UTC

| Check | Outcome | Boundary |
| --- | --- | --- |
| P4 deployment | PASS | Independent byte verification, matching boot identity and USB host readiness; prior image retained |
| EMOS installation | PASS | Corrective v0.1.22 full 128 KiB ROM readback matches; utility bytes verified earlier |
| Consecutive file operations | PASS | 16 requests; checked 4096-byte upload/download, HEAD, range, overwrite rejection, COPY, MOVE, listing, directory creation and recursive deletion |
| Repeated MOVE/read handback | PASS | 20 consecutive pairs plus setup (42 requests), 35.71 seconds host wall time; no retries or client delays |
| Partly typed CLI | PASS | External operation rejected; Escape returns to successful idle admission |
| Interrupted upload | PASS | Client EOF does not publish an incomplete destination; subsequent request works |
| Concurrent HTTP worker | PASS | Competing request rejected; recovery after the first connection closes |
| Manual listener ownership | PASS | Automatic request rejected while manual listener is active; manual byte readback and unchanged startup verified |
| ExCom boundary | PASS for rejection only | Automatic file request refused; return to Legacy restores access. ExCom file service remains unimplemented |
| Native Linux GVfs/GIO | PASS for bounded subdirectory smoke | Direct mount/list/read/write/rename/delete/mkdir/rmdir, exact file readback; no diagnostic proxy |
| Root PROPFIND | FAIL | Depth 0 and 1 return 500; manual root enumeration succeeds. Root metadata handling remains open |

The basic operation sequence took 41.74 seconds summed across individual HTTP
requests, measured by the host monotonic clock. This excludes deployment and
later fault/native tests and is not a throughput-optimization result. Detailed
request durations, local output, identities, rollback bytes and file hashes are
retained in the ignored runtime qualification directory.

Hardware also exposed a distinct response/resource-release race: the next request
could reach the acceptor after the client received its preceding response but
before the old worker released its media lease. This produced the bare worker
503 response. A one-byte completion barrier now releases the final response byte
only after storage teardown and worker admission release. It does not queue or
replay requests. Partial-write and completion-order regressions pass. The corrected
basic run required neither client sleeps nor mutation retries.

Native discovery uses the documented extension capability URI rather than claiming
DAV class 1/2/3. GVfs emitted a missing `standard::size` metadata warning during
its successful smoke; visual file-manager acceptance and broader metadata behavior
remain unqualified. Root access must be fixed before claiming the whole-card
native workflow works. No macOS Finder or Lenovo GUI acceptance is claimed.

The CLI linefeed cause is identified separately: `mos_input` prints a newline for
its private service return and the next main-loop iteration prints another prompt.
No new EMOS UI change was flashed in this correction. Successful automatic jobs
still disturb the CLI presentation; that remains an A11 usability follow-up.
