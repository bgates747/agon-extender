/* Actual accounting.c lifecycle; timer/native entries are explicit stubs. */
#include <assert.h>
#include <stdlib.h>
#include "accounting.h"
static int provider_ok=1,rearm_ok=1;static unsigned retired,arms,starts;
int agon_rxdiag_init(void){return 1;}
int agon_rxdiag_admit(void){return provider_ok;}
int agon_rxdiag_rearm(uint32_t epoch,uint8_t quiet){assert(epoch&&quiet);++arms;return rearm_ok;}
void agon_rxdiag_stop(void){++retired;}
void agon_cpu_start_native(void){++starts;agon_cpu_record[ACP_ACTIVE]=1;}
void agon_cpu_stop_native(void){agon_cpu_record[ACP_ACTIVE]=0;agon_cpu_record[ACP_STOPPED]=1;}
int main(int argc,char**argv){
 assert(argc==2);int n=atoi(argv[1]);unsigned char out[AGON_CPU_BYTES];
 assert(!agon_cpu_admit());assert(agon_cpu_init());assert(!agon_cpu_init());
 if(n==0){provider_ok=0;assert(!agon_cpu_admit());return 0;}
 assert(agon_cpu_admit());assert(!agon_cpu_admit());
 assert(!agon_cpu_start(0,1,1));assert(!agon_cpu_start(1,0,1));assert(!agon_cpu_start(1,1,0));assert(!arms);
 if(n==1){agon_cpu_record[ACP_POISON]=1;assert(!agon_cpu_start(1,1,1));return 0;}
 if(n==2){rearm_ok=0;assert(!agon_cpu_start(1,1,1));assert(!starts);agon_cpu_stop();assert(retired==1);return 0;}
 assert(agon_cpu_start(0x12345678,1,1));assert(arms==1&&starts==1);assert(!agon_cpu_start(2,1,1));
 assert(!agon_cpu_snapshot(out,1));
 if(n==3){agon_cpu_record[ACP_ACTIVE]=0;assert(!agon_cpu_snapshot(out,1));return 0;} /* reset/incomplete */
 agon_cpu_stop();assert(retired==1);assert(!agon_cpu_snapshot(out,0));
 if(n==4)agon_cpu_record[ACP_POISON]=1;
 if(n==5)agon_cpu_record[ACP_FLAGS]|=ACP_CLOCK_INVALID;
 if(n==6)agon_cpu_record[ACP_FLAGS]|=ACP_CONTEXT_INVALID;
 if(n==7)agon_cpu_record[ACP_FLAGS]|=ACP_OVERFLOW;
 assert(agon_cpu_snapshot(out,1)==(n==8));
 if(n==8){assert(out[8]==1&&out[10]==96&&out[16]==0x78&&out[19]==0x12);assert(out[12]==3);}
 agon_cpu_stop();assert(retired==1);return 0;
}
