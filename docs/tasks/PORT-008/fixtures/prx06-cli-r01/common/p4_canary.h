#ifndef AGON_EXTENDER_P4_CANARY_H
#define AGON_EXTENDER_P4_CANARY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

enum {
    P4_CANARY_SIZE = 1024,
    P4_CANARY_MAGIC_SIZE = 4,
    P4_CANARY_SEQUENCE_OFFSET = 4,
    P4_CANARY_PAYLOAD_OFFSET = 8,
    P4_CANARY_CRC_OFFSET = 1022,
    P4_CANARY_SEQUENCE = 1,
    P4_CANARY_FIRST_BYTE = 0x41,
    P4_CANARY_LAST_PAYLOAD_BYTE = 0xF5,
    P4_CANARY_CRC = 0x6474,
    P4_CANARY_LAST_BYTE = 0x74,
};

uint16_t p4_crc16_ccitt(const uint8_t *data, size_t size);
void p4_canary_build(uint8_t record[P4_CANARY_SIZE]);
uint32_t p4_canary_read_sequence(const uint8_t record[P4_CANARY_SIZE]);
uint16_t p4_canary_read_crc(const uint8_t record[P4_CANARY_SIZE]);
bool p4_canary_validate(const uint8_t *record, size_t size);

#endif
