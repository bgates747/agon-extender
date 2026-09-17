/* Task-owned entry. Original sorting/model/range routines above remain C. */
#include "szip_p4.h"
#include <setjmp.h>
#include "esp_heap_caps.h"
#undef malloc
#undef calloc
#undef free
static jmp_buf failure;
static volatile unsigned admitted;
static const uint8_t *input;
static uint8_t *output;
static size_t input_n,input_at,output_n,output_at,allocated;
static void *allocations[4096];
void p4_szip_reset_sort(void);
_Noreturn void sz_fail(int code){longjmp(failure,code?code:1);}
void *sz_alloc(size_t n){
 if(!n)n=1;
 if(n>12*1024*1024-allocated)sz_fail(3);
 for(unsigned i=0;i<4096;i++)if(!allocations[i]){
  void *p=heap_caps_malloc(n,MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
  if(!p)sz_fail(3);allocations[i]=p;allocated+=n;return p;
 }
 sz_fail(3);
}
void *sz_calloc(size_t n,size_t width){if(width && n>SIZE_MAX/width)sz_fail(3);size_t bytes=n*width;void*p=sz_alloc(bytes);memset(p,0,bytes);return p;}
void sz_free(void*p){if(!p)return;for(unsigned i=0;i<4096;i++)if(allocations[i]==p){heap_caps_free(p);allocations[i]=NULL;return;}sz_fail(1);}
int sz_get(void){if(input_at==input_n)sz_fail(1);return input[input_at++];}
int sz_put(int c){if(output_at==output_n)sz_fail(2);output[output_at++]=(uint8_t)c;return (uint8_t)c;}
int sz_unget(int c,FILE*f){(void)f;if(!input_at || input[input_at-1]!=(uint8_t)c)sz_fail(1);--input_at;return c;}
size_t sz_read(void*p,size_t s,size_t n,FILE*f){(void)f;if(s && n>SIZE_MAX/s)sz_fail(1);size_t bytes=s*n;if(bytes>input_n-input_at)sz_fail(1);memcpy(p,input+input_at,bytes);input_at+=bytes;return n;}
size_t sz_write(const void*p,size_t s,size_t n,FILE*f){(void)f;if(s && n>SIZE_MAX/s)sz_fail(2);size_t bytes=s*n;if(bytes>output_n-output_at)sz_fail(2);memcpy(output+output_at,p,bytes);output_at+=bytes;return n;}
int p4_szip(int decode,const uint8_t*src,size_t length,uint8_t*dst,size_t cap,size_t*written){
 if(!src||!dst||!written||!length||length>2097152)return 1;
 *written=0;if(__sync_lock_test_and_set(&admitted,1))return 4;
 input=src;input_n=length;input_at=0;output=dst;output_n=cap;output_at=0;allocated=0;
 memset(allocations,0,sizeof allocations);p4_szip_reset_sort();
 int error=setjmp(failure);
 if(!error){
  order=3;recordsize=1;verbosity=0;
  if(decode){
   if(length<14||memcmp(src,"CmpS",4)||memcmp(src+8,"SZ\012\004\001\014",6))sz_fail(1);
   uint32_t expected=(uint32_t)src[4]|(uint32_t)src[5]<<8|(uint32_t)src[6]<<16|(uint32_t)src[7]<<24;
   if(!expected||expected>1048590||expected>cap)sz_fail(2);
   input_at=14;output_n=expected;
   while(input_at<input_n){
    uint4 n;unsigned dir=readblockdir(&n);if(!dir||!n||n>expected-output_at)sz_fail(1);
    unsigned char*buf=sz_alloc(n+1);int type=sz_get();
    if(type==0)readstorblock(dir+1,n,buf);
    else if(type==1)readszipblock(dir+1,n,buf);
    else sz_fail(1);
    sz_free(buf);
   }
   if(output_at!=expected)sz_fail(1);
  }else{
   /* -b41o3: inputs within our cap fit in one block, order3, recordsize1. */
   writeglobalheader(length);unsigned char*buf=sz_alloc(length+4);memcpy(buf,src,length);
   unsigned dir=writeblockdir(length);
   if(length<=5)writestorblock(dir,length,buf);else writeszipblock(dir,length,buf);
  }
  *written=output_at;
 }
 for(unsigned i=0;i<4096;i++)if(allocations[i]){heap_caps_free(allocations[i]);allocations[i]=NULL;}
 p4_szip_reset_sort();__sync_lock_release(&admitted);return error;
}
