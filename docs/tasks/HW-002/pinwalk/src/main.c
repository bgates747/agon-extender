/* Keyboard-free entry to the retained legacy generic header pinwalk.
 * BC-001: cold boot, a short MOS-clock delay, one walk, then released inputs.
 * The GPIO assembly is unchanged from legacy commit 4485e44. This diagnostic
 * still exercises PD4-PD7/PB5 as well as PC0-PC7; the former I2C exercise is
 * omitted because only the direct GPIO waveform is needed here.
 */
#include <agon/mos.h>
#include <stdio.h>
#include <time.h>
#include "pinwalk_wire.h"
#include "build_identity.h"

int main(void)
{
    putch(22);
    putch(3);
    pinwalk_release();
    puts(BUILD_ID);
    puts("EXPERIMENTAL - keyboard-free header pinwalk");
    puts("One walk after approximately five seconds; then return to MOS.");
    const clock_t start = clock();
    while ((clock_t)(clock() - start) < 5UL * CLOCKS_PER_SEC) {
        /* MOS clock depends on onboard VDP VSync. If absent, stay released. */
    }
    puts("PINWALK BEGIN schema=1");
    pinwalk_gpio_run();
    pinwalk_release();
    puts("PINWALK END schema=1 - GPIO released");
    return 0;
}
