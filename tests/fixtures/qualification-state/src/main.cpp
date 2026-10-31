// Cross-component qualification support, not resident firmware.
// Only ordinary MOS VDU/query/file APIs. Never touches boot files or UART/GPIO.
// The Pi owns route selection, a single-buffered entry contract and restoration.
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern "C" uint24_t bench_clock(const volatile uint8_t *);
extern "C" uint24_t bench_count(const uint8_t *, uint24_t);
static volatile uint8_t *sv;
struct Mode { unsigned number, width, height, colours; };
static bool query(Mode &mode, int expected = -1) {
    sv[sysvar_vdp_pflags] &= uint8_t(~vdp_pflag_mode);
    const uint8_t command[] = {23, 0, 0x86};
    if (bench_count(command, sizeof command)) return false;
    auto start = bench_clock(sv);
    uint32_t fuse = 10000000;
    while (uint24_t(bench_clock(sv) - start) < 600 && --fuse) {
        if (!(sv[sysvar_vdp_pflags] & vdp_pflag_mode)) continue;
        mode = {sv[sysvar_scrMode], unsigned(getsysvar_scrwidth()),
                unsigned(getsysvar_scrheight()), sv[sysvar_scrColours]};
        if (mode.width && mode.height && mode.colours &&
            (expected < 0 || mode.number == unsigned(expected))) return true;
        sv[sysvar_vdp_pflags] &= uint8_t(~vdp_pflag_mode);
    }
    return false;
}
static bool settle() {
    // >=1 second at nominal 120/140 ticks/s, independently bounded if stopped.
    auto start = bench_clock(sv);
    uint32_t fuse = 10000000;
    while (uint24_t(bench_clock(sv) - start) < 160 && --fuse) {}
    return fuse != 0;
}
static bool token_valid(const char *s) {
    if (strlen(s) != 16) return false;
    for (unsigned i = 0; i < 16; ++i)
        if (!((s[i] >= '0' && s[i] <= '9') || (s[i] >= 'A' && s[i] <= 'F')))
            return false;
    return true;
}
int main(int argc, char **argv) {
    if (argc != 3 && argc != 7) return 19;
    bool restore = !strcmp(argv[1], "restore");
    const char *token = argv[argc - 1];
    if (!token_valid(token) || (restore ? argc != 7 :
        argc != 3 || strcmp(argv[1], "capture"))) return 19;
    sv = mos_sysvars();
    Mode actual{};
    bool okay = query(actual) && actual.number < 128;
    if (restore && okay) {
        unsigned number = unsigned(atoi(argv[2]));
        if (number >= 128) return 19;
        if (actual.number != number) {
            const uint8_t select[] = {22, uint8_t(number)};
            okay = !bench_count(select, sizeof select) && query(actual, number) && settle();
        }
        okay = okay && actual.width == unsigned(atoi(argv[3])) &&
               actual.height == unsigned(atoi(argv[4])) &&
               actual.colours == unsigned(atoi(argv[5]));
    }
    // Do not silently replace an unsupported double-buffered entry mode.
    if (!okay) { puts("Qualification state query/restore failed."); return 19; }
    char path[100];
    snprintf(path, sizeof path, "/agents/extender/results/qstate-%s.txt", token);
    FIL file{};
    if (ffs_fopen(&file, path, FA_WRITE | FA_CREATE_NEW)) return 19;
    char record[180];
    int count = snprintf(record, sizeof record,
        "schema=1\ntoken=%s\nmode=%u\nwidth=%u\nheight=%u\ncolours=%u\n",
        token, actual.number, actual.width, actual.height, actual.colours);
    bool saved = count > 0 && count < int(sizeof record) &&
                 ffs_fwrite(&file, record, count) == unsigned(count);
    saved = ffs_fsync(&file) == 0 && saved;
    saved = ffs_fclose(&file) == 0 && saved;
    puts(saved ? "Qualification state complete." : "Qualification state save failed.");
    return saved ? 0 : 19;
}
