// Actual maintained startup helper with SDK boundaries, no device operations.
#include <cassert>
#include <vector>
#include "extender/transport/console_uart_owner.hpp"
using namespace agon::extender::transport;
static int core,installResult,timeoutResult;
static std::vector<int> calls;
int xPortGetCoreID(){return core;}
esp_err_t uart_driver_install(uart_port_t port,int rx,int tx,int n,QueueHandle_t *q,int flags){
  assert(core==consoleUartOwnerCore&&port==UART_NUM_1&&rx==4096&&tx==0&&n==32&&flags==0);
  calls.push_back(1);if(!installResult)*q=reinterpret_cast<void*>(0x1234);return installResult;
}
esp_err_t uart_set_rx_timeout(uart_port_t port,uint8_t symbols){
  assert(core==consoleUartOwnerCore&&port==UART_NUM_1&&symbols==2);calls.push_back(2);return timeoutResult;
}
int main(){
  for(int c:{0,1})for(int install:{ESP_OK,ESP_FAIL})for(int timeout:{ESP_OK,ESP_FAIL}){
    core=c;installResult=install;timeoutResult=timeout;calls.clear();QueueHandle_t q=nullptr;
    auto r=startConsoleUart(&q);
    if(c!=consoleUartOwnerCore){assert(r==ESP_ERR_INVALID_STATE&&calls.empty()&&!q);}
    else if(install){assert(r==install&&calls==std::vector<int>{1}&&!q);}
    else {assert(r==timeout&&(calls==std::vector<int>{1,2})&&q);}
  }
}
