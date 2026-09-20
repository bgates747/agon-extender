// BENCH-007 diagnostic game client. Include in one C++ translation unit only.
// No SD, printf, or reply retrieval while frames are being measured.
#pragma once
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern "C" uint24_t bench_clock(const volatile uint8_t *);
extern "C" uint24_t bench_count(const uint8_t *,uint24_t);
extern "C" void graphics_callback(void);
extern "C" uint24_t gt_prt_init(void),gt_prt_read(void);
extern "C" void gt_prt_begin(void),gt_prt_close(void);
namespace gt {
// Runtime switch keeps both controls in exactly the same binary.
// Read once outside timing: timing.cfg contains ASCII 0 (host only) or 1 (markers).
static bool markers=true;
constexpr unsigned Frames=120;
struct HostRow {uint24_t active,logic,submit,pacing,total,overflow,mos_ticks;};
static HostRow host[Frames];
static volatile uint8_t *sv;
static volatile bool received,bad,armed,transport_fault;
static volatile uint32_t value,count;
static volatile uint8_t metric,source=255;
static volatile uint16_t expected;
static unsigned frame;
static uint24_t entry,logic_end,submit_end,pace_begin,mos_entry,run_start,run_end;
static uint32_t u32(const uint8_t*p){return uint32_t(p[0])|(uint32_t(p[1])<<8)|(uint32_t(p[2])<<16)|(uint32_t(p[3])<<24);}
static uint24_t now(){return bench_clock(sv);}
static bool send(unsigned op,unsigned id,unsigned detail=0){uint8_t b[]={23,0,0xEF,uint8_t(op),uint8_t(id),uint8_t(id>>8),uint8_t(detail)};return bench_count(b,sizeof b)==0;}
static bool request(unsigned op,unsigned id,unsigned detail=0){
 expected=id;received=false;bad=false;armed=true;
 bool sent=send(op,id,detail);auto at=now();uint32_t limit=8000000;
 while(sent&&!received&&!bad&&uint24_t(now()-at)<1200&&--limit){}
 armed=false;return sent&&received&&!bad&&metric!=8;
}
static bool init(){
 FILE*cfg=fopen("timing.cfg","r");if(!cfg)return false;
 int selected=fgetc(cfg);fclose(cfg);if(selected!='0'&&selected!='1')return false;markers=selected=='1';
 sv=mos_sysvars();mos_setkbvector(graphics_callback,0);frame=0;source=255;transport_fault=false;
 bool ok=gt_prt_init() && (!markers || (request(5,0)&&metric==0&&value==0x475431&&count>=Frames));
 if(!ok)mos_setkbvector(nullptr,0);
 return ok;
}
static void loop_begin(){mos_entry=now();if(frame==0)run_start=mos_entry;gt_prt_begin();entry=0;}
static void drawing_begin(){logic_end=gt_prt_read();if(markers&&!send(6,frame))transport_fault=true;}
static void drawing_end(){submit_end=gt_prt_read();if(markers&&!send(7,frame))transport_fault=true;pace_begin=gt_prt_read();}
static bool loop_end(){auto end=gt_prt_read();host[frame]={uint24_t(pace_begin-entry),uint24_t(logic_end-entry),uint24_t(submit_end-logic_end),uint24_t(end-pace_begin),uint24_t(end-entry),uint24_t(end==65535),uint24_t(now()-mos_entry)};bool done=++frame>=Frames||transport_fault;if(done)run_end=now();return done;}
static bool save(const char*path){
 gt_prt_close();
 if(transport_fault||(markers&&(!request(9,0)||value||count!=frame))){mos_setkbvector(nullptr,0);return false;}
 uint8_t f=mos_fopen(path,FA_WRITE|FA_CREATE_ALWAYS);bool ok=f!=0;char line[240];
 char header[]="source,frame,active_prt,logic_prt,submit_prt,pacing_prt,total_prt,overflow,mos_ticks,run_ticks,submitted_us,completed_us,drain_us\r\n";
 if(ok)ok=mos_fwrite(f,header,strlen(header))==strlen(header);
 for(unsigned i=0;i<frame&&ok;i++){
  uint32_t v[3]={0,0,0};for(unsigned m=1;markers&&m<=3&&ok;m++){ok=request(8,i,m)&&metric==m&&count==frame;v[m-1]=value;}
  if(!ok)break;
  auto&r=host[i];
  int n=snprintf(line,sizeof line,"%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%lu,%lu,%lu\r\n",source,i,r.active,r.logic,r.submit,r.pacing,r.total,r.overflow,r.mos_ticks,uint24_t(run_end-run_start),(unsigned long)v[0],(unsigned long)v[1],(unsigned long)v[2]);
  ok=mos_fwrite(f,line,n)==unsigned(n);
 }
 if(f)mos_fclose(f);
 mos_setkbvector(nullptr,0);return ok;
}
}
extern "C" void graphics_receive(const uint8_t*p){
 using namespace gt;
 if(!armed||p[0]!='Q'||p[1]!='T'||p[2]!='G'||p[3]!=0xA1||uint16_t(p[4]|(uint16_t(p[5])<<8))!=expected||p[7]>1)return;
 if(source==255)source=p[7];
 if(p[7]!=source)return;
 if(received){bad=true;return;}metric=p[6];value=u32(p+8);count=u32(p+12);received=true;
}
