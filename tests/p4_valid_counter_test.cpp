#include "extender/transport/p4_valid_counter.hpp"
#include <cassert>
#include <iostream>
using Counter=agon::extender::transport::P4ValidCounter;
static int core,level=1,op,failAt=-1,raw,accum,stopEdges,unitDeletes;
static bool gated,clockHigh=true;
static bool unitLive,channelLive,enabled,running,watchpoint,cleared,pendingOverflow,deliverIrq=true,partialDelete;
static bool fails(){return op++==failAt;}
int xPortGetCoreID(){return core;}
int gpio_get_level(int pin){assert(pin==16);return level;}
int gpio_pullup_dis(int pin){assert(pin==16||pin==14);return fails()?ESP_FAIL:ESP_OK;}
int gpio_pulldown_dis(int pin){assert(pin==16||pin==14);return fails()?ESP_FAIL:ESP_OK;}
int pcnt_new_unit(const pcnt_unit_config_t*c,void**out){
 assert(!unitLive&&c->low_limit==-32768&&c->high_limit==32767&&c->flags.accum_count);
 if(fails())return ESP_FAIL;
 unitLive=true;raw=7;*out=(void*)1;return ESP_OK;
}
int pcnt_new_channel(void*u,const pcnt_chan_config_t*c,void**out){
 assert(u==(void*)1&&unitLive&&!channelLive&&!enabled);
 gated=c->edge_gpio_num==14;
 assert((gated&&c->level_gpio_num==16)||(!gated&&c->edge_gpio_num==16&&c->level_gpio_num==-1));
 if(fails())return ESP_FAIL;
 channelLive=true;*out=(void*)2;return ESP_OK;
}
int pcnt_channel_set_edge_action(void*c,int p,int n){assert(c==(void*)2&&p==(gated?0:1)&&n==1);return fails()?ESP_FAIL:ESP_OK;}
int pcnt_channel_set_level_action(void*c,int h,int l){assert(c==(void*)2&&h==(gated?2:0)&&!l);return fails()?ESP_FAIL:ESP_OK;}
int pcnt_unit_add_watch_point(void*u,int n){assert(u==(void*)1&&n==32767&&!enabled);if(fails())return ESP_FAIL;watchpoint=true;return ESP_OK;}
int pcnt_unit_enable(void*u){assert(u==(void*)1&&unitLive&&!enabled&&watchpoint);if(fails())return ESP_FAIL;enabled=true;return ESP_OK;}
int pcnt_unit_clear_count(void*u){assert(u==(void*)1&&enabled&&!running&&watchpoint);if(fails())return ESP_FAIL;raw=accum=0;pendingOverflow=false;cleared=true;return ESP_OK;}
int pcnt_unit_start(void*u){assert(u==(void*)1&&enabled&&!running&&cleared&&level==1);if(fails())return ESP_FAIL;running=true;return ESP_OK;}
static void increment(){if(++raw==32767){raw=0;if(deliverIrq)accum+=32767;else pendingOverflow=true;}}
static void pulse(){assert(running&&!gated);level=!level;increment();}
static void clockEdge(bool high){assert(running&&gated);if(clockHigh&&!high&&!level)increment();clockHigh=high;}
static void qualifiedClock(){clockEdge(false);clockEdge(true);}
int pcnt_unit_get_count(void*u,int*out){
 assert(u==(void*)1&&unitLive&&enabled);
 if(fails())return ESP_FAIL;
 // Pinned driver's pending high-limit compensation, including its midpoint guard.
 *out=raw+accum+(pendingOverflow&&raw<=32767/2?32767:0);return ESP_OK;
}
int pcnt_unit_stop(void*u){assert(u==(void*)1&&enabled&&running);if(fails())return ESP_FAIL;while(stopEdges-->0){if(gated)increment();else pulse();}stopEdges=0;running=false;return ESP_OK;}
int pcnt_unit_disable(void*u){assert(u==(void*)1&&enabled&&!running);if(fails())return ESP_FAIL;enabled=false;return ESP_OK;}
int pcnt_del_channel(void*c){assert(c==(void*)2&&channelLive&&!enabled);if(fails())return ESP_FAIL;channelLive=false;return ESP_OK;}
int pcnt_del_unit(void*u){assert(u==(void*)1&&unitLive&&!channelLive&&!enabled&&!partialDelete);++unitDeletes;if(fails()){partialDelete=true;return ESP_FAIL;}unitLive=false;return ESP_OK;}
static void reset(){assert(!unitLive&&!channelLive&&!enabled&&!running);core=0;level=1;op=0;failAt=-1;raw=accum=stopEdges=unitDeletes=0;watchpoint=cleared=pendingOverflow=partialDelete=false;deliverIrq=true;gated=false;clockHigh=true;}
int main(){unsigned cases=0;
 reset();{
  Counter c(16,0);int before=op;core=1;assert(!c.begin()&&op==before);core=0;
  level=0;assert(!c.begin()&&op==before);level=1;assert(c.begin());
  assert(!c.sample(true).ended);pulse();auto p=c.sample(true);assert(p.started&&!p.ended&&!p.failed);
  pulse();p=c.sample(false);assert(p.started&&!p.ended&&!p.failed&&running);
  p=c.sample(true);assert(p.started&&p.ended&&!p.failed&&!running);
  assert(c.cleanup()&&unitDeletes==1);++cases;
 }
 for(int count:{0,1,3,4}){
  reset();Counter c(16,0);assert(c.begin());for(int i=0;i<count;++i)pulse();
  auto p=c.sample(true);assert(!p.ended);assert(p.failed==(count>2));
  if(count>2){raw=2;level=1;assert(c.sample(true).failed);} // sticky rejection
  assert(c.cleanup());++cases;
 }
 for(int count:{32769,65536})for(bool irq:{false,true}){
  reset();Counter c(16,0);assert(c.begin());deliverIrq=irq;for(int i=0;i<count;++i)pulse();
  assert(raw==2&&c.sample(true).failed);assert(c.cleanup());++cases;
 }
 for(int extra:{1,2}){
  reset();Counter c(16,0);assert(c.begin());pulse();pulse();stopEdges=extra;
  assert(c.sample(true).failed);assert(c.cleanup());++cases;
 }
 // Count2 with low VALID cannot be a complete high-to-low-to-high record.
 reset();{Counter c(16,0);assert(c.begin());pulse();pulse();level=0;assert(c.sample(true).failed);assert(c.cleanup());++cases;}
 // Gated CLOCK counts only falling edges while VALID is active low.
 for(unsigned n:{1,2,3,7,255,256,257,1024,4095,4096}){
  reset();Counter c(16,0);assert(c.beginClock(14,n));
  for(int i=0;i<16;++i){qualifiedClock();}assert(raw==0); // inactive EOF/handshake clocks
  level=0;for(unsigned i=0;i<n;++i){qualifiedClock();}assert(raw==int(n));
  auto p=c.sample(true);assert(!p.failed&&p.started&&!p.ended&&running); // exact N, VALID still low
  level=1;p=c.sample(false);assert(!p.failed&&!p.ended&&running); // wait actual DMA completion
  p=c.sample(true);assert(!p.failed&&p.started&&p.ended&&!running);
  assert(c.cleanup());++cases;
 }
 reset();{
  Counter c(16,0);int before=op;
  assert(!c.beginClock(-1,1)&&!c.beginClock(16,1)&&!c.beginClock(14,0)&&!c.beginClock(14,4097));
  assert(op==before);core=1;assert(!c.beginClock(14,1)&&op==before);core=0;
  level=0;assert(!c.beginClock(14,1)&&op==before);level=1;
  assert(c.beginClock(14,1));assert(c.cleanup());++cases;
 }
 for(unsigned n:{1,4096}){
  reset();Counter c(16,0);assert(c.beginClock(14,n));level=0;
  for(unsigned i=0;i<n-1;++i){qualifiedClock();}level=1;
  auto p=c.sample(true);assert(!p.failed&&!p.ended&&running);assert(c.cleanup());++cases;
  reset();Counter extra(16,0);assert(extra.beginClock(14,n));level=0;
  for(unsigned i=0;i<n+1;++i){qualifiedClock();}level=1;
  assert(extra.sample(true).failed);raw=n;assert(extra.sample(true).failed);assert(extra.cleanup());++cases;
 }
 for(unsigned n:{1,4096})for(bool irq:{false,true}){
  reset();Counter c(16,0);assert(c.beginClock(14,n));deliverIrq=irq;level=0;
  for(unsigned i=0;i<32767+n;++i){qualifiedClock();}level=1;
  assert(raw==int(n)&&c.sample(true).failed);assert(c.cleanup());++cases;
 }
 for(int late:{1,2}){
  reset();Counter c(16,0);assert(c.beginClock(14,1));level=0;qualifiedClock();level=1;stopEdges=late;
  assert(c.sample(true).failed);assert(c.cleanup());++cases;
 }
 reset();{Counter c(16,0);assert(c.beginClock(14,1));raw=-1;assert(c.sample(true).failed);assert(c.cleanup());++cases;}
 // Fail every start/sample/cleanup SDK operation, preserving partial resources.
 reset();int total;
 {Counter c(16,0);assert(c.begin());pulse();pulse();assert(c.sample(true).ended);assert(c.cleanup());total=op;}
 for(int failure=0;failure<total;++failure){
  reset();Counter c(16,0);failAt=failure;
  if(c.begin()){pulse();pulse();c.sample(true);}
  bool cleaned=c.cleanup();failAt=-1;
  if(partialDelete){
   assert(!cleaned);int before=op,deletes=unitDeletes;assert(!c.cleanup()&&op==before&&unitDeletes==deletes);
   // Model the required whole-board reset after a partial SDK destruction.
   unitLive=false;partialDelete=false;
  }else assert(cleaned||c.cleanup());
  assert(!unitLive&&!channelLive&&!enabled&&!running);++cases;
 }
 reset();
 {Counter c(16,0);assert(c.beginClock(14,1));level=0;qualifiedClock();level=1;assert(c.sample(true).ended);assert(c.cleanup());total=op;}
 for(int failure=0;failure<total;++failure){
  reset();Counter c(16,0);failAt=failure;
  if(c.beginClock(14,1)){level=0;qualifiedClock();level=1;c.sample(true);}
  bool cleaned=c.cleanup();failAt=-1;
  if(partialDelete){
   assert(!cleaned);int before=op,deletes=unitDeletes;assert(!c.cleanup()&&op==before&&unitDeletes==deletes);
   unitLive=false;partialDelete=false;
  }else assert(cleaned||c.cleanup());
  assert(!unitLive&&!channelLive&&!enabled&&!running);++cases;
 }
 reset();std::cout<<"PASS "<<cases<<" PCNT VALID/CLOCK cases; qualified falling-edge count, exact length while VALID low, wrap/pending ISR, capture stop races, sticky faults and retained cleanup failure\n";
}
