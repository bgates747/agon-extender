#include "p4_canary.h"

static const uint8_t canary_magic[P4_CANARY_MAGIC_SIZE] = {
    0x41, 0x45, 0x50, 0x33, /* "AEP3" */
};

uint16_t p4_crc16_ccitt(const uint8_t *data, size_t size)
{
    uint16_t crc = UINT16_C(0xFFFF);

    for (size_t index = 0; index < size; ++index) {
        crc ^= (uint16_t)data[index] << 8;
        for (unsigned bit = 0; bit < 8; ++bit) {
            if ((crc & UINT16_C(0x8000)) != 0) {
                crc = (uint16_t)((crc << 1) ^ UINT16_C(0x1021));
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}

void p4_canary_build(uint8_t record[P4_CANARY_SIZE])
{
    for (size_t index = 0; index < P4_CANARY_MAGIC_SIZE; ++index) {
        record[index] = canary_magic[index];
    }

    record[P4_CANARY_SEQUENCE_OFFSET + 0] = 0x01;
    record[P4_CANARY_SEQUENCE_OFFSET + 1] = 0x00;
    record[P4_CANARY_SEQUENCE_OFFSET + 2] = 0x00;
    record[P4_CANARY_SEQUENCE_OFFSET + 3] = 0x00;

    for (size_t offset = P4_CANARY_PAYLOAD_OFFSET;
         offset < P4_CANARY_CRC_OFFSET; ++offset) {
        record[offset] = (uint8_t)(offset - P4_CANARY_PAYLOAD_OFFSET);
    }

    const uint16_t crc = p4_crc16_ccitt(record, P4_CANARY_CRC_OFFSET);
    record[P4_CANARY_CRC_OFFSET] = (uint8_t)(crc >> 8);
    record[P4_CANARY_CRC_OFFSET + 1] = (uint8_t)crc;
}

uint32_t p4_canary_read_sequence(const uint8_t record[P4_CANARY_SIZE])
{
    return (uint32_t)record[P4_CANARY_SEQUENCE_OFFSET + 0] |
           ((uint32_t)record[P4_CANARY_SEQUENCE_OFFSET + 1] << 8) |
           ((uint32_t)record[P4_CANARY_SEQUENCE_OFFSET + 2] << 16) |
           ((uint32_t)record[P4_CANARY_SEQUENCE_OFFSET + 3] << 24);
}

uint16_t p4_canary_read_crc(const uint8_t record[P4_CANARY_SIZE])
{
    return ((uint16_t)record[P4_CANARY_CRC_OFFSET] << 8) |
           (uint16_t)record[P4_CANARY_CRC_OFFSET + 1];
}

bool p4_canary_validate(const uint8_t *record, size_t size)
{
    if (size != P4_CANARY_SIZE ||
        record[0] != P4_CANARY_FIRST_BYTE ||
        record[P4_CANARY_CRC_OFFSET - 1] != P4_CANARY_LAST_PAYLOAD_BYTE ||
        record[P4_CANARY_SIZE - 1] != P4_CANARY_LAST_BYTE) {
        return false;
    }

    for (size_t index = 0; index < P4_CANARY_MAGIC_SIZE; ++index) {
        if (record[index] != canary_magic[index]) {
            return false;
        }
    }
    if (p4_canary_read_sequence(record) != P4_CANARY_SEQUENCE) {
        return false;
    }
    for (size_t offset = P4_CANARY_PAYLOAD_OFFSET;
         offset < P4_CANARY_CRC_OFFSET; ++offset) {
        if (record[offset] !=
            (uint8_t)(offset - P4_CANARY_PAYLOAD_OFFSET)) {
            return false;
        }
    }

    return p4_canary_read_crc(record) == P4_CANARY_CRC &&
           p4_crc16_ccitt(record, P4_CANARY_CRC_OFFSET) == P4_CANARY_CRC;
}
