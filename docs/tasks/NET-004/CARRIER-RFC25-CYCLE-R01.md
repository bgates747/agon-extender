# Independent guarded RFC25 and parallel cycle

Prepare a generic control that alternates parallel echo records with interrupt
driven UART0 drawing. The ordinary-output control passed without reproducing
the fault. This variant isolates RFC25 scheduling while keeping game records,
modules and asset allocation out of the investigation. No physical invocation
is selected by this source plan.

N04-018.03.5 Retain the existing plain and ordinary graphics builds/evidence.
  Add an explicit parallel-only RFC25 variant; no default workload change,
  application callback-vector replacement, raw UART/GPIO access or new syscall.
  Use the guarded25 contract of the exact EMOS8270 comparison composition. [x]

N04-018.03.6 The eZ80 application owns one static67B immutable packet: four
  ordinary GCOL/PLOT line sequences and one trailing pixel query23,0,84h,x;y;.
  Prearm its source-release flag and pixel-reply flag before the one submission.
  EMOS owns UART0 transmission and the flag-only ISR callback. Mainboard VDP
  executes the packet and returns its pixel reply through ordinary MOS RX.
  Wait for both events before the next network operation. [x]

N04-018.03.7 Keep admission, source release and receiver reply distinct. A0
  admits;19/31/32/35 refuse without publication. Unknown results retain uncertain
  ownership. Callback may precede syscall return and means source release,
  not TEMT. A point reply is an ordered receiver witness, not a public UART
  drain API or optical proof. There is only one point query outstanding; this
  fixture sends no palette query or other point-packet producer. [x]

N04-018.03.8 Preserve foreground ADL1/MB0/EI. The callback only stores a flag
  and returns; no C/MOS/output/EI in ISR. Foreground Escape requests cancellation
  but cannot release borrowed storage. An uncertain outstanding source stops
  all further output/network/cleanup dispatch and retains static RAM/code with
  interrupts enabled for owner recovery. No payload resubmission or timeout
  return that leaves a callback pointing into unloaded application RAM. [x]

N04-018.03.9 Check the actual leaf with source-release-before-return, reply-first,
  source-first, all named refusals, unknown result, source-stall, reply-timeout,
  cancellation, packet content and one-submit assertions. Compile unchanged
  defaults plus the explicit variant through normal compiler FIFO; record exact
  sources and a fresh build timestamp. No hardware during preparation. [ ]

  The finite compile tranche uses one compiler at a time, expected under two
  minutes and a three-minute whole-tranche stop including owned cleanup.
  Each native build and sanitizer step is bounded to30s; require512MiB available
  RAM, temperature below80C and actual owned-descendant retirement before the
  normal compiler release/next-owner handoff. No emulator or target operation.

N04-018.03.10 Only a later complete owner source/current-component/rollback
  freeze may select one finite physical case with the existing echo peer and
  normal fresh exclusive checkout. Original actor retirement/RAM-before-LOAD,
  no replay, exact UART restoration, normal files/feature/state/CLI handback and
  release remain mandatory. No MechAgon case or filter installation is added. [ ]

## Source basis and limits

Official read-only baseline: agon-docs f9806bd3, MOSv3.0.2 and VDPv2.16.0.
The official [system command](../../../../../agon-docs/docs/vdp/System-Commands.md)
defines the pixel query. VDPv2.16.0 `video/vdu_sys.h` decodes its two words,
and `sendScreenPixel()` calls `waitPlotCompletion()` before returning the
ordinary pixel packet. MOS's public point flag/sysvars provide the receive
channel; mode/font notifications use a different flag. This avoids treating
an unsolicited mode packet as the selected query's completion. Colour values
are retained as diagnostics, not used to claim optical correctness.

The maintained EMOS8270 source is71552879. Its guarded RFC25 leaf preserves
BC/DE/HL/IX/IY/shadows/MB and exposes explicit A results with unspecified flags.
Its internal `emos_uart0_async_owned()` checks IER/TEMT before a netp reservation;
that owner function is not a callable application ABI. The source-release
callback and the later receiver reply are both required here, and a later
network refusal still stops without resubmission. No guessed drain number,
internal ROM address or direct TEMT read is introduced.

UART's source reply identifies MechAgon's submit/callback leaf as worked code,
not a general library. Only its established ABI facts inform the independent
small application bridge; no consumer implementation is imported. UART's raw
RC3 examples have different A semantics and are not reused. The actual installed
comparison and eventual rollback must be reconciled afresh before physical work.
