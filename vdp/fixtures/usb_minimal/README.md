# USB-only keyboard enumeration reproducer

This INPUT-004 firmware isolates the pinned ESP-IDF USB host/HID path on the
same P4-PC HS peripheral and onboard hub. It provides no Extender display,
network, EMOS keyboard, Agon UART, SD or controller service. Successful raw USB
enumeration/admission is the comparison; this is not a MOS application and does
not implement a MOS video-mode lifecycle. The host owns exact Extender app
restoration before releasing Agon reset or claiming normal CLI readiness.

Boot is inert. Only the independent USB Serial/JTAG console is initialized.
An admitted host sends one literal `START` line while Agon is held in reset.
That starts one acquisition; another START is rejected until an intentional
external restart. `STOP` ends the active observation, and `STATUS` only reports
retained application state. Neither command resets, retries or reflashes.

The acquisition window is20seconds from START, including hub setup. Keyboard
boot-protocol admission followed by5clean seconds ends early. API, transfer,
disconnect or queue-overflow failures end immediately. The installed USB/HID
APIs do not expose initial failed-enumeration events: the host retains the
ordinary SDK `ENUM ... FAILED` serial line and may issue STOP. A window timeout
does not identify a unique USB cause. Existing blocking HID control APIs each
have the pristine component's5second timeout, so handling a command/deadline
can be delayed by a call already in progress. No host timer causes a reset.

Lines beginning `USBMIN ` contain JSON ready/start/enumerated/HID/error/end
records. The host must durably save the complete serial capture; firmware does
not write flash, NVS or SD evidence. END freezes fixture evidence and leaves the
application passively accepting STATUS/rejecting START. USB library/HID tasks
retain ordinary SDK maintenance; this is not a claimed bus shutdown. No keys
are delivered to EMOS. F310 may enumerate as a full-speed device but its vendor
XInput interface has no controller client here; no controller-report result is
claimed. Report payloads are not printed.

## Reconstructing the candidate

1. Use exactly ESP-IDF5.5.5 commit
   `b774170ff46c393eeb5e495ea37936038d3f4f4f`, and a pristine USB Host HID1.2.1
   component from upstream commit `e3c35b840b9fc9969b981011c9ff782c01168433`.
   Copy the latter to the generated project's `components/usb_host_hid` and set
   `IDF_COMPONENT_MANAGER=0`. The manifest records the intended dependency;
   the host builder verifies exact component tree bytes, not just that string.
   Do not copy an installed locally patched HID component by assumption.
2. The host builder provides `USB_MINIMAL_BUILD_ID`,
   `USB_MINIMAL_SOURCE_COMMIT`, `USB_MINIMAL_HUB_RESET_GPIO`,
   `USB_MINIMAL_HUB_ASSERT_MS` and `USB_MINIMAL_HUB_RECOVERY_MS` as CMake inputs.
   Obtain board constants from maintained `vdp/build/boards/p4-pc.json` and
   retain their provenance; CMake generates `usb_minimal_config.h`. No hostnames,
   serial identities, mount paths or other machine values belong in this tree.
3. Match installed silicon range100–199, CPU/cache/tick/USB memory settings,
   root/hub timing and existing app partition. Disable flash coredump output.
   `sdkconfig.defaults` supplies relevant baseline defaults but does not replace
   host verification of effective SDK configuration and linked components.
4. The host-install task is pinned to core1 with priority6, matching Extender's
   IRQ allocation core. HID uses priority5/no affinity. The event queue exists
   before either library starts. The hub active-low reset uses the supplied
   maintained board timings, then default peripheral-map0 selects the HS block.
5. `fsls_only.cmake` changes only HCFG.FSLSSUPP immediately before root reset,
   against a hash-pinned upstream HCD. No stage/register instrumentation, IN cache
   backport or deferred USBH logging patch is included. Other SDK USB units stay
   original. The host must verify the sole generated HCD compile/archive/link
   selection and original USBH selection in the build receipt.

The source API flow is adapted from Espressif's pinned
`examples/peripherals/usb/host/hid/main/hid_host_example.c`. It removes the
example's GPIO0 quit assumption and installs the queue before USB callbacks.

The absent non-control IN cache backport is intentional: initial control
enumeration was already synchronized in the pinned driver. A later report
failure cannot be attributed to Extender removal alone. Successful admission
would implicate integration/configuration/scheduling differences; the same
initial descriptor failure would produce a smaller upstream reproducer without
proving a silicon or SDK defect. Undocumented PHY/register toggles are excluded.
