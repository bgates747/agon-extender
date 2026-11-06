/* SPDX-License-Identifier: GPL-3.0-only: actual portable utility core tests. */
#include "setup.h"
#include <assert.h>
#include <string.h>
#include <stdlib.h>
struct peer {
 uint32_t clock,ready;
 char rx[14000],tx[500],log[50000],payload[30];
 size_t ri,rn,tn,ln,pn;unsigned pending,queries,commands;
 int scenario,phase,escape_phase,log_calls,closed;unsigned dropped;
};
static const char *password="s3c,\"ret\\phrase";
static uint32_t now(void *v) {return ((struct peer*)v)->clock;}
static int esc(void *v) {struct peer *p=v;return p->escape_phase&&p->phase==p->escape_phase;}
static void enqueue(struct peer *p,const char *s,unsigned delay) {
 assert(p->ri==p->rn);p->ri=0;p->rn=strlen(s);assert(p->rn<sizeof(p->rx));memcpy(p->rx,s,p->rn);p->ready=p->clock+delay;
}
static int rx(void *v) {struct peer *p=v;if((int32_t)(p->clock-p->ready)<0||p->ri==p->rn||(p->scenario==19&&p->clock%3))return -1;return (unsigned char)p->rx[p->ri++];}
static void idle(void *v) {struct peer *p=v;if(p->scenario!=12)p->clock++;}
static int msg(void *v,const char *s) {
 struct peer *p=v;
 /* A synchronous screen/card write leaves only the first16 unread UART bytes.
  * The host transcript already exists; subsequent arriving bytes are lost. */
 if(((p->scenario==21&&p->phase==11)||(p->scenario==22&&p->phase==9))&&p->rn-p->ri>16) {
  p->dropped+=(unsigned)(p->rn-p->ri-16);p->rn=p->ri+16;
 }
 size_t n=strlen(s);assert(p->ln+n+2<sizeof(p->log));memcpy(p->log+p->ln,s,n);p->ln+=n;p->log[p->ln++]='\n';p->log[p->ln]=0;p->log_calls++;
 return !(p->scenario==11&&p->log_calls>=5);
}
static void frame(struct peer *p,const char *text,int close) {
 char out[2500];snprintf(out,sizeof(out),"\r\nSEND OK\r\n+IPD,%u:%s%s",(unsigned)strlen(text),text,close?"\r\nCLOSED\r\n":"");enqueue(p,out,0);
}
static void command(struct peer *p) {
 char out[900];p->commands++;
 if(!strcmp(p->tx,"AT")) {
  p->phase=1;if(p->scenario==1||p->scenario==12)return;
  enqueue(p,"AT\r\nOK\r\n",p->scenario==2?360:0);
 } else if(!strcmp(p->tx,"ATE0")) {p->phase=2;enqueue(p,"OK\r\n",0);}
 else if(!strcmp(p->tx,"AT+GMR")) {p->phase=3;enqueue(p,"AT version:1.3.0.0\r\nSDK version:2.0.0\r\nOK\r\n",0);}
 else if(!strcmp(p->tx,"AT+CWMODE_CUR=1")) {p->phase=4;enqueue(p,"OK\r\n",0);}
 else if(!strcmp(p->tx,"AT+CWDHCP_CUR=1,1")) {p->phase=5;enqueue(p,p->scenario==3?"ERROR\r\n":"OK\r\n",0);}
 else if(!strncmp(p->tx,"AT+CWJAP_CUR=",13)) {
  p->phase=6;
  if(p->scenario==4)return;
  snprintf(out,sizeof(out),"%s\r\nWIFI CONNECTED\r\nWIFI GOT IP\r\n%s\r\n",p->tx,p->scenario==5?"FAIL":"OK");enqueue(p,out,p->scenario==2?600:0);
 } else if(!strcmp(p->tx,"AT+CIFSR")) {
  p->phase=7;p->queries++;
  snprintf(out,sizeof(out),"+CIFSR:STAIP,\"%s\"\r\n+CIFSR:STAMAC,\"ac:0b:fb:d1:c4:ac\"\r\nOK\r\n",(p->scenario==6||(p->scenario==7&&p->queries==1))?"0.0.0.0":"192.0.2.15");enqueue(p,out,0);
 } else if(!strcmp(p->tx,"AT+CIPMODE=0")||!strcmp(p->tx,"AT+CIPMUX=0")||!strcmp(p->tx,"AT+CIPDINFO=0")) {p->phase=8;enqueue(p,"OK\r\n",0);}
 else if(!strncmp(p->tx,"AT+CIPSTART=",12)) {
  p->phase=9;
  if(p->scenario==8)enqueue(p,"ERROR\r\n",0);
  else if(p->scenario==9)enqueue(p,"CONNECT\r\nOK\r\n+IPD,99999:bad",0);
  else {
   const char *welcome=p->scenario==22?"wifi-bbs-r01-b2026-11-06-04-03-51Z (experimental)\r\nPi Wi-Fi BBS. Type help.\r\nbbs> ":"test BBS\r\nbbs> ";snprintf(out,sizeof(out),"CONNECT\r\nOK\r\n+IPD,%u:%s",(unsigned)strlen(welcome),welcome);enqueue(p,out,0);
  }
 } else if(!strncmp(p->tx,"AT+CIPSEND=",11)) {p->phase=10;p->pending=(unsigned)atoi(p->tx+11);p->pn=0;assert(p->pending<sizeof(p->payload));enqueue(p,p->scenario==14?"ERROR\r\n":p->scenario==15?"":"OK\r\n> ",0);}
 else {fprintf(stderr,"Unexpected command: %s\n",p->tx);abort();}
}
static int tx(void *v,unsigned char c) {
 struct peer *p=v;
 if(p->scenario==10)return 0;
 if(p->scenario==13&&p->clock<360)return 0;
 if(p->pending) {
  p->phase=11;p->payload[p->pn++]=(char)c;
  if(--p->pending==0) {
   p->payload[p->pn]=0;
   if(p->scenario==16)enqueue(p,"SEND FAIL\r\n",0);
   else if(p->scenario==17)enqueue(p,"SEND OK\r\n+IPD,20:truncated",0);
   else if(!strcmp(p->payload,"quit\r\n"))frame(p,"Goodbye.\r\n",1);
   else if(p->scenario==23) {
    const char *body="Reply before SEND OK.\r\nbbs> ";char reordered[200];
    snprintf(reordered,sizeof(reordered),"+IPD,%u:%s\r\nSEND OK\r\n",(unsigned)strlen(body),body);enqueue(p,reordered,0);
   }
   else if(p->scenario==21)frame(p,"help | time | uptime | note TEXT | notes | quit\r\nNotes: 1-60 printable characters; notes shows the last three.\r\nbbs> ",0);
   else if(p->scenario==20)frame(p,"secret-long and secret must be redacted.\r\nbbs> ",0);
   else if(p->scenario==18)frame(p,"ERROR is just BBS text; OK too.\r\nbbs> ",0);
   else frame(p,"Useful BBS data.\r\nbbs> ",0);
  }
 } else {
  assert(p->tn+1<sizeof(p->tx));
  if(c=='\n') {if(p->tn&&p->tx[p->tn-1]=='\r')p->tn--;p->tx[p->tn]=0;command(p);p->tn=0;}
  else p->tx[p->tn++]=(char)c;
 }
 return 1;
}
static int file_next(void *p) {int c=fgetc(p);return c==EOF?(ferror(p)?-2:-1):c;}
static int read_config(FILE *f,struct ws_config *c,char *e,size_t n,int (*cancel)(void *),void *ctx) {
 struct ws_reader r={f,file_next};return ws_read_config(&r,c,e,n,cancel,ctx);
}
static int always_cancel(void *ctx) {(void)ctx;return 1;}
static int read_error(void *ctx) {(void)ctx;return -2;}
static void config_tests(void) {
 const char *valid="ssid=home\npassword=a,\"b\\c#\nbbs_host=example.invalid\nbaud=115200\n";
 const char *invalid[]={"ssid=x\npassword=p\nbbs_host=h\nssid=y\n","ssid=x\npassword=p\nbbs_host=h\nunknown=y\n","ssid=x\npassword=p\nbbs_host=h\njoin_seconds=0\n","ssid=x\npassword=p\nbbs_host=a,b\n","ssid=x\npassword=p\nbbs_host=h\ntick_hz=1000\n","ssid=x\npassword=p\nbbs_host=h\nbaud=230400\n","password=p\nbbs_host=h\n"};
 struct ws_config c;char error[160];FILE *f=tmpfile();assert(f);fputs(valid,f);rewind(f);assert(!read_config(f,&c,error,sizeof(error),NULL,NULL));fclose(f);assert(c.baud==115200&&c.tick_hz==120&&!strcmp(c.password,"a,\"b\\c#"));
 for(unsigned i=0;i<sizeof(invalid)/sizeof(*invalid);i++) {f=tmpfile();fputs(invalid[i],f);rewind(f);assert(read_config(f,&c,error,sizeof(error),NULL,NULL)==WS_CONFIG);assert(!strstr(error,"password=p"));fclose(f);}
 f=tmpfile();fputs("ssid=x\npassword=\nbbs_host=h",f);rewind(f);assert(!read_config(f,&c,error,sizeof(error),NULL,NULL));fclose(f);
 f=tmpfile();fwrite("ssid=x\0evil",1,11,f);rewind(f);assert(read_config(f,&c,error,sizeof(error),NULL,NULL)==WS_CONFIG);fclose(f);
 f=tmpfile();for(int i=0;i<4097;i++)fputc('\n',f);rewind(f);assert(read_config(f,&c,error,sizeof(error),NULL,NULL)==WS_CONFIG);fclose(f);
 f=tmpfile();fputs(valid,f);rewind(f);assert(read_config(f,&c,error,sizeof(error),always_cancel,NULL)==WS_CANCEL);fclose(f);
 {struct ws_reader r={NULL,read_error};assert(ws_read_config(&r,&c,error,sizeof(error),NULL,NULL)==WS_CONFIG);}

}
static int run(int scenario,int escape_phase,uint32_t clock,unsigned hz) {
 static struct peer p;static struct ws_state s;struct ws_config c;struct ws_io io;int result;
 memset(&p,0,sizeof(p));p.scenario=scenario;p.escape_phase=escape_phase;p.clock=clock;
 ws_defaults(&c);strcpy(c.ssid,"private-home");strcpy(c.password,password);strcpy(c.host,"bbs.example.invalid");c.tick_hz=hz;c.join_seconds=8;
 if(scenario==20) {strcpy(c.ssid,"secret");strcpy(c.password,"secret-long");}
 io.ctx=&p;io.now=now;io.escape=esc;io.receive=rx;io.transmit=tx;io.idle=idle;io.message=msg;
 result=ws_run(&s,&c,&io);
 assert(!strstr(p.log,password)&&!strstr(p.log,"private-home")&&!strstr(p.log,"s3c\\,\\\"ret\\\\phrase"));
 assert(!s.cfg.password[0]&&!s.cfg.ssid[0]);
 if(scenario==20)assert(!strstr(p.log,"secret-long")&&!strstr(p.log,"-long"));
 if(scenario==1||scenario==2||scenario==4||scenario==6||scenario==10||scenario==13)assert(strstr(p.log,"Still waiting"));
 if(escape_phase) {assert(result==WS_CANCEL);assert(strstr(p.log,"Escape pressed"));}
 else {
  int expected=WS_OK;
  if(scenario==1||scenario==4||scenario==6||scenario==10||scenario==15||scenario==17)expected=WS_TIMEOUT;
  if(scenario==3||scenario==5||scenario==8||scenario==14||scenario==16)expected=WS_MODEM;
  if(scenario==9)expected=WS_PROTOCOL;
  if(scenario==11)expected=WS_LOG;
  if(scenario==12)expected=WS_CLOCK;
  if(result!=expected)fprintf(stderr,"scenario%d: result%d expected%d\n%s",scenario,result,expected,p.log);
  assert(result==expected);
  if(scenario==21||scenario==22)assert(!p.dropped);
  if(!result)assert(strstr(p.log,"Success:")&&strstr(p.log,"BBS reply:")&&strstr(p.log,"BBS request: time"));
 }
 return result;
}
int main(int argc,char **argv) {
 if(argc==2) {run(atoi(argv[1]),0,0,120);return 0;}
 config_tests();
 for(int i=0;i<=23;i++)run(i,0,0,120);
 for(int i=1;i<=11;i++)run(0,i,0,120);
 run(0,0,0xfffffff0UL,120);run(0,0,0,100);
 puts("PASS: config cases,24 AT scenarios,11 cancellation phases, clock wrap and100Hz.");return 0;
}
