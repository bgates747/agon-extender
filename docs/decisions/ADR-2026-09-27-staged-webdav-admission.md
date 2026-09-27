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

Once admitted, the external transfer occupies the foreground CLI until completion,
cancellation or failure cleanup. EMOS does not dispatch another command or user
application during that interval. The selected display mode remains unchanged.
The Author accepted this foreground ownership on 2026-09-27.

A running eZ80 application may explicitly initiate transfers in either direction
through an EMOS-owned API. This is a separate, locally initiated admission path;
an external client cannot obtain it by setting an origin flag in a packet.
Application-initiated calls are synchronous: the application waits for completion
or failure and receives a defined result before resuming. No background completion
callbacks are introduced (Author accepted 2026-09-27).
The application cooperatively performs or delegates its foreground work; EMOS
does not create a background filesystem task or run FAT operations in an ISR.

EMOS initiates the safe-point check/admission exchange. P4 exposes pending intent
and responds only through the admitted service. Existing keyboard traffic and
UART RTS/CTS are unchanged. No direct GPIO access, parallel bus reversal or new
logic circuitry is part of this design.

## Staging requirement

P4-local SD staging is required for this new service. If staging media is absent
or has insufficient space, report a clear failure; do not silently fall back to
RAM-only staging or a different transfer method. This does not disable existing
explicit CLI transfer tools. Accepted by the Author on 2026-09-27.

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

## Cancellation and recovery — accepted 2026-09-27

Escape on Agon requests cancellation of external foreground transfers. Return to
CLI only after safe cleanup. Application-origin transfers retain application-owned
keyboard policy; EMOS does not impose Escape cancellation on the caller.

Preserve the established per-file staged replacement and recovery mechanism:
prepare and verify the new file under the selected transfer contract, retain the
old target as backup during activation, and retire it only after confirmed
success. Cancellation during activation waits for completion or a recoverable
failure boundary. Do not erase the only confirmed good copy during cleanup.

This is recoverable replacement, not unconditional power-failure atomicity on FAT.
Directory transfers are not all-or-nothing in the first iteration: completed files
remain and incomplete entries are reported. No new filesystem transaction layer
or silent relaxation of the checked/fast transfer contract is selected.

## Exported namespace — accepted 2026-09-27

Expose the entire Agon mainboard SD card from `/` by default. No configurable
subdirectory-selection feature is required for the first iteration. Preserve
path validation and rejection of deleting the filesystem root. P4-local staging
remains separate from the exported Agon filesystem.

## Transfer serialization — accepted 2026-09-27

Allow one active transfer job at a time. Competing clients receive a busy response;
do not introduce multi-user scheduling or silently queue their work. The same
ownership rule covers external clients, explicit CLI tools and application-origin
transfers. Multiple HTTP sockets from a native client are not by themselves
separate jobs; implementation must preserve client compatibility while enforcing
EMOS's single admitted mainboard owner.

## Authentication scope — accepted 2026-09-27

Keep this Agon file service password-free: no user accounts, usernames or
passwords in the current implementation scope. Any reachable client may request
access, subject to EMOS admission and single-job ownership. Session/job identifiers
coordinate transfers; they are not credentials.
