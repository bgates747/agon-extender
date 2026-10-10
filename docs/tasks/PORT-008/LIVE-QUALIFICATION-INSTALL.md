# PORT-008 LC03-B — Paired installation and boot recovery

The private P4/EMOS pair is installed and verified. Correcting P4's GPIO input
setup restored the required physical release handshake and Extender keyboard
admission. Complete EMOS ROM readback matches; original startup is restored,
input is ready/neutral and the listener is offline. No parallel payload ran.
LC03-B's block tests and F03 remain open; production is unchanged.
[Receipt](LIVE-QUALIFICATION-INSTALL.json) retains both attempts and hashes;
device addresses and exact local commands remain in ignored bench records.

| Check | Result |
|---|---|
| Corrected private P4/browser build | Passed; source frozen/unchanged; 376.61 host seconds |
| Private build identity controls | 14 tests pass; both private flags and restricted probe lineage required |
| P4 installation | Bootloader, application, partition table and initial OTA metadata independently verified |
| Physical boot release | Passed after one Agon reset with corrected P4; console banner and input admission observed |
| EMOS installation | Complete 131072-byte ROM equals the 130984-byte candidate padded with `FF` |
| Diagnostic MOSlet | `/emos/parprobe.bin` independently read back; exact retained 10750-byte build |
| Original startup | Original 38 bytes restored/read back; resolved temporary transaction siblings removed |
| Final input/service state | Keyboard ready, neutral, held0/pending0; listener offline/no pending request |
| Real parallel blocks | Not invoked; first/last-byte alignment and physical turnaround remain unproved |

Installed P4: `port-008-probe-r04-b2026-10-09-23-44-55Z`, application SHA256
`8f6a5f8084d38dcb61b5677be8057200b8710d5a07e083153f4f5d0d6c8fcff8`.
Installed EMOS: `agon-emos-v0.1.24-b2026-10-09-20-35-19Z`, complete ROM SHA256
`da4ac8ee514a4c07f3544a45c3fbdab7cf78f5682c51117f2cb656d0819690ff`.
EMOS bytes are unchanged from LC03-A. The mainboard Pingo VDP was not changed;
no new prior-firmware backup was taken under the Author's standing waiver.

## Confirmed GPIO defect and test correction

1. P4's boot adapter enabled input before calling `gpio_reset_pin()`. Pinned
   ESP-IDF5.5.5 (`b774170ff46c393eeb5e495ea37936038d3f4f4f`),
   `components/esp_driver_gpio/src/gpio.c:462`, explicitly disables both input
   and output during that reset. Its public GPIO header documents that reads
   return zero while input is disabled. CLOCK/VALID therefore could not be read
   correctly, preventing the release protocol from completing.
2. The SDK mock incorrectly modeled reset as input mode. Correcting the mock
   reproduces the old boot failure (`assert(x.live())`). The
   [boot adapter](../../../vdp/video/extender/transport/p4_boot_release.cpp)
   now retains the initial input fence to remove stale output, resets the mux,
   then enables input again. No pin map, wire protocol, release requirement,
   EMOS ownership or timed fallback changed.
3. With the corrected SDK model and product fix, sanitized tests pass:
   732 boot cases, 82 paired native base cases /111 private total,
   264 coordinator cases and 151 payload cases. Full P4 build validation passes.
   The corrected physical image also restores the retained FS/LS-only keyboard
   setting omitted from r01 and adds private USB boot-state observations.
   Physical recovery is evidence for that complete corrected composition,
   rather than an isolated hardware A/B comparison of each build difference.

## First attempt and recovery

P4 r01 was flash-verified but its UART owner never reached the post-release
console banner. HTTP remained healthy while keyboard readiness was false and
the SD listener was offline. After one Agon reset, the Author saw a MOS prompt
and autoexec line2 reporting “EMOS dispatcher busy.” That generic result also
represents UART/input admission refusal; it did not establish a stuck dispatcher.
This informative failure and its original artifact hashes remain in the receipt.

The temporary startup selected Extender input, saved the complete ROM under
`/agents/extender/results/p8q-rom.bin` and started the listener. After corrected
boot and exact ROM verification, the host resolved the known original startup
backup using the listener's documented recovery operation, restored/read back
the original startup, then resolved the verified temporary backup. The retained
original and temporary hashes were checked before either cleanup. Unknown user
files were untouched. The installation helpers are one-shot evidence, not a
general replayable deployment recipe.

The bench is idle at the MOS CLI with admitted input; no collector, flash,
transfer or test remains active. The private browser-output image is a
qualification composition, not a production or HDMI promotion. Pause for Author
review before invoking the existing 20-case two-way MOSlet. Reset/fault recovery,
payload timing and electrical release still require separate evidence.
