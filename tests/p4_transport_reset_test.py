"""Actual private recovery leaves and parser control methods; no hardware."""
from pathlib import Path
from datetime import datetime, timezone
from time import monotonic
import subprocess, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
VIDEO=ROOT/'vdp/video'
SDK='''#pragma once
#include <cstdint>
#include <cstddef>
using esp_err_t=int;using uart_port_t=int;using QueueHandle_t=void*;
constexpr int ESP_OK=0,ESP_FAIL=1,ESP_ERR_INVALID_STATE=2,UART_NUM_1=1,pdPASS=1;
constexpr unsigned UART_INTR_TX_DONE=1,UART_INTR_TXFIFO_EMPTY=2;
struct uart_dev_t {};extern uart_dev_t hardware;
#define UART_LL_GET_HW(p) (&hardware)
#define pdMS_TO_TICKS(n) (n)
int xPortGetCoreID();
esp_err_t uart_driver_install(int,int,int,int,void**,int);
esp_err_t uart_set_rx_timeout(int,uint8_t);
esp_err_t uart_disable_intr_mask(int,unsigned);
esp_err_t uart_flush_input(int);
esp_err_t uart_wait_tx_done(int,int);
esp_err_t uart_get_buffered_data_len(int,std::size_t*);
int uart_read_bytes(int,void*,unsigned,int);
void uart_ll_txfifo_rst(uart_dev_t*);
int xQueueReset(void*);
'''
STREAM='''#pragma once
#include <cstddef>
#include <cstdint>
class Stream {
 public:
 virtual ~Stream()=default;
 virtual int available()=0;virtual int read()=0;virtual int peek()=0;
 virtual void flush()=0;virtual size_t write(uint8_t)=0;
 virtual size_t write(const uint8_t*,size_t)=0;
 virtual size_t readBytes(uint8_t*,size_t)=0;
 virtual size_t readBytes(char*,size_t)=0;
 unsigned getTimeout(){return 200;}
};
'''
def method(path, signature):
    text=path.read_text();start=text.index(signature);brace=text.index('{',start)
    depth=1;end=brace+1
    while depth:
        depth += (text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]
class ResetTests(unittest.TestCase):
    def test_actual_leaves(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);(d/'sdk.hpp').write_text(SDK);(d/'Stream.h').write_text(STREAM)
            for name in ('driver/uart.h','freertos/FreeRTOS.h','freertos/queue.h','hal/uart_ll.h'):
                f=d/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text('#include "sdk.hpp"\n')
            exe=d/'reset'
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',
                '-fsanitize=address,undefined','-fno-sanitize-recover=all',f'-I{d}',f'-I{VIDEO}',
                str(ROOT/'tests/p4_transport_reset_test.cpp'),
                str(VIDEO/'extender/transport/p4_parallel_handover.cpp'),'-o',str(exe)],check=True)
            subprocess.run([str(exe)],check=True,timeout=10)
    def test_actual_parser_boundary_preserves_scene(self):
        # Execute the maintained method bodies, not a second reset implementation.
        context=method(VIDEO/'context.h','void consoleTransportBoundary()')
        processor=method(VIDEO/'vdu_stream_processor.h','void consoleTransportBoundary()')
        source='''#include <cassert>
#include <string>
#include <deque>
enum class VDUProcessorState {Active, PagedModePaused};
struct Context {VDUProcessorState processorState=VDUProcessorState::PagedModePaused;
 unsigned idleFrameCount=8; int scene=77;
'''+context+'''};
struct Events {std::deque<int> q{1,2};unsigned size(){return q.size();}
 void pop(){assert(!q.empty());q.pop_front();}};
struct Processor {bool commandsEnabled=false,echoEnabled=true,echoBuffering=true;
 std::string echoBuffer="old output";int a=0,b=0;int *outputStream=&a,*originalOutputStream=&b;
 Context c;Context *context=&c;Events eventQueue;
'''+processor+'''};
int main(){Processor p;p.consoleTransportBoundary();
 assert(p.commandsEnabled&&!p.echoEnabled&&!p.echoBuffering&&p.echoBuffer.empty());
 assert(p.outputStream==p.originalOutputStream&&!p.eventQueue.size());
 assert(p.c.processorState==VDUProcessorState::Active&&!p.c.idleFrameCount&&p.c.scene==77);
 p.consoleTransportBoundary();}
'''
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/'parser.cpp';f.write_text(source);exe=f.with_suffix('')
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',str(f),'-o',str(exe)],check=True)
            subprocess.run([str(exe)],check=True)
    def test_console_owner_ordering(self):
        s=(VIDEO/'extender/transport/console_hardware.inc').read_text()
        run=s.split('void runConsole(VDUStreamProcessor *processor)',1)[1]
        loop=run.split('for(;;)',1)[1]
        self.assertLess(loop.index('startup.poll('),loop.index('usbhost::pump('))
        cancel=run.split('auto cancelTransport=[&](){',1)[1].split('\n  };',1)[0]
        # Comments mention the forbidden helper; executable calls must not.
        code='\n'.join(line.split('//',1)[0] for line in cancel.splitlines())
        self.assertNotIn('console_cancel_tx(',code);self.assertNotIn('uart_set_pin(',code)
        for call in ('s.transportLost()','console_keys.reset()','keyboard.admissionBoundary()',
                     'processedKeyboard().reset()','r.boundary(', 'sdTransportLost()',
                     'processor->consoleTransportBoundary()', 'discardConsoleUart(',
                     'keyboard.lost(', 'usbhost::transportBoundary()'):
            self.assertIn(call,code)
        restore=run.split('auto restoreUart=[](){',1)[1].split('\n  };',1)[0]
        self.assertLess(restore.index('discardConsoleUart'),restore.index('uart_set_pin'))
        self.assertLess(restore.index('consoleUartResetIdle'),restore.index('uart_set_pin'))
        self.assertLess(restore.index('usbhost::transportBoundary'),restore.index('uart_set_pin'))
        worker=(VIDEO/'extender/storage/webdav/runtime.cpp').read_text()
        self.assertIn('q.complete(generation,response,got,close)',worker)
    def test_queued_usb_reports_cross_no_epoch(self):
        usb=VIDEO/'extender/input/p4_usb_host.hpp'
        body=method(usb,'inline void transportBoundary()')
        gate=usb.read_text().split('} else if (!detached.load()',1)[1].split(') report(',1)[0]
        source='''#include <atomic>
#include <cassert>
std::atomic<unsigned> generation{7};std::atomic<bool> detached{false};
struct Event {unsigned generation;};
'''+body+'''
bool accepts(Event event){return !detached.load()'''+gate+''';}
int main(){Event old{generation.load()};assert(accepts(old));
 transportBoundary();assert(!accepts(old));Event whileDetached{generation.load()};
 transportBoundary();assert(!accepts(whileDetached));
 Event fresh{generation.load()};assert(accepts(fresh));detached=true;assert(!accepts(fresh));}
'''
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/'usb.cpp';f.write_text(source);exe=f.with_suffix('')
            subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror',str(f),'-o',str(exe)],check=True)
            subprocess.run([str(exe)],check=True)
if __name__=='__main__':
    start=datetime.now(timezone.utc).isoformat();clock=monotonic()
    try:result=unittest.main(exit=False).result
    finally:print(f'Reset suite: start={start}, end={datetime.now(timezone.utc).isoformat()}, '
                  f'elapsed={monotonic()-clock:.6f} s (host tests, not wire timing)')
    raise SystemExit(0 if result.wasSuccessful() else 1)
