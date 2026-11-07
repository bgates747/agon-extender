/* Actual observer.c foreground lifecycle under independently controlled native
 * leaves. No claim of executing an IRQ or emulating the timer instructions. */
#include <assert.h>
#include <stdlib.h>
#include "observer.h"
extern volatile uint8_t agon_rxdiag_ready[3];
static unsigned claims,prepares,publishes,retires,reads;
static int ready_mode,clock_claim=1,publish_ok=1;
int agon_rxdiag_enabled(void){return 1;}
int agon_rxdiag_claim(void){++claims;return clock_claim;}
int agon_rxdiag_prepare(void){++prepares;return 1;}
int agon_rxdiag_publish(void){++publishes;return publish_ok;}
void agon_rxdiag_ready_sample(void){
 ++reads;agon_rxdiag_ready[0]=ready_mode?0:123;
 agon_rxdiag_ready[1]=0;agon_rxdiag_ready[2]=0x0d;
}
void agon_rxdiag_retire(void){++retires;}
int main(int argc,char**argv){
 assert(argc==2);int test=atoi(argv[1]);
 if(test==0){
  assert(agon_rxdiag_init());assert(!claims&&!reads&&!retires);
  agon_rxdiag_record[80]=2;assert(!agon_rxdiag_init());
  assert(agon_rxdiag_record[80]==2);return 0;
 }
 if(test==1){clock_claim=0;assert(!agon_rxdiag_admit());assert(claims==1);return 0;}
 assert(agon_rxdiag_admit());assert(agon_rxdiag_record[8]==2);
 assert(!agon_rxdiag_admit());assert(!agon_rxdiag_init());assert(claims==1);
 if(test==2){
  assert(!agon_rxdiag_rearm(0,1));assert(!agon_rxdiag_rearm(1,0));
  assert(!prepares);assert(agon_rxdiag_rearm(1,1));
  assert(!agon_rxdiag_rearm(1,1));assert(prepares==1);return 0;
 }
 if(test==3)ready_mode=1;
 if(test==4)publish_ok=0;
 if(test==3||test==4){
  assert(!agon_rxdiag_rearm(1,1));assert(retires==1);
  assert(reads==(test==3?256:1));
  assert(!agon_rxdiag_rearm(2,1));assert(!agon_rxdiag_admit());
  assert(claims==1&&prepares==1);return 0;
 }
 assert(test==5);assert(agon_rxdiag_rearm(1,1));
 agon_rxdiag_record[80]=2;agon_rxdiag_stop();agon_rxdiag_stop();
 assert(retires==1&&agon_rxdiag_record[80]==2);
 assert(!agon_rxdiag_rearm(2,1));assert(!agon_rxdiag_admit());
 return 0;
}
