/* Experimental foreground lifecycle. IRQ marker is native assembly only.
 * New implementation from PRT1 register contracts; no resident MOS address,
 * direct UART/GPIO access or borrowed profiler scratch. No target execution
 * qualification follows from compiling this file.
 */
#include "observer.h"
#include <string.h>
#ifndef __ez80__
#error "Observer requires the eZ80 app toolchain"
#endif
volatile uint8_t agon_rxdiag_record[128];
volatile uint8_t agon_rxdiag_next_epoch[4],agon_rxdiag_ready[3];
extern int agon_rxdiag_claim(void),agon_rxdiag_prepare(void);
extern int agon_rxdiag_publish(void),agon_rxdiag_enabled(void);
extern void agon_rxdiag_ready_sample(void),agon_rxdiag_retire(void);
static uint32_t last_epoch;
static uint8_t owned,initialized,admitted_once;
int agon_rxdiag_init(void){
 if(initialized)return 0;
 /* Pure app storage, for NULL-marker controls too. Must precede OPEN. */
 memset((void*)agon_rxdiag_record,0,128);
 memcpy((void*)agon_rxdiag_record,"MGIRQ001",8);
 agon_rxdiag_record[8]=2;agon_rxdiag_record[10]=128;
 agon_rxdiag_record[12]=ARD_PARTIAL;
 agon_rxdiag_record[24]=0x40;agon_rxdiag_record[25]=0x19;
 agon_rxdiag_record[26]=1;
 agon_rxdiag_record[30]=0x0d;
 initialized=1;return 1;
}
int agon_rxdiag_admit(void){
 if(owned||admitted_once||!agon_rxdiag_enabled())return 0;
 if(!initialized&&!agon_rxdiag_init())return 0;
 if(!agon_rxdiag_claim())return 0;
 agon_rxdiag_record[12]|=ARD_ADMITTED;
 last_epoch=0;owned=1;admitted_once=1;return 1;
}
int agon_rxdiag_rearm(uint32_t epoch,uint8_t no_live_source){
 if(!owned||!no_live_source||!epoch||epoch<=last_epoch||
    !agon_rxdiag_enabled()||!agon_rxdiag_prepare())return 0;
 /* Interrupts stay enabled throughout this bounded readiness loop. */
 for(unsigned i=0;i<256;++i){
  agon_rxdiag_ready_sample();
  if((agon_rxdiag_ready[0]||agon_rxdiag_ready[1])&&agon_rxdiag_ready[2]==0x0d){
   for(unsigned j=0;j<4;++j)agon_rxdiag_next_epoch[j]=(uint8_t)(epoch>>(8*j));
   if(agon_rxdiag_publish()){last_epoch=epoch;return 1;}
   break;
  }
  if(agon_rxdiag_ready[2]!=0x0d&&agon_rxdiag_ready[2]!=0x0f)break;
 }
 /* Keep first-error association/record, but exclude this unusable clock. */
 agon_rxdiag_retire();owned=0;return 0;
}
void agon_rxdiag_stop(void){
 if(owned){agon_rxdiag_retire();owned=0;}
}
