# Legacy finite-job qualification

The Author released the bench for autonomous qualification. Local target and host
checks pass. The first physical tranche is limited to automatic external jobs in
Legacy mode; ExCom and application-origin staged file jobs remain unfinished.
Production v0.1.0 is not replaced by these candidate builds.

## Selected candidates

| Component | Identity | Source |
| --- | --- | --- |
| Resident EMOS | agon-emos-v0.1.22-b2026-09-27-23-46-40Z | agon-emos e6a23cb |
| Finite utility | sdjob-v0.1.0-b2026-09-27-23-45-52Z | agon-emos e6a23cb |
| P4 | uart-excom-console-r60-b2026-09-27-23-45-52Z | Extender c1e879e7; explicit staged-WebDAV export |

Registry r118 and these draft identities use the Author's standing version
preapproval. No new production version/tag is selected.

## Local evidence

| Check | Result and boundary |
| --- | --- |
| Actual eZ80 utility + actual P4 Peer | PASS: HELLO/STAT/READ, exact bytes, FINISH/CLOSE, return to prompt |
| Missing utility, absent peer, corrupt reply, key-before-grant race | PASS in maintained UART-peer emulator harness |
| EMOS tests and linked guards | PASS: 129 tests, ABI/VDU/UART/parallel/keyboard checks |
| Target firmware | 128,369-byte EMOS ROM; identified 23,230-byte finite utility; P4 clean exported build passed |
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

Physical execution is in progress. Exact manifests, logs and rollback bytes are
retained under ignored `agents/remote005-webdav-runtime`. The actual incoming P4
full flash was saved before replacement; mainboard ROM and unchanged startup were
also preserved. Update this section with terminal outcomes before closeout.

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
