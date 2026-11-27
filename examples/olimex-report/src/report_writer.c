#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "report_writer.h"

#define TOKEN_LEN 16
#define HEADER_LEN 23

/* AgonDev ffs_fwrite exposes the count only. Keep the MOS status as well. */
extern uint8_t olx_ffs_write(FIL *file, const void *data, uint24_t size, uint24_t *written);

int olx_report_token(const char *token)
{
    return token && strlen(token) == TOKEN_LEN && strspn(token, "0123456789abcdef") == TOKEN_LEN;
}

static int valid_name(const char *name)
{
    const char alphabet[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-";
    size_t stem = strspn(name, alphabet);
    if (!stem || stem > 8)
        return 0;
    if (!name[stem])
        return 1;
    const char *suffix = name + stem + 1;
    return name[stem] == '.' && *suffix && strlen(suffix) <= 3
        && strspn(suffix, alphabet) == strlen(suffix);
}

int olx_report_save(const char *token, const char *path, const void *payload, size_t size)
{
    const char *slash = strrchr(path, '/');
    if (!olx_report_token(token) || path[0] != '/' || !slash || !valid_name(slash + 1)
            || size > 0xffffffUL - HEADER_LEN || (size && !payload))
        return 1;

    char header[HEADER_LEN];
    memcpy(header, "OLXR1 ", 6);
    memcpy(header + 6, token, TOKEN_LEN);
    header[HEADER_LEN - 1] = '\n';

    FIL file;
    uint24_t written = 0;
    uint24_t actual = 0;
    uint8_t status = ffs_fopen(&file, path, FA_CREATE_NEW | FA_WRITE);
    uint8_t close_status = 0;
    const char *stage = "open";
    if (!status) {
        status = olx_ffs_write(&file, header, sizeof(header), &written);
        actual = written;
        if (!status && written == sizeof(header) && size) {
            written = 0;
            status = olx_ffs_write(&file, payload, size, &written);
            actual += written;
        }
        close_status = ffs_fclose(&file);
        if (status)
            stage = "write";
        else if (actual != size + HEADER_LEN)
            stage = "short";
        else
            stage = close_status ? "close" : "saved";
    }

    printf("OLXR1 %s %s %lu %lu %s %u %u\n", token, slash + 1,
           (unsigned long)size + HEADER_LEN, (unsigned long)actual, stage,
           (unsigned)status, (unsigned)close_status);
    return status || close_status || actual != size + HEADER_LEN;
}
