# UART0 receive witness — checked source result

The optional witness fits and passes source/native checks. It retains receive status, pre-parser state and the last raw completed packet in application RAM. It is uninstalled; no hardware case or missing-reply cause is established. The tested carry/flow-control derivative stays immutable.

| Cost (bytes) | Witness OFF / c1047 | Witness ON | ON minus OFF |
|---|---:|---:|---:|
| ROM used |130737|131046|+309|
| ROM free |335|26|-309|
| Initialized data |802|802|0|
| Resident BSS |3499|3502|+3|
| Optional app record |0|36|+36|
| Owner gateway local stack allocation |16|19|+3|

Identified build `agon-emos-eirene-r05-b2026-11-07-23-38-00Z`, EMOS source `03e05c20586e830df27f97b228d8b1d2fa7a791e`, SDK source `d6be7212ab2a5a96b88423bba15f7b4cbbd6108b`. Full131072-byte ROM `3bb38d6cd3986a141e389f38008bfe49476560d708b1095bdcc7db457b080e74`. The matched OFF ROM reproduces exact c1047. No core/emitter change, timer, extra LSR/RBR read, callback routing or source-lifetime change. All native mandatory guards pass. First provisional ON exceeded physical ROM by50bytes and stopped at the linker; the corrected decoder reads/validates OPEN7 extra field once and normalizes only the local shape to ordinary OPEN4. No record or flow guard was removed.

## Checks and limits

1. Linked record leaves pass790 cases: every LSR, real zero/data bytes, count wrap, first-error retention, all0..16 payload lengths, NULL and bounds; two deliberately disabled leaves fail their result oracles. The actual linked handler additionally passes256 LSR cases with explicit peripheral/parser/U1 stubs; the existing carry validator retains524 cases and three branch mutations. This bounded interpreter is not a full ISA/IRQ or device timing result.
2. Actual SDK/EMOS C with fake hardware passes13 record-association/span/NULL/duplicate/refused CLOSE/fault/positive CLOSE/abort cases, existing RX/lifetime and notify regressions. Old SDK and conflicting OPEN7 schema negative controls fail as intended. Native default notify binary/objects are exact; unchanged core/emitter objects are exact. Witness-enabled native notify probe costs50text/36BSS and3 extra main-frame bytes; its service frame remains20bytes. These are that probe's costs, not a consumer whole-stack peak.
3. Native record leaves use at most15bytes saved stack internally; packet capture adds its3-byte call return (18bytes below pre-call SP). RX wrapper including saved AF/return and leaf saves peaks15bytes; the old receive helper alone used3bytes. Owner gateway local allocation rises16→19bytes. This is bounded local evidence, not complete interrupted application/IRQ stack qualification.
4. Measured instruction paths in the bounded model: RX leaf max38, packet leaf max54 counting16 LDIR repetitions, NULL11/12. Add the calling wrapper/IRQ sibling instruction work. No cycle/time bound or performance neutrality is established. The observer adds work while the existing receive protection is held.
5. Capture covers only IRQ receive status, pre-parser and raw frame completion. It does not cover public polling RX, accepted callback delivery or loss time. Last payload is raw buffer; only `[0:last_length]` is valid. Counters wrap16bits. Current parser sample is before the received byte; command/remaining may be stale outside their parser state. Zero first-errorLSR means no observed masked error since app initialization.

## Private matched association

Define `AGON_NETA_UART0_RX_WITNESS` to a distinct zeroed36-byte app record, set schema1 before OPEN, and include the matched `net_async.h`. Undefined retains ordinary OPEN4 and optional APP notify. DefinedNULL is disabled OPEN7. EMOS validates the whole span before publication under the existing owner lock. The old UART1 diagnostic marker OPEN7 is a different schema and simultaneous selection is rejected. Record/code/source/client remain valid on refused CLOSE or quarantine. Positive CLOSE and actual abort/reset remove the association together with the service hook. No app reset/mutation while associated. Read coherently only after removal or from explicitly preserved stopped RAM; live snapshots can mix epochs. EMOS does not grant record aliasing safety.

Use `net_uart0_witness.h` for byte layout and checked-result.json for exact symbol map. Consumer caller/decoder integration belongs to MechAgon. A later physical case must bind this new ROM/map/SDK and its own frozen app; passing source checks does not select it.

## Retained P4 coredump announcement

The saved reset log's `af5f9e3ac...` matches the retained current ELF SHA `af5f9e3acc84c869bfd83e184ba7a0f7df380d69da41da7da8a943efa949d34a` and known build. The flash announcement says a valid31108-byte prior dump exists, but no dump blob/timestamp/producing-ELF metadata was acquired. Saved PC fields are reset context, not a coredump backtrace. Mapping one initial PC to HDMI expansion and another to idle does not identify a crash cause; two explicit-reset addresses remain unresolved. Attribution to actual104 is UNKNOWN. No fresh device acquisition or firmware action occurred.

All source commits are local; publication hold remains. Generated artifacts and controlled failure logs are retained separately. Concurrent consumer custody remains with its actual owner; Extender performs no target access for this source task. No new owner reservation/case, deployment, production selection or acceptance claim.

Final local artifact: `uart0-rx-witness-r02.zip`,351127bytes, SHA256 `4ad43b5be9ffaf55aab55cefbf967df7f5e1177b3dc4325bd2afdf3f89865989`;56 members independently verified against the final manifest. Earlier package-r01 is superseded pre-handoff metadata output; no source/runtime change.
