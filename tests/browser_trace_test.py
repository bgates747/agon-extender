"""Bounded recorder concurrency/overflow/disable and actual send-loop timing."""
from pathlib import Path
import subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)
 (p/'esp_timer.h').write_text('#pragma once\n#include <chrono>\ninline int64_t esp_timer_get_time(){return std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}\n')
 (p/'esp_heap_caps.h').write_text('#pragma once\n#include <cstdlib>\n#define MALLOC_CAP_SPIRAM 0\n#define MALLOC_CAP_8BIT 0\ninline void *heap_caps_malloc(size_t n,int){return malloc(n);}\n')
 (p/'test.cpp').write_text(r'''
#define AGON_EXTENDER_BROWSER_TYPING 1
#include "extender/diagnostic/browser_trace.hpp"
#include "extender/input/browser_keyboard.hpp"
#include <cassert>
#include <thread>
#include <cstdio>
using namespace agon::extender::diagnostic;
int main(){
 auto &t=browserTrace();t.begin();assert(t.available());
 std::thread a([]{for(int i=0;i<6000;++i)trace("a",i);});
 std::thread b([]{for(int i=0;i<6000;++i)trace("b",i);});
 a.join();b.join();auto n=t.freeze();assert(n==12000);
 TraceRecord row{};assert(!t.read(0,row)); int64_t last=0;
 for(auto i=n-t.capacity;i<n;++i){assert(t.read(i,row));assert(row.us>=last);last=row.us;}
 trace("frozen");assert(t.freeze()==n);
 printf("record cost total=%lld us, max=%lld us (host, not P4)\n",(long long)t.cost_us(),(long long)t.max_cost_us());
 t.configure(false);trace("disabled");assert(t.freeze()==0);
 t.configure(true);trace("enabled");assert(t.freeze()==1);
 t.configure(true);
 agon::extender::input::BrowserKeyboard keys; keys.ready(true); assert(keys.take(42,0));
 keys.expire(2000);assert(!keys.heartbeat(42,2001));
 assert(t.freeze()==1);assert(t.read(0,row));assert(row.id==42 && row.a==3);
 puts("PASS: concurrent monotonic records, bounded overwrite, freeze, disabled comparison and re-enable");
}
''')
 subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-pthread','-fsanitize=address,undefined','-I'+str(p),'-I'+str(ROOT/'vdp/video'),str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
