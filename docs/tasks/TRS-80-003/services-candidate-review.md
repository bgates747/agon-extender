# Guest-disabled services candidate review

## Executive summary

No blocking lifecycle defect found in the inspected RUN-01 worker. This source
review supports the proposed bounded startup/SD test; it does not establish
runtime correctness, Author flash authorization or production acceptance.
No firmware, peer source or bench state was changed.

Reviewed services.cpp SHA-256:
`4d829dc2aa8a605f1a4a25966a245121a033978fa4001738eb328143aa67fee8`.
Peer receipt identifies `trs80-services-r01-b2026-09-27-01-35-15Z`, built but not
deployed, using Extender 2ecd55b8. The peer owns binding reviewed source to its
frozen candidate; this review is not an independent complete binary audit.

## Findings

| ID | Assessment | Evidence and limits |
|---|---|---|
| SC01 | Lifecycle consistent | Process-long Ethernet object and worker; callback only xTaskNotifyGive; explicit initArduino before start. Candidate config disables Arduino autostart and uses 1000-Hz FreeRTOS tick. No guest call in services.cpp. |
| SC02 | Bounded failure behavior consistent | Failed Ethernet start records fault, no retry storm. DHCP deadline reports degraded waiting without reboot. HTTP start attempted once after IP; failure stays visible. No stop below live SD server. |
| SC03 | Telemetry appropriate for first candidate | Worker stack and internal/PSRAM heap sampled separately; private mount and HTTP task internals not accessed. Server readiness does not claim mounted storage. Actual resource sufficiency remains a bench measurement. |
| SC04 | Nonblocking observation limitation | Only boolean hasIP transitions trigger lease/address logging. A changed address while hasIP remains true, or loss/recovery between observations, may be unreported. Coalescing preserves latest readiness, not event history. If qualification claims every transition/address renewal, extend observations first; otherwise state this limit. |
| SC05 | Rollback artifact verified offline | Retained r57 factory image is 1,691,888 bytes; SHA-256 06ec2ef817f38e3d62dc28869d9267be3b8f8b39637f6e51e988c70f40bf5697 matches local rollback record; deployment receipt exists. This short factory image is not a full incoming-flash backup across changed partitions. Current board state was not queried. |

The first candidate intentionally omits guest, media leases, browser/input and
coordinated teardown. Do not expand those requirements into this startup test.
Retain the planned full incoming-flash preservation and independent verification
before any separately authorized firmware switch. Local artifact/receipt paths
were supplied privately through the mailbox rather than tracked here.
