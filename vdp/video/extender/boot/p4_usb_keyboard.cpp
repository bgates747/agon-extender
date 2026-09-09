// PORT-015 W2: standalone native USB acquisition, not the EDP release image.
// Dedicated P4 HS PHY (EXT2 USB-P/USB-N); USB-C Serial/JTAG remains the console.
// No Agon transport or GPIO setup, renderer, networking or EMOS source admission.
// HID 1.2.1 is pinned for its close/disconnect fixes; see the target allowlist.
#include <Arduino.h>
#include <atomic>
#include <cstdio>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include <freertos/task.h>
#include <esp_intr_alloc.h>
#include <usb/usb_host.h>
#include <usb/hid_host.h>
#include "../input/usb_boot_keyboard.hpp"
#include "../../../.pio/build-identities/p4-usb-keyboard/build_identity.hpp"

namespace {
using Decoder=agon::extender::input::UsbBootKeyboard;
enum class Kind { connected, report, disconnected };
struct Event {
  Kind kind{};
  hid_host_device_handle_t handle{};
  size_t size{};
  unsigned generation{};
  uint8_t report[64]{};
  uint16_t vid{},pid{};
  uint8_t address{},interface{};
};
QueueHandle_t events{};
std::atomic<hid_host_device_handle_t> active{};
std::atomic<bool> detached{};
std::atomic<unsigned> faults{};
std::atomic<unsigned> report_generation{};
constexpr unsigned overflow=1,transfer_error=2,link_error=4;
Decoder keyboard;
bool running{};
uint32_t key_events{},reports{},connections{};
uint32_t last_status{};

void inputFault(unsigned fault) {
  // Reports copied before a loss can never rearm the decoder afterwards.
  report_generation.fetch_add(1);
  faults.fetch_or(fault);
}

void key(const Decoder::Key &event) {
  ++key_events;
  const auto &p=event.processed;
  printf("USB KEY %s usage=%02x modifiers=%02x ascii=%u vk=%u mapped=%s\n",
         p.down?"DOWN":"UP",event.usage,p.modifiers,p.ascii,p.virtual_key,
         event.mapped?"yes":"no");
}

void interfaceEvent(hid_host_device_handle_t handle,hid_host_interface_event_t kind,void *) {
  Event event{}; event.handle=handle;
  if (kind==HID_HOST_INTERFACE_EVENT_DISCONNECTED) {
    // HID 1.2.1 + IDF 5.5.5 may log EP command ESP_ERR_INVALID_STATE
    // before this callback: upstream disconnect cleanup clears an endpoint
    // after its port is disabled. Our second close only deletes the retained
    // interface. Keep other errors visible; do not suppress the USB HOST tag.
    // Source trace/evidence: hardware/designs/light2-harness-r03/tests/
    // usb-keyboard-unplug-review.md. Recheck when either dependency changes.
    detached.store(true);
    event.kind=Kind::disconnected;
    // Only one interface is claimed. Reports reserve two queue entries for
    // CONNECTED/DISCONNECTED, so unplug cannot be lost behind a report flood.
    if (xQueueSend(events,&event,0)!=pdTRUE) faults.fetch_or(link_error);
    // The application closes the retained WAIT_USER_DELETION interface. Do
    // not retain or dereference the parent's USB device after this callback.
  } else if (kind==HID_HOST_INTERFACE_EVENT_TRANSFER_ERROR) {
    inputFault(transfer_error);
  } else if (kind==HID_HOST_INTERFACE_EVENT_INPUT_REPORT) {
    event.kind=Kind::report;
    event.generation=report_generation.load();
    if (hid_host_device_get_raw_input_report_data(handle,event.report,sizeof(event.report),&event.size)!=ESP_OK)
      inputFault(transfer_error);
    else if (uxQueueSpacesAvailable(events)<=2 || xQueueSend(events,&event,0)!=pdTRUE)
      inputFault(overflow);
  }
}

void connected(hid_host_device_handle_t handle,hid_host_driver_event_t kind,void *) {
  if (kind!=HID_HOST_DRIVER_EVENT_CONNECTED) return;
  hid_host_dev_params_t params{};
  if (hid_host_device_get_params(handle,&params)!=ESP_OK) return;
  if (params.sub_class!=HID_SUBCLASS_BOOT_INTERFACE || params.proto!=HID_PROTOCOL_KEYBOARD || active.load()) {
    printf("USB IGNORE address=%u interface=%u subclass=%u protocol=%u\n",
           params.addr,params.iface_num,params.sub_class,params.proto);
    return;
  }
  // Claim in the notification callback so a queued connection retains a valid
  // interface until its corresponding disconnect is consumed. Control requests
  // run in loop(), while the HID task continues servicing USB completions.
  hid_host_device_config_t config{};
  config.callback=interfaceEvent;
  const auto result=hid_host_device_open(handle,&config);
  if (result!=ESP_OK) { printf("USB OPEN FAIL %s\n",esp_err_to_name(result)); return; }
  active.store(handle); detached.store(false);
  hid_host_dev_info_t info{};
  hid_host_get_device_info(handle,&info);
  Event event{}; event.kind=Kind::connected; event.handle=handle;
  event.vid=info.VID; event.pid=info.PID;
  event.address=params.addr; event.interface=params.iface_num;
  if (xQueueSend(events,&event,0)!=pdTRUE) faults.fetch_or(link_error);
}

void hostEvents(void *) {
  for (;;) {
    uint32_t flags{};
    const auto result=usb_host_lib_handle_events(portMAX_DELAY,&flags);
    if (result!=ESP_OK) {
      faults.fetch_or(link_error);
      vTaskDelay(pdMS_TO_TICKS(10));
    }
  }
}

bool check(esp_err_t result,const char *operation) {
  if (result==ESP_OK) return true;
  printf("USB FAIL %s: %s\n",operation,esp_err_to_name(result)); return false;
}
}

void setup() {
  printf("\nUSB KEYBOARD %s build=%s status=%s\n",AGON_EXTENDER_SOURCE_IDENTITY,
         AGON_EXTENDER_BUILD_ID,AGON_EXTENDER_ARTIFACT_STATUS);
  // Allocate before installing drivers: a keyboard may already be attached.
  events=xQueueCreate(32,sizeof(Event));
  if (!events) { printf("USB FAIL event allocation\n"); return; }
  usb_host_config_t host{};
  host.intr_flags=ESP_INTR_FLAG_LEVEL1;
  host.peripheral_map=0; // P4 dedicated HS PHY, not the GPIO26/27 FS port.
  if (!check(usb_host_install(&host),"host install")) return;
  if (xTaskCreate(hostEvents,"usb-library",4096,nullptr,6,nullptr)!=pdPASS) {
    printf("USB FAIL library task allocation\n"); return;
  }
  hid_host_driver_config_t driver{};
  driver.create_background_task=true;
  driver.task_priority=5; driver.stack_size=4096;
  driver.core_id=tskNO_AFFINITY; driver.callback=connected;
  if (!check(hid_host_install(&driver),"HID install")) return;
  running=true;
  printf("USB HOST READY: attach one boot keyboard; acquisition only\n");
}

void loop() {
  if (!running) { delay(100); return; }
  const auto fault=faults.exchange(0);
  if (fault) {
    keyboard.lostReport(key);
    printf("USB INPUT FAULT flags=%u: held keys released; release all physical keys\n",fault);
    if (fault&link_error) {
      printf("USB HOST FAULT: reset P4 before continuing\n"); running=false; return;
    }
  }
  if (uint32_t(millis()-last_status)>=5000) {
    last_status=millis();
    printf("USB STATUS attached=%u reports=%lu key_events=%lu\n",
           active.load()!=nullptr && !detached.load(),static_cast<unsigned long>(reports),
           static_cast<unsigned long>(key_events));
  }
  Event event{};
  if (xQueueReceive(events,&event,pdMS_TO_TICKS(20))!=pdTRUE) return;
  if (event.kind==Kind::connected) {
    if (detached.load()) return; // disconnect notice owns subsequent cleanup
    ++connections;
    printf("USB CONNECTED #%lu vid=%04x pid=%04x address=%u interface=%u\n",
           static_cast<unsigned long>(connections),event.vid,event.pid,event.address,event.interface);
    auto result=hid_class_request_set_protocol(event.handle,HID_REPORT_PROTOCOL_BOOT);
    if (result==ESP_OK && !detached.load()) result=hid_class_request_set_idle(event.handle,0,0);
    if (result==ESP_OK && !detached.load()) result=hid_host_device_start(event.handle);
    if (detached.load()) return;
    if (!check(result,"boot protocol/start")) {
      // Close also generates DISCONNECTED; its queue event owns final deletion.
      check(hid_host_device_close(event.handle),"close failed admission"); return;
    }
    printf("USB KEYBOARD READY: press/release keys; US subset, no repeat or LEDs\n");
  } else if (event.kind==Kind::disconnected) {
    keyboard.disconnect(key);
    check(hid_host_device_close(event.handle),"disconnect close");
    active.store(nullptr);
    printf("USB DISCONNECTED: held keys released; waiting for keyboard\n");
  } else if (!detached.load() && event.generation==report_generation.load()) {
    ++reports;
    const auto result=keyboard.report(event.report,event.size,key);
    if (result==Decoder::Result::invalid) printf("USB REPORT INVALID size=%u: release all keys\n",unsigned(event.size));
    if (result==Decoder::Result::rearmed) printf("USB INPUT REARMED\n");
  }
}
