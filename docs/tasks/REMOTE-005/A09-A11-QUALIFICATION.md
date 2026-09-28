# Finite-job qualification — Legacy and ExCom

The Author released the bench for autonomous qualification. Local target and host
checks pass. The latest bounded physical tranche covers automatic external jobs
in Legacy and negotiated ExCom. Application-origin staged file jobs and broader
fault/native-client acceptance remain unfinished.
Production v0.1.0 is not replaced by these candidate builds.

## Selected candidates

| Component | Identity | Source |
| --- | --- | --- |
| Resident EMOS | agon-emos-v0.1.22-b2026-09-28-02-01-12Z | agon-emos 1e3373f |
| Finite utility | sdjob-v0.1.0-b2026-09-28-01-41-18Z | agon-emos dd3527e |
| P4 | uart-excom-console-r60-b2026-09-28-02-19-56Z | Extender e2193f07; explicit staged-WebDAV export |

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

## Root and CLI follow-up — candidate prepared September 28 UTC

The Author released the bench again and explicitly allowed replacing the TRS-80
composition. Its actual full P4 flash was saved before restoring the verified
Extender r60 candidate; no TRS-80 source was changed.

Root failure is the checked engine's incorrect use of stock `ffs_stat("/")`:
official MOS v3.0.2 FatFS intentionally rejects the origin directory. The engine
now opens/closes that directory before reporting root metadata. The host FatFS
substitute now reproduces the upstream rejection; the new root regression fails
on the old engine and passes with the correction. No stock FatFS patch is needed.

Resident EMOS now handles private service returns inside its CLI input wrapper,
after editor storage has been freed, without printing another newline/prompt on
success. Errors still print a diagnostic and fresh prompt. Public editor and
ordinary command CR/ESC behavior are unchanged. The compiled wrapper regression
covers repeated jobs and an error followed by recovery. Actual eZ80 execution
with the new ROM and utility passed FINISH/CLOSE and exactly one retained prompt.
132 owner tests and linked firmware checks pass; paired host file-engine checks
also pass. Physical deployment/results follow separately below.

### Root/CLI deployment and results

The updated resident ROM is 128,406 bytes; full 128 KiB physical readback matches
its padded image exactly. The identified finite utility is 23,325 bytes and was
read back byte-for-byte after installation. P4 is unchanged from the corrected
r60 build in the selected-candidate table. Mainboard startup and manual listener
remain unchanged. The previous ROM, utility and actual incoming P4 image are
retained for rollback.

| Renewed check | Result |
| --- | --- |
| Root PROPFIND, Depth 0 and 1 | PASS; root metadata and full immediate-child listing |
| File/directory operation sequence | PASS; 18 HTTP requests including root, 45.36 seconds summed host request time; exact payload/range checks |
| Partial CLI, interrupted upload, worker contention, manual listener ownership | PASS; subsequent eligible operation succeeds |
| ExCom boundary | PASS for refusal and Legacy recovery only; not ExCom transfer support |
| Linux native root mount | PASS; direct GVfs/GIO root mount/list and test-subdirectory read/write/rename/delete/mkdir/rmdir; exact 4096-byte download |
| Silent CLI continuation | PASS in actual eZ80 execution (one prompt after a completed job) and compiled wrapper test (success/error/resume); same ROM physically read back |

The prior root failure is closed for this candidate. The CLI newline correction
is installed; separate visual human acceptance is not claimed. GVfs still emits
the previously observed missing-directory-size metadata warning, despite passing
operations. GUI acceptance on each desktop, broader interleavings/media faults,
ExCom and application-origin integration remain open. No production promotion.
Final state: normal Legacy prompt, ready neutral Extender keyboard, manual
listener stopped, temporary native mount and test session closed.

### Next bounded A11 tranche: negotiated ExCom finite jobs

Frozen work contract: enable the existing external finite job in ExCom after
Legacy capability negotiation. P4 consumes F6 only at the retained VDU 23,0
command boundary, drains invalid declared payloads without interpreting them as
VDU, and queues 8D replies through its sole console UART owner. EMOS admits the
finite utility in ExCom only with the negotiated capability; manual listener and
application-owned leases remain Legacy-only in this tranche. Successful ExCom
completion retains the negotiated incarnation for subsequent jobs; a transport
failure invalidates it and requires Legacy renegotiation. No implicit mode
switch, parallel transport, production promotion or new file operations.

Research basis: official `agon-docs/docs/vdp/System-Commands.md` defines the
VDU 23,0 dispatcher; its `VDU-Commands.md` line-pattern command VDU 23,246 is a
different namespace. The maintained `vdu_sys.h` supplies the actual command
boundary, while `console_hardware.inc` currently recognizes F6 only in Legacy.
The admission contract already assigns capability bit 1 to active ExCom framing.

Validation: owner host tests for capability/ownership/completion/failure;
bounded packet-consumption regression and P4 build; paired actual firmware on
the authorized bench, repeated ExCom root/file operations followed by Legacy
recovery, preserving startup and rollback. Broader A11 faults and A12 desktop
acceptance remain open. Record actual results rather than inferring them from
compilation or Legacy tests.

### Negotiated ExCom results — September 28 UTC

The selected pair above is installed. EMOS is 128,493 bytes (+87 from the prior
candidate); its entire 128 KiB ROM readback matches, SHA256
`2faea97b8044eadcaed7d93704e35e7ee9119c0887698a3a10a20f83122968f9`.
P4 was backed up, flashed, independently verified and its boot identity checked.
The finite utility and 38-byte startup file are unchanged. Production remains
unchanged. Exact deployment receipts, scripts, screen-text samples and result
JSON are retained in the ignored runtime hardware silo (`excom-deployment`,
`peer-p4-excom`, `excom-basic-results.json`, `excom-abort-observations.json` and
`excom-recovery-results.json`).

| Check | Result |
| --- | --- |
| Target builds / EMOS qualification | PASS; 132 owner tests plus linked guards; exported P4 build |
| Portable active F6 reader | PASS under sanitizers; all 256 declared lengths and every truncated prefix; following VDU remains untouched |
| ExCom root/file/directory suite | PASS; 18 HTTP requests, 44.88 seconds summed request time, exact 4096-byte payload/range checks, protected overwrite, COPY/MOVE and recursive DELETE |
| Partial CLI line | PASS; 503 while typing, 200 after Escape clears line |
| Client EOF during upload | No destination created; cancellation invalidates ExCom admission, subsequent request returns 503 |
| Explicit Legacy recovery | PASS; absent incomplete destination confirmed, existing file unchanged, ExCom re-entry and five further exact reads pass |
| Keyboard/display coexistence | PASS; sampled EDP text contains injected before/after markers, including after the abort; no implicit mode change |
| Final state | Legacy idle admission passes; Extender keyboard ready/neutral, zero queued/held events; manual listener offline |

The initial abort check expected immediate ExCom recovery and failed with 503.
This is retained as a limitation, not disguised as a passing immediate-recovery
test: the current finite utility reports cancellation as unsuccessful completion,
so EMOS deliberately invalidates the negotiated admission. This includes a client
EOF even before destination activation, not only physical UART failures. EMOS
prints `EMOS backend unavailable` but remains responsive; explicitly return to
Legacy to renegotiate, then ExCom may be selected again. No automatic retry or
mode switch was added. Friendlier cancellation recovery can be considered within
the remaining A11 interruption work; this bounded tranche does not close A11.
Application-origin integration, broader media faults and native desktop acceptance
are still open. No browser streaming performance or human visual acceptance is
claimed by these checks.

### Clean cancellation contract — A11 continuation

Author authorized implementation and the bench remains available. P4 may request
an orderly stop after a client cancellation only when the checked wire backend
is healthy and its peer has no outstanding file record/reply. The existing
STATUS stop flag with result 0 lets the unchanged finite utility clean up and
acknowledge FINISH; resident EMOS then closes the grant normally and retains
ExCom negotiation. P4 must still classify the HTTP operation as cancelled, never
successful or replayable. A poisoned exchange, missing acknowledgement, failed
utility cleanup or open Agon write stage retains the fault path. No protocol
layout, EMOSlet ABI or production change is required.

Validate clean stop versus in-flight/poisoned cancellation in host tests, the
actual HTTP/Peer/finite-utility chain with a truncated upload and subsequent job,
and physical repeated ExCom aborted uploads followed by exact reads/new writes.
Preserve startup, current EMOS/utility and rollback; finish at a recoverable CLI.

### Clean cancellation results — September 28 UTC

The selected P4 build now distinguishes orderly client cancellation from a
poisoned exchange. EMOS, `/emos/sdjob.bin` and startup are unchanged. P4 backup,
independent flash verification and matching boot identity are retained under
`hardware/peer-p4-clean-cancel`; run evidence is under `hardware/clean-cancel`
in the ignored runtime silo.

| Check | Result |
| --- | --- |
| Quiet cancellation / repeated stop | PASS; STATUS requests healthy stop; FINISH/CLOSE complete but P4 never reports the cancelled operation successful |
| In-flight record or prior poison | PASS; cannot downgrade to orderly cancellation |
| Actual HTTP/Peer/finite utility/engine | PASS under sanitizers; truncated PUT returns error, creates no destination, utility returns cleanly and subsequent GET succeeds without a fresh HELLO |
| Existing unfinished-stage / lost-READY tests | PASS; terminal failure behavior retained |
| Identified P4 build and physical deployment | PASS; independent verification and boot identity |
| Three physical ExCom upload cancellations | PASS; after each EOF, absent destination, exact 4096-byte existing-file read and a fresh write/read, without reset, mode switch or request retry |
| Keyboard/display and final recovery | PASS; before/after text markers, no backend-unavailable diagnostic; returned to Legacy with idle admission and ready neutral keyboard |

The physical sequence made 16 HTTP requests (32.39 seconds summed request time),
plus three intentionally incomplete raw uploads and keyboard/text observations.
This is functional evidence, not a throughput comparison. The earlier blanket
client-abort limitation is superseded for these clean cancellations. Missing
acknowledgements, poisoned exchanges, failed cleanup and unfinished Agon write
stages retain conservative Legacy renegotiation. Already completed mutations are
not rolled back or retried. Broader A11 media/interruption and application-origin
coverage remain open; no production promotion or native GUI acceptance claimed.
