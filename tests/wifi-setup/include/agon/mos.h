/* Host-only MOS API double. Never used by native build. */
#ifndef TEST_MOS_H
#define TEST_MOS_H
#include <stdint.h>
#include <stddef.h>
#define FA_READ 1
#define FA_WRITE 2
#define FA_OPEN_ALWAYS 16
#define FR_OK 0
struct test_file;typedef struct test_file FIL;
typedef struct {unsigned baudRate,dataBits,stopBits,parity,flowcontrol,eir;} UART;
uint32_t getsysvar_time(void);
uint8_t getsysvar_keyascii(void),getsysvar_vkeydown(void);
int mos_ugetc_nb(void);
uint8_t mos_uopen(UART *),mos_uclose(void);
uint8_t mos_fopen(const char *,uint8_t),mos_fclose(uint8_t),mos_feof(uint8_t);
size_t mos_fread(uint8_t,char *,size_t),mos_fwrite(uint8_t,char *,size_t);
FIL *mos_getfil(uint8_t);
uint8_t mos_flseek(uint8_t,uint32_t),ffs_fsize(FIL *,uint32_t *),ffs_fsync(FIL *);
#endif
