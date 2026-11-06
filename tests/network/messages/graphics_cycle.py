#!/usr/bin/env python3
"""Exercise the actual independent fixture leaf; no hardware or timing claim."""
from pathlib import Path
import os, subprocess, tempfile

ROOT=Path(__file__).resolve().parents[3]
s=(ROOT/'tests/fixtures/network/main.cpp').read_text()
begin=s.index('static uint8_t graphics_cycle(');brace=s.index('{',begin);end=brace+1;depth=1
while depth:
    if s[end]=='{':depth+=1
    elif s[end]=='}':depth-=1
    end+=1
leaf=s[begin:end]
support=r'''
#include <cassert>
#include <cstdint>
#include <cstring>
using uint24_t=uint32_t; // Host width, not native ABI or wrap qualification.
enum {sysvar_vdp_pflags,sysvar_scrMode,vdp_pflag_mode=16};
static uint8_t sysvars[2];static uint24_t graphics_ticks[4],now;
static unsigned calls,escape_calls;static bool fail_write,ready=true,cancel;
static uint8_t actual[32];static unsigned bytes;
static uint24_t ticks(){return now++;}
static bool escaped(){return cancel&&++escape_calls>1;}
static bool write_bytes(const uint8_t*p,unsigned n){
    ++calls;bytes=n;memcpy(actual,p,n);
    if(ready)sysvars[sysvar_vdp_pflags]|=vdp_pflag_mode;
    return !fail_write;
}
'''
checks=r'''
int main(){
    sysvars[sysvar_scrMode]=20;
    assert(graphics_cycle(0)==0&&calls==1&&bytes==18);
    const uint8_t expected[]={18,0,1,25,4,32,0,32,0,25,5,224,0,64,0,23,0,134};
    assert(!memcmp(actual,expected,sizeof(expected))&&graphics_ticks[0]>0);
    calls=0;assert(graphics_cycle(3)==0&&calls==1&&actual[2]==4&&actual[7]==128&&actual[13]==160);
    calls=0;fail_write=true;assert(graphics_cycle(0)==132&&calls==1);fail_write=false;
    calls=0;cancel=true;assert(graphics_cycle(0)==130&&calls==1);cancel=false;
    calls=0;ready=false;assert(graphics_cycle(0)==131&&calls==1);ready=true;
    calls=0;sysvars[sysvar_scrMode]=19;assert(graphics_cycle(0)==133&&calls==1);
}
'''
with tempfile.TemporaryDirectory(prefix='net-cycle-check-') as name:
    p=Path(name);(p/'check.cpp').write_text(support+leaf+checks)
    subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
        str(p/'check.cpp'),'-o',str(p/'check')],check=True,timeout=30)
    subprocess.run([str(p/'check')],check=True,timeout=5,
        env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0'))
print('Actual graphics-cycle leaf: packet/order, four positions, one write, refusal, Escape, timeout and mode mismatch pass')
