# PORT-010 — Prove an acknowledged UART round trip

Status: implementation authorized, in progress. Started: 2026-09-07.

The Author accepted the next chunk: EMOS sends the previously proven 18-byte
message, P4 sends a short acknowledgement, and EMOS verifies it with a bounded
wait. Keep the seated harness, powered reset-button invocation, Enter-to-arm
host prompt and prominent PASS/FAIL output. No flow control, VDU routing,
activation or production protocol is added.

## Implementation decisions and bounded references

1. Official [MOS UART APIs](../../../../agon-docs/docs/mos/API.md), 0x15–0x18,
   say mos_ugetc blocks while UART1 is open. The installed EMOS v0.2.0 source
   confirms this in serial.asm. Its C-function table exposes no nonblocking RX
   call. Do not fake a timeout around a blocking read or patch an application
   to access UART registers. References remain read-only.
2. EMOS will own a small nonblocking read/write helper and an explicit
   `EMOS UARTTEST` diagnostic command, tracked in sibling INTEG-004. The command
   requires Legacy and an unused UART1, opens 115200/8N1 without flow control,
   sends once, checks a reply, closes and reports one clear result. It changes
   no public MOS API or module gateway. A missing/stalled peer or clock must
   terminate; host tests exercise the actual command engine.
3. P4 receives on GPIO22 and transmits on GPIO12 → Agon PC1 over existing r03
   wiring. Only GPIO12 becomes an output. P4 sends `ACK\r\n` only after exact
   receipt of `EMOS UART1 -> P4\r\n`; no retries. Strict matching and error
   handling remain. The reply is a fixture contract, not EDP protocol.
4. The onboard VDP clock increments by two per VBlank (EMOS interrupts.asm).
   Bound waits using observed low-byte clock deltas, with a finite polling
   budget as a separate stalled-clock escape. Do not describe that budget as a
   calibrated duration or assume the clock advances once per millisecond.
5. Author-approved identities: uart-roundtrip-probe-r01 and agon-emos-v0.3.0
   (new backward-compatible command), recorded in registry r26. Review builds
   carry those identities with draft status. The installed, working EMOS remains unchanged during
   implementation. Reuse its proven build and installation procedure when a
   reviewed replacement is ready; no speculative flash or WROOM work.

## Work

1. [x] Implement/test EMOS bounded command and P4 reply composition.
2. [x] Build/check both endpoints and prepare the [test sheet](../../hardware/designs/light2-harness-r03/tests/uart-roundtrip.md)
   and round-trip capture checker. Reuse the existing private launcher
   mechanics when approved identities permit deployment staging.
3. [ ] Obtain required emulator/flash validation for the concrete
   EMOS replacement before deployment. SD is reported mounted locally.
4. [ ] Confirm timeout with the receive-only P4, then run with a reply;
   retain informative failures and passing evidence beside r03's tests.

The forward checkpoint was frozen in Extender e013e42 and EMOS bd08b76.
Machine-specific details remain in HARDWARE.local.md. No push was requested.

## Implementation checkpoint

1. EMOS and P4 draft target builds pass. The complete configured EMOS gate
   passes: 134 generic Python tests, 67 EMOS tests, target compilation/runtime,
   firmware layout, ABI/VDU/baud checks, shell parity and formatter/FatFS gates.
   The EMOS host probe covers 15 scenarios including exact/fragmented replies,
   wrong/extra/incomplete replies, UART failures, TX/RX deadlines, clock wrap,
   stalled clock and an already-open UART. Four new capture tests reject
   misleading acknowledgements; nine existing forward-capture tests and the
   sanitizer-enabled request matcher also pass.
2. A target header omission required three generic UART1 register lvalue
   mappings in mos-agondev (BUILD-002). RBR/THR are port D0, LSR is D5; a target
   compilation test verifies actual IN0/OUT0 instructions. The generic header
   contract includes the same mappings. No upstream checkout was modified.
3. EMOS uses its maintained printf path. The restricted runtime intentionally
   excludes AgonDev puts/putchar; do not broaden that runtime for this probe.
4. The emulated target reports the expected no-peer timeout and returns to
   the prompt. Its CLI must retain open stdin during the wait: upstream exits
   on EOF even if MOS has not finished. A dedicated review script handles this
   and creates a pinned graphical profile. Automated evidence is not Author
   graphical approval and does not prove physical baud or reply receipt.
5. Initial outputs were UNVERSIONED-DO-NOT-DEPLOY/draft. The Author has since
   approved registry r26, EMOS v0.3.0 and uart-roundtrip-probe-r01 for identified
   draft review builds. Graphical acceptance and candidate freeze/rebuild remain
   pending. No SD edit, flash or physical reset
   occurred. The mounted SD still contains the accepted forward test.
6. The no-reply hardware test can use the currently installed receive-only P4
   image before installing the reply image, without disturbing the harness.
   A negative UARTTEST returns MOS's existing FR_TIMEOUT; MOS also displays
   “Volume timeout.” That inherited error wording does not indicate an SD
   failure here; the preceding diagnostic identifies the missing P4 reply.

Scripts: `scripts/prepare_uart_roundtrip.py` builds the P4 bundle and proposed
SD autoexec locally; `scripts/capture_uart_roundtrip.py` checks both P4 request
receipt and exactly one ACK record. EMOS owns `scripts/review_uart_probe.py`.
Machine-local build logs and the draft graphical review are recorded under
`agents/`; no draft result is physical qualification evidence.

## Approved-identity review builds

1. EMOS draft: `agon-emos-v0.3.0-b2026-09-08-03-42-39Z`, 117824 bytes,
   SHA-256 `c3afd15996f24450767900afcb033a932f3b98a98374248ff148d2ef1743cdf5`. The maintained-source and builder
   inputs remain uncommitted; their snapshots are retained in the private
   build manifest. The full configured gate, ordinary smoke and intentional
   bad-SD checks pass.
2. P4 draft: `uart-roundtrip-probe-r01-b2026-09-08-03-42-41Z`; build passes.
   It remains a review artifact, not a hardware deployment candidate.
3. The combined graphical profile runs the same-build ordinary SD/clock smoke
   followed by UARTTEST. Its automated target check observes all smoke PASS
   markers, the expected missing-peer UART failure, and prompt return.
   The private launcher is `agents/review-uart-roundtrip`. The Author supplied
   its screenshot: the exact draft build, SD/CLOCK PASS, expected no-peer
   failure, autoexec line 4 error, inherited Volume timeout and final `/ *`
   prompt are visible. The Author accepted the visual check and explicitly
   approved the source checkpoint. Clean candidate preparation and physical
   qualification remain pending; no flash or SD edit.

## Accepted source checkpoint

The Author accepted the visual review and authorized commits across Extender,
EMOS and the generic builder. EMOS cfc9afc and mos-agondev cf24304 freeze
their reviewed implementation. This Extender checkpoint retains r26's approved
draft identities; existing dirty review images are not deployment candidates.

Extender origin/main contained d30f4fc, the published version of the local
e013e42 UART checkpoint amendment. Their only tree differences were two raw
log `.gitattributes` files. Merge f46a219 preserves both histories and the local
attributes; its tree is identical to e013e42. No firmware or evidence bytes
changed. Do not amend these published checkpoints or force-push over them.
