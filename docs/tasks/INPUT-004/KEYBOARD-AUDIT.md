# USB keyboard comparison — INPUT-004

All three audited keyboards enumerate successfully on Linux at 1.5 Mbit/s and expose
standard boot-keyboard interfaces. The originally failing P4 keyboard identifies
as `04d9:a088`, a Holtek USB vendor ID, without brand/model strings. None
supplies the full-speed control proposed in the task. Logitech and
CHERRY remain untested on P4; the original keyboard's captured P4 failure precedes
HID report handling. CHERRY has the simplest interface layout of the three.

## Comparison

| Property | Logitech K120 | Original P4 keyboard | CHERRY G83 family |
|---|---|---|---|
| Audit run | INPUT-004-2026-10-28-21-33-10Z | INPUT-004-2026-10-28-21-40-01Z | INPUT-004-2026-10-28-21-44-24Z |
| Manufacturer/product strings | Logitech / USB Keyboard | Neither supplied | Neither supplied; family name comes from USB-ID database |
| USB ID | `046d:c31c` | `04d9:a088` (Holtek vendor allocation) | `046a:0011` (G83 / RS 6000 database label) |
| Device revision / USB specification descriptor | `0x6402` / `0x0110` | `0x0113` / `0x0200` | `0x0111` / `0x0200` |
| Negotiated speed | **1.5 Mbit/s, low speed** | **1.5 Mbit/s, low speed** | **1.5 Mbit/s, low speed** |
| EP0 maximum packet | 8 bytes | 8 bytes | 8 bytes |
| Configurations / interfaces | 1 / 2; alternate setting 0 | 1 / 2; alternate setting 0 | 1 / 1; alternate setting 0 |
| Keyboard interface | Interface 0: boot keyboard `03/01/01` | Interface 0: boot keyboard `03/01/01` | Interface 0: boot keyboard `03/01/01` |
| Keyboard interrupt endpoint | IN `0x81`, maximum 8 bytes, interval 10 ms | IN `0x81`, maximum 8 bytes, interval 10 ms | IN `0x81`, maximum 8 bytes, interval 10 ms |
| Keyboard report descriptor | 65 bytes; no report IDs | 62 bytes; no report IDs | 64 bytes; no report IDs |
| Keyboard input layout | 8 bytes: modifier/reserved/six-key | Same 8-byte layout | Same 8-byte layout |
| LED output descriptor | 1 byte: 5 LED bits + 3 padding | 1 byte: 3 LED bits + 5 padding | 1 byte: 3 LED bits + 5 padding |
| Additional interface | HID `03/00/00`: consumer/system/vendor feature | HID `03/00/00`: system/consumer/relative mouse | None |
| Additional interrupt endpoint | IN `0x82`, maximum 4 bytes, interval 255 ms | IN `0x82`, maximum 8 bytes, interval 10 ms | None |
| Additional report descriptor | 184 bytes; input IDs 1/2/3; feature ID 5 | 153 bytes; input IDs 1/2/3 | None |
| Declared configuration power | Bus powered, maximum 90 mA; remote wake | Bus powered, maximum 100 mA; remote wake | Bus powered, maximum 100 mA; remote wake |
| Linux binding | `usbhid` / `hid-generic` | `usbhid` / `hid-generic` | `usbhid` / `hid-generic` |
| Observed Linux topology | Host root hub directly; no internal hub | Host root hub directly; no internal hub | Host root hub directly; no internal hub |
| Linux enumeration | Successful | Successful | Successful |
| Actual Linux typing / LED exercise | Not performed | Not performed | Not performed |
| P4 enumeration / typing | Not tested | SETUP failure captured; Author observes no characters | Not tested |

The interval values are endpoint declarations, not measured report rates or
input latency. Configuration power is declared demand, not a current or voltage
measurement. `bcdUSB` describes the USB specification; negotiated speed comes
from sysfs/topology. This host's verbose `lsusb` prints a rounded `1Mbps` label
for all three devices, while sysfs and `lsusb -t` correctly report 1.5 Mbit/s.

## Interpretation against the current P4 client

1. The P4 keyboard client selects HID boot subclass/keyboard protocol, so all
   devices' interface 0 matches its admission filter. Their 8-byte modifier/
   reserved/six-key layouts match the maintained decoder. P4 enumeration and
   successful class requests require separate physical verification.
2. The P4 client selects boot protocol. Interface 1 is separate from ordinary
   typing and does not meet that client's filter; media/system controls on that
   interface are outside the current keyboard feature. Their report IDs do not
   make interface 0 incompatible.
   On K120, including each report ID byte, its inputs are 2, 2 and 4 bytes;
   its vendor feature report is 6 bytes and is not an interrupt input report.
   On the original keyboard, the system/consumer/mouse inputs are respectively
   2, 4 and 4 bytes including their IDs. The mouse descriptor does not establish
   the presence or operation of a physical pointing control.
3. All three keyboards are low speed. Comparing them on P4 can distinguish a
   device-specific interaction from a shared P4 low-speed path. Linux success
   alone does not identify the P4-side fault. The original keyboard's ordinary
   report layout supplies no reason to change the decoder for its earlier
   initial-SETUP failure.
4. CHERRY's single interface removes the extra HID interfaces present in the
   other two devices, making it a simpler low-speed comparison. Initial SETUP
   occurs before HID interface/report handling, so that simplicity supplies no
   evidence of a remedy for the captured failure.
5. One additional keyboard remains available for Linux audit. Preserve a separate
   immutable audit run for each attachment; append its column/results here. Select a
   full-speed boot keyboard for a P4 control if any specimen actually negotiates
   at 12 Mbit/s. Retain browser recovery and the unchanged firmware composition.

## Evidence identity and collection limits

Read-only collection on 2026-10-28 took 0.47 local-host monotonic seconds for K120
and 0.45 seconds for the original keyboard; CHERRY took 0.39 seconds. These
exclude discovery/interpretation. Collection retained 79, 82 and 49 records
respectively, including binary USB/configuration and each HID report descriptor,
decoded `lsusb` output, sysfs properties, topology and driver/input capabilities. The
selected USB address remained stable throughout collection. No input-event
stream was read, driver detached, keyboard setting changed or device reset.
The P4 bench was not accessed. Raw host-specific records and the repeatable
machine-local collector are indexed in `HARDWARE.local.md`.

| Keyboard / retained descriptor | SHA-256 |
|---|---|
| K120 device/configuration, 77 bytes | `0a2162ad783fd450070e479a74b5bbbe1e0c8114088cfcdc1a64f0d9528bbc5a` |
| K120 interface 0 report, 65 bytes | `5333cc3a23db1dd7a9e8303e2169a54a7070f69822fa503014834652c24410b6` |
| K120 interface 1 report, 184 bytes | `079ef49793e62bf0afc17b68d0d3506be78cf682541eee8c4e83af70fee4342c` |
| Original device/configuration, 77 bytes | `a68464ad7042b7580006ce4707c706af19e8aadd129fd76b97ba2d22cf849ac2` |
| Original interface 0 report, 62 bytes | `f9655a3edfbbd6456802a9643cd138ee859aa1f1ae03bc21c522edfac1343ae2` |
| Original interface 1 report, 153 bytes | `60e3ece84f2e2511da32b0c2e74084b7109b21c4782a8522d444d2b8e1d53201` |
| CHERRY device/configuration, 52 bytes | `45ada985d6d025c52fec27a7a1e0b4202611b38fe65fa236fa998c2b37f2d474` |
| CHERRY interface 0 report, 64 bytes | `7dc1bf27adc8050102009c1a8dd9cc243175e2b6a01a0519f7aa947f8e924292` |
