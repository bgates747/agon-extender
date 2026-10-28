"""Fail-closed SDK backport generation and board-selection guard."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SDK_SOURCE = ROOT / "agents/build001/native-tools/esp-idf/components/usb/hcd_dwc.c"
RECIPE = ROOT / "vdp/native/usb_fsls_only.cmake"
sys.path.insert(0, str(ROOT / "scripts"))
from validate_p4_build import check_usb_hcd_derivative


def generate(output: Path) -> str:
    subprocess.run(["cmake", f"-DUSB_HCD_SOURCE={SDK_SOURCE}",
                    f"-DUSB_HCD_OUTPUT={output}", "-P", str(RECIPE)],
                   check=True, capture_output=True)
    return output.read_text()


class UsbFslsBuildTest(unittest.TestCase):
    def test_known_sdk_derivative_and_rejection_of_changed_dependency(self):
        original = SDK_SOURCE.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            source, output = work / "hcd.c", work / "patched.c"
            source.write_bytes(original)
            command = ["cmake", f"-DUSB_HCD_SOURCE={source}",
                       f"-DUSB_HCD_OUTPUT={output}", "-P", str(RECIPE)]
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(source.read_bytes(), original)
            self.assertNotEqual(output.read_bytes(), original)
            output.unlink()
            source.write_bytes(original + b"\n// changed dependency\n")
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unreviewed USB HCD source", result.stderr)
            self.assertFalse(output.exists())

    def test_devkit_fsls_request_rejected_before_build_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "uncreated"
            result = subprocess.run(
                [str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/build_p4.py"),
                 "--profile", "p4-console", "--board", "p4-devkit",
                 "--usb-fsls-only", "--output", str(output)],
                capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires p4-pc / p4-console", result.stderr)
            self.assertFalse(output.exists())

    def test_validator_rejects_changes_anywhere_in_complete_derivative(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "patched.c"
            text = generate(output)
            check_usb_hcd_derivative(SDK_SOURCE, output)
            for altered in (text + "\n// unrelated change\n",
                            text.replace("if (!done || is_in || is_ctrl)",
                                         "if ((is_in == done) || is_ctrl)"),
                            text.replace("ls_error.stage", "ls_error.frame")):
                self.assertNotEqual(altered, text)
                output.write_text(altered)
                with self.assertRaisesRegex(SystemExit, "complete bounded"):
                    check_usb_hcd_derivative(SDK_SOURCE, output)

    def test_ls_error_snapshot_lifecycle_and_task_only_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            text = generate(work / "patched.c")
            isr = text.split("static hcd_pipe_event_t _intr_hdlr_chan(", 1)[1]
            isr = isr.split("static void intr_hdlr_main(", 1)[0]
            error = isr.split("case USB_DWC_HAL_CHAN_EVENT_ERROR: {", 1)[1]
            error = error.split("case USB_DWC_HAL_CHAN_EVENT_HALT_REQ:", 1)[0]
            capture = error[error.index("        if (pipe->ep_char.type"):]
            capture = capture.split("        pipe->last_event", 1)[0]
            self.assertIn("pipe->ep_char.ls_via_fs_hub", capture)
            self.assertIn("failed->flags.ctrl.cur_stg", capture)
            self.assertNotIn("ESP_LOG", isr)
            self.assertLess(error.index("extender_ls_error.stage"),
                            error.index("_buffer_parse(pipe)"))
            dequeue = "urb_t *hcd_urb_dequeue(" + text.split(
                "urb_t *hcd_urb_dequeue(", 1)[1].split("esp_err_t hcd_urb_abort(", 1)[0]
            after_unlock = dequeue.split("    HCD_EXIT_CRITICAL();", 1)[1]
            self.assertNotIn("pipe->", after_unlock)
            self.assertNotIn("ESP_LOG", dequeue.split("    HCD_EXIT_CRITICAL();", 1)[0])
            self.assertEqual(after_unlock.count("ESP_LOGE("), 1)
            storage = text.split("typedef struct {\n    urb_t *urb;", 1)[1]
            storage = "typedef struct {\n    urb_t *urb;" + storage.split("} extender_ls_error_t;", 1)[0] + "} extender_ls_error_t;"
            # Compile the actual generated capture and dequeue, with queue/lock
            # spies. This checks URB ownership and lifetime rather than copying
            # the diagnostic implementation into a Python model.
            harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <sys/queue.h>
typedef struct urb_s {
    void *hcd_ptr;
    int hcd_var;
    TAILQ_ENTRY(urb_s) tailq_entry;
} urb_t;
typedef struct { unsigned type, dev_addr, bEndpointAddress, ls_via_fs_hub, mps; } usb_dwc_hal_ep_char_t;
typedef int usb_speed_t;
#define USB_SPEED_LOW 0
#define USB_DWC_XFER_TYPE_CTRL 0
#define URB_HCD_STATE_IDLE 0
#define URB_HCD_STATE_DONE 3
typedef struct { urb_t *urb; struct { struct { unsigned cur_stg; } ctrl; } flags; } dma_buffer_block_t;
typedef struct pipe_obj pipe_t;
TAILQ_HEAD(pipe_head, pipe_obj);
typedef struct { struct pipe_head pipes_active_tailq, pipes_idle_tailq; unsigned num_pipes_idle, num_pipes_queued; void *hal; int speed; } port_t;
''' + storage + r'''
struct pipe_obj {
    extender_ls_error_t extender_ls_error;
    TAILQ_HEAD(urb_head, urb_s) done_urb_tailq;
    TAILQ_ENTRY(pipe_obj) tailq_entry;
    unsigned num_urb_done, num_urb_pending;
    struct { unsigned has_urb; } cs_flags;
    struct { unsigned buffer_num_to_exec, buffer_num_to_parse, rd_idx; } multi_buffer_control;
    dma_buffer_block_t *buffers[2];
    usb_dwc_hal_ep_char_t ep_char;
    port_t *port;
};
typedef pipe_t *hcd_pipe_handle_t;
static bool locked, in_isr;
static unsigned emitted, got_stage, got_error, got_frame;
static uint32_t usb_dwc_hal_port_get_cur_frame_num(void *hal) {
    assert(locked && in_isr); (void)hal; return 1234;
}
#define HCD_ENTER_CRITICAL() do { assert(!locked && !in_isr); locked = true; } while (0)
#define HCD_EXIT_CRITICAL() do { assert(locked && !in_isr); locked = false; } while (0)
#define CACHE_SYNC_DATA_BUFFER_M2C(pipe, urb) do { assert(locked); } while (0)
static void emit_error(const char *tag, const char *format, unsigned addr, unsigned ep,
                       unsigned speed, unsigned pre, unsigned mps, unsigned stage,
                       unsigned error, unsigned frame) {
    assert(!locked && !in_isr);
    assert(addr == 0 && ep == 0 && speed == 1 && pre == 1 && mps == 8);
    (void)tag; (void)format;
    emitted++; got_stage=stage; got_error=error; got_frame=frame;
}
#define HCD_DWC_TAG "HCD DWC"
#define ESP_LOGE(...) emit_error(__VA_ARGS__)
static void capture_failure(pipe_t *pipe, unsigned chan_error) {
    assert(locked && in_isr);
''' + capture + r'''
}
''' + dequeue + r'''
static void enqueue_done(pipe_t *p, urb_t *u) {
    u->hcd_ptr=p; u->hcd_var=URB_HCD_STATE_DONE;
    TAILQ_INSERT_TAIL(&p->done_urb_tailq,u,tailq_entry); p->num_urb_done++;
}
static void fail(pipe_t *p, unsigned error) {
    in_isr=true; locked=true; capture_failure(p,error); locked=false; in_isr=false;
}
int main(void) {
    port_t port={.speed=1}; pipe_t p={.port=&port};
    dma_buffer_block_t b={0}; urb_t older={0}, failed={0};
    TAILQ_INIT(&p.done_urb_tailq); p.buffers[0]=&b;
    p.ep_char=(usb_dwc_hal_ep_char_t){.type=0,.mps=8,.ls_via_fs_hub=1};
    b.urb=&failed; b.flags.ctrl.cur_stg=1;
    fail(&p,0);
    assert(p.extender_ls_error.urb==&failed && !emitted);
    b.flags.ctrl.cur_stg=0; // _buffer_parse clears its flags before task dequeue.
    enqueue_done(&p,&older); enqueue_done(&p,&failed);
    assert(hcd_urb_dequeue(&p)==&older && !emitted);
    assert(p.extender_ls_error.urb==&failed);
    assert(hcd_urb_dequeue(&p)==&failed && emitted==1);
    assert(got_stage==1 && got_error==0 && got_frame==1234);
    assert(p.extender_ls_error.urb==NULL);
    assert(hcd_urb_dequeue(&p)==NULL && emitted==1);
    // Later failures may reuse the URB; each is consumed exactly once.
    b.flags.ctrl.cur_stg=2; fail(&p,3); enqueue_done(&p,&failed);
    assert(hcd_urb_dequeue(&p)==&failed && emitted==2);
    assert(got_stage==2 && got_error==3);
    // Full-speed control and LS non-control failures do not create records.
    p.ep_char.ls_via_fs_hub=0; fail(&p,0); assert(p.extender_ls_error.urb==NULL);
    p.ep_char.ls_via_fs_hub=1; p.ep_char.type=1; fail(&p,0);
    assert(p.extender_ls_error.urb==NULL && emitted==2);
    return 0;
}
'''
            source = work / "lifecycle.c"
            source.write_text(harness)
            subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                            str(source), "-o", str(work / "lifecycle")],
                           check=True, capture_output=True)
            subprocess.run([str(work / "lifecycle")], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
