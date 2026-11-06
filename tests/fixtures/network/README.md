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

The first r02 invocation returned cleanly at argument validation, before mode or
network activity. Its inherited AgonDev `sscanf` treats a string NUL as a
successful trailing `%c`; the fixture now uses `endpoint.hpp` for exact decimal
IPv4/port parsing. Preserve that failed build as evidence. Build the corrected
source with a fresh UTC timestamp under the same approved r02 identity. The
host controller must recognize early diagnostic plus actual CLI return and
close its own passive reader before checking for free USB ports.


## Prepared r03 carrier selection

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
