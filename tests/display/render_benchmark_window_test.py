"""Exercise real benchmark scopes across window boundaries and probe controls."""
import pathlib,tempfile,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory() as tmp:
 p=pathlib.Path(tmp);(p/'freertos').mkdir()
 (p/'esp_timer.h').write_text('#pragma once\n#include <cstdint>\ninline std::int64_t test_now=1;\ninline std::int64_t esp_timer_get_time(){return test_now;}\n')
 (p/'freertos/FreeRTOS.h').write_text('#pragma once\n')
 (p/'freertos/task.h').write_text('#pragma once\ninline void vTaskDelay(int){}\n')
 (p/'test.cpp').write_text('''#include "extender/diagnostics/render_benchmark.hpp"
#include <cassert>
int main(){unsigned char m[12]={'B','0','0','9',1,1,7,0,3,12,0,0};
 agon_bench::marker(m,12);{agon_bench::Scope s(agon_bench::Drain);test_now+=100;}
 auto &w=agon_bench::windows[0];assert(w.phases[0].calls==1&&w.phases[0].us==100);
 {agon_bench::Scope s(agon_bench::Expand);m[5]=2;test_now+=20;agon_bench::marker(m,12);test_now+=10;}
 assert(w.phases[agon_bench::Expand].calls==0&&w.phases[agon_bench::Expand].drops==1);
 assert(agon_bench::json().find("\\\"end_us\\\":121")!=std::string::npos);
 m[5]=1;m[6]=8;m[8]=2;agon_bench::marker(m,12);
 {agon_bench::Scope s(agon_bench::Drain);test_now+=100;}
 assert(agon_bench::windows[1].phases[0].calls==0);
 m[5]=2;agon_bench::marker(m,12);m[5]=0;agon_bench::marker(m,12);assert(agon_bench::used==0);
}''')
 subprocess.run(['g++','-std=c++17','-DAGON_EXTENDER_RENDER_BENCHMARK=1','-I'+str(p),'-I'+str(ROOT/'vdp/video'),str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('benchmark window boundary and probe-control checks passed')
