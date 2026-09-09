// Native USB boot-keyboard acquisition. USB tasks only retain/copy interface
// events; one application owner performs control requests and consumes reports.
// Derived from the frozen W2 acquisition fixture for the USB-to-EMOS
// composition. Leave that qualified standalone fixture's executable unchanged.
#pragma once
#include <atomic>
#include <cstdio>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include <freertos/task.h>
#include <esp_intr_alloc.h>
#include <usb/usb_host.h>
#include <usb/hid_host.h>

namespace agon::extender::input::usbhost {
enum class Kind { connected, report, disconnected };
struct Event {
  Kind kind{}; hid_host_device_handle_t handle{};
  size_t size{}; unsigned generation{}; uint8_t report[64]{};
  uint16_t vid{},pid{}; uint8_t address{},interface{};
};
inline QueueHandle_t events{};
inline std::atomic<hid_host_device_handle_t> active{};
inline std::atomic<bool> detached{};
inline std::atomic<unsigned> faults{}, generation{};
inline bool running{};
inline unsigned connections{};
constexpr unsigned overflow=1,transfer_error=2,link_error=4;
inline void fault(unsigned value) { generation.fetch_add(1); faults.fetch_or(value); }
inline bool check(esp_err_t result,const char *operation) {
  if (result==ESP_OK) return true;
  printf("USB FAIL %s: %s\n",operation,esp_err_to_name(result)); return false;
}
inline void interfaceEvent(hid_host_device_handle_t handle,hid_host_interface_event_t kind,void *) {
  Event event{}; event.handle=handle;
  if (kind==HID_HOST_INTERFACE_EVENT_DISCONNECTED) {
    // HID 1.2.1 / IDF 5.5.5 can log endpoint-clear INVALID_STATE before this
    // callback after physical removal. See usb-keyboard-unplug-review.md beside
    // the r03 hardware tests. Keep other errors visible; recheck on upgrades.
    detached.store(true); event.kind=Kind::disconnected;
    if (xQueueSend(events,&event,0)!=pdTRUE) fault(link_error);
  } else if (kind==HID_HOST_INTERFACE_EVENT_TRANSFER_ERROR) fault(transfer_error);
  else if (kind==HID_HOST_INTERFACE_EVENT_INPUT_REPORT) {
    event.kind=Kind::report; event.generation=generation.load();
    if (hid_host_device_get_raw_input_report_data(handle,event.report,sizeof(event.report),&event.size)!=ESP_OK)
      fault(transfer_error);
    else if (uxQueueSpacesAvailable(events)<=2 || xQueueSend(events,&event,0)!=pdTRUE) fault(overflow);
  }
}
inline void connected(hid_host_device_handle_t handle,hid_host_driver_event_t kind,void *) {
  if (kind!=HID_HOST_DRIVER_EVENT_CONNECTED) return;
  hid_host_dev_params_t params{};
  if (hid_host_device_get_params(handle,&params)!=ESP_OK) return;
  if (params.sub_class!=HID_SUBCLASS_BOOT_INTERFACE || params.proto!=HID_PROTOCOL_KEYBOARD || active.load()) {
    printf("USB IGNORE address=%u interface=%u subclass=%u protocol=%u\n",params.addr,params.iface_num,params.sub_class,params.proto); return;
  }
  hid_host_device_config_t config{}; config.callback=interfaceEvent;
  if (!check(hid_host_device_open(handle,&config),"open")) return;
  active.store(handle); detached.store(false);
  hid_host_dev_info_t info{}; hid_host_get_device_info(handle,&info);
  Event event{}; event.kind=Kind::connected; event.handle=handle;
  event.vid=info.VID; event.pid=info.PID; event.address=params.addr; event.interface=params.iface_num;
  if (xQueueSend(events,&event,0)!=pdTRUE) fault(link_error);
}
inline void hostEvents(void *) {
  for (;;) {
    uint32_t flags{};
    if (usb_host_lib_handle_events(portMAX_DELAY,&flags)!=ESP_OK) {
      fault(link_error); vTaskDelay(pdMS_TO_TICKS(10));
    }
  }
}
inline bool begin() {
  events=xQueueCreate(32,sizeof(Event));
  if (!events) return false;
  usb_host_config_t host{}; host.intr_flags=ESP_INTR_FLAG_LEVEL1;
  host.peripheral_map=0; // Dedicated HS USB-P/USB-N, EXT2.19/20.
  if (!check(usb_host_install(&host),"host install")) return false;
  if (xTaskCreate(hostEvents,"usb-library",4096,nullptr,6,nullptr)!=pdPASS) return false;
  hid_host_driver_config_t driver{}; driver.create_background_task=true;
  driver.task_priority=5; driver.stack_size=4096; driver.core_id=tskNO_AFFINITY; driver.callback=connected;
  running=check(hid_host_install(&driver),"HID install");
  if (running) printf("USB HOST READY: attach one boot keyboard\n");
  return running;
}
inline bool attached() { return active.load()!=nullptr && !detached.load(); }
// Callbacks execute only on the application owner. Loss callbacks must clear
// owned key state; the USB driver itself does not publish MOS keyboard packets.
template<class Report,class Connection,class Lost>
void pump(Report report,Connection connection,Lost lost) {
  if (!running) return;
  const auto bits=faults.exchange(0);
  if (bits) {
    lost(); printf("USB INPUT FAULT flags=%u\n",bits);
    if (bits&link_error) { running=false; printf("USB HOST FAULT: reset P4\n"); return; }
  }
  Event event{};
  if (xQueueReceive(events,&event,0)!=pdTRUE) return;
  if (event.kind==Kind::connected) {
    if (detached.load()) return;
    printf("USB CONNECTED #%u vid=%04x pid=%04x address=%u interface=%u\n",++connections,event.vid,event.pid,event.address,event.interface);
    auto result=hid_class_request_set_protocol(event.handle,HID_REPORT_PROTOCOL_BOOT);
    if (result==ESP_OK && !detached.load()) result=hid_class_request_set_idle(event.handle,0,0);
    if (result==ESP_OK && !detached.load()) result=hid_host_device_start(event.handle);
    if (detached.load()) return;
    if (!check(result,"boot protocol/start")) { check(hid_host_device_close(event.handle),"close failed admission"); return; }
    connection(true);
    printf("USB KEYBOARD READY\n");
  } else if (event.kind==Kind::disconnected) {
    connection(false);
    // Driver retained WAIT_USER_DELETION; this second close removes it.
    check(hid_host_device_close(event.handle),"disconnect close"); active.store(nullptr);
    printf("USB DISCONNECTED: held keys released; waiting for keyboard\n");
  } else if (!detached.load() && event.generation==generation.load()) report(event.report,event.size);
}
}
