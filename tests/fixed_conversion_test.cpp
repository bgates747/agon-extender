#include "extender/port/fixed_conversion.hpp"
#include <cassert>
#include <cmath>
#include <cstdint>
#include <limits>
#include <iostream>
using agon::extender::port::encodeFixed;
static unsigned checks;
static void good(float input,bool width,int shift,std::uint32_t expected){
    std::uint32_t out=0x12345678;assert(encodeFixed(input,width,shift,out));
    assert(out==expected);++checks;
}
static void bad(float input,bool width,int shift){
    std::uint32_t out=0x12345678;assert(!encodeFixed(input,width,shift,out));
    assert(out==0x12345678);++checks;
}
int main(){
    for(bool width:{false,true}){
        good(0,width,0,0);good(-0.0f,width,0,0);
        good(-0.9f,width,0,0);good(0.9f,width,0,0);
        good(-1.9f,width,0,width?65535u:0xffffffffu);
        good(1.9f,width,0,1);good(-12.25f,width,2,width?65487u:0xffffffcfu);
        good(-49.0f,width,-2,width?65524u:0xfffffff4u);
        bad(std::numeric_limits<float>::quiet_NaN(),width,0);
        bad(std::numeric_limits<float>::infinity(),width,0);
        bad(-std::numeric_limits<float>::infinity(),width,0);
        bad(std::numeric_limits<float>::max(),width,31);
        good(std::numeric_limits<float>::denorm_min(),width,0,0);
    }
    good(-32768,true,0,32768);good(32767,true,0,32767);
    good(-32768.5f,true,0,32768);good(32767.5f,true,0,32767);
    bad(-32769,true,0);bad(32768,true,0);
    good(-2147483648.0f,false,0,0x80000000u);
    good(std::nextafter(2147483648.0f,0.0f),false,0,0x7fffff80u);
    bad(2147483648.0f,false,0);bad(std::nextafter(-2147483648.0f,-INFINITY),false,0);
    for(int shift=-32;shift<=31;++shift){
        good(std::ldexp(-123.0f,-shift),true,shift,65413);
        good(std::ldexp(123.0f,-shift),true,shift,123);
        good(std::ldexp(-123456.0f,-shift),false,shift,0xfffe1dc0u);
    }
    // Exhaustive signed16 integer domain, with an independent integer oracle.
    for(int value=-32768;value<=32767;++value)
        good(static_cast<float>(value),true,0,static_cast<std::uint16_t>(value));
    std::cout<<checks<<" conversion checks passed\n";
}
