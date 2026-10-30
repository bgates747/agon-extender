# Development controller transport

Applications interpret controller input through the reusable [controller API](../controller-api.md); resident EMOS supplies a small admitted transport endpoint. This development source changes the application/EMOS gateway to operations 4–7 while preserving P4's CI2/CIS2 UART bytes. The new application include and reduced EMOS endpoint require a matched build. No new physical installation or hardware acceptance is claimed.

The earlier physically reviewed viewer-r03/EMOSv0.1.27 combination uses gateway operations 0–3 and a 96-byte application result. Its complete contract is [frozen separately](../tasks/INPUT-005/CONTROLLER-GATEWAY-V1.md). Those installed bytes and their evidence remain unchanged. The reduced endpoint rejects old operations; the new client also fails clearly against the earlier endpoint. Selected production remains unchanged.

The canonical definitions are `vdp/video/extender/input/controller/appliance_wire.h`. EMOS's `src/emos_controller_wire.h` and the embedded block in `include/agon/controller.hpp` are mechanical copies. `scripts/sync_controller_wire.py`, the viewer builder and pipeline checks reject drift. The viewer builder also checks the public include's existing MOS gateway/function constants against maintained EMOS `mos_api.inc`; no global MOS call or function index is added.

Under the [accepted processor-link policy](../decisions/ADR-2026-10-25-processor-link-crc-policy.md), this path contains no CRC or substitute software checksum. The two gateway timing bytes described below are metadata, not a checksum trailer.

## Processor ownership

1. P4's controller acquisition adapters normalize the admitted USB or [LAN source](controller-lan.md). The P4 controller receiver stores coherent state and contiguous button/D-pad transitions. Application code contains no USB device IDs or physical report decoders.
2. The eZ80 application invokes `ext.controller` through the existing resident gateway. EMOS admits caller/buffers, owns UART1 serialization and reception, correlates one outstanding request, retains one reply and enforces transport lifetime. No application pointer or callback survives a gateway call.
3. The application library encodes a typed `CI` request. EMOS admits only that fixed controller endpoint and transmits the complete request through its existing serializer over the wired eZ80 UART1/P4 console connection. P4's console owner receives the request and alone transmits the reply; P4's USB/network acquisition workers never write that UART.
4. P4's console owner encodes state only when it can enqueue a complete reply. Keyboard/VDU backpressure therefore cannot give a previously encoded snapshot a new observation age. Keyboard and service packets retain complete-packet boundaries.
5. EMOS copies the raw reply with interrupts enabled. The application library validates the complete controller result before changing accepted source/edge/count state. It alone applies source age, local age, neutralization and the edge acknowledgement carried in the next request.
6. EMOS retains ordinary VDU routing, keyboard admission and committed mode. Controller and SD leases/mailboxes remain independent even though their transports share EMOS's UART owner. Applications cannot borrow the SD lease or take UART/GPIO ownership.

## Resident gateway

The service uses the existing 66-byte gateway ABI 1/service operation 2, namespace `ext`, provider `controller`. Its request and complete input/output buffers must lie in ordinary application RAM `0x040000..0x0AFFFF`. Keep the public `Client` in static application storage; the MOS-owned call stack is not suitable. Core, MOSlet and interrupt callers are excluded, and foreground calls require enabled interrupts.

| Input operation | Input bytes | Output bytes | Resident EMOS action |
|---:|---:|---:|---|
| 4 OPEN | 1 | 4 | Allocate a nonzero boot-local token and admit one caller |
| 5 RECEIVE | 1 | 98 | Copy one untouched 96-byte CIS2 reply followed by two raw timing bytes |
| 6 SEND | 20 | 0 | Admit and serialize the application's complete fixed 19-byte CI envelope |
| 7 CLOSE | 1 | 0 | Revoke local admission and discard pending state |

The first input byte is the operation. SEND's remaining 19 bytes are `23,0,F7` plus the complete 16-byte CI body below. EMOS checks the fixed prefix/version, request-or-close kind, current token and nonzero query. It does not interpret controller flags, controls, source identities or transitions. P4 retains its own body validation.

OPEN returns a 24-bit counter encoded as little-endian u32 with its high byte zero. EMOS never reuses a token within a boot and refuses counter exhaustion. Tokens correlate ownership; they are not authentication.

OPEN and traffic require healthy pre-existing `EMOS KEYINPUT extender` admission and Legacy or ExCom. The application cannot enable a disabled path or change display routing through this service. CLOSE still revokes local admission after mode change, expiry or transport failure, subject to its caller/buffer/interrupt checks. The library attempts a typed CI close while healthy, then always requests local CLOSE even if that send fails.

EMOS admits one outstanding request and one unread reply. RECEIVE returns busy 31 while waiting or without a reply; successful RECEIVE consumes that reply once. SEND request returns busy while either exists. An admitted typed close may cancel pending state. The endpoint rejects old gateway operations 0–3 with invalid parameter 19; an absent service retains the gateway's normal unavailable/not-found behavior.

An outstanding request or unread reply expires after 30 nominal MOS clock units. EMOS's existing VBlank owner enforces expiry while the application is busy, so a late reply cannot revive an expired lease after low-byte clock wrap. Application entry/exit and keyboard transport faults also revoke admission. A failed partial send is never replayed automatically. SEND can encounter the existing serializer's bounded CTS wait; RECEIVE does not wait for UART data.

The receive ISR accepts exact-length replies matching the current caller/query. It copies the raw body into resident storage without interpreting its magic or controller fields. RECEIVE copies that immutable storage with interrupts enabled, appends timing metadata, then revalidates lifetime/transport health in a short locked section before publishing success. Tick/fault cleanup changes admission state, not bytes being copied.

## Typed console request: 16-byte body

Forward UART framing remains `23,0,F7` followed by this body. Multibyte integers are little-endian. The fixed F7 body remains 16 bytes; its final two bytes are reserved zero.

| Body offset | Bytes | Meaning |
|---:|---:|---|
| 0 | 2 | ASCII `CI`, distinct from console activation's `EX` |
| 2 | 1 | Carrier version 2 |
| 3 | 1 | 1 request; 2 close |
| 4 | 4 | Current nonzero EMOS caller token |
| 8 | 4 | Highest transition fully validated and accepted by the application library |
| 12 | 2 | Nonzero query sequence, unique within this lease |
| 14 | 2 | Reserved zero |

The application library allocates query sequences and renews a healthy lease at 65000, before exhaustion at 65535. Renewal preserves accepted source identity and press counts. Faults and expiry require explicit close/open; the library never silently reconnects.

P4 retires transitions only on a subsequent request from the same caller and the source session whose response P4 delivered. Source change cannot apply an acknowledgement from the previous source. An impossible future acknowledgement receives no reply, and the EMOS request expires. A dropped reply therefore leaves P4's transitions queued. The 128-record bound and explicit overflow failure remain unchanged.

The application library validates the entire reply, including every transition and reserved/unused bytes, before committing source changes, counts or acknowledgement. Malformed or stale contents never acknowledge a valid prefix. Duplicate transition IDs do not count twice. A changed P4 receiver/acquisition-session identity resets the application's count baseline and accepted edge cursor. Ordinary source expiry preserves already observed counts for inspection.

## Controller reply and gateway timing

Return UART framing remains `8E,96` plus the following body. Type 8E is Extender-local, not an upstream VDP assignment. Neither P4's physical envelope nor the CIS2 layout changes with this gateway revision.

| Body offset | Bytes | Meaning |
|---:|---:|---|
| 0 | 4 | ASCII `CIS2` |
| 4 | 4 | Echoed caller token |
| 8 | 2 | Echoed query sequence |
| 10 | 1 | Bit 0 source active, bit 1 source valid; other bits zero |
| 11 | 1 | Transition count 0–8 |
| 12 | 8 | Opaque P4 receiver instance |
| 20 | 8 | Opaque admitted acquisition-session identity |
| 28 | 4 | Latest source state sequence |
| 32 | 2 | P4 observation age in milliseconds, unchanged by EMOS |
| 34 | 2 | Held mask, with the normalized logical controls |
| 36 | 8 | Four signed 16-bit sticks: left X/Y, right X/Y |
| 44 | 2 | Unsigned 8-bit left/right triggers |
| 46 | 2 | Reserved zero |
| 48 | 48 | Up to 8 transitions: sequence u32, control u8, down u8; unused records zero |

An invalid source has neutral sticks/triggers, no held controls and no transitions. The application library validates these conditions and exposes validity separately from source activity. The 16 identity bytes are opaque to the eZ80 application; no LAN header or 64-bit arithmetic is required there.

RECEIVE appends these bytes only in application memory:

| Gateway offset | Bytes | Meaning |
|---:|---:|---|
| 96 | 1 | Raw request-to-reception delta in nominal MOS clock units |
| 97 | 1 | Raw reception-to-copy delta in nominal MOS clock units |

The public library reproduces the conservative freshness bound:

```text
age = P4 source age + ((round-trip ticks + 2) + (cache ticks + 2)) * 9
```

Each local delta has its own whole-tick phase allowance. Round trip conservatively bounds reply transit; it is not a measured one-way delay. The multiplier and 250 ms rejection threshold are nominal policy, not clock calibration or measured controller latency. The library additionally ages its retained sample from the application clock on subsequent `update()` calls, including while waiting for a reply. At the bound it clears validity/held/sticks/triggers without fabricating presses or acknowledging stale transitions. A responsive carrier can remain open while its source is invalid or stale.

## Software validation and physical boundary

The portable P4 peer checks exercise retained edges, source change, delayed encoding and expiry. The resident endpoint checks cover caller/memory/IRQ/mode admission, correlation, one-shot delivery, expiry and coherent copies. The public-header model checks cover controller validation before ACK, source/count handling, stale neutralization, local clock wrap, cleanup and healthy renewal. The native pipeline links the actual P4 peer, resident C endpoint and public application client with UART/clock/gateway hardware boundaries replaced.

These checks and AgonDev compilation establish software compatibility for the new matched source. They do not establish physical UART timing, controller-to-display latency, arbitrary device compatibility or a newly installed combination. Earlier physical and instruction results remain attached to their exact builds in the [controller integration evidence](../tasks/INPUT-001.md); the [application extraction task](../tasks/INPUT-005.md) owns the new offline work and its deployment boundary.
