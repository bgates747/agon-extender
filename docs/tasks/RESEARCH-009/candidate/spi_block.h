#ifndef RESEARCH_009_SPI_BLOCK_H
#define RESEARCH_009_SPI_BLOCK_H

#include <stdbool.h>
#include <stdint.h>

/*
 * Host-checkable reference for one eZ80-owned SPI block and its P4 receipt.
 * The callers enforce an absolute deadline, the physical SPI arbiter and
 * the READY/MISO wiring. This code neither opens hardware nor changes
 * existing UART or SD protocols.
 */
enum spi_direction { P4_TO_EZ80, EZ80_TO_P4 };
enum spi_phase { SPI_IDLE, SPI_OFFERED, SPI_ARMED, SPI_CLOCKING, SPI_RETURN, SPI_FAULT };

struct spi_offer {
    uint32_t session;
    uint32_t sequence;
    uint16_t bytes;
    enum spi_direction direction;
};

struct spi_block {
    enum spi_phase phase;
    struct spi_offer offer;
    bool complete;
};

enum { SPI_BLOCK_BYTES = 512, SPI_DMA_ALIGN = 4 };

uint16_t spi_wire_bytes(uint16_t payload);
uint16_t spi_dma_span(uint16_t payload);
bool spi_offer(struct spi_block *b, struct spi_offer offer);
bool spi_arm(struct spi_block *b, struct spi_offer armed);
bool spi_start(struct spi_block *b, bool ready_asserted, bool sd_released);
bool spi_close(struct spi_block *b, bool cs_inactive, bool miso_isolated);
bool spi_confirm(struct spi_block *b, struct spi_offer completed, uint32_t clocked_bits);
void spi_abort(struct spi_block *b);
bool spi_retire(struct spi_block *b, bool cs_inactive, bool miso_isolated, bool p4_retired);

#endif
