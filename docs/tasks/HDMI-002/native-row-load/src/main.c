/* P4 native-row comparison. Runs on the EMOS-selected route, uses the original
 * packed mode-preview files, and writes only packet-local measurement data.
 * MOS time is a mainboard VBlank counter (+2/edge); record Pi elapsed separately.
 */
#include <agon/mos.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>

#define SEND(a) mos_puts((const char *)(a), sizeof(a), 0)
static char block[4096];

static int active_mode(void) {
    static const char query[] = {23, 0, 0x86};
    mos_clearvdpflags(vdp_pflag_mode);
    SEND(query);
    if (mos_waitforvdpflags(vdp_pflag_mode)) return -1;
    return mos_sysvars()[sysvar_scrMode];
}

static bool select_mode(unsigned n) {
    int current = active_mode();
    if (current < 0) return false;
    if ((unsigned)current == n) return true;
    const char change[] = {22, (char)n};
    SEND(change);
    if (active_mode() != (int)n) return false;
    uint32_t start = getsysvar_time(), fuse = 10000000;
    while (getsysvar_time() - start < 160 && --fuse) {}
    return fuse != 0;
}

static bool preview(unsigned n) {
    char name[13], head[2];
    snprintf(name, sizeof name, "m%03u.vdu", n);
    uint8_t file = mos_fopen(name, FA_READ);
    if (!file) return false;
    bool ok = mos_fread(file, head, 2) == 2 &&
              head[0] == 22 && (uint8_t)head[1] == n && select_mode(n);
    if (ok) {
        unsigned count;
        while ((count = mos_fread(file, block, sizeof block)) != 0)
            mos_puts(block, count, 0);
        if (active_mode() != (int)n) ok = false;
        if (ok) while (getch() != 27) {}
    }
    mos_fclose(file);
    return ok;
}

/* Two separately marked sprites exercise both stock implementations. Palette
 * 1 is selected across a 32-row boundary by the signal list in buffer 61000.
 * These ephemeral fixture IDs are used only at the clean commissioned prompt.
 */
static void install_scene(void) {
    static const uint8_t scene[] = {
        23,27,0,237, 23,27,2,8,0,8,0,255,255,255,255,
        23,27,4,0, 23,27,5, 23,27,6,237, 23,27,20,
        23,27,4,1, 23,27,5, 23,27,6,237, 23,27,19,
        23,27,7,2, 23,27,4,0, 23,27,11, 23,27,4,1, 23,27,11,
        23,0,0xc4,0,1,0, 23,0,0xa0,0x48,0xee,2,
        23,0,0xa0,0x48,0xee,0,12,0, 31,0,0,0, 32,0,1,0, 1,0,0,0,
        23,0,0xc4,3,0x48,0xee
    };
    SEND(scene);
}

static void retire_scene(void) {
    static const uint8_t reset[] = {
        23,27,7,0, 23,27,4,0, 23,27,5, 23,27,4,1, 23,27,5,
        23,0,0xc4,4, 23,0,0xc4,1,1,0, 23,0,0xa0,0x48,0xee,2,
        23,0,0xa0,0xed,0xfa,2, 23,1,1
    };
    SEND(reset);
}

static void render(unsigned n, uint32_t step) {
    uint8_t y = (uint8_t)(step % 192);
    uint8_t draw[] = {
        23,7,1,2,1, 23,27,0,237, 23,27,3,16,0,0,0,
        23,27,4,0,23,27,13,56,0,y,0, 23,27,4,1,23,27,13,96,0,y,0,
        23,27,15, 23,0,0xc4,2,1,0,0,(uint8_t)step,0,255
    };
    SEND(draw);
    if (n >= 128) {
        static const uint8_t swap[] = {23,0,0xc3};
        SEND(swap);
    }
}

static bool load(unsigned n, int method) {
    if ((n != 0 && n != 3 && n != 8 && n != 20 && n != 136) || !select_mode(n))
        return false;
    bool draw = method == 'R' || method == 'B';
    bool read = method == 'D' || method == 'B';
    uint8_t file = read ? mos_fopen("m020.vdu", FA_READ) : 0;
    if (read && !file) return false;
    printf("Mode %u test %c, Escape ends window\r\n", n, method);
    if (draw) install_scene();
    uint32_t count = 0, bytes = 0, start = getsysvar_time();
    bool ok = true;
    do {
        if (draw) render(n, count);
        if (method == 'C') putch(12);
        if (read) {
            unsigned got = mos_fread(file, block, sizeof block);
            if (got == 0) {
                if (mos_flseek(file, 0) != 0) { ok = false; break; }
                got = mos_fread(file, block, sizeof block);
                if (!got) { ok = false; break; }
            }
            bytes += got;
        }
        ++count;
    } while (getsysvar_keyascii() != 27);
    uint32_t end = getsysvar_time();
    if (file) mos_fclose(file);
    if (draw) retire_scene();
    if (active_mode() != (int)n) ok = false;
    FILE *csv = fopen("rowload.csv", "a");
    if (!csv) return false;
    int wrote = fprintf(csv, "%u,%c,%lu,%lu,%lu,%lu,%u\n",
                        n, method, (unsigned long)start, (unsigned long)end,
                        (unsigned long)count, (unsigned long)bytes, ok ? 1U : 0U);
    int closed = fclose(csv);
    return ok && wrote > 0 && closed == 0;
}

static bool transitions(void) {
    // Exercise same-carrier bank/geometry changes and a direct 8 -> 20
    // under draw pressure. select_mode verifies each edge and settles once.
    static const unsigned modes[] = {8, 136, 8, 20, 0, 3, 0};
    for (unsigned round = 0; round < 10; ++round) {
        for (unsigned i = 0; i < sizeof modes / sizeof *modes; ++i) {
            unsigned n = modes[i];
            if (!select_mode(n)) return false;
            putch(12);
            if (n >= 128) {
                static const uint8_t swap[] = {23,0,0xc3};
                SEND(swap);
            }
        }
    }
    return true;
}

int main(void) {
    const char cursor[] = {4,23,1,1,23,1,3};
    if (active_mode() != 0) { puts("Start at a mode 0 prompt."); return 1; }
    bool ok = true;
    for (;;) {
        SEND(cursor);
        puts("P pattern, C clear, R draw, D SD read, B both, T transitions, Q exit.");
        int how = getch();
        if (how >= 'a' && how <= 'z') how -= 'a' - 'A';
        if (how == 27 || how == 'Q') break;
        if (how == 'T') {
            puts("Testing ten mode round trips.");
            ok = transitions();
            if (!select_mode(0) || !ok) { ok = false; break; }
            continue;
        }
        if (how != 'P' && how != 'R' && how != 'C' && how != 'D' && how != 'B') continue;
        putch(how);
        puts(" Mode number then Enter:");
        unsigned mode = 0, digits = 0;
        int c;
        while ((c = getch()) != 13 && c != 27) {
            if (c >= '0' && c <= '9' && digits < 3) {
                mode = 10 * mode + (c - '0'); ++digits; putch(c);
            }
        }
        if (c == 27 || !digits) continue;
        putch(13);
        ok = how == 'P' ? preview(mode) : load(mode, how);
        if (!select_mode(0) || !ok) { ok = false; break; }
    }
    SEND(cursor);
    puts(ok ? "Row test closed." : "Row test failed.");
    return ok ? 0 : 1;
}
