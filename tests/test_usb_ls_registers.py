"""Execute generated HCD ISR/dequeue diagnostics; no hardware or target build."""
from pathlib import Path
import os
import re
import subprocess
import tempfile
import unittest

from usb_fsls_build_test import generate


def function(source, name):
    match = re.search(r"^[^\n;]*\b" + re.escape(name) + r"\([^;{}]*\)\s*\{",
                      source, re.MULTILINE)
    if match is None:
        raise AssertionError("Missing generated function: " + name)
    end, depth = match.end(), 1
    while depth and end < len(source):
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    if depth:
        raise AssertionError("Unterminated generated function: " + name)
    return source[match.start():end]


HARNESS = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/queue.h>
typedef struct urb_s {
    void *hcd_ptr; int hcd_var; TAILQ_ENTRY(urb_s) tailq_entry;
} urb_t;
typedef struct { volatile uint32_t val; } reg_t;
typedef struct { reg_t hcint_reg, hcchar_reg, hctsiz_reg; } channel_regs_t;
typedef struct { reg_t hcfg_reg, gusbcfg_reg, hfir_reg, hprt_reg; } usb_dwc_dev_t;
typedef struct { usb_dwc_dev_t *dev; struct { unsigned hsphy_type; } constant_config; } hal_t;
static struct { reg_t fc_06; } USB_UTMI;
typedef struct { channel_regs_t *regs; } usb_dwc_hal_chan_t;
typedef int usb_dwc_hal_chan_event_t, usb_dwc_hal_chan_error_t, hcd_pipe_event_t, usb_speed_t;
enum { USB_SPEED_LOW=0, USB_DWC_XFER_TYPE_CTRL=0, HCD_PIPE_STATE_HALTED=2,
       URB_HCD_STATE_IDLE=0, URB_HCD_STATE_DONE=3, HCD_PIPE_EVENT_NONE=0,
       HCD_PIPE_EVENT_URB_DONE=1, USB_DWC_HAL_CHAN_EVENT_CPLT=0,
       USB_DWC_HAL_CHAN_EVENT_ERROR=1, USB_DWC_HAL_CHAN_EVENT_HALT_REQ=2,
       USB_DWC_HAL_CHAN_EVENT_NONE=3 };
typedef struct { unsigned type, dev_addr, bEndpointAddress, ls_via_fs_hub, mps; } usb_dwc_hal_ep_char_t;
typedef struct { urb_t *urb; struct { struct { unsigned cur_stg; } ctrl; } flags; } dma_buffer_block_t;
typedef struct pipe_obj pipe_t;
TAILQ_HEAD(pipe_head, pipe_obj);
typedef struct {
    struct pipe_head pipes_active_tailq, pipes_idle_tailq;
    unsigned num_pipes_idle, num_pipes_queued;
    hal_t *hal; int speed; struct { unsigned conn_dev_ena; } flags;
} port_t;
__STORAGE__
struct pipe_obj {
    extender_ls_error_t extender_ls_error;
    TAILQ_HEAD(urb_head, urb_s) done_urb_tailq;
    TAILQ_ENTRY(pipe_obj) tailq_entry;
    unsigned num_urb_done, num_urb_pending;
    struct { unsigned has_urb, waiting_halt; } cs_flags;
    struct { unsigned buffer_num_to_exec, buffer_num_to_parse, rd_idx; } multi_buffer_control;
    dma_buffer_block_t *buffers[2];
    usb_dwc_hal_ep_char_t ep_char;
    port_t *port; hcd_pipe_event_t last_event; unsigned state;
};
typedef pipe_t *hcd_pipe_handle_t;
static usb_dwc_dev_t hardware;
static channel_regs_t channel;
static hal_t hal={.dev=&hardware};
static usb_dwc_hal_chan_t chan={.regs=&channel};
static bool locked, in_isr, completed, poison_on_unlock;
static pipe_t *poison_pipe;
static unsigned emitted, frame_reads, decodes, done_calls, parse_calls, continues, notifications;
static unsigned done_event, done_cancelled, selected_error=0;
static usb_dwc_hal_chan_event_t selected_event;
static char line[1024];
static void seed_registers(void) {
    channel.hcint_reg.val=0x11111111; channel.hcchar_reg.val=0x22222222;
    channel.hctsiz_reg.val=0x33333333; hardware.hcfg_reg.val=0x44444444;
    hardware.gusbcfg_reg.val=0x55555555; hardware.hfir_reg.val=0x66666666;
    hardware.hprt_reg.val=0x77777777; USB_UTMI.fc_06.val=0x88888888;
    frame_reads=decodes=done_calls=parse_calls=continues=notifications=0;
}
static void mutate_registers(void) {
    channel.hcint_reg.val=0; channel.hcchar_reg.val=0xa2222222;
    channel.hctsiz_reg.val=0xa3333333; hardware.hcfg_reg.val=0xa4444444;
    hardware.gusbcfg_reg.val=0xa5555555; hardware.hfir_reg.val=0xa6666666;
    hardware.hprt_reg.val=0xa7777777; USB_UTMI.fc_06.val=0xa8888888;
}
static uint32_t usb_dwc_hal_port_get_cur_frame_num(hal_t *context) {
    assert(locked && in_isr && context==&hal && !decodes);
    ++frame_reads; return 0x1234;
}
static usb_dwc_hal_chan_event_t usb_dwc_hal_chan_decode_intr(usb_dwc_hal_chan_t *c) {
    assert(locked && in_isr && c==&chan);
    /* No diagnostic may acknowledge/change hardware. The real HAL decoder is
       the destructive boundary; mutate every register to catch late reads. */
    assert(channel.hcint_reg.val==0x11111111 && channel.hcchar_reg.val==0x22222222);
    assert(channel.hctsiz_reg.val==0x33333333 && hardware.hcfg_reg.val==0x44444444);
    assert(hardware.gusbcfg_reg.val==0x55555555 && hardware.hfir_reg.val==0x66666666);
    assert(hardware.hprt_reg.val==0x77777777 && USB_UTMI.fc_06.val==0x88888888);
    ++decodes; mutate_registers(); return selected_event;
}
static usb_dwc_hal_chan_error_t usb_dwc_hal_chan_get_error(usb_dwc_hal_chan_t *c) {
    assert(locked && in_isr && c==&chan && decodes==1); return selected_error;
}
static int usb_dwc_hal_chan_get_qtd_idx(usb_dwc_hal_chan_t *c) {
    assert(locked && in_isr && c==&chan); return 9;
}
static hcd_pipe_event_t pipe_decode_error_event(usb_dwc_hal_chan_error_t error) { return 40+error; }
static bool _buffer_check_done(pipe_t *p) { (void)p; return completed; }
static void _buffer_exec_cont(pipe_t *p) { (void)p; assert(locked && in_isr); ++continues; }
static bool _buffer_can_exec(pipe_t *p) { (void)p; return false; }
static bool _buffer_can_fill(pipe_t *p) { (void)p; return false; }
static void _buffer_exec(pipe_t *p) { (void)p; assert(!"Unexpected second execution"); }
static void _buffer_fill(pipe_t *p) { (void)p; assert(!"Unexpected refill"); }
static void _buffer_done(pipe_t *p, int stop, unsigned event, bool cancelled) {
    (void)p; assert(locked && in_isr && stop==9); ++done_calls;
    done_event=event; done_cancelled=cancelled;
}
static void enqueue_done(pipe_t *p, urb_t *u) {
    u->hcd_ptr=p; u->hcd_var=URB_HCD_STATE_DONE;
    TAILQ_INSERT_TAIL(&p->done_urb_tailq,u,tailq_entry); ++p->num_urb_done;
}
static void _buffer_parse(pipe_t *p) {
    assert(locked && in_isr); ++parse_calls;
    dma_buffer_block_t *b=p->buffers[p->multi_buffer_control.rd_idx];
    assert(b->urb); enqueue_done(p,b->urb);
    b->urb=NULL; b->flags.ctrl.cur_stg=0; // SDK parse consumes URB and clears flags.
}
static bool _internal_pipe_event_notify(pipe_t *p, bool from_isr) {
    (void)p; assert(locked && in_isr && from_isr); ++notifications; return true;
}
static void unlock_dequeue(void) {
    assert(locked && !in_isr); locked=false;
    if (poison_on_unlock) {
        /* The task log must use detached copies, not any live pipe fields. */
        poison_pipe->port=NULL; memset(&poison_pipe->ep_char,0,sizeof(poison_pipe->ep_char));
        memset(&poison_pipe->extender_ls_error,0,sizeof(poison_pipe->extender_ls_error));
        poison_on_unlock=false;
    }
}
#define HCD_ENTER_CRITICAL() do { assert(!locked && !in_isr); locked=true; } while (0)
#define HCD_EXIT_CRITICAL() unlock_dequeue()
#define CACHE_SYNC_DATA_BUFFER_M2C(pipe, urb) do { assert(locked && !in_isr); } while (0)
static void emit_error(const char *tag, const char *format, ...) {
    assert(!locked && !in_isr); (void)tag;
    va_list ap; va_start(ap,format); vsnprintf(line,sizeof(line),format,ap); va_end(ap); ++emitted;
}
#define HCD_DWC_TAG "HCD DWC"
#define ESP_LOGE(...) emit_error(__VA_ARGS__)
__ISR__
__DEQUEUE__
static hcd_pipe_event_t interrupt(pipe_t *p, unsigned event) {
    selected_event=event; bool yield=false; locked=in_isr=true;
    hcd_pipe_event_t result=_intr_hdlr_chan(p,&chan,&yield);
    locked=in_isr=false;
    assert(decodes==1 && yield==(event==USB_DWC_HAL_CHAN_EVENT_HALT_REQ)); return result;
}
static void init(pipe_t *p, port_t *port, dma_buffer_block_t *b, urb_t *u, unsigned stage) {
    memset(p,0,sizeof(*p)); memset(b,0,sizeof(*b)); memset(u,0,sizeof(*u));
    port->hal=&hal; port->speed=1; port->flags.conn_dev_ena=1;
    p->port=port; p->buffers[0]=b; p->cs_flags.waiting_halt=1;
    p->ep_char=(usb_dwc_hal_ep_char_t){.type=0,.mps=8,.ls_via_fs_hub=1};
    b->urb=u; b->flags.ctrl.cur_stg=stage; TAILQ_INIT(&p->done_urb_tailq);
    hal.constant_config.hsphy_type=2; completed=true;
    seed_registers();
}
static void check_log(unsigned stage, unsigned error, unsigned hsphy) {
    char expected[128];
    snprintf(expected,sizeof(expected),"stage=%u hal_error=%u frame=4660",stage,error);
    assert(strstr(line,expected));
    assert(strstr(line,"addr=0 ep=0 port_speed=1 ls_pre=1 mps=8"));
    assert(strstr(line,"hcint=11111111 hcchar=22222222 hctsiz=33333333 hcfg=44444444"));
    assert(strstr(line,"gusbcfg=55555555 hfir=66666666 hprt=77777777"));
    snprintf(expected,sizeof(expected),"hsphy=%u utmi_fc06=%08x",hsphy,hsphy?0x88888888u:0u);
    assert(strstr(line,expected));
}
int main(void) {
    port_t port={0}; pipe_t p; dma_buffer_block_t b; urb_t failed,older={0};
    unsigned cases=0;
    init(&p,&port,&b,&failed,0); enqueue_done(&p,&older); selected_error=0;
    assert(interrupt(&p,USB_DWC_HAL_CHAN_EVENT_ERROR)==40);
    assert(frame_reads==1 && done_calls==1 && parse_calls==1 && done_event==40 && !done_cancelled);
    assert(p.state==HCD_PIPE_STATE_HALTED && p.last_event==40);
    assert(p.extender_ls_error.urb==&failed && p.extender_ls_error.stage==0 && !emitted);
    assert(!b.urb && !b.flags.ctrl.cur_stg && !channel.hcint_reg.val);
    mutate_registers(); // Later hardware state must not substitute the failure snapshot.
    assert(hcd_urb_dequeue(&p)==&older && !emitted && p.extender_ls_error.urb==&failed);
    poison_pipe=&p; poison_on_unlock=true;
    assert(hcd_urb_dequeue(&p)==&failed && emitted==1); check_log(0,0,2);
    p.port=&port;
    assert(hcd_urb_dequeue(&p)==NULL && emitted==1); ++cases;
    /* A later failure may reuse a returned URB: capture new stage/error once. */
    init(&p,&port,&b,&failed,2); selected_error=3;
    assert(interrupt(&p,USB_DWC_HAL_CHAN_EVENT_ERROR)==43);
    assert(hcd_urb_dequeue(&p)==&failed && emitted==2); check_log(2,3,2);
    assert(p.extender_ls_error.urb==NULL && hcd_urb_dequeue(&p)==NULL && emitted==2); ++cases;
    /* Actual PHY marker zero must leave UTMI absent, rather than reuse old MMIO. */
    init(&p,&port,&b,&failed,1); selected_error=1; hal.constant_config.hsphy_type=0;
    assert(interrupt(&p,USB_DWC_HAL_CHAN_EVENT_ERROR)==41 && frame_reads==1);
    assert(hcd_urb_dequeue(&p)==&failed && emitted==3); check_log(1,1,0); ++cases;
    /* Non-control IN/OUT and full-speed control keep their original error
       actions without touching the diagnostic's frame/MMIO path or record. */
    for (unsigned type=0;type<4;++type) for (unsigned low=0;low<2;++low) {
        if (!type && low) continue;
        for (unsigned input=0;input<2;++input) {
            init(&p,&port,&b,&failed,1); p.ep_char.type=type;
            p.ep_char.ls_via_fs_hub=low; p.ep_char.bEndpointAddress=input?0x81:1;
            assert(interrupt(&p,USB_DWC_HAL_CHAN_EVENT_ERROR)==41);
            assert(!frame_reads && !p.extender_ls_error.urb && done_calls==1 && parse_calls==1);
            assert(p.state==HCD_PIPE_STATE_HALTED && !done_cancelled);
            assert(hcd_urb_dequeue(&p)==&failed && emitted==3); ++cases;
        }
    }
    /* Success, control-stage continuation, requested halt and no-event preserve
       original queue/notification behavior and never retain/log diagnostics. */
    for (unsigned event=0;event<=USB_DWC_HAL_CHAN_EVENT_NONE;++event) {
        if (event==USB_DWC_HAL_CHAN_EVENT_ERROR) continue;
        init(&p,&port,&b,&failed,1);
        hcd_pipe_event_t result=interrupt(&p,event);
        assert(frame_reads==1 && !p.extender_ls_error.urb && emitted==3);
        if (event==USB_DWC_HAL_CHAN_EVENT_NONE) {
            assert(result==HCD_PIPE_EVENT_NONE && !done_calls && !parse_calls && !notifications);
        } else {
            assert(result==HCD_PIPE_EVENT_URB_DONE && done_calls==1 && parse_calls==1);
            assert(done_cancelled==(event==USB_DWC_HAL_CHAN_EVENT_HALT_REQ));
            assert(done_event==(event==USB_DWC_HAL_CHAN_EVENT_HALT_REQ?HCD_PIPE_EVENT_NONE:HCD_PIPE_EVENT_URB_DONE));
            assert(notifications==(event==USB_DWC_HAL_CHAN_EVENT_HALT_REQ));
            assert(hcd_urb_dequeue(&p)==&failed && emitted==3);
        }
        ++cases;
    }
    init(&p,&port,&b,&failed,0); completed=false;
    assert(interrupt(&p,USB_DWC_HAL_CHAN_EVENT_CPLT)==HCD_PIPE_EVENT_NONE);
    assert(continues==1 && !done_calls && !parse_calls && !p.extender_ls_error.urb && emitted==3); ++cases;
    printf("LS register snapshot: %u actual ISR/dequeue lifecycle cases passed\n",cases);
    return 0;
}
'''


class UsbLsRegisterTests(unittest.TestCase):
    def test_actual_generated_predecode_registers_survive_parser_and_dequeue(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            text = generate(work / "hcd.c")
            isr = function(text, "_intr_hdlr_chan")
            dequeue = function(text, "hcd_urb_dequeue")
            storage = re.search(r"typedef struct \{\s*urb_t \*urb;.*?\} extender_ls_error_t;",
                                text, re.DOTALL)
            self.assertIsNotNone(storage)
            before_decode = isr.split("usb_dwc_hal_chan_decode_intr(chan_obj)", 1)[0]
            # Diagnostic register access must be read-only; the original HAL
            # decoder remains the sole acknowledge/program boundary here.
            self.assertNotRegex(before_decode, r"(?:hcint_reg|hcchar_reg|hctsiz_reg|hcfg_reg|gusbcfg_reg|hfir_reg|hprt_reg|fc_06)\.val\s*=")
            self.assertNotIn("ESP_LOG", isr)
            self.assertNotIn("pipe->", dequeue.split("HCD_EXIT_CRITICAL();", 1)[1])
            harness = HARNESS.replace("__STORAGE__", storage.group()).replace(
                "__ISR__", isr).replace("__DEQUEUE__", dequeue)
            source, executable = work / "registers.c", work / "registers"
            source.write_text(harness)
            result = subprocess.run(
                ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                 "-fsanitize=address,undefined", str(source), "-o", str(executable)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            environment = dict(os.environ)
            previous = environment.get("ASAN_OPTIONS", "")
            environment["ASAN_OPTIONS"] = previous + (":" if previous else "") + "detect_leaks=0"
            result = subprocess.run([str(executable)], capture_output=True, text=True, env=environment)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("21 actual ISR/dequeue lifecycle cases passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
