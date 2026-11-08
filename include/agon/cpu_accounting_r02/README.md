# Compact accounting dispatch (C2, source fit correction)

This adapter factors the retained C1 accounting bridge. It leaves the existing
MGCPU001/schema1 recorder, its native A-event ABI and sole timer provider
unchanged. Physical fit and controls are being measured; no timer/device use
or deployment is selected.

1. Include this matched net_async.h in the single transport-owning C unit and
   define AGON_NETA_CPU_ACCOUNTING=1. Link adapter.s with unchanged sources in
   ../cpu_accounting and ../rxdiag. The adapter supplies an exact8-byte table:
   JP ordinary-C service then JP inline-event decoder. This extra service JP
   lives in app RAM and is observer work, not an extra transport call/sample.
2. Private OPEN5 is op0/service-address24/tagC2. EMOS validates the full8-byte
   table span before association, binds the service and the adjacent marker JP
   under the same exclusion. It does not infer an offset inside ordinary C.
   This is deliberately incompatible with C1 OPEN8 and both old OPEN7 schemas.
3. Ordinary OPEN4 remains the no-observer control. Define the option0/leave it
   undefined for that form. There is no separate NULL marker field in C2:
   OPEN4 supplies the equivalent unobserved association. App init remains pure.
4. Each EMOS hook CALLs its initialized RAM JP slot, followed by one event byte.
   The app adapter preserves AF/HL/IX with stack-local saves, consumes that byte
   from the native return address and calls the unchanged A-event recorder.
   FF goes directly to the independent one-byte poison store without touching
   shared event/sample scratch. Nested NMI therefore cannot corrupt that scratch.
5. Unassociated dispatch targets a four-instruction native return-address skip
   leaf which preserves every register and IFF. Association/removal changes only
   its24-bit target in one native store; its JP opcode remains immutable. Both
   initial control and positive-close/abort removal use that default target.
   Refused close retains service/target/code/record/source/provider storage.
6. The three UART0 TX paths share one complete owner service/AF/EI/RETI tail
   only when accounting is enabled. No reserve/RX-first/protection is removed.
   Each actual native exit is marked; default OFF keeps its exact original
   instructions. Marker positions and unsupported-path poison remain unchanged.
7. Raw AW_WORK7/takenHALT6/return86 still use agon_cpu_entry's A-event ABI in
   the unchanged recorder; the MOS owner need not adopt inline-event decoding.
   Preserve adjacent EI/HALT and all wait results/IFF. No MOS leaf/app is edited.
8. All original clock,54000-count limit, one-window/quiescence/positive-close,
   incomplete/reset/poison/context checks and partial-boundary/gap limits apply.
   More app adapter work is not a timing improvement or certified UART reserve.

Use exact returned source/firmware identities, not this directory's existence,
for a later qualified composition. Neither a fit nor a link grants runtime PRT
ownership, native execution, optical timing or complete CPU% coverage.
