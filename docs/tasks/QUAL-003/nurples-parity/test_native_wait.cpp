#include <cassert>
#include <chrono>
#include <future>
#include <thread>
#include "extender/display/stock_native_access.hpp"
namespace agon::extender::display {
std::recursive_mutex &stockNativeMutex(){static std::recursive_mutex m;return m;}
}
using namespace agon::extender::display;
int main(){
#ifdef AGON_EXTENDER_NATIVE_WAIT_TRACE
 using namespace agon_native_wait;
 prepare();arm();assert(observing());
 std::thread other([]{assert(!observing());StockNativeGuard g(stockNativeMutex());});other.join();
 assert(calls==0);
 {std::recursive_mutex foreground;StockNativeGuard g(foreground);}assert(calls==0);
 {StockNativeGuard g(stockNativeMutex());StockNativeGuard nested(stockNativeMutex());}
 assert(calls==2);boundary();assert(count==1 && samples[0].calls==2 && calls==0);
 std::promise<void> held;auto ready=held.get_future();
 std::thread holder([&]{std::lock_guard lock(stockNativeMutex());held.set_value();std::this_thread::sleep_for(std::chrono::milliseconds(30));});
 ready.wait();{StockNativeGuard g(stockNativeMutex());}holder.join();
 boundary();assert(samples[1].calls==1 && samples[1].wait_us>=1000 && samples[1].maximum_us==samples[1].wait_us);
 for(unsigned i=2;i<=Capacity;++i)boundary();assert(invalid && count==Capacity+1);
 stop();{StockNativeGuard g(stockNativeMutex());}boundary();assert(count==Capacity+1);
 arm();assert(count==0 && !invalid);stop();std::free(samples);samples=nullptr;
#else
 {StockNativeGuard g(stockNativeMutex());StockNativeGuard nested(stockNativeMutex());}
#endif
}
