# REMOTE-007 — Restore staged WebDAV file transfers

## Executive summary

The current bench has a reported WebDAV failure: directory metadata requests
succeed, but file downloads return empty HTTP 500 responses. The foreground
EMOS listener successfully transfers files on the same bench. Investigate and
repair the staged WebDAV path without weakening transfer checks or EMOS admission.
Task recorded on 2026-10-08; investigation, implementation and bench execution
await selection. No hardware work is authorized by this writeup alone.

## Evidence and interpretation

| Operation | Reported result | Meaning |
|---|---|---|
| WebDAV PROPFIND / HEAD for existing fixtures | Succeeded | Metadata access does not establish file-body transfer correctness |
| WebDAV GET of `/autoexec.txt` and a benchmark binary | Empty HTTP 500 | Download failure; root cause unresolved |
| P4-local SD status | Mounted, ESP_OK, ample space | Does not prove staging operations or transaction state are healthy |
| Foreground checked EMOS listener PUT and independent GET | Exact bytes verified; listener EXIT succeeded | Working fallback and useful control, not proof the automatic path is healthy |

These observations come from the fsim agent's 2026-10-08 handover in ignored
`HARDWARE.local.md`, corroborated by the Author. That local record identifies
the fixture paths and retained host receipts. Preserve those receipts before
investigation; do not infer current installed identities from Git HEAD.
WebDAV PUT was not attempted in that reported failure sequence. Earlier bounded
WebDAV passes remain valid historical evidence; the point of regression is unknown.

## Scope and ownership

The host file manager or curl sends HTTP/WebDAV requests to the P4 on port 8081.
The P4 adapter stages data on its own SD card. At an eligible idle CLI, EMOS on
the eZ80 admits a finite `/emos/sdjob.bin` job using the existing P4–eZ80 UART
transport. Compare that path with the foreground `/emos/sdserve.bin` listener.
Do not bypass EMOS admission or contact a running application with external jobs.

Use the [mainboard SD guide](../mainboard-sd.md),
[staged protocol](../protocols/staged-webdav.md),
[adapter contract](../../vdp/video/extender/storage/webdav/README.md) and
[original implementation task](REMOTE-005.md). Reuse existing service tests and
scratch-file fixtures. P4-local HTTP port 8080 is a separate service, not WebDAV.
No new file protocol, authentication scheme or broad performance work belongs here.

## Work contract

R07-01 [ ] Preserve the reported evidence and record exact installed P4, EMOS,
sdjob and host-client identities, plus display mode and CLI/service readiness.
Read current bench ownership and constraints before requesting hardware access.
Locate existing tests and review official MOS file API contracts before code changes.

R07-02 [ ] Reproduce with a bounded curl sequence: PROPFIND, HEAD and GET of a
known small file. Retain HTTP status, headers, body size, correlated service/job
state and bounded logs. Compare exact bytes with a checked listener GET of the
same file, exiting the listener before automatic-service checks. Preserve startup
and user files; use only a dedicated scratch directory for mutations.

R07-03 [ ] Trace the first failing boundary: host request, P4 admission, finite
EMOS job, UART response, P4 staging open/write/read, HTTP body delivery or cleanup.
Check paired-component compatibility, timeout/error propagation and retained
transaction state. Do not assume a hardware, client or HTTP-only fault merely
because the listener works. Summarize the causal evidence before selecting a fix.

R07-04 [ ] Implement the smallest evidenced repair in the owning checkout, with
a focused regression test. Preserve correctness checks, busy rejection and
uncertain-transaction recovery. Do not delete staging evidence or automatically
retry uncertain writes to make a test pass. Compile affected components and run
existing relevant tests before deployment.

R07-05 [ ] On an available bench, verify known-byte downloads and scratch uploads
with independent readback, empty and multi-chunk files, directory listing and
scratch mkdir/rename/delete. Repeat the core transfer checks in Legacy and
negotiated ExCom. Confirm busy-application rejection, return to usable CLI and
continued foreground-listener operation. Record durations and exact identities;
stop on corruption or uncertain mutation rather than replaying it.

R07-06 [ ] Validate directory browsing and two-way copying in the Lenovo file
manager with the Author. Record other host clients as untested unless actually
checked. Update current operating guidance with the result and remaining limits;
after explicit acceptance, follow production promotion/version gates. Close only
the demonstrated failure scope, not all of REMOTE-005's remaining qualification.

## Completion and gates

Completion requires an explained failure, retained failing/passing evidence,
correct file-body transfers and Author file-manager review. Record any residual
limitations explicitly. Until then use the documented foreground listener for
reliable transfers. Creating this task does not reserve the bench, flash firmware,
start tests, commit unrelated work or authorize production promotion.
