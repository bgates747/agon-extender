// Observable lifecycle transitions, including fallback and uncertain cleanup.
#include "mode_lifecycle.hpp"
#include <cassert>
#include <vector>
using test_appliance::Mode;
const Mode cli{0,640,480,16},test{8,320,240,64};
struct IO {
    Mode current=cli;
    std::vector<unsigned> selected;
    unsigned queries=0,waits=0,cleanups=0,fail_query=0;
    bool fallback=false,select_ok=true,wait_ok=true;
    bool query(Mode &out){if(++queries==fail_query)return false;out=current;return true;}
    bool cli_supported(const Mode &m){return m.number<128;}
    bool select(unsigned n){selected.push_back(n);current=n==0?cli:test;
        if(fallback&&n==8)current={3,640,240,64};
        return select_ok;}
    bool settle(){++waits;return wait_ok;}
    bool prepare_cli(){++cleanups;return true;}
};
int main(){
    {IO io;io.current=test;test_appliance::ModeSession<IO> s(io);
     assert(s.begin(test));assert(s.restore());assert(s.restore());
     assert(io.selected.empty()&&io.waits==0&&io.queries==2&&io.cleanups==1);}
    {IO io;test_appliance::ModeSession<IO> s(io);assert(s.begin(test));
     assert(io.current==test&&io.waits==1);assert(s.restore());
     assert(io.current==cli&&io.waits==2&&io.selected==std::vector<unsigned>({8,0}));}
    {IO io;io.fallback=true;test_appliance::ModeSession<IO> s(io);
     assert(!s.begin(test));assert(s.restore());assert(io.current==cli&&io.waits==1);}
    {IO io;io.fail_query=2;test_appliance::ModeSession<IO> s(io);
     assert(!s.begin(test));assert(s.restore());assert(io.current==cli);}
    {IO io;io.current={136,320,240,64};test_appliance::ModeSession<IO> s(io);
     assert(!s.begin(test));assert(s.restore());assert(io.selected.empty()&&io.cleanups==0);}
    {IO io;{test_appliance::ModeSession<IO> s(io);assert(s.begin(test));}
     assert(io.current==cli&&io.waits==2&&io.cleanups==1);}
    {IO io;test_appliance::ModeSession<IO> s(io);assert(s.begin(test));io.fail_query=3;
     assert(!s.restore());assert(!s.restore());assert(io.cleanups==0&&io.selected.size()==1);}
    {IO io;io.wait_ok=false;test_appliance::ModeSession<IO> s(io);
     assert(!s.begin(test));io.wait_ok=true;assert(s.restore());assert(io.current==cli);}
    {IO io;test_appliance::ModeSession<IO> s(io);
     assert(!s.begin({8,640,240,64}));assert(s.restore());assert(io.current==cli);}
}
