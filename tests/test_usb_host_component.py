"""Complete component selection and actual two-root hub lifecycle regression."""
from pathlib import Path
import hashlib
import re
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from p4_usb_host import prepare,verify,HCD_SHA,USBH_SHA,check_linkage
from test_usb_ep0_task_logging import function

HARNESS=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/queue.h>
#define ENABLE_USB_HUBS 0
#define HCD_NUM_PORTS 2
#define BIT(n) (1u<<(n))
#define MALLOC_CAP_DEFAULT 0
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGD(...) ((void)0)
#define ESP_ERROR_CHECK(x) assert((x)==ESP_OK)
#define HUB_DRIVER_ENTER_CRITICAL() do{assert(!locked);locked=true;}while(0)
#define HUB_DRIVER_EXIT_CRITICAL() do{assert(locked);locked=false;}while(0)
#define HUB_DRIVER_CHECK(c,e) do{if(!(c))return(e);}while(0)
#define HUB_DRIVER_CHECK_FROM_CRIT(c,e) do{if(!(c)){HUB_DRIVER_EXIT_CRITICAL();return(e);}}while(0)
typedef int esp_err_t;
enum{ESP_OK=0,ESP_FAIL=1,ESP_ERR_INVALID_ARG=2,ESP_ERR_INVALID_STATE=3,ESP_ERR_NO_MEM=4,INJECTED=5};
enum{ROOT_PORT_STATE_NOT_POWERED=0,ROOT_PORT_STATE_POWERED=1,HCD_PORT_CMD_POWER_ON=1,HCD_PORT_CMD_POWER_OFF=2};
typedef struct{int index;bool powered;}port_t;
typedef port_t*hcd_port_handle_t;
typedef struct{hcd_port_handle_t hdl;int index;}constant_t;
typedef struct{constant_t constant;struct{int state;}dynamic;}root_hub_port_t;
typedef struct node{TAILQ_ENTRY(node)entry;}node_t;
typedef struct{
 struct{TAILQ_HEAD(nodes,node)dev_nodes_tailq;}single_thread;
 root_hub_port_t root_hub_ports[2];
 struct{void(*proc_req_cb)(void);void*proc_req_cb_arg;void(*event_cb)(void);void*event_cb_arg;}constant;
}hub_driver_t;
typedef struct{void(*callback)(void);void*callback_arg,*context;int intr_flags;void*fifo_config;bool fsls_only;}hcd_port_config_t;
typedef struct{unsigned port_map;int intr_flags;void*fifo_config;bool fsls_only;void(*proc_req_cb)(void);void*proc_req_cb_arg;void(*event_cb)(void);void*event_cb_arg;}hub_config_t;
static hub_driver_t*p_hub_driver_obj;
static bool locked,allocated,active[2],allocation_failure;
static int failure=-1,power_failure=-1,created,deleted,powered,off;
static void root_port_callback(void){}
static void*heap_caps_calloc(size_t n,size_t size,int cap){(void)cap;if(allocation_failure)return NULL;assert(!allocated);allocated=true;return calloc(n,size);}
static void heap_caps_free(void*p){assert(allocated);allocated=false;free(p);}
static esp_err_t hcd_port_init(int index,const hcd_port_config_t*c,hcd_port_handle_t*out){
 assert(index>=0&&index<2&&!active[index]);
 assert(c->context==c->callback_arg&&c->callback==root_port_callback&&c->intr_flags==7&&!c->fsls_only);
 if(index==failure)return INJECTED;
 port_t*p=calloc(1,sizeof(*p));p->index=index;*out=p;active[index]=true;++created;return ESP_OK;
}
static esp_err_t hcd_port_deinit(hcd_port_handle_t p){assert(p&&!p->powered&&active[p->index]);active[p->index]=false;++deleted;free(p);return ESP_OK;}
static esp_err_t hcd_port_command(hcd_port_handle_t p,int command){
 assert(p&&active[p->index]);
 if(command==HCD_PORT_CMD_POWER_ON){if(p->index==power_failure)return INJECTED;assert(!p->powered);p->powered=true;++powered;}
 else{assert(command==HCD_PORT_CMD_POWER_OFF&&p->powered);p->powered=false;++off;}
 return ESP_OK;
}
esp_err_t hub_root_stop(void);
__FUNCTIONS__
static void clean(void){assert(!locked&&!allocated&&!p_hub_driver_obj&&!active[0]&&!active[1]);}
int main(void){
 unsigned cases=0;
 for(unsigned map=1;map<4;++map){
  clean();created=deleted=powered=off=0;hub_config_t c={.port_map=map,.intr_flags=7};void*client=(void*)1;
  assert(hub_install(&c,&client)==ESP_OK&&client==NULL);
  assert(active[0]==!!(map&1)&&active[1]==!!(map&2));
  assert(hub_install(&c,&client)==ESP_ERR_INVALID_STATE);
  assert(hub_root_start()==ESP_OK&&powered==(map==3?2:1));
  assert(hub_uninstall()==ESP_ERR_INVALID_STATE);
  assert(hub_root_stop()==ESP_OK&&off==powered);
  assert(hub_root_stop()==ESP_OK&&off==powered);
  assert(hub_uninstall()==ESP_OK&&deleted==created);clean();++cases;
 }
 for(int f=0;f<2;++f){
  failure=f;created=deleted=0;hub_config_t c={.port_map=3,.intr_flags=7};void*client;
  assert(hub_install(&c,&client)==INJECTED);assert(deleted==created);clean();++cases;
 }failure=-1;
 for(int f=0;f<2;++f){
  power_failure=f;created=deleted=powered=off=0;hub_config_t c={.port_map=3,.intr_flags=7};void*client;
  assert(hub_install(&c,&client)==ESP_OK);assert(hub_root_start()==INJECTED);
  assert(powered==off);assert(hub_uninstall()==ESP_OK);clean();++cases;
 }power_failure=-1;
 allocation_failure=true;hub_config_t c={.port_map=3,.intr_flags=7};void*client;
 assert(hub_install(&c,&client)==ESP_ERR_NO_MEM);clean();++cases;
 allocation_failure=false;c.port_map=0;assert(hub_install(&c,&client)==ESP_ERR_INVALID_ARG);clean();++cases;
 printf("PASS %u actual dual-root hub cases: both ports powered, cleanup and failure rollback\n",cases);
}
'''

class CompleteHost(unittest.TestCase):
 def test_actual_dual_root_hub(self):
  with tempfile.TemporaryDirectory() as p:
   project=Path(p)/'project';project.mkdir();prepare(project)
   source=(project/'components/usb/src/hub.c').read_text()
   functions='\n'.join(function(source,n) for n in ('hub_install','hub_uninstall','hub_root_start','hub_root_stop'))
   c=Path(p)/'hub.c';c.write_text(HARNESS.replace('__FUNCTIONS__',functions))
   subprocess.run(['cc','-std=c17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(c),'-o',str(Path(p)/'hub')],check=True)
   subprocess.run([str(Path(p)/'hub')],check=True)
 def test_derivatives_and_source_drift(self):
  with tempfile.TemporaryDirectory() as p:
   project=Path(p)/'project';project.mkdir();prepare(project)
   def generate():
    return subprocess.run(['cmake',f'-DUSB16_DIR={project}/components/usb',f'-DUSB16_OUTPUT={p}/out','-P',str(ROOT/'vdp/native/usb_host_component.cmake')],capture_output=True,text=True)
   result=generate();self.assertEqual(result.returncode,0,result.stderr)
   for n,pin in [('hcd_dwc.c',HCD_SHA),('usbh.c',USBH_SHA)]:self.assertEqual(hashlib.sha256((Path(p)/'out'/n).read_bytes()).hexdigest(),pin)
   source=project/'components/usb/src/hcd_dwc.c';source.write_text(source.read_text()+'\n')
   self.assertNotEqual(generate().returncode,0)
   with self.assertRaises(SystemExit):verify(project)
 def test_component_ep0_actions_do_not_collide(self):
  from test_usb_ep0_task_logging import HARNESS as LOG_HARNESS
  with tempfile.TemporaryDirectory() as p:
   project=Path(p)/'project';project.mkdir();prepare(project)
   subprocess.run(['cmake',f'-DUSB16_DIR={project}/components/usb',f'-DUSB16_OUTPUT={p}/out','-P',str(ROOT/'vdp/native/usb_host_component.cmake')],check=True)
   selected=(Path(p)/'out/usbh.c').read_text()
   actions=re.search(r'typedef enum \{.*?\} dev_action_t;',selected,re.S).group()
   bits=re.findall(r'(DEV_ACTION_\w+)\s*=\s*\(1 << (\d+)\)',actions)
   self.assertEqual(len({value for _,value in bits}),len(bits))
   harness=LOG_HARNESS.replace('__ACTIONS__',actions)
   for marker,name in [('__SET_ACTIONS__','_dev_set_actions'),('__EP0_CALLBACK__','ep0_pipe_callback'),('__PROCESS__','usbh_process')]:harness=harness.replace(marker,function(selected,name))
   stubs=''.join(f'static void {name}(device_t*d){{(void)d;assert(0);}}\n' for name in ['handle_prop_removed_event','handle_epn_clear','handle_prop_suspend_event','handle_prop_resume_event'])
   stubs+='static void handle_prop_all_idle_event(void){assert(0); }\n'
   harness=harness.replace('esp_err_t usbh_process(void)',stubs+'esp_err_t usbh_process(void)',1)
   source=Path(p)/'actions.c';source.write_text(harness)
   subprocess.run(['cc','-std=c17','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-fsanitize=address,undefined',str(source),'-o',str(Path(p)/'actions')],check=True)
   subprocess.run([str(Path(p)/'actions')],check=True)
 def test_old_single_root_component_refused(self):
  with tempfile.TemporaryDirectory() as p:
   project=Path(p)/'project';project.mkdir();prepare(project)
   source=project/'components/usb/src/hub.c'
   source.write_bytes((ROOT/'agents/build001/native-tools/esp-idf/components/usb/hub.c').read_bytes())
   with self.assertRaises(SystemExit):verify(project)
if __name__=='__main__':unittest.main()
