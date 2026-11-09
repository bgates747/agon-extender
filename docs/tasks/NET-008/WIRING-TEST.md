# ESP8266 wiring test and Author-held bench

Smith reports the new wiring complete, requests an Extender reservation held
until he explicitly requests release, and then directs Extender to use an
existing test plan or devise and execute one. This plan selects a bounded
physical wiring/AT test, not a new Wi-Fi configuration, Internet session or
complete application bridge acceptance. The dedicated scheduler still grants
and manages central custody; Extender operates only after its actual handoff.

## Hold and preparation

1. Reserve NET-008 for linux-extender through the central FIFO and notify the
   dedicated scheduler. Preserve any active predecessor. Smith's explicit hold
   remains after the tests; no automatic release on completion or idle time.
2. Keep the exact standard a25f EMOS, dc43 mainboard VDP and normal startup.
   Preserve the existing P4 image/provenance and rollback bytes. Inspect the
   current firmware's supported UART2 access before selecting a test adapter.
3. If no adapter exists, prepare the smallest isolated P4 development diagnostic
   for UART2 TX47/RX48 at1152008N1, preserving the other harness pins and3.3V
   LDO4 bank. It must remain stopped after reset/boot and start only by an
   explicit admitted CLI invocation. For this P4-only appliance, reuse the
   maintained USB-minimal diagnostic's USB Serial/JTAG `STATUS`/`START` console
   model: no eZ80 appliance runs, so no MOS LOAD/RUN is involved. Boot merely
   prepares safe input pins and supply, never sends a modem command. Freeze exact source/configuration/build
   and command/rollback before deployment; no bare test autoexec or mainboard
   firmware replacement. Compiler work uses the separate Pi FIFO.

## Finite tests

1. Record the real modem's incoming bytes without changing its stored settings.
   Drain only bounded startup noise into a retained transcript, not an infinite
   wait. Keep the network disconnected unless already associated; do not alter
   credentials, saved Wi-Fi mode, baud, reset settings or flash.
2. Explicitly invoke one bounded AT sequence over the new wires: `AT` and
   `AT+GMR`, each CRLF-terminated, with finite response bounds and exact raw
   transcript. Require a complete positive terminal response and nonempty
   firmware identity. First unexpected fault stops the sequence; do not run
   broad baud scans, reset the modem or repeat unknown commands automatically.
3. After those pass, issue a small finite repeated `AT` check to verify stable
   byte framing. Separate parser/terminal errors from timeout/no-byte symptoms.
   Record baud, GPIOs, elapsed time and per-command response independently.
4. Stop/retire the UART2 diagnostic and join every owned reader/process. Restore
   exact incoming P4 application if a temporary image was required, with an
   independent write check and normal startup/input admission. Verify ordinary
   Extender key input and an existing checked SD read/EXIT path. Leave the card
   mounted. Preserve original display route/modes and normal CLI.
5. Record result and limitations. AT response proves finite serial communication
   with the real modem, not supply-current margin, Wi-Fi performance, EMOS
   bridge functionality or long-soak reliability. Leave the bench held for
   Smith after normal cleanup; release only on his explicit later instruction.

## Current preparation state

Wiring is Author-reported; RX48 is orange. No adapter existed at initial
inspection. The isolated source is now `vdp/fixtures/esp8266_uart/`, built only
by `scripts/build_modem_probe.py`; `scripts/run_modem_probe.py` asserts the actual
lease, verifies stopped identity with STATUS, submits START once, retains raw
bytes and validates all five commands and retirement. It never flashes, resets
or releases custody. Each command has a2s bound, GMR3s; the host uses8s readiness
and25s after explicit START. Source/validator checks precede native compilation.
The identified P4-PC build now passes with the pinned ESP-IDF5.5.5 source and
documented Pi-native compiler/Python environment. Installation, invocation and
restoration evidence remain pending; compilation is not a runtime pass.

## Preparation result and current stop boundary

1. Source commit `5e2540ad9a70c4fc303694aaff6b3e834d2a5b05`, build
   `net008-uart2-probe-b2026-11-09-19-40-46Z`,199584-byte application SHA256
   `20469b02247e08dee4bbecf8a1ec412285b8a82d67ea0f8e1f5137766fcaae73`.
   Normal application offset0x20000; generated partition bytes equal the
   retained installed layout. No bootloader/partition/NVS update is selected.
2. One valid transcript and eight negative validator controls pass: missing or
   duplicate results, wrong GPIO/command, UART error, absent retirement, false
   OK and missing modem identity are refused. The final native build takes
   44.044 host seconds; its real parent wait0 and empty owned process groups
   are retained. Compiler custody was normally released and its successor
   notified. Initial stale-host-environment and strict-indentation failures
   were corrected before this clean identified build; no device was involved.
3. Exact incoming P4 rollback is locally retained:1760160 bytes SHA256
   `d9bcb1a2b277e4dcec808d46a33d53879ea4ac4f3e35d69f80345d3c9ac4043e`,
   build `net-003-r02-b2026-11-06-09-03-07Z`. Retained bytes are rehashed, not
   downloaded again from the unchanged device. Selective application install
   and independent readback must preserve sector tails and unrelated storage.
4. The dedicated manager has reserved the Author-requested hold, but actual
   fresh admission/grant is blocked by automatic review: the reviewer rejected
   the pregrant CLI/read/EXIT checks because no lease had yet been granted,
   while the current grant protocol requires that fresh physical evidence.
   This is an unresolved admission boundary, not a test failure or hardware
   observation. Do not fabricate fresh evidence, grant from an old receipt,
   switch operator/transport to evade the rejection or access the target.
5. No firmware has been installed, no modem command sent and no electrical or
   AT pass claimed. The queued hold remains for Smith; actual manager approval
   resolution and genuine handoff precede all physical work. Continue with this
   prepared test after that boundary is resolved, then retain custody until
   Smith explicitly requests release.

## Author correction: grant before hardware checks

Smith explicitly supersedes the circular admission sequence: exclusive bench
custody must be granted before the operator checks physical readiness. The
dedicated Olimex scheduler owns correction of the canonical scheduling guide,
its enforcing helper and affected current operating references. The original
denied pregrant probe remains historical and must not be retried as such.

The corrected sequence must establish FIFO custody through host-only registry
and predecessor-handback reconciliation, perform actual readiness checks under
that lease, and permit the selected wiring test only after readiness succeeds.
A grant establishes ownership, not a hardware-ready claim. Unknown occupancy
still requires reconciliation; failed readiness retains exclusive custody.
No fabricated observation, alternate registry or restamped historical receipt
is part of this correction. The existing hold and test scope remain unchanged.

The owner correction has been requested; implementation, device-free validation
and actual grant/admission are still pending. Extender has not accessed hardware.
