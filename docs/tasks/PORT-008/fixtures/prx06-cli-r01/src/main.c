/* Historical PRX-06 CLI-only launcher; not a supported EMOS application API.
 * Author approved direct-GPIO historical comparison. No SD or startup writes.
 * Host installs historical receiver only after admitted CLI delivers RUN.
 */
#include "prx06_wire.h"
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "p4_canary.h"
static uint8_t record[P4_CANARY_SIZE];
static const char *run_sweep(void)
{
    unsigned sent = 0;
    p4_canary_build(record);
    if (!p4_canary_validate(record, sizeof(record))) return "FAIL: local canary.";
    puts("Sweep armed. Waiting for the host fixture...");
    for (uint8_t profile = 0; profile < PRX06_PROFILES; ++profile) {
        for (uint8_t repeat = 0; repeat < PRX06_REPEATS; ++repeat) {
            uint8_t result = prx06_send(record, profile);
            if (result != PRX06_OK) {
                prx06_enter_idle();
                printf("PRX06 AGON FAIL profile=%u repeat=%u result=%u sent=%u\r\n",
                       profile, repeat, result, sent);
                return "FAIL: admission or completion timeout.";
            }
            ++sent;
            printf("Profile %u repeat %u sent.\r\n", profile, repeat + 1);
        }
    }
    if (prx06_send(record, PRX06_PROFILES - 1) != PRX06_OK) {
        prx06_enter_idle();
        return "FAIL: analyzer record did not complete.";
    }
    prx06_enter_idle();
    printf("PRX06 AGON COMPLETE records=%u state=released\r\n", sent + 1);
    return "Sweep sent; use the host verdict as authority.";
}
int main(void) {
 /* CLI launch only: never open, write or restore autoexec or any SD file.
  * Historical GPIO ownership exception applies only to this isolated fixture.
  * P4 starts in normal firmware; host flashes receiver after RUN delivery.
  */
 prx06_enter_idle();
 const char *status=run_sweep();puts(status);
 return strncmp(status,"Sweep sent;",11)?1:0;
}
