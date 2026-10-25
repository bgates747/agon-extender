#include "view.hpp"
#include <stdio.h>
#include <assert.h>
struct Svg {
    void clear(){puts("<rect width='512' height='384' fill='black'/>");}
    const char* ink(unsigned c){static const char*v[]={"#000","#000","#000","#000","#000","#000","#000","#000","#555","#f55","#5f5","#ff5","#55f","#000","#5ff","#fff"};return v[c];}
    void rect(int x,int y,int w,int h,unsigned c){printf("<rect x='%d' y='%d' width='%d' height='%d' fill='%s'/>\n",x,y,w,h,ink(c));}
    void line(int x,int y,int a,int b,unsigned c){printf("<path d='M%d,%d L%d,%d' stroke='%s'/>\n",x,y,a,b,ink(c));}
    void circle(int x,int y,int r,unsigned c){printf("<circle cx='%d' cy='%d' r='%d' fill='none' stroke='%s'/>\n",x,y,r,ink(c));}
    void text(unsigned x,unsigned y,const char*s,unsigned fg,unsigned){printf("<text x='%u' y='%u' fill='%s' font-family='DejaVu Sans Mono' font-weight='bold' font-size='16' textLength='%zu' lengthAdjust='spacingAndGlyphs'>%s</text>\n",x*12,y*16+14,ink(fg),strlen(s)*12,s);}
};
int main(){
    using namespace controller_view;
    assert(byte_axis(-32768)==0&&byte_axis(32767)==255);
    assert(position(-32768)==-48&&position(32767)==48);
    Svg canvas;View<Svg> view(canvas);Sample s{};
    s.connected=s.valid=s.replay=true;s.stick[0]=16384;s.stick[1]=-16384;
    s.trigger[0]=96;s.trigger[1]=220;s.held=1|(1<<11);s.presses[0]=3;s.presses[11]=1;
    puts("<svg xmlns='http://www.w3.org/2000/svg' width='1024' height='768' viewBox='0 0 512 384'>");
    view.paint(s);puts("</svg>");
}
