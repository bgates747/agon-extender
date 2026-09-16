#define NP_TRACE_HOST
#define AGON_EXTENDER_LOCK_WAKE_TRACE
#include "extender/diagnostics/lock_wake_trace.hpp"
#include <cassert>
int main(){using namespace agon_lock_wake;uint8_t n[8]={'P','0','2',0,1,0,0,0};assert(begin(n));Ticket a,b;a.enter();a.acquired();b.enter();b.acquired();b.released();a.released();assert(totals[0].count==1&&totals[1].count==1);assert(in_flight==0&&depths[0]==0);assert(!begin(n));notify(0);entered(0);assert(totals[6].count==1);active=false;n[4]=0;assert(begin(n));Ticket off;off.enter();off.acquired();off.released();assert(totals[0].count==0);n[4]=1;assert(begin(n));Ticket held;held.enter();held.acquired();active=false;assert(!begin(n));held.released();assert(in_flight==0);assert(begin(n));}
