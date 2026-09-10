/* Standalone MOS 3 FatFS contract probe. No EMOS-specific API or hardware I/O.
 * Each run gets a new directory. Unexpected CREATE_NEW success is closed
 * without writing, so the deliberately existing sentinel is not overwritten.
 * Video mode is selected by autoexec, never here. */
#include <agon/mos.h>
#include <stdio.h>
#include <string.h>
#include "build_identity.h"

static FIL file;
static char directory[64], path[96], buffer[64], report[1024];
static const char sentinel[]="An existing file must survive.\r\n";
volatile unsigned fs_exit_status=1;
__attribute__((noinline)) void fs_done(void) { __asm__ volatile("nop"); }

static unsigned verify(void) {
    unsigned status=ffs_fopen(&file,path,FA_READ);
    if (status) return status;
    memset(buffer,0,sizeof(buffer));
    unsigned size=ffs_fread(&file,buffer,sizeof(buffer));
    unsigned close_status=ffs_fclose(&file);
    if (close_status) return close_status;
    return size==sizeof(sentinel)-1 && !memcmp(buffer,sentinel,size) ? 0 : 1;
}

int main(void) {
    unsigned setup=FR_EXIST, create=255, sync=255, close_status=255, original=255, reopened=255;
    for (unsigned i=1;i<1000;++i) {
        snprintf(directory,sizeof(directory),"/extender/fscheck/R%05u",i);
        setup=mos_mkdir(directory);
        if (!setup || setup!=FR_EXIST) break;
    }
    if (!setup) {
        snprintf(path,sizeof(path),"%s/CREATE.DAT",directory);
        setup=ffs_fopen(&file,path,FA_WRITE|FA_CREATE_NEW);
        if (!setup) {
            unsigned size=ffs_fwrite(&file,sentinel,sizeof(sentinel)-1);
            setup=ffs_fclose(&file);
            if (size!=sizeof(sentinel)-1) setup=FR_DISK_ERR;
        }
        if (!setup) {
            create=ffs_fopen(&file,path,FA_WRITE|FA_CREATE_NEW);
            if (!create) ffs_fclose(&file); /* expose wrong result; do not write */
            original=verify();
        }
        snprintf(path,sizeof(path),"%s/SYNC.DAT",directory);
        unsigned opened=ffs_fopen(&file,path,FA_WRITE|FA_CREATE_NEW);
        if (!opened) {
            unsigned size=ffs_fwrite(&file,sentinel,sizeof(sentinel)-1);
            sync=ffs_fsync(&file);
            close_status=ffs_fclose(&file);
            if (size!=sizeof(sentinel)-1 && !setup) setup=FR_DISK_ERR;
            reopened=verify();
        } else if (!setup) setup=opened;
    }
    fs_exit_status=setup || create!=FR_EXIST || sync || close_status || original || reopened;
    snprintf(report,sizeof(report),
        "Filesystem probe %s (%s)\r\n"
        "setup=%u (expected 0)\r\n"
        "create_existing=%u (expected 8: FR_EXIST)\r\n"
        "original_contents=%u (expected 0)\r\n"
        "sync_open_written=%u (expected 0: FR_OK)\r\n"
        "close=%u (expected 0)\r\n"
        "reopened_contents=%u (expected 0)\r\n"
        "Filesystem probe %s\r\n",
        FS_BUILD_ID,FS_STATUS,setup,create,original,sync,close_status,reopened,
        fs_exit_status ? "FAIL" : "PASS");
    puts(report);
    if (!setup) {
        snprintf(path,sizeof(path),"%s/RESULT.TXT",directory);
        unsigned saved=mos_save(path,report,strlen(report));
        printf("Result file: %s; save status %u\r\n",path,saved);
        if (saved) fs_exit_status=1;
    }
    fs_done();
    return fs_exit_status;
}
