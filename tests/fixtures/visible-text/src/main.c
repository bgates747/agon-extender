/* SD-loaded qualification sample. EMOS owns the P4 transport; this program
 * only formats text and submits one bounded request. The optional preview
 * writes the same text through ordinary MOS VDU to the onboard display.
 * Video mode belongs exclusively in autoexec, never in this program.
 */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "build_identity.h"

extern uint24_t emos_gateway_call(uint8_t *request);
/* Static buffers are in application RAM, separate from the MOS-owned stack.
 * Existing EMOS v1 gateway: 66 bytes, ABI 1.0, operation 2 (service).
 * This tiny binding is a fixture, not a transport or a second mode authority.
 */
static uint8_t request[66];
static char text[1024];

static void write24(uint8_t *p, uint24_t n) {
    p[0] = n; p[1] = n >> 8; p[2] = n >> 16;
}

static void prepare(uint24_t address, uint24_t length) {
    memset(request, 0, sizeof(request));
    request[0] = sizeof(request); request[2] = 1;
    request[4] = 3; request[5] = 10; request[6] = 2;
    write24(request + 10, address); write24(request + 13, length);
    memcpy(request + 25, "edu", 3);
    memcpy(request + 41, "text-probe", 10);
}

static int check_rejections(void) {
    const uint24_t cases[][2] = {
        {0, 1}, {0x03FFFF, 1}, {0x0AFFFF, 2}, {0x0B0000, 1},
        {0xFFFFFF, 2}, {(uint24_t)text, 0}, {(uint24_t)text, 1025}
    };
    for (unsigned i=0; i<sizeof(cases)/sizeof(cases[0]); ++i) {
        prepare(cases[i][0], cases[i][1]);
        if (emos_gateway_call(request) != FR_INVALID_PARAMETER) return 0;
    }
    const uint8_t invalid[][3] = {{22,3,0}, {23,0,0x80}, {31,2,0}};
    for (unsigned i=0; i<3; ++i) {
        memcpy(text, invalid[i], 3);
        prepare((uint24_t)text, i==2 ? 2 : 3);
        if (emos_gateway_call(request) != FR_INVALID_PARAMETER) return 0;
    }
    text[0]='X'; prepare((uint24_t)text, 1); request[19]=1;
    if (emos_gateway_call(request) != FR_INVALID_PARAMETER) return 0;
    return 1;
}

/* Stock MOS time advances by two units per 60 Hz VBlank. Thirty units
 * gives approximately 250 ms, with one-tick resolution. Bound polling even
 * if the onboard clock stops. No keyboard or direct timer/GPIO access. */
static int pause_between_lines(void) {
    const volatile uint8_t *clock=mos_sysvars();
    uint8_t last=clock[sysvar_time];
    unsigned elapsed=0;
    uint24_t budget=0xFFFFFF;
    while (elapsed<30 && --budget) {
        uint8_t now=clock[sysvar_time];
        elapsed+=(uint8_t)(now-last);
        last=now;
    }
    return elapsed>=30;
}

static uint24_t submit(int length, int preview) {
    if (preview) {
        for (int i=0; i<length; ++i) putch((uint8_t)text[i]);
        return 0;
    }
    prepare((uint24_t)text, length);
    uint24_t status=emos_gateway_call(request);
    if (status) printf("VDP TEXT SAMPLE FAIL: EMOS status %u\r\n", status);
    return status;
}

int main(int argc, char **argv) {
    puts(SAMPLE_ID);
    printf("VDP TEXT SAMPLE %s (%s)\r\n", SAMPLE_BUILD_ID, SAMPLE_STATUS);
    if (argc > 1 && strcmp(argv[1], "check") == 0) {
        if (!check_rejections()) { puts("TEXT GATEWAY CHECK FAIL"); return 1; }
        puts("TEXT GATEWAY CHECK PASS: invalid requests rejected");
        return 0;
    }
    int preview=argc>1 && strcmp(argv[1], "preview")==0;
    if (argc>1 && !preview) { puts("Usage: VTEXT [preview|check]"); return 19; }
    if (!preview) puts("VDP TEXT SAMPLE: sending banner, then count 1..10 with 250 ms pauses");
    int length=snprintf(text, sizeof(text), "\x0c\x1f\x02\x02" "EMOS TO EDP: UART TEXT\r\n");
    if (length<0 || (unsigned)length>=sizeof(text)) return 1;
    uint24_t status=submit(length, preview);
    if (status) return (int)status;
    for (unsigned number=1; number<=10; ++number) {
        if (!pause_between_lines()) { puts("VDP TEXT SAMPLE FAIL: clock stalled"); return 1; }
        length=snprintf(text, sizeof(text), "%u\r\n", number);
        if (length<0 || (unsigned)length>=sizeof(text)) return 1;
        status=submit(length, preview);
        if (status) return (int)status;
    }
    if (preview) puts("TEXT SAMPLE PREVIEW: onboard VDU only");
    else puts("VDP TEXT SAMPLE PASS: confirm browser banner and count 1..10");
    return 0;
}
