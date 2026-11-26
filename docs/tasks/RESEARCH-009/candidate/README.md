# SPI block admission candidate

This portable C model tests the sequencing that a future EMOS SPI owner and P4
SPI peripheral driver would implement for a staged SD payload. It adds no
application API, UART opcode, checksum, driver integration or production object.

1. EMOS offers a block using the existing control path. Each offer binds a
   nonzero session, sequence, direction and logical byte count. EMOS checks
   that the P4 has armed the matching DMA descriptor. The physical READY
   signal alone cannot identify a block. The real adapter must require an
   inactive READY baseline and a fresh arm indication on recovery.
2. The P4 prepares its source or destination buffer in DMA-capable memory,
   queues the descriptor and asserts READY when the peripheral is armed.
   The host clocks a multiple of four bytes. Both endpoints ignore padding.
   The P4 descriptor has four extra bytes of capacity so that
   `trans_len` clipping cannot hide an oversized transaction. Provision the
   complete descriptor span on both the P4 TX and RX paths used by the driver.
3. EMOS starts the clock only after its SPI arbiter has exclusive ownership
   and the SD driver has finished deselect and release. The adapter drives
   at most one chip select low. The P4's shared MISO is hardware-gated.
   EMOS deasserts the P4 chip select and restores the SD configuration before
   it waits for the ordinary UART return. No SD operation or callback takes
   the bus during a selected burst.
4. The P4 reports the observed bit count against the same offer. EMOS accepts
   only an exact receipt and returns ownership after the old descriptor retires
   and both select and MISO isolation are safe. The caller owns deadlines,
   duplicate/replay prevention across retired offers, durable SD progress and
   session invalidation after resets. A fault leaves the block fenced until the
   same physical release is proved.

The model checks one block at a time. It does not simulate the eZ80 SPI status
register, FatFS, the P4 driver callbacks, electrical isolation, timing or reset
pins. Those checks need linked firmware and physical qualification. The
512-byte sample block limit is for the experiment. Measure the effect of block
size and acknowledgements before choosing a production packet or budget.

From this directory, compile with a host C11 compiler:

```sh
scratch=$(mktemp -d)
cc -std=c11 -O2 -Wall -Wextra -Werror -pedantic spi_block.c test_spi_block.c -o "$scratch/test-spi"
"$scratch/test-spi"
```

The checks cover all 512 logical sizes in both directions including residues
of one, two and three bytes, premature clocks, a stale arm and reply, short and
extra clocks, SD exclusion, and cancellation through every live phase. The
[P4 SPI driver reference](https://docs.espressif.com/projects/esp-idf/en/release-v5.5/esp32p4/api-reference/peripherals/spi_slave.html)
describes DMA alignment and descriptor length reporting.
