// UART-DATA-PROBE-r01 only; include in the retained vdu_sys_video switch.
// No renderer changes. Production builds must not include this command.
case 0xEE: {
    int op=readByte_t(), token=readWord_t(), length=readWord_t(), pattern=readByte_t();
    if(op<1 || op>4 || token<0 || length<0 || pattern<0 || pattern>3) break;
    static uint16_t owner;
    static uint32_t started, elapsed, actual, errors, first_bad;
    static bool armed, checked;
    auto reply=[&](uint16_t id,uint8_t kind,uint32_t a,uint32_t b) {
        uint8_t p[16]={'Q','T','G',0xA1,uint8_t(id),uint8_t(id>>8),kind,
#if defined(AGON_EXTENDER_CONSOLE)
            1,
#else
            0,
#endif
            uint8_t(a),uint8_t(a>>8),uint8_t(a>>16),uint8_t(a>>24),
            uint8_t(b),uint8_t(b>>8),uint8_t(b>>16),uint8_t(b>>24)};
        send_packet(0x0C,sizeof p,p);
    };
    uint32_t state=0x12345678U,position=0;
    auto next=[&]() -> uint8_t {
        uint32_t i=position++;
        if(pattern==0)return 0;
        if(pattern==1)return 255;
        if(pattern==2)return (i&1)?0xAA:0x55;
        state^=state<<13;state^=state>>17;state^=state<<5;return uint8_t(state);
    };
    if(op==1) {
        owner=token;armed=true;checked=false;
        reply(token,0,length,pattern);started=micros();
    } else if(op==2 && armed && owner==token) {
        elapsed=uint32_t(micros()-started);armed=false;actual=errors=0;first_bad=0xFFFFFFFFU;
        auto found=buffers.find(64010);
        if(found!=buffers.end())for(auto const &block:found->second) {
            for(size_t i=0;i<block->size();++i) {
                uint8_t expected=next();
                if(actual>=unsigned(length) || block->getBuffer()[i]!=expected) {
                    ++errors;if(first_bad==0xFFFFFFFFU)first_bad=actual;
                }
                ++actual;
            }
        }
        if(actual!=unsigned(length)) {++errors;if(first_bad==0xFFFFFFFFU)first_bad=actual;}
        checked=true;reply(token,1,elapsed,actual);
    } else if(op==3 && checked && owner==token) {
        reply(token,2,errors,first_bad);
    } else if(op==4 && length>=1 && length<=256) {
        uint32_t start=micros();
        for(unsigned i=0;i<unsigned(length);++i) {
            uint32_t a=0,b=0;
            for(unsigned j=0;j<4;++j)a|=uint32_t(next())<<(8*j);
            for(unsigned j=0;j<4;++j)b|=uint32_t(next())<<(8*j);
            reply(i,96,a,b);
        }
        reply(token,3,uint32_t(micros()-start),length);
    }
} break;
