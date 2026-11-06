# Generic finite network echo appliance

This fixture exercises opaque messages through the matched application/EMOS/P4
endpoint while mainboard mode20 remains visible. It contains no consumer game
schema. Source preparation does not authorize deployment or invocation.

1. Build `main.cpp` with the public `include/agon/net.h`, application router
   `include/agon/net_callback.asm`, existing controller fixture `mos_io.asm`
   and existing scroll `mode_lifecycle.hpp`. Preserve exact source pins.
   Pass the approved fixture identity and actual UTC timestamp with `--build-id`;
   the builder embeds it in the start banner, durable result and build manifest.
   The default unversioned build is for source checking and must not be deployed.
2. The fixture queries/saves entry mode, conditionally selects mode20, waits at
   least one monitor-settling second after switches and restores entry/CLI.
   Double-buffered entry is explicitly refused by the reused lifecycle helper.
3. OPEN snapshots the previous MOS callback, then the fixture installs its router.
   Only NM is consumed; all ordinary callback events chain. Release precedes
   previous-vector restoration on completion, cancellation and failure. A refused
   release retains the live router/static memory, records the failure and waits
   with interrupts enabled for admitted owner recovery; it never returns or
   automatically resets/replays. No refused-release injection is selected.
4. Deploy only beneath `/extender/network` with results beneath
   `/agents/extender/results`. Never change startup. The result path must be fresh.
5. The Pi echo peer starts explicitly with an admitted numeric LAN bind/port and
   new output directory. It accepts one client and exactly four independent byte
   fixtures of length0,1,56,128. No game, emulator or automatic app invocation.
6. Explicit MOS invocation is `LOAD /extender/network/netprobe.bin`, then
   `RUN &040000 IPv4:port /agents/extender/results/FRESH.txt` through the admitted CLI.
   The fixture owns conditional mode lifecycle; runner preselection instead owns
   earlier restoration and its own minimum one-second delay.
7. Escape cancels all foreground waits. An uncertain SEND is never retried.
   P4's abandoned lease closes the socket after local release. Both Agon result
   and Pi result must pass; record callback/mode/CLI restoration independently.
8. Clocks are separate: Agon reports nominal120Hz units, Pi reports monotonic ns.
   They are not synchronized latency measurements. The finite socket/run bounds
   are failure gates, not estimated time or permission for resets/replays.

Current state: Author approves r02 on2026-11-05. Corrected clean source74bb87c4
builds network-echo-probe-r02-b2026-11-05-15-38-40Z,16207B, and completes one
physical four-record pass through Agon/EMOS/P4/Pi. Durable app and peer records,
mode0/callback restoration, actual CLI and startup/resource handback are retained
under NET-003. Earlier parser-failed bytes remain preserved and unselected.
No Escape/fault/controller exercise, optical pass or production acceptance follows.

## Independent graphics-cycle source variant

The explicit builder option `--graphics-cycle` adds ordinary counted mainboard
VDU line drawing and one mode-query completion after each0/1/127/128-byte echo.
The next network request follows that completion. The result records four raw
query tick intervals in nominal120Hz units, distinct from rendering time and
optical output. It uses the existing four-record peer with
`--sizes 0,1,127,128`. Default builds retain their original workload.

This source variant belongs to NET-004's independent carrier investigation;
it is not an extra MechAgon final attempt or a guarded RFC25 test. The first
compiled parallel variant passes one physical four-record/four-draw control
on2026-11-06; NET-004/INDEPENDENT-RESULT-R01.md records exact scope and restoration.
This does not clear the renderer defect. No module, sprite, raw peripheral access,
automatic replay or new callback is added by the option.

The separate explicit `--rfc25-cycle --carrier parallel` variant uses one
static67B packet containing four ordinary line sequences and a trailing point
query. It prearms the source-release and point flags before one guarded25 call,
and waits for both before another network operation. The ISR only stores the
source-release flag; it is not a drain or optical completion API. Unknown
admission or an outstanding source at timeout retains application RAM/code with
interrupts enabled, without further MOS/output/network cleanup or a return.
The host must preserve that original invocation and recover normally; no replay.
The builder excludes combining this option with the ordinary-graphics option
or UART carrier. Its source/build and later physical boundaries are in
`docs/tasks/NET-004/CARRIER-RFC25-CYCLE-R01.md`; no hardware result is inherited.
The first explicit build passes actual state/packet sanitizer checks and native
linking at17953B/d04442f1. Its exact source/build manifest is retained in
`docs/tasks/NET-004/RFC25-CYCLE-MANIFEST-R01.json`; physical staging/invocation
still requires a new owner package and fresh actual checkout.

The first r02 invocation returned cleanly at argument validation, before mode or
network activity. Its inherited AgonDev `sscanf` treats a string NUL as a
successful trailing `%c`; the fixture now uses `endpoint.hpp` for exact decimal
IPv4/port parsing. Preserve that failed build as evidence. Build the corrected
source with a fresh UTC timestamp under the same approved r02 identity. The
host controller must recognize early diagnostic plus actual CLI return and
close its own passive reader before checking for free USB ports.


## Built r03 carrier selection

The builder's explicit `--carrier parallel` selects the public netp include,
application-owned whole-record buffers and no NM callback/router object. The
default `--carrier uart` retains the UART callback adapter. Both variants share
the existing endpoint parser, mode20 lifecycle, Escape, fresh result paths and
explicit invocation. Source preparation is not a physical pass or deployment.

The parallel variant uses0/1/127/128-byte payloads; start the same finite echo
peer with `--sizes 0,1,127,128`. Before consuming each pending reply it requests
a13-byte output, checks required size/no-consume, then takes the whole reply.
The durable record identifies carrier and size-check count. RELEASE polls only
BUSY within the finite close bound; a refused/uncertain payload is never replayed.
A failed close retains storage for owner recovery. NET-004/QUALIFICATION-R01.md
owns preparation and the later selected component/bench handoff. Preserve r02
accepted binaries/results; r03 has no inherited physical acceptance.

Both variants compile from clean dd933691. The parallel00:34:43Z build is16567
bytes; no hardware r03 run occurred. Exact identities are retained by NET-004.

## Finite repeated matrix preparation

`build.py --carrier parallel --repeat-matrix` selects the separate176-record,
four-session source; `--rfc25-cycle` additionally selects guarded67B UART0
batches. The original four-record source is unchanged. The finite peer is
`repeat_peer.py` and the bounded work/physical gate is
[PARALLEL-001](../../../docs/tasks/PARALLEL-001/REPEAT-MATRIX-R01.md). This is
source preparation, not a qualified deployment or default bench recipe.
