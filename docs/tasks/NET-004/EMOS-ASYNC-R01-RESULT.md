# Provisional UART1 adaptation — offline result

The first application-owned EMOS adaptation passes actual-source sanitizer tests,
an eZ80 application link and every selected native firmware validator. The engine
remains in application RAM. This is a checked provisional consumer binding, not
a physical async-performance/30 Hz result. The subsequent first physical trial
failed with receiver overrun; its [physical result](EMOS-ASYNC-PHYSICAL-R01-RESULT.md)
records exact evidence and complete working-ROM restoration/release.

## Exact scope and sizes

| Byte scope | Synchronous control | Provisional async | Added bytes |
|---|---:|---:|---:|
| Resident EMOS ROM used |129108|130141|1033|
| Resident ROM free |1964|931|−1033|
| Link-only application units, text |1157|2346|1189|
| Link-only application units, BSS |372|391|19|

The application units include the actual submit/progress/take/close probe and
SDK inline paths: async main/adapter1747B + unchanged generic core569B + OTIRX
leaf30B. They exclude common CRT/runtime and the consumer's existing receive/
VDPlet callback chain. The full linked async probe has text3597B/data78B/BSS445B;
that is an actual probe executable, not MechAgon's whole program. Consumer link
size and useful foreground work remain its separate trial evidence. Resident
storage adds only hook3B/demand1B/provider-owner1B; no resident source/count,
transfer queue, buffer, callback engine or timeout loop is introduced.

1. EMOS source `2c4705310a49c7d97fc606bf47344cc36f68ab2e`, isolated owner
   branch codex/net004-uart1-app-r01, task INTEG-024. Identified experimental
   build `agon-emos-eirene-r05-b2026-11-07-06-35-12Z` selects guarded RFC25,
   UART-NM and optional app glue; parallel/old TX diagnostics remain disabled.
2. Full padded131072B ROM SHA256
   `043a0989b08a7429a2c52aca6a037660f8c19c067376173d17af7c46f1238c0f`;
   raw130141B `b9f08a09d85052a9d748539502b73bfc6d192094d974259523565a4bbe22b947`.
   Map `b87c12848dc5f33571bc60bab904a2b789f75082555ef4729ee4232b5e86a109`.
3. UART core/emitter unchanged at823bb91dd4c1af5a1488e3d3361648646b601445.
   Include net_async.h instead of net.h in the transport-owning C unit; link the
   pinned core/emitter, not the vanilla vector installer. Existing NM callback
   chaining remains consumer-owned. Positive TX hook close does not restore a
   separately installed user keyboard callback: retire that existing chain too.
4. Exact retained build objects, ELF/map/ROM and input hashes remain in the
   ignored owner binding inventory. Working UART ROMa25f/P4d9bcb remain installed
   and are retained rollback. The candidate was subsequently installed/verified for
   one failed trial, then rolled back; see the physical result.

## What passed

1. Actual app adapter + unchanged U1 core + actual EMOS net/neta C, with hardware
   alone substituted: early reply while TX is blocked; TAKE then new SUBMIT;
   immutable146B borrow/query identity; delayed CTS/retry; RX-first16-byte cap;
   ten-burst146B TX; callback before SDK SUBMIT returns; separately later TEMT;
   timeout/invalid-reply close refusal; first line-error fault and abnormal exit.
2. MechAgon's malformed successful OPEN/refused-cleanup finding is reproduced
   at the provider-output/refusal boundary and corrected. The app retains its
   cleanup association/storage and blocks payload with an unvalidated token.
   A later positive RELEASE removes the hook. This synthetic ordering is not
   the cause of physical74 and does not demonstrate a generic U1 defect.
3. A rejected SUBMIT may clear NM admission while the app service hook remains
   attached. Progress/close now use the retained hook association, allowing
   positive cleanup even after that refusal; payload still requires a validated
   open token and admission. The actual-C refusal regression passes. This is an
   application-only correction; ROM, wire and generic U1 core are unchanged.
4. Existing actual synchronous EMOS/P4/public-C peer tests pass. Default SDK
   hooks produce a byte-identical synchronous eZ80 object versus the recorded
   pre-adaptation header, including its error/release behavior.
5. Mandatory startup, baud/divisor, parallel-upload/common pad ownership,
   keyboard IRQ/callback, console, guarded RFC25, UART-NM, new app-hook and
   control-TX-selection validators pass on the linked full firmware. Existing
   IRQ register saves remain; linked owner tick/reset/RX-first calls and bounded
   CTS sampling are checked; generic U1 engine symbols are absent from ROM.
6. Compiler297 first passed host/application checks but stopped at our numeric
   IER C-lvalue mistake. Source014d74a/logs preserved; a bounded native IER leaf
   corrected it. Compiler299 passed all composition/native/ROM checks11.345s;
   compiler301 passed the additional malformed-OPEN regression/native-size
   update3.145s. Compiler303 passed the rejected-SUBMIT cleanup regression,
   sanitizer/native link and unchanged-default-object checks2.125s; its smaller
   app probe supplies the current table. Every owned child joined and compiler slot released. One queued
   wrapper entry refused before compilation because it had no lease; no overlap.

## MechAgon consumer link evidence

MechAgon's separately checked caller reports these paired whole-application
links at b78d91e using the checked r02 SDK; compiler304 passed its actual-caller
lifetime/scheduler tests and both native links, then released. These scopes
include the consumer and its existing receive/VDPlet chain, unlike the small
owner probe above. The resident ROM cost remains separate.

| Consumer bytes | Synchronous UART1 baseline | Application async UART1 | Added bytes |
|---|---:|---:|---:|
| Text |36274|38250|1976|
| BSS |6165|6189|24|
| Data |87|87|0|
| Executable file |36361|38337|1976|

Async executable SHA256
`cf910bd7e15533067f5c1cd886af0b3874258acfc4da087c1923e1bd784bfb4b`;
map `330608002abab39fc98efe1c7aef74f8fd9de159453f285b92510423392872cb`.
These links establish no useful-CPU percentage or frame-rate result. The later
first consumer invocation failed with UART1 receiver overrun and deliberate
quarantine; the working ROM is restored and the bench released. The
[owner installation plan](EMOS-ASYNC-PHYSICAL-R01.md) bounds that separate
firmware change and rollback.

## Remaining physical boundary

The P4 source's RTS stop threshold64/128B FIFO bounds the proposed16B burst with
headroom for queued eZ80 FIFO/shifter bytes under one writer; this source argument
is not a measured electrical CTS qualification. EMOS keeps RX/vector/error/LSR,
GPIO/mode/writer ownership. No source or wire completion proves peer execution.

MechAgon adapted its caller, checked its links and ran one frozen finite trial
with the independent source/wire/reply lifetimes and reciprocal UART0/NM gate.
That trial failed with receiver overrun. Extender completed exact EMOS-only
installation/readback, evidence preservation, working-ROM rollback/fullreadback
and normal clean release. Receive/IRQ/peer STOP timing remains unresolved.
No vanilla benchmark gate, production promotion, implicit parallel substitution,
checksum, replay, speedup or tick-for-tick30Hz claim is introduced.
