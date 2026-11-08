# NET-004 — Optional UART0 receive witness R01

EMOS will optionally retain a small receive witness in application RAM so a stopped consumer can distinguish bytes received, packet framing, and callback acceptance. The missing FRAME reply in actual104 and the later UART1 error remain separate unresolved observations. The checked preparation was subsequently selected for one R12 diagnostic consumer, actual108, as recorded below; no successor is implied by that historical selection.

## Scope and ownership

1. Extender owns the optional EMOS integration and matched application SDK. MechAgon owns its recorder storage, caller integration and stopped interpretation. The generic UART owner separately assesses transmit/failure-copy timing.
2. Preserve the frozen c1047 derivative (source9dd099f;335 ROM bytes free), all existing STOP/RX-first tails, source lifetimes, public receive ABI, callback routing and carry/no-data fix. Work in a separate source checkout.
3. Default-OFF must reproduce the exact c1047 ROM using its retained identity header. ON receives its own identified source/build and actual ROM/RAM/stack measurements before any physical freeze.
4. No new timer, status/RBR acknowledgement, per-byte callback, checksum, retry, reset or resident ring/framework. No inferred cause or performance claim.

## Bounded reference précis

Official read-only baseline checked2026-11-07: MOSv3.0.2/8336409351ee5314e02801a7b72a4f1bb5282519; VDPv2.16.0/c7ac293d2aa81ddfa693390549bcd909069c8fc3; docs f9806bd3cbff6ed5d1c08bef1d51fed11764b86b. System-Commands.md (VDP packet section) specifies cmd|0x80,length,payload; API.md mos_setkbvector specifies callback DE and lifetime through removal. Raw packet completion is distinct from callback acceptance. EMOS currently bounds payload to16 bytes and discards oversized frames. The source-owned serial helper reads LSR once, reads RBR only with DR, returns carry set for every real byte including zero. The UART0 IRQ owns full register saves and receive protection before this helper.

## Checked private composition

1. `EMOS_UART0_RX_WITNESS=1` requires APP/RFC25 and rejects the other diagnostic OPEN7 schema. Ordinary OPEN4 is unchanged. The matched private OPEN7 associates an optional36-byte app record; NULL explicitly disables collection. EMOS validates the whole span before publication under the existing owner lock.
2. The application zeros the record before OPEN and retains it, service code and source until positive CLOSE or actual owner teardown. Refused CLOSE retains the association. Successful CLOSE/reset/abort clears the record pointer alongside actual hook teardown. No concurrent app reset or mutation while associated.
3. The IRQ-only receive sibling carries its existing raw LSR to the observer; public `UART0_serial_RX` stays byte-identical. The observer preserves receive AF/carry and all parser context. Parser completion records before filtering and callback dispatch; it does not count accepted callbacks.
4. Record offsets:0 RX count16,2 no-DR count16,4 raw complete count16 (all modulo65536);6 lastLSR,7 lastRBR (valid if lastLSR.DR);8 firsterrorLSR (0 unset; mask0x9e),9 firsterrorRBR (valid onlyDR),10..12 firsterror pre-parser state/cmd/remaining;13 last complete command,14 actual payload length;15 schema1 app-owned;16..31 last raw payload (only prefix[0:length] valid);32..34 latest pre-parser state/cmd/remaining;35 reserved0. First error is retained. Oversize packets never increment completion.
5. App reads coherently only after positive CLOSE/association removal, or retained stopped post-reset RAM with that limitation stated. A concurrent live byte dump is provisional and may mix epochs. No new masked copy/snapshot API.

## Implementation and qualification

1. [x] Add source-owned optional IRQ/parser witnesses and matched OPEN lifecycle/SDK schema, preserving optional notify in the checked SDK.
2. [x] Native OFF identity, ON link/fit, all mandatory guards, no extra I/O/carry/context checks, lifecycle/span and SDK negative controls. Capture real linked costs and bounded record instruction behavior; do not label abstract controls as full ISA/IRQ execution.
3. [x] Package exact source/config/build/map/SDK/schema/results and return owner-ready source evidence. No physical selection follows from passing source checks.

## State

Source/native preparation complete under direct human GOAL/resume and owner delegation G01-U0-001. The [checked result](EMOS-UART0-RX-WITNESS-R01-RESULT.md) records exact costs, controls, map/lifetime and limits. No physical case or deployment selected. Component/hardware/production selection unchanged; generated artifacts remain local and publication hold persists.

Coverage is IRQ-only, before parser consumption and before raw completion filtering. It does not cover polling receive or callback acceptance. Command/remaining may be stale outside their valid parser states. Record must not alias client/source/code; span checking does not establish alias safety.


## Actual108 diagnostic outcome

The separately frozen R12 caller used the final3bb38d witness image and exact f1de native/map. Full131072-byte installation/readback and stopped sole handoff passed. The one original run failed its150s CLI observation after318 host frames/317 intents and TCP EOF. Root actors joined before owner recovery. One Agon recovery restored CLI; the64KiB RAM image is explicitly post-reset and was saved before any later LOAD/write. It matches immutable caller bytes and contains raw UART0 LSR0x63/OE+DR with pre-parser[2,6,7]; this software label does not authenticate a MODE packet after possible earlier loss. First renderer reply deadline and error witness have no common timestamp or proven causal order. No original hook retirement, coherent live snapshot, global no-error or timing pass is inferred.

Exact incominga25f rollback, full readback and fresh normal CLI/state/files/input/resources passed; actual108 released00:45:33.630970UTC. Frozen source/package evidence remains unchanged. Further owner source work is tracked separately in [UART0 receive reserve](UART0-RX-RESERVE-R01.md); this result selects no replay, installation or successor case.
