/* SPDX-License-Identifier: GPL-3.0-only
 * Separate startup application, reusing our project's counted MOS/file adapter.
 * Radiotux's source files are not included, copied or modified. His utilities
 * are monolithic/blocking; our Escape-capable adapter is original project code.
 * Rename only OUR diagnostic entry point while sharing its static helpers.
 */
#define main ws_diagnostic_main
#include "../../wifi-setup/src/main.c"
#undef main

static int quiet_message(void *ctx,const char *text) {
 /* All redacted details go to the log. Screen output is limited to English
  * stage/outcome/wait messages, never raw AT transcripts or credentials. */
 const char *visible[]={"Connecting", "Connected:", "Station IP:", "Checking network",
   "Ping ", "Warning:", "Wi-Fi ready", "Wi-Fi connected;", "Ping disabled",
   "Still waiting", "MOS clock", "Stopped:", "Module operation", "TCP may",
   "Cannot ", "MOS refused", "Escape pressed"};
 for(unsigned i=0;i<sizeof(visible)/sizeof(*visible);i++)
  if(!strncmp(text,visible[i],strlen(visible[i]))) {puts(text);break;}
 return append_log(ctx,text);
}
static int choose_connection(int automatic) {
 if(escape(NULL))return 0;
 if(automatic) {puts("Automatic connection enabled. Escape cancels.");return 1;}
 puts("1) Connect as configured\n2) Skip connection\nChoose 1 or 2 (Escape skips):");
 /* Use the MOS-maintained keyboard state: no blocking read, vector takeover,
  * deadline or implicit choice. Unrelated inherited RUN keys are ignored. */
 for(;;) {
  if(getsysvar_vkeydown()) {
   unsigned c=getsysvar_keyascii();
   if(c==27||c=='2')return 0;
   if(c=='1')return 1;
  }
  idle(NULL);
 }
}
#ifndef WS_START_ENTRY
#define WS_START_ENTRY main
#endif
int WS_START_ENTRY(int argc,char **argv) {
 uint8_t cfg=0;char error[160]={0};UART uart;int result;uint32_t end;
 struct ws_io io;struct ws_reader reader;
 const char *cfgpath=argc>1?argv[1]:"wifi-start.cfg";
 const char *logpath=argc>2?argv[2]:"progress.log";
 size_t cn=strlen(cfgpath),ln=strlen(logpath);
 memset(&platform,0,sizeof(platform));memset(&state,0,sizeof(state));memset(&config,0,sizeof(config));
 puts("Wi-Fi startup");
 if(argc>3||(argc>1&&(!strcmp(argv[1],"--help")||!strcmp(argv[1],"-h")))) {
  puts("Usage: wifi-start [private.cfg [progress.log]]\nDefaults: wifi-start.cfg and progress.log in current directory.\nChoose Connect or Skip; auto_connect=1 skips the menu. Escape cancels.");
  return argc>3?ws_mos_exit(WS_CONFIG):0;
 }
 if(cn<4||ln<4||strcmp(cfgpath+cn-4,".cfg")||strcmp(logpath+ln-4,".log")) {
  puts("Use a private .cfg input and a distinct .log output.");return ws_mos_exit(WS_CONFIG);
 }
 if(escape(NULL))return 0;
 cfg=mos_fopen(cfgpath,FA_READ);
 if(cfg) {
  reader.ctx=&cfg;reader.next=config_next;
  result=ws_read_start_config(&reader,&config,error,sizeof(error),escape,NULL);
  mos_fclose(cfg);
 } else {result=WS_CONFIG;snprintf(error,sizeof(error),"Cannot open private configuration file.");}
 /* A missing/invalid cfg must not prevent a user from choosing Skip. Never
  * trust auto_connect from a configuration that did not completely validate. */
 if(result==WS_CANCEL||!choose_connection(!result&&config.auto_connect)) {
  memset(&config,0,sizeof(config));puts("Connection skipped. UART was not opened.");return 0;
 }
 if(result) {puts(error);memset(&config,0,sizeof(config));return ws_mos_exit(result);}
 platform.hz=config.tick_hz;platform.start=now(NULL);
 platform.log=mos_fopen(logpath,FA_WRITE|FA_OPEN_ALWAYS);
 if(!platform.log) {puts("Cannot append progress log. UART not opened.");memset(&config,0,sizeof(config));return ws_mos_exit(WS_LOG);}
 platform.file=mos_getfil(platform.log);
 if(!platform.file||ffs_fsize(platform.file,&end)!=FR_OK||mos_flseek(platform.log,end)!=FR_OK) {
  puts("Cannot locate end of progress log. UART not opened.");result=WS_LOG;goto close_log;
 }
 if(!quiet_message(&platform,WIFI_BUILD_ID "; starting connection-only session.")) {result=WS_LOG;goto close_log;}
 snprintf(error,sizeof(error),"Nominal MOS clock: %u counts/second; UART1 %u baud,8N1,no RTS/CTS.",config.tick_hz,config.baud);
 if(!quiet_message(&platform,error)) {result=WS_LOG;goto close_log;}
 if(escape(NULL)) {quiet_message(&platform,"Escape pressed before UART open.");result=WS_CANCEL;goto close_log;}
 uart.baudRate=config.baud;uart.dataBits=8;uart.stopBits=1;uart.parity=0;uart.flowcontrol=0;uart.eir=0;
 if(mos_uopen(&uart)!=0) {quiet_message(&platform,"MOS refused UART1 open; no module command sent.");result=WS_MODEM;}
 else {
  io.ctx=&platform;io.now=now;io.escape=escape;io.receive=receive;io.transmit=transmit;io.idle=idle;io.message=quiet_message;
  result=ws_start(&state,&config,&io);mos_uclose();
 }
 if(ffs_fsync(platform.file)!=FR_OK||platform.log_failed) {puts("Log incomplete: card write/sync failed.");if(!result)result=WS_LOG;}
close_log:
 mos_fclose(platform.log);memset(&state,0,sizeof(state));memset(&config,0,sizeof(config));
 printf("%s See %s for details.\n",result?"Connection stopped.":"Finished.",logpath);
 return ws_mos_exit(result);
}
