/* Exercise the actual shared core with an AT peer, not a duplicate engine. */
#define main diagnostic_core_checks
#include "../wifi-setup/test_core.c"
#undef main
static unsigned pings;
static int startup_tx(void *v,unsigned char c) {
 struct peer *p=v;
 if(c=='\n'&&(strstr(p->tx,"AT+CIPSTA_CUR?")==p->tx||strstr(p->tx,"AT+PING=")==p->tx)) {
  int gateway=strstr(p->tx,"AT+CIPSTA_CUR?")==p->tx;
  p->tn=0;memset(p->tx,0,sizeof(p->tx));p->phase=gateway?12:13;
  if(gateway)enqueue(p,p->scenario==35?"ERROR\r\n":p->scenario==36?"+CIPSTA_CUR:gateway:\"0.0.0.0\"\r\nOK\r\n":"+CIPSTA_CUR:gateway:\"192.0.2.1\"\r\nOK\r\n",0);
  else {
   pings++;
   if(p->scenario==32)return 1;
   enqueue(p,p->scenario==30?"ERROR\r\n":p->scenario==31?"OK\r\n":p->scenario==33?"+999999999999999999\r\nOK\r\n":"+12\r\nOK\r\n",0);
  }
  return 1;
 }
 return tx(v,c);
}
static void start_case(int scenario,int cancel,unsigned hz,uint32_t clock) {
 static struct peer p;static struct ws_state s;struct ws_config c;struct ws_io io;
 memset(&p,0,sizeof(p));p.scenario=scenario;p.escape_phase=cancel;p.clock=clock;pings=0;
 ws_defaults(&c);strcpy(c.ssid,"private-home");strcpy(c.password,password);c.tick_hz=hz;c.join_seconds=5;
 if(scenario==34)strcpy(c.ping_host,"none");
 if(scenario==37)strcpy(c.ping_host,"example.invalid");
 io=(struct ws_io){&p,now,esc,rx,startup_tx,idle,msg};
 int result=ws_start(&s,&c,&io);
 int expected=cancel?WS_CANCEL:scenario==32?WS_TIMEOUT:scenario==33?WS_PROTOCOL:WS_OK;
 if(result!=expected)fprintf(stderr,"startup scenario%d cancel%d got%d expected%d\n%s",scenario,cancel,result,expected,p.log);
 assert(result==expected);assert(!strstr(p.log,password)&&!strstr(p.log,"private-home"));
 assert(!strstr(p.log,"BBS")&&!strstr(p.log,"CIPSTART")&&!s.cfg.ssid[0]&&!s.cfg.password[0]);
 if(!cancel&&scenario==0)assert(pings==2&&strstr(p.log,"12 ms")&&!s.ping_warning);
 if(!cancel&&(scenario==30||scenario==31||scenario==35||scenario==36))assert(s.ping_warning);
 if(!cancel&&scenario==34)assert(!pings);
 if(!cancel&&scenario==32)assert(pings==1&&s.uncertain);
}
static void start_config_tests(void) {
 const char *data[]={"ssid=x\npassword=p\n", "ssid=x\npassword=p\nauto_connect=1\nping_host=example.invalid\n", "ssid=x\npassword=p\nauto_connect=2\n", "ssid=x\npassword=p\nauto_connect=0\nauto_connect=1\n", "ssid=x\npassword=p\nping_host=a\"bad\n", "ssid=x\npassword=p\nbbs_host=old.invalid\n"};
 for(unsigned i=0;i<6;i++) {
  FILE *f=tmpfile();fputs(data[i],f);rewind(f);struct ws_reader r={f,file_next};struct ws_config c;char e[160];
  int rc=ws_read_start_config(&r,&c,e,sizeof(e),NULL,NULL);fclose(f);assert(rc==((i>=2&&i<=4)?WS_CONFIG:WS_OK));
  if(i==0)assert(!c.auto_connect&&!strcmp(c.ping_host,"gateway"));
  if(i==1)assert(c.auto_connect);
 }
}
int main(void) {
 start_config_tests();start_case(0,0,120,0);start_case(0,0,100,0xfffffff0UL);
 for(int i=30;i<=37;i++)start_case(i,0,120,0);
 for(int phase=1;phase<=7;phase++)start_case(0,phase,120,0);
 start_case(0,12,120,0);start_case(0,13,120,0);
 puts("PASS: startup config, DHCP/gateway, real ping, refusal/malformed/timeout, explicit/disabled host, Escape and redaction.");return 0;
}
