/* AUDIO-001 storage-only fixture. No mode change, parallel IO or firmware writes.
 * Generates its own 1 MiB test file, then measures synchronous MOS reads.
 * Reports are written after timing; first/last-byte checks are not a full CRC.
 */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#define DATA "/test/audio001/data.bin"
#define REPORT "/test/audio001/results.csv"
#define BYTES 1048576UL
static FIL input, output;
static uint8_t buffer[16384];
static const uint24_t sizes[] = {512,2940,4096,8192,16384,8192};
static char line[240];
static int log_line(const char *text) {
 uint24_t n=strlen(text);
 puts(text);
 return ffs_fwrite(&output,text,n)==n;
}
int main(void) {
 uint24_t i; uint32_t total; int failed=0;
 puts("AUDIO-001 SD benchmark: preparing 1 MiB. No parallel transfer.");
 if (ffs_fopen(&input,DATA,FA_WRITE|FA_CREATE_ALWAYS)) return 1;
 for(i=0;i<sizeof(buffer);i++) buffer[i]=(uint8_t)i;
 for(total=0;total<BYTES;total+=sizeof(buffer)) {
  if(ffs_fwrite(&input,(char*)buffer,sizeof(buffer))!=sizeof(buffer)) { ffs_fclose(&input); return 2; }
 }
 if(ffs_fclose(&input)) return 3;
 if(ffs_fopen(&output,REPORT,FA_WRITE|FA_CREATE_ALWAYS)) return 4;
 snprintf(line,sizeof(line),"audio001-sd-r01,clock_ticks_per_second,%lu\r\n",(unsigned long)CLOCKS_PER_SEC);
 if(!log_line(line)) failed=1;
 if(!log_line("chunk_bytes,bytes,calls,open_ticks,read_ticks,endpoints_ok,close_ok\r\n")) failed=1;
 for(i=0;i<sizeof(sizes)/sizeof(sizes[0]);i++) {
  uint32_t bytes=0,calls=0; int valid=1; clock_t begin=clock(),opened,elapsed; int closed;
  if(ffs_fopen(&input,DATA,FA_READ)) { failed=1; break; }
  opened=clock()-begin; begin=clock();
  while(bytes<BYTES) {
   uint24_t want=BYTES-bytes<sizes[i]?(uint24_t)(BYTES-bytes):sizes[i];
   uint24_t got=ffs_fread(&input,(char*)buffer,want);
   if(got!=want || !got) { valid=0; break; }
   if(buffer[0]!=(uint8_t)bytes || buffer[got-1]!=(uint8_t)(bytes+got-1)) valid=0;
   bytes+=got;calls++;
  }
  elapsed=clock()-begin; closed=ffs_fclose(&input)==0;
  snprintf(line,sizeof(line),"%u,%lu,%lu,%lu,%lu,%d,%d\r\n",(unsigned)sizes[i],(unsigned long)bytes,(unsigned long)calls,(unsigned long)opened,(unsigned long)elapsed,valid,closed);
  if(!log_line(line))failed=1;
  if(!valid||!closed||bytes!=BYTES||elapsed==0)failed=1;
 }
 if(!log_line(failed?"FAIL\r\n":"PASS\r\n"))failed=1;
 if(ffs_fclose(&output))failed=1;
 puts(failed?"AUDIO-001 finished: FAIL":"AUDIO-001 finished: PASS; results saved.");
 return failed;
}
