#include <agon/mos.h>
#include <stdbool.h>
#include <stdio.h>

enum {
    SCREEN_CHARACTER_FLAG = 0x02,
    REHEARSAL_VDU_SELECTOR = 0xb8,
    REHEARSAL_VDU_REPLY = 0x56,
    INVALID_PARAMETER = 19,
};

int main(void) {
    char accepted[] = "EMOS BENCH019 probe";
    char rejected[] = "EMOS BENCH019 other";
    const unsigned accepted_status = mos_oscli(accepted, NULL, 0);
    const unsigned rejected_status = mos_oscli(rejected, NULL, 0);
    const bool emos_pass = accepted_status == 0 && rejected_status == INVALID_PARAMETER;

    mos_clearvdpflags(SCREEN_CHARACTER_FLAG);
    putch(23);
    putch(0);
    putch(REHEARSAL_VDU_SELECTOR);
    const unsigned vdp_status = mos_waitforvdpflags(SCREEN_CHARACTER_FLAG);
    const unsigned vdp_value = vdp_status == 0 ? getsysvar_scrchar() : 0;
    const bool vdp_pass = vdp_status == 0 && vdp_value == REHEARSAL_VDU_REPLY;

    FILE *const report = fopen("/test/bench019/result.txt", "wb");
    if (!report) {
        puts("BENCH019 FAIL opening result.txt");
        return 1;
    }
    const int written = fprintf(report, "EMOS %s accepted=%u rejected=%u\n"
                                "VDPlet %s status=%u value=%u\n",
                                emos_pass ? "PASS" : "FAIL", accepted_status, rejected_status,
                                vdp_pass ? "PASS" : "FAIL", vdp_status, vdp_value);
    const int closed = fclose(report);
    const bool success = written >= 0 && closed == 0 && emos_pass && vdp_pass;
    puts(success ? "BENCH019 PASS" : "BENCH019 FAIL; see result.txt");
    return success ? 0 : 1;
}
