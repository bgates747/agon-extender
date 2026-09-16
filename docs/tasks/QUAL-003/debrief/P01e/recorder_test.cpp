#define NP_TRACE_HOST
#define AGON_EXTENDER_OWNER_TRACE
#include "extender/diagnostics/owner_trace.hpp"
#include <cassert>
int main(){using namespace agon_owner_trace;uint8_t n[8]={'P','0','2',0,0,0,0,0};registerOutput();assert(begin(n));Ticket off;off.enter();off.acquired();off.beforeRelease();off.afterRelease();assert(!holds);switched(0,1,task(),"test",3);assert(!rings[0].count);
 n[4]=1;assert(begin(n));for(unsigned i=0;i<600;++i)switched(0,i%2,task(),"test",3);assert(rings[0].count==600);assert(rings[0].events[599%Capacity].kind==1);assert(!begin(n));
 Ticket a,b;a.enter();a.acquired();b.enter();b.acquired();b.beforeRelease();b.afterRelease();assert(!holds&&in_flight==1);a.start=now()-9000;a.beforeRelease();assert(trigger.fired&&!recording);a.afterRelease();assert(holds==1&&max_hold>=9000&&!in_flight);switched(0,1,task(),"test",3);assert(rings[0].count==600);enabled=false;assert(begin(n));assert(!trigger.fired&&!rings[0].count);
}
