#include <agon/mos.h>
#include <agon/vdp.h>
#include <agon/timer.h>
#include <stdio.h>
extern "C" uint24_t gt_prt_init(void),gt_prt_read(void);
extern "C" void gt_prt_begin(void),gt_prt_close(void);
int main(){
 if(!gt_prt_init()){printf("PRT1 unavailable\n");return 1;}
 unsigned values[124];waitvblank();
 for(unsigned i=0;i<120;i++){gt_prt_begin();waitvblank();values[i]=gt_prt_read();}
 gt_prt_begin();values[120]=gt_prt_read();
 gt_prt_begin();delay(10);values[121]=gt_prt_read();
 gt_prt_begin();delay(30);values[122]=gt_prt_read();
 gt_prt_begin();delay(100);values[123]=gt_prt_read();gt_prt_close();
 FILE*f=fopen("prt.csv","w");if(!f)return 2;
 fprintf(f,"sample,prt_counts\n");for(unsigned i=0;i<124;i++)fprintf(f,"%u,%u\n",i,values[i]);
 int status=fclose(f);printf("PRT check %s\n",status?"failed":"complete");return status;
}
