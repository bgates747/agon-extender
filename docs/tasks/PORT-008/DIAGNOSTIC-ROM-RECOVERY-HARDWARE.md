# Diagnostic ROM recovery — hardware qualification

State: passed, 2026-10-09. The Author authorized the bench and explicitly waived
backups of installed firmware. The ordinary EMOS candidate and all three
MOSlets are installed. The unfinished private parallel composition was not flashed.

| Physical check | Outcome | Coverage |
|---|---|---|
| EMOS installation | Pass | Full 128 KiB readback equals candidate padded with FF; fresh boot/input |
| UARTTEST / VDPPOLL / UARTFLOW `--version` | 3 pass | Real SD loading/dispatch; zero return, keyboard lease retained |
| Extra arguments | 3 pass | Nonzero return; no diagnostic lease acquired |
| Keyboard-owned UART | 3 pass | Nonzero refusal; keyboard lease/RTS preserved |
| UARTTEST / UARTFLOW against ordinary P4 | 2 pass | Expected nonzero; diagnostic UART and RTS released |
| VDPPOLL against ordinary P4 | Pass | Exact `17 00 80 A5` request / `80 01 A5` reply at 1152000 baud |
| UARTTEST against dedicated P4 peer | Pass | Exact 18-byte request / 5-byte ACK at 115200 baud, no flow control; both ends report pass |
| UARTFLOW against retained matched P4 peer | Pass | Request/reply, CTS/RTS blocking and cancellation; both ends report pass |
| Final restoration | Pass | Original 38-byte startup, ordinary P4 r13, idle MOS prompt, input ready/neutral, listener offline |

These are correctness/cleanup checks, not throughput measurements. Negative
bench checks establish nonzero returns; exact 15/19 codes remain covered by
the retained off-bench executable tests. Each RAM snapshot checks the new
candidate's diagnostic-active and RTS ownership symbols. While keyboard input
owns UART1, RTS remaining owned is correct; after a diagnostic closes, both
owners and UART-open flags are clear. Input reacquired without resetting after
the combined refusal/failure batch.

## Installed and restored identities

EMOS: `agon-emos-v0.1.24-b2026-10-09-16-28-01Z`, 128739 bytes, SHA-256
`bbae7be825927827f1d8af622dfdd11e2e87986eabd76a98a5a63a7c70491365`.
The verified complete ROM hash is
`f5f4495dea2d50b7cd5c516cc8675790d55cc98c773f3c25c55b8b176bf9a9df`.
Ordinary EMOS retains 2333 free ROM bytes; the unflashed private candidate
retains 1748. The extraction recovers 1938 bytes.

The exact ordinary P4 `rgb-001-r13-b2026-10-09-05-23-43Z` application was
restored and independently flash-verified after each dedicated peer run:
`a38d3f39602ec52860b89fdd6954d4764a0fbf95def60ba5b646c40ab6ba3c02`.
Only app0 at 0x20000 was written; bootloader, partitions and OTA selection
were not written. Mainboard Pingo VDP was untouched. No previous-firmware
backup was taken. Newly installed EMOS readback is verification evidence.

Utilities reside at `/emos/uarttest.bin`, `/emos/vdppoll.bin` and
`/emos/uartflow.bin`; candidate and verification batch at `/extender/install`;
Agon RAM/ROM evidence at `/agents/extender/results/dr-*`; startup preservation
at `/agents/extender/backups/startup/dr-*`. The exact original startup is restored
and its closed root transaction siblings are cleaned. Unknown files are untouched.
[Machine-readable evidence](DIAGNOSTIC-ROM-RECOVERY-HARDWARE.json) records hashes
and retained local paths. Production selection/tagging remains unchanged pending
Author review; this is not ExExt activation or parallel hardware qualification.

## Setup corrections and limits

The first listener commands did not enter the service; a reset to a verified
prompt resolved entry. A pre-existing completed startup transaction was archived
before cleanup. Fresh file-service sessions and acknowledgement settling were
required between clients/ownership changes. P4 HTTP readiness must be awaited
after app restoration before the reset helper requests pre-reset status.
These are setup corrections, not diagnostic failures.

The ordinary P4 already implements General Poll; it is a successful VDPPOLL
peer, not a negative control. The initial collector wrongly expected failure
and also expected keyboard-owned RTS to be free. Corrected expectations reuse
the original saved results; firmware was not changed to make the checks pass.
A separate compiled poll peer was not deployed or counted as hardware evidence.

UARTFLOW's retained run records total elapsed and finite peer-capture durations
in host monotonic seconds. UARTTEST's later collection duration is recorded
separately; complete installation and UARTTEST preparation/runtime timing were
not measured. No calibrated physical waveform capture was performed. Reset /
live UART drain / parallel direction and coordinator qualification remain open
in the parent task.
