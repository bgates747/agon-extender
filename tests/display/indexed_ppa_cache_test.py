#!/usr/bin/env python3
"""Actual helper + explicit cache/RAM model; not a hardware PPA qualification."""
from pathlib import Path
import json
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent

def main():
    output=(ROOT/'vdp/video/extender/display/hdmi_output.cpp').read_text()
    linear=output[output.index('bool HdmiOutput::publishLinear('):output.index('bool HdmiOutput::startDirectSubmitter(')]
    assert linear.index('waitForSubmittedBuffer(stopping)') < linear.index('indexed_output_cache_.begin(') < linear.index('std::memset(destination')
    assert linear.index('esp_lcd_panel_draw_bitmap(') < linear.index('ownership_.submitted(target)') < linear.index('indexed_output_cache_.submitted(cache_attempt)')
    assert 'indexed_.expand(scaler_.source(),320*240*3,320,240,w,h)' in linear
    assert '!scaled && IndexedOutputCacheState::nativeMode20' in linear
    service=(ROOT/'vdp/video/extender/display/stock_p4_service.cpp').read_text()
    activate=service[service.index('void StockP4Service::activate('):service.index('bool StockP4Service::attach(')]
    assert activate.index('resetIndexedOutputCache()') < activate.index('active_.store(true')
    # The mode transaction already joins the old service before activation.
    mode=(ROOT/'vdp/video/agon_screen.h').read_text()
    commit=mode[mode.index('commitPreparedMode(std::move(candidate),'):]
    assert commit.index('_stockFrameService->detach()') < commit.index('service.activate()')
    with tempfile.TemporaryDirectory(prefix='indexed-ppa-cache-') as temp:
        temp=Path(temp);(temp/'driver').mkdir();(temp/'freertos').mkdir()
        (temp/'esp_cache.h').write_text('''#pragma once
#include <cstddef>
using esp_err_t=int;
constexpr int ESP_OK=0,ESP_FAIL=-1;
constexpr int ESP_CACHE_MSYNC_FLAG_DIR_C2M=4,ESP_CACHE_MSYNC_FLAG_DIR_M2C=8;
esp_err_t esp_cache_msync(void *,std::size_t,int);
''')
        (temp/'esp_heap_caps.h').write_text('''#pragma once
#include <cstddef>
constexpr int MALLOC_CAP_SPIRAM=1,MALLOC_CAP_8BIT=2;
void *heap_caps_aligned_alloc(std::size_t,std::size_t,int);
void *heap_caps_aligned_calloc(std::size_t,std::size_t,std::size_t,int);
void heap_caps_free(void *);
''')
        (temp/'esp_log.h').write_text('#pragma once\n#define ESP_LOGE(...) ((void)0)\ninline char const *esp_err_to_name(int){return "fake failure";}\n')
        (temp/'esp_timer.h').write_text('#pragma once\n#include <cstdint>\ninline std::int64_t test_now=100;\ninline std::int64_t esp_timer_get_time(){return test_now;}\n')
        (temp/'freertos/FreeRTOS.h').write_text('#pragma once\n')
        (temp/'freertos/task.h').write_text('#pragma once\ninline void vTaskDelay(int){}\n')
        (temp/'driver/ppa.h').write_text('''#pragma once
#include "esp_cache.h"
#include <cstdint>
using ppa_client_handle_t=void *;
constexpr int PPA_OPERATION_BLEND=1,PPA_CLUT_BLEND_BG=2,PPA_BLEND_COLOR_MODE_L8=3,
  PPA_BLEND_COLOR_MODE_A8=4,PPA_BLEND_COLOR_MODE_RGB888=5,PPA_ALPHA_NO_CHANGE=6,PPA_TRANS_MODE_BLOCKING=7;
struct color_pixel_argb8888_data_t {std::uint8_t a{},r{},g{},b{};};
struct ppa_client_config_t {int oper_type{},max_pending_trans_num{};};
struct Input {void const *buffer{};int pic_w{},pic_h{},block_w{},block_h{},block_offset_x{},block_offset_y{},blend_cm{};};
struct Output {void *buffer{};std::size_t buffer_size{};int pic_w{},pic_h{},block_offset_x{},block_offset_y{},blend_cm{};};
struct ppa_blend_oper_config_t {Input in_bg{},in_fg{};Output out{};int bg_alpha_update_mode{},fg_alpha_update_mode{},mode{};};
int ppa_register_client(ppa_client_config_t const *,ppa_client_handle_t *);
int ppa_unregister_client(ppa_client_handle_t);
int ppa_set_color_lookup_table(int,color_pixel_argb8888_data_t const *,int);
int ppa_do_blend(ppa_client_handle_t,ppa_blend_oper_config_t const *);
''')
        test=temp/'helper_test.cpp'
        test.write_text(r'''#include "extender/display/hdmi_ppa_indexed.hpp"
#include "extender/display/indexed_output_cache.hpp"
#include "extender/diagnostics/render_benchmark.hpp"
#include "driver/ppa.h"
#include "esp_heap_caps.h"
#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
constexpr int OW=684,OH=384,W=512,H=384,LEFT=86;
constexpr std::size_t BYTES=OW*OH*3;
struct Plane {std::vector<std::uint8_t> cache,ram;unsigned c2m{},m2c{};
  Plane():cache(BYTES,0xA5),ram(BYTES,0xEF){}
};
Plane planes[2];
unsigned driver_inputs{},blends{};int fail_stage{};bool driver_cache{};
color_pixel_argb8888_data_t palette[256];
int esp_cache_msync(void *p,std::size_t n,int flags) {
  test_now+=(flags==ESP_CACHE_MSYNC_FLAG_DIR_C2M?7:3);
  for(auto &plane:planes)if(p==plane.cache.data()) {
    assert(n==BYTES);
    if(flags==ESP_CACHE_MSYNC_FLAG_DIR_C2M) {
      ++plane.c2m;if(fail_stage==1){fail_stage=0;return ESP_FAIL;}
      plane.ram=plane.cache;
    } else {
      assert(flags==ESP_CACHE_MSYNC_FLAG_DIR_M2C);++plane.m2c;
      if(fail_stage==3&&!driver_cache){fail_stage=0;return ESP_FAIL;}
      plane.cache=plane.ram; // invalidation followed by a future CPU read
    }
  }
  return ESP_OK;
}
void *heap_caps_aligned_alloc(std::size_t alignment,std::size_t n,int) {
  void *p{};return posix_memalign(&p,alignment,n)?nullptr:p;
}
void *heap_caps_aligned_calloc(std::size_t alignment,std::size_t n,std::size_t size,int caps) {
  auto p=heap_caps_aligned_alloc(alignment,n*size,caps);if(p)std::memset(p,0,n*size);return p;
}
void heap_caps_free(void *p){std::free(p);}
int ppa_register_client(ppa_client_config_t const *c,ppa_client_handle_t *p) {
  assert(c->oper_type==PPA_OPERATION_BLEND&&c->max_pending_trans_num==1);*p=reinterpret_cast<void*>(1);return ESP_OK;
}
int ppa_unregister_client(ppa_client_handle_t){return ESP_OK;}
int ppa_set_color_lookup_table(int kind,color_pixel_argb8888_data_t const *p,int n) {
  assert(kind==PPA_CLUT_BLEND_BG&&n==256);std::copy(p,p+n,palette);return ESP_OK;
}
int ppa_do_blend(ppa_client_handle_t,ppa_blend_oper_config_t const *c) {
  ++blends;
  assert(c->in_bg.blend_cm==PPA_BLEND_COLOR_MODE_L8&&c->in_fg.blend_cm==PPA_BLEND_COLOR_MODE_A8);
  assert(c->out.blend_cm==PPA_BLEND_COLOR_MODE_RGB888&&c->mode==PPA_TRANS_MODE_BLOCKING);
  assert(c->out.pic_w==OW&&c->out.pic_h==OH&&c->in_bg.block_w==W&&c->in_bg.block_h==H);
  // Retain pinned driver input C2M and full-row output pre-invalidation.
  driver_cache=true;
  esp_cache_msync(const_cast<void*>(c->in_bg.buffer),W*H,ESP_CACHE_MSYNC_FLAG_DIR_C2M);
  esp_cache_msync(const_cast<void*>(c->in_fg.buffer),W*H,ESP_CACHE_MSYNC_FLAG_DIR_C2M);driver_inputs+=2;
  esp_cache_msync(c->out.buffer,BYTES,ESP_CACHE_MSYNC_FLAG_DIR_M2C);
  driver_cache=false;
  if(fail_stage==2){fail_stage=0;return ESP_FAIL;}
  Plane *dest{};for(auto &p:planes)if(p.cache.data()==c->out.buffer)dest=&p;
  assert(dest);
  auto src=static_cast<std::uint8_t const*>(c->in_bg.buffer);
  auto mask=static_cast<std::uint8_t const*>(c->in_fg.buffer);
  for(int y=0;y<H;++y)for(int x=0;x<W;++x) {
    assert(mask[y*W+x]==0);auto colour=palette[src[y*W+x]];
    auto offset=((y+c->out.block_offset_y)*OW+x+c->out.block_offset_x)*3;
    dest->ram[offset]=colour.b;dest->ram[offset+1]=colour.g;dest->ram[offset+2]=colour.r;
  }
  return ESP_OK;
}
void check(Plane const &p,std::uint8_t const *src) {
  assert(p.cache==p.ram);
  for(int y=0;y<H;++y)for(int x=0;x<OW;++x) {
    auto offset=(y*OW+x)*3;
    if(x<LEFT||x>=LEFT+W)assert(p.cache[offset]==0&&p.cache[offset+1]==0&&p.cache[offset+2]==0);
    else {auto c=palette[src[y*W+x-LEFT]];assert(p.cache[offset]==c.b&&p.cache[offset+1]==c.g&&p.cache[offset+2]==c.r);}
  }
}
int main() {
  using namespace agon::extender::display;
  unsigned char marker[12]={'B','0','0','9',1,1,1,0,1,1,0,0};agon_bench::marker(marker,12);
  HdmiPpaIndexed ppa;assert(ppa.initialize());IndexedOutputCacheState state;
  auto fill=[&](unsigned k){for(int i=0;i<W*H;++i)ppa.source()[i]=std::uint8_t(i+k);};
  for(unsigned target=0;target<2;++target) {
    fill(target);std::fill(planes[target].cache.begin(),planes[target].cache.end(),0);
    auto a=state.begin(target,true,true);assert(a.preserve_cpu_writes);
    assert(ppa.expand(planes[target].cache.data(),BYTES,OW,OH,W,H,LEFT,0,a.preserve_cpu_writes));
    state.submitted(a);check(planes[target],ppa.source());assert(planes[target].c2m==1&&planes[target].m2c==2);
  }
  for(unsigned target=0;target<2;++target) {
    fill(target+2);auto a=state.begin(target,true,false);assert(!a.preserve_cpu_writes);
    assert(ppa.expand(planes[target].cache.data(),BYTES,OW,OH,W,H,LEFT,0,a.preserve_cpu_writes));
    state.submitted(a);check(planes[target],ppa.source());assert(planes[target].c2m==1&&planes[target].m2c==4);
  }
  assert(agon_bench::indexed_pre_c2m[0].calls==2&&agon_bench::indexed_pre_c2m[0].us==14);
  // Default argument keeps historical pre-writeback behaviour for other callers.
  assert(ppa.expand(planes[0].cache.data(),BYTES,OW,OH,W,H,LEFT));assert(planes[0].c2m==2);
  for(int stage=1;stage<=3;++stage) {
    state.invalidate();auto a=state.begin(0,true,false);assert(a.preserve_cpu_writes);
    fail_stage=stage;
    assert(!ppa.expand(planes[0].cache.data(),BYTES,OW,OH,W,H,LEFT,0,a.preserve_cpu_writes));
    auto retry=state.begin(0,true,false);assert(retry.preserve_cpu_writes);
    assert(ppa.expand(planes[0].cache.data(),BYTES,OW,OH,W,H,LEFT,0,retry.preserve_cpu_writes));
    state.submitted(retry);check(planes[0],ppa.source());
  }
  // Ending a window during this scope is reported as a drop, not leaked into
  // the following window; the six original phase indices remain unchanged.
  {agon_bench::IndexedPreC2MScope scope;marker[5]=2;agon_bench::marker(marker,12);}
  assert(agon_bench::indexed_pre_c2m[0].drops==1&&agon_bench::PhaseCount==6);
  assert(agon_bench::outstanding==0);auto result=agon_bench::json();
  assert(driver_inputs==2*blends);ppa.reset();
  std::puts(result.c_str());
  marker[5]=0;agon_bench::marker(marker,12);
  assert(!agon_bench::indexed_pre_c2m_overflow);
  for(unsigned i=0;i<17;++i) {
    marker[5]=1;marker[6]=std::uint8_t(i);agon_bench::marker(marker,12);
    {agon_bench::IndexedPreC2MScope scope;test_now+=5;}
    marker[5]=2;agon_bench::marker(marker,12);
  }
  assert(agon_bench::indexed_pre_c2m_overflow&&agon_bench::outstanding==0);
  assert(agon_bench::json().find("\"indexed_pre_c2m\":null")!=std::string::npos);
  marker[5]=0;agon_bench::marker(marker,12);assert(!agon_bench::indexed_pre_c2m_overflow);
  marker[5]=1;marker[8]=2;agon_bench::marker(marker,12);
  {agon_bench::IndexedPreC2MScope scope;test_now+=5;}
  assert(agon_bench::indexed_pre_c2m[0].calls==0&&agon_bench::outstanding==0);
  marker[5]=2;agon_bench::marker(marker,12);
}
''')
        # The retained compact diagnostic JSON formatter has an unrelated
        # misleading-indentation warning; do not turn this cache pilot into a
        # formatting change across that existing header.
        flags=['g++','-std=c++17','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-O1','-g',
               '-fsanitize=address,undefined','-fno-omit-frame-pointer',
               '-I'+str(temp),'-I'+str(ROOT/'vdp/video')]
        binary=temp/'state'
        subprocess.run([*flags,str(HERE/'indexed_output_cache_test.cpp'),'-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
        helper=ROOT/'vdp/video/extender/display/hdmi_ppa_indexed.cpp'
        binary=temp/'helper'
        subprocess.run([*flags,'-DAGON_EXTENDER_RENDER_BENCHMARK=1',str(helper),str(test),'-o',str(binary)],check=True)
        result=subprocess.run([str(binary)],check=True,capture_output=True,text=True)
        document=json.loads(result.stdout)
        assert document['schema']==1 and not document['indexed_pre_c2m_overflow']
        assert len(document['windows'][0]['phases'])==6
        assert document['windows'][0]['indexed_pre_c2m']['boundary_drops']==1
        disabled=subprocess.check_output([*flags,'-E','-P',str(helper)],text=True)
        assert 'IndexedPreC2MScope' not in disabled and 'indexed_pre_c2m' not in disabled
    print('PASS: actual helper cache/RAM border model, two planes, steady omission, default preservation, failures, measured scope and benchmark-off exclusion')
    print('LIMIT: mocked PPA/cache execution proves call ordering and modelled ownership; actual P4 cache/DMA timing and output correctness remain untested')

if __name__=='__main__':main()
