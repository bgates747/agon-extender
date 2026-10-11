# PORT-008 — READY software review

## Executive summary

No software cause for the DevKit's low READY reading was established. The exact
installed EMOS build initializes Agon PD4 as an input. The historical P4 receiver
configures GPIO20 as an input plus open-drain output and writes one to release
it. Retained compiled code confirms those settings and the correct input bit.
The recent comparison stopped before sender execution or receiver arming; it
provides no parallel payload result. Do not replace an unexplained low input
with an assumed high or diagnose DMA from this attempt.

The host runner has one definite reporting defect: caught failures still produce
exit status zero. Its JSON correctly reports failure/non-invocation. The runner
also adds an early READY gate absent from the original passing procedure and
uses an unobserved fixed sender-start delay. These limits need attention before
reusing the procedure; they do not explain the electrical reading by themselves.

## Scope and pinned inputs

Author authorized a files-only review while using Jukebox. No bench connection,
firmware build/deployment, reset, input injection or SD operation occurred.

| Input | Exact identity and evidence |
|---|---|
| Installed EMOS | `9b67182cca4cb51f9fee0473ab32dda1e766e3db`; reviewed retained ELF and matching 128579-byte payload, SHA-256 `812cd23f20b1254e019e5b6d6c33e00eaa30e05603774152b609b8ef83c154a4` |
| MOS builder | `90034c2348761c42bab4217ce5b0f906922dc0e4`; compatibility contract and compiled startup |
| Historical receiver/sender | Legacy commit `4626fcc41a0da5811a4374175fe803957ec5ab4f`; receiver source and sender wire assembly byte-identical to that commit |
| P4 SDK | ESP-IDF v5.5.5, `b774170ff46c393eeb5e495ea37936038d3f4f4f`; GPIO driver/HAL and PARLIO RX initialization |
| Harness | [Original profile](../../../hardware/designs/light2-harness-r01/profile.yaml): PD4/header13 ↔ GPIO20/EXT2-13; READY_N 10 kΩ pull-up |
| Current execution | Local control-bias-r01 run result: `invoked=false`, no records, GPIO20 read zero before reset/arm |

Official [GPIO documentation](../../../../../agon-docs/docs/GPIO.md) was consulted
first. Relevant EMOS source at the pinned revision: `src/uart.c`,
`src_startup/init_params_f92.asm`, `src/emos_parallel.c`,
`src/emos_parallel_io.asm`. Current EMOS HEAD is not the installed baseline.
The SDK detail is in `components/esp_driver_gpio/src/gpio.c`,
`components/hal/esp32p4/include/hal/gpio_ll.h` and
`components/esp_driver_parlio/src/parlio_rx.c`.

## Findings

| ID | Finding | Implication |
|---|---|---|
| RS01 | Compiled `init_UART0` writes PD_DR=FF, PD_DDR=FF, PD_ALT1=00, PD_ALT2=00. UART0 activation changes only PD0–PD3. UART1 uses Port C. | Normal initialization leaves PD4 as GPIO input; the installed UART code does not intentionally drive READY low. This is static evidence, not a live register dump. |
| RS02 | Compiled P4 `configure_ready` selects mask 0x00100000, mode7 (`INPUT_OUTPUT_OD`), no internal pulls, then sets GPIO20 to one. `print_status` passes20 to `gpio_get_level`, which reads input bit20. | No pin-number typo, disabled READY input, reversed release polarity or output-latch substitution was found. |
| RS03 | Before USB `a`, the receiver executes only READY initialization and its USB command loop. PARLIO allocation/configuration and DMA receive begin inside `receive_one_record`, reached by `a`. | PARLIO and DMA had not been started when the failing precheck read zero. Their payload behavior cannot explain that particular run stage. |
| RS04 | Historical sender initialization and transfer explicitly keep PD4 input and clear its alternate functions; CLOCK/VALID alone become outputs. Assembly is unchanged. | Sender code has no deliberate READY output drive. The current attempt never executed it, so sender correctness is not live evidence for this attempt. |
| RS05 | The newest runner requires READY high before resetting Agon. The August passing runner instead began after the operator started the sender, with no initial status gate. Passing logs show READY high after completed records. | The new gate examines a different phase. Its failure cannot establish failure of the original transfer procedure. Expected idle electrical high remains reasonable; blindly bypassing this observation is not justified. |
| RS06 | `state=released` is constant diagnostic text recording receiver intent. CLOCK/VALID inputs are not enabled until PARLIO setup. | The label is not proof of actual voltage; early zero CLOCK/VALID values are not wiring measurements. READY input, however, is explicitly enabled. |
| RS07 | Runner catches exceptions, writes JSON and falls through without a nonzero process exit. Receiver failures likewise leave process exit zero. | Definite host reporting defect. Shell success must not be treated as test success. Existing JSON/USB evidence correctly shows non-invocation here. No receiver integrity result was hidden or converted into a pass. |
| RS08 | Runner waits17 host seconds after reset rather than observing sender readiness. | It does not prove SD startup, executable entry or completion. This delay was never reached in the latest attempt. A future procedure needs explicit sender preparation evidence or a separately justified admission method. |

The Author measured 10 kΩ from the correctly placed blue READY_N pin to its rail.
The earlier suspected offset is withdrawn. That resistance/path observation does
not measure powered line voltage or prove both processor pads see the same level.
No hypothesis of a broken board, missing wire or bad DMA is promoted by this review.

## Disposition within the existing control task

[DH03/DH04](DEVKIT-HARDWARE-R01.md) remain the owners; no new task or transport
redesign is introduced. Before another comparison, correct the runner's exit
status and readiness evidence in a fresh procedure, preserving the existing run.
If static review remains inconclusive, the smallest physical check is powered
READY-to-common-ground voltage with the receiver deliberately released, reconciled
with pad configuration/readback. Do not request analyzer relocation first.
That is a future bench check, not authorization to interrupt Jukebox now.

Offline evidence under the ignored control-bias-r01 `ready-software-review`
directory contains exact-identity checks, a review-result JSON and disassembly
of the retained P4/EMOS functions. No firmware source, generated image, historical
run or deployment procedure was modified. Current normal startup remains restored.
