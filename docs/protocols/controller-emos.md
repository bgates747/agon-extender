# Development controller read service

The mode20 Agon application reads controller state through a candidate resident
EMOS service. P4 retains button/D-pad transitions until EMOS has copied them to
the caller. This document describes the prepared checksum-free carrier2 and
96-byte application result. Source/software and target compilation checks pass;
this correction is not installed or physically qualified. The installed
CRC-bearing EMOSv0.1.25/P4r11/viewer-r02 combination loses controller and keyboard
input. [INPUT-001](../tasks/INPUT-001.md) owns naming, deployment and physical gates.
The [frozen carrier1 description](../tasks/INPUT-001/CONTROLLER-CARRIER-V1.md)
retains the earlier98-byte layout; the two combinations must not be mixed.

Under the [accepted Author policy](../decisions/ADR-2026-10-25-processor-link-crc-policy.md),
this controller path contains no CRCs or substitute software checksums.

The canonical byte definitions are
`vdp/video/extender/input/controller/appliance_wire.h` in Extender. EMOS's
`src/emos_controller_wire.h` is a mechanical copy, not an independent authority.
`scripts/sync_controller_wire.py` checks it; explicit`--write` regenerates it.
The application builder and pipeline tests also reject any drift.

## Processor ownership

1. The Linux sender publishes over the [controller LAN protocol](controller-lan.md).
   The P4 UDP worker stores coherent state and contiguous transitions.
2. The Agon application invokes the existing resident gateway, namespace `ext`,
   service `controller`. EMOS validates caller/buffers and owns the UART1
   serializer, receive ISR, resident cache and freshness deadline. The app never
   writes UART/GPIO or changes keyboard admission/display routing.
3. EMOS sends a typed `CI` request inside the existing F7/16 Extender control
   envelope. The P4 console owner recognizes that namespace in Legacy and
   ExCom. It requests state from the controller cache and alone writes the
   response on physical UART1 to the eZ80. The network worker writes no UART.
4. The response is encoded only when the console owner can enqueue it, so
   keyboard/VDU backpressure does not give a previously encoded snapshot a fresh
   timestamp. Keyboard/reply packets retain their complete-packet boundaries.
5. No global MOS call or getfunction index is added. The application build
   mechanically generates bindings from maintained EMOS `mos_api.inc` and
   verifies matching EMOS/P4 carrier-header bytes. It does not fork an SDK ABI.
   Reply type8E is Extender-local, not an upstream VDP assignment.

## Resident gateway candidate

Use the existing66-byte gateway ABI1/service operation2. Input is one byte;
all request/input/output memory must be ordinary application RAM below0xB0000.
MOSlet/Core/ISR callers are excluded. The existing application lifecycle clears
the controller cache/lease on entry, exit and keyboard transport fault.

| Input byte | Operation | Output |
|---:|---|---|
| 0 | OPEN | None; allocate a new boot-local caller token and clear controller cache |
| 1 | READ | Exactly96bytes; copy the latest resident snapshot without waiting for UART or a reply |
| 2 | REQUEST | None; send one bounded UART request without waiting for a reply |
| 3 | CLOSE | None; clear the lease and send a best-effort typed close while the transport is healthy |

The caller requires existing healthy `EMOS KEYINPUT extender` admission and
Legacy or ExCom. The application cannot admit its own disabled keyboard path.
The service borrows the existing serializer, not the SD listener/lease. Missing
old-firmware service returns the normal gateway unavailable/not-found result.

READ before a response, or while a refresh is outstanding, returns busy31. REQUEST while a response is outstanding
or waiting to be read returns busy31. A request expires after30 nominal MOS
clock units; expiry invalidates the lease and requires an explicit reopen.
READ also rejects source age plus conservative local cache age reaching250ms.
These are uncalibrated nominal-clock bounds, not measured physical latency.
REQUEST can encounter the existing UART serializer's bounded CTS wait; only
READ is a nonblocking copy. A failed partial send is not replayed automatically.

The existing EMOS VBlank owner checks outstanding/cache deadlines even while
the application is busy. A delayed reply cannot revive an expired lease after
the low-byte clock wraps. At reception EMOS bounds return transit using the
request round-trip, with an extra whole-tick phase margin. Source age exceeding
the bound clears validity/values, while a responsive carrier may continue.

EMOS validates response length, magic, caller/query identity, flags, held
mask and transition bounds before publication. No application pointer is kept
by the ISR. READ copies retained transitions once, advances its acknowledgement
cursor after the copy, and clears those transition records in its cached copy.
Repeated READ returns the cached state with no duplicate transitions when no
refresh is pending. The app also checks source identity and transition IDs.

READ holds the interrupt lock only for admission/metadata checks and the final
post-copy acknowledgement. While waiting for a reply, READ returns busy rather
than copying a previous cache. With no request outstanding, the resident cache
cannot be republished by the UART owner until a later foreground REQUEST.
EMOS copies and normalizes the result with interrupts enabled, then revalidates
lease/transport health and records consumption in a short locked section.
Tick/fault cleanup invalidates flags without modifying the cache bytes.
The request timestamp is stored before arming its waiting flag.

## Typed console request:16 bytes

UART1 forward framing is `23,0,F7` followed by the complete16-byte body.
Integers are little-endian. The existing fixed-size F7 carrier remains16bytes;
its final two bytes are reserved zero, not a checksum. Changing that shared
carrier would require a separate console-framing change.

| Offset | Bytes | Meaning |
|---|---:|---|
| 0 | 2 | ASCII `CI`; distinct from console activation's `EX` |
| 2 | 1 | Carrier version2 |
| 3 | 1 | 1 request;2 close |
| 4 | 4 | Nonzero EMOS caller token |
| 8 | 4 | Highest transition copied to application memory |
| 12 | 2 | Nonzero query sequence; never wraps within a lease |
| 14 | 2 | Reserved zero |

Tokens are boot-local ownership/correlation, not authentication. UART admission
and reset boundaries still need physical qualification; no cross-reset security
or fully qualified stale-byte recovery claim is made here. A sequence exhausted
at65535 requires a new lease. A different caller token replaces only the private
appliance request, not the Linux sender or keyboard capture session.
The viewer renews a healthy lease at65000, preserving source identity and press
counts. This does not automatically reopen after loss/expiry.

P4 retires a transition only on a subsequent request from the same caller and
the source session whose response P4 delivered. A changed UDP source session
cannot apply an acknowledgement from the preceding source. An impossible future
acknowledgement receives no response; the EMOS request expires. Dropping a UART
response therefore leaves P4's queue intact. The128-record bound and explicit
overflow failure remain in force.

## Controller result:96 bytes

UART1 return framing is `8E,96` plus this body. READ returns that body through
the gateway. Source identities are opaque bytes to the eZ80; no LAN datagram
header or64-bit arithmetic is required there.

| Offset | Bytes | Meaning |
|---|---:|---|
| 0 | 4 | ASCII `CIS2` |
| 4 | 4 | Echoed caller token |
| 8 | 2 | Echoed query sequence |
| 10 | 1 | Bit0 source active, bit1 source valid; other bits zero |
| 11 | 1 | Transition count0–8 |
| 12 | 8 | Opaque P4 receiver instance |
| 20 | 8 | Opaque admitted LAN source session |
| 28 | 4 | Latest LAN state sequence |
| 32 | 2 | P4 observation age on wire; EMOS augments it with a conservative return-transit bound at cache publication |
| 34 | 2 | Held mask, same logical controls as LAN |
| 36 | 8 | Four signed16 sticks: left X/Y, right X/Y |
| 44 | 2 | Unsigned8 left/right triggers |
| 46 | 2 | Reserved zero |
| 48 | 48 | Up to8 transitions: sequence u32, control u8, down u8; unused records zero |

Invalid source state has neutral axes/triggers, no held controls and no queued
transitions. Consumers must inspect validity. Source/session changes clear the
application's count baseline; ordinary expiry retains its previous observed
count for inspection. Consumer flight/throttle/pause policy is unchanged.

The Agon viewer requests at most one refresh per two nominal sysvar units and
repaints every six. With the usual two-unit60Hz VBlank clock, that is nominal60
requests/s and20 repaints/s. Linux publication remains120Hz independently.
Repeated cache reads and drawing rate are not controller USB report rates.

## Validation boundary

The portable P4 peer test verifies queue retention, explicit consumption,
delayed encoding, source change and expiry. The resident C-service test verifies
cache coherence, malformed/stale replies, caller/IRQ/mode refusal and expiry.
The native pipeline test links the actual P4 receiver/peer, actual resident C
service and actual application client with only UART/clock/gateway hardware
boundaries replaced. It proves software interoperability. A separate linked-image instruction test
reproduces the old masked-read FIFO failure and verifies pending-read refusal,
a coherent unlocked copy and Escape delivery with the correction. Its bounded
arrival model does not calibrate physical UART timing or qualify the bench.
