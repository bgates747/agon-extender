/* SPDX-License-Identifier: GPL-3.0-only
 * UART admission, 115200 8N1, no-flow-control foreground polling and modest
 * byte pacing follow Radiotux Agon-Software e265db1 ifconfig/minicom. The
 * bounded parser/state machine below is project-owned. No AT passthrough,
 * interrupts, hardware ownership changes, reset or persistent credentials.
 */
#include "setup.h"
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#define STALL_POLLS 2000000UL
/* Redact entire messages before display/logging, including delayed command
 * echoes and AT-escaped credentials. No raw RX transcript is ever written. */
static void escaped(const char *src,char *dst) {
 while(*src) {if(*src=='"'||*src=='\\'||*src==',')*dst++='\\';*dst++=*src++;}*dst=0;
}
static void say(struct ws_state *s,const char *text) {
 char out[WS_REPLY+160],a[130],b[130];unsigned char mask[WS_REPLY+160];
 size_t length;
 snprintf(out,sizeof(out),"%s",text);length=strlen(out);memset(mask,0,sizeof(mask));
 escaped(s->cfg.ssid,a);escaped(s->cfg.password,b);
 /* Find every match in the original text before changing it. A shorter SSID
  * that prefixes the password must not hide the remaining password suffix. */
 for(size_t i=0;i<length;i++) {
  const char *keys[4]={s->cfg.ssid,s->cfg.password,a,b};
  for(unsigned k=0;k<4;k++) {
   size_t n=strlen(keys[k]);
   if(n&&i+n<=length&&!memcmp(out+i,keys[k],n))memset(mask+i,1,n);
  }
 }
 for(size_t i=0;i<length;i++)if(mask[i])out[i]='*';
 if(!s->io.message(s->io.ctx,out)&&!s->failed)s->failed=WS_LOG;
}
static int check(struct ws_state *s) {
 uint32_t now=s->io.now(s->io.ctx);
 if(s->io.escape(s->io.ctx)) {s->failed=WS_CANCEL;return 0;}
 if(s->failed)return 0;
 if(now!=s->last_clock) {s->last_clock=now;s->still_polls=0;}
 else {
  s->still_polls++;
  if(s->still_polls%250000UL==0)say(s,"MOS clock has not advanced during this wait; Escape still cancels. Bounded poll guard is active.");
  if(s->still_polls>=STALL_POLLS) {s->failed=WS_CLOCK;return 0;}
 }
 return 1;
}
static void append_batch(struct ws_state *s,const char *line) {
 size_t n=strlen(line);
 if(s->batch_n+n+2>=sizeof(s->batch)) {s->failed=WS_PROTOCOL;return;}
 memcpy(s->batch+s->batch_n,line,n);s->batch_n+=n;s->batch[s->batch_n++]='\n';s->batch[s->batch_n]=0;
}
static void quoted(struct ws_state *s,const char *line,const char *key,char *out,size_t cap) {
 size_t n=strlen(key);const char *e;
 if(strncmp(line,key,n))return;
 e=strchr(line+n,'"');if(!e||(size_t)(e-line-n)>=cap) {s->failed=WS_PROTOCOL;return;}
 memcpy(out,line+n,(size_t)(e-line-n));out[e-line-n]=0;
}
static void modem_line(struct ws_state *s) {
 char *p=s->line;while(*p==' ')p++;
 if(!*p)return;
 if(!strcmp(p,"OK"))s->ok=1;
 else if(!strcmp(p,"SEND OK"))s->send_ok=1;
 else if(!strcmp(p,"ERROR")||!strcmp(p,"FAIL")||!strcmp(p,"SEND FAIL")||!strcmp(p,"ALREADY CONNECTED")||!strncmp(p,"busy",4))s->error=1;
 else if(!strcmp(p,"CLOSED")) {s->closed=1;s->connected=0;}
 else if(!strcmp(p,"CONNECT"))s->connected=1;
 quoted(s,p,"+CIFSR:STAIP,\"",s->ip,sizeof(s->ip));
 quoted(s,p,"+CIFSR:STAMAC,\"",s->mac,sizeof(s->mac));
 /* Startup ping/gateway replies are parsed only as bounded modem lines.
  * The latency is reported by ESP8266, never inferred from MOS serial time. */
 quoted(s,p,"+CIPSTA_CUR:gateway:\"",s->gateway,sizeof(s->gateway));
 quoted(s,p,"+CIPSTA:gateway:\"",s->gateway,sizeof(s->gateway));
 if(p[0]=='+'&&isdigit((unsigned char)p[1])) {
  unsigned long value=0;const char *q=p+1;
  while(isdigit((unsigned char)*q)) {if(value>6553UL) {s->failed=WS_PROTOCOL;break;}value=value*10+(unsigned)(*q++-'0');}
  if(!*q&&value<=65535UL) {s->ping_ms=(unsigned)value;s->ping_seen=1;}
 }
 /* Joining may echo a complete credential-bearing command even after ATE0.
  * Store only known nonsecret status text in this phase, never its raw echo. */
 if(s->secret) {
  if(!strcmp(p,"WIFI CONNECTED")||!strcmp(p,"WIFI GOT IP")||!strcmp(p,"WIFI DISCONNECT")||!strcmp(p,"OK")||!strcmp(p,"FAIL")||!strcmp(p,"ERROR"))append_batch(s,p);
  else if(!strncmp(p,"+CWJAP:",7)&&strlen(p)==8&&isdigit((unsigned char)p[7]))append_batch(s,p);
 } else if(!strncmp(p,"AT+CWJAP",9))append_batch(s,"Credential command echo suppressed.");
 else append_batch(s,p);
}
static void consume(struct ws_state *s,unsigned char c) {
 if(s->ipd_left) {
  if(s->reply_n+1>=sizeof(s->reply)) {s->failed=WS_PROTOCOL;return;}
  s->reply[s->reply_n++]=(c=='\r'||c=='\n'||(c>=32&&c<127))?(char)c:'.';
  s->reply[s->reply_n]=0;
  if(!--s->ipd_left)s->ipd_frames++;
  return;
 }
 if(c==':'&&s->line_n>=5&&!strncmp(s->line,"+IPD,",5)) {
  char *p=s->line+5;unsigned n=0;
  if(!*p) {s->failed=WS_PROTOCOL;return;}
  while(*p) {
   if(!isdigit((unsigned char)*p)||n>204UL) {s->failed=WS_PROTOCOL;return;}
   n=n*10+(unsigned)(*p++-'0');
  }
  if(!n||n>=sizeof(s->reply)-s->reply_n) {s->failed=WS_PROTOCOL;return;}
  s->ipd_left=n;s->line_n=0;s->line[0]=0;return;
 }
 if(c=='>'&&(!s->line_n||(s->line_n==1&&s->line[0]==' '))) {s->prompt=1;s->line_n=0;s->line[0]=0;return;}
 /* The modem may send '> ' without a newline. Its trailing space is not
  * part of a subsequent +IPD header; payload spaces were handled above. */
 if(c==' '&&s->prompt&&!s->line_n)return;
 if(c=='\r')return;
 if(c=='\n') {modem_line(s);s->line_n=0;s->line[0]=0;return;}
 if(s->line_n+1>=sizeof(s->line)) {s->failed=WS_PROTOCOL;return;}
 s->line[s->line_n++]=(c>=32&&c<127)?(char)c:'.';s->line[s->line_n]=0;
}
static int pump(struct ws_state *s) {
 if(!check(s))return 0;
 /* Short batches keep Escape/deadline checks running even under RX flood. */
 unsigned got=0;
 for(unsigned i=0;i<32;i++) {int c=s->io.receive(s->io.ctx);if(c<0)break;got++;consume(s,(unsigned char)c);if(s->failed)return 0;}
 if(got)s->last_rx=s->io.now(s->io.ctx);
 s->io.idle(s->io.ctx);return check(s);
}
static void show_batch(struct ws_state *s) {
 if(s->batch_n) {say(s,s->batch);s->batch_n=0;s->batch[0]=0;}
}
static int expired(struct ws_state *s,uint32_t start,unsigned seconds) {
 return (uint32_t)(s->io.now(s->io.ctx)-start)>=(uint32_t)seconds*s->cfg.tick_hz;
}
static void breadcrumb(struct ws_state *s,const char *what,uint32_t start,uint32_t *last,unsigned bound) {
 uint32_t now=s->io.now(s->io.ctx);
 if((uint32_t)(now-*last)>=(uint32_t)2*s->cfg.tick_hz&&
    (uint32_t)(now-s->last_rx)>=s->cfg.tick_hz/4) {
  char msg[180];*last=now;
  snprintf(msg,sizeof(msg),"Still waiting for %s: %lu / %u seconds. Escape cancels.",what,(unsigned long)((uint32_t)(now-start)/s->cfg.tick_hz),bound);say(s,msg);
 }
}
static int transmit(struct ws_state *s,const char *data) {
 uint32_t start=s->io.now(s->io.ctx),last=start;
 for(size_t i=0;data[i];) {
  int sent;if(!pump(s))return 0;
  sent=s->io.transmit(s->io.ctx,(unsigned char)data[i]);
  if(sent<0) {s->failed=WS_MODEM;return 0;}
  if(sent)i++;
  if(expired(s,start,s->cfg.command_seconds)) {s->failed=WS_TIMEOUT;return 0;}
  breadcrumb(s,"UART transmit readiness",start,&last,s->cfg.command_seconds);
 }
 return 1;
}
enum { WAIT_OK,WAIT_PROMPT,WAIT_CONNECT,WAIT_REPLY,WAIT_QUIT };
static int wait_for(struct ws_state *s,int target,unsigned seconds,const char *what) {
 uint32_t start=s->io.now(s->io.ctx),last=start;
 while(pump(s)) {
  int reply_ready=!s->ipd_left&&s->reply_n>=5&&!strcmp(s->reply+s->reply_n-5,"bbs> ");
  int done=(target==WAIT_OK&&s->ok)||(target==WAIT_PROMPT&&s->prompt)||
    (target==WAIT_CONNECT&&s->ok&&s->connected&&reply_ready)||
    (target==WAIT_REPLY&&s->send_ok&&reply_ready)||
    (target==WAIT_QUIT&&s->send_ok&&s->closed&&!s->ipd_left&&s->reply_n);
  if(s->error) {s->uncertain=0;s->failed=WS_MODEM;break;}
  if(done) {if(target!=WAIT_PROMPT)s->uncertain=0;show_batch(s);return !s->failed;}
  if(s->closed&&target!=WAIT_QUIT) {s->failed=WS_PROTOCOL;break;}
  if(expired(s,start,seconds)) {s->failed=WS_TIMEOUT;break;}
  breadcrumb(s,what,start,&last,seconds);
 }
 show_batch(s);return 0;
}
static void flags(struct ws_state *s) {s->ok=s->send_ok=s->prompt=s->closed=s->error=0;}
static int command_wait(struct ws_state *s,const char *cmd,unsigned seconds,const char *what,int secret,int target) {
 char text[280];flags(s);s->secret=secret;
 snprintf(text,sizeof(text),"Request: %s",secret?"AT+CWJAP_CUR=<credentials redacted>":cmd);say(s,text);
 snprintf(text,sizeof(text),"Waiting for %s (up to %u seconds; Escape cancels).",what,seconds);say(s,text);
 s->uncertain=1;
 if(!transmit(s,cmd)||!transmit(s,"\r\n"))return 0;
 return wait_for(s,target,seconds,what);
}
static int command(struct ws_state *s,const char *cmd,unsigned seconds,const char *what,int secret) {
 return command_wait(s,cmd,seconds,what,secret,WAIT_OK);
}
static int send_bbs(struct ws_state *s,const char *request,int final) {
 char cmd[50],msg[100];flags(s);s->secret=0;
 snprintf(cmd,sizeof(cmd),"AT+CIPSEND=%u",(unsigned)strlen(request));
 snprintf(msg,sizeof(msg),"BBS request: %s",request);say(s,msg);
 s->uncertain=1;s->data_pending=1;
 if(!transmit(s,cmd)||!transmit(s,"\r\n")||!wait_for(s,WAIT_PROMPT,s->cfg.command_seconds,"ESP8266 send prompt"))return 0;
 if(!transmit(s,request))return 0;
 s->data_pending=0;
 /* Do not print or sync SEND OK metadata while +IPD is still arriving.
  * With a16-byte polled UART FIFO, that I/O gap loses a fast BBS reply.
  * Complete the logical transaction before emitting either metadata or data. */
 if(!wait_for(s,final?WAIT_QUIT:WAIT_REPLY,s->cfg.bbs_seconds,final?"BBS goodbye and TCP closure":"SEND OK and complete BBS reply"))return 0;
 if(!s->reply_n) {s->failed=WS_PROTOCOL;return 0;}
 say(s,"BBS reply:");say(s,s->reply);s->reply_n=0;s->reply[0]=0;return !s->failed;
}
static int address_valid(const char *ip,const char *mac) {
 const char *p=ip;unsigned dots=0,n=0,digits=0;
 for(;;p++) {
  if(*p>='0'&&*p<='9') {if(++digits>3)return 0;n=n*10+(unsigned)(*p-'0');if(n>255)return 0;}
  else if(*p=='.'||!*p) {if(!digits)return 0;if(!*p)break;if(++dots>3)return 0;n=digits=0;}
  else return 0;
 }
 if(dots!=3||strlen(mac)!=17)return 0;
 for(unsigned i=0;i<17;i++)if(i%3==2?mac[i]!=':':!isxdigit((unsigned char)mac[i]))return 0;
 return 1;
}
static int wifi_steps(struct ws_state *s) {
 char cmd[260],ssid[67],pass[131],msg[170];
 say(s,"Opening ESP8266 command-mode setup. No stored settings or MAC change.");
 if(!command(s,"AT",s->cfg.command_seconds,"AT response",0))return 0;
 if(!command(s,"ATE0",s->cfg.command_seconds,"echo off",0))return 0;
 if(!command(s,"AT+GMR",s->cfg.command_seconds,"firmware version",0))return 0;
 if(!command(s,"AT+CWMODE_CUR=1",s->cfg.command_seconds,"station mode",0))return 0;
 if(!command(s,"AT+CWDHCP_CUR=1,1",s->cfg.command_seconds,"station DHCP enabled",0))return 0;
 escaped(s->cfg.ssid,ssid);escaped(s->cfg.password,pass);
 snprintf(cmd,sizeof(cmd),"AT+CWJAP_CUR=\"%s\",\"%s\"",ssid,pass);
 say(s,"Joining configured Wi-Fi. SSID and password are not displayed or logged.");
 if(!command(s,cmd,s->cfg.join_seconds,"Wi-Fi association",1)) {memset(cmd,0,sizeof(cmd));memset(pass,0,sizeof(pass));return 0;}
 memset(cmd,0,sizeof(cmd));memset(pass,0,sizeof(pass));s->secret=0;
 /* Association OK need not mean DHCP is complete. Observe the original join
  * for a bounded lease interval; CIFSR is a fresh query, never a join replay. */
 {
  uint32_t start=s->io.now(s->io.ctx),last=start;
  for(;;) {
   if(!command(s,"AT+CIFSR",s->cfg.command_seconds,"station address and MAC",0))return 0;
   if(s->ip[0]&&s->mac[0]) {
    if(!address_valid(s->ip,s->mac)) {s->failed=WS_PROTOCOL;return 0;}
    if(strcmp(s->ip,"0.0.0.0"))break;
   }
   if(expired(s,start,s->cfg.join_seconds)) {s->failed=WS_TIMEOUT;return 0;}
   say(s,"Wi-Fi joined; DHCP lease not ready yet.");
   {uint32_t pause=s->io.now(s->io.ctx);while(!expired(s,pause,1)) {if(!pump(s))return 0;breadcrumb(s,"DHCP lease",start,&last,s->cfg.join_seconds);}}
  }
 }
 snprintf(msg,sizeof(msg),"Station IP: %s; MAC: %s. Address assigned by DHCP.",s->ip,s->mac);say(s,msg);
 say(s,"Your router's MAC reservation determines the canonical address.");
 return !s->failed;
}
static int steps(struct ws_state *s) {
 char cmd[260];
 if(!wifi_steps(s))return 0;
 if(!command(s,"AT+CIPMODE=0",s->cfg.command_seconds,"normal TCP command mode",0))return 0;
 if(!command(s,"AT+CIPMUX=0",s->cfg.command_seconds,"single TCP connection",0))return 0;
 if(!command(s,"AT+CIPDINFO=0",s->cfg.command_seconds,"bounded TCP receive framing",0))return 0;
 snprintf(cmd,sizeof(cmd),"AT+CIPSTART=\"TCP\",\"%s\",%u",s->cfg.host,s->cfg.port);
 /* CONNECT/OK can be immediately followed by the welcome. Receive both
  * before any display/card output, for the same FIFO reason as CIPSEND. */
 if(!command_wait(s,cmd,s->cfg.bbs_seconds,"BBS TCP connection and welcome",0,WAIT_CONNECT))return 0;
 say(s,"BBS welcome:");say(s,s->reply);s->reply_n=0;s->reply[0]=0;
 if(!send_bbs(s,"help\r\n",0)||!send_bbs(s,"time\r\n",0)||!send_bbs(s,"uptime\r\n",0)||!send_bbs(s,"quit\r\n",1))return 0;
 say(s,"Success: Wi-Fi, DHCP, TCP and BBS request/reply checks passed.");return !s->failed;
}
static int ping_command(struct ws_state *s,const char *cmd,const char *what) {
 if(command(s,cmd,s->cfg.command_seconds,what,0))return 1;
 /* A complete ERROR proves command mode has returned. It cannot distinguish
  * unsupported PING from an unreachable peer. Never clear timeout/cancel/I/O. */
 if(s->failed==WS_MODEM&&s->error&&!s->uncertain) {
  s->failed=0;s->ping_warning=1;
  say(s,"Warning: connectivity check refused or unavailable; Wi-Fi remains connected.");
  return -1;
 }
 return 0;
}
static int startup_steps(struct ws_state *s) {
 char cmd[120],msg[160];const char *target=s->cfg.ping_host;int rc;
 say(s,"Connecting to configured Wi-Fi. Escape cancels.");
 if(!wifi_steps(s))return 0;
 say(s,"Connected: Wi-Fi association and DHCP verified.");
 if(!strcmp(target,"none")) {say(s,"Ping disabled in configuration; network latency not checked.");return !s->failed;}
 if(!strcmp(target,"gateway")) {
  rc=ping_command(s,"AT+CIPSTA_CUR?","DHCP gateway query");if(rc<=0)return rc<0;
  if(!address_valid(s->gateway,s->mac)||!strcmp(s->gateway,"0.0.0.0")) {
   s->ping_warning=1;say(s,"Warning: module did not report a valid gateway; ping not checked.");return !s->failed;
  }
  target=s->gateway;
 }
 say(s,"Checking network reachability with two pings.");
 snprintf(cmd,sizeof(cmd),"AT+PING=\"%s\"",target);
 for(unsigned i=0;i<2;i++) {
  s->ping_seen=0;rc=ping_command(s,cmd,"network ping");if(rc==0)return 0;
  if(rc>0) {
   if(s->ping_seen) {snprintf(msg,sizeof(msg),"Ping %u: %u ms (ESP8266-reported round trip).",i+1,s->ping_ms);say(s,msg);}
   else {s->ping_warning=1;say(s,"Warning: ping returned OK without a latency; reply not verified.");}
  } else break;
 }
 say(s,s->ping_warning?"Wi-Fi connected; ping verification incomplete. See progress log.":"Wi-Fi ready; both network pings passed.");
 return !s->failed;
}
static int run(struct ws_state *s,const struct ws_config *c,const struct ws_io *io,int startup) {
 int result;memset(s,0,sizeof(*s));s->cfg=*c;s->io=*io;s->last_clock=io->now(io->ctx);s->last_rx=s->last_clock;
 say(s,"Wi-Fi setup: Escape cancels at any stage. Progress is logged without credentials.");
 if(startup)startup_steps(s);else steps(s);result=s->failed;
 if(result) {
  char msg[100];snprintf(msg,sizeof(msg),"Stopped: %s (result %d).",result==WS_CANCEL?"Escape pressed":result==WS_TIMEOUT?"deadline expired":result==WS_PROTOCOL?"unexpected or oversized response":result==WS_LOG?"log write failed":result==WS_CLOCK?"MOS clock stopped":"ESP8266 refused or UART closed",result);say(s,msg);
  if(s->uncertain||s->data_pending)say(s,"Module operation may still be pending. No cleanup command injected; reset the module manually before another attempt if needed.");
  else if(s->connected)say(s,"TCP may remain open. No hidden reconnect or replay; close it manually before another attempt.");
 }
 say(s,"Closing this program's UART. Wi-Fi is left associated if setup succeeded.");
 memset(s->cfg.password,0,sizeof(s->cfg.password));memset(s->cfg.ssid,0,sizeof(s->cfg.ssid));
 return result?result:s->failed;
}

int ws_run(struct ws_state *s,const struct ws_config *c,const struct ws_io *io) {return run(s,c,io,0);}
int ws_start(struct ws_state *s,const struct ws_config *c,const struct ws_io *io) {return run(s,c,io,1);}
