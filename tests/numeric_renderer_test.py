"""Exercise exact renderer bodies, ownership and template sampling under sanitizers."""
from pathlib import Path
import subprocess,tempfile
from processed_keyboard_test import function
ROOT=Path(__file__).resolve().parents[1]
cpp=(ROOT/'vdp/vendor/vdp-gl/src/displaycontroller.cpp').read_text()
hpp=(ROOT/'vdp/vendor/vdp-gl/src/displaycontroller.h').read_text()
body=function(cpp,'void IRAM_ATTR BitmappedDisplayController::drawBitmapWithTransform(')
templates='\n'.join('template<class TRawGetRow,class TRawSetPixelInRow>\n'+function(hpp,'void genericRawDrawTransformedBitmap_'+name+'(') for name in ('Mask','RGBA2222','RGBA8888'))
pre=r'''
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <climits>
#include <vector>
#include <algorithm>
#include <limits>
#include "extender/port/numeric_conversion.hpp"
#define IRAM_ATTR
struct RGBA8888{uint8_t R,G,B,A;};
struct Point{int X,Y;};
struct Rect{int X1,Y1,X2,Y2;Rect(int a=0,int b=0,int c=0,int d=0):X1(a),Y1(b),X2(c),Y2(d){}int width(){return std::max(0,X2-X1+1);}int height(){return std::max(0,Y2-Y1+1);}Rect translate(int x,int y){return {X1+x,Y1+y,X2+x,Y2+y};}Rect intersection(Rect r){return {std::max(X1,r.X1),std::max(Y1,r.Y1),std::min(X2,r.X2),std::min(Y2,r.Y2)};}Rect merge(Rect r){return {std::min(X1,r.X1),std::min(Y1,r.Y1),std::max(X2,r.X2),std::max(Y2,r.Y2)};}};
int imin(int a,int b){return std::min(a,b);}int imax(int a,int b){return std::max(a,b);}
enum class PixelFormat{Undefined,Mask,RGBA2222,RGBA8888};
struct Bitmap{int width=2,height=2;const uint8_t*data=nullptr;PixelFormat format=PixelFormat::RGBA2222;};
struct BitmapTransformedDrawingInfo{int X=0,Y=0;Bitmap*bitmap;const float*transformMatrix;const float*transformInverse;bool freeMatrix;};
unsigned calls=0,writes=0,hidden=0,drawn=0,checks=0;int badCall=-1,badAxis=0;bool badAll=false;float badValue=0;
void dspm_mult_3x3x1_f32(const float*m,const float*p,float*out){for(int r=0;r<3;r++){out[r]=0;for(int c=0;c<3;c++)out[r]+=m[r*3+c]*p[c];}if(int(calls)==badCall||badAll)out[badAxis]=badValue;++calls;}
struct Pool{std::vector<void*>freed;void free(void*p){assert(std::find(freed.begin(),freed.end(),p)==freed.end());freed.push_back(p);}};
struct BitmappedDisplayController{struct State{Point origin{0,0};Rect absClippingRect{0,0,31,31};}state;Pool m_primDynMemPool;State&paintState(){return state;}void hideSprites(Rect){++hidden;}
 void rawDrawBitmapWithMatrix_Mask(int,int,Rect&,Bitmap const*,float const*){++drawn;}
 void rawDrawBitmapWithMatrix_RGBA2222(int,int,Rect&,Bitmap const*,float const*){++drawn;}
 void rawDrawBitmapWithMatrix_RGBA8888(int,int,Rect&,Bitmap const*,float const*){++drawn;}
 void drawBitmapWithTransform(BitmapTransformedDrawingInfo const&,Rect&);
};
struct Generic {
'''
checks=r'''
};
int main(){
 const float nan=std::numeric_limits<float>::quiet_NaN(),inf=std::numeric_limits<float>::infinity();
 float matrix[9]={1,0,0,0,1,0,0,0,1},inverse[9]={1,0,0,0,1,0,0,0,1};Bitmap bitmap;
#ifdef AGON_EXTENDER_STOCK_RUNTIME
 for(float f:{nan,inf,-inf,2147483648.f,-2147483904.f})for(int corner=0;corner<4;corner++)for(int axis:{0,1})for(bool own:{false,true}){BitmappedDisplayController c;BitmapTransformedDrawingInfo info{0,0,&bitmap,matrix,inverse,own};Rect update{8,8,9,9};badCall=corner;badAxis=axis;badValue=f;calls=hidden=drawn=0;c.drawBitmapWithTransform(info,update);assert(update.X1==8&&update.Y1==8&&update.X2==9&&update.Y2==9);assert(hidden==0&&drawn==0&&calls==unsigned(corner+1));assert(c.m_primDynMemPool.freed.size()==(own?2:0));++checks;}
 Generic g;
 for(float f:{nan,inf,-inf,-1.f,2.f})for(int axis:{0,1})for(int format=0;format<3;format++){badAll=true;badValue=f;badAxis=axis;writes=0;auto row=[](int y){assert(y>=0&&y<2);return y;};auto pixel=[](int,int,auto...){++writes;};Rect rect{0,0,2,2};if(format==0)g.genericRawDrawTransformedBitmap_Mask(0,0,rect,&bitmap,inverse,row,pixel);if(format==1)g.genericRawDrawTransformedBitmap_RGBA2222(0,0,rect,&bitmap,inverse,row,pixel);if(format==2)g.genericRawDrawTransformedBitmap_RGBA8888(0,0,rect,&bitmap,inverse,row,pixel);assert(writes==0);++checks;}
#endif
 badAll=false;badCall=-1;
 for(bool own:{false,true})for(int off:{0,-1,100}){BitmappedDisplayController c;BitmapTransformedDrawingInfo info{off,off,&bitmap,matrix,inverse,own};Rect update{8,8,9,9};drawn=hidden=0;c.drawBitmapWithTransform(info,update);assert(drawn==(off==100?0:1));assert(c.m_primDynMemPool.freed.size()==(own?2:0));++checks;}
 uint8_t bytes[16];std::fill(bytes,bytes+16,255);bitmap.data=bytes;
 uint64_t hash=0;for(int axis:{0,1})for(float offset:{-1.5f,-.5f,0.f,.5f,1.5f})for(int format=0;format<3;format++){Generic g;writes=0;inverse[2]=axis==0?offset:0;inverse[5]=axis==1?offset:0;auto row=[](int y){assert(y>=0&&y<2);return y;};auto pixel=[&](int y,int x,auto...){assert(x>=0&&x<2);hash=hash*31+unsigned(y*2+x+1);++writes;};Rect rect{0,0,2,2};if(format==0)g.genericRawDrawTransformedBitmap_Mask(0,0,rect,&bitmap,inverse,row,pixel);if(format==1)g.genericRawDrawTransformedBitmap_RGBA2222(0,0,rect,&bitmap,inverse,row,pixel);if(format==2)g.genericRawDrawTransformedBitmap_RGBA8888(0,0,rect,&bitmap,inverse,row,pixel);++checks;}
 printf("valid sampling hash %llu\n",(unsigned long long)hash);printf("renderer cases %u\n",checks);
}
'''
with tempfile.TemporaryDirectory() as t:
 p=Path(t);source=pre+templates+'\n};\n'+body+'\nstruct Dummy {\n'+checks
 (p/'test.cpp').write_text(source)
 results=[]
 for label,flags in [('guarded',['-DAGON_EXTENDER_STOCK_RUNTIME']),('stock',[])]:
  subprocess.run(['c++','-std=c++17','-O1','-g','-fsanitize=address,undefined,float-cast-overflow','-fno-sanitize-recover=all','-I'+str(ROOT/'vdp/video'),*flags,str(p/'test.cpp'),'-o',str(p/label)],check=True)
  output=subprocess.check_output([str(p/label)],text=True);print(label,output.strip());results.append(output.splitlines()[0])
 assert results[0]==results[1]
