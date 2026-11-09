# UART0 CTS edge progress — isolated owner qualification

The retained RFC25 sender masks TX when CTS blocks and rearms only at VBlank. This source tranche implements an optional genuine UART modem interrupt rearm so accepted source transmission can resume while the foreground is HALTed. Actual158 does not prove how often the old defer path ran. No device, default firmware or physical case is changed.

1. Scope is the existing resumed human real-game30Hz goal, independently read in MechAgon thread01a1a883, turn01a1bfe2-fed2, human message01a1bfe2-ff74. Root selects this concrete owner tranche in frozen81062c5 LIVE-30HZ-CTS-PROGRESS-R02.md. Scheduler retains all physical custody; Extender supplies source/native qualification only.
2. Baseline is exact native EMOS branch7e1c7a3b0fd5f976dc5d45bc3d8a5de75605364f, ROM1e4e54dd, OPEN4/RFC25/UART0 RX reserve. Clone into a separate owner source checkout; never edit retained baseline/archive/generated translation output. Implement defaultOFF EMOS_UART0_CTS_IRQ; OFF with original identity must reproduce full1e4e byte-for-byte.
3. Selected design: existing UART0 vector classifies genuine modem-status cause separately, acknowledges MSR and invokes existing single-sample rearm; no copier outside TXIRQ. Arm modem change only while CTS retry pending, with immediate CTS resample after arm to close the lost-edge window; disable only the newly owned modem enable after rearm. Reject preexisting modem-enable ownership before submit mutation. Keep VBlank fallback. Preserve source/count before CTS acceptance, RX-first/reserve/U1 exit tail, registers/IFF/route/span guards and callback-before-return legality. No new syscall/SDK, timer, busy loop, raw consumer I/O or retirement relaxation.
4. Research: official agon-docs f9806bd3 GPIO and mos/API UART interrupt bits, read-only MOSv3.0.2/VDPv2.16.0 baselines; exact uart.c sets PD3 CTS alternate-function input through hardware flow setup. Zilog eZ80F92/F93 PS015313-0508, physical page14/107/112-116/122 (PDF pages20/113/118-122/128) defines PD3 active-low CTS0, modem-change IRQ, IER3, IIR cause0 and MSR read acknowledgement. Publisher URL redirects; identical manufacturer PDF mirror https://www.mouser.com/catalog/specsheets/Zilog_ps0153-2.pdf. No new GPIO remapping/wiring. Record other modem-input assumptions and noise limits.
5. Finite qualification: actual linked defaultOFF identity, optionalON full wrapper/mandatory inherited validators, linked-byte/state-machine negative controls covering CTS transitions around mask/arm/ack/resample, pending ownership, spurious/no-pending IRQ, source callback/IER/RX state, VBlank fallback and caller register/stack preservation. Native instruction harness uses explicit hardware stubs; it is not silicon/whole-ISA timing proof. Serial Pi FIFO compiler tranche <=600s, each subprocess <=210s, owned process groups joined and slot released before results.
6. Return full ROM/map/ELF/source archive/API/profile, exact sizes/static stack changes and qualified limits. Optional witness only if bounded/epoch-safe and fits; otherwise explicitly omit. No physical readiness, incidence count, latency cure,30Hz pass, baud change or production promotion. Separate source disposition on NM source+TEMT overlap may inform a later consumer change; do not implement it here.

## State

1. [x] Source diagnosis and direct human resume verified; concrete plan frozen before code.
2. [x] Isolated source implementation and meaningful negative controls.
3. [x] Exact OFF reproduction, optional ON fit/link/ABI checks and finite resource release.
4. [x] Package/return with honest runtime/GPIO/witness/coexistence limits.

Result: [source qualification](UART0-CTS-PROGRESS-R01-RESULT.md). All bounded work complete; no physical selection.
