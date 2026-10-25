/* Developmental EMOS/application controller carrier. Mirrored by the EMOS
 * candidate; no MOS API slot, SD lease or keyboard payload is repurposed.
 * CI requests use the existing F7/16 Extender control envelope; replies use
 * Extender-local UART1 type8E. Version2 removes the agent-added CRCs under
 * the Author's2026-10-25 instruction. The fixed carrier's last two bytes are
 * reserved zero; the result has no checksum trailer. See INPUT-001. */
#ifndef EXT_CONTROLLER_APPLIANCE_WIRE_H
#define EXT_CONTROLLER_APPLIANCE_WIRE_H
#define CONTROLLER_REPLY 0x8E
#define CONTROLLER_CARRIER_VERSION 2
#define CONTROLLER_RESULT_MAGIC "CIS2"
#define CONTROLLER_RESULT_SIZE 96
#define CONTROLLER_BATCH 8
static unsigned short controller_u16(const unsigned char*p){return p[0]|((unsigned short)p[1]<<8);}
static unsigned long controller_u32(const unsigned char*p){return (unsigned long)controller_u16(p)|((unsigned long)controller_u16(p+2)<<16);}
static void controller_put16(unsigned char*p,unsigned short v){p[0]=v;p[1]=v>>8;}
static void controller_put32(unsigned char*p,unsigned long v){controller_put16(p,v);controller_put16(p+2,v>>16);}
#endif
