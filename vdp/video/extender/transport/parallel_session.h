/* PORT-008 F02c2b3: private, dormant session lifecycle. Mirrored in EMOS.
 * Reuses the existing console prepare/challenge/commit idiom and CRC.
 * The owner wrapper must establish UART recovery and serializer authority.
 * No parser, GPIO, mode commitment, clock or autonomous request lives here.
 * Invalidation retains the last nonce solely to reject reuse; phase, not
 * retained bytes, grants admission. Boot must also quarantine stale wire data.
 */
#ifndef EMOS_PARALLEL_SESSION_H
#define EMOS_PARALLEL_SESSION_H
#include <string.h>
#include "control_crc.h"
/* Include the owner's parallel-wire header first (its filename differs). */
#define PARALLEL_PREPARE 1
#define PARALLEL_COMMIT 3
#define PARALLEL_SESSION_IDLE 0
#define PARALLEL_SESSION_PREPARING 1
#define PARALLEL_SESSION_COMMITTING 2
#define PARALLEL_SESSION_ACTIVE 3
#define PARALLEL_SESSION_STAGED 4
typedef struct {
    unsigned char bytes[PARALLEL_SESSION_SIZE];
    unsigned char transaction[4];
    unsigned char phase;
} t_parallelSession;

static inline unsigned char parallel_nonzero(const unsigned char *p) {
    return p[0] | p[1] | p[2] | p[3];
}
static inline void parallel_session_invalidate(t_parallelSession *s) {
    s->phase = PARALLEL_SESSION_IDLE;
    s->bytes[4] = s->bytes[5] = 0;
}
static inline void parallel_session_seal(unsigned char *p) {
    unsigned short crc = console_crc(p);
    p[14] = (unsigned char)crc; p[15] = (unsigned char)(crc >> 8);
}
static inline unsigned char parallel_session_valid(const unsigned char *p) {
    unsigned short crc = console_crc(p);
    return p[0]=='E' && p[1]=='X' && p[2]==PARALLEL_WIRE_VERSION &&
        p[12]==PARALLEL_EXEXT && !p[13] && parallel_nonzero(p+4) &&
        p[14]==(unsigned char)crc && p[15]==(unsigned char)(crc>>8);
}
static inline unsigned char parallel_session_begin(t_parallelSession *s,
    const unsigned char *transaction, unsigned char *request) {
    if (!parallel_nonzero(transaction) ||
        (s->phase != PARALLEL_SESSION_IDLE && s->phase != PARALLEL_SESSION_ACTIVE)) return 0;
    parallel_session_invalidate(s);
    memcpy(s->transaction,transaction,4);
    memset(request,0,16);
    request[0]='E'; request[1]='X'; request[2]=PARALLEL_WIRE_VERSION;
    request[3]=PARALLEL_PREPARE; request[12]=PARALLEL_EXEXT;
    memcpy(request+4,transaction,4); parallel_session_seal(request);
    s->phase=PARALLEL_SESSION_PREPARING;
    return 1;
}
static inline unsigned char parallel_session_accept(t_parallelSession *s,
    const unsigned char *reply, unsigned char *commit) {
    if (!parallel_session_valid(reply) || memcmp(reply+4,s->transaction,4)) return 0;
    if (s->phase==PARALLEL_SESSION_PREPARING && reply[3]==(PARALLEL_PREPARE|0x80)) {
        if (!parallel_nonzero(reply+8) || !memcmp(reply+8,s->bytes,4)) return 0;
        memcpy(s->bytes,reply+8,4);
        /* The console owner may reuse its request/reply buffer in place. */
        if (commit != reply) memcpy(commit,reply,16);
        commit[3]=PARALLEL_COMMIT; parallel_session_seal(commit);
        s->phase=PARALLEL_SESSION_COMMITTING;
    } else if (s->phase==PARALLEL_SESSION_COMMITTING && reply[3]==(PARALLEL_COMMIT|0x80) &&
               !memcmp(reply+8,s->bytes,4)) s->phase=PARALLEL_SESSION_ACTIVE;
    else return 0;
    return s->phase;
}
static inline unsigned char parallel_session_peer(t_parallelSession *s,
    const unsigned char *request, const unsigned char *nonce, unsigned char *reply) {
    if (!parallel_session_valid(request)) return 0;
    if (request[3]==PARALLEL_PREPARE) {
        if (parallel_nonzero(request+8) || !parallel_nonzero(nonce) ||
            !memcmp(nonce,s->bytes,4)) return 0;
        parallel_session_invalidate(s);
        memcpy(s->transaction,request+4,4); memcpy(s->bytes,nonce,4);
        s->phase=PARALLEL_SESSION_STAGED;
    } else if (request[3]==PARALLEL_COMMIT && s->phase==PARALLEL_SESSION_STAGED &&
               !memcmp(request+4,s->transaction,4) && !memcmp(request+8,s->bytes,4))
        s->phase=PARALLEL_SESSION_ACTIVE;
    else return 0;
    memcpy(reply,request,16); memcpy(reply+8,s->bytes,4);
    reply[3]|=0x80; parallel_session_seal(reply);
    return 1;
}
#endif
