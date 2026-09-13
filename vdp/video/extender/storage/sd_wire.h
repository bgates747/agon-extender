/* PORT-017 v1 byte codec. Shared reviewed copy for the eZ80 foreground agent.
 * No allocation, alignment assumptions, device calls or native struct wire ABI.
 */
#ifndef EXTENDER_SD_WIRE_H
#define EXTENDER_SD_WIRE_H
#include <stdint.h>
#include <stddef.h>
#define SD_HEADER 20
#define SD_MAX_RECORD 240
#define SD_MAX_PAYLOAD 220
#define SD_REQUEST 1
#define SD_RESPONSE 2
#define SD_PRESENCE 3
enum sd_operation { SD_HELLO=1, SD_STAT, SD_LIST, SD_READ, SD_BEGIN,
    SD_WRITE, SD_FINISH, SD_ACTIVATE, SD_CANCEL, SD_RECOVER, SD_EXIT };
enum sd_status { SD_OK=0, SD_BAD_REQUEST, SD_UNSUPPORTED, SD_BUSY, SD_STALE,
    SD_SEQUENCE, SD_FILE_ERROR, SD_INTEGRITY, SD_RECOVERY_REQUIRED };
static inline uint16_t sd_u16(const uint8_t *p) {
    return (uint16_t)p[0] | ((uint16_t)p[1]<<8);
}
static inline uint32_t sd_u32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1]<<8) |
        ((uint32_t)p[2]<<16) | ((uint32_t)p[3]<<24);
}
static inline void sd_put16(uint8_t *p,uint16_t n) { p[0]=n; p[1]=n>>8; }
static inline void sd_put32(uint8_t *p,uint32_t n) {
    p[0]=n; p[1]=n>>8; p[2]=n>>16; p[3]=n>>24;
}
static inline uint32_t sd_crc_update(uint32_t crc,const uint8_t *p,size_t n) {
    while(n--) {
        unsigned b; crc^=*p++;
        for(b=0;b<8;++b) crc=(crc>>1)^((crc&1)?UINT32_C(0xedb88320):0);
    }
    return crc;
}
static inline uint32_t sd_crc(const uint8_t *p,size_t n) {
    return sd_crc_update(UINT32_C(0xffffffff),p,n)^UINT32_C(0xffffffff);
}
static inline void sd_seal(uint8_t *p) {
    uint32_t c=sd_crc_update(UINT32_C(0xffffffff),p,16);
    c=sd_crc_update(c,p+SD_HEADER,sd_u16(p+14));
    sd_put32(p+16,c^UINT32_C(0xffffffff));
}
static inline int sd_valid(const uint8_t *p,size_t n) {
    uint32_t c;
    if(n<SD_HEADER || n>SD_MAX_RECORD || p[0]!='S' || p[1]!='D' || p[2]!=1 ||
        p[3]<SD_REQUEST || p[3]>SD_PRESENCE || sd_u16(p+14)!=n-SD_HEADER ||
        sd_u32(p+4)==0) return 0;
    c=sd_crc_update(UINT32_C(0xffffffff),p,16);
    c=sd_crc_update(c,p+SD_HEADER,n-SD_HEADER)^UINT32_C(0xffffffff);
    return sd_u32(p+16)==c;
}
static inline void sd_header(uint8_t *p,uint8_t kind,uint32_t session,
                             uint32_t sequence,uint8_t op,uint8_t status,uint16_t n) {
    p[0]='S';p[1]='D';p[2]=1;p[3]=kind;
    sd_put32(p+4,session);sd_put32(p+8,sequence);p[12]=op;p[13]=status;
    sd_put16(p+14,n);
}
#endif
