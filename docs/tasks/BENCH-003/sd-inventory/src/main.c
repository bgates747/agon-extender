/* Read-only directory walker; writes one new report, never removes files.
 * BENCH-003 support: replace thousands of paginated UART directory requests.
 * MOS3 public FatFS APIs; standalone foreground application, no video modes.
 */
#include <agon/mos.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
static DIR dirs[24];
static FILINFO infos[24];
static FIL output;
static char path[512],line[640],lower[512];
static unsigned long count;
static int emit(const char *s) {
 unsigned n=strlen(s);return ffs_fwrite(&output,s,n)==n && !ffs_ferror(&output);
}
static int walk(unsigned depth) {
 if(depth>=24)return 90;
 uint8_t e=ffs_dopen(&dirs[depth],path);if(e)return e;
 unsigned base=strlen(path);
 for(;;){
  FILINFO *f=&infos[depth];e=ffs_dread(&dirs[depth],f);
  if(e||!f->fname[0])break;
  if(!strcmp(f->fname,".")||!strcmp(f->fname,".."))continue;
  unsigned n=strlen(f->fname);
  if(base+n+2>=sizeof(path)){e=91;break;}
  if(base>1)strcat(path,"/");strcat(path,f->fname);
  for(unsigned i=0;i<=strlen(path);i++)lower[i]=tolower((unsigned char)path[i]);
  count++;
  if(strstr(lower,"nurpl") || strstr(lower,"/arcade/rally") || depth==0){
   sprintf(line,"%u\t%lu\t%s\n",(unsigned)f->fattrib,(unsigned long)f->fsize,path);
   if(!emit(line)){e=92;break;}
  }
  if(f->fattrib&16){e=walk(depth+1);if(e)break;}
  path[base]=0;
 }
 path[base]=0;
 uint8_t close=ffs_dclose(&dirs[depth]);return e?e:close;
}
int main(void){
 puts("BENCH-003 SD inventory: read-only scan, report /test/nscan.tsv");
 uint8_t e=ffs_fopen(&output,"/test/nscan.tsv",FA_WRITE|FA_CREATE_NEW);
 if(e)return e;
 strcpy(path,"/");int result=walk(0);
 sprintf(line,"END\t%lu\t%d\n",count,result);if(!emit(line))result=92;
 e=ffs_fclose(&output);if(!result)result=e;
 printf("Inventory complete: %lu entries, status %d\n",count,result);return result;
}
