# P084 UART0 CTS-edge port for production PARLIO EMOS

Production EMOS can trap the eZ80 inside its UART0 interrupt while the
mainboard VDP withholds CTS. The owner will qualify an isolated candidate that
yields to the game and re-arms transmission on a hardware CTS edge. It keeps the
same transport ABI and the production PARLIO build profile.

Smith selected no busy waits on either processor in FSIM turn
`01a1efe7-1acb-72c2-b6df-216855770bb8`, message
`01a1efe7-1b06-75a0-9d0b-6ca890969b8c`. FSIM owns the demand-pull consumer and
requested this EMOS dependency under its frozen implementation contract.

- P084-TX-01 [x] Trace production EMOS `abefa2f943eb3089c08d85bf39e48ebb4938f4bd`,
  ROM `9b90b5d94ec6888d85ef1fa1acf23a82b2e0eb1f179b75f549863fbd72343673`.
  Guarded `25h` has no foreground send wait. Each UART0 TX interrupt spins
  while PD3 CTS is high with interrupts disabled.

- P084-TX-02 [x] Port opt-in CTS deferral and modem IRQ re-arm to an isolated
  EMOS worktree based on that production commit. Use the [qualified CTS-edge
  design](UART0-CTS-PROGRESS-R01-RESULT.md) and its retained source as donor.
  Preserve the `25h` register/result ABI, 16-byte FIFO limit, exact ordering,
  single source ownership, distinct callback/TEMT/VDP receipt, and SD read and
  write PARLIO plus UART1 runtime composition. Check pending ownership, reject
  pre-owned modem interrupt enable, keep VBlank as re-arm fallback, and leave
  the TX IRQ as the sole copier. Scope this option to the paired production
  RFC25 and two-way SD profile. Use no consumer GPIO or UART bypass.

- P084-TX-03 [x] Run the native firmware wrapper and all mandatory linked
  validators on the Pi compiler FIFO. Compare option-off bytes under the same
  production identity. Execute the retained linked-byte edge model on the
  option-on ROM and check partial backpressure, unrelated or spurious IRQs,
  owner lifetime, RX path, exact table admission and unchanged SD support.
  Use a single serial compile reservation, bounded to ten minutes of work once
  granted, and join the compiler before release.

- P084-TX-04 [x] Retain exact candidate ROM, ELF, map, source and validation
  hashes. Return the artifact path, no-spin/readiness limits and unchanged ABI
  to FSIM. The [current production selection](../../../production/current.yaml)
  stays in place. Physical testing, installation, promotion, FSIM OPEN diagnostics
  and unrelated owner work require separate scope.

The [Agon MOS API](https://agonplatform.github.io/agon-docs/mos/API/) establishes
the interrupt and callback baseline. The existing CTS-edge donor traces PD3
active-low CTS0, UART modem interrupt cause, and MSR acknowledgement to the
Zilog documentation. Source and linked-byte tests can prove control flow and
owner semantics under the model. Hardware edge timing and FSIM runtime behavior
remain a separate qualification.

## Offline result

Plan frozen and pushed at `5744fa761d1c1f89774e538e3bea007d59bfe52e`.
The [EMOS source revision](https://github.com/bgates747/agon-emos/commit/44f791aa706d9a28c083d81714926735cb922c90)
is published on `codex/p084-parlio-cts-irq`.

| Artifact | Identity |
| --- | --- |
| Experimental build | `agon-emos-eirene-r06-b2026-11-18-18-36-09Z` |
| Padded ROM, 131,072 bytes | `503ea79250df07fdc0a01ba287cca5772fd548b14e3712ba9fe44a024dcad12e` |
| ELF | `84b76edcba7d96e85bcb113a57acc748edd130af0c591f23f54be82e927cc85a` |
| Map | `e3c08587796bd143070b56ff5af7984e936adf63ca79362769827161191de625` |
| Source archive | `d4cd79ce87914f63cad073caa133e57c976d00e74b5671aa04ce94dac28f45bf` |

The option-off ROM matched the production restore image byte for byte. The
option-on ROM uses 130,040 bytes, 118 more than production, leaving 1,032 bytes.
Initialized RAM is unchanged and BSS grows by one byte. Both builds passed all
mandatory linked validators, including the paired SD read and upload checks.
The option-on build additionally passed 90 linked CTS cases with a maximum of
nine modeled stack bytes on the rearm path. The build rejected CTS IRQ without
the paired SD and RFC25 profile and with the separate application-network
PARLIO carrier. Pi compiler generation 978 was released after both serial build
process groups joined.

The TX interrupt samples CTS once before touching the pending source or count.
If the receiver withholds permission, EMOS masks TX, publishes the deferred
owner, arms and acknowledges the modem interrupt, resamples CTS and returns.
The modem interrupt or VBlank rearms the sole FIFO copier. A later stop can
still leave a partly transmitted stream, so the application retains source
and callback through release, honors TEMT ordering and waits for its own
correlated VDP receipt before reusing staging. Pin the exact ROM to select
this behavior. The `25h` result and callback ABI are unchanged and do not
advertise CTS-edge support. No bench run, installation or promotion occurred.
