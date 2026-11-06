# Parallel network carrier — bounded physical result

The mainboard application successfully exchanged four binary messages through
EMOS, the parallel pipe, P4 and a TCP echo peer. Reusing the existing P4 receive
descriptor correction resolved the observed 127-byte boundary failure. This
qualifies the selected finite carrier exchange and clean return to the CLI;
renderer coexistence, IRQ gaps and comparative performance remain unqualified.

## Exact selected components

| Component | Identity | Bytes | SHA-256 |
|---|---|---:|---|
| P4 application | net-004-r02-b2026-11-06-01-28-30Z; source 221e6207cc25adab344adb7adffe822ada1fbbda | 1764128 | a967fac2e1364e5c1d80964ed5e8183feee693e4f63c256a02654dc8482e6eee |
| Complete EMOS ROM | agon-emos-eirene-r04-b2026-11-06-00-23-15Z; source c9c8b6be316b5ebb64da1f16773ec3c886349267 | 131072 | b5a1f4aa3b9f4527aafb5f48aa29445c3e30962c5b21382729c370944b043b02 |
| Application appliance | network-echo-probe-r04-b2026-11-06-01-09-40Z; source d23264a4 | 16569 | 643f6b4aa151e7f703bcdf3f5e4b679d25c4c877d96371442234cbd6b1da4474 |
| Public parallel SDK | corrected provider-name declaration | — | e0504f1e9e33a8ae8dcb034bc91d84cb82270fd7f38279abfc88a3a5e054f011 |

EMOS binds sysvars at 0xBC322 and KBvector at 0xBC38E, with four bytes of ROM
remaining. RFC25 uses the normalized admission result and the retained callback
contract. The P4-only correction did not change these addresses or the SDK.
The mainboard VDP, startup and foreground listener were preserved.

## Attribution and reuse

1. The initial appliance was refused before OPEN because its public descriptor
   declared three provider-name bytes for four-byte `netp`. The corrected SDK
   and regression now traverse actual resident gateway validation/routing,
   instead of testing only the inner endpoint.
2. The corrected appliance exchanged zero and one bytes, then stopped before
   the 127-byte message reached the TCP peer. A separately selected passive
   dual-USB diagnostic reported a 141-byte native receive with only 128 bytes
   counted and one completion. Close refused with status132; application storage
   remained owned. Raw captures, SD receipts and RAM were preserved.
3. The network build had omitted the existing FWBUG-016 RX derivative. The
   pinned IDF callback counted one descriptor per coalesced DONE status, missing
   the short second descriptor. The new composition selects the retained
   completed-descriptor walk for network builds too; it adds no new wire bytes,
   checksum, per-byte handshake or RX algorithm.
4. Actual-source descriptor checks include 128+13 and 128+14 bytes. The full
   build validator proves exact derived source, one compilation, archive
   membership and final ELF linkage. Twenty-six admitted host checks passed.
   The finite serial full build completed in 937.344 seconds including its
   admitted checks; all owned compiler descendants joined before release.
5. The operator installed only the new P4 application sectors, preserving the
   unresolved final-sector tail and independently comparing the complete new
   written span. The bootloader, partition table and mutable partitions were
   untouched. Prior diagnostic results and RAM were collected before LOAD.

## Selected run and handback

The single fresh run began on 2026-11-06 UTC, with run identity
`NET-004-2026-11-06-01-46-52Z`. The application installed no NM callback and used
only foreground `netp`; P4 owned TCP and the Pi peer echoed opaque bytes.
Mainboard graphics stayed on Legacy UART0. No UART network-payload fallback
was compiled or selected.

| Check | Actual result |
|---|---|
| Binary payload lengths | 0, 1, 127 and 128 bytes: 4/4 pass |
| Short TAKE / required-size retention | 10 checks; whole replies subsequently matched |
| Application result / RELEASE | error0, RELEASE0, restore1 |
| Application timing | 14 nominal120Hz ticks; not a throughput or calibrated latency claim |
| Host invocation to observed completion | 10.202 seconds, including command delivery and observation |
| Host setup through collection | 30.327 seconds; separate from application timing |
| Native mode / callback afterward | mode0 / zero |
| CLI, input, transfers | actual read/EXIT handback; input admitted/neutral; listener offline and staged worker idle |
| Owned actors | peer and both passive USB readers joined; programming ports free |
| Preserved files | startup and installed listener bytes unchanged |

The clean handoff transfers sole hardware operation to the existing consumer
lease; it is not a bench release, production promotion or human optical pass.
Owner-local installation, run, failure and handoff receipts retain machine
paths and current custody. The consumer owns its separate VDP/module selection
and renderer qualification. N04-007 still owns broader IRQ/service-gap,
keyboard/UART0 coexistence and latency comparisons.
