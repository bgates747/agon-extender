# Complete USB host override

The `--usb-dual-host --usb-fsls-only` build selects the complete Espressif USB1.6.0
host component so both USB root ports are actually serviced. IDF5.5.5's original
hub chooses one port even after both PHYs are initialized. The earlier PHY-only
recipe/patch are retained for traceability and are not selected by this build.

`usb-1.6.0.zip` is the unmodified28-file official registry archive, identified in
`component.json`, including its Apache-2.0 license. Source commit:
`630f1c4e61f71d62bb57ff1b840931da24c3329f` in
[Espressif's USB repository](https://github.com/espressif/esp-usb/tree/630f1c4e61f71d62bb57ff1b840931da24c3329f/host/usb).
The [registry](https://components.espressif.com/components/espressif/usb/versions/1.6.0/readme)
documents overriding the library on supported IDF5.x releases. The Python builder
verifies the archive and all members, extracts into a fresh generated component,
and leaves both the SDK and pristine component unchanged.

The complete component retains IDF5.5.5's PHY/HAL and silicon guards. Generated
HCD/USBH derivatives apply only two existing local accommodations:

1. Restrict the HS-capable port immediately before root reset. The new public
   `fsls_only` option remains false because this old HAL rejects it. Do not fake
   a newer HAL capability. USB1.6.0 already contains the DMA IN cache correction.
2. Defer EP0 error/STALL messages from ISR to task context, before original
   lifecycle actions. New action bits12/13 do not alias existing component
   bits0–11. No old low-speed MMIO probes are imported.

The CMake recipe and validator pin complete derivative bytes and prove the
actual source/object/archive/ELF selection, including both-root hub, enumeration,
public header precedence and SDK-owned PHY. Remove the derivatives only after
qualifying an upstream replacement with equivalent behavior. A clean build or
host lifecycle regression does not establish physical coexistence.
