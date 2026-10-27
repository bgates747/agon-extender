// Pure lifecycle policy. IO owns fresh EMOS-routed queries and bounded waits.
// Double-buffered entry is gated: a final swap cannot make future CLI text live.
#pragma once
#include <stdint.h>
namespace test_appliance {
struct Mode {
    uint8_t number;
    uint16_t width,height;
    uint8_t colours;
    bool operator==(const Mode &other) const {
        return number==other.number&&width==other.width&&height==other.height&&colours==other.colours;
    }
    bool operator!=(const Mode &other) const {return !(*this==other);}
};
template<class IO> class ModeSession {
    IO &io;
    Mode entry{};
    bool captured=false,closed=false,cleanup_ok=true,attempted=false,settled=false;
 public:
    explicit ModeSession(IO &adapter):io(adapter) {}
    ModeSession(const ModeSession&)=delete;
    ModeSession& operator=(const ModeSession&)=delete;
    bool begin(const Mode &wanted) {
        if(captured||closed||!io.query(entry)||!io.cli_supported(entry))return false;
        captured=true;
        if(entry==wanted)return true;
        attempted=true;
        if(!io.select(wanted.number))return false;
        Mode actual{};
        if(!io.query(actual)||actual!=wanted)return false;
        return settled=io.settle();
    }
    bool restore() {
        if(closed)return cleanup_ok;
        closed=true;
        if(!captured)return cleanup_ok;
        Mode actual{};
        cleanup_ok=io.query(actual);
        if(cleanup_ok&&actual!=entry)
            cleanup_ok=io.select(entry.number)&&io.query(actual)&&actual==entry&&io.settle();
        else if(cleanup_ok&&attempted&&!settled)cleanup_ok=io.settle();
        if(cleanup_ok)cleanup_ok=io.prepare_cli();
        return cleanup_ok;
    }
    ~ModeSession(){restore();}
};
}
