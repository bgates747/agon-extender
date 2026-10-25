// Shared Agon/native renderer. Drawing is incremental; input ownership is external.
#pragma once
#include <stdint.h>
#include <stdio.h>
#include <string.h>

namespace controller_view {
struct Sample {
    int16_t stick[4]{};
    uint8_t trigger[2]{};
    uint16_t held{}, presses[15]{};
    uint32_t sequence{}, age_ms{};
    uint16_t generation{};
    bool connected{}, valid{}, replay{};
};
inline unsigned byte_axis(int16_t value) {
    return (int32_t(value) + 32768) >> 8;
}
inline int position(int16_t value) {
    return int((int32_t(value) + 32768) * 96 / 65535) - 48;
}
enum Colour { Black=0, Grey=8, Red=9, Green=10, Yellow=11, Blue=12, Cyan=14, White=15 };
constexpr const char *labels[15] = {
    "A", "B", "Y", "X", "LB", "RB", "Back", "Start", "Guide", "L3", "R3",
    "Left", "Right", "Up", "Down"
};

template<class Canvas> class View {
    Canvas &c;
    Sample old{};
    uint16_t base[15]{};
    bool first=true;
    const char *message="Waiting for controller";
    void box(unsigned index, bool down) {
        const int row=index<6?0:index<11?1:2;
        const int column=index-(row==0?0:row==1?6:11);
        const int width=row==0?84:row==1?96:120;
        const int x=12+column*width, y=256+row*32;
        const int bg=down?Green:Grey, fg=down?Black:White;
        c.rect(x,y,width-8,28,bg);
        // Labels use the same 12x16 font as the numeric axes. A tiny count is
        // unnecessary: the total and most recent press are shown below.
        c.text(x/12,y/16,labels[index],fg,bg);
    }
    void stick(unsigned index, const Sample &s) {
        const int cx=108+index*252, cy=144;
        // Erase only the old marker, then repair the static grid underneath.
        // Clearing the whole panel on each sample produces visible flicker.
        if(first)c.rect(cx-54,cy-54,109,109,Black);
        else if(old.valid)c.rect(cx+position(old.stick[index*2])-3,
                                 cy+position(old.stick[index*2+1])-3,7,7,Black);
        c.circle(cx,cy,50,Grey);
        c.line(cx-50,cy,cx+50,cy,Grey);
        c.line(cx,cy-50,cx,cy+50,Grey);
        if(s.valid) {
            const int x=cx+position(s.stick[index*2]);
            const int y=cy+position(s.stick[index*2+1]);
            c.rect(x-3,y-3,7,7,Cyan);
        }
        char text[24];
        for(unsigned axis=0;axis<2;++axis) {
            const int16_t raw=s.valid?s.stick[index*2+axis]:0;
            snprintf(text,sizeof(text),"%c%+6d /%3u",axis?'Y':'X',int(raw),byte_axis(raw));
            c.text(index?22:1,13+axis,text,White,Black);
        }
    }
    void trigger(unsigned index, const Sample &s) {
        const int x=204+index*252, y=92, height=104;
        if(first)c.rect(x,y,24,height,Grey);
        const unsigned value=s.valid?s.trigger[index]:0;
        const int fill=int(value*unsigned(height)/255);
        const int previous=first?0:int((old.valid?old.trigger[index]:0)*unsigned(height)/255);
        if(fill>previous)c.rect(x,y+height-fill,24,fill-previous,Yellow);
        else if(fill<previous)c.rect(x,y+height-previous,24,previous-fill,Grey);
        char text[4];snprintf(text,sizeof(text),"%3u",value);
        c.text(index?38:17,13,text,White,Black);
    }
 public:
    explicit View(Canvas &canvas):c(canvas) {}
    void status(const char *text) {message=text;first=true;}
    void reset_counts(const Sample &s) {memcpy(base,s.presses,sizeof(base));first=true;}
    void paint(const Sample &input) {
        Sample s=input;
        if(!s.valid)s.held=0;
        if(s.generation!=old.generation)memset(base,0,sizeof(base));
        if(first) {
            c.clear();
            c.text(1,0,"F310 controller / Mode 20",White,Black);
            c.text(1,4,"Left stick",White,Black);
            c.text(22,4,"Right stick",White,Black);
            c.text(17,4,"LT",Yellow,Black);c.text(38,4,"RT",Yellow,Black);
            c.text(1,23,"Esc exits    R clears counts",White,Black);
        }
        if(first||s.valid!=old.valid||s.connected!=old.connected||s.replay!=old.replay) {
            c.rect(0,32,512,16,Black);
            c.text(1,2,s.replay?(s.connected?"Replay: connected / visual review":"Replay: disconnected / visual review"):
                   s.valid?"Agon received controller input":message,
                   s.replay?Yellow:s.valid?Green:Red,Black);
        }
        for(unsigned i=0;i<2;++i) {
            if(first||s.valid!=old.valid||s.stick[i*2]!=old.stick[i*2]||s.stick[i*2+1]!=old.stick[i*2+1])stick(i,s);
            if(first||s.valid!=old.valid||s.trigger[i]!=old.trigger[i])trigger(i,s);
        }
        unsigned total=0,changed=0;int latest=-1;
        for(unsigned i=0;i<15;++i) {
            const unsigned count=uint16_t(s.presses[i]-base[i]);
            total+=count;
            if(s.presses[i]!=old.presses[i]){latest=int(i);++changed;}
            if(first||((s.held^old.held)&(1u<<i)))box(i,s.held&(1u<<i));
        }
        if(first||memcmp(s.presses,old.presses,sizeof(s.presses))) {
            char text[43];snprintf(text,sizeof(text),"Presses %5u  Changed %-8s",total,
                                   changed>1?"Multiple":latest>=0?labels[latest]:"-");
            c.rect(0,352,512,16,Black);
            c.text(1,22,text,White,Black);
        }
        old=s;first=false;
    }
};
}
