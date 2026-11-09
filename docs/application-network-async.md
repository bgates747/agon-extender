# Async application-network development profile

Extender maintains the application-owned async UART1 adapter in
`include/agon/net_async.h`, with `net.h` and `net_callback.asm`. The selected
[component descriptor](../components/application-network/agon-emos-eirene-r05-b2026-11-09-12-24-49Z/component.yaml)
pins the exact SDK, dependency snapshots and EMOS build used by the finite
sustained game qualification. [The profile selector](application-network-profile.yaml)
identifies that descriptor. This is an explicit development configuration;
[Olimex defaults](olimex-firmware-standard.json) and the
[production installation](../production/current.yaml) retain their own authority.

## Obtain and verify the component

1. Obtain the retained `application-network.zip` and its adjacent `SHA256SUMS`
   from the Extender owner through the normal development-machine file-transfer
   route. Its repository-relative retention directory is
   `dist/components/application-network/agon-emos-eirene-r05-b2026-11-09-12-24-49Z/`.
   The descriptor records the archive's exact size and SHA256. There is no
   published release asset or download URL for this component. A Git clone
   supplies the maintained headers and descriptors, but not the generated ROM
   archive. Local-only packaging does not establish public redistribution or
   license clearance for the full historical source archive.
2. Compare the archive size and SHA256 with the committed descriptor, then run
   `sha256sum -c SHA256SUMS` in its retention directory. The adjacent checksum
   file is a convenience; the committed descriptor is the expected identity.
   Extract with `unzip application-network.zip -d NEW_EMPTY_DIRECTORY`.
3. In that new directory run `sha256sum -c SHA256SUMS`. The internal
   `MANIFEST.yaml` inventories every payload by relative name, size and hash;
   the outer descriptor also pins this manifest and the internal checksum file.
   Keep the complete archive for reproduction and rollback. Do not silently
   substitute a different header, ROM, library or Git HEAD.
4. An installer records the exact installed ROM and retained rollback bytes
   through the current scheduling procedure. The application requires that
   external provenance before entry. This guide does not install firmware,
   reserve the bench or invoke a test. Matching retained installation provenance
   permits normal reuse; no redundant firmware rewrite is required.

The archive contains `firmware/` (ROM, binary, map, ELF and original build
manifest), `source/` (complete versioned EMOS source tar and owner patch),
`sdk/agon/`, `dependencies/uart1/`, `dependencies/foreground-wait/`, and
`qualification/`. Dependency licenses accompany their exact snapshots. The
source tar preserves commit `beec8b9555d6a3f51ce2d2ba2cfe3b05d0c02097`, based
on `7e1c7a3b0fd5f976dc5d45bc3d8a5de75605364f`. It is a retained native
development branch, not a claim that the component was merged into current
EMOS main. Follow its native Makefile and identified-build instructions;
rebuilding is a new activity and does not inherit exact-byte qualification.

## Required component and ownership

| Actor/component | Required identity or responsibility |
|---|---|
| eZ80 EMOS | `agon-emos-eirene-r05-b2026-11-09-12-24-49Z`; ROM SHA256 `d3a4524a91b5a36b0b1cb02e3156a81c487e0c135223e22b8b87ed3440d033af`, 131072 bytes |
| Application adapter | `net_async.h`, 6258 bytes, SHA256 `e98cc8de6532ecf53c5244b16d050f3bbcf0088236211f9d927da3fa1bdeedb5`; matched `net.h` and router in the descriptor |
| Application UART1 core | Exact packaged `u1_tx.h`, `u1_tx.c`, `u1_emit.src`; EMOS invokes the admitted application hook and retains peripheral/IRQ ownership |
| Application wait helper | Exact packaged `aw_wait.h`, `aw_wait.s`, `libaw_wait.a`; foreground atomic wait, with its documented entry conditions |
| Mainboard VDP | VDPlet v0.1.2-alpha async-r1, SHA256 `dc43ecb8b1c324ffd1a032e6cc0c56d8c05dd33a355ce170c23adb35ffb533ab`; exact release requirement remains explicit |
| Extender P4 | Existing matched network service and transport configuration; application messages traverse mainboard UART1 to P4 and then P4 TCP to the peer. This component does not replace P4 firmware or promote P4 v0.2.1 |
| Application/peer | Bounded scheduling, record processing, game protocol, semantic replies, useful work and session cleanup |

The EMOS profile enables guarded UART0 RFC25, application UART1, UART0 RX
reserve and CTS-edge progress. CPU, network-parallel and diagnostic witnesses
are absent. Its historical build manifest remains experimental/source-qualified;
the later [qualification record](../components/application-network/agon-emos-eirene-r05-b2026-11-09-12-24-49Z/qualification.yaml)
records actual162 separately. The ROM has 75 bytes free. Combining another
feature or profile requires its own composition and qualification.

## Entry, service and exit

1. Include `net_async.h` **instead of** `net.h` in the single transport-owning
   translation unit. Keep the client/engine, source, callback, code and reply
   storage alive in ordinary application RAM. Link the exact UART core/emitter
   and callback router; do not install the core's vanilla IRQ, write peripheral
   registers directly or bypass EMOS mode/routing admission.
2. Require the exact externally recorded ROM/build profile. At an admitted
   prompt, `EMOS STATUS` can report the build before application entry. Gateway
   access through MOS0x51 (or discovery through MOS0x50 function0x20/flags0)
   and successful namespace/OPEN checks do not distinguish this CTS-edge ROM from
   every earlier `OPEN4` provider. There is no public CTS feature query. A
   missing/mismatched profile produces an explicit unsupported-configuration
   result; do not fall back silently to synchronous `ext.net`, another provider
   or raw UART. The global a25f baseline lacks this `ext.neta` profile.
3. The product-local gateway uses ABI1.0, a 66-byte frame, service operation2,
   and zero-padded `ext`/`neta` names. `agon_neta_begin` requests local selector0
   with a four-byte OPEN (selector and 24-bit ordinary C hook), validating the
   seven-byte token/prior-callback reply. Install the application router via
   public MOS0x1D before CONNECT. This interface is not an upstream allocated
   MOS API or a stable global capability declaration.
4. SUBMIT uses local selector2; bounded foreground `agon_neta_progress` uses
   selector4 for RX-first progress and later positive drain. Keep IRQs enabled
   for foreground calls. NM wire version1 has a 14-byte header and payloads
   up to128 bytes; follow `net.h` token/query and one-pending-exchange rules.
   Source release, UART TEMT, an NM reply, peer semantic completion and graphics
   END/CLOSE are separate observations. Never infer one from another.
5. Optional `AGON_NETA_NOTIFY`, defined before inclusion, may only mark sticky
   application-RAM pending state after publication. It must not call MOS, EI,
   log, allocate, wait or reenter the adapter. Leave
   `AGON_NETA_DIAGNOSTIC_MARKER` **undefined**: even defining it as zero requests
   diagnostic OPEN7, which this ROM does not provide.
6. For the packaged atomic wait helper, call `aw_begin` before service/useful
   work, perform bounded progress, then `aw_wait` to consume/recheck the token.
   Keep ADL1, MB0, entry IRQs enabled and the public clock stable. A wake is not
   proof of drain or revocation; bounded progress/fallback remains necessary.
   Two public clock counts per VBlank do not provide120 interrupts per second
   or a high-resolution wall clock.
7. `agon_neta_close` performs progress and selector3 RELEASE. Only a positive
   release retires the hook/source association; then restore the saved MOS
   callback. Refusal, fault or uncertain timeout retains associated storage,
   code and callback until supported recovery. Do not force detach, reuse the
   source, return into unloaded code, reconnect or replay uncertain traffic.

## Qualification and support limits

Actual162 used this exact ROM/SDK with a matched caller, P4 renderer/service
and host bridge: three unseeded Native/Walls rounds, 73.568336538 active seconds,
31.004856229 host Hz, all2284 source/host/native/module poses and all2281 eligible
next-model commands, normal closure and standard restoration/release. The
descriptor pins those consumer records rather than implying that a header
alone reproduces the game. The original build record and later runtime result
are both retained without changing their historical labels.

This finite result establishes the declared combination only. It does not
measure optical FPS, CPU headroom, exclusive phase time, maximum throughput,
flat per-frame deadlines, long-soak reliability, whole IRQ/application stack
or CTS interrupt incidence. Useful-work capacity must be measured with a
bounded workload and the delivery/cadence oracles still enabled. Keep generic
adapter maintenance in Extender; consumers may pin unchanged snapshots for
reproducible builds. The synchronous and parallel development interfaces remain
documented separately in [Application network messages](network-messages.md).
