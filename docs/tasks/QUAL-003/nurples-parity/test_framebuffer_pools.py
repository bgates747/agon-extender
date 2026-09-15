"""Exercise actual stock allocation/free methods with a fragmented host heap.

No copied allocator algorithm: extract the production methods at test time.
The simulated regions make short allocation and fallback reproducible.
"""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[4]
def method(path,signature):
 s=(root/path).read_text();a=s.index(signature);b=s.index('{',a);depth=1;i=b+1
 while depth:
  depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[a:i]
base='vdp/vendor/vdp-gl/src/dispdrivers/vgabasecontroller.cpp'
pal='vdp/vendor/vdp-gl/src/dispdrivers/vgapalettedcontroller.cpp'
source=r'''
#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <unordered_map>
#define AGON_EXTENDER_STOCK_RUNTIME
#define AGON_EXTENDER_INTERNAL_FRAMEBUFFER
#define AGON_EXTENDER_INTERNAL_GAME_MODE
#define AGON_EXTENDER_INTERNAL_POOLS
#define ESP_LOGI(...) ((void)0)
#define FABGLIB_VIEWPORT_MEMORY_POOL_COUNT 128
#define FABGLIB_MINFREELARGESTBLOCK 4000
#define MALLOC_CAP_8BIT 1
#define MALLOC_CAP_SPIRAM 2
#define MALLOC_CAP_INTERNAL 4
#define MALLOC_CAP_32BIT 8
#define MALLOC_CAP_DMA 16
using std::size_t;
using std::max;using std::min;
#define tmax max
#define tmin min
std::vector<size_t> regions;
struct Block{size_t bytes;int region;};
std::unordered_map<void*,Block> live;
int internalPools=0,freedInternalPools=0;
size_t heap_caps_get_largest_free_block(unsigned caps){
 return caps&MALLOC_CAP_SPIRAM ? 1000000 : *std::max_element(regions.begin(),regions.end());
}
size_t heap_caps_get_free_size(unsigned){size_t total=0;for(auto n:regions)total+=n;return total;}
void* heap_caps_malloc(size_t n,unsigned caps){
 if(!n)return nullptr;
 int region=-1;
 if(!(caps&MALLOC_CAP_SPIRAM)){
  for(size_t i=0;i<regions.size();++i)if(regions[i]>=n){region=int(i);break;}
  if(region<0)return nullptr;
  regions[region]-=n;
 }
 auto p=std::malloc(n);assert(p);live[p]={n,region};
 if(region>=0 && n>=5120)++internalPools;
 return p;
}
void heap_caps_free(void* p){
 if(!p)return;auto it=live.find(p);assert(it!=live.end());
 if(it->second.region>=0){regions[it->second.region]+=it->second.bytes;if(it->second.bytes>=5120)++freedInternalPools;}
 std::free(p);live.erase(it);
}
struct VGABaseController{
 int m_viewPortHeight=384,m_viewPortWidth=512;
 uint8_t**m_viewPortMemoryPool=nullptr;
 volatile uint8_t**m_viewPort=nullptr,**m_viewPortVisible=nullptr;
 bool isDoubleBuffered(){return false;}
 void allocateViewPort(uint32_t,int);void freeViewPort();
};
struct VGAPalettedController:VGABaseController{
 int m_viewPortRatioDiv=1,m_viewPortRatioMul=1,m_linesCount=4;
 uint8_t*m_lines[4]={};
 void allocateViewPort();void freeViewPort();
};
'''
for path,sig in ((base,'void VGABaseController::allocateViewPort('),(base,'void VGABaseController::freeViewPort('),(pal,'void VGAPalettedController::allocateViewPort('),(pal,'void VGAPalettedController::freeViewPort(')):
 source+='\n'+method(path,sig)+'\n'
source+=r'''
void check(std::vector<size_t> chunks,bool wantInternal,bool attempted){
 assert(live.empty());regions=chunks;internalPools=freedInternalPools=0;
 VGAPalettedController c;c.allocateViewPort();assert(c.m_viewPortHeight==384);
 assert(c.m_viewPort==c.m_viewPortVisible);
 bool internal=live.at(c.m_viewPortMemoryPool[0]).region>=0;assert(internal==wantInternal);
 if(attempted && !wantInternal)assert(freedInternalPools>0);
 for(int y=0;y<384;++y){assert(c.m_viewPort[y]);for(int x=0;x<512;++x)c.m_viewPort[y][x]=uint8_t(x+y);}
 c.freeViewPort();assert(live.empty());assert(regions==chunks);
 assert(!c.m_viewPort && !c.m_viewPortVisible && !c.m_viewPortMemoryPool);
}
int main(){
 check({120000,110000},true,true); // no contiguous framebuffer, full stock pools
 check({60000,50000},false,false); // insufficient total, no internal attempt
 std::vector<size_t> fragmented(90,2000);fragmented.push_back(40000);
 check(fragmented,false,true); // total sufficient, stock short height cleaned up
 check({300000},true,true);
}
'''
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp)/'test.cpp';p.write_text(source);exe=Path(temp)/'test'
 subprocess.run(['g++','-std=c++17','-g','-fsanitize=address,undefined',str(p),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
print('Actual stock multi-pool allocation and full-height fallback: four cases passed')
