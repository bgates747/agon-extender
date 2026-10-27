// Mode20 appliance: live through EMOS, or explicitly labelled recorded input.
// No application callback, raw UART/GPIO or display-route ownership.
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "view.hpp"
#include "mode_lifecycle.hpp"
#include "font.hpp"
#include "identity.hpp"
#include "live.hpp"

extern "C" uint24_t bench_clock(const volatile uint8_t *);
extern "C" uint24_t bench_count(const uint8_t *,uint24_t);
static volatile uint8_t *sysvars;
static controller_view::Live live;
static uint24_t ticks(){return bench_clock(sysvars);}
static bool write_bytes(const uint8_t *p,unsigned n){return bench_count(p,n)==0;}

struct Canvas {
    bool healthy=true;
    void send(const uint8_t*p,unsigned n){if(healthy)healthy=write_bytes(p,n);}
    void clear(){const uint8_t p[]={12};send(p,sizeof(p));}
    void colour(unsigned value){const uint8_t p[]={18,0,uint8_t(value)};send(p,sizeof(p));}
    void plot(unsigned mode,int x,int y){
        const uint8_t p[]={25,uint8_t(mode),uint8_t(x),uint8_t(x>>8),uint8_t(y),uint8_t(y>>8)};send(p,sizeof(p));
    }
    void rect(int x,int y,int w,int h,unsigned value){colour(value);plot(4,x,y);plot(0x65,x+w-1,y+h-1);}
    void line(int x,int y,int x2,int y2,unsigned value){colour(value);plot(4,x,y);plot(5,x2,y2);}
    void circle(int x,int y,int r,unsigned value){colour(value);plot(4,x,y);plot(0x95,x+r,y);}
    void text(unsigned x,unsigned y,const char*s,unsigned fg,unsigned bg){
        const uint8_t p[]={4,17,uint8_t(fg),17,uint8_t(bg+128),31,uint8_t(x),uint8_t(y)};
        send(p,sizeof(p));send(reinterpret_cast<const uint8_t*>(s),strlen(s));
    }
};
struct ModeIO {
    int expected_mode=-1;
    bool query(test_appliance::Mode &out){
        sysvars[sysvar_vdp_pflags]&=uint8_t(~vdp_pflag_mode);
        const uint8_t p[]={23,0,0x86};if(!write_bytes(p,sizeof(p)))return false;
        auto start=ticks();uint32_t fuse=8000000;
        // Stock VDP v2.16.0 vdu_fonts.h emits unsolicited mode information
        // when selecting/deleting fonts. Cleanup can leave a mode20 reply
        // ahead of the selected entry-mode reply. A shared completion flag
        // cannot identify which request produced it. Keep the one query
        // outstanding and consume replies until the selected mode arrives;
        // never mistake that earlier font reply for failed restoration.
        while(uint24_t(ticks()-start)<600&&--fuse){
            if(!(sysvars[sysvar_vdp_pflags]&vdp_pflag_mode))continue;
            out={sysvars[sysvar_scrMode],uint16_t(getsysvar_scrwidth()),uint16_t(getsysvar_scrheight()),sysvars[sysvar_scrColours]};
            if(out.width&&out.height&&out.colours&&
               (expected_mode<0||out.number==expected_mode)){
                expected_mode=-1;return true;
            }
            sysvars[sysvar_vdp_pflags]&=uint8_t(~vdp_pflag_mode);
        }
        expected_mode=-1;return false;
    }
    bool cli_supported(const test_appliance::Mode&s){return s.number<128;}
    bool select(uint8_t mode){
        const uint8_t p[]={22,mode};
        if(!write_bytes(p,sizeof(p)))return false;
        expected_mode=mode;return true;
    }
    bool settle(){
        // Nominal sysvar clock advances twice per60/70Hz VBlank.160ticks
        // exceeds one second on either, with an independent stopped-clock fuse.
        auto start=ticks();uint32_t fuse=10000000;
        while(uint24_t(ticks()-start)<160&&--fuse){}
        return fuse!=0;
    }
    bool prepare_cli(){
        const uint8_t p[]={4,26,23,0,0x95,0,255,255,0,17,15,17,128,18,0,15,23,1,1,12};
        return write_bytes(p,sizeof(p));
    }
};
static uint16_t read16(const uint8_t*p){return uint16_t(p[0])|uint16_t(p[1])<<8;}
static uint32_t read32(const uint8_t*p){return uint32_t(read16(p))|uint32_t(read16(p+2))<<16;}
struct Replay {
    FILE *file=nullptr;
    uint8_t row[54]{};
    uint32_t remaining{},duration{};
    bool pending=false,failed=false;
    bool open(const char*path){
        file=fopen(path,"rb");if(!file)return false;
        uint8_t header[16];
        if(fread(header,1,sizeof(header),file)!=sizeof(header)||memcmp(header,"CVR1",4)||read32(header+12))return false;
        remaining=read32(header+4);duration=read32(header+8);
        return remaining&&remaining<=100000&&duration<=3600000;
    }
    bool advance(uint32_t elapsed,controller_view::Sample &s){
        while(remaining||pending){
            if(!pending){
                if(fread(row,1,sizeof(row),file)!=sizeof(row)){failed=true;return false;}
                --remaining;pending=true;
            }
            if(read32(row)>elapsed)return true;
            s.sequence=read32(row+4);s.generation=read16(row+8);
            s.connected=row[10]&1;s.valid=row[10]&2;s.replay=true;
            if(row[11]||(row[10]&~3)||row[10]==2){failed=true;return false;}
            for(unsigned i=0;i<4;++i)s.stick[i]=int16_t(read16(row+12+i*2));
            memcpy(s.trigger,row+20,2);s.held=read16(row+22);
            if((s.held&0x8000)||(s.held&0x1800)==0x1800||(s.held&0x6000)==0x6000){failed=true;return false;}
            for(unsigned i=0;i<15;++i)s.presses[i]=read16(row+24+i*2);
            pending=false;
        }
        return true;
    }
    void close(){if(file)fclose(file);file=nullptr;}
};
int main(int argc,char **argv){
    puts(CONTROLLER_BUILD_ID " (experimental)");
    const bool recorded=argc>1&&!strcmp(argv[1],"replay");
    if(argc>1&&!recorded){
        puts("Usage: ctrlview [replay [capture.cvr]]");return 19;
    }
    Replay replay;
    if(recorded&&!replay.open(argc>2?argv[2]:"/extender/controller/capture.cvr")){
        replay.close();puts("Cannot open valid controller replay.");return 1;
    }
    if(!recorded&&!live.open()){
        printf("EMOS controller service unavailable (status%u).\r\n",live.error);return 1;
    }
    sysvars=mos_sysvars();ModeIO io;test_appliance::ModeSession<ModeIO> mode(io);
    bool ok=mode.begin({20,512,384,64});
    if(!ok){replay.close();live.close();mode.restore();puts("Mode20 unavailable or entry cleanup unsupported.");return 1;}
    // Temporary font buffer64001 belongs to this appliance until cleanup.
    const uint8_t setup[]={23,1,0,23,0,192,0,26,29,0,0,0,0,23,0,160,1,250,2,
                          23,0,160,1,250,0,0,32};
    ok=write_bytes(setup,sizeof(setup))&&write_bytes(controller_font,sizeof(controller_font));
    const uint8_t font[]={23,0,0x95,1,1,250,12,16,14,0,23,0,0x95,0,1,250,0};
    ok=write_bytes(font,sizeof(font))&&ok;
    Canvas canvas;controller_view::View<Canvas> view(canvas);controller_view::Sample sample{};sample.replay=recorded;
    // No controller request may be outstanding during the first, complete
    // screen draw: rendering must not consume the resident transport deadline.
    view.paint(sample);ok=ok&&canvas.healthy;
    char link_error[43]{};
    const auto start=ticks();auto last=start;
    uint32_t elapsed_ticks=0,next_paint=0,next_input=0,fuse=20000000;
    bool exit=false,r_down=false,link_ok=true;
    while(ok&&!exit&&fuse){
        --fuse;
        auto now=ticks();uint24_t delta=uint24_t(now-last);last=now;elapsed_ticks+=delta;
        if(delta)fuse=20000000;
        if(recorded)ok=replay.advance(elapsed_ticks*1000/120,sample);
        else if(link_ok&&elapsed_ticks>=next_input){
            link_ok=live.update(sample);next_input=elapsed_ticks+2;
            if(!link_ok){
                sample.valid=sample.connected=false;
                snprintf(link_error,sizeof(link_error),"EMOS link lost: %s %u",
                         live.error_operation==1?"read":live.error_operation==2?"request":"service",
                         unsigned(live.error));
                view.status(link_error);
            }
        }
        if(!ok)break;
        // Six sysvar units give nominal20Hz, staying below30Hz even when an
        // unchanged mainboard clock runs at70Hz while Extender displays mode20.
        if(elapsed_ticks>=next_paint){view.paint(sample);next_paint=elapsed_ticks+6;}
        auto key=sysvars[sysvar_keyascii];
        if(sysvars[sysvar_vkeydown]&&key==27)exit=true;
        bool current_r=sysvars[sysvar_vkeydown]&&(key=='r'||key=='R');
        if(current_r&&!r_down)view.reset_counts(sample);
        r_down=current_r;
        ok=ok&&canvas.healthy;
    }
    replay.close();
    ok=live.close()&&ok;
    // Select built-in font before releasing the temporary buffer, even when
    // the entry mode already was20. The route and startup are never changed.
    const uint8_t cleanup[]={4,23,0,0x95,0,255,255,0,23,0,0x95,4,1,250,23,0,160,1,250,2};
    ok=write_bytes(cleanup,sizeof(cleanup))&&ok;
    bool restored=mode.restore();
    if(link_error[0])puts(link_error);
    puts(!restored?"Controller viewer cleanup failed.":!ok||!fuse?"Controller viewer failed.":"Controller viewer closed.");
    return ok&&restored&&fuse?0:1;
}
