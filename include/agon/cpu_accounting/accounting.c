#include "accounting.h"
#include "../rxdiag/observer.h"
#include <string.h>
volatile uint8_t agon_cpu_record[AGON_CPU_BYTES];
static uint8_t initialized,claimed,started;
extern void agon_cpu_start_native(void),agon_cpu_stop_native(void);
int agon_cpu_init(void){
 if(initialized)return 0;
 if(!agon_rxdiag_init())return 0;
 memset((void*)agon_cpu_record,0,AGON_CPU_BYTES);
 memcpy((void*)agon_cpu_record,"MGCPU001",8);
 agon_cpu_record[8]=1;agon_cpu_record[10]=AGON_CPU_BYTES;
 agon_cpu_record[ACP_FLAGS]=ACP_PARTIAL_BOUNDARIES|ACP_UNKNOWN_GAP;
 initialized=1;return 1;
}
int agon_cpu_admit(void){
 if(!initialized||claimed||!agon_rxdiag_admit())return 0;
 claimed=1;return 1;
}
int agon_cpu_start(uint32_t epoch,uint8_t u0,uint8_t u1){
 if(!claimed||started||!epoch||!u0||!u1||agon_cpu_record[ACP_POISON])return 0;
 if(!agon_rxdiag_rearm(epoch,1))return 0;
 for(unsigned i=0;i<4;++i)agon_cpu_record[ACP_EPOCH+i]=(uint8_t)(epoch>>(8*i));
 started=1;agon_cpu_start_native();return agon_cpu_record[ACP_ACTIVE]!=0;
}
void agon_cpu_stop(void){
 if(started)agon_cpu_stop_native();
 if(claimed){agon_rxdiag_stop();claimed=0;}
}
int agon_cpu_snapshot(uint8_t out[AGON_CPU_BYTES],uint8_t closed){
 if(!closed||claimed||!started||!agon_cpu_record[ACP_STOPPED]||
    agon_cpu_record[ACP_ACTIVE]||agon_cpu_record[ACP_POISON]||
    (agon_cpu_record[ACP_FLAGS]&~(ACP_PARTIAL_BOUNDARIES|ACP_UNKNOWN_GAP)))return 0;
 memcpy(out,(const void*)agon_cpu_record,AGON_CPU_BYTES);return 1;
}
