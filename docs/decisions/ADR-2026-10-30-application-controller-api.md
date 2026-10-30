# Keep controller interpretation in a reusable application include

- Status: Accepted
- Completeness: Complete
- Date: 2026-10-30
- Related task: INPUT-005

The Author requests maximum practical recovery of resident EMOS flash by moving
controller handling into ordinary applications. A single maintained include
forms part of the Author's personal API: standardized proven routines reused
across games and tools. No MOSlet or dynamically loaded provider is involved.

The application include owns controller request/reply interpretation, logical
controls, source/transition tracking, acknowledgement after acceptance and stale
state policy. P4 acquisition adapters own device-specific USB decoding and feed
the normalized gamepad interface. Compatibility follows the decoded controls,
not a promise that all USB devices use identical physical reports.

EMOS retains admitted routing/UART ownership, bounded safe delivery, lifetime
cleanup and necessary correlation/timing protection. Applications do not write
UART/GPIO directly. Reuse the existing gateway and transport owners; keep SD and
controller leases independent. No checksums are introduced.

The owning task records the gateway migration, measured size and validation.
This decision does not qualify hardware, choose a release version or promote
an untested installation.
