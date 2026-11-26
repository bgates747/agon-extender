#include <assert.h>
#include <stdio.h>
#include "spi_block.h"

static void clock_block(struct spi_block *b, struct spi_offer o)
{
    struct spi_offer stale = o;
    --stale.session;
    assert(spi_offer(b, o));
    assert(!spi_start(b, true, true));  /* READY alone may be stale. */
    assert(!spi_arm(b, stale));
    assert(spi_arm(b, o));
    assert(!spi_start(b, true, false)); /* SD still owns the bus. */
    assert(!spi_start(b, false, true));
    assert(spi_start(b, true, true));
    assert(!spi_offer(b, o));
    assert(!spi_confirm(b, o, 8u * spi_wire_bytes(o.bytes)));
    assert(!spi_close(b, false, true));
    assert(!spi_close(b, true, false));
    assert(spi_close(b, true, true));
}

int main(void)
{
    struct spi_block b = {0};
    unsigned tested = 0;
    assert(!spi_wire_bytes(0));
    assert(!spi_wire_bytes(513));
    for (uint16_t size = 1; size <= SPI_BLOCK_BYTES; ++size) {
        uint16_t wire = spi_wire_bytes(size);
        assert(wire % 4 == 0 && wire >= size && wire - size < 4);
        assert(spi_dma_span(size) == wire + 4);
        for (int direction = P4_TO_EZ80; direction <= EZ80_TO_P4; ++direction) {
            struct spi_offer o = {5, ++tested, size, (enum spi_direction)direction};
            clock_block(&b, o);
            assert(!spi_retire(&b, true, true, true));
            assert(spi_confirm(&b, o, 8u * wire));
            assert(!spi_confirm(&b, o, 8u * wire));
            assert(!spi_retire(&b, true, true, false));
            assert(spi_retire(&b, true, true, true));
            clock_block(&b, o);
            assert(!spi_confirm(&b, o, 8u * wire - 1));
            assert(b.phase == SPI_FAULT && !b.complete);
            assert(!spi_retire(&b, true, false, true));
            assert(spi_retire(&b, true, true, true));
            clock_block(&b, o);
            assert(!spi_confirm(&b, o, 8u * wire + 1));
            assert(spi_retire(&b, true, true, true));
        }
    }
    const struct spi_offer offered = {6, 9, 177, EZ80_TO_P4};
    struct spi_offer wrong = offered;
    ++wrong.sequence;
    clock_block(&b, offered);
    assert(!spi_confirm(&b, wrong, 8u * spi_wire_bytes(offered.bytes)));
    assert(spi_retire(&b, true, true, true));
    for (enum spi_phase phase = SPI_OFFERED; phase <= SPI_RETURN; ++phase) {
        b.phase = phase;
        spi_abort(&b);
        assert(!spi_offer(&b, offered));
        assert(!spi_retire(&b, false, true, true));
        assert(!spi_retire(&b, true, false, true));
        assert(!spi_retire(&b, true, true, false));
        assert(spi_retire(&b, true, true, true));
    }
    printf("PASS: %u size/direction pairs, short and excess clocks, stale arm/reply, SD exclusion and abort recovery\n", tested);
}
