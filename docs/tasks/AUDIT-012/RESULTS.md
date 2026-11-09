# Pinned firmware compatibility audit — Extender

The standard release artifacts are retained and verified. The immediate 6502
cohort can use the selected EMOS and VDPlet for its Apple arm, with an explicit
F6 comparison exception for its Row arm. Older complete production selections,
old controller viewers and private receive/instrumentation fixtures must not
be treated as ordinary default deployments. No hardware was accessed.

## Scope and method

Smith required the task to be committed and pushed before analysis. The
scheduler created `a1686bf5`; Extender reconciled the shared-file collision in
`0fa52f26` and pushed both before either audit contribution. One task/TODO
entry remains. The [machine-readable inventory](inventory.json) records all99
unfinished TODO entries, their task hashes,19 candidate groups, exact sources
and dispositions. This is an audit of current selections and task remainders,
not a claim that all archived experiments are deployment candidates.

Extender read the current handbook, production/component selectors, relevant
current guides, actual a25f source/map and candidate evidence. The scheduler
independently reviewed the75 first-job input records and standard artifacts.
Unresolved contracts remain explicit; no test, build, flash, emulator launch,
production promotion or other-project source edit was performed.

## Default identities

| Platform/component | Required identity | Audit evidence / limit |
|---|---|---|
| All three mainboard VDPs | VDPlet v0.1.2-alpha;1100304B; `b004570b607b45bbd6e87a3c704b65b23d3221981db3aac6cf2578aa22d766e3` | Nine release SHA256SUMS entries pass; published feature manifest checked; no new physical pairing claimed |
| Olimex MOS | Full EMOS131072B; `a25f1612f4aaa542c5488cf3266d968ad3d1d61e9df3b5ce2c680650f5d7a2ca`; source `2c79c6006d6bcb0c2b3f9d8d6aae3ef4b36c730a` | Retained ROM/map rehashed, owner Eirene function inventory and actual controller/RFC25 source checked |
| Alexe/Console8 MOS | Eirene3.1.0_uart0_rc_3, ZIP member mos-rc3.bin100879B; `d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50` | Exact Author pin; source/API audit of Extender standalone utilities, no bare-MOS installation |
| Extender P4 | Exact separately selected/admitted P4 image | Mainboard VDPlet does not replace Extender P4; board/profile and retained installation still matter |

## Candidate dispositions

Rows prioritize active incompatibilities and explicit exceptions in their
dispositions, rather than implying a pass from a matching filename. Group IDs
map directly to every task's coverage entry in the inventory.

| ID | Candidate group | Disposition | Finding |
|---|---|---|---|
| A01 | Selected standard pair | exact standard artifacts; physical pairing unqualified | VDPlet b004/1100304B and full EMOS a25f/131072B rehash exactly. All nine release SHA256SUMS entries pass. P4 is a separate component. Published VDP optional async worker, counted return and PCM are disabled. EMOS guarded25h is present;61h/62h and private26h are absent. |
| A02 | Accepted v0.1.0 installation | needs adaptation for ordinary default deployment | Immutable accepted bundle selects P4r55, EMOSv0.1.19 and historical stock VDP preservation. Its MOS is not current a25f and does not establish current Eirene functionality. Historical acceptance remains valid only for its recorded scope. |
| A03 | Combined native v0.2.1 candidate | needs adaptation of companion bindings | Candidate retains P4r16 but companion EMOS84da/v27 and old controller operations0–3, with F060 native preservation. Current a25f implements controller4–7,98B; old viewer0–3/96B is refused. P4 component acceptance is not evidence for a new complete tuple. |
| A04 | Accepted UART SD utility | source-compatible; current default VDP pairing unqualified | 24753B listener0566 uses EMOS services and ordinary UART SD path. Retained a25f/installed P4 lineage has repeated read/EXIT handbacks. Published P4r27 component pin is acceptance provenance, not proof it is currently installed. New native VDP pairing has not run. |
| A05 | Parallel SD upload trial | inherent firmware/carrier exception | Trial explicitly requires EMOS855aa7/P4 5db0/listenerf60f together. Default a25f has network_parallel=false; that selector cannot stand in for the trial. Legacy-only and allocation-refusal limits remain. |
| A06 | Earlier Eirene r02 qualification | historical composition; needs rebind for ordinary reuse | Original migration starts from RC2 42h/43h and an older complete image. It is not the current 25h/a25f default. Its partial paired qualification cannot qualify later a25f/b004. |
| A07 | Public controller client and old viewer | new client source-compatible; old viewer incompatible | Current public header4–7/98B matches retained a25f source and linked controller symbol. P4 physical CI2/CIS2 stays96B; timing bytes are EMOS-to-app only. Old viewer0–3/96B is not interchangeable. New pair physical behavior is unqualified. |
| A08 | Extracted diagnostics | unversioned firmware not deployable; utility pairing unresolved | Extraction metrics intentionally use UNVERSIONED-DO-NOT-DEPLOY images. Older edu.text-probe/fake-provider fixtures are retired. Exact external diagnostic utilities require their declared EMOS service/slot and new-pair timing validation; general table parity alone is insufficient. |
| A09 | Application network transport | standard synchronous carrier retained; later optional ABI exception | Matched d9b P4/a25f baseline uses EMOS-owned synchronous UART1 NM gateway. Later application-owned async/UART1 APP or receive-reserve compositions are not implied by default a25f. Vanilla MOS UART1 ISR/vector takeover conflicts with admitted Extender ownership. |
| A10 | Optional CPU/IRQ accounting compositions | inherent instrumentation firmware exception | Full f05c ROM is a separately identified accounting build with C2 API and12B free. OFF1e4e is also not a25f. Neither experimental hooks nor private maps are default API. Existing partial runtime evidence remains limited. |
| A11 | Temporary counted receiver171c/raw90h | inherent firmware/protocol exception; incompatible with default feature set | RX006 passed on temporary171c plus producer7d09 in prior finite cases. Standard a25f lacks26h/raw90h, and VDP012 explicitly disables counted_return. Prior132/136/139 results do not transfer to b004. |
| A12 | P4 display/board/render candidates | P4 changes separate; new mainboard pairing unqualified | These are Extender P4 builds, not replacements for the mainboard VDPlet. Ordinary MOS/VDU output contracts are retained at source level; optical/mode/performance gates and deferred work remain. Old matching mainboard control images must be replaced by defaults unless the comparison specifically needs them. |
| A13 | Console8 Wi-Fi utilities | source-compatible public RC3 APIs; exact-pair execution unqualified | Standalone utilities use MOS UART1 open/write/close, foreground nonblocking RX/THRE polling, public clock/key/FatFS and synchronous VDU. They do not need25h/42h/43h. Must own the physical ESP8266/UART1; not valid on an active EMOS-owned UART1. Previous manual pass does not prove exact RC3/VDP012 pairing. |
| A14 | Host services and recovery tools | source-compatible conditional on actual carrier; no firmware replacement default | Maintained HTTP/input/reset/SD tools act through the exact installed P4/EMOS services. Most need no native VDP extension. Old prepare/build/flash helpers and dated receipts are not universal current installers; stock emulator controls and fake-provider scripts cannot imply default hardware readiness. |
| A15 | Formal qualification and rendering fixtures | needs default-bound receipts/oracles before reuse | Canonical runner does not flash firmware. Existing success is tied to old receipts/output profiles. Stock-reference/pixel captures may be deliberately version-specific, while ordinary new runs use defaults. Old startup-writing or private-map fixtures cannot be replayed unchanged. |
| A16 | Communication fixture cores | unresolved live adapters; no deployable default-bound suite | Portable cores/host/native-link probes do not supply all actual EMOS/P4 mixed-leg adapters. Matched diagnostic firmware is an explicit transport comparison, not ordinary default. No physical-only helper/CRC permission is inferred beyond each existing task. |
| A17 | Research, documentation and planning remainder | no current deployable candidate in remaining scope | These TODO remainders are research, decisions, documentation, infrastructure or scoped closeout rather than a new firmware-bound deployment. Their archived binaries are not made current by an unfinished checkbox. |
| A18 | Parked or unscheduled legacy experiments | no current launch candidate; archived dependencies retained | Stopped/deferred hardware and standalone P4 demos remain archived research/partial results. Detached P4 demo has no mainboard MOS/VDP link. Unimplemented PCM cannot be inferred from the default VDP release, whose PCM option is disabled. |
| A19 | Delegated PERF-022 original fixture cohort | Apple exact-standard source match; Row inherent F6 exception | Original219b contract/75 records reviewed by scheduler; Apple uses b004 with a25f guarded25h/callback/fresh POINT; Row uses retained F6f2c. New-pair runtime, PRT ownership and physical execution unqualified. Original restoration wording is superseded by explicit current-b004 cleanup addendum, not edited in place. |

## Consequences for current operation

1. Keep one maintained [default selector](../../olimex-firmware-standard.json)
   and [function inventory](../../olimex-emos-functions.md). Reuse installed
   matching firmware; verify only changed writes. The last installed identity
   is an observation, not a desired selector or fresh readiness receipt.
2. The default VDPlet disables optional async-worker, counted-return and PCM.
   That is independent of EMOS's UART0 async25h support. Do not silently enable
   those VDP features or infer private26h/raw90h from the release version.
3. Current EMOS guards25h and returns A=0 on admission. A nonzero refusal does
   not install a callback or start a transfer. A bare-RC3 caller ignoring A
   needs an EMOS-specific admission contract before use; otherwise it can wait
   forever for a callback that will not occur. Callback, wire drain, fresh
   ordered reply and rendering completion remain separate facts.
4. The audit confirms a25f's linked controller endpoint already uses4–7/98B.
   The maintained public client matches it; the older accepted viewer0–3/96B
   does not. P4's physical CI2/CIS2 wire remains96B. No speculative new firmware
   is required just to expose this current endpoint.
5. Historical production bundles/tags retain their identities and acceptance.
   Current operating/install guides now make clear that they cannot override
   the new default MOS/VDP instruction for a fresh ordinary deployment. A
   separately qualified successor composition remains production closeout work.
6. Firmware/carrier/instrumentation comparisons retain exact exceptions and
   current-standard cleanup. A frozen old fixture is not an exception merely
   because it expects old bytes. Source owners adapt/re-freeze ordinary tests;
   no blanket fallback, new approval form or recurring audit gate is introduced.
7. The delegated original PERF-022 cohort remains first. Its standard cleanup
   addendum leaves b004 installed even if Row fails before Apple. First-job
   operator preparation, original budgets and first-fault rules continue.
   New hardware readiness or a run result is not claimed here.

## Follow-up ownership and completion

Extender owns standard selector/protocol upkeep, production companion migration
and current controller/diagnostic mapping. Consumer owners retain their code and
firmware-specific corrections. The scheduling agent checks the declared tuple
and exception during normal admission; it does not decide undocumented API
semantics. Concrete existing-record answers were sent to6502, FSIM and MechAgon
for their independent audits. No new workload was assigned to them.

The bounded source/artifact audit is complete with the explicit gaps above.
Those gaps remain in their existing owning tasks; they are not silently passed
or converted into new physical work. Checks:99 unique TODO entries covered,19
groups, existing evidence references hashed, standard ROM/VDP hashes matched,
all nine release checksums passed, and final documentation links validated.
