/* Experimental app-RAM UART service observer, schema2. No normal UART API.
 * Link observer.c + observer.s into ONE static application; never install an
 * IRQ/vector or read UART/GPIO in caller code. Pair only with identified
 * EMOS_UART1_RX_DIAGNOSTIC OPEN7. The admitted marker must remain resident
 * through source release, later drain and positive owner CLOSE. Refused CLOSE
 * retains this association/storage; freeze/stop never authorize unload.
 */
#ifndef AGON_RXDIAG_OBSERVER_H
#define AGON_RXDIAG_OBSERVER_H
#include <stdint.h>
#define AGON_RXDIAG_BYTES 128
#define AGON_RXDIAG_VERSION 2
/* Byte offsets, explicitly LE; no compiler-dependent C struct overlay. */
enum {
 ARD_MAGIC=0, ARD_VERSION=8, ARD_SIZE=10, ARD_FLAGS=12,
 ARD_EPOCH=16, ARD_SEQUENCE=20, ARD_HZ=24, ARD_RELOAD=28, ARD_CONTROL=30,
 ARD_PREVIOUS=32, ARD_CURRENT=56, ARD_SPAN_BYTES=24,
 ARD_LSR=80, ARD_REMAINING=81, ARD_PC_DR=82, ARD_RX_HOLD=83,
 ARD_PARSER_RAW6=84, ARD_RX_VALID=90,
 ARD_FAULT_COUNT=92, ARD_FAULT_CONTROL=94, ARD_FAULT_EVENT=95,
 ARD_QUERY=96, ARD_CAP_HITS=100, ARD_CLEAN_EMPTY=104,
 ARD_FIRST_RBR=108, ARD_FIRST_RBR_CONTROL=110, ARD_FIRST_RBR_VALID=111,
 ARD_LAST_RBR=112, ARD_LAST_RBR_CONTROL=114, ARD_LAST_RBR_VALID=115,
 ARD_GAP_FLAGS=116
};
enum { ARD_ADMITTED=1, ARD_FROZEN=2, ARD_CLOCK_INVALID=4,
 ARD_OVERFLOW=8, ARD_PARTIAL=16, ARD_REARM_GAP=32, ARD_OWNER_INVALID=64,
 ARD_RAW_ERROR=128 };
enum { ARD_RX_LSR_VALID=1, ARD_RX_REMAINING_VALID=2,
 ARD_RX_PC_VALID=4, ARD_RX_HOLD_VALID=8, ARD_RX_PARSER_VALID=16 };
/* Span24 offsets: epoch4/sequence4/tag1/flags1/entryPC1/exitPC1,
 * start2/end2/derivedDuration2/startControl1/endControl1/innerTag1/depth1/res2.
 * Runtime derivedDuration stays ZERO/INVALID. Stopped decoder derives only
 * same-epoch nonzero descending valid0x0d endpoints; never wrap arithmetic.
 */
enum { ARD_SPAN_PRESENT=1, ARD_START_CAPTURED=2, ARD_END_CAPTURED=4,
 ARD_DURATION_VALID=8, ARD_ACTIVE_AT_FAULT=16, ARD_MISSING_BOUNDARY=32,
 ARD_CROSS_EPOCH=64 };
/* Runtime never sets DURATION_VALID. Native endpoints/captured controls alone
 * are raw evidence. Decoder requires flags1/2/4, both controls0x0d, same epoch,
 * start/end nonzero and start>=end. Eight bounded nested tags retain matching
 * entry/end identity; overflow/mismatch is partial, never a CPU timing stack. PARTIAL globally describes omitted tails,
 * not permission to treat a missing end as0. Current active-at-fault is
 * explicitly bit16; there is no measured all-IRQ gap. Gap_flags is reserved0
 * until an actual gap boundary is captured; REARM_GAP means excluded interval,
 * never a duration. Overflow invalidates derived spans rather than wrapping. */
enum { ARD_U0_RX=1, ARD_U0_TX=2, ARD_U1_DRAIN=3, ARD_VBLANK=4,
 ARD_FOREGROUND=5, ARD_APP_GUARD=6, ARD_PACKET=0x10, ARD_SERVICE=0x11,
 ARD_FIRST_READ=0x20, ARD_CAP=0x21, ARD_EMPTY=0x22, ARD_ERROR=0x40 };
extern volatile uint8_t agon_rxdiag_record[AGON_RXDIAG_BYTES];
/* entry is an ADDRESS only, never call it as C. Native marker ABI:
 * A=event; B=raw drain REMAINING, C=existing sample for RX events only;
 * D=owner PC_DR, E=owner scoped hold, HL=immediate six-byte parser prefix.
 * Event40 alone interprets C as LSR. First-read20 would carry DATA. Do not
 * retain HL. All primary/shadow/ADL registers and IFF remain unchanged.
 */
void agon_rxdiag_entry(void);
/* Before OPEN association, caller explicitly admits disposable inactive PRT1,
 * source bits/vector/reload/pending state. No PRT0/vector/IRQ edits. Fresh
 * record initialized only here; never clear after hook association begins. */
/* Pure one-time record initialization for the NULL-marker control; no timer
 * reads or writes. Returns0 on repeat, never clears an associated/frozen record. */
int agon_rxdiag_init(void);
int agon_rxdiag_admit(void);
/* Caller establishes no live TX source/drain and a foreground boundary; no
 * pending NM alone is insufficient. Returns0 on frozen/live/expired/unsafe
 * publication. Once started readiness fails, the clock is retired and later
 * rearm/admit refuse for this app lifetime; CLOSE association still required.
 * The readiness loop is IRQ-enabled, each timer access bounded
 * atomic, and final publication rechecks first-fault/span state. Nominal72kHz,
 * /256 single pass65536, not external calibration or complete IRQ coverage. */
int agon_rxdiag_rearm(uint32_t epoch, uint8_t no_live_source);
void agon_rxdiag_freeze(void);
/* Stops owned timer, restores only owned source bits; does NOT detach hook,
 * clear fault, cancel source or authorize unload. Owner CLOSE remains required. */
void agon_rxdiag_stop(void);
#endif
