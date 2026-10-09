/* Shared fixed 16-byte control-body CRC; mirrored in EMOS and EDP. */
#ifndef EMOS_CONTROL_CRC_H
#define EMOS_CONTROL_CRC_H
static unsigned short console_crc(const unsigned char *p) {
    /* Use native-width arithmetic: avoids adding a short-XOR runtime helper
     * to the restricted AgonDev link closure. Low 16 bits define the CRC. */
    unsigned int crc = 0xFFFF;
    unsigned char i, bit;
    for (i = 0; i < 14; ++i) {
        crc ^= (unsigned short)p[i] << 8;
        for (bit = 0; bit < 8; ++bit)
            crc = (unsigned short)((crc << 1) ^ ((crc & 0x8000) ? 0x1021 : 0));
    }
    return crc;
}
#endif
