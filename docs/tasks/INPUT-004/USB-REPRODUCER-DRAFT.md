# Draft: P4 low-speed keyboard fails its first descriptor request through FS hub

A minimal USB-only application reproduces the keyboard's initial descriptor
failure on a P4-PC. A full-speed F310 enumerates through the same onboard hub.
This draft asks Espressif to identify the supported pre-v3 P4 configuration or
a known correction. It does not establish a chip or driver defect.

**Prepared for Author review; not submitted.** This report contains generic board
and source identities, not private host addresses, credentials or unique device
serial numbers. Any public submission or source attachment requires separate
Author authorization. Retained local source/log archives remain unchanged.

## Hardware and selected software

| Item | Reproducer |
|---|---|
| Board / chip | Olimex ESP32-P4-PC Rev C; boot reports P4 v1.3 |
| SDK | ESP-IDF 5.5.5, `b774170ff46c393eeb5e495ea37936038d3f4f4f` |
| Silicon configuration | `CONFIG_ESP32P4_SELECTS_REV_LESS_V3=y`; effective min100/max199 |
| HID component | `espressif/usb_host_hid` 1.2.1; pristine vendor package; upstream `e3c35b840b9fc9969b981011c9ff782c01168433` |
| USB controller / topology | Integrated HS-capable controller, forced FS/LS-only root; onboard hub; directly attached LS keyboard plus FS F310 |
| Keyboard | Logitech K120 `046d:c31c`; Linux enumerates it at1.5Mbit/s, EP0 MPS8, standard boot-keyboard interface; no internal hub observed |
| Other device | F310 `046d:c21d`, full speed; enumeration observer only, no XInput client in this reproducer |
| USB ownership | Host installed on core1, priority6; HID worker priority5, no affinity; event queue created before either starts |
| Board hub reset | GPIO21 active-low, asserted20ms, recovery200ms |
| Acquisition | Inert boot; one explicit serial START; host sends STOP after definitive failure; no physical replug or application/host replay; ordinary SDK/hardware retry policy retained |
| Excluded services | No Extender video/network/controller client/Agon transport/SD service |

The SDK remains unmodified. The only generated HCD change restricts an
HS-capable root to FS/LS immediately before root reset, following Espressif's
[FS/LS-only guidance](https://docs.espressif.com/projects/esp-usb/en/latest/esp32p4/usb_host.html#full-low-speed-only-host).
IDF 5.5.5 has no public install-time FSLS option. The adaptation adds:

```c
if (port->hal->constant_config.hsphy_type != 0) {
    usb_dwc_ll_hcfg_set_fsls_supp_only(port->hal->dev);
}
```

immediately before the existing `usb_dwc_hal_port_toggle_reset(port->hal, true)`.
Original HCD SHA-256:
`33fea9059ee546d1c773fc5e86ed0c294e600e645c4c14e0788ce879f596280b`;
complete generated HCD SHA-256:
`e26a6ecaac14fd67814b00722d8d1df39305006905fd9362c889f17cfbfd1625`.
There is no cache, transfer-stage, register-diagnostic or USBH logging patch in
this minimal image. Existing SDK control-buffer synchronization and its1ms
LS-via-FS-hub stage delay remain intact.

## Observed result

One explicit START yields the following excerpt from the retained serial capture:

```text
USBMIN {"event":"host_ready","irq_core":1,"hid_core":-1,"peripheral_map":0}
W (2207) HCD DWC: Low-speed, extra delay will be applied in ISR
E (2208) USBH: Dev 0 EP 0 Error
E (2208) ENUM: Bad transfer status 1: CHECK_SHORT_DEV_DESC
E (2209) ENUM: [1:3] CHECK_SHORT_DEV_DESC FAILED
E (2209) EXT_PORT: [1:3] Port disabled, reset attempts=1
W (2393) hid-host: No HID device at USB port 2
USBMIN {"event":"enumerated","address":2,"vid":1133,"pid":49693,"speed_usb_enum":1,"class":255}
USBMIN {"event":"end","reason":"HOST_STOPPED","elapsed_us":6027266,"enumerations":1,"keyboard_admitted":false,"reports":0,"restart_allowed":false}
```

The host sent STOP five observed seconds after the definitive failure and kept
five further clean seconds after END. END reports controlled acquisition
completion, not success or measured enumeration latency. The HID warning concerns
F310's vendor interface at USB address2. It does not identify another failed
keyboard port. No HID keyboard device or report was observed.

This uninstrumented reproducer does **not** distinguish SETUP, DATA or STATUS
within the short-descriptor request. An earlier separate Extender image captured
stage0/SETUP and HAL excessive-transaction error for its own attempt. Its read-only
snapshot showed rootFULL, address0/EP0/OUT/MPS8, PRE1, DATA0 and FSLS-only enabled.
Those earlier observations must not be claimed as new instrumentation of the
minimal image. Neither capture observes USB wire signaling.

## Retained identity and source

1. Fixture source commit: `4610e9672bdb420e554cef1326a6fea756426ede`,
   [native source and lifecycle](../../../vdp/fixtures/usb_minimal/README.md),
   [pinned host builder](../../../scripts/build_usb_minimal.py).
2. Tested build: `input004-usb-minimal-r01-b2026-10-29-00-05-23Z`.
   Application289184bytes, SHA-256
   `0e0d896847907dd43ce5231adeb83591730bdbdee09b912ea952a18b33907a3b`.
   Source and HID archives are retained separately with exact inventories.
3. Complete serial capture5180bytes, SHA-256
   `92ac6466a4daa58bb8706df45a13a5b2a605a8ba951922a9e3a5546a1c37be9e`.
   The diagnostic application was removed after this result and exact original
   P4 flash restoration was verified; no repeat is implied by this draft.
4. The image and ready receipt identify the exact source/build; START repeats
   the build. END belongs to that one-shot capture and does not itself repeat
   source/build fields. Target elapsed units are `esp_timer` microseconds;
   physical calibration was not measured. Source/configuration/compiled-linkage
   checks passed separately.

## Questions for Espressif

1. Is a pre-v3 P4 v1.3 HS-UTMI controller, with a full-speed upstream hub link
   and low-speed downstream keyboard, supported by this SDK configuration?
   If a correction or restriction applies, what exact public commit/document
   identifies it?
2. The [reviewed USB host1.6.0 release](https://components.espressif.com/components/espressif/usb/versions/1.6.0)
   retains the selected initial-control/PRE functions and requires
   `USB_DWC_HAL_INIT_HAS_CONFIG` for its public FSLS option, which our SDK lacks.
   Is there a released, pre-v3-compatible SDK/component pair recommended for
   this particular topology, rather than an unrelated general upgrade?
3. What is the integrated HS-UTMI DWC frame-clock/HFIR contract when the root
   operates at full speed, and what is the documented polarity/use of
   UTMI.FC06 `pre_hphy_lsie`? Existing public register labels do not establish
   a safe clock or preamble change. No such speculative changes were made.

The separate [compatibility assessment](USB-COMPATIBILITY.md) records the bounded
source comparison and why matching existing public reports do not yet establish
the same fault. The submitted report, if authorized, should preserve the local
adaptation disclosure and distinguish observed facts from hypotheses.
