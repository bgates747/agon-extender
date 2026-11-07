# Paired half-baud UART1 control assessment

A matched576000-baud P4/EMOS pair is feasible as an explicit experimental control.
It doubles the nominal empty16-byte receiver interval and leaves ample raw line
capacity for the existing small NM traffic. This is source arithmetic, not proof
of reliable service, spare CPU or a fix for consumer83. No firmware or physical
case is selected here; the diagnostic recorder work continues independently.

1. EMOS owns mainboard UART1 setup in `src/uart.c:uart1_keyboard_open`, currently
   literal1152000/8N1 with hardware flow control. Its widened32-bit calculation
   uses18432000/(16*baud); divisor1 currently and exact divisor2 at576000. The
   ordinary mainboard-to-mainboard-VDP UART0 setup must remain unchanged. Do not
   lower a shared UART default or let a public app reconfigure admitted UART1.
2. P4 owns the other endpoint in `vdp/video/extender/transport/console_hardware.inc`,
   `beginConsole()` UART_NUM_1 config and its boot identification. Both must
   select576000 coherently, preserving pins, 8N1, CTS/RTS, FIFO/reserve/parser,
   NM/keyboard/control/SD semantics and timeout rules. This affects every service
   sharing that physical link, not just NM. ESP8266 Console8 is a separate pair.
3. Nominal8N1 line capacity is57600bytes/s per direction versus115200 currently.
   Byte time becomes17.361us; empty16-byte FIFO geometry277.778us versus138.889us.
   Neither is a safe DI budget: initial occupancy, peer tail, latency and STOP
   response are not established by this arithmetic.
4. Current NM header is14bytes, max payload128, max body142. Mainboard request
   carries four framing bytes plus that body: max146 on the wire (the147th SDK
   input byte is a local selector). One max request at30/60Hz consumes4380/8760
   bytes/s,7.60%/15.21% of the57600B/s directional line. These are single-request
   bounds, not complete Mech turns: actual SEND/POLL/replies, key/control/SD
   traffic and retries must be counted separately from the existing traces.
   One146-byte request occupies2.535ms nominal at576000 versus1.267ms now;
   max body142 occupies2.465ms before its actual reply framing is added.
5. Use a separately identified OFF-accounting P4 derivative and exact EMOS
   derivative with UART1-only compile selection, paired manifests and retained
   d9b/a25f rollback. Existing baud validator derives the fixed UART0 baseline and checks both
   widened arithmetic helpers; add an explicit selected UART1 settings/divisor2
   proof for this composition, retaining the UART0 divisor1 negative controls. Do not disable it. No
   SDK/core/emitter algorithm or persistent ordinary default change is needed.
6. A fresh matched control needs both application installs/readbacks and the
   maintained initialization/input/bootstrap proof before invoking one finite
   unprofiled case. A half-installed mismatch may remove keyboard/SD service;
   prepare the already-supported noninteractive installation/rollback path.
   Preserve normal startup and exact mainboard/native/P4 identities. No silent
   fallback, live retune, transaction replay or extra test is authorized here.
7. Source work should first close the lighter consumer serialization control
   if selected; its run would retain the current baud. Successful half-baud or
   serialization alone would narrow workload/service risks, not identify noise,
   IRQ blackout or the exact cause of the measured overrun.

Exact retained source baseline: EMOS954e3c54 and P4e14e0b8a. The separate optional
accounting sourceae7504c0 is a checked derivative, not installed baud authority.
Native build duration is a preparation estimate only; no added field size or
runtime timing is claimed until actual artifacts exist.
