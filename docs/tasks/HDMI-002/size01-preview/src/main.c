/* Packet-local reader for the four existing packed mode-preview-r02 streams.
 * The retained viewer uses absolute SD paths and unconditional switches.
 * Use job-relative files and settle after a confirmed switch. Both arms use
 * this same binary and the same original labelled, palette-quantized streams.
 */
#include <agon/mos.h>
#include <stdio.h>
#include <stdlib.h>

struct pattern { unsigned mode, bytes; const char *file; };
static const struct pattern patterns[] = {
    {0, 86354, "m000.vdu"}, {8, 27248, "m008.vdu"},
    {20, 65523, "m020.vdu"}, {3, 50495, "m003.vdu"}
};

static int active_mode(void) {
    static const char query[] = {23, 0, 0x86};
    mos_clearvdpflags(vdp_pflag_mode);
    mos_puts(query, sizeof query, 0);
    if (mos_waitforvdpflags(vdp_pflag_mode)) return -1;
    return mos_sysvars()[sysvar_scrMode];
}

static int select_mode(unsigned mode) {
    int active = active_mode();
    if (active < 0) return 0;
    if ((unsigned)active == mode) return 1;
    char select[] = {22, (char)mode};
    mos_puts(select, sizeof select, 0);
    if (active_mode() != (int)mode) return 0;
    // MOS advances two ticks per vblank. 160 ticks exceed one second even
    // at 75 Hz. A stalled clock fails before issuing pattern drawing bytes.
    uint32_t start = getsysvar_time();
    uint32_t fuse = 10000000;
    while (getsysvar_time() - start < 160 && --fuse) {}
    return fuse != 0;
}

static int show(const struct pattern *p) {
    uint8_t fh = mos_fopen(p->file, FA_READ);
    if (!fh) return 0;
    char *data = malloc(p->bytes);
    unsigned loaded = 0;
    while (data && loaded < p->bytes) {
        unsigned count = p->bytes - loaded;
        if (count > 4096) count = 4096;
        if (mos_fread(fh, data + loaded, count) != count) break;
        loaded += count;
    }
    char extra;
    int complete = loaded == p->bytes && mos_fread(fh, &extra, 1) == 0;
    mos_fclose(fh);
    int ok = complete && data[0] == 22 && data[1] == (char)p->mode &&
             select_mode(p->mode);
    if (ok) {
        // Only the initial VDU 22 is handled above. Send every remaining byte
        // of the reviewed labelled pattern through MOS, in bounded chunks.
        for (unsigned pos = 2; pos < p->bytes;) {
            unsigned count = p->bytes - pos;
            if (count > 4096) count = 4096;
            mos_puts(data + pos, count, 0);
            pos += count;
        }
        while (getch() != 27) {}
    }
    free(data);
    return ok;
}

static int menu(void) {
    if (!select_mode(0)) return 0;
    static const char menu_vdu[] = {4, 23, 1, 1, 23, 1, 3, 12};
    mos_puts(menu_vdu, sizeof menu_vdu, 0);
    puts("Mode 0, 8, 20 or 3. Enter selects. Escape returns or exits.");
    unsigned mode = 0, digits = 0;
    for (;;) {
        char key = getch();
        if (key == 27) return 1;
        if (key >= '0' && key <= '9' && digits < 3) {
            mode = 10 * mode + (key - '0');
            ++digits;
            putch(key);
        } else if (key == 13 && digits) {
            for (unsigned i = 0; i < sizeof patterns / sizeof *patterns; ++i) {
                if (patterns[i].mode == mode) return show(&patterns[i]) ? 2 : 0;
            }
            puts(" Select 0, 8, 20 or 3.");
            mode = digits = 0;
        }
    }
}

int main(void) {
    char excom[] = "EMOS EXCOM --keep-display", legacy[] = "EMOS LEGACY --keep-display";
    if (mos_oscli(excom, NULL, 0)) return 1;
    int entry = active_mode(), result = 0;
    if (entry >= 0 && entry < 128) {
        do { result = menu(); } while (result == 2);
        if (!select_mode((unsigned)entry)) result = 0;
        static const char cursor[] = {4, 23, 1, 1, 23, 1, 3};
        mos_puts(cursor, sizeof cursor, 0);
    }
    if (mos_oscli(legacy, NULL, 0)) return 1;
    puts(result ? "HDMI preview closed." : "HDMI preview failed.");
    return result ? 0 : 1;
}
