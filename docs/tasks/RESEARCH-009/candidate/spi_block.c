#include "spi_block.h"

static bool same_offer(struct spi_offer a, struct spi_offer b)
{
    return a.session == b.session && a.sequence == b.sequence &&
           a.bytes == b.bytes && a.direction == b.direction;
}

uint16_t spi_wire_bytes(uint16_t payload)
{
    return payload && payload <= SPI_BLOCK_BYTES ?
        (uint16_t)((payload + SPI_DMA_ALIGN - 1u) & ~(SPI_DMA_ALIGN - 1u)) : 0;
}

uint16_t spi_dma_span(uint16_t payload)
{
    uint16_t wire = spi_wire_bytes(payload);
    /* IDF clips trans_len to the descriptor length. Reserve one word so
     * surplus clocks are still distinguishable from exact completion. */
    return wire ? (uint16_t)(wire + SPI_DMA_ALIGN) : 0;
}

bool spi_offer(struct spi_block *b, struct spi_offer offer)
{
    if (b->phase != SPI_IDLE || offer.session == 0 ||
        !spi_wire_bytes(offer.bytes) ||
        (offer.direction != P4_TO_EZ80 && offer.direction != EZ80_TO_P4)) {
        return false;
    }
    b->offer = offer;
    b->complete = false;
    b->phase = SPI_OFFERED;
    return true;
}

bool spi_arm(struct spi_block *b, struct spi_offer armed)
{
    if (b->phase != SPI_OFFERED || !same_offer(b->offer, armed)) {
        return false;
    }
    b->phase = SPI_ARMED;
    return true;
}

bool spi_start(struct spi_block *b, bool ready_asserted, bool sd_released)
{
    if (b->phase != SPI_ARMED || !ready_asserted || !sd_released) {
        return false;
    }
    b->phase = SPI_CLOCKING;
    return true;
}

bool spi_close(struct spi_block *b, bool cs_inactive, bool miso_isolated)
{
    if (b->phase != SPI_CLOCKING || !cs_inactive || !miso_isolated) {
        return false;
    }
    b->phase = SPI_RETURN;
    return true;
}

bool spi_confirm(struct spi_block *b, struct spi_offer completed, uint32_t clocked_bits)
{
    if (b->phase != SPI_RETURN || b->complete) {
        return false;
    }
    if (!same_offer(b->offer, completed) ||
        clocked_bits != UINT32_C(8) * spi_wire_bytes(b->offer.bytes)) {
        spi_abort(b);
        return false;
    }
    b->complete = true;
    return true;
}

void spi_abort(struct spi_block *b)
{
    if (b->phase != SPI_IDLE) {
        b->complete = false;
        b->phase = SPI_FAULT;
    }
}

bool spi_retire(struct spi_block *b, bool cs_inactive, bool miso_isolated, bool p4_retired)
{
    if ((b->phase != SPI_FAULT && !(b->phase == SPI_RETURN && b->complete)) ||
        !cs_inactive || !miso_isolated || !p4_retired) {
        return false;
    }
    *b = (struct spi_block){0};
    return true;
}
