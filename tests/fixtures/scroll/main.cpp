// SCROLL-001: eight finite single-buffer cases. Modes are selected in startup,
// never here. MOS/EMOS owns all VDU output and the admitted QTG diagnostic reply.
// SD and reverse replies occur only before/after each measured case.
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "selection.hpp"

extern "C" uint24_t bench_clock(const volatile uint8_t *);
extern "C" uint24_t bench_count(const uint8_t *, uint24_t);
extern "C" void graphics_callback(void);

static volatile uint8_t *sv;
static volatile bool armed, received, duplicate;
static volatile uint16_t expected;
static volatile uint8_t metric, source=255;
static volatile uint32_t value, count;
static uint8_t packet[29];
static unsigned width, height, margin, steps, mode, colours, instrument;
static char result_base[128],result_path[128];
static uint32_t u32(const uint8_t *p) {
    return uint32_t(p[0]) | uint32_t(p[1])<<8 | uint32_t(p[2])<<16 | uint32_t(p[3])<<24;
}
extern "C" void graphics_receive(const uint8_t *p) {
    if (!armed || memcmp(p,"QTG\xA1",4) || uint16_t(p[4]|uint16_t(p[5])<<8)!=expected || p[7]>1) return;
    if(source==255) source=p[7];
    if(source!=p[7]) return;
    if(received) {duplicate=true;return;}
    metric=p[6];value=u32(p+8);count=u32(p+12);received=true;
}
static uint24_t clock_ticks() {return bench_clock(sv);}
static bool send(const uint8_t *p,unsigned n) {return bench_count(p,n)==0;}
static bool request(unsigned op,unsigned token,unsigned flags=0) {
    expected=token;received=duplicate=false;armed=true;
    uint8_t p[]={23,0,0xEF,uint8_t(op),uint8_t(token),uint8_t(token>>8),uint8_t(flags)};
    bool ok=send(p,sizeof p);auto start=clock_ticks();uint32_t budget=8000000;
    while(ok&&!received&&!duplicate&&uint24_t(clock_ticks()-start)<1200&&--budget) {}
    armed=false;return ok&&received&&!duplicate;
}
static void word(uint8_t *p,int v) {p[0]=uint8_t(v);p[1]=uint8_t(v>>8);}
static void viewport(uint8_t *p,int x,int y,int w,int h) {
    p[0]=24;word(p+1,x);word(p+3,y+h-1);word(p+5,x+w-1);word(p+7,y);
}
static bool pace() {
    uint8_t before=sv[sysvar_time];uint32_t budget=8000000;
    while(sv[sysvar_time]==before&&--budget) {}
    return budget!=0;
}
static bool load_pattern(unsigned id) {
    char path[24];snprintf(path,sizeof path,"c%02u.vdu",id);
    uint8_t f=mos_fopen(path,FA_READ);if(!f)return false;
    uint8_t block[4096];bool ok=true;
    while(ok) {auto n=mos_fread(f,(char*)block,sizeof block);if(!n)break;ok=send(block,n);}
    mos_fclose(f);return ok;
}
static bool update(unsigned id,unsigned step) {
    unsigned direction=id%4;bool partial=id>=4;
    int x=0,y=0,w=width,h=height,dx=0,dy=0;
    if(partial) {if(direction<2){x=margin;w-=2*margin;}else{y=margin;h-=2*margin;}}
    viewport(packet,x,y,w,h);
    packet[9]=23;packet[10]=7;packet[11]=partial?2:1;
    static const uint8_t dirs[]={3,2,1,0};packet[12]=dirs[direction];packet[13]=1;
    if(direction==0) {dy=h-1-int(step%h);viewport(packet+14,x,y+h-1,w,1);}
    if(direction==1) {dy=-h+1+int(step%h);viewport(packet+14,x,y,w,1);}
    if(direction==2) {dx=w-1-int(step%w);viewport(packet+14,x+w-1,y,1,h);}
    if(direction==3) {dx=-w+1+int(step%w);viewport(packet+14,x,y,1,h);}
    packet[23]=25;packet[24]=0xED;word(packet+25,dx);word(packet+27,dy);
    return send(packet,sizeof packet);
}
static bool run_case(unsigned id,uint8_t file) {
    bool ok=load_pattern(id);
    if(ok)ok=request(1,id,instrument)&&metric==0&&value==1&&count==instrument;
    uint24_t start=clock_ticks(),previous=start;unsigned missed=0,done=0;
    for(;done<steps&&ok;++done) {
        ok=pace();auto edge=clock_ticks();auto delta=uint24_t(edge-previous);
        if(delta>2)missed+=delta/2-1;
        previous=edge;if(ok)ok=update(id,done);
    }
    auto elapsed=uint24_t(clock_ticks()-start);
    if(ok)ok=request(2,id)&&metric==1;
    bool valid=true;
    for(unsigned detail=1;detail<=12&&ok;++detail) {
        uint32_t v=value,c=count;
        if(detail!=1){ok=request(4,id,detail)&&metric==detail;v=value;c=count;}
        if(!ok)break;
        if(instrument&&((detail==9||detail==11)&&c!=steps))valid=false;
        if(instrument&&(detail==3||detail==5||detail==10||detail==12)&&c)valid=false;
        char line[200];int n=snprintf(line,sizeof line,"%s,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%lu,%lu\r\n",
            scroll_fixture::names[id],source,mode,width,height,margin,instrument,done,elapsed,missed,
            detail,(unsigned long)v,(unsigned long)c);
        ok=mos_fwrite(file,line,n)==unsigned(n);
    }
    return ok&&valid;
}
int main(int argc,char **argv) {
    int selected=argc>=2?scroll_fixture::select(argv[1]):-1;
    const char *label=argc==3?argv[2]:nullptr;
    if(argc<2||argc>3||selected<0||(label&&!scroll_fixture::valid_label(label))) {
        puts("Usage: RUN &040000 <case|all> [run-label]");
        for(auto name:scroll_fixture::names)puts(name);
        return 1;
    }
    source=255;armed=received=duplicate=false;
    sv=mos_sysvars();
    FILE *cfg=fopen("scroll.cfg","r");if(!cfg){puts("Missing scroll.cfg");return 1;}
    int fields=fscanf(cfg,"%u %u %u %u %u %u %u %127s",&width,&height,&margin,
                      &steps,&mode,&colours,&instrument,result_base);fclose(cfg);
    if(fields!=8||width<1||height<1||width>32767||height>32767||margin*2>=width||margin*2>=height||
       steps<1||steps>10000||instrument>1||mode>=128||
       strncmp(result_base,"/agents/extender/results/",25)||
       sv[sysvar_scrMode]!=mode||getsysvar_scrwidth()!=width||getsysvar_scrheight()!=height||
       sv[sysvar_scrColours]!=colours) {puts("Invalid configuration or startup mode");return 1;}
    mos_setkbvector(graphics_callback,0);
    bool ok=request(11,65535)&&metric==0&&value==0x534331&&count==12;
    // The capability probe prevents ordinary/unextended firmware producing an
    // apparently valid measurement. No measured work has begun on failure.
    if(!ok){mos_setkbvector(nullptr,0);puts("SCROLL-001 timing firmware required");return 1;}
    unsigned length=strlen(result_base);
    if(length<4||strcmp(result_base+length-4,".csv")) {
        mos_setkbvector(nullptr,0);puts("Result base must end in .csv");return 1;
    }
    result_base[length-4]=0;
    int path_length=snprintf(result_path,sizeof result_path,"%s-%s-%s%s%s.csv",result_base,
        source==0?"mb":"ext",argv[1],label?"-":"",label?label:"");
    if(path_length<0||unsigned(path_length)>=sizeof result_path) {
        mos_setkbvector(nullptr,0);puts("Result path too long");return 1;
    }
    uint8_t file=mos_fopen(result_path,FA_WRITE|FA_CREATE_NEW);
    if(!file){mos_setkbvector(nullptr,0);puts("Results already exist or cannot be created");return 1;}
    const char *header="case,source,mode,width,height,margin,instrument,updates,mos_ticks,missed_slots,metric,value_us,count_or_crossing\r\n";
    ok=mos_fwrite(file,(char*)header,strlen(header))==strlen(header);
    auto suite_start=clock_ticks();
    if(ok)ok=scroll_fixture::dispatch(selected,[&](unsigned id){return run_case(id,file);});
    auto suite_end=clock_ticks();char duration[90];
    int duration_n=snprintf(duration,sizeof duration,"SUITE,%u,%u,%u\r\n",suite_start,suite_end,uint24_t(suite_end-suite_start));
    ok=mos_fwrite(file,duration,duration_n)==unsigned(duration_n)&&ok;
    const char *terminal=ok?"PASS complete\r\n":"FAIL incomplete\r\n";
    bool saved=mos_fwrite(file,(char*)terminal,strlen(terminal))==strlen(terminal);
    mos_fclose(file);mos_setkbvector(nullptr,0);ok=ok&&saved;
    uint8_t reset[]={26,23,1,1,12};send(reset,sizeof reset);
    const char *message=selected==8?(ok?"Scrolling batch complete. Results saved.":"Scrolling batch failed. Preserve results."):
                                  (ok?"Scrolling test complete. Results saved.":"Scrolling test failed. Preserve results.");
    puts(message);puts(result_path);
    if(source<=1) {
        // Preserve the first completion cue while repeating it on the other
        // display. Finish in Legacy. EMOS owns routing; no mode changes occur.
        char legacy[]="EMOS LEGACY --keep-display";
        char excom[]="EMOS EXCOM --keep-display";
        if(mos_oscli(source==1?legacy:excom,nullptr,0)==0) {
            send(reset,sizeof reset);
            puts(message);puts(result_path);
            if(source==0)mos_oscli(legacy,nullptr,0);
        }
    }
    return ok?0:1;
}
