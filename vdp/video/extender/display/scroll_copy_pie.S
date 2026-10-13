/*
 * SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: 2021 Espressif Systems (Shanghai) Co., Ltd.
 *
 * RESEARCH-007 project-owned bounded adaptation of ESP-DL3.3.9
 * dl/tool/isa/esp32p4/dl_esp32p4_memcpy.S, commit
 * 12c0616de145b704e1149c474b9a1e852e631d67 (esp-dl/ subdirectory):
 * https://github.com/espressif/esp-dl/blob/12c0616de145b704e1149c474b9a1e852e631d67/esp-dl/dl/tool/isa/esp32p4/dl_esp32p4_memcpy.S
 *
 * The aligned32-byte copy loop and unaligned vector-splice traversal follow
 * upstream. Differences: the C++ caller handles edges; the source is explicitly
 * aligned before entry; SAR_BYTES is supplied directly instead of obtaining it
 * through an unaligned load. Thus the kernel is independent of PIE CFG.mis_ld
 * and CFG.mis_st, performs no speculative destination reads and never changes
 * CFG. Preserve this bound if replacing it with upstream's general memcpy.
 *
 * C ABI: a0=16-aligned destination; a1=16-aligned source base;
 * a2=nonzero multiple-of32 byte count; a3=source byte shift0..15.
 * The C++ caller supplies at least16 valid source bytes on both sides of the
 * nominal body. Aligned source needs exactly a2 bytes; shifted source reads
 * a2+16 bytes starting at a1. Only a2 destination bytes are written.
 * Clobbers caller-saved a0/a1/a2, q0/q1/q2 and task-saved SAR_BYTES. No stack,
 * callee-saved GPR, FPU, hardware-loop, interrupt-mask or peripheral state.
 * Task context only: IDF5.5.5 portasm.S saves/restores these PIE registers and
 * vectors.S lazily enables PIE. ISRs must use the C++ libc fallback.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

// Selector plumbing only: both callers reuse the exact same proven kernel.
#if ((defined(AGON_EXTENDER_SCROLL_FAST) && AGON_EXTENDER_SCROLL_FAST) || \
     (defined(AGON_EXTENDER_INDEXED_SNAPSHOT_PIE) && AGON_EXTENDER_INDEXED_SNAPSHOT_PIE)) && defined(ESP_PLATFORM)
#include "sdkconfig.h"
#if !CONFIG_IDF_TARGET_ESP32P4 || !defined(__riscv_xesppie) || __riscv_xlen != 32 || CONFIG_ESP_REV_MIN_FULL < 100
#error "P4 row-copy assembly requires reviewed ESP32-P4 v1.x-or-newer RV32+XEspPIE"
#endif
    .section .iram1.agon_extender_scroll_copy_pie,"ax",@progbits
    .balign 4
    .global agon_extender_scroll_copy_pie
    .type agon_extender_scroll_copy_pie, @function
    .option push
    .option norvc
agon_extender_scroll_copy_pie:
    beqz a2, .Lscroll_done
    beqz a3, .Lscroll_aligned
    esp.movx.w.sar.bytes a3
.Lscroll_shifted:
    esp.vld.128.ip q0, a1, 16
    esp.vld.128.ip q1, a1, 16
    esp.vld.128.ip q2, a1, 0
    esp.src.q q0, q0, q1
    esp.src.q q1, q1, q2
    esp.vst.128.ip q0, a0, 16
    esp.vst.128.ip q1, a0, 16
    addi a2, a2, -32
    bnez a2, .Lscroll_shifted
    ret
.Lscroll_aligned:
    esp.vld.128.ip q0, a1, 16
    esp.vld.128.ip q1, a1, 16
    esp.vst.128.ip q0, a0, 16
    esp.vst.128.ip q1, a0, 16
    addi a2, a2, -32
    bnez a2, .Lscroll_aligned
.Lscroll_done:
    ret
    .option pop
    .size agon_extender_scroll_copy_pie, .-agon_extender_scroll_copy_pie
#endif
    .section .note.GNU-stack,"",@progbits
