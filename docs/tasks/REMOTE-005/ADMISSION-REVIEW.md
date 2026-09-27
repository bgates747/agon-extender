# R05-A02 — CLI, caller-memory and ExCom source review

Date: 2026-09-27. Source review only; no firmware edit, build, emulator or bench
run. These are implementation recommendations for the accepted behavior, not
claims of deployed support.

## Executive result

Feasible with bounded changes, but not by automatically typing `EMOS sdserve`
or merely deleting the Legacy mode check. Three changes are necessary:

1. A top-level-CLI-only escape from the stock line editor's key wait, with
   admission rechecked before launching the foreground utility.
2. An application transfer helper that does not load over a live MOSlet or
   application. Reuse the resident transport gateway; keep file work foreground.
3. P4 parser and sender changes for SD envelopes during active ExCom, in addition
   to the EMOS admission change. Existing P4 code explicitly excludes that path.

## Baselines and research scope

| Checkout | Revision / state |
| --- | --- |
| Official MOS | v3.0.2, 8336409351ee5314e02801a7b72a4f1bb5282519; clean. Remote v3 tags checked, including matching v3.0.2. |
| Official docs | f9806bd3cbff6ed5d1c08bef1d51fed11764b86b; pre-existing untracked `._.DS_Store` left untouched. |
| EMOS | 19486d7d01e9b3b31deb232f07fb042995b16513; clean. |
| Extender | 37625ada review-start checkpoint; maintained P4 source inspected, not an assertion of installed firmware identity. |

Read official docs/mos/API.md: line-editor API 0x09, OSCLI behavior, MOS API
calling modes and filesystem primitives. The documented editline result is
CR/ESC; do not change this public ABI for the private CLI wakeup.
EMOS src/mos_editor.c is byte-identical to the selected stock MOS source.
The authoritative current SD wire contract remains ../../protocols/mainboard-sd.md.

## Findings and source map

### A02-F01 — outer CLI loop is insufficient

EMOS main.c:245–258 calls mos_input, which calls mos_EDITLINE (src/mos.c:223).
mos_EDITLINE computes current line length then calls waitKey; waitKey loops until
keycount changes and keydown is nonzero (src/mos_editor.c:229,384). A before/after
hook around mos_input alone cannot admit a request while the prompt sits idle.
Applications also use the same editor through mos_api.asm mos_api_editline.

Recommendation: add a private CLI-aware entry/helper around the retained editor,
not a generic auto-service hook in public mos_EDITLINE or every waitKey caller.
At empty line/no pending key, permit a bounded idle-service poll and return a
private internal wake reason after normal editor cleanup. mos_input/main handles
that reason explicitly, launches foreground service, then redraws a fresh prompt.
Keep public API 0x09 CR/ESC behavior unchanged. Do not print the existing "Escape"
message or execute a synthetic command for the wake reason.

Use the existing editor's buffer, history, cursor and cleanup logic; no new line
editor. Free its tab-completion allocation before invoking utility code. Clear
top-level-CLI eligibility while processing a key, history/hotkey/tab work or a
command; applications calling an editor never become externally eligible.

### A02-F02 — policy is not an idle flag

src/emos.c emosPolicy records Core/MOSlet/application classification, with enter
and leave in mos_runBin (src/mos.c:283). Core includes executing CLI commands and
autoexec; it does not mean empty, idle prompt. emosBusy protects individual gateway
calls, not an entire transfer job. Neither can be reused unchanged as the new
external admission authority.

Recommendation: explicit small foreground admission state owned by EMOS, separate
from current policy classification. Atomically recheck CLI eligibility, empty line,
pending key and request identity before committing an external job. No FAT work
or long waits while interrupts are masked. Foreground single-thread dispatch
prevents a command/application starting after this claim; IRQ reception merely
records bounded state. Define the keyboard event at the admission boundary: an
already pending key wins; later keys belong to transfer UI/cancellation and must
not become a command executed after return. Do not promise buffered input the
stock single-event keyboard state cannot preserve.

External busy attempts must be rejected, not retained for execution after app
exit. P4 must distinguish unavailable from stale CLI advertisements; every job
requires EMOS authorization. A new request/boot identity and explicit rejection
retire any pending intent. Current presence is not this new authority.

### A02-F03 — idle utility loading exists; nested loading is intentionally barred

src/emos.c emos_run_utility (541) checks Core policy and loads only the fixed
0xB0000..0xB7FFF MOSlet area, with size/header checks, then uses stock mos_runBin.
It leaves normal application space intact within that memory contract. The
check prevents a running application or MOSlet invoking `EMOS sdserve` through
OSCLI. This is a real memory/lifecycle constraint, not a guard to delete casually.

Use that loader for CLI-origin service only, with a separate authorized transfer
owner preserved through the service's own enter/leave. Existing application
entry/exit resets sdlink (emos.c:240–269); new job state must distinguish expected
service entry from a user application, otherwise launching the service cancels
its own admission. Failure to load returns to a usable prompt. The current utility
runs indefinitely until Escape/EXIT; auto-dispatch needs a finite admitted-job
mode, not an indefinite listener takeover.

### A02-F04 — application-origin calls need foreground reusable code

The existing ext.sdlink gateway already accepts ordinary application and MOSlet
buffers within 0x040000..0x0B7FFF (src/emos_sdlink.c). It copies records into resident
buffers and retains no caller pointers. It is a bounded transport API, not a
high-level file-transfer API. Calling it does not prove an external operation is
permitted; the new origin/job contract must enforce that independently.

Recommended minimum: a synchronous application-side helper/SDK using EMOS
admission and gateway calls, with caller-owned foreground filesystem work and
bounded state. Factor reusable utility logic where justified. Keep the resident
API for authorization/transport; do not add the full file server to ROM or load a
second MOSlet over the caller. Require explicit requested paths/direction and bind
P4 responses to that operation; an application-owned transfer must never open a
general external directory server.

This fits the agreed synchronous behavior while avoiding a relocator, save/restore
loader or TSR. For a genuinely single-call high-level resident ABI, file orchestration
would need additional resident code or a separately reserved load region: not the
smallest first choice. Present the SDK/resident split explicitly before freezing
A03/A05. Native Z80 callers, pointer promotion, stack placement and gateway range
limits must be specified/tested; no claim that all current programs qualify.

### A02-F05 — ExCom has two deliberate exclusions

EMOS src/emos_sdlink.c:45 rejects any non-Legacy mode. It also requires healthy
Extender keyboard selection and UART ownership. Removing the mode guard alone
is insufficient:

- P4 video/extender/transport/console_hardware.inc:203–227 recognizes F6 SD
  envelopes in the inactive/preactivation parser only.
- The SD request sender at 265 explicitly requires !s.session.active().
- In ExCom, ConsoleStream feeds UART bytes to the retained VDU processor; no
  active SD receive dispatch was found in that path.
- EMOS's existing 8D receive dispatch is present independently in
  src/emos_keyboard.c:136. It is reusable, subject to admitted job ownership.

Recommendation: implement a narrowly scoped active-ExCom service-command handler
at the real VDU command boundary and enable reverse service packets through the
existing sole UART owner, behind complete replies/keyboard packets. Keep private
service bytes away from ordinary bitmap/text payload parsing. Do not scan raw
incoming bytes for F6 inside arbitrary data. Transmit packets only as whole
records; preserve timeout/fault behavior. No new GPIO/parallel operation needed.

Applications must call the transfer service at a completed VDU command boundary;
suspending halfway through a length-delimited bitmap/upload stream and injecting
a service command would corrupt it. Determine how admission can establish or
contractually require this boundary before enabling the new mode. Review any ISR
callback that writes display traffic against the existing transitioning lock.
This is a real qualification gate, not a throughput redesign.

### A02-F06 — existing service presence is not idle-CLI readiness

P4 storage/sd_service.hpp only sends after application presence, permits one pending
request and caches results; presence expires after five seconds. EMOS resets
admission on app entry/exit/fault. No listener means requests currently fail
unavailable. Therefore automatic CLI operation needs a small distinct readiness/
intent/admission exchange initiated or checked by EMOS at the safe point. Reuse
existing queue/retry idioms without letting stale presence authorize work.

Staging and WebDAV must not preempt or silently share an existing manual sdserve
session. Keep keyboard health/source prerequisite initially unless separately
changed; Legacy keyboard-on-mainboard-only access is not established by this
review. Busy, offline, unsupported mode and transport fault need distinct results.

### A02-F07 — Escape and cleanup mostly have existing foreground precedent

projects/sdserve/src/main.c polls Escape between service_request calls, then calls
service_stop and closes admission. File activation runs synchronously in service.c;
Escape cannot interrupt it through this main loop. That is a useful basis for
finishing/recovering activation before cancellation returns, but long individual
operations need defined responsiveness and progress boundaries.

Do not reuse that unconditional Escape policy in an application helper. The
application owns keyboard policy; a synchronous helper must document any optional
cooperative cancel check rather than promising the blocked caller keeps running.

## Proposed next coding order

1. Settle the SDK/resident split, then freeze A03 wire/state contract. Include
   safe CLI wakeup, finite-job identity and busy rejection without deferred replay.
2. Implement A04 private CLI hook plus host/emulator state tests. Keep stock editor
   behavior intact for apps, and test empty/partial/history/hotkey/Enter races.
3. Implement A05 application helper and memory sentinels, no nested MOSlet load.
4. Enable active ExCom framing on both ends with synthetic byte-stream tests;
   only then combine A06 staging and A08 WebDAV adapter. A07 directory work remains
   foreground utility scope. No bench until the existing deployment gate.

## Review conclusion

A02 source investigation is complete. No architectural need for external logic
ICs, background FAT ISR work or a resident WebDAV server was found. The concrete
question for Author review is whether the application-facing convenience call may
live in a small linked helper while admission/transport remain resident EMOS.
This is recommended; it is not yet implemented or silently accepted.
