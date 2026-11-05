/* NET-003 matched development endpoint. No CRC/checksum, peripheral access or
 * game semantics. Canonical bytes are mirrored into EMOS and the C app include. */
#ifndef AGON_NET_WIRE_H
#define AGON_NET_WIRE_H
#include <stdint.h>
#define AGON_NET_VERSION 1
#define AGON_NET_VDU 0xF4
#define AGON_NET_REPLY 0x8F
#define AGON_NET_HEADER 14
#define AGON_NET_PAYLOAD 128
#define AGON_NET_BODY 142
#define AGON_NET_INPUT 147
#define AGON_NET_CONNECT 1
#define AGON_NET_POLL 2
#define AGON_NET_SEND 3
#define AGON_NET_CONNECTED 0
#define AGON_NET_CONNECTING 1
#define AGON_NET_RECEIVED 2
#define AGON_NET_ACCEPTED 3
#define AGON_NET_BUSY 4
#define AGON_NET_FAULT 5
#define AGON_NET_CLOSED 6
#define AGON_NET_INVALID 7
#define AGON_NET_LOCAL_OPEN 0
#define AGON_NET_LOCAL_TAKE 1
#define AGON_NET_LOCAL_SUBMIT 2
#define AGON_NET_LOCAL_RELEASE 3
/* Stable generic fault payload; socket errno stays in P4 diagnostics. */
#define AGON_NET_PEER_CLOSED 1
#define AGON_NET_CONNECT_FAILED 2
#define AGON_NET_CONNECT_TIMEOUT 3
#define AGON_NET_BAD_FRAME 4
#define AGON_NET_IO_FAILED 5
#define AGON_NET_LEASE_EXPIRED 6
static inline uint32_t agon_net_u32(const uint8_t*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static inline void agon_net_put32(uint8_t*p,uint32_t v){p[0]=v;p[1]=v>>8;p[2]=v>>16;p[3]=v>>24;}
#endif
