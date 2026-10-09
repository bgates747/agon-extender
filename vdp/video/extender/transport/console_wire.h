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
#define CONSOLE_PREPARE_KEEP 5
#include "control_crc.h"
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
