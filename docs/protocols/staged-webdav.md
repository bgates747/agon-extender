# Staged mainboard file access — development capability

The explicit staged-WebDAV P4 candidate serves a limited HTTP/WebDAV file API on
port 8081. It is not selected production and does not claim DAV class 1, 2 or 3
conformance. OPTIONS advertises this document URI as its extension capability;
that enables discovery by clients that require a DAV header without advertising
unsupported locking or property updates.

P4 stages data on its local card. Resident EMOS admits each mainboard operation
only at an eligible idle CLI and runs `/emos/sdjob.bin` as a finite EMOSlet.
The development implementation supports finite external requests in Legacy and
ExCom after Legacy capability negotiation. Successful ExCom jobs retain that
negotiation. Clean client cancellation also preserves it after acknowledged
FINISH/CLOSE at a quiet wire boundary: no partial upload destination is activated
and the next ExCom job can proceed. A poisoned exchange, failed cleanup or
unfinished Agon write stage still requires Legacy renegotiation. Cancellation
does not promise rollback of mutations already completed. Keyboard/display
operation remains available.
There is no implicit display switch. Manual listeners and application-owned
leases remain Legacy-only. Bounded Legacy/ExCom physical checks pass; broader
fault checks, application-origin integration and native-client acceptance remain in
[REMOTE-005](../tasks/REMOTE-005.md). No manual listener is required for this API;
an active manual listener instead excludes automatic jobs.

The [adapter contract](../../vdp/video/extender/storage/webdav/README.md) defines
methods and bounds: OPTIONS, PROPFIND, GET, HEAD, PUT, MKCOL, COPY, MOVE and DELETE.
There is no LOCK, UNLOCK, PROPPATCH, authentication or TLS. Use only on the trusted
local network. The Agon card root is exposed subject to protected service paths.
Concurrent or ineligible requests fail rather than queue. Clients must not retry
an uncertain mutation automatically. A successful response follows job completion
and release of shared storage resources; it does not promise power-loss atomicity
for a whole directory operation.
