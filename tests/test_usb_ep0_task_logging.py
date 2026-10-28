"""Execute the generated USBH callbacks/actions; no USB device or target build."""
from pathlib import Path
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SDK_SOURCE = ROOT / "agents/build001/native-tools/esp-idf/components/usb/usbh.c"
RECIPE = ROOT / "vdp/native/usb_ep0_task_logging.cmake"


def generate(source: Path, output: Path):
    return subprocess.run(
        ["cmake", f"-DUSBH_SOURCE={source}", f"-DUSBH_OUTPUT={output}",
         "-P", str(RECIPE)], capture_output=True, text=True)


def function(source: str, name: str) -> str:
    """Extract an actual definition, skipping its forward declaration."""
    match = re.search(r"^[^\n;]*\b" + re.escape(name) + r"\([^;{}]*\)\s*\{",
                      source, re.MULTILINE)
    if match is None:
        raise AssertionError(f"Missing function definition: {name}")
    position, depth = match.end(), 1
    while depth and position < len(source):
        depth += (source[position] == "{") - (source[position] == "}")
        position += 1
    if depth:
        raise AssertionError(f"Unterminated function definition: {name}")
    return source[match.start():position]


HARNESS = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/queue.h>
#include <inttypes.h>
typedef int esp_err_t;
typedef void *hcd_pipe_handle_t;
typedef enum {
    HCD_PIPE_EVENT_URB_DONE, HCD_PIPE_EVENT_ERROR_XFER,
    HCD_PIPE_EVENT_ERROR_URB_NOT_AVAIL, HCD_PIPE_EVENT_ERROR_OVERFLOW,
    HCD_PIPE_EVENT_ERROR_STALL, HCD_PIPE_EVENT_UNKNOWN
} hcd_pipe_event_t;
enum { ESP_OK=0, ESP_ERR_INVALID_STATE=1, USB_PROC_REQ_SOURCE_USBH=3 };
__ACTIONS__
typedef struct device_s device_t;
struct device_s {
    struct {
        TAILQ_ENTRY(device_s) tailq_entry;
        struct { unsigned in_pending_list; } flags;
        uint32_t action_flags;
    } dynamic;
    struct { unsigned address; } constant;
    bool alive;
};
typedef struct {
    struct {
        TAILQ_HEAD(idle_devices, device_s) devs_idle_tailq;
        TAILQ_HEAD(pending_devices, device_s) devs_pending_tailq;
    } dynamic;
    struct {
        bool (*proc_req_cb)(int, bool, void *);
        void *proc_req_cb_arg;
    } constant;
} usbh_t;
static usbh_t host, *p_usbh_obj;
static device_t device, *observed_device;
static bool locked, isr, notification_result, inject_during_dequeue;
static unsigned wakes, bad_logs, errors, stalls, seen_count, seen[64];
static unsigned proc_cookie;
enum { LOG_ERROR=100, LOG_STALL=101, HALT=1, FLUSH, DEQUEUE, CLEAR,
       GONE, FREE_DEVICE, NEW_DEVICE };
static void lock(bool safe) {
    assert(!locked && (safe || !isr)); locked=true;
}
static void unlock(bool safe) {
    assert(locked && (safe || !isr)); locked=false;
}
#define USBH_ENTER_CRITICAL_SAFE() lock(true)
#define USBH_EXIT_CRITICAL_SAFE() unlock(true)
#define USBH_ENTER_CRITICAL() lock(false)
#define USBH_EXIT_CRITICAL() unlock(false)
#define USBH_CHECK_FROM_CRIT(c, v) do { if (!(c)) { unlock(false); return (v); } } while (0)
#define USBH_TAG "USBH"
#define ESP_LOGD(...) do {} while (0)
static void log_error(const char *tag, const char *format, unsigned address) {
    (void)tag;
    if (locked || isr) { ++bad_logs; return; }
    assert(observed_device->alive && address == observed_device->constant.address);
    assert(seen_count < 64);
    if (strstr(format,"STALL")) { ++stalls; seen[seen_count++]=LOG_STALL; }
    else { assert(strstr(format,"Error")); ++errors; seen[seen_count++]=LOG_ERROR; }
}
#define ESP_LOGE(...) log_error(__VA_ARGS__)
#define ESP_EARLY_LOGE(...) log_error(__VA_ARGS__)
static bool processing_request(int source, bool from_isr, void *arg) {
    assert(!locked && source==USB_PROC_REQ_SOURCE_USBH && from_isr==isr);
    assert(arg==&proc_cookie); ++wakes; return notification_result;
}
static bool _dev_set_actions(device_t *, uint32_t);
static bool ep0_pipe_callback(hcd_pipe_handle_t, hcd_pipe_event_t, void *, bool);
static void handle(device_t *d, unsigned action) {
    assert(!locked && !isr && d==observed_device && d->alive && seen_count<64);
    seen[seen_count++]=action;
}
static void handle_epn_halt_flush(device_t *d) { handle(d,HALT); }
static void handle_ep0_flush(device_t *d) { handle(d,FLUSH); }
static void handle_ep0_dequeue(device_t *d) {
    handle(d,DEQUEUE);
    if (inject_during_dequeue) {
        inject_during_dequeue=false;
        assert(ep0_pipe_callback(NULL,HCD_PIPE_EVENT_ERROR_STALL,d,false));
    }
}
static void handle_ep0_clear(device_t *d) { handle(d,CLEAR); }
static void handle_prop_gone_evt(device_t *d) { handle(d,GONE); }
static void handle_free(device_t *d) {
    handle(d,FREE_DEVICE);
    USBH_ENTER_CRITICAL();
    assert(!d->dynamic.flags.in_pending_list);
    TAILQ_REMOVE(&p_usbh_obj->dynamic.devs_idle_tailq,d,dynamic.tailq_entry);
    USBH_EXIT_CRITICAL();
    d->alive=false; d->constant.address=UINT32_MAX;
}
static void handle_prop_new_dev(device_t *d) {
    handle(d,NEW_DEVICE); d->constant.address=17;
}
__SET_ACTIONS__
__EP0_CALLBACK__
__PROCESS__
static void reset(void) {
    assert(!locked && !isr);
    memset(&host,0,sizeof(host)); memset(&device,0,sizeof(device));
    p_usbh_obj=&host; observed_device=&device; device.alive=true; device.constant.address=7;
    TAILQ_INIT(&host.dynamic.devs_idle_tailq); TAILQ_INIT(&host.dynamic.devs_pending_tailq);
    TAILQ_INSERT_TAIL(&host.dynamic.devs_idle_tailq,&device,dynamic.tailq_entry);
    host.constant.proc_req_cb=processing_request; host.constant.proc_req_cb_arg=&proc_cookie;
    wakes=bad_logs=errors=stalls=seen_count=0; notification_result=true; inject_during_dequeue=false;
}
static bool callback(hcd_pipe_event_t event, bool interrupt) {
    isr=interrupt; bool result=ep0_pipe_callback(NULL,event,&device,interrupt); isr=false;
    assert(!locked); return result;
}
static void add_actions(uint32_t actions) {
    USBH_ENTER_CRITICAL(); assert(!_dev_set_actions(&device,actions)); USBH_EXIT_CRITICAL();
}
static unsigned pending_count(void) {
    unsigned count=0; device_t *d;
    TAILQ_FOREACH(d,&host.dynamic.devs_pending_tailq,dynamic.tailq_entry) ++count;
    return count;
}
static bool checked_no_callback_logs(void) {
    if (bad_logs || errors || stalls) {
        fprintf(stderr,"EP0 callback logged before task processing\n"); return false;
    }
    return true;
}
int main(void) {
    unsigned cases=0;
    for (unsigned interrupt=0;interrupt<2;++interrupt) {
        for (unsigned event=0;event<=HCD_PIPE_EVENT_UNKNOWN;++event) {
            reset();
            uint32_t expected=event==HCD_PIPE_EVENT_URB_DONE?DEV_ACTION_EP0_DEQUEUE:
                event==HCD_PIPE_EVENT_UNKNOWN?0:
                event==HCD_PIPE_EVENT_ERROR_STALL?
                DEV_ACTION_EP0_DEQUEUE|DEV_ACTION_EP0_CLEAR|DEV_ACTION_EP0_LOG_STALL:
                DEV_ACTION_EP0_FLUSH|DEV_ACTION_EP0_DEQUEUE|DEV_ACTION_EP0_CLEAR|DEV_ACTION_EP0_LOG_ERROR;
            assert(callback(event,interrupt)==(expected!=0));
            if (!checked_no_callback_logs()) return 1;
            assert(device.dynamic.action_flags==expected && wakes==(expected!=0));
            assert(pending_count()==(expected!=0));
            assert(usbh_process()==ESP_OK && !locked);
            assert(errors==(unsigned)(event>=HCD_PIPE_EVENT_ERROR_XFER && event<=HCD_PIPE_EVENT_ERROR_OVERFLOW));
            assert(stalls==(unsigned)(event==HCD_PIPE_EVENT_ERROR_STALL));
            assert(!device.dynamic.action_flags && !device.dynamic.flags.in_pending_list && !pending_count());
            unsigned at=errors+stalls;
            if (expected&DEV_ACTION_EP0_FLUSH) assert(seen[at++]==FLUSH);
            if (expected&DEV_ACTION_EP0_DEQUEUE) assert(seen[at++]==DEQUEUE);
            if (expected&DEV_ACTION_EP0_CLEAR) assert(seen[at++]==CLEAR);
            assert(at==seen_count && !bad_logs);
            assert(usbh_process()==ESP_OK && at==seen_count); ++cases;
        }
    }
    /* An existing pending batch coalesces repeated callbacks and wakes once. */
    reset(); assert(callback(HCD_PIPE_EVENT_ERROR_XFER,true));
    assert(!callback(HCD_PIPE_EVENT_ERROR_OVERFLOW,false));
    assert(!callback(HCD_PIPE_EVENT_ERROR_URB_NOT_AVAIL,true));
    assert(!callback(HCD_PIPE_EVENT_ERROR_STALL,false));
    assert(!callback(HCD_PIPE_EVENT_URB_DONE,true));
    assert(pending_count()==1 && wakes==1 && checked_no_callback_logs());
    assert(usbh_process()==ESP_OK && errors==1 && stalls==1);
    assert(seen_count==5 && seen[0]==LOG_ERROR && seen[1]==LOG_STALL);
    assert(seen[2]==FLUSH && seen[3]==DEQUEUE && seen[4]==CLEAR); ++cases;
    /* Actual action-queue merging retains existing lifecycle flags. Logging
       precedes their handlers; FREE continues taking precedence over NEW. */
    for (unsigned freeing=0;freeing<2;++freeing) {
        reset(); assert(callback(HCD_PIPE_EVENT_ERROR_XFER,true));
        add_actions(DEV_ACTION_EPn_HALT_FLUSH|DEV_ACTION_PROP_GONE_EVT|
                    DEV_ACTION_PROP_NEW_DEV|(freeing?DEV_ACTION_FREE:0));
        assert(usbh_process()==ESP_OK && errors==1 && !stalls && !bad_logs);
        assert(seen_count==7 && seen[0]==LOG_ERROR && seen[1]==HALT && seen[2]==FLUSH);
        assert(seen[3]==DEQUEUE && seen[4]==CLEAR && seen[5]==GONE);
        assert(seen[6]==(freeing?FREE_DEVICE:NEW_DEVICE));
        assert(device.alive==!freeing && !pending_count()); ++cases;
    }
    /* An error arriving while a task handles an earlier batch gets one fresh
       request and one later log, rather than loss or an unbounded callback. */
    reset(); assert(callback(HCD_PIPE_EVENT_ERROR_XFER,true)); inject_during_dequeue=true;
    assert(usbh_process()==ESP_OK && errors==1 && stalls==1 && wakes==2);
    assert(seen_count==7 && seen[0]==LOG_ERROR && seen[4]==LOG_STALL && !pending_count()); ++cases;
    /* Preserve the original processing-request callback's yield return. */
    reset(); notification_result=false;
    assert(!callback(HCD_PIPE_EVENT_URB_DONE,true) && wakes==1 && pending_count()==1);
    assert(usbh_process()==ESP_OK && !bad_logs); ++cases;
    p_usbh_obj=NULL;
    assert(usbh_process()==ESP_ERR_INVALID_STATE && !locked); ++cases;
    printf("USBH deferred EP0 logging: %u callback/action/lifecycle cases passed\n",cases);
    return 0;
}
'''


class UsbEp0TaskLoggingTests(unittest.TestCase):
    def selected(self, work: Path) -> str:
        output = work / "usbh.c"
        result = generate(SDK_SOURCE, output)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return output.read_text()

    def test_generation_rejects_changed_sdk_and_validator_rejects_tampering(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        from validate_p4_build import check_usb_ep0_derivative
        original = SDK_SOURCE.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            selected = self.selected(work)
            output = work / "usbh.c"
            self.assertEqual(SDK_SOURCE.read_bytes(), original)
            check_usb_ep0_derivative(SDK_SOURCE, output)
            output.write_text(selected + "\n// unreviewed derivative\n")
            with self.assertRaises(SystemExit):
                check_usb_ep0_derivative(SDK_SOURCE, output)
            source, output = work / "changed-usbh.c", work / "must-not-exist.c"
            source.write_bytes(original + b"\n// changed SDK\n")
            result = generate(source, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unreviewed", result.stderr)
            self.assertFalse(output.exists())

    def test_validator_requires_selected_translation_unit_archive_and_elf(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        from validate_p4_build import check_usb_ep0_linkage
        with tempfile.TemporaryDirectory() as temporary:
            build = Path(temporary)
            output = build / "agon-extender-usb/usbh.c"
            result = generate(SDK_SOURCE, output)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            obj = "esp-idf/usb/CMakeFiles/__idf_usb.dir/generated/usbh.c.obj"
            action = {"file": str(output), "output": obj}
            archive = "build esp-idf/usb/libusb.a: C_STATIC_LIBRARY_LINKER__idf_usb_ " + obj
            elf = "build agon_extender.elf: C_EXECUTABLE_LINKER__agon_extender_ esp-idf/usb/libusb.a"
            ninja = archive + "\n" + elf + "\n"
            check_usb_ep0_linkage([action], ninja, build, True)
            stock = {"file": str(SDK_SOURCE), "output": "stock-usbh.c.obj"}
            check_usb_ep0_linkage([stock], ninja, build, False)
            check_usb_ep0_linkage([], "", build, False)
            failures = (
                ("missing compile action", [], ninja, True),
                ("duplicate compile actions", [action, action], ninja, True),
                ("unselected stock source", [stock], ninja, True),
                ("derivative while disabled", [action], ninja, False),
                ("missing archive", [action], elf, True),
                ("object name only a substring", [action],
                 archive.replace(obj, "prefix_" + obj) + "\n" + elf, True),
                ("duplicate archive edges", [action], ninja + archive, True),
                ("missing ELF", [action], archive, True),
                ("archive name only a substring", [action],
                 archive + "\n" + elf + ".backup", True),
            )
            for label, actions, edges, enabled in failures:
                with self.subTest(case=label):
                    with self.assertRaises(SystemExit):
                        check_usb_ep0_linkage(actions, edges, build, enabled)

    def test_actual_generated_callbacks_queue_and_log_in_task_before_lifecycle(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            selected = self.selected(work)
            actions = re.search(r"typedef enum \{\s*DEV_ACTION_EPn_HALT_FLUSH.*?\} dev_action_t;",
                                selected, re.DOTALL)
            self.assertIsNotNone(actions)
            definitions = r"(DEV_ACTION_\w+)\s*=\s*\(1\s*<<\s*(\d+)\)"
            original_bits = re.findall(definitions, SDK_SOURCE.read_text())
            selected_bits = re.findall(definitions, actions.group())
            self.assertEqual(selected_bits, original_bits + [
                ("DEV_ACTION_EP0_LOG_ERROR", "7"), ("DEV_ACTION_EP0_LOG_STALL", "8")])
            harness = HARNESS.replace("__ACTIONS__", actions.group())
            for marker, name in (("__SET_ACTIONS__", "_dev_set_actions"),
                                 ("__EP0_CALLBACK__", "ep0_pipe_callback"),
                                 ("__PROCESS__", "usbh_process")):
                harness = harness.replace(marker, function(selected, name))
            callback = function(selected, "ep0_pipe_callback")
            self.assertNotIn("ESP_EARLY_LOG", callback)
            self.assertNotIn("ESP_LOG", callback)
            source, executable = work / "actions.c", work / "actions"
            source.write_text(harness)
            compile_result = subprocess.run(
                ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-parameter",
                 "-fsanitize=address,undefined", str(source), "-o", str(executable)],
                capture_output=True, text=True)
            self.assertEqual(compile_result.returncode, 0, compile_result.stdout + compile_result.stderr)
            environment = dict(os.environ)
            previous = environment.get("ASAN_OPTIONS", "")
            environment["ASAN_OPTIONS"] = previous + (":" if previous else "") + "detect_leaks=0"
            result = subprocess.run([str(executable)], capture_output=True, text=True,
                                    env=environment)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("18 callback/action/lifecycle cases passed", result.stdout)
            # Restore only the real original callback: this must expose the
            # regression even with the selected queue/process bodies retained.
            original_callback = function(SDK_SOURCE.read_text(), "ep0_pipe_callback")
            source.write_text(harness.replace(callback, original_callback, 1))
            compile_result = subprocess.run(
                ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-parameter",
                 str(source), "-o", str(executable)], capture_output=True, text=True)
            self.assertEqual(compile_result.returncode, 0, compile_result.stdout + compile_result.stderr)
            result = subprocess.run([str(executable)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("EP0 callback logged before task processing", result.stderr)


if __name__ == "__main__":
    unittest.main()
