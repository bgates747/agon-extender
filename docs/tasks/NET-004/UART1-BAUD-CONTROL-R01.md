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
3. [x] Strengthen the owner build guards to prove selected UART1 divisor2 and
   unchanged UART0 divisor1, plus actual paired P4 configuration/source binding.
   Preserve every mandatory existing check and reject mismatched declarations.
4. [x] After actual current-case stop, normal FIFO finite paired original/control
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

## Native EMOS checkpoint; P4 links still pending

The original EMOS954e3c54 rebuild is byte-exact to retained8de66. The isolated
EMOS532a0da derivative passes all mandatory source/linked owner checks, including
UART0 divisor1, UART1 divisor2 and refusals for mismatched old source/executable.
Every byte of the new raw image equals the original after only the owned UART1
baud immediate and the new build timestamp are substituted. ROM layout and map
are identical:130497 used/575 free, no BSS increase. The complete padded image
is fee5eb5955c7efeb2bbe50d3627e1c9bdc50629ef6285a399dbf91ad6c6a847d.
This establishes native source/executable composition, not physical UART timing.

P4 source2496922b and all5557 retained VDP files join exact installedd9b source
e14e0b8a, with only owner UART1 setup/bootlabel altered. Paired manifest/source
checks reject wrong UART0/UART1, framing, flow control, pairing/default declarations
and mismatched actual setup. Fresh original/control native P4 builds are still
pending under compiler368. No paired firmware fit or deployment is claimed yet.

## P4 baseline reproduction and local SDK setup correction

The exact installed-source e14e0b8a native P4 build passed in551.199s. Board,
compiler, dependency lock, effective SDK configuration, HDMI/USB/controller/boot
and private reset-endpoint hash equal the installedd9b manifest; the full
validation report is identical. The new application is1760224B/6e007c12,
versus installed1760160B/d9bcb1a2. It is not byte-exact. Flash text/data/BSS are
unchanged; rodata adds72B, accounted by three generated USB assertion-path
strings that each grow24B in the new output namespace. Embedded build date and
ESP-IDF's automatically discovered project-version string also differ. That
version comes from the containing output checkout, not the maintained clean
e14 source recorded in the manifest. Do not call a future comparison a strictly
baud-bytes-only image substitution; retain these metadata/path/relocation limits.

The half-baud P4 attempt stopped before compilation because its isolated
checkout lacked the ignored link to the existing immutable SDK. No candidate
code executed or device changed. The local link is corrected without source,
SDK or compiler changes. Compiler368 released after all descendants joined;
actual successor Mech369 was notified immediately. A new normal FIFO request
covers only the remaining unchanged P4 source build. No completed original
build or EMOS result is repeated for that ordinary local setup correction.

## Completed native pair and retained limits

Both native firmware wrappers passed their mandatory build/link checks. EMOS
continues to use575B of ROM spare. The P4 linked `beginConsole` setup passes
576000 to physical UART1, with the matching boot label; the retained1152000
executable is refused as that control. UART0 remains1152000/divisor1. Neither
candidate has been installed or run. This is source/native-build readiness,
not a receive-overrun fix, physical baud measurement or application result.

| Native footprint | Fresh1152000 control |576000 control | Difference |
|---|---:|---:|---:|
| EMOS raw ROM |130497B |130497B |0B |
| EMOS free ROM |575B |575B |0B |
| P4 application |1760224B |1760256B |+32B |
| P4 flash text |1338092B |1338092B |0B |
| P4 flash rodata |283708B |283740B |+32B |
| P4 DRAM0 BSS |38392B |38392B |0B |
| P4 DRAM1 BSS |11576B |11576B |0B |

The final P4 raw SDK-config hash comparison stopped after the successful native
build because two partition-file settings contain the different absolute source
checkout paths. A stopped source assessment admits only those two path-valued
keys after comparing both actual partition source files and generated partition
binaries byte for byte; the remaining effective configuration matches exactly.
The original raw configs, hashes and failed driver result are unchanged. No
rebuild or configuration edit was needed. Additional diagnostic path strings,
boot label/build identity and automatic version metadata remain explicit image
differences; unchanged section size is not instruction identity.

Checked source commits are EMOS532a0da and P4 2496922b, both published on their
isolated experimental branches. Full padded EMOS is fee5eb5955c7efeb2bbe50d3627e1c9bdc50629ef6285a399dbf91ad6c6a847d;
P4 application is280469515ea1af04132f42a99d9db3f01c5380a4498295f48dd1c1f9d4370629.
The locally retained15-member source/runtime package is1095024B with SHA256
fc6224401d28b30ce5e748f94a09c49389ab13f228976dbb3f3f2f232f4b0467;
every archive member was compared with its input. It includes private-configured
firmware for local owner coordination, not public binary distribution. Exact
ELFs/maps/configuration, original/control receipts and retained d9b/a25f rollback
remain with the component owner. No production selection or new physical case.

Compiler368 completed the original/native checks and released after the local
setup stop. Compiler370 completed the unchanged P4 control in543.315s and
released14:08:58UTC after all descendants joined; actual successor Wolf371 was
notified immediately. The separate stopped configuration/linked assessment is
not represented as a clean original driver run or executed hardware test.
