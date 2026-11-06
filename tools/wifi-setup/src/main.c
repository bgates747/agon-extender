/* SPDX-License-Identifier: GPL-3.0-only
 * Console8 stock-MOS adapter. MOS owns UART open/write/close and ordinary VDU.
 * RX and THRE polling match AgonDev/Radiotux's foreground UART1 technique.
 * No use on an Extender installation which owns UART1. No interrupt/vector,
 * port-selector or flow-control modification outside normal MOS UART admission.
 */
#include "setup.h"
#include <agon/mos.h>
#include <string.h>
#ifndef WIFI_BUILD_ID
#define WIFI_BUILD_ID "wifi-setup-development-unidentified"
#endif
extern int wifi_try_put(int);
static struct ws_state state;
static struct ws_config config;
struct platform {uint8_t log;FIL *file;uint32_t start;unsigned hz;int log_failed;};
static struct platform platform;
static uint32_t now(void *unused) {
 uint32_t a,b;(void)unused;
 /* Library reads the four-byte clock in two instructions. A second sample
  * avoids the rollover tear without masking interrupts or borrowing a timer. */
 a=getsysvar_time();b=getsysvar_time();return (uint32_t)(b-a)<4?b:getsysvar_time();
}
static int escape(void *unused) {(void)unused;return getsysvar_keyascii()==27&&getsysvar_vkeydown();}
static int receive(void *unused) {(void)unused;return mos_ugetc_nb();}
static int transmit(void *unused,unsigned char c) {(void)unused;return wifi_try_put(c);}
static void idle(void *unused) {(void)unused;for(volatile unsigned i=0;i<60;i++);}
static int append_log(void *ctx,const char *text) {
 struct platform *p=ctx;uint32_t elapsed=(uint32_t)(now(NULL)-p->start);unsigned long sec=(unsigned long)(elapsed/p->hz);
 if(p->log_failed)return 0;
 char prefix[35];size_t n;
 snprintf(prefix,sizeof(prefix),"[%lu s] ",sec);n=strlen(prefix);
 /* AgonDev fputc discards MOS write errors and fflush has no disk sync.
  * Use counted MOS writes and the documented MOS3 FatFS sync instead. */
 if(mos_fwrite(p->log,prefix,n)!=n||mos_fwrite(p->log,(char *)text,strlen(text))!=strlen(text)||mos_fwrite(p->log,"\r\n",2)!=2||ffs_fsync(p->file)!=FR_OK) {
  p->log_failed=1;puts("Log write failed. Stopping; check free card space.");return 0;
 }
 return 1;
}
static int message(void *ctx,const char *text) {
 struct platform *p=ctx;
 printf("[%lu s] %s\n",(unsigned long)((uint32_t)(now(NULL)-p->start)/p->hz),text);
 return append_log(ctx,text);
}
static int config_next(void *ctx) {
 unsigned char c;uint8_t fh=*(uint8_t *)ctx;
 if(mos_fread(fh,(char *)&c,1)==1)return c;
 return mos_feof(fh)?-1:-2;
}
int main(int argc,char **argv) {
 uint8_t cfg;char error[160];UART uart;int result;const char *cfgpath,*logpath;struct ws_io io;struct ws_reader reader;size_t cn,ln;uint32_t end;
 memset(&platform,0,sizeof(platform));
 puts(WIFI_BUILD_ID " (experimental)");
 if(argc>1&&(!strcmp(argv[1],"--help")||!strcmp(argv[1],"-h"))) {
  puts("Usage: wifi-setup <private.cfg> [progress.log]\nDefault log: wifi-setup.log in current directory. Escape cancels.\nNo credentials on command line. Read README before using UART1.");return 0;
 }
 if(argc<2||argc>3) {puts("Usage: wifi-setup <private.cfg> [progress.log]");return ws_mos_exit(WS_CONFIG);}
 cfgpath=argv[1];logpath=argc==3?argv[2]:"wifi-setup.log";
 cn=strlen(cfgpath);ln=strlen(logpath);
 /* Distinct suffixes also prevent ordinary case-insensitive FAT aliasing. */
 if(cn<4||ln<4||strcmp(cfgpath+cn-4,".cfg")||strcmp(logpath+ln-4,".log")) {
  puts("Use a private .cfg input and a distinct .log output.");return ws_mos_exit(WS_CONFIG);
 }
 if(escape(NULL))return ws_mos_exit(WS_CANCEL);
 platform.hz=120;platform.start=now(NULL);
 platform.log=mos_fopen(logpath,FA_WRITE|FA_OPEN_ALWAYS);if(!platform.log) {puts("Cannot append progress log. UART not opened.");return ws_mos_exit(WS_LOG);}
 platform.file=mos_getfil(platform.log);
 if(!platform.file||ffs_fsize(platform.file,&end)!=FR_OK||mos_flseek(platform.log,end)!=FR_OK) {
  puts("Cannot locate the end of the progress log.");mos_fclose(platform.log);return ws_mos_exit(WS_LOG);
 }
 if(!message(&platform,WIFI_BUILD_ID "; starting new session.")) {mos_fclose(platform.log);return ws_mos_exit(WS_LOG);}
 cfg=mos_fopen(cfgpath,FA_READ);
 if(!cfg) {message(&platform,"Cannot open private configuration file. UART not opened.");mos_fclose(platform.log);return ws_mos_exit(WS_CONFIG);}
 reader.ctx=&cfg;reader.next=config_next;
 result=ws_read_config(&reader,&config,error,sizeof(error),escape,NULL);mos_fclose(cfg);
 if(result) {message(&platform,error);memset(&config,0,sizeof(config));mos_fclose(platform.log);return ws_mos_exit(result);}
 if(escape(NULL)) {message(&platform,"Escape pressed before UART open.");memset(&config,0,sizeof(config));mos_fclose(platform.log);return ws_mos_exit(WS_CANCEL);}
 platform.hz=config.tick_hz;
 snprintf(error,sizeof(error),"Clock conversion: %u ticks/second (nominal); UART1 %u baud, 8N1, no RTS/CTS.",config.tick_hz,config.baud);message(&platform,error);
 uart.baudRate=config.baud;uart.dataBits=8;uart.stopBits=1;uart.parity=0;uart.flowcontrol=0;uart.eir=0;
 if(platform.log_failed)result=WS_LOG;
 else if(mos_uopen(&uart)!=0) {message(&platform,"MOS refused UART1 open; no module command sent.");result=WS_MODEM;}
 else {
  io.ctx=&platform;io.now=now;io.escape=escape;io.receive=receive;io.transmit=transmit;io.idle=idle;io.message=message;
  result=ws_run(&state,&config,&io);mos_uclose();
 }
 memset(&state,0,sizeof(state));memset(&config,0,sizeof(config));
 if(ffs_fsync(platform.file)!=FR_OK||platform.log_failed) {puts("Log incomplete: card write/sync failed.");if(!result)result=WS_LOG;}
 mos_fclose(platform.log);
 printf("Returning to MOS. Application result %d; MOS exit %d.\n",result,ws_mos_exit(result));return ws_mos_exit(result);
}
