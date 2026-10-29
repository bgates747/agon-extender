# USB host compatibility assessment

The reviewed newer USB host release does not supply an identified correction for
the keyboard's initial request failure. It supports the installed SDK in general,
but its public FS/LS-only option needs a HAL capability absent from that SDK.
A component-only change would retain the same PHY/HAL and the same initial
control-transfer functions. Keep the reproduced baseline; another firmware
trial needs a stated diagnostic purpose rather than an assumed upgrade fix.

Assessment date: 2026-10-28, with source retrieval continuing on 2026-10-29 UTC.
This is bounded research under [INPUT-004](../INPUT-004.md), not production
selection, hardware qualification or a claim that every upstream fix was searched.

## Exact inputs and compatibility boundaries

| Input | Selected identity | Finding |
|---|---|---|
| Baseline SDK | ESP-IDF 5.5.5, `b774170ff46c393eeb5e495ea37936038d3f4f4f` | Actual P4 v1.3 uses the explicit pre-v3 configuration and revision bounds 100–199. Keep these guards. |
| Reviewed component | Espressif USB host 1.6.0, `630f1c4e61f71d62bb57ff1b840931da24c3329f`, released 2026-10-05 | Manifest requires IDF >=5.5.3 and includes the P4 target. Those declarations alone do not establish every optional feature or silicon revision. |
| Component override | USB 1.6.0 on IDF 5.x | Espressif supports overriding the bundled USB component. Its CMake deliberately retains the selected SDK's `usb_phy.c`; SDK HAL/LL also remain selected. |
| Public `fsls_only` | USB 1.6.0 with the pinned SDK | HCD checks `USB_DWC_HAL_INIT_HAS_CONFIG`. Without it, requesting this option returns `ESP_ERR_NOT_SUPPORTED`. IDF 5.5.5 lacks that capability. Do not fake the macro or remove the refusal. |
| Existing FSLS backport | Pinned baseline HCD, immediately before root reset | Already sets the root's FS/LS-only restriction. The inspected development HAL performs the equivalent restriction at reset; obtaining the public API alone is not an identified new remedy. |

Primary authorities: [official component release and manifest](https://components.espressif.com/components/espressif/usb/versions/1.6.0),
[release changelog](https://components.espressif.com/components/espressif/usb/versions/1.6.0/changelog?language=en),
[override guidance](https://components.espressif.com/components/espressif/usb/versions/1.6.0/readme),
[exact HCD](https://github.com/espressif/esp-usb/blob/630f1c4e61f71d62bb57ff1b840931da24c3329f/host/usb/src/hcd_dwc.c),
[exact component CMake](https://github.com/espressif/esp-usb/blob/630f1c4e61f71d62bb57ff1b840931da24c3329f/host/usb/CMakeLists.txt)
and [pinned P4 revision configuration](https://github.com/espressif/esp-idf/blob/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/esp_hw_support/port/esp32p4/Kconfig.hw_support).

Additional released SDK checks preserve the distinction between pre-v3 support
and the optional new HAL capability:

| Examined release | Exact release commit | Pre-v3 / HAL result |
|---|---|---|
| IDF 5.5.6 | `880a203ae603d08a94d06aa01e0d6761958e5e9e` | Kconfig retains the pre-v3 family; inspected HAL implementation still uses the old initializer. Exact header retrieval was unsuccessful. |
| IDF 6.0 | `662a3be354759d9487bf4b1a629fadb766cb1800` | Kconfig retains the pre-v3 family; inspected HAL implementation still uses the old initializer. Exact header retrieval was unsuccessful. |
| IDF 6.1 | `fff9895c82d744c7237be8847347bdd1b07c6643` | Kconfig retains the pre-v3 family; inspected complete HAL header lacks the configured initializer/capability macro. |

These are bounded source checks, not compiled replacement SDKs. They identify no
released SDK with the required capability within this examined set; they do not
establish the earliest supporting release or rule out every other release.
References: [5.5.6 HAL implementation](https://github.com/espressif/esp-idf/blob/880a203ae603d08a94d06aa01e0d6761958e5e9e/components/hal/usb_dwc_hal.c),
[6.0 HAL implementation](https://github.com/espressif/esp-idf/blob/662a3be354759d9487bf4b1a629fadb766cb1800/components/esp_hal_usb/usb_dwc_hal.c),
[6.1 HAL header](https://github.com/espressif/esp-idf/blob/fff9895c82d744c7237be8847347bdd1b07c6643/components/esp_hal_usb/include/hal/usb_dwc_hal.h).
The separately inspected [development HAL](https://github.com/espressif/esp-idf/blob/master/components/esp_hal_usb/usb_dwc_hal.c)
is a moving research reference, not a pinned or selected build input.

The retained official component ZIP has SHA-256
`da5be2a2743ede3bd63e6c4046e381e24b16567ea8a7541b6f5d094abea5098b`.
Its HCD has SHA-256
`f7be5cff2be70176baab93e1b4e643e1d5bd3cd56383f01cc79392c76c5adc15`.
Native exact-commit downloads independently match the package HCD and CMake
bytes. The packaged manifest adds repository commit metadata and normalizes the
repository URL; its other parsed fields match the repository manifest.
The ignored research receipt records the download URL, all 28 package files and
its explicitly defined content digest. Package hashes identify research inputs;
they are not added to processor communications.

## Initial-request comparison

Whole-function comparisons against the retained release package give these
results. Equality covers those functions, including comments and whitespace;
it does not establish complete stack equivalence or correct electrical behavior.

| Relevant behavior / function | IDF 5.5.5 versus USB 1.6.0 | Diagnostic implication |
|---|---|---|
| PRE and EP0 configuration: `pipe_set_ep_char` | Byte-identical | No identified new low-speed PRE selection remedy. |
| Initial control descriptors: `_buffer_fill_ctrl`, `_buffer_fill` | Byte-identical | No identified new first-request descriptor construction remedy. |
| First execution and continuation: `_buffer_exec`, `_buffer_exec_cont` | Byte-identical | No identified new initial SETUP sequencing remedy. |
| Completed-stage handling: `_buffer_check_done`, `_intr_hdlr_chan` | Byte-identical | Existing 1 ms PRE stage delay remains. It follows completed stages, not the first SETUP. |
| Short request/parser: `control_request_general`, `parse_short_dev_desc` in `enum.c` | Byte-identical | No identified short-descriptor request/parser remedy. |
| EP0 callback: `ep0_pipe_callback` in `usbh.c` | Byte-identical | No identified EP0 callback correction for this failure. |
| Non-control IN cache cleaning | Changed | CTRL was already synchronized. This independent fix does not identify our first-SETUP cause. |
| Port/enumeration lifecycle and scheduling | Changed | A controlled component comparison could still behave differently; no reviewed change establishes a targeted fix. |

Relevant source is the [exact release directory](https://github.com/espressif/esp-usb/tree/630f1c4e61f71d62bb57ff1b840931da24c3329f/host/usb/src)
and [pinned SDK USB directory](https://github.com/espressif/esp-idf/tree/b774170ff46c393eeb5e495ea37936038d3f4f4f/components/usb).

## Similar reports and limits

1. [Espressif issue 15683](https://github.com/espressif/esp-idf/issues/15683)
   includes similar P4 EP0/short-descriptor logs, but the relevant reports involve
   internal keyboard hubs and a discussion of unsupported split transactions.
   Our root connection is forced to full speed, and the audited keyboards have
   no internal hub in the observed Linux topology. Matching log text or a retail
   K120 name does not establish the same fault.
2. [Issue 18153](https://github.com/espressif/esp-idf/issues/18153) concerns a
   keyboard that enumerates and types before failing after multiple key presses.
   Our failure precedes HID admission.
3. [Issue 604](https://github.com/espressif/esp-usb/issues/604) concerns later
   hub loss/teardown. Its milestone does not establish a released fix for our
   first request. Do not resume the Author-deprioritized controller transient
   investigation on this basis.
4. Public source still does not resolve the precise integrated HS-UTMI frame
   clock or ambiguous preamble-bit contract recorded in the owning task.
   No undocumented bit toggle, guessed frame interval or added delay follows.

## Result and next evidence

Extender performed no new native build, flash, reset, input injection or bench
access for this assessment. The exact restored Extender application and original
minimal failing build remain the comparison authorities. Production is unchanged.

An adapted USB 1.6.0 comparison is structurally possible on the existing SDK:
keep its public `fsls_only` false, leave the SDK capability refusal untouched,
and apply the same explicitly identified root-reset backport. That would test
broader host-component changes, with the same SDK PHY/HAL. It has no demonstrated
first-SETUP fix and was not built or selected here.

The [draft reproducer report](USB-REPRODUCER-DRAFT.md) collects the existing
negative result and precise questions for Espressif. Extender has not contacted
Espressif or published a report/attachment. Author selection of vendor review,
a discriminating wire capture or a specifically justified firmware comparison
remains in the owning task's decision register.
