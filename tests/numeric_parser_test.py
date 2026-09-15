"""Execute retained parser bodies with bounded storage/argument fakes."""
from pathlib import Path
import subprocess,tempfile
from processed_keyboard_test import function
ROOT=Path(__file__).resolve().parents[1]
buffered=(ROOT/'vdp/video/vdu_buffered.h').read_text()
sprites=(ROOT/'vdp/video/vdu_sprites.h').read_text()
logical=function(buffered,'case AFFINE_TRANSLATE_OS_COORDS:')
logical='void VDUStreamProcessor::logical() '+logical[logical.index('{'):]
parts=[logical,function(buffered,'void VDUStreamProcessor::bufferTransformBitmap('),function(sprites,'void VDUStreamProcessor::createBitmapFromBuffer(')]
preamble=r'''
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <climits>
#include <cstdio>
#include <memory>
#include <vector>
#include <map>
#include <limits>
#include <algorithm>
#define AGON_EXTENDER_P4_BOOT 1
#define debug_log(...) ((void)0)
#include "extender/port/numeric_conversion.hpp"
struct Point {int X,Y;};
struct Rect {int x1,y1,x2,y2;Rect(int a,int b,int c,int d):x1(a),y1(b),x2(c),y2(d){}int width(){return x2-x1+1;}int height(){return y2-y1+1;}};
namespace fabgl {int imin(int a,int b){return std::min(a,b);}int imax(int a,int b){return std::max(a,b);}}
struct RGBA2222 {uint8_t value;RGBA2222(int r=0,int=0,int=0,int=0):value(r){}};
struct RGB888{};
enum class PixelFormat{RGBA8888,RGBA2222,Mask,Native};
unsigned allocated=0,scaled=0,unmapped=0,cleared=0,checks=0;
struct BufferStream {std::vector<uint8_t> data;uint64_t length;explicit BufferStream(uint64_t n):data(n<4096?n:0),length(n){++allocated;}void*getBuffer(){return data.empty()?nullptr:data.data();}uint64_t size(){return length;}};
struct Bitmap {int width=2,height=2;Bitmap()=default;Bitmap(int w,int h,uint8_t*,PixelFormat):width(w),height(h){}Bitmap(int w,int h,uint8_t*p,PixelFormat f,RGB888):Bitmap(w,h,p,f){}RGBA2222 getPixel2222(int x,int y){assert(x>=0&&x<width&&y>=0&&y<height);return RGBA2222(7);}};
template<class T,class...A>std::shared_ptr<T>make_shared_psram(A&&...args){return std::make_shared<T>(std::forward<A>(args)...);}
std::map<uint16_t,std::vector<std::shared_ptr<BufferStream>>> buffers;
std::map<uint16_t,std::shared_ptr<Bitmap>> bitmaps;
std::shared_ptr<Bitmap>getBitmap(uint16_t id){return bitmaps.count(id)?bitmaps[id]:nullptr;}
bool checkTransformBuffer(const std::vector<std::shared_ptr<BufferStream>>&s){return s.size()==2;}
void bufferClear(uint16_t id){buffers.erase(id);}
void clearBitmap(uint16_t id){++cleared;bitmaps.erase(id);}
struct Context {Point scale(int16_t x,int16_t y){++scaled;return {x/2,y/2};}void unmapBitmapFromChars(uint16_t){++unmapped;}void getColour(int,RGB888*){}} ctx;
int multCall=0,badCall=-1,badAxis=0;float badValue=0;
void dspm_mult_3x3x1_f32(const float*m,const float*p,float*out){for(int r=0;r<3;r++){out[r]=0;for(int c=0;c<3;c++)out[r]+=m[r*3+c]*p[c];}if(multCall++==badCall)out[badAxis]=badValue;}
constexpr int TRANSFORM_BITMAP_RESIZE=1,TRANSFORM_BITMAP_EXPLICIT_SIZE=2,TRANSFORM_BITMAP_TRANSLATE=4;
struct VDUStreamProcessor {Context*context=&ctx;int dimensions=2;bool is3D=false,useBufferValue=false,useAdvancedOffsets=false,useMultiFormat=false;struct {int columns=3;}size;float transform[16]={};float input[3]={};int consumed=0;
 bool readFloatArguments(float*p,int n,bool,bool,bool){for(int i=0;i<n;i++)p[i]=input[i];consumed+=n;return true;}
 int readWord_t(){return 2;}
 void logical();void bufferTransformBitmap(uint16_t,uint8_t,uint16_t,uint16_t);void createBitmapFromBuffer(uint16_t,uint8_t,uint16_t,uint16_t);
};
void setup(){buffers.clear();bitmaps.clear();auto a=std::make_shared<BufferStream>(36);auto b=std::make_shared<BufferStream>(36);float id[9]={1,0,0,0,1,0,0,0,1};memcpy(a->getBuffer(),id,36);memcpy(b->getBuffer(),id,36);buffers[1]={a,b};buffers[2]={std::make_shared<BufferStream>(1)};bitmaps[100]=std::make_shared<Bitmap>();allocated=scaled=unmapped=cleared=0;multCall=0;badCall=-1;}
'''
checks=r'''
int main(){
 using namespace agon::extender::port;
 const float nan=std::numeric_limits<float>::quiet_NaN(),inf=std::numeric_limits<float>::infinity();
 for(int i=-32768;i<=32767;++i){float f=float(i);assert(fitsTruncatedInt16(f));VDUStreamProcessor p;p.input[0]=f;p.input[1]=-0.75f;p.logical();assert(p.consumed==2&&p.transform[2]==i/2&&p.transform[5]==0);++checks;}
 for(float f:{nan,inf,-inf,32768.f,-32769.f,1e30f,-1e30f})for(int axis:{0,1})for(int n:{2,3}){VDUStreamProcessor p;p.dimensions=n;p.size.columns=n+1;p.is3D=n==3;p.input[axis]=f;p.input[2]=3.25f;auto before=scaled;p.logical();assert(scaled==before&&p.consumed==n);for(float x:p.transform)assert(x==0);++checks;}
 for(float f:{-32768.5f,-32768.9f,32767.5f,1.75f,-1.75f}){VDUStreamProcessor p;p.input[0]=f;p.logical();assert(p.transform[2]==int16_t(f)/2);++checks;}
 for(float f:{nan,inf,-inf,2147483648.f,-2147483904.f})for(int corner=0;corner<4;corner++)for(int axis:{0,1})for(int opt:{1,4,5,7}){setup();auto old=buffers[2][0];badCall=corner;badAxis=axis;badValue=f;VDUStreamProcessor p;p.bufferTransformBitmap(2,opt,1,100);assert(allocated==0&&buffers[2][0]==old&&bitmaps.count(2)==0&&multCall==corner+1);++checks;}
 setup();VDUStreamProcessor p;p.bufferTransformBitmap(2,5,1,100);assert(buffers[2][0]->size()==9&&bitmaps.count(2));++checks;
 setup();float*m=(float*)buffers[1][1]->getBuffer();m[0]=nan;p.bufferTransformBitmap(2,0,1,100);for(auto b:buffers[2][0]->data)assert(b==0);++checks;
 for(unsigned format=0;format<5;format++)for(unsigned w:{0u,1u,7u,8u,9u,32767u,32768u,65535u})for(unsigned h:{0u,1u,32767u,32768u,65535u}){setup();uint64_t row=format==2?(w+7)/8:format==1||format==3?w:uint64_t(w)*4;uint64_t count=row*h;buffers[3]={std::make_shared<BufferStream>(count)};p.createBitmapFromBuffer(3,format,w,h);assert(bool(bitmaps.count(3))==(count<=UINT32_MAX));assert(cleared==1&&unmapped==1);++checks;}
 assert(fitsTruncatedInt32(-2147483648.f));assert(fitsTruncatedInt32(std::nextafter(2147483648.f,0.f)));assert(!fitsTruncatedInt32(2147483648.f));assert(!fitsTruncatedInt32(nan));assert(fitsBitmapByteCount(4294967295.));assert(!fitsBitmapByteCount(4294967296.));
 printf("numeric parser: %u cases passed\n",checks);
}
'''
with tempfile.TemporaryDirectory() as t:
 p=Path(t);(p/'test.cpp').write_text(preamble+'\n'.join(parts)+checks)
 subprocess.run(['c++','-std=c++17','-O1','-g','-fsanitize=undefined,float-cast-overflow','-fno-sanitize-recover=all','-I'+str(ROOT/'vdp/video'),str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
