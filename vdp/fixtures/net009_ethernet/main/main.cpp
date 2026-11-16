#include "transfer.h"

#include <cstdio>
#include <unistd.h>
#include <fcntl.h>
#include "driver/usb_serial_jtag.h"
#include "driver/usb_serial_jtag_vfs.h"
#include "esp_eth.h"
#include "esp_eth_netif_glue.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_timer.h"
#include "lwip/sockets.h"
#include "lwip/tcp.h"

namespace {
esp_netif_t *netif = nullptr;

void start_ethernet() {
    // Olimex P4-PC Rev C matches the maintained P4-PC board config. Only
    // Ethernet and USB Serial/JTAG are active in this fixture.
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_config_t netif_config = ESP_NETIF_DEFAULT_ETH();
    netif = esp_netif_new(&netif_config);
    ESP_ERROR_CHECK(netif ? ESP_OK : ESP_ERR_NO_MEM);
    eth_mac_config_t mac_config = ETH_MAC_DEFAULT_CONFIG();
    eth_esp32_emac_config_t emac_config = ETH_ESP32_EMAC_DEFAULT_CONFIG();
    emac_config.smi_gpio.mdc_num = 31;
    emac_config.smi_gpio.mdio_num = 52;
    emac_config.clock_config.rmii.clock_mode = EMAC_CLK_EXT_IN;
    emac_config.clock_config.rmii.clock_gpio = 50;
    eth_phy_config_t phy_config = ETH_PHY_DEFAULT_CONFIG();
    phy_config.phy_addr = 1;
    phy_config.reset_gpio_num = 51;
    auto *mac = esp_eth_mac_new_esp32(&emac_config, &mac_config);
    auto *phy = esp_eth_phy_new_ip101(&phy_config);
    ESP_ERROR_CHECK(mac && phy ? ESP_OK : ESP_ERR_NO_MEM);
    esp_eth_handle_t handle = nullptr;
    esp_eth_config_t eth = ETH_DEFAULT_CONFIG(mac, phy);
    ESP_ERROR_CHECK(esp_eth_driver_install(&eth, &handle));
    ESP_ERROR_CHECK(esp_netif_attach(netif, esp_eth_new_netif_glue(handle)));
    ESP_ERROR_CHECK(esp_eth_start(handle));
}

void status() {
    esp_netif_ip_info_t ip{};
    if (esp_netif_is_netif_up(netif)) esp_netif_get_ip_info(netif, &ip);
    std::printf("NET009 {\"event\":\"status\",\"source\":\"%s\",\"ip\":\"" IPSTR "\"}\n",
                NET009_SOURCE_COMMIT, IP2STR(&ip.ip));
}

void terminal(uint32_t nonce, const net009::Result &result) {
    std::printf("NET009 {\"event\":\"result\",\"nonce\":%lu,\"pass\":%s,"
                "\"tx_frames\":%lu,\"rx_frames\":%lu,\"error\":\"%s\",\"failed_frame_hex\":\"",
                static_cast<unsigned long>(nonce), result.error ? "false" : "true",
                static_cast<unsigned long>(result.tx_frames),
                static_cast<unsigned long>(result.rx_frames), result.error ? result.error : "");
    if (result.error) {
        for (size_t i = 0; i < result.received_size; ++i) std::printf("%02x", result.received[i]);
    }
    std::puts("\"}");
}

void serve(const net009::Arm &arm) {
    esp_netif_ip_info_t ip{};
    const int listener = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    net009::Result result;
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    socklen_t size = sizeof(addr);
    if (!esp_netif_is_netif_up(netif) || esp_netif_get_ip_info(netif, &ip) != ESP_OK || !ip.ip.addr)
        result.error = "no_ip";
    else if (listener < 0)
        result.error = "socket";
    else {
        addr.sin_addr.s_addr = ip.ip.addr;
        if (bind(listener, reinterpret_cast<sockaddr *>(&addr), size) ||
            listen(listener, 1) ||
            getsockname(listener, reinterpret_cast<sockaddr *>(&addr), &size))
            result.error = "listen";
    }
    if (result.error) {
        terminal(arm.nonce, result);
        if (listener >= 0) close(listener);
        return;
    }
    std::printf("NET009 {\"event\":\"armed\",\"nonce\":%lu,\"ip\":\"" IPSTR "\",\"port\":%u}\n",
                static_cast<unsigned long>(arm.nonce), IP2STR(&ip.ip), ntohs(addr.sin_port));
    fd_set ready;
    FD_ZERO(&ready);
    FD_SET(listener, &ready);
    timeval timeout{15, 0};
    const int client = select(listener + 1, &ready, nullptr, nullptr, &timeout) == 1
                           ? accept(listener, nullptr, nullptr) : -1;
    close(listener);
    const int on = 1;
    if (client < 0) result.error = "accept";
    else if (fcntl(client, F_SETFL, O_NONBLOCK) ||
             setsockopt(client, IPPROTO_TCP, TCP_NODELAY, &on, sizeof(on)))
        result.error = "socket_options";
    else result = net009::transfer(client, arm, esp_timer_get_time);
    terminal(arm.nonce, result);
    if (client >= 0) {
        // Leave TCP connected for the host's guarded +++ and explicit close.
        // After a data fault, discard any bytes already in flight.
        const auto deadline = esp_timer_get_time() + 15000000;
        uint8_t discarded[1024];
        for (auto remaining = deadline - esp_timer_get_time(); remaining > 0;
             remaining = deadline - esp_timer_get_time()) {
            FD_ZERO(&ready);
            FD_SET(client, &ready);
            timeout = {long(remaining / 1000000), long(remaining % 1000000)};
            if (select(client + 1, &ready, nullptr, nullptr, &timeout) <= 0 ||
                recv(client, discarded, sizeof(discarded), MSG_DONTWAIT) <= 0) break;
        }
        close(client);
    }
    status();
}

bool valid(unsigned rate, unsigned ms) {
    return (rate == 115200 || rate == 230400 || rate == 384000 ||
            rate == 576000 || rate == 1152000) &&
           (ms == 3000 || ms == 10000 || ms == 30000 || ms == 60000);
}
}

extern "C" void app_main() {
    usb_serial_jtag_driver_config_t usb{4096, 256};
    ESP_ERROR_CHECK(usb_serial_jtag_driver_install(&usb));
    usb_serial_jtag_vfs_use_driver();
    std::setvbuf(stdout, nullptr, _IONBF, 0);
    start_ethernet();
    status();
    char line[96];
    size_t length = 0;
    char c;
    bool overflow = false;
    for (;;) {
        if (usb_serial_jtag_read_bytes(&c, 1, pdMS_TO_TICKS(20)) != 1) continue;
        if (c == '\r' || c == '\n') {
            if (length && !overflow) {
                line[length] = 0;
                unsigned nonce, baud, ms;
                char dir[5], extra;
                if (!strcmp(line, "STATUS")) status();
                else if (std::sscanf(line, "ARM %u %u %u %4s %c", &nonce, &baud, &ms, dir, &extra) == 4 &&
                         valid(baud, ms) && (!strcmp(dir, "up") || !strcmp(dir, "down")))
                    serve({nonce, baud, ms, !strcmp(dir, "up")});
                else std::puts("NET009 {\"event\":\"refused\"}");
            }
            length = 0;
            overflow = false;
        } else if (length + 1 < sizeof(line) && !overflow) {
            line[length++] = c;
        } else overflow = true;
    }
}
