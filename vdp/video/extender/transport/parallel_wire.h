/* PORT-008 COMPLETION-REMOVAL-R01: experimental paired parallel format4.
 * No transport CRC/checksum. Keep the 16-byte carrier for this isolated cut;
 * transmit zero in former CRC slots14-15 and IGNORE them on receipt.
 * Formats2/3 peers cannot admit; COMPLETE/ACK is removed. Ordinary version1 console controls are separate.
 * Mirrored exactly in EMOS. See PARALLEL-ADMISSION.md for ownership/lifetime.
 * session[0..3] is established by the coordinator, never by an offer;
 * session[4..5] is the last consumed sequence. Reset/cancel invalidates it.
 */
#ifndef EMOS_PARALLEL_WIRE_H
#define EMOS_PARALLEL_WIRE_H
#include <string.h>
#define PARALLEL_WIRE_VERSION 4
#define PARALLEL_OFFER 2
#define PARALLEL_ACK 0x82
#define PARALLEL_STREAM_START 6
#define PARALLEL_STREAM_POLL 8
#define PARALLEL_STREAM_STOP 10
#define PARALLEL_EXEXT 3
#define PARALLEL_SESSION_SIZE 6
/* Padding is not a check: receivers deliberately ignore these two bytes. */
static inline void parallel_control_pad(unsigned char *p) {
    p[14] = p[15] = 0;
}
/* Only an exact admission ACK grants entry. Physical return owns completion. */
static inline unsigned char parallel_block_matches(const unsigned char *offer,
    const unsigned char *p, unsigned char operation) {
    if (offer[2]!=PARALLEL_WIRE_VERSION || memcmp(offer,p,3) || p[3]!=operation || memcmp(offer+4,p+4,9) ||
        p[13]) return 0;
    return 1;
}
static inline unsigned char parallel_offer_valid(const unsigned char *session,
                                          const unsigned char *p) {
    unsigned short next;
    if (!(session[0] | session[1] | session[2] | session[3]) ||
        p[0] != 'E' || p[1] != 'X' || p[2] != PARALLEL_WIRE_VERSION ||
        p[3] != PARALLEL_OFFER || p[12] > 1 || p[13] ||
        !(p[10] | p[11]) || p[11] > 16 || (p[11] == 16 && p[10]) ||
        memcmp(session, p + 4, 4)) return 0;
    next = (unsigned short)((session[4] | ((unsigned short)session[5] << 8)) + 1);
    if (!next || p[8] != (unsigned char)next || p[9] != (unsigned char)(next >> 8)) return 0;
    return 1;
}
#endif
