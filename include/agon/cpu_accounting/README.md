# Short-window app-RAM accounting (experimental)

This source supplies instrumented execution-class counts for one short window.
It is not deployable yet: the enabled EMOS boundary derivative exceeds ROM.
Native compilation and host/source controls cannot qualify physical IRQ timing.

1. Link accounting.c/accounting.s **and the unchanged** ../rxdiag/observer.c/.s.
   The latter is the only PRT1 owner/lifecycle provider; its old128B record is
   provider evidence only. Do not interpret MGIRQ001/schema2 as CPU totals.
2. Init once before association; separately authorized inactive PRT1 admission
   precedes use. Select AGON_NETA_CPU_MARKER=agon_cpu_entry with this matched
   net_async.h and EMOS_CPU_ACCOUNTING. OPEN8 has op0, service pointer24, marker
   pointer24, discriminator C1. NULL is supported; old OPEN7 cannot collide.
   Use the normal include root plus the matched UART core include directory.
3. Once both real UART owners positively prove quiescence, a nonzero epoch may
   start ONE window. The API accepts these owner facts; it does not manufacture
   them from no pending NM or source release. No rearm/second window is allowed
   in this minimal app lifetime. This avoids silently discarding a live record.
   Each new app lifetime requires fresh true quiescence and leaves the gap
   explicitly unknown; no90s continuous ledger exists.
4. Stop in foreground with no live gateway/IRQ/callback/wait annotation, retire
   timer, positively CLOSE the actual owner, then copy via snapshot. Refused
   CLOSE/quarantine retains all code/record/source/provider storage. STOP,
   sourceNULL, timeout or a cached wire-idle value never detach a hook.
5. No timer IRQ/vector is installed. PRT1 /256 single pass must stay nonzero,
   control0Dh and same system source. Samples must descend without wrap.
   Elapsed >54000 nominal counts is invalid (0.75s at nominal72000Hz). Timer
   expiry, source/control change, nesting mismatch, saturation or poison
   invalidates the snapshot; it does not become a zero duration.
6. MGCPU001/schema1 is96 bytes, LE counters independent of C packing. Totals
   at32 are five exclusive16-bit **instrumented interval** buckets: foreground,
   foreground gateway, maskable IRQ, taken-HALT and internal observer. Vector
   subdivisions42 and counts48 are U0/U1/VBlank; subdivisions are NOT extra
   totals. Markers54 counts boundaries. Byte62/63 record bounded callback
   annotation depth/highwater (max4), byte27 bounds wait annotation depth1.
   These are orthogonal annotations, not additional CPU buckets. Byte56 is
   reserved; no undocumented semantic reason value is inferred from it.
7. Each marker samples before and after native recorder work. The second
   sample does not cover its own subsequent accumulator/store/restores/RET;
   entry register saves and EMOS prefix/suffix are also omitted. PARTIAL
   BOUNDARIES and UNKNOWN GAP are always set. Their duration is UNKNOWN, not0.
   Thus foreground/HALT buckets include boundary bias and cannot be called
   pure physical CPU/HALT occupancy or used for a complete CPU% claim. No
   instruction-cycle calibration or electrical receive reserve is supplied.
8. UART0 entry follows its existing receive-protection guard and precedes IIR;
   every RX/TX exit follows the full UART1/RX-first service tail. UART1 entry
   follows initial reserve-enter and precedes variable RX-first; exit follows
   both passes/reserve-leave. VBlank includes clock/retry/full keyboard tick.
   I2C/default-vector/fatal/NMI run an independent poison leaf. Unsupported
   vectors are not claimed measured zero. Caller vector replacement loses
   coverage and is forbidden in a qualified composition.
9. NMI poison touches only record byte13 and its own AF save, never shared
   marker scratch. Maskable nesting is rejected; no nested EI is introduced.
   Reset destroys the app session: an active/incomplete retained record has no
   positive stopped snapshot and MUST be rejected. No uninitialized RAM-pointer
   call was inserted in early reset. A newly started app is a new session, not
   resumption/completion of a pre-reset window.
10. Native event ABI is A, all regs/IFF preserved by entry. Foreground wrapper
    additionally preserves incoming IFF. Events1/2/3 enter actual vectors and
    81/82/83 exit;4/84 gateway;6 taken HALT,86 return,7 raw AW_WORK. First IRQ
    after HALT ends its logical wait and resumes foreground on IRQ return.
    The atomic-wait owner must place6 before the adjacent EI/HALT, not between
    them. No shared MOS wait leaf is changed here.20/21 callback and30/31 wait
    annotations are optional balanced boundaries. No callback-exclusive total
    or extra UART LSR/RBR/CTS/service sample is added.

The full root CPU headroom objective, physical fit, runtime timer permission,
wait-owner integration,128KiB capture migration and a finite physical case remain
separate. Production selection, current device bytes and old evidence are unchanged.
