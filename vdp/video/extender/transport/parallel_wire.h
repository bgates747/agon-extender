/* PORT-008 F02c2b1: private candidate; NOT bound to a live UART parser.
 * Include the existing console wire header first: reuse its 16-byte CRC.
 * Mirrored exactly in EMOS. See PARALLEL-ADMISSION.md for ownership/lifetime.
 * session[0..3] is established by the coordinator, never by an offer;
 * session[4..5] is the last consumed sequence. Reset/cancel invalidates it.
 */
#ifndef EMOS_PARALLEL_WIRE_H
#define EMOS_PARALLEL_WIRE_H
#include <string.h>
#define PARALLEL_WIRE_VERSION 2
#define PARALLEL_OFFER 2
#define PARALLEL_ACK 0x82
#define PARALLEL_COMPLETE 4
#define PARALLEL_COMPLETE_ACK 0x84
#define PARALLEL_EXEXT 3
#define PARALLEL_SESSION_SIZE 6
/* The retained offer supplies authority, never the arriving result. Failure
 * status is a valid result, not permission to publish a received prefix. */
static inline unsigned char parallel_block_matches(const unsigned char *offer,
    const unsigned char *p, unsigned char operation) {
    unsigned short crc;
    if (memcmp(offer,p,3) || p[3]!=operation || memcmp(offer+4,p+4,9) ||
        p[13] > (operation==PARALLEL_ACK ? 0 : 1)) return 0;
    crc=console_crc(p);
    return p[14]==(unsigned char)crc && p[15]==(unsigned char)(crc>>8);
}
static inline unsigned char parallel_offer_valid(const unsigned char *session,
                                          const unsigned char *p) {
    unsigned short next, crc;
    if (!(session[0] | session[1] | session[2] | session[3]) ||
        p[0] != 'E' || p[1] != 'X' || p[2] != PARALLEL_WIRE_VERSION ||
        p[3] != PARALLEL_OFFER || p[12] > 1 || p[13] ||
        !(p[10] | p[11]) || p[11] > 16 || (p[11] == 16 && p[10]) ||
        memcmp(session, p + 4, 4)) return 0;
    next = (unsigned short)((session[4] | ((unsigned short)session[5] << 8)) + 1);
    if (!next || p[8] != (unsigned char)next || p[9] != (unsigned char)(next >> 8)) return 0;
    crc = console_crc(p);
    return p[14] == (unsigned char)crc && p[15] == (unsigned char)(crc >> 8);
}
#endif
