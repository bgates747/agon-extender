# R05-A03 — staged transfer admission contract

Date: 2026-09-27. Design for the next implementation tranche; no deployed wire
change. Builds remain on the existing SD contract until the paired endpoints
implement and negotiate this extension. Architecture authority is the accepted
Author decisions in REMOTE-005 and its linked proposed ADR.

## Scope and actors

EMOS controls safe-point eligibility, execution origin and the one admitted
mainboard job. P4 owns external HTTP requests, local staging and the sole P4
UART writer. Foreground utility or linked application helper performs mainboard
filesystem work. UART receive handlers copy/validate bounded control records;
no filesystem calls, utility launch or arbitrary callbacks in interrupt context.

The extension uses existing private F6/8D envelopes with explicitly separate
control-record kinds. No new VDU opcode, direct GPIO path or parallel-bus change.
Application code uses resident gateway calls, never the private UART sender.
Both Legacy and ExCom are target modes, with unchanged display route. ExCom
requires A02's active-parser and complete-packet changes before enablement.

## Job boundary — important for native clients

A job is one admitted filesystem operation/transfer, identified by P4 before
submission, not a TCP connection or an entire mounted WebDAV share. A server-side
recursive COPY/DELETE is one bounded job; a file manager's folder upload normally
consists of separate MKCOL/PUT requests and therefore separate jobs. Each request
must independently obtain admission. No atomic tree transfer or exclusive ownership
of a whole drag-and-drop gesture is promised. An application can run between
completed jobs; later external requests then receive busy, not delayed execution.

While a job owns mainboard service, competing mainboard work is rejected. Multiple
sockets do not acquire more owners. P4 may answer transport-level OPTIONS locally;
mainboard-backed metadata requests require admission too. Sending already completed
snapshot bytes requires no additional Agon filesystem operation. Busy behavior
with native clients' concurrent metadata requests is an explicit compatibility
test, not a presumed pass. Do not infer an authenticated user from IP/User-Agent,
and do not invent a client cookie requirement native file managers cannot satisfy.

## EMOS states

| State | External mainboard work | Application-origin work | Exit |
| --- | --- | --- | --- |
| UNAVAILABLE | Reject/offline | Fail unavailable | Successful transport/control handshake |
| CLI_NOT_ELIGIBLE | Reject busy | Only actual running caller may request via separate application state | Top-level editor reaches empty idle point |
| CLI_IDLE | Offer may be considered; not yet permission | Not applicable | Pending key/command, offer claim, mode/fault |
| EXTERNAL_CLAIMED | Only matching job; CLI dispatch held | Reject busy | Utility ready or failed-load cleanup |
| EXTERNAL_ACTIVE | Matching bounded operations only | Reject busy | Completion, cancel or failure |
| APPLICATION | Reject busy | Local caller may begin | App transfer admission or application exit |
| APPLICATION_ACTIVE | Reject busy, including reads | Only matching caller/job | Completion/cancel/failure returns to caller |
| CLOSING | Reject busy | Reject busy | Recovery-safe cleanup then prior CLI/application context |
| FAULT | Reject/unavailable | Fail with known/uncertain outcome | Explicit clean re-handshake; no old work replay |

These states supplement emosPolicy and emosBusy; neither existing field encodes
the safe CLI boundary or whole-job lifetime. CLI builtin/autoexec execution is
not CLI_IDLE. A public mos_editline call from an application is not CLI_IDLE.
User application transitions must not be confused with the owned utility launch:
service entry/leave carries a private expected-job context and must not erase its
own new grant when existing sdlink reset code runs.

## Admission sequence — external request

1. P4 accepts a host request as provisional, assigns a nonzero job ID and preserves
   exact operation/paths/overwrite conditions. No mainboard mutation, success reply
   or automatic deferred queue follows from this provisional receipt.
2. EMOS polls P4 only from the eligible top-level idle path. P4 returns NO_WORK or
   one OFFER bound to that poll and current link incarnation. Outside a current
   eligible window, P4 rejects external requests as busy/unavailable. A pending
   offer has a bounded admission deadline; it cannot outlive the originating
   request or transition into an application/partly typed CLI line.
3. On OFFER, EMOS rechecks empty line, pending keyboard event, execution context,
   mode, transport health and no job owner. A pending key wins. EMOS atomically
   claims the job or returns REJECT. Interrupt masking covers only state updates;
   it never covers UART waits or SD work.
4. EMOS exits the private CLI editor path with cleanup, then launches the finite-job
   utility. Utility-load failure reports REJECT/FAILED and restores a prompt. P4
   cannot send filesystem records until EMOS reports READY for the exact grant.
5. P4 stages upload content and computes CRC, then drives the existing checked
   file-transfer record sequence under that grant. EMOS executes only admitted
   operations. Admission occupies CLI even while the host upload is arriving.
   Download staging works in reverse before serving a complete snapshot.
6. At terminal result, P4 must have evidence of mainboard commit or declared
   recovery/error before reporting WebDAV success/failure. EMOS closes foreground
   ownership safely and redraws CLI. P4 retires provisional/active request state.
   No rejected, cancelled or skipped job is automatically resubmitted later.

Initial idle-poll candidate: at most once per mainboard VBlank/time advance,
not once per iteration of waitKey. This is a testable starting rate, not a final
performance requirement. Noneligible transitions invalidate the window and pending
offers immediately in EMOS. P4 stale knowledge may cause a failed offer, never
permission. Bounded deadlines are to be calibrated under A09; no unbounded wait.

## Admission sequence — application origin

The linked synchronous helper calls a resident BEGIN operation with requested
direction/path descriptor. EMOS establishes origin from local execution state,
not a field supplied by P4. Caller buffers and path lengths are copied/validated
before transmission. The helper remains loaded in the caller's own memory;
no second EMOSlet is loaded. No background callback is retained after return.

EMOS requests P4 staging/reservation for that application job. P4 must return busy
if another staging/transfer job owns the service. Only a matching reply is admitted;
P4 cannot convert an external pending offer into an application-owned operation.
The helper cooperatively performs mainboard work for the declared paths/direction,
using the same recoverable file semantics. It returns a defined result and releases
ownership. While active, all external mainboard requests remain busy.

Control/data API calls require foreground context with interrupts enabled, legal
buffers and complete VDU command boundaries. Caller application memory, registers
specified by the ABI and display route must survive. Exact C/assembly SDK function
signatures and supported caller modes are A05 implementation details, not permission
to bypass the existing gateway range checks.

## Control framing proposal

Reuse SD's 20-byte header, CRC and 240-byte maximum. Existing kinds 1–3 and
operations 1–11 keep their meanings. Proposed control kinds: 4 request, 5 reply.
Old sd_valid rejects these kinds; paired implementation must demultiplex them
before the old file-service validator. Do not send experimental controls to a
legacy-only peer without an identified capability/bootstrap handshake. Production
wire capability/version changes follow the version policy before build/deployment.

Control header: bytes 0–2 retain SD and major 1; byte 3 is control kind; bytes
4–7 are nonzero control session; 8–11 sequence; 12 operation; 13 result (requests
zero); 14–15 payload length; 16–19 existing CRC. Integer fields little endian.
Header session is control-channel identity, not a user account or file transaction.

Common payload prefix, 28 bytes:

| Offset | Size | Meaning |
| --- | --- | --- |
| 0 | 8 | link incarnation assigned by P4 handshake; zero only during HELLO |
| 8 | 4 | EMOS execution generation; increments on eligibility/owner transitions |
| 12 | 4 | P4 job ID; zero only for messages without a job |
| 16 | 8 | grant ID assigned by EMOS for an admitted job; zero until granted |
| 24 | 1 | origin: external or local application; descriptive, not authorization |
| 25 | 1 | requested operation class |
| 26 | 2 | flags/capabilities; unknown required bits rejected |

Remaining 192 bytes hold operation-specific negotiation or descriptor pieces.
A complete two-path descriptor may exceed one record under existing 120-byte
path limits. Use bounded descriptor fragments with total length, offset and final
checksum; refuse overlaps/out-of-range fragments. Freeze descriptor schema before
A04/A05 coding; never truncate paths or silently reduce supported path lengths.
No native C struct packing is the wire ABI.

Control operations (proposed values within control namespace):

| Value | Operation | Initiator and result |
| --- | --- | --- |
| 1 | HELLO | EMOS initiates fresh link negotiation; P4 returns new incarnation and capabilities |
| 2 | POLL | Eligible EMOS asks; P4 returns NO_WORK or bounded OFFER descriptor |
| 3 | DECIDE | EMOS grants/rejects exact offered job after recheck; P4 acknowledges |
| 4 | READY | EMOS utility ready; P4 acknowledges before any file records |
| 5 | APP_BEGIN | Resident EMOS requests application-owned staging job; P4 grants/reserves or refuses |
| 6 | DESCRIPTOR | EMOS requests/acknowledges bounded descriptor fragments |
| 7 | STATUS | EMOS polls job state/cancel request; P4 replies, never launches work |
| 8 | CANCEL | EMOS requests safe cancellation; reply distinguishes pending cleanup from terminal |
| 9 | FINISH | EMOS reports terminal file/job outcome; P4 acknowledges exact outcome |
| 10 | CLOSE | EMOS closes grant/window; P4 acknowledges retirement |

External disconnect/cancel is latched on P4 and returned on EMOS STATUS; Escape
is latched by the external foreground utility. Application helper does not impose
Escape behavior. Existing file records execute only under the active grant and
matching derived file session; opening that session must bind it to the job.
Manual sdserve keeps its explicit, separate lifecycle and cannot share the grant.

## Incarnation, retries and stale work

Each clean control HELLO rotates the P4 link incarnation and retires earlier offers
and grants. EMOS startup ignores old controls until completing a new handshake;
reset/transport fault closes admission and parser state. P4 restart invalidates
its old incarnation and requires a new EMOS handshake. Nonces identify runs, not
security credentials. Implement bounded collision/wrap handling; rotate before
sequence/job/grant counters wrap, never silently reuse identity.

Replies must match full link, session, generation, job, grant, opcode and sequence
as applicable. Reject mismatches without side effects. Duplicate identical messages
return cached outcomes; the same identity with changed bytes is a conflict.
Never retry an uncertain mutation as a fresh job automatically. Keep enough terminal
state to distinguish already committed from not executed until the peer acknowledges
or recovery takes over. Retained filesystem recovery records survive separately
from volatile control caches.

P4 may not use a pre-application OFFER at the next idle prompt: a generation change
invalidates it. HTTP client-initiated retry is a new explicit attempt subject to
current admission; that differs from a hidden P4 deferred queue.

## Results and cancellation

Control result domain: OK, NO_WORK, BUSY, OFFLINE, STALE, UNSUPPORTED, INVALID,
IO_ERROR, CANCEL_PENDING, CANCELLED, RECOVERY_REQUIRED. Freeze numeric values with
codec tests before firmware compilation. Existing file status values are unchanged.
Result must carry whether mainboard commit is confirmed, not merely staged on P4.

Suggested HTTP mapping: busy/temporary unavailability -> 503 with explicit reason;
lock/precondition conflicts -> method-appropriate 423/412; invalid path -> 400;
missing source -> 404; exhausted staging -> 507; IO/uncertain completion -> explicit
failure, never 2xx. Do not use 202 as a native client's substitute for completed PUT.
Check Finder/GVfs behavior before finalizing retry headers and timeouts.

Once activation starts, cancellation waits for a completed or recoverable boundary.
No deletion of the only good copy. CLI returns after cleanup; failure may leave
recovery artifacts. Completed directory entries stay completed. Successful staging
is removed when its serving/transfer lifetime ends; interrupted evidence is retained
only while needed. Staging deletion is not proof the mainboard transaction completed.

## Discriminating tests for A04–A09

A03-T01 [ ] Idle offer admitted; partly typed line/Enter/key-before-claim rejects
without changing input. No-key idle polling actually wakes service.

A03-T02 [ ] Public application editline and autoexec never grant external access.
Application entry invalidates a prior offer; returning to CLI cannot execute it.

A03-T03 [ ] Utility startup preserves granted job and loaded program region;
missing/wrong utility returns error without launching stale memory.

A03-T04 [ ] Application-origin upload/download uses no nested load; external offer
cannot spoof origin or change paths. Caller data and return state preserved.

A03-T05 [ ] Both modes carry complete SD records without injecting into a partly
consumed VDU payload; keyboard/reply prioritization and fault cleanup preserved.

A03-T06 [ ] Duplicate controls replay outcome only; modified duplicates, stale
incarnations/generations, wrong grants and wrap attempts never execute mutations.

A03-T07 [ ] Cancel before stage/during upload/during activation/during download;
retain only justified recovery state, no false success or later replay.

A03-T08 [ ] P4/EMOS reset, link fault, SD-full/missing, client disconnect and
concurrent native-client requests all retire or recover ownership predictably.

## Delivery boundary

A03 state/message design is delivered. Numeric/schema details explicitly marked
above are codec-freeze prerequisites within A03 before source implementation, not
implemented wire claims. No benchmark, emulator, firmware or hardware work occurred.
The job-per-operation definition and native-client concurrency tests prevent us
from accidentally promising a whole GUI folder gesture is one protocol transaction.
