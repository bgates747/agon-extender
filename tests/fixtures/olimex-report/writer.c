#include "agon/mos.h"
#include "report_writer.h"

#include <assert.h>
#include <string.h>

static unsigned scenario, opens, writes, closes;
static char captured[64];
static unsigned used;

uint8_t ffs_fopen(FIL *file, const char *name, uint8_t mode)
{
    assert(strcmp(name, "/test/extender/example/direct/RESULT.BIN") == 0);
    assert(mode == (FA_WRITE | FA_CREATE_NEW));
    ++opens;
    if (scenario == 1)
        return 8; /* FR_EXIST */
    file->open = 1;
    return 0;
}

uint8_t olx_ffs_write(FIL *file, const void *data, uint24_t length, uint24_t *written)
{
    assert(file->open);
    ++writes;
    *written = (writes == 2 && (scenario == 2 || scenario == 4)) ? 2 : length;
    memcpy(captured + used, data, *written);
    used += *written;
    return writes == 2 && scenario == 4 ? 1 : 0;
}

uint8_t ffs_fclose(FIL *file)
{
    assert(file->open);
    file->open = 0;
    ++closes;
    return scenario >= 3 ? 1 : 0;
}

int main(void)
{
    const char token[] = "0123456789abcdef";
    const char *path = "/test/extender/example/direct/RESULT.BIN";
    assert(!olx_report_token("ABCDEF0123456789"));
    assert(!olx_report_token(NULL));
    assert(olx_report_save("bad", path, "abc", 3) != 0);
    assert(olx_report_save(token, "/RESULT.TXT.LONG", "abc", 3) != 0);
    assert(!opens);
    for (scenario = 0; scenario < 5; ++scenario) {
        opens = writes = closes = used = 0;
        int result = olx_report_save(token, path, "abc", 3);
        assert((result == 0) == (scenario == 0));
        assert(opens == 1);
        assert(writes == (scenario == 1 ? 0 : 2));
        assert(closes == (scenario == 1 ? 0 : 1));
        if (scenario == 0)
            assert(used == 26 && !memcmp(captured, "OLXR1 0123456789abcdef\nabc", used));
    }
    return 0;
}
