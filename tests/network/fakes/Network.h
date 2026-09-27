#pragma once
#include <functional>
#include <map>
using network_event_handle_t = unsigned;
enum arduino_event_id_t { ARDUINO_EVENT_ETH_START, ARDUINO_EVENT_ETH_CONNECTED,
 ARDUINO_EVENT_ETH_GOT_IP, ARDUINO_EVENT_ETH_LOST_IP, ARDUINO_EVENT_ETH_DISCONNECTED,
 ARDUINO_EVENT_ETH_STOP, OTHER_EVENT };
struct arduino_event_info_t {};
struct FakeNetwork {
 using Fn = std::function<void(arduino_event_id_t, arduino_event_info_t)>;
 std::map<unsigned,Fn> handlers;
 unsigned next=0;
 bool fail=false;
 unsigned onEvent(Fn callback) {if(fail)return 0;handlers[++next]=callback;return next;}
 void removeEvent(unsigned id) {handlers.erase(id);}
};
inline FakeNetwork Network;
