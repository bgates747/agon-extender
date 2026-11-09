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
Exact compiled-image/installation/invocation/restoration evidence remains pending
in the ignored NET-008 operating record; source existence is not a runtime pass.
