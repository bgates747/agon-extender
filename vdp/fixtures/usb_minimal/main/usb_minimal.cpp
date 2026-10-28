/*
 * USB-only INPUT-004 reproducer. Host/HID API flow derived from Espressif's
 * ESP-IDF 5.5.5 examples/peripherals/usb/host/hid/main/hid_host_example.c
 * (2022-2025 Espressif Systems, Unlicense OR CC0-1.0).
 *
 * Intentionally no Extender video/network/Agon UART/SD service. Boot is inert
 * until an explicit START line on USB Serial/JTAG. No GPIO0 quit convention,
 * reboot, root-power cycle, retry loop, SDK log hook or register diagnostic.
 */
#include <atomic>
#include <cstdio>
#include <cstring>
#include <cinttypes>
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/usb_serial_jtag.h"
#include "driver/usb_serial_jtag_vfs.h"
#include "esp_intr_alloc.h"
#include "esp_timer.h"
#include "usb/usb_host.h"
#include "usb/hid_host.h"
#include "usb_minimal_config.h"

namespace {
constexpr int64_t acquisition_us = 20'000'000;
constexpr int64_t settle_us = 5'000'000;
enum class Kind { ready, error, enumerated, gone, hid, disconnected, report, transfer_error };
struct Event {
    Kind kind{};
    hid_host_device_handle_t hid{};
    uint8_t address{};
    size_t report_size{};
    esp_err_t error{};
    const char *operation{};
};
QueueHandle_t events;
usb_host_client_handle_t observer;
std::atomic<bool> collecting{false}, queue_overflow{false};
bool started{}, ended{}, usb_ready{};
int64_t start_us{}, admitted_us{};
unsigned enumerations{}, reports{};
hid_host_device_handle_t keyboard;
const char *end_reason = "NOT_STARTED";

void send(const Event &event)
{
    if (collecting.load() && xQueueSend(events, &event, 0) != pdTRUE) queue_overflow.store(true);
}

bool checked(esp_err_t result, const char *operation)
{
    if (result == ESP_OK) return true;
    Event event{}; event.kind = Kind::error; event.error = result; event.operation = operation;
    send(event);
    return false;
}

void hid_interface(hid_host_device_handle_t handle, hid_host_interface_event_t kind, void *)
{
    if (!collecting.load()) return;
    Event event{}; event.hid = handle;
    if (kind == HID_HOST_INTERFACE_EVENT_DISCONNECTED) event.kind = Kind::disconnected;
    else if (kind == HID_HOST_INTERFACE_EVENT_TRANSFER_ERROR) event.kind = Kind::transfer_error;
    else if (kind == HID_HOST_INTERFACE_EVENT_INPUT_REPORT) {
        uint8_t bytes[64];
        event.kind = Kind::report;
        if (!checked(hid_host_device_get_raw_input_report_data(handle, bytes, sizeof(bytes), &event.report_size), "report_read")) return;
    } else return;
    send(event);
}

void hid_connected(hid_host_device_handle_t handle, hid_host_driver_event_t kind, void *)
{
    if (kind == HID_HOST_DRIVER_EVENT_CONNECTED) {
        Event event{}; event.kind = Kind::hid; event.hid = handle; send(event);
    }
}

void observer_event(const usb_host_client_event_msg_t *message, void *)
{
    Event event{};
    if (message->event == USB_HOST_CLIENT_EVENT_NEW_DEV) {
        event.kind = Kind::enumerated; event.address = message->new_dev.address;
    } else if (message->event == USB_HOST_CLIENT_EVENT_DEV_GONE) event.kind = Kind::gone;
    else return;
    send(event);
}

void usb_task(void *)
{
    // This task installs the USB IRQ on core1, matching the installed Extender.
    const auto pin = static_cast<gpio_num_t>(USB_MINIMAL_HUB_RESET_GPIO);
    if (!checked(gpio_set_level(pin, 0), "hub_reset_preload") ||
        !checked(gpio_set_direction(pin, GPIO_MODE_OUTPUT), "hub_reset_output")) vTaskDelete(nullptr);
    vTaskDelay(pdMS_TO_TICKS(USB_MINIMAL_HUB_ASSERT_MS));
    if (!checked(gpio_set_level(pin, 1), "hub_reset_release")) vTaskDelete(nullptr);
    vTaskDelay(pdMS_TO_TICKS(USB_MINIMAL_HUB_RECOVERY_MS));
    usb_host_config_t host{};
    host.intr_flags = ESP_INTR_FLAG_LEVEL1;
    host.peripheral_map = 0; // P4 default HS peripheral, still through onboard hub.
    if (!checked(usb_host_install(&host), "host_install")) vTaskDelete(nullptr);
    usb_host_client_config_t client{};
    client.max_num_event_msg = 16;
    client.async.client_event_callback = observer_event;
    if (!checked(usb_host_client_register(&client, &observer), "observer_install")) vTaskDelete(nullptr);
    hid_host_driver_config_t hid{};
    hid.create_background_task = true; hid.task_priority = 5;
    hid.stack_size = 4096; hid.core_id = tskNO_AFFINITY; hid.callback = hid_connected;
    if (!checked(hid_host_install(&hid), "hid_install")) vTaskDelete(nullptr);
    Event ready{}; ready.kind = Kind::ready; send(ready);
    for (;;) {
        uint32_t flags{};
        const auto result = usb_host_lib_handle_events(pdMS_TO_TICKS(100), &flags);
        if (result != ESP_ERR_TIMEOUT && !checked(result, "host_events")) vTaskDelete(nullptr);
        // No automatic free/uninstall, reset, retry or second acquisition.
        // After END the SDK keeps normal USB maintenance; app evidence is frozen.
    }
}

void finish(const char *reason)
{
    if (!started || ended) return;
    collecting.store(false); ended = true; end_reason = reason;
    const auto elapsed = esp_timer_get_time() - start_us;
    std::printf("USBMIN {\"event\":\"end\",\"reason\":\"%s\",\"elapsed_us\":%" PRId64
                ",\"enumerations\":%u,\"keyboard_admitted\":%s,\"reports\":%u,\"restart_allowed\":false}\n",
                reason, elapsed, enumerations, admitted_us ? "true" : "false", reports);
    std::fflush(stdout);
}

void inspect_device(uint8_t address)
{
    usb_device_handle_t device{};
    if (!checked(usb_host_device_open(observer, address, &device), "device_open")) return;
    const usb_device_desc_t *descriptor{};
    usb_device_info_t info{};
    const bool valid = checked(usb_host_get_device_descriptor(device, &descriptor), "device_descriptor") &&
                       checked(usb_host_device_info(device, &info), "device_info");
    if (valid) {
        ++enumerations;
        std::printf("USBMIN {\"event\":\"enumerated\",\"address\":%u,\"vid\":%u,\"pid\":%u,\"speed_usb_enum\":%u,\"class\":%u}\n",
                    unsigned(address), unsigned(descriptor->idVendor), unsigned(descriptor->idProduct),
                    unsigned(info.speed), unsigned(descriptor->bDeviceClass));
    }
    checked(usb_host_device_close(observer, device), "device_close");
}

void handle(const Event &event)
{
    if (ended) return;
    switch (event.kind) {
    case Kind::ready:
        usb_ready = true;
        std::printf("USBMIN {\"event\":\"host_ready\",\"irq_core\":1,\"hid_core\":-1,\"peripheral_map\":0}\n");
        break;
    case Kind::error:
        std::printf("USBMIN {\"event\":\"error\",\"operation\":\"%s\",\"esp_error\":%d}\n", event.operation, int(event.error));
        finish("API_ERROR"); break;
    case Kind::enumerated: inspect_device(event.address); break;
    case Kind::hid: {
        hid_host_dev_params_t params{};
        if (!checked(hid_host_device_get_params(event.hid, &params), "hid_params")) break;
        std::printf("USBMIN {\"event\":\"hid_interface\",\"address\":%u,\"interface\":%u,\"subclass\":%u,\"protocol\":%u}\n",
                    unsigned(params.addr), unsigned(params.iface_num), unsigned(params.sub_class), unsigned(params.proto));
        if (keyboard || params.sub_class != HID_SUBCLASS_BOOT_INTERFACE || params.proto != HID_PROTOCOL_KEYBOARD) break;
        hid_host_device_config_t config{}; config.callback = hid_interface;
        if (!checked(hid_host_device_open(event.hid, &config), "hid_open") ||
            !checked(hid_class_request_set_protocol(event.hid, HID_REPORT_PROTOCOL_BOOT), "hid_boot_protocol") ||
            !checked(hid_class_request_set_idle(event.hid, 0, 0), "hid_idle") ||
            !checked(hid_host_device_start(event.hid), "hid_start")) break;
        keyboard = event.hid; admitted_us = esp_timer_get_time();
        std::printf("USBMIN {\"event\":\"keyboard_admitted\",\"address\":%u,\"interface\":%u}\n", unsigned(params.addr), unsigned(params.iface_num));
        break;
    }
    case Kind::disconnected: finish("HID_DISCONNECTED"); break;
    case Kind::transfer_error: finish("HID_TRANSFER_ERROR"); break;
    case Kind::gone:
        std::printf("USBMIN {\"event\":\"device_gone\"}\n"); break;
    case Kind::report:
        ++reports;
        if (reports == 1) std::printf("USBMIN {\"event\":\"first_report\",\"bytes\":%u}\n", unsigned(event.report_size));
        break;
    }
}

void command(const char *line)
{
    if (!std::strcmp(line, "START") && !started) {
        started = true; end_reason = "RUNNING";
        start_us = esp_timer_get_time(); collecting.store(true);
        std::printf("USBMIN {\"event\":\"start\",\"build\":\"%s\",\"window_us\":%" PRId64 ",\"settle_us\":%" PRId64 "}\n",
                    USB_MINIMAL_BUILD_ID, acquisition_us, settle_us);
        if (xTaskCreatePinnedToCore(usb_task, "usb-minimal", 6144, nullptr, 6, nullptr, 1) != pdPASS) finish("TASK_CREATE_FAILED");
    } else if (!std::strcmp(line, "STOP")) finish("HOST_STOPPED");
    else if (!std::strcmp(line, "STATUS"))
        std::printf("USBMIN {\"event\":\"status\",\"started\":%s,\"ended\":%s,\"reason\":\"%s\"}\n",
                    started ? "true" : "false", ended ? "true" : "false", end_reason);
    else std::printf("USBMIN {\"event\":\"command_rejected\"}\n");
    std::fflush(stdout);
}
} // namespace

extern "C" void app_main(void)
{
    // Console-only installation uses the independent USB Serial/JTAG block.
    // No host/hub GPIO or other peripheral is touched before explicit START.
    usb_serial_jtag_driver_config_t console{};
    console.tx_buffer_size = 2048; console.rx_buffer_size = 256;
    if (usb_serial_jtag_driver_install(&console) != ESP_OK) {
        std::printf("USBMIN {\"event\":\"console_error\"}\n");
        for (;;) vTaskDelay(pdMS_TO_TICKS(1000));
    }
    usb_serial_jtag_vfs_use_driver();
    std::setvbuf(stdout, nullptr, _IONBF, 0);
    events = xQueueCreate(32, sizeof(Event)); // Before host or HID can callback.
    if (!events) {
        std::printf("USBMIN {\"event\":\"queue_error\"}\n");
        for (;;) vTaskDelay(pdMS_TO_TICKS(1000));
    }
    std::printf("USBMIN {\"event\":\"ready\",\"build\":\"%s\",\"source\":\"%s\",\"start_required\":true,\"host_started\":false}\n",
                USB_MINIMAL_BUILD_ID, USB_MINIMAL_SOURCE_COMMIT);
    char line[32]{}; size_t used{}; bool discard{};
    for (;;) {
        char byte{};
        if (usb_serial_jtag_read_bytes(&byte, 1, pdMS_TO_TICKS(10)) == 1) {
            if (byte == '\n' || byte == '\r') {
                if (used && !discard) { line[used] = 0; command(line); }
                used = 0; discard = false;
            } else if (!discard) {
                if (used + 1 < sizeof(line)) line[used++] = byte;
                else { discard = true; std::printf("USBMIN {\"event\":\"command_too_long\"}\n"); }
            }
        }
        if (!started || ended) continue;
        if (usb_ready) {
            const auto result = usb_host_client_handle_events(observer, 0);
            if (result != ESP_ERR_TIMEOUT) checked(result, "observer_events");
        }
        if (queue_overflow.exchange(false)) finish("EVENT_QUEUE_OVERFLOW");
        Event event{};
        for (unsigned count = 0; count < 32 && !ended && xQueueReceive(events, &event, 0) == pdTRUE; ++count) handle(event);
        const auto now = esp_timer_get_time();
        if (!ended && admitted_us && now - admitted_us >= settle_us) finish("KEYBOARD_ADMITTED_SETTLED");
        if (!ended && now - start_us >= acquisition_us) finish("NO_SETTLED_KEYBOARD_WITHIN_WINDOW");
    }
}
