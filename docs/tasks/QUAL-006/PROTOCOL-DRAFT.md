# QUAL-006 control protocol — working draft

Status: Proposed; not an implementation or deployment contract.
Date: 2026-10-13.
Owner: [QUAL-006](../QUAL-006.md), Q06-04 and Q06-D04-T01.

## Executive summary

The accepted architecture can use a transport-independent snapshot, ordered
events and finite job state machine. EMOS supplies execution truth and launch
authorization; P4 supplies host sessions, resource arbitration and event storage.
Neither a missing response nor a reconnected client authorizes another launch.
This draft specifies logical fields and dispositions for review. Concrete wire
layouts, command/access details and resource budgets remain proposed. The
selected transport and boot-scoped enablement policy are accepted as recorded
in the parent task.

The first implementation tranche remains observation only. Job and fixture
records below describe the subsequent contract, not permission to implement or
enable remote execution before that tranche is qualified.

## Identity and encoding

1. Every message declares schema major/minor and required capabilities. Unknown
   major or missing required capabilities rejects the operation before mutation.
   Do not assign a released protocol version or private opcode from this draft.
2. P4 and EMOS each identify their build and boot incarnation. Link establishment
   binds both incarnations to a link generation. Boot identity construction and
   collision/reuse guarantees must be proved; existing time-derived identifiers
   alone must not be promoted to persistent uniqueness.
3. EMOS increments a foreground generation on each ownership transition. P4
   assigns event sequences within its boot incarnation. Exhaustion invalidates
   the affected sequence space; it never silently wraps into a valid old identity.
4. The host creates a job ID and descriptor digest. P4 binds its offer to the
   current link and host lease; EMOS supplies the grant and foreground generation.
   Retrying a lookup is distinct from requesting execution again.
5. Binary fixture records use explicit integer widths and byte order, never C
   structure layout. The wire encoding is pending. A JSON host representation
   encodes wide counters/opaque identifiers as strings to avoid browser rounding.
6. Error text is bounded supporting detail. Stable typed codes drive the runner.

## Snapshot schema

| Group | Logical fields | Authority and interpretation |
|---|---|---|
| Schema | major, minor, capabilities | Each peer declares supported contract; P4 exposes negotiated compatibility. |
| P4 | boot identity, build identity, sample monotonic time, event cursor | P4-owned facts; boot/build identity is separate from the installation receipt. |
| EMOS report | boot/build identity, link generation, report sequence, receipt age, validity/reason | EMOS creates the report; P4 attaches local receive time and freshness. |
| Foreground | phase, generation, execution origin, current command/job identity | EMOS only. Unknown application identity remains explicit. |
| Input | EMOS-selected source/admission; P4 owner, held/pending/neutral | Separate EMOS and P4 observations, not an inferred CLI state. |
| Mode/display | EMOS route/mode intent and generation; P4 committed geometry/generation | Requested and committed state stay distinct. |
| Job | job/descriptor/grant identity, phase, fixture hash/schema, last assertion, terminal disposition | EMOS supplies execution phase; P4 separately reports offer/storage/client phase. |
| Safety | cancellation capability, cleanup/restoration state, reset-safety knowledge | EMOS/job-owned observations; never a replacement for reset authorization. |
| Resources | lease owner/generation, declared consumers, conflicts | P4 network/resource owner, with EMOS foreground eligibility separate. |
| Retention | earliest/latest event sequence, terminal-journal availability | P4 reports exactly what reconnect can retrieve. |

A snapshot is a coherent P4 copy of local facts plus a specific EMOS report,
not an instantaneous cross-processor transaction. Every EMOS-owned field shares
that report's identity and freshness. P4 must not combine an old foreground
report with a new link and label the result current.

Validity reasons distinguish `not-admitted`, `incompatible-peer`, `no-report`,
`stale-report`, `peer-restarted` and `link-lost`. Unavailable transport is not an
EMOS foreground phase. Freshness thresholds remain configurable, declared and
subject to measurement; stale safety knowledge cannot authorize recovery.

## Read-only query scheduling

1. P4 requests a snapshot only on an admitted UART epoch. Before that it returns
   `not-admitted` locally rather than inventing EMOS state.
2. EMOS receive handling records a bounded pending request. EMOS copies a coherent
   resident state and its sole foreground output owner emits the complete reply
   between whole records. No ISR transmission or second UART writer is introduced.
3. Coalesce duplicate outstanding observation requests. A query must not create
   an unbounded queue or delay application output indefinitely.
4. The implementation must identify each service opportunity: idle editor,
   built-in command, utility and supervised application. Uncooperative programs
   may prevent timely replies; P4 then reports the last report as stale/unknown.
   Interrupt receipt alone does not prove a response can be transmitted safely.
5. Query watchdog expiry reports observation failure. It does not mean that EMOS
   is idle, crashed, disposable or safe to reset.

## Ordered event schema and reconnect

Each event carries schema, P4 boot identity and sequence, event kind, P4
monotonic receive time, source authority and applicable EMOS boot/link/report,
foreground, job/grant and fixture/schema bindings. EMOS-origin records carry
their source sequence so P4 can detect a missing ingress record.

| Event class | Required meaning |
|---|---|
| Peer/link | Current peer identity, negotiated availability or invalidation |
| Foreground | EMOS-reported phase/generation transition |
| Offer/grant | P4 provisional offer versus EMOS authorization/rejection |
| Fixture | Start, bounded progress, assertion, completion |
| Supervisor | Load/launch/return status, missing or malformed completion |
| Cleanup | Restoration started/verified/failed and resulting EMOS foreground |
| Resource | Lease acquired/released/expired, conflict or client disconnect |
| Gap | Missing ingress records or unavailable retained history |

1. The host first obtains a snapshot, then asks for events after its cursor with
   the same P4 boot identity. Snapshot sampling and cursor capture must share a
   defined synchronization boundary so an intervening event cannot disappear.
2. An event request returns ordered records, the next cursor and retention bounds.
   Empty results mean no retained new event at that cursor, not completion.
3. Wrong boot identity or a cursor older than retained history returns an explicit
   gap/restart disposition. The host obtains a fresh snapshot and queries the
   known job's terminal journal. It never resubmits automatically.
4. Lost state during P4 restart is reported as unknown. Do not claim durable
   terminal recovery unless the selected persistence implementation proves it.
5. Host disconnect does not cancel a granted fixture. Lease expiry rejects new
   work and records loss of ownership; cancellation/cleanup requires the job's
   separately declared cooperative contract.

## Finite job descriptor

The descriptor includes job ID/digest, expected peer identities/capabilities,
fixture path/hash/size, result schema, working directory, bounded arguments,
requested mode/route, independently checked code/data/heap/stack bounds,
no-nested-MOSlet declaration, resources, cancellation capability, destructive
scope, cleanup contract and observation watchdogs. Required fields may not be
inferred from current directory, cached pixels or a historical task name.

P4 validates host/session/resource eligibility; EMOS independently checks its
current safe point, mode ownership, memory contract and exact offered identity.
A host-supplied `safe=true` field cannot authorize execution or recovery.

## Job state machine

| Transition | Actor and condition | Failure disposition |
|---|---|---|
| absent → offered | P4 validates enabled host lease and bounded descriptor | Disabled, incompatible, conflict or invalid descriptor; nothing launched |
| offered → granted | EMOS atomically validates empty CLI, pending input, link and exact offer | Busy/input wins/stale offer; offer retired without deferred replay |
| granted → preparing | EMOS binds foreground/grant and prepares declared mode/resources | Preparation failure; no fixture start claimed |
| preparing → running | EMOS/supervisor verifies and loads the proved fixture, then observes bound start | Missing/changed image, unsafe memory, load failure or missing start |
| running → reported | Fixture sends valid bound completion | Assertions failed, malformed/missing record or unexpected return |
| reported → cleaning | EMOS/supervisor performs the accepted cleanup | Cleanup failure remains separate from fixture assertions |
| cleaning → terminal | EMOS reports final foreground and cleanup result; P4 records journal and releases resources | Recovery-required or unknown; no speculative next launch |

Pass requires valid fixture completion, passing required assertions, verified
cleanup and EMOS-declared handback. A completed measurement with deferred raw
collection remains `awaiting-artifacts`; it cannot become a validated pass until
the required artifacts match their identity/integrity contract.

Repeated submission of the same job ID and descriptor returns known status and
does not create another execution. The same ID with a different digest is a
conflict. If a peer restart prevents proving previous disposition, the answer is
unknown rather than a new grant.

Cancellation is optional and cooperative. Uninstrumented applications and
noninterruptible restoration intervals have no generic Escape/reset fallback.
An observation watchdog or host lease expiry never invents cancellation safety.

## Resource and enablement proposals

These are review targets, not accepted limits or measured capacity:

| Item | Starting proposal | Proof needed |
|---|---|---|
| Executing jobs | One EMOS job and one host control lease | Atomic admission against user input and storage ownership |
| Event readers | One initial host reader | Concurrent browser/input/storage service and disconnect tests |
| Event retention | 128 fixed slots, at most 256 binary bytes each | Full identity encoding fits; overflow is explicit; memory placement/locking are bounded |
| Terminal journal | Separate bounded records; reject new work if unacknowledged terminal capacity is exhausted | Persistence medium, restart recovery and retention/acknowledgement policy |
| Progress | Coalescible bounded updates; assertions/terminal records cannot disappear silently | Producer limits and overflow disposition without blocking rendering |
| Host batches | Fixed record/encoded-byte cap, caller cannot request unbounded history | Serialization memory, send latency and request-task responsiveness |
| Enablement | Accepted Q06-D07: EMOS operator command enables execution for the current boot; reboot disables it; host lease and per-job EMOS grant still required | Exact command, disable-during-job behavior, network access and browser policy |

The proposed event slots alone cost 32 KiB before metadata, snapshots, terminal
records, serialization and client state. Do not treat that subtotal as a proven
P4 budget. The first observation-only tranche does not enable job execution.
Read-only status is accepted as available after ordinary Extender admission
without enabling execution. Its concrete network exposure and rate limits remain
contract details. The facility supports production bug reports and feature proofs
on exact firmware, with diagnostic payload and evidence identities retained.

## Host transport comparison

Local source observations: `HttpVideoConfig` defaults to seven sockets and a
4096-byte HTTP task stack; `startServer` disables LRU purge and installs explicit
open/close hooks. Existing video uses WebSocket frames and queued dispatch.
Its complete-send path can wait on a slow client, so existing WebSocket support
does not itself prove a nonblocking event service.

| Candidate | Potential reuse | Main cost/risk | Required check |
|---|---|---|---|
| SSE | HTTP response framing; natural ordered server events | Persistent socket, slow writer, lifetime/cleanup | Asynchronous response ownership, bounded writes and reconnect cursor |
| WebSocket | Existing handshake, socket hooks and queued-send patterns | Persistent socket and explicit application replay/credit rules | Per-client generation, credit/batch cap, send isolation and disconnect cleanup |
| Bounded long-poll | Ordinary HTTP request/response and cursor parameters | Retained request ownership or repeated request overhead | No sleeping on shared request task; bounded pending requests, cancellation and timeout response |

The Author selected asynchronous bounded long-poll on 2026-10-13, based on the
source review below. This is an architectural selection, not a measured capacity
result. Separately qualify P4 memory, service latency and reconnect behavior on
both boards when bench work is authorized.

### Selected transport — asynchronous bounded long-poll

Accepted under Q06-D04-T01 on 2026-10-13, with resource qualification required
on both boards. This is not a measured performance conclusion or final
implementation freeze.

1. Host uses ordinary snapshot GET, event GET with boot/cursor, and separate
   explicit job/control requests. Full-duplex messaging is unnecessary for the
   accepted interface. Existing standard-library host clients can retain their
   HTTP model without adding a WebSocket dependency.
2. P4 admits at most one outstanding event request from the control reader.
   Copy it using the SDK asynchronous-request API, hand it to one bounded worker,
   and return the shared HTTP handler immediately. Never sleep awaiting an event
   on the shared request task.
3. Target a one-second empty-response wait, ending earlier when events arrive.
   Send at most the configured record/byte batch and complete the asynchronous
   request exactly once. The host advances its cursor only after validating the
   complete response, then issues the next GET. Empty results preserve its cursor.
4. Worker allocation failure, busy reader, send failure, disconnect, server stop,
   peer restart and wait expiry all release request/socket ownership through the
   SDK completion contract. A failed send must not release EMOS job authority or
   trigger a new job. Session/reader generations protect reused socket numbers.
5. Snapshot/keyboard/display handlers continue independently of the event wait.
   The worker may block only within its own bounded response/send contract. Its
   stack, response buffer and retained-request memory must fit the declared budget.
6. Measure shared-service latency, heap/stack high-water marks, disconnect leaks,
   socket exhaustion and reconnect gaps with DevKit browser video/input active,
   and independently on PC. Reject the design if bounded ownership or acceptable
   service latency cannot be demonstrated.

The pinned ESP-IDF header documents that `httpd_req_async_handler_begin` allocates
a request usable by an asynchronous thread, while completion frees the request
and relinquishes socket ownership. It explicitly warns that missing completion
eventually prevents new connections. That is the principal lifecycle proof gate.

By contrast, `httpd_queue_work` executes its callback in HTTPD's context. The
existing video path calls its complete-send loop from that callback, and the
loop allows up to five seconds for a slow client. Queueing therefore does not
isolate event sends from the shared request task. SSE would also need independent
response ownership and additionally retains its streaming socket indefinitely.

SDK source reviewed: ESP-IDF commit
`b774170ff46c393eeb5e495ea37936038d3f4f4f`,
[`esp_http_server.h`](https://github.com/espressif/esp-idf/blob/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/esp_http_server/include/esp_http_server.h),
as identified in the retained candidate manifest. Local project send/cleanup
sources are linked below. No hardware request or load measurement was performed.

## Offline validation cases before implementation freeze

1. Snapshot/cursor race: an event arriving during snapshot construction is
   present either in that snapshot's state or in the following retained feed.
2. Input wins the offer/grant race; no fixture launches and no offer is replayed.
3. Duplicate job/digest returns status; changed digest conflicts; peer restart
   cannot turn uncertain execution into a fresh launch.
4. Old peer/link/foreground/job/fixture bindings reject delayed records.
5. An event retention gap requires snapshot reconciliation; missing assertions
   or completion cannot become a pass from the latest progress value.
6. Return without completion, failed cleanup and deferred artifacts stay distinct.
7. Host disconnect/lease expiry leaves an executing fixture observed or unknown,
   never automatically cancelled/reset/restarted.
8. Unproved fixture memory and nested-MOSlet use reject before loading.
9. Queue/client exhaustion rejects or reports loss explicitly without unbounded
   allocation, application-output blocking or silent terminal eviction.
10. Before admission, state is unavailable; query silence cannot authorize reset.

All limits, source baselines and tests need review before the parent task marks
the implementation contract frozen. This draft changes no firmware or runner.

## Concrete contract proposals — review required

These details implement the accepted policy on paper. They are not yet accepted
wire assignments, released versions, current commands or implemented endpoints.
Q06-02 remains open until these proposals and the listed proof gates are resolved.

### Operator commands and disable behavior

| Proposed command | EMOS action |
|---|---|
| `EMOS DIAG STATUS` | Report execution enabled/disabled for this boot, current job and disable-pending state. No mode change or input admission. |
| `EMOS DIAG ENABLE` | At an empty top-level CLI, enable supported diagnostic job admission for this EMOS boot. Repeated enable returns current state. |
| `EMOS DIAG DISABLE` | Stop admitting new diagnostic offers immediately. Retire ungranted offers. If a job is granted/running/cleaning, mark disable pending and let that job reach its declared safe terminal boundary. |

Disable never injects Escape, resets hardware or interrupts a restoration interval.
It is separate from a cooperative cancellation request. On reboot the execution
enable flag is false, old grants are invalid and the host must reconcile uncertain
prior work. A reset is not a supported way to obtain cancellation success.

Read-only status remains available after ordinary Extender admission while
execution is disabled. Host HTTP requests cannot call ENABLE or acquire an EMOS
grant merely by writing a proposed enabled flag. Exact command parsing, error
codes and ROM cost require implementation-baseline review in agon-emos.

### Proposed private framing

Use the existing bounded F6 output and 8D input envelopes. The existing SD
admission/file protocol keeps its magic, kinds and operations unchanged. Its
offer/grant machinery remains the only launch authorization path. Add observation
and fixture records to the paired demultiplexers only after capability negotiation;
do not send an experimental record into an unnegotiated active ExCom parser.

A candidate observation/report record reuses the existing 20-byte header shape,
little-endian integers and 240-byte maximum, with distinct proposed magic `QC`:

| Offset | Bytes | Proposed field |
|---:|---:|---|
| 0 | 2 | Magic `QC`; distinct from `SD` |
| 2 | 1 | Candidate wire major, initially 1; not a released protocol version |
| 3 | 1 | Message class: observation request, observation response or bound fixture report; numeric assignment pending namespace audit |
| 4 | 4 | Negotiated control session, nonzero |
| 8 | 4 | Request/report sequence; no wrap into reuse |
| 12 | 1 | Operation: HELLO, SNAPSHOT, FRAGMENT or FIXTURE_RECORD; numeric assignment pending |
| 13 | 1 | Typed disposition |
| 14 | 2 | Payload bytes, maximum 220 |
| 16 | 4 | Existing SD CRC algorithm over header bytes 0–15 followed by payload; the CRC field itself is excluded |

This is a framing proposal, not permission to take a free-looking kind/opcode.
Audit both paired parsers, inactive/active ExCom handling and old-peer rejection
before assigning numbers. Observation HELLO negotiates read-only capability and
identity; it cannot grant a job or enable execution. Legacy-only safe bootstrap
and subsequent active-ExCom support must be proved independently.

A snapshot larger than one record is captured once, then sent as bounded fragments
of that same report. Fragment prefix: report ID u32, total bytes u16, offset u16,
whole-report CRC u32; at most 208 data bytes remain. Proposed total bound: 1024
bytes, one report buffer and one outstanding query per peer. All fragments must
match session/query/report identity, total and CRC. Reject overlap, inconsistent
duplicates, excess size and incomplete reports. Never publish a partial snapshot.
Duplicate fragment requests read the same captured report rather than combining
states captured at different times. Buffer expiry reports incomplete observation.

### Bound fixture-report envelope

The helper submits an active grant reference, local sequence, event kind and
bounded body through the resident gateway. EMOS validates caller context, copies
the body and stamps authoritative binding fields; a fixture cannot self-assert
another job's authority. Proposed EMOS-to-P4 payload:

| Offset | Bytes | Field |
|---:|---:|---|
| 0 | 16 | P4 boot identity |
| 16 | 16 | EMOS boot identity |
| 32 | 8 | Link generation |
| 40 | 8 | Foreground generation |
| 48 | 16 | Host job identity |
| 64 | 8 | EMOS grant identity |
| 72 | 32 | Exact fixture SHA-256 |
| 104 | 2 | Fixture result schema |
| 106 | 4 | Source record sequence |
| 110 | 1 | Event kind |
| 111 | 1 | Body bytes, at most 96 |
| 112 | 0–96 | Typed body |

Maximum payload is 208 bytes, below the proposed 220-byte framing allowance.
P4 appends its receive timestamp and journal sequence outside this payload.
The full tuple is evidence binding, not network authentication.

| Kind | Proposed body content |
|---|---|
| Start | Fixture schema and declared assertion-set digest |
| Progress | Phase code, completed/total work counters and optional bounded numeric detail |
| Assertion | Stable assertion ID, pass/fail, typed expected/observed values and units |
| Completion | Fixture disposition, assertion counts and artifact-manifest digest |
| Supervisor return | Load/launch/return disposition, return code and whether valid completion was seen |
| Cleanup | Cleanup/restoration disposition and EMOS resulting foreground generation |

The fixture result schema fixes assertion IDs, value encodings and units before
launch. Numeric enum assignments and per-kind body layouts remain schema work;
free text cannot replace typed assertions. A completion count/digest must agree
with retained assertions; missing records or overflow prevent a pass. Progress
may be coalesced, but the emitted source sequence must not manufacture a gap for
updates deliberately coalesced before emission.

### Initial queue, client and watchdog targets

1. One active EMOS job, one host launch lease, one event reader and one outstanding
   observation request per link. Reject a second owner; do not queue later launch.
2. Target 128 event slots of 256 bytes (32 KiB). The slot includes metadata;
   it is not an additional 256-byte body allowance. A missing old event produces
   an explicit cursor gap. A lost required assertion/terminal record prevents
   successful validation even if the latest snapshot says idle.
3. Target eight terminal slots, each holding job/descriptor identities, result,
   artifact-manifest hash and evidence acknowledgement state. Do not evict an
   unacknowledged terminal result to launch job nine. Exact slot bytes and crash-recovery format remain open. Accepted Q06-D08
   places the durable journal on P4-local SD for both DevKit and PC; RAM slots
   alone do not survive a P4 restart. Missing/full journal storage rejects new
   diagnostic jobs while ordinary operation and read-only status remain usable.
4. Target batches of at most eight events and 8192 encoded bytes. Serialize outside
   the 4096-byte HTTP task stack. One bounded pending send per reader; slow readers
   receive a gap/disconnect disposition rather than an unbounded queue.
5. Coalesce progress before emission to a target maximum four reports per second;
   assertions and terminal records are not silently coalesced. Timing fixtures
   report aggregate measurements outside timed regions where possible.
6. Target a five-second query watchdog, ten-second host heartbeat and thirty-second
   lease expiry. These are proposed liveness bounds, not completion/reset timers.
   An expired lease blocks new work; it does not revoke an executing EMOS grant
   or claim that cleanup occurred. Measure these targets before freezing them.

### Evidence export

The host writes one job bundle containing its request/descriptor digest, exact
P4/EMOS installation receipts and observed identities, negotiated schema and
capabilities, fixture identity and memory proof, lease/grant records, initial/final
snapshots, ordered events with gap markers, typed dispositions, durations and
artifact manifest. Each artifact entry carries purpose, path, size, SHA-256,
producer and collection/validation state. Physical-card collection is a supported
artifact path and never implies that missing raw data already validated.

Separate execution completion, cleanup completion, artifact completeness and
assertion validity. A bug report may retain a reproducible failure; successful
export means the declared evidence was copied and verified, not that the bug test
passed. Do not promise automatic upload to another person or service. Operator
export is explicit; machine-local addresses, credentials and unique-device access
recipes remain in private records rather than public diagnostic manifests.

A terminal result can be acknowledged for P4 retention release only after the
host verifies the required copied evidence. Interrupted export can reconcile
known hashes; it never reruns the fixture as an implicit collection retry.

### Candidate wire assignments

Within the proposed `QC` magic, reserve candidate classes 1=request,
2=response, 3=fixture report. Candidate operations: 1=observation HELLO,
2=snapshot capture, 3=snapshot fragment fetch, 4=fixture record. These numbers
remain draft allocations until both paired parsers and compatibility tests
prove the namespace. They do not modify `SD` control kinds or create a second
offer/grant channel. No prototype may advertise these as a released capability.

Each response echoes the session and request sequence. A snapshot-capture reply
returns report ID, total length and whole-report CRC; fragment fetch requests
carry report ID and offset. Fixture-report sequence belongs to the active grant.
Candidate dispositions are distinct success, unsupported version/capability,
not admitted, busy, stale identity, invalid length/CRC, expired report and
recovery required. Numeric disposition assignments need a complete codec table
before freeze; transport timeout is not an EMOS execution disposition.

### Candidate durable terminal-slot format

Use eight logical slots with two independent 512-byte copies per slot on
P4-local SD: 8192 bytes of record bodies, excluding filesystem allocation and
metadata. P4's storage owner serializes journal operations against local SD
HTTP, staging and any image consumers. Host APIs must not delete, replace or
rename live journal files behind that owner. Exact namespace reservation is
part of storage integration, not an inferred private mount path.

| Offset | Bytes | Candidate slot content |
|---:|---:|---|
| 0 | 4 | Magic `QJNL` |
| 4 | 2 | Candidate format major |
| 6 | 2 | Used record bytes, at most 512 |
| 8 | 8 | Slot generation, monotonic without wrap |
| 16 | 1 | Reserved, executing-uncertain, terminal or acknowledged |
| 17 | 1 | Terminal disposition, valid only in terminal/acknowledged state |
| 18 | 2 | Flags; unknown required flags reject recovery |
| 20 | 16 | Job ID |
| 36 | 32 | Descriptor SHA-256 |
| 68 | 16 | P4 boot identity |
| 84 | 16 | EMOS boot identity |
| 100 | 8 | Link generation |
| 108 | 8 | Foreground generation |
| 116 | 8 | Grant identity, zero before grant |
| 124 | 32 | Fixture SHA-256 |
| 156 | 32 | Required artifact-manifest SHA-256 |
| 188 | 32 | Terminal evidence-summary SHA-256 |
| 220 | 8 | Last retained event sequence |
| 228 | 4 | Record CRC, excluded from its own calculation |
| 232 | 280 | Reserved zero bytes; not an unbounded text field |

1. Before offering a job, P4 durably reserves a slot for its identity/digest.
   This permits truthful restart reconciliation even if power fails between
   EMOS granting the job and P4 recording that grant.
2. For each update, write the inactive copy with the next generation, flush,
   sync, close and independently reopen/validate it. Do not erase the prior
   valid copy as a prerequisite. Advertise durable success only after validation.
3. Recovery reads both copies and selects the highest valid generation. Invalid
   length/version/CRC/flags is not an empty slot. Conflicting same-generation
   copies or two invalid copies require explicit recovery, never formatting or
   silent overwrite. A first unused slot is created under an explicit initial
   journal-creation operation before diagnostic execution is enabled.
4. Reserved/executing records recovered after restart remain uncertain until
   reconciled with authoritative EMOS/job evidence. They are not permission to
   offer the same job again. A terminal record may recover execution outcome
   while event history remains incomplete; preserve those separate facts.
5. Host acknowledgement includes job ID, descriptor digest and the copied
   evidence-summary digest. P4 durably stores acknowledged state before the
   slot becomes reusable. A lost acknowledgement reply is resolved by status
   lookup or the same acknowledgement, never a new execution.
6. Media removal, write/sync/readback failure or capacity exhaustion stops new
   admission. If terminal persistence fails after a fixture returned, report
   execution outcome separately from `journal-write-failed`; do not pretend the
   terminal record is recoverable. Existing jobs follow their accepted cleanup.

CRC and two-copy storage detect/recover bounded torn-record cases; they do not
prove atomic FAT metadata updates, SD-controller power-loss guarantees or media
reliability. Qualify interruption at each write/sync/ack boundary on both boards
before claiming durable recovery. Never hot-remove the current P4 card to test
this draft without a separately approved physical procedure.

### Resource budget worksheet

| Component | Proposed fixed bound | Qualification still needed |
|---|---:|---|
| Event ring | 32768 bytes | Memory capability/placement and lock duration |
| Snapshot assembly | 1024 bytes per peer | Complete field encoding and coherent publication |
| Event response buffer | 8192 bytes | Escaping/serialization expansion and worker ownership |
| SD terminal record bodies | 8192 bytes total on media | Filesystem allocation, cache/workspace and I/O latency |
| Terminal staging buffers | Two 512-byte buffers | Storage-owner scheduling and stack placement |
| HTTP event requests | One asynchronous copy plus one worker | SDK allocation size, worker stack and disconnect cleanup |

The known RAM entries total 43008 bytes if a single 1024-byte snapshot buffer
is sufficient; peer-side copies, SDK request state, worker stack, journal cache,
locks and metadata are additional. This is a worksheet, not an approved 42 KiB
budget or permission to allocate these buffers on the shared HTTP stack.

### Implementation gates still open

| Gate | Required result before implementation freeze |
|---|---|
| Namespace and compatibility | Concrete negotiated opcodes, old-peer bounded rejection and paired parser proof |
| Identity | Boot/link construction, width, exhaustion and restart-collision rules |
| EMOS scheduling | Coherent state updates and response opportunities in each foreground context without ISR transmission |
| Memory | ROM headroom, supervisor return/memory proof, P4 event/snapshot/serialization placement and complete byte budget |
| HTTP | Accepted asynchronous bounded long-poll: prove bounded dispatch, slow-client isolation and exact request cleanup |
| Durability | Accepted P4-local SD journal: exact crash-recovery/ack/reclamation format and storage-lease integration, qualified on both DevKit and PC |
| Access | Explicit LAN/API access policy and control-owner enforcement; boot enablement is not authentication |
| Schema | Exact message enums and fixture assertion/body schemas |

Both DevKit and PC use board-profile-selected local SD storage. Qualify journal
restart recovery and missing/full media on each board. Include DevKit browser
video/input contention; an HDMI-only PC run is not equivalent evidence.

These gates fit existing Q06-02/04/05/06/07a/08 work; they do not create a second
implementation queue. The observation-only tranche needs only read-only framing,
identity, state publication and snapshot access; it does not need remote job launch
or all fixture schemas to be implemented first.

## Source map

1. [Shared HTTP configuration](../../../vdp/video/extender/network/http_video_service.hpp)
   and [server/send/close implementation](../../../vdp/video/extender/network/http_video_service.cpp)
   supply the bounded socket, stack, queued-send and cleanup observations.
2. [Wired endpoint registration](../../../vdp/video/extender/network/wired_network_service.cpp)
   supplies the existing keyboard WebSocket and status endpoint context.
3. [Finite admission contract](../REMOTE-005/ADMISSION-CONTRACT.md) supplies
   offer/grant identity, empty-CLI eligibility and input-wins prior art.
4. [Resident EMOS admission](../../../../agon-emos/src/emos_admission.c) and
   [utility loading](../../../../agon-emos/src/emos.c) supply the bounded
   interrupt-copy/foreground-decision split and existing loader guards.
5. [Original audit](AUDIT.md) and [parent task](../QUAL-006.md) retain research
   baseline identities and accepted decisions. This draft does not upgrade
   historical observations into a current installed-hardware claim.
