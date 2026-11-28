# Olimex serial transfer audit findings

Ordinary Agon Flash installs a 1.1 MB application on the mainboard in about
19 seconds, then the bench runner spends another 104 seconds sending the
written bytes back to the Pi over the mainboard USB serial port. A candidate
and production restore incur about 207 seconds of application readback
alone. The readback gives independent written-image proof, but that proof
does not require a second copy of the firmware on the Pi.

The least invasive change is to retain the current board, partition and
slot checks and have the ESP32 return a digest of the exact written range.
That removes the large transfer and retains the independent check for
accidental corruption. It still enters the unreliable USB ROM handshake.
Eliminating routine ROM entry requires a separate small verification
interface in the running VDP or its updater. The stock updater cannot
provide that proof today.

## What the bench should move

| Operation | Current payload and reason | Audit disposition |
| --- | --- | --- |
| After a stock VDP FLASH write | Mainboard ESP32 → Pi over USB serial at 115,200. Table and selector are 12,288 B. App is the exact newly written image, 1,117,392 B for v0.1.4-alpha. Today the Pi needs the app bytes solely to compare them with its local copy. | Replace the routine app read with an on-device range digest. Keep the board, layout, slot and fresh MOS proof. Retain full reads for a specific diagnostic, a qualification comparison, or preservation of bytes otherwise unavailable. |
| Prepare a mainboard firmware test | Pi → P4 over HTTP, P4 → Agon SD over UART. Sends the new candidate and actual fixture inputs. The standard v0.1.4-alpha and prior v0.1.3-alpha rollback already have verified SD copies. | Keep the first upload of test inputs. Use FLASH's CRC calculated on the Agon before confirmation. Avoid separate candidate SD payload GETs. Existing standard-image receipts plus file metadata and the FLASH CRC are enough for reuse. |
| First deployment of an SD standard | Upload the missing standard, read it back once and compare the actual bytes. Same standard later used as rollback retains its original receipt. | Keep the one deployment comparison. Publish the receipt as current card state. A replaced card, lost file or credible corruption is reason to reopen the affected proof. Routine presence checks use metadata. |
| Agon Flash writes a mainboard app | eZ80 → mainboard ESP32 over onboard UART, from the file already on the Agon SD. Approximately 1.1 MB per actual new app write. | Keep. This is the firmware delivery into the target. A restored production file can bypass Pi-side staging and still needs this write when the current app differs. |
| Retrieve original fixture results | Agon SD → P4 over UART, then P4 → Pi over HTTP. Named outputs contain work the Pi does not have. MOS state, marker and receipt do not reproduce a report. | Keep the smallest original reports required by the job. Collect once. Use explicit deferred or offboard collection for large batches when selected. Use a small command-correlated serial result directly when the fixture offers all required evidence there. |
| Preserve startup and check resident bench tools | Every standard UART listener startup rereads 45 B of startup and 26,127 B of the listener. Every mainboard install/restore additionally rereads the 15,624 B FLASH utility. A successful one-arm FLASH job opens four such listener sessions and returns **135,936 B** of these unchanged files. | Keep the startup safety check at the boundaries that rely on it. Reuse existing verified identities for resident tool files across phases. Use a controlled local digest or an existing unchanged-file receipt when exact tool identity is material. A banner or size alone cannot establish exact identity. |
| Verify an EMOS update | Stock FLASH reads back the eZ80 ROM locally for a CRC. The shared runner also saves and downloads the installed 131,072 B ROM. The older direct installer adds a full download of the staged ROM before writing. | Remove the older staged-input reverse copy. Evaluate a command-correlated FLASH ROM CRC receipt, or an exact-range target digest if required, before replacing the installed ROM download. Keep the 128 KiB ROM upload when actually programming EMOS. |
| Verify a P4 application write | P4 USB programming has an esptool digest check for the eligible stock write. The maintained P4 phase then independently downloads the entire padded application, 1,769,472 B for the selected runtime. | Audit exact pin, slot and writer digest extent, then avoid a redundant second full read for ordinary writes. Keep fuller qualification for an unknown layout or uncertain write. The P4 and mainboard programmer ports are separate. |
| Retain full backup or diagnostic evidence | Reads include full applications, NVS/store ranges, ROM traces and failed transfer recovery captures. Some are only in separately commissioned packets. | Keep the one copy needed for a real backup, evidence export or instrumented comparison. Check exact range. Use metadata or an on-target digest for an erased/unchanged assertion when its mechanism can provide equivalent proof. |
| Console output, reset, keyboard and leases | Bounded text or binary diagnostic records, command responses and reset signaling. P4 HTTP and Pi service polling are control paths. | Keep the proof needed for that request. These operations do not justify copying any firmware or fixture file. Keep native capture when it is the evidence under test. |

The following saved receipts show where that time goes. The UART file
benchmark used identical inputs for the two clients. Its timings include
host setup and client bookkeeping. The VDPL-054 USB row covers the app-read
portions of two operations. The rows are ordered by observed elapsed time.

| Saved run and operation | Bytes | Elapsed |
| --- | ---: | ---: |
| Matched historical direct UART benchmark, one SD upload | 1,100,000 | 281.1 s |
| Matched historical direct UART benchmark, one SD download | 1,100,000 | 277.0 s |
| VDPL-054 candidate plus production full USB app reads | 2,235,680 | ~207.3 s |
| Matched P4-staged UART benchmark, one SD download | 1,100,000 | 49.3 s |
| Matched P4-staged UART benchmark, one SD upload | 1,100,000 | 45.0 s |
| VDPL-054 candidate plus production onboard FLASH writes | 2,235,680 | 37.9 s |

[FLASH timing and evidence paths](ONBOARD-UART.md#retained-measurements) ·
[Matched SD benchmark](../REMOTE-009/UART-THROUGHPUT-INVESTIGATION.md#current-bench-measurement--november-27)

## Why USB reliability matters even after reducing bytes

The retained programmer records show two distinct failures. A missing ROM
SYNC reply stops before the ESP32 sends flash data. A short flash-read
packet occurs after the connection has worked. In the earlier matched
diagnostic, a full 115,200-baud read succeeded, while a later attempt at
that same baud failed before flash access. These observations neither
diagnose the cable nor establish a unique esptool-version fault.
[USB investigation](../BENCH-023.md)

A digest removes the long read, its data frames, and the risk of that
particular short-read failure. It still needs the initial SYNC. An automatic
full read after a bad digest or missing reply would add back the delay and
could obscure the actual fault. Stop at the first fault and keep the phase
and last acknowledged operation. Treat an updater that reported success
followed by a failed verification as a verification failure with write
outcome pending, rather than repeating FLASH.

## Recommended order

1. **Routine post-FLASH USB proof.** Keep MAC, table, selected slot, exact
   range, and post-programmer MOS proof. Use the installed esptool's
   range-MD5 command. Add a receipt method for the target-computed result
   and keep the release SHA-256 pin, without claiming the host received a
   raw copy. Review every consumer that currently requires
   `readback.bin` or the old full-extent receipt. Qualify range, wrong
   slot, wrong digest, communication stop, restart, and normal handback.
   Compare the digest with one retained raw read during a bounded
   qualification. Make any later full read an explicit diagnostic.
   [Espressif serial protocol](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/serial-protocol.html)
2. **Remove repeated SD tool reads.** Carry the one-time tool/file evidence
   between phases with known state and keep the small startup proof
   where it matters. Verify a change using narrow metadata or an on-device
   digest, as appropriate. Align older direct installers and documentation
   with the same rule. Preserve an explicit route for an unverified SD
   card or replaced file.
3. **Modernize EMOS and P4 verification.** Reuse the actual post-write proof
   already available on each transport when it covers the required extent.
   Qualify the different receipt contracts before replacing full reads.
   P4's writer-local digest and the eZ80's FLASH CRC attest different
   devices, algorithms and data ranges. Routine writes still use explicit
   application/ROM scope and restored boot proof.
4. **Remove routine mainboard ROM entry once a stock-compatible route is
   approved and qualified.** The prototype verified OTA receiver already
   computed a SHA-256 over the exact written extent. Production adoption
   needs a maintained interface and compatible firmware, with actual
   selected/running slot and fresh boot evidence. Preserve the existing
   USB diagnostic path for cases that need it. [Verified OTA prototype](../BENCH-024.md)
5. **Tighten discovery and commissioning.** Update stale PARLIO/legacy
   instructions, preserve frozen evidence, and apply current-policy
   admission to direct helper users that bypass the command-line check.
   Name each future large transfer and its specific purpose in its packet.
   Keep physical staging, file verification, execution, report collection
   and handback independently usable.

## Evidence and coverage

- [SD UART transfer ledger](SD-UART.md) for file staging, reports, resident
  tools and exception paths.
- [USB serial transfer ledger](USB-SERIAL.md) for both programmer ports,
  serial observations, backups, recovery scripts and digest options.
- [Onboard Agon UART ledger and measured VDPL-054 timings](ONBOARD-UART.md).
- [Per-file coverage and commissioned caller inventory](COVERAGE.md).

The audit used existing files on the Pi and retained hardware receipts.
No target, serial port, file on the card, or bench lease was changed.
