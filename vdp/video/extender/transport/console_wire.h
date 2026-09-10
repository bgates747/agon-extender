/* PORT-008 paired console control, wire version 1. Private EMOS/EDP interface.
 * Identical reviewed copy in agon-extender; see its console protocol document.
 * Ordinary VDU and stock keyboard/reply bytes are not re-encoded.
 */
#ifndef EMOS_CONSOLE_WIRE_H
#define EMOS_CONSOLE_WIRE_H
#define CONSOLE_OPCODE 0xF7
#define CONSOLE_REPLY 0xFF
#define CONSOLE_SIZE 16
#define CONSOLE_PREPARE 1
#define CONSOLE_COMMIT 2
#define CONSOLE_LEAVE 3
#define CONSOLE_ABORT 4
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
static void console_seal(unsigned char *p) {
    unsigned short crc = console_crc(p);
    p[14] = (unsigned char)crc; p[15] = (unsigned char)(crc >> 8);
}
static unsigned char console_valid(const unsigned char *p) {
    unsigned short crc = console_crc(p);
    return p[0] == 'E' && p[1] == 'X' && p[2] == 1 && p[12] == 1 &&
        p[14] == (unsigned char)crc && p[15] == (unsigned char)(crc >> 8);
}
#endif
