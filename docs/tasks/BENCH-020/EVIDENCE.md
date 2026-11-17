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
