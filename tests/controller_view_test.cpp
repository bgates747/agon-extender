#include "fixtures/controller/view.hpp"
#include <assert.h>
#include <string.h>
struct Canvas {
    unsigned operations=0,clears=0;
    char status[80]{};
    void clear(){++operations;++clears;}
    void rect(int x,int y,int w,int h,unsigned){assert(x>=0&&y>=0&&w>0&&h>0&&x+w<=512&&y+h<=384);++operations;}
    void line(int x,int y,int a,int b,unsigned){assert(x>=0&&y>=0&&a<512&&b<384);++operations;}
    void circle(int x,int y,int r,unsigned){assert(x-r>=0&&x+r<512&&y-r>=0&&y+r<384);++operations;}
    void text(unsigned x,unsigned y,const char*s,unsigned,unsigned){
        assert(x*12+strlen(s)*12<=512&&y*16+16<=384);++operations;
        if(y==2)strcpy(status,s);
    }
};
int main(){
    using namespace controller_view;
    assert(byte_axis(-32768)==0&&byte_axis(32767)==255&&byte_axis(128)==128);
    assert(position(-32768)==-48&&position(32767)==48&&position(128)==0);
    Canvas c;View<Canvas> view(c);Sample s{};s.valid=s.connected=s.replay=true;
    for(unsigned i=0;i<4;++i)s.stick[i]=i%2?-32768:32767;
    s.trigger[0]=255;s.held=0x7fff;s.presses[0]=3;
    view.paint(s);assert(strstr(c.status,"Replay: connected"));
    auto n=c.operations;view.paint(s);assert(c.operations==n);
    s.valid=s.connected=false;s.held=0;view.paint(s);
    assert(strstr(c.status,"Replay: disconnected"));
    view.reset_counts(s);view.paint(s);assert(c.clears==2);
    s.generation=1;s.valid=s.connected=true;s.presses[0]=0;view.paint(s);
    assert(strstr(c.status,"Replay: connected"));
}
