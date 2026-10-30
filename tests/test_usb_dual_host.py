"""Execute the generated host lifecycle; mock only PHY/HCD/RTOS boundaries."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT / "agents/build001/native-tools/esp-idf/components/usb/usb_host.c"
RECIPE = ROOT / "vdp/native/usb_dual_host.cmake"
sys.path.insert(0, str(ROOT / "scripts"))
from validate_p4_build import check_usb_dual_derivative, check_usb_dual_linkage
from test_usb_ep0_task_logging import function


def generate(source, output):
    return subprocess.run(["cmake", f"-DUSB_DUAL_SOURCE={source}",
                           f"-DUSB_DUAL_OUTPUT={output}", "-P", str(RECIPE)],
                          capture_output=True, text=True)


HARNESS = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/queue.h>
typedef int esp_err_t;
typedef void *SemaphoreHandle_t;
typedef void *usb_phy_handle_t;
enum { ESP_OK=0, ESP_ERR_INVALID_ARG=1, ESP_ERR_INVALID_STATE=2,
       ESP_ERR_NO_MEM=3, INJECTED=4, MALLOC_CAP_DEFAULT=0,
       USB_PHY_CTRL_OTG=0, USB_PHY_TARGET_UTMI=1, USB_PHY_TARGET_INT=2,
       USB_OTG_MODE_HOST=1, USB_PHY_SPEED_UNDEFINED=0, USB_PHY_INST_UTMI_0=1 };
#define SOC_USB_OTG_PERIPH_NUM 2
#define SOC_USB_OTG_SUPPORTED 1
#define ENABLE_ENUM_FILTER_CALLBACK 0
#define BIT0 1u
#define BIT1 2u
#define BIT(n) (1u<<(n))
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_ERROR_CHECK(call) assert((call)==ESP_OK)
static bool locked;
#define HOST_ENTER_CRITICAL() do { assert(!locked);locked=true; } while(0)
#define HOST_EXIT_CRITICAL() do { assert(locked);locked=false; } while(0)
#define HOST_CHECK(ok,error) do { if(!(ok)) return(error); } while(0)
#define HOST_CHECK_FROM_CRIT(ok,error) do { if(!(ok)){HOST_EXIT_CRITICAL();return(error);} } while(0)
typedef struct { unsigned rx_fifo_lines,nptx_fifo_lines,ptx_fifo_lines; } hcd_fifo_settings_t;
typedef struct { bool skip_phy_setup; int intr_flags; unsigned peripheral_map;
                 hcd_fifo_settings_t fifo_settings_custom; bool root_port_unpowered; } usb_host_config_t;
typedef struct { int controller,target,otg_mode,otg_speed;void *ext_io_conf,*otg_io_conf; } usb_phy_config_t;
typedef struct { int intr_flags;unsigned peripheral_map;hcd_fifo_settings_t *fifo_config; } hcd_config_t;
typedef struct { void(*proc_req_cb)(void);void *proc_req_cb_arg;
                 void(*event_cb)(void);void *event_cb_arg; } usbh_config_t;
typedef struct { void(*proc_req_cb)(void);void *proc_req_cb_arg;
                 void(*enum_event_cb)(void);void *enum_event_cb_arg; } enum_config_t;
typedef struct { unsigned port_map;void(*proc_req_cb)(void);void *proc_req_cb_arg;
                 void(*event_cb)(void);void *event_cb_arg; } hub_config_t;
typedef struct {
 struct {unsigned process_pending_flags,lib_event_flags;struct {unsigned val;} flags;} dynamic;
 struct {TAILQ_HEAD(clients,client_s) client_tailq;} mux_protected;
 struct {SemaphoreHandle_t event_sem,mux_lock;usb_phy_handle_t phy_handles[2];void *enum_client,*hub_client;} constant;
} host_lib_t;
static host_lib_t *p_host_lib_obj;
static const struct {struct {int supported_phys;} controllers[2];} usb_dwc_info={{{1},{0}}};
static int failure,alloc_failure,allocations,semaphores,sem_calls;
static int made,deleted,targets[2],hcd_calls,hub_calls;
static bool phys[2],hcd,usbh,enumerator,hub,fifo_default;
static unsigned hcd_map,hub_map;
static hcd_fifo_settings_t observed_fifo;
static void proc_req_callback(void){} static void usbh_event_callback(void){}
static void enum_event_callback(void){} static void hub_event_callback(void){}
static void *heap_caps_calloc(size_t n,size_t size,int cap){
 (void)cap;if(alloc_failure==1)return NULL;
 void*p=calloc(n,size);if(p)++allocations;return p;
}
static void heap_caps_free(void*p){if(p){--allocations;free(p);}}
static SemaphoreHandle_t semaphore(void){
 ++sem_calls;if(alloc_failure==sem_calls+1)return NULL;
 ++semaphores;return malloc(1);
}
static SemaphoreHandle_t xSemaphoreCreateBinary(void){return semaphore();}
static SemaphoreHandle_t xSemaphoreCreateMutex(void){return semaphore();}
static void vSemaphoreDelete(SemaphoreHandle_t p){assert(p);--semaphores;free(p);}
static esp_err_t usb_new_phy(const usb_phy_config_t*c,usb_phy_handle_t*out){
 assert(c->controller==USB_PHY_CTRL_OTG&&c->otg_mode==USB_OTG_MODE_HOST);
 int i=c->target==USB_PHY_TARGET_UTMI?0:1;assert(!phys[i]);targets[made++]=c->target;
 if(failure==i+1)return INJECTED;
 phys[i]=true;*out=(void*)(uintptr_t)(i+1);return ESP_OK;
}
static esp_err_t usb_del_phy(usb_phy_handle_t p){
 int i=(int)(uintptr_t)p-1;assert(i>=0&&i<2&&phys[i]);phys[i]=false;++deleted;return ESP_OK;
}
static esp_err_t hcd_install(const hcd_config_t*c){
 ++hcd_calls;hcd_map=c->peripheral_map;fifo_default=c->fifo_config==NULL;
 if(c->fifo_config)observed_fifo=*c->fifo_config;
 if(failure==3)return INJECTED;
 assert(!hcd);hcd=true;return ESP_OK;
}
static esp_err_t hcd_uninstall(void){assert(hcd);hcd=false;return ESP_OK;}
static esp_err_t usbh_install(const usbh_config_t*c){(void)c;if(failure==4)return INJECTED;usbh=true;return ESP_OK;}
static esp_err_t usbh_uninstall(void){assert(usbh);usbh=false;return ESP_OK;}
static esp_err_t enum_install(const enum_config_t*c,void**p){(void)c;(void)p;if(failure==5)return INJECTED;enumerator=true;return ESP_OK;}
static esp_err_t enum_uninstall(void){assert(enumerator);enumerator=false;return ESP_OK;}
static esp_err_t hub_install(const hub_config_t*c,void**p){
 (void)p;++hub_calls;hub_map=c->port_map;if(failure==6)return INJECTED;hub=true;return ESP_OK;
}
static esp_err_t hub_uninstall(void){assert(hub);hub=false;return ESP_OK;}
static esp_err_t hub_root_start(void){assert(hub);return ESP_OK;}
static esp_err_t hub_root_stop(void){assert(hub);return ESP_OK;}
__INSTALL__
__UNINSTALL__
static void clean(void){
 assert(!locked&&!p_host_lib_obj&&!phys[0]&&!phys[1]);
 assert(!hcd&&!usbh&&!enumerator&&!hub&&allocations==0&&semaphores==0);
}
static void reset(void){
 clean();failure=alloc_failure=sem_calls=made=deleted=hcd_calls=hub_calls=0;
 hcd_map=hub_map=0;memset(targets,0,sizeof(targets));
}
int main(void){
 unsigned cases=0;
 for(unsigned map=0;map<4;++map){
  reset();usb_host_config_t c={.peripheral_map=map,.intr_flags=1};
  assert(usb_host_install(&c)==ESP_OK);unsigned actual=map?map:1;
  assert(hcd_map==actual&&hub_map==actual&&hcd_calls==1&&hub_calls==1);
  assert(phys[0]==!!(actual&1)&&phys[1]==!!(actual&2));
  assert(made==(actual==3?2:1));
  if(actual==3)assert(targets[0]==USB_PHY_TARGET_UTMI&&targets[1]==USB_PHY_TARGET_INT);
  assert(usb_host_install(&c)==ESP_ERR_INVALID_STATE);
  assert(usb_host_uninstall()==ESP_OK);assert(deleted==made);clean();++cases;
 }
 for(int stage=1;stage<=6;++stage){
  reset();failure=stage;usb_host_config_t c={.peripheral_map=3};
  assert(usb_host_install(&c)==INJECTED);clean();
  assert(deleted==(stage==1?0:stage==2?1:2));++cases;
 }
 for(int allocation=1;allocation<=3;++allocation){
  reset();alloc_failure=allocation;usb_host_config_t c={.peripheral_map=3};
  assert(usb_host_install(&c)==ESP_ERR_NO_MEM);clean();assert(made==0);++cases;
 }
 reset();usb_host_config_t c={.peripheral_map=4};
 assert(usb_host_install(&c)==ESP_ERR_INVALID_ARG);clean();assert(made==0&&sem_calls==0);++cases;
 reset();c=(usb_host_config_t){.peripheral_map=3,.skip_phy_setup=true};
 assert(usb_host_install(&c)==ESP_OK);assert(made==0&&hcd_map==3);
 assert(usb_host_uninstall()==ESP_OK);clean();assert(deleted==0);++cases;
 for(unsigned map=1;map<=3;map+=2){
  reset();c=(usb_host_config_t){.peripheral_map=map,.fifo_settings_custom={4,5,6}};
  assert(usb_host_install(&c)==ESP_OK);assert(fifo_default==(map==3));
  if(map==1)assert(observed_fifo.rx_fifo_lines==4&&observed_fifo.nptx_fifo_lines==5&&observed_fifo.ptx_fifo_lines==6);
  assert(usb_host_uninstall()==ESP_OK);clean();++cases;
 }
 printf("PASS %u actual USB host lifecycle cases: both PHYs, partial failures, cleanup, map/FIFO and ownership\n",cases);
 return 0;
}
'''


class DualHost(unittest.TestCase):
    def test_actual_lifecycle(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            source = work / "usb_host.c"
            result = generate(SDK, source)
            self.assertEqual(result.returncode, 0, result.stderr)
            text = source.read_text()
            harness = HARNESS.replace("__INSTALL__", function(text, "usb_host_install"))
            harness = harness.replace("__UNINSTALL__", function(text, "usb_host_uninstall"))
            (work / "lifecycle.c").write_text(harness)
            subprocess.run(["cc", "-std=c17", "-Wall", "-Wextra", "-Werror",
                            "-fsanitize=address,undefined", str(work / "lifecycle.c"),
                            "-o", str(work / "lifecycle")], check=True)
            subprocess.run([str(work / "lifecycle")], check=True)

    def test_dependency_drift_and_unused_derivative_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            source, output = work / "source.c", work / "derivative.c"
            source.write_bytes(SDK.read_bytes())
            self.assertEqual(generate(source, output).returncode, 0)
            check_usb_dual_derivative(source, output)
            output.write_bytes(output.read_bytes() + b"\n// drift\n")
            with self.assertRaisesRegex(SystemExit, "complete bounded dual-host"):
                check_usb_dual_derivative(source, output)
            output.unlink()
            source.write_bytes(source.read_bytes() + b"\n// changed SDK\n")
            self.assertNotEqual(generate(source, output).returncode, 0)
            self.assertFalse(output.exists())
            with self.assertRaisesRegex(SystemExit, "exactly one USB host"):
                check_usb_dual_linkage([], "", work, True)

    def test_invalid_build_combinations_leave_no_output(self):
        for extra in (["--board", "p4-devkit", "--usb-fsls-only"],
                      ["--board", "p4-pc"],
                      ["--board", "p4-pc", "--usb-fsls-only", "--usb-direct-fs"]):
            with self.subTest(extra=extra), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "absent"
                result = subprocess.run([sys.executable, str(ROOT / "scripts/build_p4.py"),
                                         "--profile", "p4-console", "--usb-dual-host",
                                         *extra, "--output", str(output)], capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
