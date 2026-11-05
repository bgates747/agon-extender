# NET-003 — First matched application endpoint integration

Implement the existing generic message framework through a minimal admitted
EMOS endpoint and P4 worker, so MechAgon's native mainboard application can
exchange compact records with its Pi bridge. Keep game interpretation out of
resident EMOS/P4, preserve Legacy graphics and existing input/storage behavior.

## Authority and source boundaries

N03-MATCH-001 [x] Verify the all-owner accepted overnight coordination freeze:
MechAgon7681255 with plansb4ef6a2, exact contract hash retained privately.
The Author's verified driver/assistant mandate allows matched component work,
but physical/compute grants and existing policies remain separate.

N03-MATCH-002 [x] Publish this owner scope before code. Use maintained P4 source
and a separate agon-emos-owned Git worktree based on corrected Eirene16ec1f78.
Keep old branches, production selections, historical fixtures and private data.
The component task INTEG-019 owns EMOS implementation and mandatory link checks.

N03-MATCH-003 [x] Negotiate the concrete application/wire proposal with MechAgon
before dependent consumer code. Initial requested profile:128-byte opaque record,
two queued complete records per direction, normally10 per second each direction
with bounded lifecycle bursts; numeric IPv4/port supplied by the application.
Pi port7670 is consumer configuration, not a firmware constant. No observer JSON,
CRC/checksum, automatic replay or takeover of SD/controller identities.

## Accepted endpoint, implementation pending qualification

1. Existing MOS0x51/getfunction0x20 gateway, namespace ext, new provider net.
   A small C application include and documented raw gateway layout support both
   native C and assembly. Static ordinary application buffers, foreground and
   enabled IRQs only. No application ISR or callback is required.
2. Local OPEN returns a nonzero boot-local token; SUBMIT sends one correlated
   complete request at a time; TAKE returns one immutable complete correlated
   response without waiting; RELEASE revokes local admission immediately.
   Existing EMOS serializer and receive owner retain physical UART ownership.
3. Request kinds CONNECT, POLL and SEND. CONNECT carries IPv4/port, POLL yields
   current connect status or one complete RX record, SEND admits one complete
   record into P4 TX storage. A local/transport result never proves Pi game-turn
   execution. BUSY means not accepted and leaves the caller useful foreground
   work. A response timeout is uncertain and must not cause automatic replay.
4. A separate private variable-length VDU carrier and reply packet identify the
   new endpoint. Application library owns encoding/result validation. EMOS only
   checks fixed endpoint/version/length/caller/token/query and safely copies.
   Accepted header14 bytes: NM, version1, kind, token32LE, query32LE,
   payload length8, request reserved0/response status. Reply kind has bit7 set.
   CONNECT payload6 bytes (IPv4 octets, port16LE); POLL0; SEND0..128.
   P4 TCP framing remains length32LE plus opaque payload; no per-byte handshake.
5. P4 has fixed request/reply mailboxes and a worker-owned Channel<128,2>.
   Console only copies complete commands/replies under short synchronization;
   it never waits on socket I/O. Only the console owner emits UART packets.
   Worker owns connect deadline/cancel/link loss and per-pump operation budgets.
   No automatic reconnect. Experimental idle lease bounds abandoned sessions;
   accepted experimental connect1500ms, resident exchange250ms and abandoned lease2000ms.
6. Explicit local release or application exit must remain possible after fault.
   P4 worker revokes abandoned socket/session on its bounded lease; a new admitted
   CONNECT explicitly replaces prior incarnation without replaying queued work.
   No app pointer survives a resident call. Query exhaustion requires new local
   admission, not wrap/reuse. Actual ROM/static RAM cost is measured before flash.

## Implementation and evidence

N03-MATCH-004 [x] Implement shared constants, platform-neutral P4 appliance and
nonblocking worker integration behind an explicit default-off build option.
Preserve the current Ethernet owner, keyboard/VDU packet ordering and Legacy
mainboard routing. Never change monitor modes merely to initialize networking.

N03-MATCH-005 [x] Implement EMOS fixed endpoint and app-owned C codec/gateway
include. Reuse existing caller admission, serializer, ISR buffer, exit/fault
cleanup and controller-shaped host pipeline tests; do not import its semantic
code or allocate a game decoder. Keep official MOS/VDP references read-only.
Official MOS API baseline remains agon-docsf9806bd3, existing product gateway
contract and native Eirene source/linked UART-divisor checks control this work.

N03-MATCH-006 [x] Under Pi compile FIFO, run actual P4 peer + actual EMOS C +
actual application-client host pipeline with fake transport, unsafe-buffer,
backpressure, empty/full-binary, stale/wrong-query, failure and exit cases.
Compile native C application binding and full EMOS wrapper mandatory checks;
compile P4 source with actual SDK, then identified matched full build separately.
Record start/end, source/build pins, ROM/RAM and exact qualification limits.

N03-MATCH-007 [x] Publish logical checked source checkpoints. Preserve previous
accepted/installed bytes, task evidence and unrelated dirty work. Report the
actual usable interface and unsupported boundary to MechAgon immediately.

N03-MATCH-008 [ ] Before physical work, read current install/reset/SD/test protocols,
reconcile the post-manual-test bench/card/component state and obtain actual
exclusive custody. Freeze component-specific full backups, selective flashing,
independent readback and exact restoration or explicitly selected live handoff.
No autoexec edit, test-on-reset, Oryx use, premature graphical cue or uncertain replay.

N03-MATCH-009 [ ] Qualify finite generic endpoint echo and concurrent keyboard/
mainboard rendering before consumer integration under separately admitted plans.
No live arena/heavy run follows from a compile grant. MechAgon/Pi manager retain
consumer proof and live-demo duration/resource decisions. Never release a running
demo with idle checks; no production adoption or human optical pass is inferred.

## Current stop boundary

Publish the scope and negotiate the interface, then implement and verify software.
No actual device/network target, firmware write, reset, demo or heavy arena is
admitted by this document alone. Escalate only unresolved dependent choices;
continue independent authorized source preparation.

## First software checks — 2026-11-04

The actual P4 Peer, native EMOS C endpoint and public C client pass one composed
ASan/UBSan pipeline:128B binary and empty messages, two-slot backpressure,
wrong-query suppression,250ms expiry, explicit release, query65536 and exhaustion,
IRQ exclusion and an unsafe request pointer. Existing core and ephemeral IPv4
loopback checks also pass. Source tests do not establish physical timing.

The public C header compiles with ARM64-hosted AgonDev; disassembly confirms the
MOS0x51 leaf preserving IX/IY. Full native EMOS root firmware-check passes all
five existing linked gates, including both UART divisors. Unidentified native
ROM is130123B/free949B versus starting128159B/free2913B:1964B additional ROM.
The endpoint reserves148B native static RAM; no application pointer is retained.
Actual P4 console and network-service translation units compile with the pinned
native GCC/SDK headers and newly generated P4-PC board inputs. A full identified
P4 composition and physical qualification remain outstanding.

The local retained matched-host/build records preserve actual start/end and
commands. Migrated x86 host tools are not usable on Pi: an isolated native ARM64
compiler and Python environment are prepared without modifying the old cache.
Temporary setup compiler failures are not protocol or device failures.

## Candidate composition

Use a clean task-owned Git worktree of the checked Extender commit for an
identified P4 build, because unrelated scheduler documentation remains dirty
in the maintained checkout. Reuse pinned SDK inputs read-only; generated output
belongs only to this task. Explicit P4-PC/p4-console, ordinary stock-shaped HDMI,
controller input and dual USB host preserve input capabilities; do not enable
old rendering or parallel experiment flags by implication. This is a new
composition requiring fresh input/network qualification, not byte-identical
reproduction of the earlier installed PORT-008 derivative. Review the exact
manifest and coordinate matched deployment before any firmware write.

## Author correction — resident cost, 2026-11-04

The Author challenges the1964B resident increment and authorizes continuing
with offloading. The identified candidate is NOT deployed. Keep its frozen
bytes/source as comparison; do not broaden its qualification or overwrite it.
The linked symbol breakdown puts1707B in the new gateway alone, mainly duplicated
safe-copy/admission/session logic. P4 wire/TCP stays unchanged during reduction.

N03-MATCH-010 [x] Consult the consumer on reusing its existing MOS KBvector
callback for a bounded private NM reply, alongside native VDPL/keyboard work.
No second callback installation, direct UART/GPIO or hidden consumer change.

N03-MATCH-011 [x] Move reply storage, correlation, READY state, expiry and response
validation into the application include. Reuse the existing UART receive owner
and MOS callback; minimal resident code retains caller/buffer/carrier admission,
boot-local incarnation and serializer ownership. Snapshot/copy policy must be
explicit: application input remains stable through the foreground serializer
call; no application pointer survives it. App callback copies borrowed reply
bytes before ISR return and invokes no blocking service.

N03-MATCH-012 [x] Repeat actual endpoint/client pipeline and mandatory native
linked gates, preserving existing controller and keyboard behavior. Measure ROM
against both starting corrected Eirene and rejected-cost candidate. Publish the
replacement C header and exact changed EMOS identity before consumer linkage.
The full P4 build can continue because its wire format is unchanged. Actual
matched qualification and central custody remain separate.

MechAgon confirms its minimal client had no KBvector handler; the earlier
assumption that it owned VDPL callbacks was incorrect. It accepts owning one
bounded application handler, with previous-vector snapshot/chaining/restoration.
The maintained C/assembly pattern is specified in CALLBACK.md. OPEN output7
includes prior vector24LE alongside token32LE. Generic forwarding stays dormant
until first SUBMIT, after callback installation; no private vector address is
exported. The old-header unstarted native link reservation is cancelled.

Reduced source passes the actual peer/EMOS/app sanitizer pipeline, native C and
application router assembly compilation, and all five native linked gates.
The keyboard gate now also binds the new borrowed-payload callback bridge bytes.
Cold unidentified ROM129031B versus prior unidentified130123B:1092B saved.
Static network state is4B versus148B. Final identified r04 measurement follows;
compare like identity-string configurations before reporting baseline overhead.
The P4 cold build reaches final link but its15-minute outer watchdog expires;
owned IDF/Ninja descendants are confirmed stopped. Preserve its incomplete output
and frozen source; no full-build pass or candidate deployment is claimed yet.

Final identified r04 from native source5735812 uses129092B/free1980B. Against
installed identified r02 baseline128159B, the addition is933B; the first
identified network candidate used130184B, an addition of2025B. Like-for-like
saving is1092B (53.93% of the initial added ROM). All five linked gates pass.
The generic native echo fixture compiles/links23819B, with exact source/tool
manifest retained; no application/peer has been invoked on hardware.

N03-MATCH-013 [x] Finish the interrupted P4 native build using its existing,
unchanged generated ESP-IDF/Ninja project and exact frozen source17388d7f.
The wrapper's external watchdog expired after linking, before packaging; do not
pretend the original wrapper completed. Under a new finite compile reservation,
assert source/config/profile pins, resume serial Ninja only, then call the
canonical factory assembler and full action validator with the original flags.
Retain separate completion journal and exact output hashes, documenting this
one-time build recovery rather than creating a second editable source builder.
No hardware write follows merely from producing an ELF or action report.

P4 completion succeeds under fresh compile generation127:44.41s for serial
native resume plus canonical factory assembly/action validation. Frozen source,
SDK configuration, dependency lock, board inputs and identity remain unchanged;
source17388d7f, app1711424B. Original outer wrapper remains honestly recorded as
interrupted; its completion journal is separate. Owned build children joined
and both compute leases released. A byte-verified matched development package
retains P4 app/factory/proof, identified r04 EMOS, native fixture and public SDK.
This is software readiness only; no current bench component, installation,
physical API, input coexistence or game runtime is inferred.

RELEASE success proves NM disabled synchronously, independent of link/mode/fault.
A nonzero caller/gateway refusal does not prove disable. App-exit independently
resets admission, after app cleanup; do not claim an earlier callback restoration
is atomic with it. The consumer is given this precise limit and owns any selected
injected-refusal cleanup policy before testing that case. No hidden retry or new
resident fallback is added for hypothetical unsupported callers.

N03-MATCH-014 [x] Before selecting a RELEASE-refusal hardware case, agree the
application-owned terminal cleanup path with its consumer. Normal in-contract
close remains independent of physical failures. The shared close example keeps
its live router on refusal; no unconditional prior-vector restoration is taught.

N03-MATCH-015 [x] Preserve the existing browser reset controls in the candidate
before deployment. The first checked P4 composition omitted the private reset
URL metadata required by the browser; retain that build as software evidence,
but do not select it for installation. Use the maintained builder's existing
reset-URL argument, the machine-local configuration and a fresh identified output
from the same clean source. No transport or application ABI changes are needed.
Under a fresh serial compile reservation, retain the canonical complete build
and validator results, verify the embedded metadata against the private input,
and freeze a new matched development package. Keep the endpoint out of tracked
documents and preserve prior outputs. Allow a finite30-minute build watchdog
with owned process-group cleanup, rather than the insufficient15-minute wrapper
watchdog. This build does not grant physical reconciliation or deployment.

N03-MATCH-016 [x] Correct the generic echo appliance's inherited unconditional
callback restoration. On a nonzero RELEASE with an installed router, retain
that router and its static application memory, close the failure receipt, stop
network requests and wait with interrupts enabled for admitted owner recovery.
Do not return through unloaded application memory or automatically reset/replay.
Normal successful close still restores the prior callback and entry mode. Native
compile/link the corrected source under the serial build lease and preserve the
previous fixture bytes. Proposed fixture revision r02 awaits Author naming
approval before identified deployment; do not silently advance the registry.

N03-MATCH-017 [x] Finish the unchanged reset-configured P4 project after its
outer guard receives external SIGTERM at435.29 seconds, before canonical build
completion. The sender/cause is unknown; no thermal/RAM limit or hardware fault
is inferred. Native child-tree/start-identity inspection confirms no remaining
owned compiler after interruption. Ninja creates child process groups, so group
membership alone is insufficient cleanup evidence. Preserve the failed wrapper
journal, release its compile slot, and use a fresh finite reservation for exact
serial Ninja completion plus canonical assembly/action validation as in
N03-MATCH-013. Retain separate completion proof and reset-metadata verification;
never claim that the interrupted outer wrapper produced a complete manifest.

## Reset-configured completion and probe correction — 2026-11-05 UTC

Fresh compile generation130 completes the exact retained native project,
canonical factory assembly/action validation and corrected native probe check
in512.95s. Source17388d7f remains clean; P4 build
net-003-r01-b2026-11-05-01-16-07Z produces1711456B. Embedded reset metadata and
actual application bytes contain the unchanged private configured endpoint.
The observer follows742 actual child/start identities across process groups;
all children are stopped before release, next request null. The interrupted
generation129 wrapper remains failed evidence; no complete outer manifest is
fabricated. A separate verified local-only package retains completion proof,
P4 app/factory, unchanged identified EMOS r04 and unchanged public SDK.

The corrected probe compiles/links24093B with an explicit unversioned banner
and result identity. It is source-check evidence only and must not be deployed.
N03-MATCH-016 remains open for proposed r02 naming approval and an identified
build. No refused-close case is injected or hardware behavior claimed. MechAgon
accepts retaining its live app callback/static RAM in a reported terminal wait
on refusal, with IRQs enabled, no further requests and admitted owner recovery;
its corrected native r03 is separately built by its owner.

Driver questions about bounded post-manual reconciliation and the probe name
remain unanswered. No physical grant, reset, install, card access or application
invocation follows from these software passes. Current installed component and
foreground identities remain unknown; production selection is unchanged.

N03-MATCH-018 [x] Correct the discovered candidate composition mismatch before
installation. Native identified EMOS r04 links the existing parallel-pin startup
release owner, which gates all extender UART admission. The ordinary P4 candidate
omits that owner and cannot provide its reciprocal handshake. No flash has
occurred. Preserve the checked outputs as incompatible composition evidence;
do not deploy them or disable the EMOS owner to make admission appear successful.
Keep the933B EMOS endpoint and public SDK unchanged. Select the existing P4 boot
release implementation explicitly, without payload/probe/data/renderer experiments.
Extend the maintained clean identified NET-003 build selection narrowly for that
composition, verify the allowed/rejected selectors and canonical action closure,
then produce a fresh identified P4 build from clean committed inputs. Preserve
private reset metadata and dual USB/input selections. This source/configuration
correction grants no game invocation or production promotion. Notify the driver
of the concrete dependency and corrected component pins; no consumer ABI change.

The Author approves r02 and normal reset reconciliation on2026-11-05; no repeated
routine-reset approval gate applies. Identified probe source353c0ae5 builds24131B
and is independently staged/read back. Source7bbe2d59 adds a narrow clean build
selector for the required existing startup fence and rejects the boot-less named
network composition. All43 native/profile selector checks pass. Canonical full
P4 build net-003-r01-b2026-11-05-15-03-50Z completes in953.64s and its complete
action closure passes; application1759744B. Compile132 releases all child/start
identities and immediately hands the automatic133 grant to its actual owner.
The new verified local-only pair replaces the earlier incompatible selection.

Under actual bench generation36, full installed EMOS ROM equals checked r04,
and selective P4 application sectors are independently read/compared. Whole
expected P4 flash verification passes, preserving old sector tails and every
other region. This is not a second whole-device host read. Reciprocal startup,
fresh input and actual CLI/read/EXIT pass. Current startup and native text96
remain unchanged. Generic network invocation has not yet occurred at this
checkpoint; source/build/install proof is not end-to-end networking proof.

N03-MATCH-019 [x] Correct the generic probe's numeric endpoint parser after its
first actual invocation returns `Invalid numeric IPv4:port` at the MOS prompt,
before mode selection, OPEN or TCP connection. AgonDev's inherited libc scanner
consumes the terminating string NUL as a successful `%c`, unlike the host libc
assumption behind the trailing-character check. Keep the toolchain read-only;
use a bounded fixture-local decimal parser with explicit delimiters, octet/port
ranges, nonzero port and end-of-string check, covered by actual host C++ cases.
Build a fresh timestamped r02 from clean committed source under the Pi compile
lease; preserve the previous binary/capture as informative failure evidence.
Do not change EMOS/P4/SDK or advance the approved fixture revision for this
compatible correction. The host controller must recognize early application
error plus actual CLI return, close its own reader before asserting free ports,
and use fresh results/journals for the corrected explicit invocation. No replay
of the previous execution or reset is needed: actual CLI return is captured.
