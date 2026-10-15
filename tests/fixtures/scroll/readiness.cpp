// Bounded installation check, separate from the Author's 600-update tests.
// Reuse their exact callback, counter and wrap implementation. No mode changes.
#define main scroll_suite_main
#include "main.cpp"
#undef main

static bool control(uint8_t file,unsigned token,unsigned edges) {
    bool ok=request(1,token,1)&&metric==0&&value==1&&count==1;
    auto start=clock_ticks();
    for(unsigned i=0;i<edges&&ok;++i)ok=pace();
    auto ticks=uint24_t(clock_ticks()-start);
    if(ok)ok=request(2,token)&&metric==1;
    uint32_t wall=value;
    static const unsigned details[]={3,5,9,10,11,12};
    for(unsigned detail : details) {
        if(ok)ok=request(4,token,detail)&&metric==detail&&count==0;
    }
    if(ok)ok=request(4,token,8)&&metric==8&&count==256;
    if(edges&&ticks<2*edges)ok=false;
    char row[120];int n=snprintf(row,sizeof row,"CONTROL,%u,%u,%u,%lu,%u\r\n",
        source,edges,ticks,(unsigned long)wall,unsigned(ok));
    return mos_fwrite(file,row,n)==unsigned(n)&&ok;
}

int main(int argc,char **argv) {
    if(argc!=2||strcmp(argv[1],"readiness")) {
        puts("Readiness failed: RUN arguments");return 1;
    }
    width=320;height=240;margin=32;steps=3;mode=8;colours=64;instrument=1;
    source=255;armed=received=duplicate=false;sv=mos_sysvars();
    if(sv[sysvar_scrMode]!=mode||getsysvar_scrwidth()!=width||
       getsysvar_scrheight()!=height||sv[sysvar_scrColours]!=colours) {
        puts("Readiness failed: startup mode");return 1;
    }
    mos_setkbvector(graphics_callback,0);
    bool ok=request(11,65535)&&metric==0&&value==0x534331&&count==12;
    if(!ok){mos_setkbvector(nullptr,0);puts("Readiness failed: timing probe");return 1;}
    char path[100];snprintf(path,sizeof path,
        "/agents/extender/results/scroll-readiness-r01-%s.csv",source==0?"mb":"ext");
    uint8_t file=mos_fopen(path,FA_WRITE|FA_CREATE_NEW);
    if(!file){mos_setkbvector(nullptr,0);puts("Readiness failed: output exists");return 1;}
    ok=control(file,65000,0)&&control(file,65001,12);
    for(unsigned id=0;id<8&&ok;++id)ok=run_case(id,file);
    const char *terminal=ok?"PASS readiness\r\n":"FAIL readiness\r\n";
    ok=mos_fwrite(file,(char*)terminal,strlen(terminal))==strlen(terminal)&&ok;
    mos_fclose(file);mos_setkbvector(nullptr,0);
    char excom[]="EMOS EXCOM --keep-display",legacy[]="EMOS LEGACY --keep-display";
    mos_oscli(excom,nullptr,0);
    uint8_t clear[]={26,23,1,1,12};send(clear,sizeof clear);
    printf("Readiness %s: %s\n",ok?"complete":"failed",path);
    mos_oscli(legacy,nullptr,0);
    puts(ok?"Readiness complete":"Readiness failed");
    return ok?0:1;
}
