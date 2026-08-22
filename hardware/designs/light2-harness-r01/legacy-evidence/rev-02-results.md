# REV-02 bounded PING results

REV-02 passed on 2026-08-18 with the standalone Agon `rev02.bin`, dedicated
P4 `rev02` feature, and retained LA-03 probe map. The compact passing run is:

`tests/runs/2026-08-18_200400_rev-02-ping/`

Its `SHA256SUMS.local` manifest has SHA-256
`e61762af7b0c2fac189e1a67c797dadec713bbeb6ab64b94e155d17f2ff1ad4e`.
Every file named by that manifest verifies. The deterministic raw logic trace
and sigrok log were discarded after analysis.

## Exchange

The analyzer decoded one exact sequence-2 exchange at 115200 baud:

| Frame | Bytes |
|---|---|
| Agon `POLL` | `A7 E1 01 01 02 00 00 BB` |
| P4 `PING COMMAND` | `A7 E1 01 02 02 01 5A E3` |
| Agon `STATUS_OK RESPONSE` | `A7 E1 01 03 02 01 00 B8` |

Magic, version, type, sequence, opcode, argument, and check byte matched on all
three frames. The P4 endpoint reported exactly one UART PASS and bound its
short ELF identity to the freshly built local image.

## Ownership and following record

The 8 MHz, 6,000,000-sample capture triggered on the falling edge of
`REV_OE_N`, retaining the complete poll in its 10% pre-trigger interval. It
measured:

- 101.375 us forward-to-reverse both-off time;
- 13.875 us reverse-to-forward both-off time;
- zero samples with both active-low enables asserted;
- UART activity in the expected forward, reverse, and response windows;
- exactly 1,024 qualified clocks in the following PARLIO record;
- zero mismatches on analyzer-observed data bits D0, D1, and D4; and
- final forward ownership: `FWD_OE_N=0`, `REV_OE_N=1`.

The P4 independently validated all eight bits of the following canonical
record, sequence 1 and CRC `6474`. Thus the analyzer's partial data-bus view is
not used to claim full-width integrity by itself.

## Bounded and malformed behavior

Every wire frame is fixed at eight bytes. The shared native tests reject wrong
length, magic, version, checksum, opcode, and response status. The Agon driver
uses a 500 ms transaction timeout and always closes UART1; the P4 fixture uses
a 5 s exchange/canary bound and converges failed exchanges to released output
enables; the capture helper has a 30 s process timeout. These are offline/code
proofs, not a claim that malformed traffic was injected during the passing
physical run.

The retained analyzer JSON has SHA-256
`d0bdaf755c481ba0df0fbffc47ad36fb9517ddef395998f861004f78e8bfa226`;
the endpoint result has SHA-256
`a729d883f9bfb5320ed8f57db0cef5b89475fa81bbfcaced6c58ae971b42e66d`.
