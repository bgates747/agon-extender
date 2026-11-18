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

- P084-TX-02 [ ] Port opt-in CTS deferral and modem IRQ re-arm to an isolated
  EMOS worktree based on that production commit. Use the [qualified CTS-edge
  design](UART0-CTS-PROGRESS-R01-RESULT.md) and its retained source as donor.
  Preserve the `25h` register/result ABI, 16-byte FIFO limit, exact ordering,
  single source ownership, distinct callback/TEMT/VDP receipt, and SD read and
  write PARLIO plus UART1 runtime composition. Check pending ownership, reject
  pre-owned modem interrupt enable, keep VBlank as re-arm fallback, and leave
  the TX IRQ as the sole copier. Scope this option to the paired production
  RFC25 and two-way SD profile. Use no consumer GPIO or UART bypass.

- P084-TX-03 [ ] Run the native firmware wrapper and all mandatory linked
  validators on the Pi compiler FIFO. Compare option-off bytes under the same
  production identity. Execute the retained linked-byte edge model on the
  option-on ROM and check partial backpressure, unrelated or spurious IRQs,
  owner lifetime, RX path, exact table admission and unchanged SD support.
  Use a single serial compile reservation, bounded to ten minutes of work once
  granted, and join the compiler before release.

- P084-TX-04 [ ] Retain exact candidate ROM, ELF, map, source and validation
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
