# USB keyboard comparison — INPUT-004

Both audited keyboards enumerate successfully on Linux at 1.5 Mbit/s and expose
standard boot-keyboard interfaces. The originally failing P4 keyboard identifies
as `04d9:a088`, a Holtek USB vendor ID, without brand/model strings. Neither
keyboard supplies the full-speed control proposed in the task. The Logitech
remains untested on P4; the original keyboard's captured P4 failure precedes HID
report handling.

## Comparison

| Property | Logitech K120 | Original P4 keyboard |
|---|---|---|
| Audit run | INPUT-004-2026-10-28-21-33-10Z | INPUT-004-2026-10-28-21-40-01Z |
| Manufacturer/product strings | Logitech / USB Keyboard | Neither supplied; Holtek vendor ID does not establish retail brand/model |
| USB ID | `046d:c31c` | `04d9:a088` |
| Device revision / USB specification descriptor | `bcdDevice=0x6402` / `bcdUSB=0x0110` | `bcdDevice=0x0113` / `bcdUSB=0x0200` |
| Negotiated speed | **1.5 Mbit/s, low speed** | **1.5 Mbit/s, low speed** |
| EP0 maximum packet | 8 bytes | 8 bytes |
| Configurations / interfaces | 1 / 2; alternate setting 0 | 1 / 2; alternate setting 0 |
| Keyboard interface | Interface 0: HID `03/01/01`, boot keyboard | Interface 0: HID `03/01/01`, boot keyboard |
| Keyboard interrupt endpoint | IN `0x81`, maximum packet 8 bytes, declared interval 10 ms | IN `0x81`, maximum packet 8 bytes, declared interval 10 ms |
| Keyboard report descriptor | 65 bytes; no report IDs; 8-byte input layout | 62 bytes; no report IDs; 8-byte input layout |
| Keyboard input layout | 1 modifier byte, 1 reserved constant byte, 6 keycode slots | Same modifier/reserved/six-key layout |
| LED output descriptor | 1 byte: 5 LED bits and 3 padding bits | 1 byte: 3 LED bits and 5 padding bits |
| Additional interface | Interface 1: HID `03/00/00`, consumer/system controls and vendor feature | Interface 1: HID `03/00/00`, system/consumer controls and relative mouse |
| Additional interrupt endpoint | IN `0x82`, maximum packet 4 bytes, declared interval 255 ms | IN `0x82`, maximum packet 8 bytes, declared interval 10 ms |
| Additional report descriptor | 184 bytes; input IDs 1, 2 and 3; feature ID 5 | 153 bytes; input IDs 1, 2 and 3 |
| Declared configuration power | Bus powered, maximum 90 mA; remote wake capability | Bus powered, maximum 100 mA; remote wake capability |
| Linux binding | Both interfaces `usbhid`; HID instances `hid-generic` | Both interfaces `usbhid`; HID instances `hid-generic` |
| Observed Linux topology | Directly below a host root hub; no internal hub observed | Directly below a host root hub; no internal hub observed |
| Linux enumeration | Successful; descriptors, HID instances and input capabilities readable | Successful; descriptors, HID instances and keyboard/consumer/system/mouse capabilities readable |
| Actual physical typing / LED exercise | Not performed during descriptor audit | Not performed on Linux during descriptor audit |
| P4 enumeration / typing | Not tested for this specimen | Initial SETUP failure captured; Author observes no typed characters |

The interval values are endpoint declarations, not measured report rates or
input latency. Configuration power is declared demand, not a current or voltage
measurement. `bcdUSB` describes the USB specification; negotiated speed comes
from sysfs/topology. This host's verbose `lsusb` prints a rounded `1Mbps` label
for both devices, while sysfs and `lsusb -t` correctly report 1.5 Mbit/s.

## Interpretation against the current P4 client

1. The P4 keyboard client selects HID boot subclass/keyboard protocol, so both
   devices' interface 0 matches its admission filter. Their 8-byte modifier/
   reserved/six-key layouts match the maintained decoder. This is compatibility
   of the inspected descriptors,
   not proof that P4 enumeration or its subsequent class requests will succeed.
2. The P4 client selects boot protocol. Interface 1 is separate from ordinary
   typing and does not meet that client's filter; media/system controls on that
   interface are outside the current keyboard feature. Their report IDs do not
   make interface 0 incompatible.
   On K120, including each report ID byte, its inputs are 2, 2 and 4 bytes;
   its vendor feature report is 6 bytes and is not an interrupt input report.
   On the original keyboard, the system/consumer/mouse inputs are respectively
   2, 4 and 4 bytes including their IDs. The mouse descriptor does not establish
   the presence or operation of a physical pointing control.
3. Both keyboards are low speed. Comparing them on P4 can distinguish a
   device-specific interaction from a shared P4 low-speed path. Linux success
   alone does not identify the P4-side fault. The original keyboard's ordinary
   report layout supplies no reason to change the decoder for its earlier
   initial-SETUP failure.
4. Two additional models remain available for Linux audit after the original
   keyboard. Preserve a separate immutable
   audit run for each attachment; append their columns/results here. Select a
   full-speed boot keyboard for a P4 control if any specimen actually negotiates
   at 12 Mbit/s. Retain browser recovery and the unchanged firmware composition.

## Evidence identity and collection limits

Read-only collection on 2026-10-28 took 0.47 local-host monotonic seconds for K120
and 0.45 seconds for the original keyboard, excluding discovery/interpretation.
It retained 79 and 82 records respectively, including binary USB/configuration
and both HID report descriptors for each device, decoded
`lsusb` output, sysfs properties, topology and driver/input capabilities. The
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
