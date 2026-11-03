# BENCH-012 — Central physical-bench scheduling

Extender is the Author-assigned physical bench scheduler. Adopt the familiar
Golem request/grant/token/assert/release/notify lifecycle in one central physical
registry; Golem confirms no atomic physical queue or outstanding lease exists.
Oryx emulator FIFO remains unchanged. This self-assigned implementation supports
the Author's overnight scheduling and all-consumer bug-debugging authorization.

**State:** Implemented and published; eight isolated device-free checks pass.
Registry initialized from explicit no-owner handoff, no physical lease granted
or hardware operation implied. Central maintained source/instructions and ignored live state
belong in agon-dev-env/cross-agent/olimex-bench, not competing project queues.

1. [x] Obtain Golem414 handoff: no current checkout, queued request or promised
   successor. Preserve latest B10-R03 release and installed P4r27/EMOSv27/native
   identities as historical evidence, not fresh observations.
2. [x] Implement atomic host-only reserve/status, scheduler grant, token ownership
   assertion, own cancellation and evidence-backed release with next contact.
   Unique request/token/generation and no expiry/preemption. Preserve unknown
   ownership; no hardware action, automatic test/reset, human review overnight,
   or scope expansion. Physical idle proof replaces emulator process evidence.
3. [x] Support explicit consumer-to-Extender repair custody and clean return,
   with self-assigned task/evidence links, stopped owned resources and token
   invalidation. A fault preserves occupancy until coordinated resolution.
4. [x] Run isolated device-free checks for concurrent grant exclusion, FIFO,
   wrong owner/token, stale/false physical evidence, occupied cancellation,
   repair transfer/return and state preservation. No Oryx/live-queue mutation.
5. [x] Publish maintained instructions/helper/state paths, initialize only from
   the verified no-owner handoff, and tell Golem by durable mail plus steering.
   A time grant covers existing authorization only. Capture grants, repairs and
   releases durably; no periodic idle-session mailbox polling.

The helper is cooperative scheduling, not authentication or physical isolation.
Network/device identities and live component/evidence paths stay in ignored state.
Extender grants after fresh physical readiness evidence; agents assert ownership
before access, clean up their own resources, and preserve/restore components per
request. No processor protocol or firmware change. Human optical/sound judgements
are deferred while the Author sleeps.


The maintained authority is
[central physical checkout](../../../agon-dev-env/cross-agent/olimex-bench/README.md).
Its helper, tests and ignored live registry implement request/grant/token/assert/
release/next-contact plus explicit repair transfer/return. Source and copied
publication bytes agree; all eight isolated checks pass, including one winner
for competing grants. Initial activecheckout=null and reservations empty come
from Golem414, not from a new physical poll. The helper never starts tests or
accesses devices. Live scheduling is ongoing operation rather than unfinished
implementation; the task preserves its scope and evidence. Source/contact/initial
publication receipts remain in ignored agents/bench012. Oryx code/state unchanged.


Central source/instructions are committed and pushed as agon-dev-env `fa77f0c`
on its maintained deployment branch. The Extender adoption links and task
record are committed separately; unrelated environment changes are preserved.

## First prepared consumer admission

The 6502 owner has frozen its finite, already-authorized plan and reserved the
physical bench. Extender reconciles BBC BASIC's intended priority first, then
obtains a fresh scheduler observation while the registry has no active owner.
This admission starts only the accepted foreground SD listener, reads unchanged
startup/listener bytes through the pinned staged client, and exits to the CLI.
Extender observes neutral input, idle jobs and ownerless serial endpoints; it
does not invoke a diagnostic, reset, reflash or change mode/startup. Component
identities not freshly read from flash are explicitly retained historical pins,
which the consumer must independently verify where its frozen plan requires.
The registry grant and durable handoff retain the exact observation/lease;
consumer first-failure and exact native-VDP restoration boundaries remain intact.

## R01 — Machine-readable component identities, self-assigned

Golem's future consumer admission compares component SHA256 fields as exact
64hex strings. Earlier observations combine those hashes with human provenance
inside each value, preventing direct identity comparison. Separate the two for
future observations without rewriting history or disturbing active custody.

1. Define future `components` values as raw lowercase64hex SHA256, with matching
   nonempty human descriptions under `component_provenance`. Distinguish fresh
   reads from retained verified bytes; formatting is not new live verification.
2. Add opt-in validation when `component_provenance` is supplied. Keep legacy
   observations accepted so the active consumer can assert/release normally.
   Preserve past entry/release observations and all live state; no migration.
3. Check raw identity/provenance preservation, rejected descriptive/bad/missing
   fields without queue mutation, and a new-format grant followed by a legacy
   release. Use only isolated temporary state/evidence, never the live queue.
4. Publish the central helper/tests/protocol and report the future format to
   Golem. Prepare the next actual observation in that format only at authorized
   fresh admission. No device read, firmware change or redundant flash backup.

State: implemented; all ten isolated host checks pass, including new-format
grant/legacy-release compatibility and rejected malformed records without queue
mutation. Published in the central owner repository as `d0f33db`. Current6502
generation5 and every historical observation remain untouched; no live proof
was manufactured, normalized or refreshed by the source correction.

Future field scopes are explicit: P4/native VDP identify application-image bytes,
EMOS identifies complete ROM including declared padding, and startup/listener
identify complete files. Native full-flash restoration hashes belong in separate
provenance/evidence. Older full-flash-labelled observations retain their original
scope. Observation freshness is evaluated on use, not as lease expiry; a later
owner-entry check requires new actual evidence, never a restamped original grant.
