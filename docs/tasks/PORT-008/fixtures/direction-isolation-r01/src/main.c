/* PORT-008 direction isolation; adapted from the existing parcheck MOSlet.
 * Only EMOS API51h owns the transport.
 * Paired P4 data-only endpoint retains each forward block and returns it.
 * No GPIO/register/vector access, mode switches, timing hooks or serial logs.
 */
#include <agon/mos.h>
#include <stdio.h>
#include <string.h>
extern uint24_t emos_gateway_call(uint8_t *request);
static uint8_t request[66],input[2],storage[4114];
static uint8_t pattern(unsigned i){return (uint8_t)((i*73u)^((i>>3)*29u)^(i>>8)^0x69);}
static void put24(uint8_t *p,uint24_t n){p[0]=n;p[1]=n>>8;p[2]=n>>16;}
static unsigned call(unsigned n,unsigned reverse){
 memset(request,0,sizeof request);request[0]=66;request[2]=1;
 request[4]=3;request[5]=8;request[6]=2;
 memcpy(request+25,"ext",3);memcpy(request+41,"uartdiag",8);
 input[0]=6;input[1]=reverse;
 put24(request+10,(uint24_t)input);request[13]=2;
 put24(request+16,(uint24_t)(storage+1));put24(request+19,n+16);
 return emos_gateway_call(request);
}
int main(int argc,char **argv){
 unsigned reverse,status,guards,mismatches=0,first=1024,actual=0,expected=0;FILE*f;
 const unsigned n=1024;uint8_t*data=storage+17;
 if(argc!=3 || (strcmp(argv[1],"forward") && strcmp(argv[1],"reverse")) ||
    strncmp(argv[2],"/agents/extender/results/",25))return 19;
 reverse=!strcmp(argv[1],"reverse");
 f=fopen(argv[2],"r");if(f){fclose(f);return 19;}
 f=fopen(argv[2],"w");if(!f)return 15;
 memset(storage,0xCC,sizeof storage);storage[0]=0xA5;storage[n+17]=0x5A;
 if(!reverse)for(unsigned i=0;i<n;++i)data[i]=pattern(i);
 status=call(n,reverse);guards=storage[0]==0xA5 && storage[n+17]==0x5A;
 if(!status && reverse)for(unsigned i=0;i<n;++i)if(data[i]!=pattern(i)){
   if(!mismatches){first=i;actual=data[i];expected=pattern(i);}++mismatches;
 }
 fputs("length,direction,status,guards,mismatches,first_offset,actual,expected\n",f);
 fprintf(f,"%u,%u,%u,%u,%u,%u,%u,%u\n",n,reverse,status,guards,mismatches,first,actual,expected);
 fputs(reverse?"# P4 source generated independently; compare all Agon bytes\n":
               "# Forward integrity owned by P4 retained comparison, not this status\n",f);
 /* Diagnostic only: retain full received bytes after transport returns.
    No logging or SD operations run inside the native byte loop. */
 if(reverse){fputs("# received=",f);for(unsigned i=0;i<n;++i)fprintf(f,"%02x",data[i]);fputc(10,f);}
 {unsigned error=ferror(f);if(fclose(f)||error)return 15;}
 printf("Direction isolation %s: status=%u guards=%u mismatches=%u\r\n",argv[1],status,guards,mismatches);
 return status || !guards || mismatches?15:0;
}
