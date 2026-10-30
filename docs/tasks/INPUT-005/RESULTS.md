# Application-owned controller extraction — offline results

Moving controller interpretation into one reusable application include recovers
**991 EMOS ROM bytes and 29 static RAM bytes**. The resident controller module
is 45.07% smaller. The mode20 viewer uses that same include, and complete
firmware builds, target application builds and software/instruction checks pass.
Hardware, SD/startup and production selection remain unchanged. A matched
application/EMOS installation and physical review are still required.

Plans were committed/pushed before implementation: Extender `b9c844aa`, EMOS
`379bf34`. Baseline source is EMOS `eebdd76`, following diagnostic extraction.
EMOS implementation is `c5cf7aa`. Exact artifact identities and portable
accounting are in [results.json](results.json).

## Comparable resident costs

Ranked by least free ROM first. Both sides use identical unversioned identity
strings, profiles, toolchain and configuration. Capacity is 131,072 bytes.
Percentage change is `(after − before) / before × 100`.

| Composition | Before ROM, bytes | After ROM, bytes | Recovered, bytes | ROM change | After free, bytes | Static RAM before/after, bytes |
|---|---:|---:|---:|---:|---:|---:|
| Controller | 127,817 | 126,826 | 991 | −0.78% | 4,246 | 4,189 / 4,160 |
| Ordinary | 125,520 | 125,520 | 0 | 0.00% | 5,552 | 4,058 / 4,058 |

Ordinary EMOS is byte-identical to its baseline. The only object-size change
in the controller composition is `emos_controller.o`: 2,199 → 1,208 ROM bytes
and 131 → 102 static RAM bytes. The complete controller composition now costs
1,306 ROM bytes above ordinary EMOS, including its integration hooks.

The remaining 102 resident RAM bytes are the 96-byte reply, three-byte token
counter and three state/timestamp bytes. EMOS retains fixed-endpoint admission,
correlation, expiry, lifecycle cleanup and coherent interrupt-enabled delivery.
It retains no controller flags/axis decoder, source/edge cursor, press counter,
request encoder or source-age/neutralization policy.

The first extraction saved 988 bytes. A measured selective-lock variant saved
another three without removing a guard: OPEN/RECEIVE retain their admission
lock, while SEND unlocks for its stack-owned request copy. The final complete
link confirms the same three-byte saving; resident RAM is unchanged between
these variants. This is a measured practical reduction, not a proof of a global
minimum.

The preceding diagnostic extraction recovered 2,947 ROM bytes. Together these
two changes recover 3,938 bytes against the comparable unversioned controller
baseline. The installed named v0.1.27 has longer identity strings and remains
130,802 bytes / 270 free; string-length differences are excluded from savings.
No unversioned image is a deployment candidate.

## Application cost and reuse

1. The maintained public file is `include/agon/controller.hpp`; its
   [application guide](../../controller-api.md) owns usage. It contains default
   AgonDev MOS bindings, named normalized controls, native sticks/triggers,
   optional eight-bit conversion, source/age/validity and retained press counts.
   Applications supply gameplay mapping/calibration policy. P4 acquisition
   adapters still own physical device reports; this is not universal USB support.
2. A target-linked minimal consumer is 6,095 file bytes versus 1,110 for the
   same empty application: a 4,985-byte increment including newly linked SDK
   helpers and the probe's state observation. Static RAM rises 285 bytes,
   comprising the 282-byte client and three-byte observation variable. This
   is a bounded example, not an invariant library cost for every application.
   Both sides use the same toolchain/SDK/options. No allocation is performed by
   the controller include; stack high-water usage is not measured here.
3. The complete mode20 live/replay viewer is 32,267 file bytes, including UI,
   font and mode lifecycle. Its renderer/pacing and entry-mode restoration
   remain separate from reusable input handling. Compilation is not physical
   execution or a display/latency pass.
4. Review found and corrected a stale-input window after a bounded blocking
   SEND or healthy lease-renewal close. The client now ages state again after
   those calls. Model clock advances reproduce the old failure and verify
   neutralization with source/press history retained after correction.

## Compatibility and validation

1. The new application/EMOS gateway uses operations 4–7: token OPEN, one-shot
   raw RECEIVE, fixed-envelope SEND and local CLOSE. RECEIVE is 98 bytes: the
   untouched 96-byte CIS2 response plus two raw timing bytes. P4's CI2/CIS2
   physical UART bytes remain unchanged. Old/new applications and EMOS must
   not be mixed; incompatible operations fail clearly. No checksum, MOSlet,
   application UART/GPIO access or SD-lease borrowing was added.
2. Both complete EMOS profiles pass maintained wrappers and every mandatory
   link guard. The accountant reconciles binary, ELF sections, maps and object
   totals. Verification covers 117 maintained/prepared firmware inputs; eleven
   unchanged pinned AgonDev adaptations match the prior prepared baseline.
   Source archives, patches, build provenance and exact bytes remain in local
   evidence. The viewer builder also checks canonical wire copies and MOS slots.
3. All 145 EMOS host tests and 43 controller host tests pass. The actual portable
   P4 receiver/peer, resident endpoint and public client execute together with
   hardware boundaries replaced. The standalone client checks malformed-tail
   rejection before ACK, short taps, duplicates, source changes, clock wrap,
   stale neutralization, delayed sends, failure cleanup and healthy renewal.
4. Final linked eZ80 checks pass: controller admission/correlation/one-shot
   delivery/expiry/cleanup and Escape, 298 diagnostic gateway cases and 21 UART
   reservation cases. Every one of 96 raw output stores occurs with interrupts
   enabled. Ordinary RECEIVE executes 1,510 modeled instructions; its longest
   masked interval is 86. The fresh-reply/Escape case executes 2,031 instructions
   with a 519-instruction maximum masked interval including actual IRQ parsing.
   It delivers Escape without FIFO overrun/fault and preserves SP/IX/IFF.
   These synthetic scheduling counts are not calibrated physical timing.
5. The controller renderer regression and AgonDev viewer build pass. Native
   sanitizer checks run outside the sandbox's ptrace limitation. No emulator
   profile, firmware snapshot, SD mapping or hardware test was changed/launched.
6. The repository-wide version-record validator reports an unrelated existing
   connectivity-hash mismatch in `hardware/designs/light2-harness-r02/profile.yaml`.
   Both that profile and its connectivity file match published HEAD exactly.
   This task changes neither frozen harness record; the failure is retained in
   the metrics rather than presented as a controller regression or repaired here.

The [old gateway contract](CONTROLLER-GATEWAY-V1.md) is preserved byte-for-byte;
its relative links retain their historical `docs/protocols` origin. Current
instructions are the [transport contract](../../protocols/controller-emos.md)
and public application guide. Fsim owns its own consumer migration: use the
new include with the matched EMOS endpoint, preserving its renderer dependency.
P4 keyboard/controller coexistence remains the separate INPUT-004 task.

The offline implementation tranche is complete. Deployment/version selection,
physical handling/coexistence, latency and Author acceptance/promotion remain
explicitly pending; no existing acceptance scope is broadened.
