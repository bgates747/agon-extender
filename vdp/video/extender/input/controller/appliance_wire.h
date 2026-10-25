/* Developmental EMOS/application controller carrier. Mirrored by the EMOS
 * candidate; no MOS API slot, SD lease or keyboard payload is repurposed.
 * CI requests use the existing F7/16 Extender control envelope; replies use
 * Extender-local UART1 type8E. See the INPUT-001 candidate contract. */
#ifndef EXT_CONTROLLER_APPLIANCE_WIRE_H
#define EXT_CONTROLLER_APPLIANCE_WIRE_H
#define CONTROLLER_REPLY 0x8E
#define CONTROLLER_RESULT_SIZE 98
#define CONTROLLER_BATCH 8
static unsigned short controller_crc(const unsigned char *p,unsigned n) {
    unsigned int value=0xffff;
    unsigned bit;
    while(n--) {
        value^=(unsigned int)*p++<<8;
        for(bit=0;bit<8;++bit)value=(unsigned short)((value<<1)^((value&0x8000)?0x1021:0));
    }
    return (unsigned short)value;
}
static unsigned short controller_u16(const unsigned char*p){return p[0]|((unsigned short)p[1]<<8);}
static unsigned long controller_u32(const unsigned char*p){return (unsigned long)controller_u16(p)|((unsigned long)controller_u16(p+2)<<16);}
static void controller_put16(unsigned char*p,unsigned short v){p[0]=v;p[1]=v>>8;}
static void controller_put32(unsigned char*p,unsigned long v){controller_put16(p,v);controller_put16(p+2,v>>16);}
#endif
