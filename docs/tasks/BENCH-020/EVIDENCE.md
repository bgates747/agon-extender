# BENCH-020 owner evidence

Extender’s most recent applicable E/VDP example uses the esptool 5.1.0 stock
CLI on the P4-PC. The EMOS owner example uses ordinary MOS FLASH and proves
the complete ROM separately. The failed rehearsal made choices outside those
procedures. The operator packet will link the checked implementations of the
selected commands.

| Operation | Most relevant completed evidence | Boundary |
| --- | --- | --- |
| E/VDP P4-PC app0 replacement and restore | Extender's NET-009 actual183 held the mainboard in USB RTS/Q4 reset, read the table at `0x8000` and the selector at `0xf000`, used esptool 5.1.0 at 460,800 baud with `keep` for flash mode, frequency and size, wrote at `0x20000`, and independently compared the affected sectors. The restored P4 published its pad-release marker while Agon was held. Releasing Agon led to proven CLI/read/EXIT and a clean scheduler return. | This is the commissioned P4-PC application layout and stock programmer path. The Net-009 application extent and Ethernet workload are specific to that job. BENCH-019 r01 independently exercised the larger pinned 1,761,280-byte write on the same P4 layout. |
| EMOS install and startup | Extender's EMOS-001 corrected installation used one FLASH at a proved Legacy prompt. MOS completed programming and rebooted into admitted Extender input. Extender saved and retrieved all 131,072 newly written ROM bytes and verified startup and listener separately. | This establishes the regular updater and full-ROM readback. The original EMOS-001 recovery image and temporary card procedure were case-specific. BENCH-019 r01 exercised both candidate and current production ROMs on the three-processor tuple. |
| Mainboard VDPlet app0 | BENCH-019 r01 restored the release application with esptool 4.12.0 and full app0 readback at `0x10000`, then used the commissioned Agon USB restart. BENCH-019 r02's joined retry proved the pinned candidate with the same 4.12.0 stub held across the operation and the same successful post-readback restart. | Select the matching classic ESP32 route and exact write extent. The successful r02 mainboard result does not qualify the same Python adapter on P4. |
| Verified SD staging and fixture boundaries | BENCH-019 r02 stage passed with exact readbacks and listener EXIT. BENCH-019 r01 captured a real Legacy prompt, explicit LOAD and RUN, both guest assertions and both P4 values, then collected the log. | Preserve the successful result and both original stop records. The r01 observer recognized only a root or bare prompt after intervention. |

[NET-009 task](../NET-009/P4-PEER-R01.md) ·
[NET-009 install command](../../../agents/net009/p4-peer-r01/actual183-joined-console/install-write-argv.json) ·
[NET-009 handback](../../../agents/net009/p4-peer-r01/actual183-joined-console/handback.json) ·
[EMOS owner install](../EMOS-001/FLASH-R01.md#corrected-installation-completed--2026-11-04) ·
[First cold run](../BENCH-019/REHEARSAL-R01-RESULT.md) ·
[Second cold run](../BENCH-019/REHEARSAL-R02-RESULT.md)

### Worked owner examples

1. **Extender VDP, NET-009 actual183.** The operator held Agon reset. The
   following stock esptool forms show the recorded P4 commands, with the
   job-specific arguments named. Each read and write ran separately.

   ```bash
   python -m esptool --chip esp32p4 --port PORT --baud 460800 --before usb-reset --after no-reset read-flash 0x8000 0x1000 TABLE
   python -m esptool --chip esp32p4 --port PORT --baud 460800 --before no-reset --after no-reset read-flash 0xf000 0x2000 SELECTOR
   python -m esptool --chip esp32p4 --port PORT --baud 460800 --before no-reset --after no-reset write-flash --flash-mode keep --flash-freq keep --flash-size keep 0x20000 IMAGE
   python -m esptool --chip esp32p4 --port PORT --baud 460800 --before no-reset --after no-reset read-flash 0x20000 EXTENT READBACK
   cmp IMAGE READBACK
   ```

   The operator verified the table and app0 selector before writing. The
   operator then restarted the P4 while Agon remained held, observed the
   pad-release marker and released Agon. A fresh listener, read and EXIT
   established a working CLI. The curated runtime implements these commands.
2. **EMOS, corrected EMOS-001 install.** Extender installed a pinned ROM with
   one `FLASH mos ROM_PATH -f` at the Legacy CLI. After the updater restarted
   and input was admitted, Extender saved the complete ROM with
   `SAVE ROM_READBACK &0 &20000`. Extender opened the foreground SD listener,
   retrieved the saved ROM, compared all bytes and exited the listener. The
   operator runner uses the same updater, extent and fresh CLI proof with
   staged ROM and readback paths from the job.

## Instruction and execution divergences

1. The ordinary Extender dispatch required OP-10, which sent both fresh
   operators to the shared registry/lease guide. The rehearsal draft itself
   assigned custody through the scheduler's direct chat. Both logs show the
   resulting reconciliation and discovery work. The scheduler's authority,
   current custody and handback must come from one selected workflow for a
   job.
2. Extender `AGENTS.md`, the old firmware procedure and test execution allowed
   release after custom firmware for a working device. The rehearsal required
   all three production images at handback. The operator needs a clear
   instruction for changed components and an owner-published artifact, without
   inheriting a past qualification's backup or full-device write sequence.
3. Extender's draft told operators to inspect a prompt, verify bytes and
   observe completion. r01 reconstructed each route and wrote helpers. The
   r02 phase runner removed that authoring step but substituted a new
   programmer adapter. Its P4 adapter reproduced neither the stock r01
   command nor the latest owner command. Both cold P4 metadata readbacks
   matched byte for byte. The new fatal treatment of an unknown flash size
   stopped r02 before its write call. The r01 log does not expose the raw
   detected size.
4. The machine-local hardware chronology mixed current host binding with
   historical headings. Both operators searched it for live prerequisites
   although the commissioned bindings can be supplied separately. The sparse
   view should expose one compact binding and the supported operator steps.
5. The stop instructions mixed attended and unattended work. The cold goal
   uses Smith's explicit bounded unattended exception. The canonical
   directions need to keep the authority to recover, the actual bench
   ownership and the proof of safe handback visible at the action.

## Second rehearsal disposition

The second operator successfully recovered and checked in on November 17.
The retained attempt stopped before any P4 write or fixture invocation.
Recovery compared all 1,761,280 bytes of the P4 app extent with production
and left the confirmed image in place. It restored the mainboard VDPlet
application, compared all 1,130,496 bytes, retained the untouched EMOS ROM,
proved the MOS CLI and verified idle transfers and free handles. The
recovery was a separate successful return, with the original rehearsal still
failed. The operator needed a separate recovery adapter because the phase
runner correctly refused to advance past the failed install, but offered no
ordinary restore entry at that boundary.

[Operator log](../../../agents/bench019/rehearsal-r02/OPERATOR-LOG.md) ·
[Terminal recovery receipt](../../../agents/bench019/rehearsal-r02/production-recovery/complete.json) ·
[Physical handback](../../../agents/bench019/rehearsal-r02/production-recovery/handback/handback.json)

## Sparse comparison

The full checkout leaves historical recipes available to component owners.
The operator checkout includes one bench guide at the same tracked path as
the full repository, eleven required Python modules, the commissioned local
binding, and the exact artifacts for the selected run. The regular operator
guide, runtime, and test pins come from a frozen revision. The checkout uses
the commissioned host Python environment and copies of the needed production
images. The local entrance points directly to the guide and selected packet.
Refresh the sparse checkout from a subsequent guide/runtime revision before
using it for another packet.

The matched cold test keeps the previous fixture, firmware images, SD
program and result locations, expected results, install order and restore
order. It uses a fresh SD transaction namespace and evidence directory. The
two changes are the single sparse entry and the P4 stock owner sequence.
The P4, EMOS and VDPlet artifact hashes remain identical across attempts.
The rehearsal can establish that the curated end-to-end procedure works.
The retained command and source comparison explains the earlier P4 pre-write
failure independently of the rehearsal outcome.

## First curated run

The GPT-6.1 Sol high operator entered the Pi5 sparse checkout at
`bb487d00`. Every physical phase completed on its first invocation.
The operator performed all three custom writes, ran the fixture once,
collected the four expected output lines and restored all three processors.
The retained phase receipts prove child exit 0 and joined process groups.
An independent SHA-256 comparison matched all six install and restore
readbacks to the job pins. The handback records a working Legacy CLI, idle
services and free serial handles.

| Phase | Duration |
| --- | ---: |
| Verified SD staging | 157.241 s |
| Mainboard VDPlet candidate and restore | 61.867 s and 61.714 s |
| Extender VDP candidate and restore | 55.049 s and 54.920 s |
| EMOS candidate and restore | 62.518 s and 62.316 s |
| Invoke and collect | 14.844 s |
| Final physical handback | 8.143 s |

Wall time from stage supervisor start to completed physical handback was
10m01s, including gaps between commands. The earlier rehearsal's 38m22s
included a Smith hold, human recovery and fixture-observer correction, and
measures from slot-open to scheduler closure.

The first reservation command failed before reaching the scheduler. The Pi
app-server socket is outside the workspace sandbox. The operator then used
the ordinary review path, received the direct reservation and slot-open
messages and completed the bench phases. The guide now names the reviewed
invocation directly. The new cold acceptance run checks that an operator
can complete the reservation and physical qualification without that error.

## Second curated run and startup correction

The second operator reserved on its first reviewed Pi message and staged the
unchanged packet. Its mainboard write and independent full-extent comparison
passed. The Agon-only reset advanced the boot epoch, but input remained
unadmitted at the 60-second deadline. The parent joined the worker with exit 1.
The operator preserved the first fault. Later installs and feature checks
remained unrun.

Under the same slot, one paired P4/Agon startup produced a working CLI
without a firmware write. The operator then wrote and compared only the
production mainboard extent and checked in. The scheduler confirmed release.
P4 and EMOS were unchanged. All original and recovery receipts remain
separate. The failure can occur after a valid flash, so an independent
readback alone cannot qualify startup. The underlying cause of the
intermittent input admission remains unisolated.

The next frozen runtime applies the already working ordered startup after
each mainboard app write. The Pi holds Agon, restarts the installed P4,
waits for its serial pad-release marker, then releases Agon and checks
fresh keyboard admission and an actual MOS CLI exchange. The operator makes
no P4 firmware change during that phase. The fixture bytes, firmware images,
and phase order remain fixed. The guide also names the live output and
terminal receipt paths directly.

## Qualified cold run

The third GPT-6.1 Sol high operator started from the curated Pi5 checkout at
`14e20dd2`. Its initial local entry, guide, and job packet supplied the
operations. It inspected the selected tool source and actual journals, and
used no historic operating guide or locally authored bench helper. The Pi
sender reached the scheduler on its first reviewed call. The operator waited
for the direct slot-open message and used the nine planned phases once each.
No phase failure, retry, or human intervention occurred.

The paired P4/Agon startup worked after both mainboard writes. Independent
comparison matched all six candidate and production readbacks. The fixture
reported EMOS accepted 0 and rejected 19, VDPlet status 0 and value 86, and P4
results 3 → 9 and 5 → 25. The operator left a working Legacy CLI, offline
listener, idle transfers, and free serial handles. All nine parent receipts
showed exit 0 and joined workers. The scheduler confirmed release at
01:16:47 EST on November 17 with an empty FIFO.

| Recorded span | Duration |
| --- | ---: |
| Stage start to completed physical handback | 9m49s |
| SD staging and independent readbacks | 158.833 s |
| Mainboard install and restore | 64.378 s and 64.324 s |
| Extender VDP install and restore | 54.992 s and 55.099 s |
| EMOS install and restore | 62.572 s and 62.429 s |
| Fixture invocation and collection | 14.747 s |
| Final physical handback phase | 8.155 s |

[Verified phase results and digests](../../../agents/bench020/rehearsal-r03-verification.json) ·
[Scheduler release](../../../agents/bench020/rehearsal-r03-release.json)
