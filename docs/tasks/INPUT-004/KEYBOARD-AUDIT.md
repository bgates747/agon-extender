# USB keyboard comparison — INPUT-004

The first audited keyboard is a Logitech K120 with a standard boot-keyboard
interface. Linux successfully enumerates it at 1.5 Mbit/s. It is a useful
second low-speed device for the P4 investigation; it does not supply the
full-speed keyboard control proposed in the task. P4 compatibility remains
untested for this keyboard.

## Comparison

| Property | Logitech K120 |
|---|---|
| Audit run | INPUT-004-2026-10-28-21-33-10Z |
| Manufacturer/product strings | Logitech / USB Keyboard |
| USB ID | `046d:c31c` |
| Device revision / USB specification descriptor | `bcdDevice=0x6402` / `bcdUSB=0x0110` |
| Negotiated speed | **1.5 Mbit/s, low speed**; sysfs and USB topology agree |
| EP0 maximum packet | 8 bytes |
| Configurations / interfaces | 1 / 2; both interfaces use alternate setting 0 |
| Keyboard interface | Interface 0: HID `03`, boot subclass `01`, keyboard protocol `01` |
| Keyboard interrupt endpoint | IN `0x81`, maximum packet 8 bytes, declared interval 10 ms |
| Keyboard report descriptor | 65 bytes; no report IDs; 8-byte input layout |
| Keyboard input layout | 1 modifier byte, 1 reserved constant byte, 6 keycode slots |
| LED output descriptor | 1 byte: 5 LED bits and 3 padding bits |
| Additional interface | Interface 1: HID `03/00/00`, consumer/system controls and vendor feature |
| Additional interrupt endpoint | IN `0x82`, maximum packet 4 bytes, declared interval 255 ms |
| Additional report descriptor | 184 bytes; input IDs 1, 2 and 3; feature ID 5 |
| Declared configuration power | Bus powered, maximum 90 mA; remote wake capability |
| Linux binding | Both USB interfaces bind to `usbhid`; HID instances use `hid-generic` |
| Observed Linux topology | Directly below a host root hub; no internal keyboard hub observed |
| Linux enumeration | Successful; descriptors, HID instances and input capabilities readable |
| Actual physical typing / LED exercise | Not performed during this descriptor audit |
| P4 enumeration / typing | Not tested for this specimen |

The interval values are endpoint declarations, not measured report rates or
input latency. Configuration power is declared demand, not a current or voltage
measurement. `bcdUSB` describes the USB specification; negotiated speed comes
from sysfs/topology. This host's verbose `lsusb` prints a rounded `1Mbps` label
for this device, while sysfs and `lsusb -t` correctly report 1.5 Mbit/s.

## Interpretation against the current P4 client

1. The P4 keyboard client selects HID boot subclass/keyboard protocol, so
   interface 0 matches its admission filter. The 8-byte modifier/reserved/six-key
   layout matches the maintained decoder. This is descriptor compatibility,
   not proof that P4 enumeration or its subsequent class requests will succeed.
2. The P4 client selects boot protocol. Interface 1 is separate from ordinary
   typing and does not meet that client's filter; media/system controls on that
   interface are outside the current keyboard feature. Their report IDs do not
   make interface 0 incompatible.
   Including each report ID byte, its inputs are 2, 2 and 4 bytes respectively;
   the vendor feature report is 6 bytes and is not an interrupt input report.
3. Because this keyboard is also low speed, comparing it with the originally
   failing keyboard can distinguish a device-specific interaction from a shared
   P4 low-speed path. Linux success alone does not identify the P4-side fault.
4. The Author will attach the originally failing keyboard to the Linux audit
   host next, followed by two additional models. Preserve a separate immutable
   audit run for each attachment; append their columns/results here. Select a
   full-speed boot keyboard for a P4 control if any specimen actually negotiates
   at 12 Mbit/s. Retain browser recovery and the unchanged firmware composition.

## Evidence identity and collection limits

Read-only collection on 2026-10-28 took 0.47 local-host monotonic seconds,
excluding initial discovery and interpretation. It retained 79 records,
including binary USB/configuration and both HID report descriptors, decoded
`lsusb` output, sysfs properties, topology and driver/input capabilities. The
selected USB address remained stable throughout collection. No input-event
stream was read, driver detached, keyboard setting changed or device reset.
The P4 bench was not accessed. Raw host-specific records and the repeatable
machine-local collector are indexed in `HARDWARE.local.md`.

| Retained descriptor | SHA-256 |
|---|---|
| Device/configuration bytes, 77 bytes | `0a2162ad783fd450070e479a74b5bbbe1e0c8114088cfcdc1a64f0d9528bbc5a` |
| Interface 0 report, 65 bytes | `5333cc3a23db1dd7a9e8303e2169a54a7070f69822fa503014834652c24410b6` |
| Interface 1 report, 184 bytes | `079ef49793e62bf0afc17b68d0d3506be78cf682541eee8c4e83af70fee4342c` |
