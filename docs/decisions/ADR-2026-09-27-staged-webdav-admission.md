# Staged WebDAV access with EMOS-owned admission

- Status: Proposed
- Completeness: Partial
- Date: 2026-09-27
- Related task: REMOTE-005
- Open-decision tracker: REMOTE-005

## Purpose

Expose mainboard SD through native host file managers while retaining the
existing EMOS-owned transport and recoverable file-transfer mechanism. P4 uses
its local SD for staging; it does not implement WebDAV inside EMOS or invoke
mainboard filesystem operations from an interrupt.

## Proposed admission model

EMOS is the authority for whether mainboard work may start. External requests
are admitted only at an empty, idle CLI prompt. Partly typed commands cause busy
rejection and remain untouched (Author agreed 2026-09-27). EMOS rejects them as busy while a
user application runs, including read, listing and mutation requests requiring
mainboard access. Rejected work is not queued to execute after the application
exits. P4's cached indication of CLI state cannot authorize a transfer.

A running eZ80 application may explicitly initiate transfers in either direction
through an EMOS-owned API. This is a separate, locally initiated admission path;
an external client cannot obtain it by setting an origin flag in a packet.
The application cooperatively performs or delegates its foreground work; EMOS
does not create a background filesystem task or run FAT operations in an ISR.

EMOS initiates the safe-point check/admission exchange. P4 exposes pending intent
and responds only through the admitted service. Existing keyboard traffic and
UART RTS/CTS are unchanged. No direct GPIO access, parallel bus reversal or new
logic circuitry is part of this design.

## Proposed upload and download paths

Upload: host WebDAV client sends bytes to P4; P4 stages them on its local SD and
computes size/CRC. An EMOS-authorized foreground utility receives those bytes via
the established transfer mechanism, stages them on mainboard SD, then activates
them using existing recovery semantics. WebDAV success means mainboard commit,
not merely receipt into P4 staging. Admission must precede mainboard work and
remain valid through the transfer; disconnect, application entry and reset cannot
silently reuse it.

Download: after EMOS admission, the foreground mainboard utility sends a file to
P4-local staging. P4 serves the completed snapshot to the host, including range
reads. A completed snapshot may finish serving without further mainboard access;
it is not a perpetual cache of live Agon state. Fresh requests that need mainboard
access require fresh valid admission. Partial snapshots are not served as complete.

Directory listing and mutations use the same admission/serialization authority.
Staging files does not itself provide mkdir, rename or directory deletion; those
remain explicit foreground EMOSlet primitives. Directory trees are sequences of
operations with reported partial outcomes, not power-atomic transactions.

## Ownership and boundaries

P4 owns WebDAV parsing, client responses, staging quota and cleanup, checksums,
and transport orchestration. Resident EMOS owns safe-point detection, caller
admission, transport and lifecycle state. SD utility/application foreground code
owns mainboard filesystem execution. Preserve loaded application memory and typed
CLI input; missing utilities must produce an error and leave a usable prompt.

Keep ordinary CLI transfer tools working. Physical transfer remains the existing
UART service for this tranche. ExExt/parallel transport is separate work. The target is transfer support in both Legacy and ExCom, preserving the selected
display route. Removing the current Legacy-only admission requires explicit
coexistence investigation and qualification. A MOSlet may not overwrite a calling
application's memory.

No implementation, deployment or production selection follows merely from this
proposed ADR. Remaining design choices and the development/test gates are in
REMOTE-005's R05-A work items and D06–D10.
