/* SPDX-License-Identifier: GPL-3.0-only */
#include "setup.h"
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
static int bad(char *e,size_t n,unsigned line,const char *why) {
 snprintf(e,n,"Configuration line %u: %s (value not shown).",line,why);return WS_CONFIG;
}
void ws_defaults(struct ws_config *c) {
 memset(c,0,sizeof(*c));c->port=2323;c->baud=115200;c->tick_hz=120;
 c->command_seconds=5;c->join_seconds=60;c->bbs_seconds=10;strcpy(c->ping_host,"gateway");
}
static int read_config(const struct ws_reader *f,struct ws_config *c,char *e,size_t en,int (*cancel)(void *),void *ctx,int startup) {
 char line[256];unsigned num=0,seen=0,total=0;ws_defaults(c);
 for(;;) {
  char *p=line,*eq,*end,*val;unsigned bit=0;size_t n=0;int ch;
  for(;;) {
   if(cancel&&cancel(ctx)) {snprintf(e,en,"Escape pressed while reading configuration.");return WS_CANCEL;}
   ch=f->next(f->ctx);
   if(ch==-2)return bad(e,en,num+1,"read failed");
   if(ch==-1)break;
   if(++total>4096)return bad(e,en,num+1,"file too long");
   if(ch=='\n')break;
   if(n+1>=sizeof(line))return bad(e,en,num+1,"line too long");
   if(ch==0)return bad(e,en,num+1,"embedded NUL");
   line[n++]=(char)ch;
  }
  if(ch==-1&&!n)break;
  num++;if(n&&line[n-1]=='\r')n--;line[n]=0;
  for(size_t i=0;i<n;i++)if((unsigned char)line[i]<32||(unsigned char)line[i]>126)return bad(e,en,num,"use printable ASCII");
  while(*p==' ')p++;
  if(!*p||*p=='#')continue;
  eq=strchr(p,'=');if(!eq)return bad(e,en,num,"expected key=value");
  *eq=0;end=eq;while(end>p&&end[-1]==' ')*--end=0;val=eq+1;
  if(!strcmp(p,"ssid"))bit=1;
  else if(!strcmp(p,"password"))bit=2;
  else if(!strcmp(p,"bbs_host"))bit=4;
  else if(!strcmp(p,"bbs_port"))bit=8;
  else if(!strcmp(p,"baud"))bit=16;
  else if(!strcmp(p,"tick_hz"))bit=32;
  else if(!strcmp(p,"command_seconds"))bit=64;
  else if(!strcmp(p,"join_seconds"))bit=128;
  else if(!strcmp(p,"bbs_seconds"))bit=256;
  else if(startup&&!strcmp(p,"auto_connect"))bit=512;
  else if(startup&&!strcmp(p,"ping_host"))bit=1024;
  else return bad(e,en,num,"unknown key");
  if(seen&bit)return bad(e,en,num,"duplicate key");
  seen|=bit;
  n=strlen(val);
  if(bit==1||bit==2||bit==4||bit==1024) {
   size_t max=bit==1?32:bit==2?64:63;
   if(n>max||(!n&&bit!=2))return bad(e,en,num,"invalid string length");
   if(bit==4||bit==1024)for(size_t i=0;i<n;i++)if(!isalnum((unsigned char)val[i])&&val[i]!='.'&&val[i]!='-')return bad(e,en,num,"invalid hostname");
   strcpy(bit==1?c->ssid:bit==2?c->password:bit==4?c->host:c->ping_host,val);
  } else {
   unsigned long v;char *tail;
   if(!*val)return bad(e,en,num,"missing number");
   for(char *q=val;*q;q++)if(!isdigit((unsigned char)*q))return bad(e,en,num,"expected decimal number");
   v=strtoul(val,&tail,10);
   if(*tail||v>(bit==16?115200UL:65535UL)||(!v&&bit!=512))return bad(e,en,num,"number out of range");
   if(bit==512) {if(v>1)return bad(e,en,num,"auto_connect must be 0 or 1");c->auto_connect=(unsigned)v;}
   if(bit==8)c->port=(unsigned)v;
   if(bit==16) {if(v!=9600&&v!=19200&&v!=38400&&v!=57600&&v!=115200UL)return bad(e,en,num,"unsupported baud");c->baud=(unsigned)v;}
   if(bit==32) {if(v!=100&&v!=120)return bad(e,en,num,"tick_hz must be 100 or 120");c->tick_hz=(unsigned)v;}
   if(bit==64||bit==128||bit==256) {
    if(v>120)return bad(e,en,num,"timeout must be 1..120 seconds");
    if(bit==64)c->command_seconds=(unsigned)v;
    if(bit==128)c->join_seconds=(unsigned)v;
    if(bit==256)c->bbs_seconds=(unsigned)v;
   }
  }
 }
 if((seen&(startup?3:7))!=(unsigned)(startup?3:7))return bad(e,en,num,startup?"ssid and password are required":"ssid, password and bbs_host are required");
 memset(line,0,sizeof(line));return WS_OK;
}

int ws_read_config(const struct ws_reader *f,struct ws_config *c,char *e,size_t en,int (*cancel)(void *),void *ctx) {return read_config(f,c,e,en,cancel,ctx,0);}
int ws_read_start_config(const struct ws_reader *f,struct ws_config *c,char *e,size_t en,int (*cancel)(void *),void *ctx) {return read_config(f,c,e,en,cancel,ctx,1);}
