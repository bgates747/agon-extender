#include "extender/diagnostics/row_priority.hpp"
#include <cassert>
#include <vector>
struct Runtime {
 static inline unsigned value=2;
 static inline std::vector<unsigned> changes;
 static unsigned get(){return value;}
 static void set(unsigned p){value=p;changes.push_back(p);}
 static void require(bool ok){assert(ok);}
};
using Guard=agon_row_priority::Ceiling<Runtime>;
static void early(){Guard outer(true);assert(Runtime::value==19);{Guard nested(true);assert(Runtime::changes.size()==1);}assert(Runtime::value==19);return;}
int main(){
 {Guard off(false);assert(Runtime::value==2);}assert(Runtime::changes.empty());
 early();assert(Runtime::value==2);assert((Runtime::changes==std::vector<unsigned>{19,2}));
 Runtime::changes.clear();
 try {Guard g(true);throw 1;}catch(int){}
 assert(Runtime::value==2);assert((Runtime::changes==std::vector<unsigned>{19,2}));
}
