# UART1 reserve protection — first owner isolation

The corrected APP ROM passed the selected exact-byte echo test through EMOS, the P4 and Pi5:176 records, four complete connection lifecycles and no recorded error. Extender restored and independently verified the incoming working ROM and cleanly released checkout93. This qualifies quiet integration; the separate MechAgon trial will exercise overlapping UART0 rendering traffic.

## Exact result

| Item | Retained result |
|---|---|
| EMOS source | `6cf7a6a756d30d99f7745e72d5c99b91c677db41`, pushed isolated owner branch |
| Identified APP build | `agon-emos-eirene-r05-b2026-11-07-16-07-59Z` |
| Full131072-byte candidate ROM SHA-256 | `47dadc290433850c0aa500f6c165defd821ad992bc484abe5e047fbe4b800155` |
| ROM used/free | 130735/337 bytes; +238 text/0 initialized data/+2 resident BSS versus earlier8de66 APP |
| Unchanged appliance | 17809 bytes, SHA`7ad4c8915a6f0a2ed721f5ab8ac080ca526d92ce3b30a1febc74567fb037fa1e` |
| Workload | Four sessions ×44 records, eleven lengths0..128, four deterministic patterns |
| Both endpoints | 176 exact records,9936 payload bytes in each direction, excluding framing |
| Native retirement | Four opens/four positive closes, source phase4 each, first error0, final release0, entry mode restored |
| Original RAM preservation | 65536 bytes at040000 saved before any subsequent LOAD; no recovery reset |
| RAM SHA-256 | `916b77a1b69dd890192729a50873169241fe715d51676e4c7fe7743b7211f887` |
| Immutable app identity | All17712 init/text/rodata bytes match the selected appliance |
| Restoration | Exact incominga25f full131072-byte ROM independently compared; P4/native/startup/listener unchanged |
| Final handback | Actual root CLI/cursor, raw0/callback0/route0, whole files, neutral input, offline listener/idle worker/free USB; all owned actors joined |
| Clean release | Generation93,2026-11-07T16:32:10.658579+00:00; old token invalid, SD mounted |

## Implementation and qualification limits

1. EMOS asserts UART1 STOP early around admitted UART0 work, keeps a distinct hold and runs bounded RX-first service before READY. A16-byte drain cap retains STOP and deferred continuation until the existing drain observes clean-empty. The generic U1 sender, emitter and public APP ABI are unchanged. Source release, later wire idle, reply retirement and positive CLOSE remain distinct.
2. Actual-source sanitizers, five semantic mutation controls, existing SDK/core/owner regressions and every selected mandatory native/linked validator passed. Parent/candidate ordinary non-app images with a common identity header are byte-exact. Structural checks do not execute native IRQ instructions. The guarded tail saves27 bytes of registers, excluding outer frames/parser/hook/calls; no whole-call stack peak is claimed.
3. Diagnostic-ON exceeded the physical ROM linker bound and was not installed. Its informative failure is retained separately. The checked APP is the selected reliability path; no validator was dropped or ROM truncated.
4. Extender installed and independently read back the exact candidate before ONE explicit CLI invocation. The app kept UART0 display/SD traffic outside live network ownership. The Pi peer and native SD witnesses agree on the complete ordered byte matrix and positive closes. RAM was saved after actual terminal CLI, before later LOAD, without a recovery reset. FLASH automatic boots are installation/restoration events.
5. Host dispatch-to-terminal was12.843279s, peer lifetime13.428713s and the native witness290 nominal120Hz MOS counts. Their scopes differ; these establish provenance, not speed or CPU savings. The case does not establish physical competing-UART0 safety, STOP-tail timing, overnight reliability or a cause/cure for actual92 OE.
6. The owner retained81 exact selected inputs as79 unique snapshots, complete original host/peer/native/SD/RAM evidence and both independent ROM readbacks. No sensor, CRC, renderer, timer, baud change, uncertain retry or replay was added. The first mixed-workload consumer requires its own exact frozen kit, fresh grant, installation/readback and sole-operator handoff.

The [selected plan](EMOS-ASYNC-RX-PROTECTION-R01.md) and [parent investigation](EMOS-ASYNC-RX-R01.md) retain the dependency and scope. Machine-local result93.json and linked raw evidence remain with the owner; no production promotion or performance acceptance is inferred.
