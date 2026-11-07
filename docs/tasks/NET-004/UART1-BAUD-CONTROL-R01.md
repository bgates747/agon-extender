# Paired half-baud UART1 control assessment

A matched576000-baud P4/EMOS pair is feasible as an explicit experimental control.
It doubles the nominal empty16-byte receiver interval and leaves ample raw line
capacity for the existing small NM traffic. This is source arithmetic, not proof
of reliable service, spare CPU or a fix for consumer83. No firmware installation or physical
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

## Selected contingency source preparation

After checked serialized R04 preparation, Mech selects coherent paired576000
source/control preparation under the existing reliability goal. Current86 live
case takes precedence: no compiler launch or target call until actual root
stopped return. No install, next physical case or ordinary-default change is
selected by this preparation. Keep native observer80fe separately frozen.

1. [x] Create isolated EMOS derivative of954e3c54 and P4 derivative ofe14e0b8a,
   not the optional accounting/observer trees. Retain exact8de/d9b rollback.
2. [x] Change only the selected owner UART1 baud setup and its identifying
   source/build metadata to576000. Keep UART0, source/CTS/retry/IRQ algorithms,
   P4 RX reserve and NM/keyboard/control framing unchanged. A small literal
   task-private control is sufficient; no runtime retune or resident fallback.
3. [ ] Strengthen the owner build guards to prove selected UART1 divisor2 and
   unchanged UART0 divisor1, plus actual paired P4 configuration/source binding.
   Preserve every mandatory existing check and reject mismatched declarations.
4. [ ] After actual current-case stop, normal FIFO finite paired original/control
   builds and identity-bound links record ROM/BSS/image/stack and exact artifacts.
   No new SDK/client wire algorithm or unobserved source/buffer lifetime change.
5. [ ] Only a later separately selected finite case may stage/install the pair
   through independent recovery/current bootstrap and full readbacks. Keep the
   old pair usable for rollback if half-installed input/SD becomes unavailable.

Research baseline is the exact owner UART setup/arithmetic source described
above and the official documentation/source baseline in the receive-diagnostic
plan. No additional hardware tolerance or measured latency is assumed.

Source-only draft is prepared in separate owner branches from954e3c54/e14e0b8a.
EMOS changes only owned UART1 settings literal and adds source/linked divisor
checks plus a paired-control manifest field. P4 changes only UART_NUM_1 setup/
bootlabel and binds a task-private source declaration into its native builder
and artifact manifest. No runtime option, fallback or ordinary default change.
Python syntax inspected; native builds, linked settings controls and size remain
pending. No compiler was launched during the current86 live observation.

## Finite native build tranche

After actual86 stopped, build the experimental matched pair under one normal
Pi compiler lease, serially: original EMOS identity-matched byte control, new
half-baud EMOS identified wrapper/all mandatory linked checks, original P4
source/configuration reproduction, then new half-baud P4 native build. Retain
full exact source closures to954e3c54/e14e0b8a and original installed8de66/d9b
artifacts; current incominga25f is rollback, not the app-enabled comparison arm.
The P4 original and candidate retain the existing reset endpoint by private
configuration/hash, HDMI/USB/controller/boot/dependency settings. No optional
accounting/observer source is selected. Use two P4 compiler workers, low priority,
one-second thermal/resource telemetry,80C and512MiB floor; each P4 child840s,
whole tranche2100s. Stop on first failure, join owned children and immediately
release/notify actual compiler successor before lengthy analysis. Record ROM/
image/sections and effective configuration differences; build success is not
physical baud, CTS response or application performance qualification.
