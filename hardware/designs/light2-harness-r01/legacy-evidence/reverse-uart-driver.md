# Port C reverse-UART driver

Decision D-006 and [`design/carrier-breakout-design.md`](../design/carrier-breakout-design.md)
define the electrical boundary. This document defines the software lifecycle.
It does not replace the task gates in `TODO.md`.

## Endpoint bindings

The Agon uses its supported UART1 peripheral on `PC0/TxD1` and `PC1/RxD1`.
These nets reach the UEXT and expansion headers; they are not the onboard VDP
UART. Agondev's `mos_uopen`, `mos_uputc`, `mos_ugetc_nb`, and `mos_uclose`
provide the baseline lifecycle. `agm_wire_enter_idle` restores Port C to GPIO
after closing UART1.

The P4 uses hardware UART1 at 115200 baud, 8 data bits, no parity, and one stop
bit. GPIO22 is RX from Agon `PC0`; GPIO12 becomes TX toward Agon `PC1` only
during the reverse-driving phase. GPIO15 drives `FWD_OE_N`; GPIO21 drives
`REV_OE_N`. Both buffer enables are active Low and externally pulled High.

## Fixed exchange

Each forward record is followed by one bounded control opportunity:

1. The P4 completes the mounted PARLIO receive and releases `READY_N`.
2. The Agon restores idle, opens UART1, and transmits one eight-byte `POLL`.
3. The P4 receives the poll with forward buffers enabled.
4. The P4 disables forward ownership, waits the break interval, makes GPIO12 a
   UART output, enables reverse ownership, and sends one eight-byte `COMMAND`.
5. After UART TX-empty, the P4 disables reverse ownership, waits the break
   interval, makes GPIO12 an input, and re-enables forward ownership.
6. The Agon applies the command and sends one eight-byte `RESPONSE` on PC0.
7. Both endpoints validate the response, close UART mode, and return to the
   forward parallel state.

There is no unsolicited P4 transmission. A browser STOP becomes pending on the
P4 and is delivered at the next poll. Thus no additional request GPIO and no
second meaning for `READY_N` are introduced.

The Agon waits 10–20 ms after accepting the command before beginning its
response. Its 100 Hz `clock()` source cannot express the P4's microsecond-scale
handoff directly, so two tick changes guarantee at least one complete 10 ms
tick. This prevents the first response byte from entering U1 during the
measured reverse-to-forward both-off interval.

## Frame

Every frame is exactly eight bytes:

| Offset | Meaning |
|---:|---|
| 0 | magic `0xA7` |
| 1 | magic `0xE1` |
| 2 | version `1` |
| 3 | type: poll `1`, command `2`, response `3` |
| 4 | poll sequence, copied through command and response |
| 5 | opcode: none `0`, ping `1`, stop `2` |
| 6 | command argument or response status |
| 7 | `0xFF` XOR bytes 0 through 6 |

The fixed size is the maximum size. There is no length field, allocation,
escaping, general RPC envelope, or unbounded parser. Damaged magic, version,
type, sequence, or check byte rejects the exchange.

## Test payload envelope (re-used for REV-02a)

For the forward-to-reverse correctness fixture (`REV-02a`), start with a
reproducible deterministic payload source and any integrity field that gives
strong fault localization. The existing `P4`-side canary layout in
`common/p4_canary.[ch]` is a valid default because it is already implemented and
instrumented, but it is not the only acceptable format.

| Offset | Meaning |
|---:|---|
| 0x00 | Example canonical marker/magic (`"AEP3"` in the existing canary) |
| 0x04 | Sequence field if present (for ordering / replay detection) |
| 0x08 | Payload bytes |
| 0x1FE | Example embedded CRC16-CCITT high byte (canary layout example) |
| 0x1FF | Example embedded CRC16-CCITT low byte |

`P4_CANARY_SIZE` remains a valid starting point (`1024`) for REV-02a if you
keep the canary format unchanged. Alternative fixed-size streams are allowed if
both sides share the exact expected generator and integrity check.

Default canary path:
- fixed width `[0x08..0x1FD]` payload in `common/p4_canary.[ch]`
- `p4_canary_validate()` verifies embedded CRC via `p4_canary_read_crc()` and
  `p4_crc16_ccitt()`.

## Failure convergence

The P4 driver sets both enables High on malformed input, timeout, short write,
or response mismatch and makes GPIO12 an input. The caller must explicitly
re-enter forward ownership before another PARLIO record. The Agon closes UART1
on every exit and restores GPIO ownership before continuing. Neither endpoint
retries invisibly.

The initial break-before-make interval is 10 microseconds. REV-01 must measure
the physical interval at U1 outputs and may reduce or increase it from evidence.
The 500 ms Agon transaction timeout is intentionally generous for the first
proof and is not a latency target.

## Implementation surfaces

- `common/reverse_uart_protocol.[ch]`: platform-neutral fixed-frame codec;
- `src/modules/agm/reverse_uart.[ch]`: P4 hardware UART and buffer ownership driver;
- `agm/agon/src/reverse_uart.[ch]`: Agon UART1 poll/command/response driver;
- `test/test_reverse_uart_protocol.c`: native known-good and damaged-frame
  checks.

The drivers are not yet called by the media path. REV-02 integrates them only
through the standalone `agon/rev02_ping` and P4 `rev02` diagnostic fixtures
defined in [`tests/procedures/rev-02-ping.md`](../tests/procedures/rev-02-ping.md),
so fixture orchestration does not enter the working AGM appliance.
