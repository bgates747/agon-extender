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
   `RUN IPv4:port /agents/extender/results/FRESH.txt` through the admitted CLI.
   The fixture owns conditional mode lifecycle; runner preselection instead owns
   earlier restoration and its own minimum one-second delay.
7. Escape cancels all foreground waits. An uncertain SEND is never retried.
   P4's abandoned lease closes the socket after local release. Both Agon result
   and Pi result must pass; record callback/mode/CLI restoration independently.
8. Clocks are separate: Agon reports nominal120Hz units, Pi reports monotonic ns.
   They are not synchronized latency measurements. The finite socket/run bounds
   are failure gates, not estimated time or permission for resets/replays.

Current state: original and corrected close-refusal native compile/link pass;
the corrected source-check build is explicitly unversioned. Approval of proposed
fixture revision r02 and an identified build remain pending before deployment.
The earlier binary remains preserved and is not selected for deployment.
NET-003 owns matched component qualification and custody; no standalone demo
readiness or production acceptance is claimed.
