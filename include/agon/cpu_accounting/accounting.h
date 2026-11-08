/* Experimental MGCPU001/schema1, one short app-RAM window. Never a CPU% API.
 * Link this recorder WITH the unchanged rxdiag observer.c/.s timer provider.
 * Only one provider owns PRT1. No old MGIRQ001 data is reinterpreted.
 * OPEN8/C1 requires EMOS_CPU_ACCOUNTING; ordinary OPEN4 remains unchanged.
 */
#ifndef AGON_CPU_ACCOUNTING_H
#define AGON_CPU_ACCOUNTING_H
#include <stdint.h>
#define AGON_CPU_BYTES 96
#define AGON_CPU_MAX_COUNTS 54000u /* nominal0.75s /256, NOT calibrated */
enum { ACP_FLAGS=12, ACP_POISON=13, ACP_ACTIVE=14, ACP_STOPPED=15,
 ACP_EPOCH=16, ACP_FIRST=20, ACP_LAST=22, ACP_CLASS=24, ACP_RESUME=25,
 ACP_VECTOR=26, ACP_REASON_DEPTH=27, ACP_TOTALS=32, ACP_VECTORS=42,
 ACP_COUNTS=48, ACP_MARKERS=54, ACP_REASON=56, ACP_LAST_CONTROL=57,
 ACP_START_CONTROL=58, ACP_END_CONTROL=59, ACP_END=60,
 ACP_CALLBACK_DEPTH=62, ACP_CALLBACK_MAX=63 };
enum { ACP_PARTIAL_BOUNDARIES=1, ACP_UNKNOWN_GAP=2, ACP_INVALID=4,
 ACP_CLOCK_INVALID=8, ACP_CONTEXT_INVALID=16, ACP_OVERFLOW=32 };
enum { ACP_FOREGROUND=0, ACP_GATEWAY=1, ACP_IRQ=2, ACP_HALT=3,
 ACP_OBSERVER=4 };
enum { ACP_U0_ENTER=1, ACP_U1_ENTER=2, ACP_VBLANK_ENTER=3,
 ACP_GATE_ENTER=4, ACP_HALT_TAKEN=6, ACP_AW_WORK=7,
 ACP_CALLBACK_ENTER=0x20, ACP_CALLBACK_EXIT=0x21,
 ACP_WAIT_ENTER=0x30, ACP_WAIT_EXIT=0x31,
 ACP_START=0x60, ACP_STOP=0x70, ACP_U0_EXIT=0x81,
 ACP_U1_EXIT=0x82, ACP_VBLANK_EXIT=0x83, ACP_GATE_EXIT=0x84,
 ACP_HALT_RETURN=0x86 };
extern volatile uint8_t agon_cpu_record[AGON_CPU_BYTES];
/* ADDRESS only. ABI C1 jump entries+0 marker(A event, existing DI), +4 poison.
 * Marker preserves ALL primary/index/shadow/ADL regs and leaves IFF unchanged.
 * No C/MOS/logging/UART/GPIO, no reentry under EI. Independent poison is NMI-safe.
 * Foreground wrapper preserves regs and incoming IFF; wait owner must call the
 * DI marker before adjacent EI/HALT, never insert between those instructions.
 */
void agon_cpu_entry(void);
void agon_cpu_foreground(void); /* native A-event ABI, NOT C argument ABI */
int agon_cpu_init(void); /* pure storage; before association, one time */
int agon_cpu_admit(void); /* dormant provider claim; needs separate timer scope */
int agon_cpu_start(uint32_t epoch,uint8_t uart0_quiescent,uint8_t uart1_quiescent);
void agon_cpu_stop(void); /* never detach; refused CLOSE retains all storage */
/* Snapshot only after STOP + timer retirement + positive owner CLOSE. IRQ hooks
 * can still poison an associated stopped record. Copy no live record under DI.
 * Returns0 for incomplete/reset/poison/clock/context/overflow; partial remains.
 */
int agon_cpu_snapshot(uint8_t out[AGON_CPU_BYTES],uint8_t positive_close);
#endif
