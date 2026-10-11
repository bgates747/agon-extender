#include "extender/network/screen_text.hpp"
#if defined(AGON_EXTENDER_TELEMETRY)
#include "../telemetry/target.hpp"
#endif
// Single retained-parser owner for ordinary VDU, USB events and stock replies.
// USB callbacks only queue reports. Neither ISR nor network task writes UART1.
#include <driver/gpio.h>
#include <hal/uart_ll.h>
#include <esp_random.h>
#include "console_uart_owner.hpp"
#include "../storage/local/http.hpp"
#if defined(AGON_EXTENDER_PARALLEL_BOOT_CANDIDATE)
#include "p4_boot_startup.hpp"
#include "p4_uart_reset.hpp"
#include "p4_block_coordinator.hpp"
#if defined(AGON_EXTENDER_PARALLEL_DATA_CHECK)
#include "p4_parallel_data_check.hpp"
#endif
#if defined(AGON_EXTENDER_PARALLEL_PROBE)
#include "p4_parallel_probe.hpp"
#endif
#endif
#if defined(AGON_EXTENDER_NATIVE_BUILD)
#include "agon_extender_board_config.hpp"
namespace console_board = agon::extender::board;
#else
// Historical hybrid reproductions retain their original DevKit tuple.
// Board selection is supported only by the maintained native build wrapper.
namespace console_board {
constexpr int kUartTx=12,kUartRx=22,kUartRts=11,kUartCts=23;
constexpr int kFencePins[]={9,10,11,12,13,14,15,17,20,21,22,23,32,33};
constexpr char kIdentity[]="legacy-devkit";
}
#endif
#include "../input/p4_usb_host.hpp"
#include "../input/usb_cli_keyboard.hpp"
#include "../input/usb_key_queue.hpp"
#include "../diagnostics/frame_timing.hpp"
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
#include "../input/remote_target.hpp"
#endif
#if defined(AGON_EXTENDER_SD_SERVICE)
#include "../storage/sd_target.hpp"
#endif
namespace {
ConsoleStream *console_stream;
QueueHandle_t console_events;
#if defined(AGON_EXTENDER_PARALLEL_DATA_CHECK)
std::optional<agon::extender::transport::P4ParallelDataCheck> console_data_check;
#endif
#if defined(AGON_EXTENDER_PARALLEL_PROBE)
std::optional<agon::extender::transport::P4ParallelProbe> console_probe;
#endif
agon::extender::input::UsbCliKeyboard console_keyboard;
agon::extender::input::UsbKeyQueue console_keys;
bool console_locale_pending{},console_admit_pending{},console_overload{};
void console_cancel_tx() {
  // IDF 5.5.5 flush is RX-only; inherited bounded TX cancellation from PORT-015.
  ESP_ERROR_CHECK(gpio_reset_pin(gpio_num_t(console_board::kUartTx)));
  ESP_ERROR_CHECK(uart_disable_intr_mask(UART_NUM_1,UART_INTR_TX_DONE|UART_INTR_TXFIFO_EMPTY));
  uart_ll_txfifo_rst(UART_LL_GET_HW(UART_NUM_1));
  ESP_ERROR_CHECK(gpio_set_level(gpio_num_t(console_board::kUartTx),1));
  ESP_ERROR_CHECK(uart_set_pin(UART_NUM_1,console_board::kUartTx,console_board::kUartRx,
                             console_board::kUartRts,console_board::kUartCts));
}
}
#if defined(AGON_EXTENDER_SD_SERVICE)
void consoleSdReceive(const uint8_t *p,unsigned n) {
  agon::extender::storage::sdReceive(p,n,millis());
}
void consoleSdIncomplete() { console_stream->fail("incomplete SD envelope"); }
#endif
void consoleLayout(int region) {
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
  agon::extender::input::remoteLocked([](auto &r){r.boundary();return 0;});
#endif
  if (!console_keys.releaseAll()) console_stream->fail("layout release capacity");
  console_keyboard.admissionBoundary();
  console_keyboard.locale=region;
  console_locale_pending=region>=0 && region<=1;
}
void consolePoll() { if(console_locale_pending) console_admit_pending=true; }
bool consoleControl(VDUStreamProcessor *processor, const uint8_t *p) {
  uint8_t reply[CONSOLE_SIZE];
  if (p[2]==PARALLEL_WIRE_VERSION) {
#if defined(AGON_EXTENDER_EXEXT_STREAM)
    if(p[3]==PARALLEL_STREAM_START || p[3]==PARALLEL_STREAM_POLL || p[3]==PARALLEL_STREAM_STOP) {
      if(!console_stream->parallelVdu.request(p,reply,console_stream->session.active()))return false;
      console_stream->controlReply(reply,sizeof(reply));return true;
    }
    // Backpressure leaves a complete control envelope with the UART owner;
    // do not admit a physical transfer before storage is available.
    if(p[3]==PARALLEL_OFFER && !console_stream->parallelVdu.canOffer(p))return false;
#endif
    // Shared F7 framing, distinct capability. No display reset or mode commit.
    if (!console_stream->parallel.request(p,millis(),esp_random(),reply)) return false;
#if defined(AGON_EXTENDER_EXEXT_STREAM)
    if(p[3]==PARALLEL_OFFER && !console_stream->parallelVdu.acceptedOffer()) {
      console_stream->parallel.cancel();console_stream->fail("parallel stream storage");return false;
    }
#endif
#if defined(AGON_EXTENDER_PARALLEL_DATA_CHECK)
    if(p[3]==PARALLEL_OFFER && (!console_data_check || !console_data_check->acceptedOffer())) {
      console_stream->parallel.cancel();console_stream->fail("data check storage");return false;
    }
#endif
#if defined(AGON_EXTENDER_PARALLEL_PROBE)
    if(p[3]==PARALLEL_OFFER && (!console_probe || !console_probe->acceptedOffer(micros()))) {
      console_stream->parallel.cancel();console_stream->fail("private probe storage");return false;
    }
#endif
  } else {
#if defined(AGON_EXTENDER_PARALLEL_BOOT_CANDIDATE)
    if(!console_stream->parallel.uartTransitionAllowed())return false;
#endif
    if (!console_stream->session.request(p,millis(),esp_random(),reply)) return false;
    // An ordinary lease change revokes capability but preserves proven UART
    // ownership. Physical cancel would fence/discard this command's own reply.
#if defined(AGON_EXTENDER_PARALLEL_BOOT_CANDIDATE)
    console_stream->parallel.revokeUartCapability();
#else
    console_stream->parallel.cancel();
#endif
  }
  if(p[2]==1 && p[3]==CONSOLE_PREPARE) {
    // PORT-008 N002: raw changeMode() replaces Canvas with no selected font.
    // Skipping retained vdu_mode() context reset crashed on EMOS's first
    // VDU 26 (cursorHome -> getFont()->width). Use the complete stock lifecycle,
    // including drain, context/font reset and mode reply, before acknowledging
    // preparation. EMOS ignores that pre-commit mode reply in Legacy; its
    // post-commit queries still own publication. USB acquisition is separate.
    processor->vdu_mode(0);
  }
  // QUAL-003: PREPARE_KEEP deliberately leaves Canvas, contexts and resource
  // buffers intact. Its fresh lease is still required before ordinary output.
  console_stream->controlReply(reply,sizeof(reply));
  // Successful native block exchanges are the ordinary ExExt hot path. USB
  // stdout backpressure must not become per-block work; first faults still log.
  if(p[2]!=PARALLEL_WIRE_VERSION)
    printf("Console control version=%u op=%u active=%u\n",p[2],p[3],console_stream->session.active());
  return true;
}
ConsoleStream *beginConsole() {
  // MANDATORY BOARD FORK (FWBUG-014): --board p4-pc enables fixed 3.3V LDO4
  // for D7/GPIO46 before any pad setup; --board p4-devkit makes this a no-op.
  // Supply ownership is independent of an SD card or EMOS transport lease.
  // Fail before touching shared pads if the board's I/O bank cannot be powered.
  if(!agon::extender::local_sd::beginSharedIoSupply())abort();
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
  agon::extender::input::remoteLocked([](auto &r){r.begin(esp_random());return 0;});
#endif
  for(int pin:console_board::kFencePins) {
    ESP_ERROR_CHECK(gpio_reset_pin(gpio_num_t(pin)));
    ESP_ERROR_CHECK(gpio_set_direction(gpio_num_t(pin),GPIO_MODE_INPUT));
    ESP_ERROR_CHECK(gpio_pullup_dis(gpio_num_t(pin)));ESP_ERROR_CHECK(gpio_pulldown_dis(gpio_num_t(pin)));
  }
  uart_config_t cfg{};cfg.baud_rate=1152000;cfg.data_bits=UART_DATA_8_BITS;
  cfg.parity=UART_PARITY_DISABLE;cfg.stop_bits=UART_STOP_BITS_1;
  cfg.flow_ctrl=UART_HW_FLOWCTRL_CTS_RTS;cfg.rx_flow_ctrl_thresh=64;cfg.source_clk=UART_SCLK_DEFAULT;
  ESP_ERROR_CHECK(uart_param_config(UART_NUM_1,&cfg));
#if !defined(AGON_EXTENDER_PARALLEL_BOOT_CANDIDATE)
  ESP_ERROR_CHECK(uart_set_pin(UART_NUM_1,console_board::kUartTx,console_board::kUartRx,
                             console_board::kUartRts,console_board::kUartCts));
#endif
  console_stream=new ConsoleStream;
  console_stream->setTimeout(COMMS_TIMEOUT); // match stock setupVDPProtocol (200 ms)
  if(!agon::extender::input::usbhost::begin()) console_stream->fail("USB host startup");
  return console_stream;
}
void runConsole(VDUStreamProcessor *processor) {
  // First driver operation on the sole process owner. Setup only configured
  // pins/registers and built an inactive Stream; it did not install an ISR.
  ESP_ERROR_CHECK(agon::extender::transport::startConsoleUart(&console_events));
#if defined(AGON_EXTENDER_PARALLEL_BOOT_CANDIDATE)
  // Driver/ISR belongs to this core. Setup never attached shared UART pins.
  // Neither the parser nor keyboard serializer runs until reciprocal release.
  agon::extender::transport::P4BootStartup startup(console_stream->parallel.handover,console_board::kDataPins,
      console_board::kReady,console_board::kClock,console_board::kValid,xPortGetCoreID());
  auto restoreUart=[](){
    // Shared pads are already detached. Cancel old FIFO/ring/event contents
    // BEFORE reattaching; RX flush alone is not TX/shift-register quiescence.
    using namespace agon::extender::transport;
    if(!discardConsoleUart(console_events) || !consoleUartResetIdle())return false;
    agon::extender::input::usbhost::transportBoundary();
    return uart_set_pin(UART_NUM_1,console_board::kUartTx,console_board::kUartRx,
        console_board::kUartRts,console_board::kUartCts)==ESP_OK;
  };
  // HTTP can start before retained VDP/display initialization finishes. The
  // installer must not release a held Agon reset on HTTP readiness alone:
  // EMOS has a bounded boot handshake. This one-time USB marker observes the
  // actual console owner's completed pad fence; it grants no UART ownership.
  if(startup.begin(millis()))
    printf("Parallel boot pads released; awaiting EMOS\n");
  while(!startup.poll(millis(),restoreUart)) {
#if defined(AGON_EXTENDER_PARALLEL_PROBE)
    // LC03-B boot diagnosis only: USB console, never the shared UART. Sample
    // actual pads at a bounded cadence; do not manufacture release progress.
    static uint32_t nextBootReport=0;
    if(int32_t(millis()-nextBootReport)>=0) {
      nextBootReport=millis()+500;
      printf("Parallel boot phase=%u ready_n_command=%u clock=%d valid=%d\n",
          unsigned(console_stream->parallel.handover.phase()),
          unsigned(console_stream->parallel.handover.readyN()),
          gpio_get_level(gpio_num_t(console_board::kClock)),
          gpio_get_level(gpio_num_t(console_board::kValid)));
    }
#endif
    vTaskDelay(pdMS_TO_TICKS(1));
  }
#if defined(AGON_EXTENDER_PARALLEL_DATA_CHECK)
  console_data_check.emplace(console_stream->parallel);
  if(!console_data_check->begin())abort();
#endif
#if defined(AGON_EXTENDER_PARALLEL_PROBE)
  console_probe.emplace(console_stream->parallel);
  if(!console_probe->begin())abort();
#endif
#if defined(AGON_EXTENDER_EXEXT_STREAM)
  if(!console_stream->parallelVdu.begin())abort();
#endif
  agon::extender::transport::P4BlockCoordinator block(console_stream->parallel,
      console_board::kDataPins,console_board::kClock,console_board::kValid,
      console_board::kReady,console_board::kUartTx,console_board::kUartRx,
      console_board::kUartRts,console_board::kUartCts,xPortGetCoreID());
#endif
  printf("ExCom console %s (%s), UART1 1152000 8N1 RTS/CTS\n",AGON_EXTENDER_BUILD_ID,AGON_EXTENDER_ARTIFACT_STATUS);
  printf("Board %s UART1 TX=%d RX=%d RTS=%d CTS=%d\n",console_board::kIdentity,
         console_board::kUartTx,console_board::kUartRx,console_board::kUartRts,console_board::kUartCts);
  namespace timing = agon::extender::diagnostics;
  auto &s=*console_stream;
  auto &keyboard=console_keyboard;
  auto emit=[](agon::extender::input::ProcessedKey k){
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
    agon::extender::input::remoteLocked([&](auto &r){
      r.physicalKey(k);
      agon::extender::input::ProcessedKey up;
      while(r.release(up))if(!console_keys.push(up))console_overload=true;
      return 0;
    });
#endif
    if(!console_keys.push(k))console_overload=true;
  };
  uint8_t incoming[244]{};
  unsigned used=0,need=3;
  unsigned discard=0;
  uint32_t partial_at=0,tx_at=0;
  bool transmitting=false;
#if defined(AGON_EXTENDER_PARALLEL_BOOT_CANDIDATE)
  bool failureReported=false;
  auto cancelTransport=[&](){
    // P4BootStartup completed a NEW physical fence before this callback.
    // Do not call console_cancel_tx: its ordinary fault path rebinds GPIO.
#if defined(AGON_EXTENDER_PARALLEL_DATA_CHECK)
    console_data_check->cancel();
#endif
#if defined(AGON_EXTENDER_PARALLEL_PROBE)
    console_probe->cancel();
#endif
    s.transportLost();used=discard=0;need=3;partial_at=tx_at=0;transmitting=false;
    failureReported=false;
    console_keys.reset();keyboard.lost([](agon::extender::input::ProcessedKey){});
    keyboard.admissionBoundary();agon::extender::input::usbhost::transportBoundary();
    agon::extender::input::processedKeyboard().reset();
    console_locale_pending=console_admit_pending=console_overload=false;
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
    agon::extender::input::remoteLocked([](auto &r){
      r.boundary(agon::extender::input::RemoteKeyboard::transport);
      agon::extender::input::ProcessedKey ignored;
      while(r.release(ignored)){} // old releases cannot cross physical epochs
      return 0;
    });
#endif
#if defined(AGON_EXTENDER_SD_SERVICE)
    agon::extender::storage::sdTransportLost();
#endif
#if defined(AGON_EXTENDER_TELEMETRY)
    agon::extender::telemetry::reset();
#endif
    processor->consoleTransportBoundary();
    const bool cleared=agon::extender::transport::discardConsoleUart(console_events);
    if(!cleared)printf("Private UART reset cleanup failed; pads remain fenced\n");
    return cleared;
  };
#endif
  // I/O-only recursion is deliberately bounded: retained reads may service
  // UART control/native handover, but never reenter processNext or callbacks.
  std::function<void(bool)> step;
  step=[&](bool parseCommands) {
    const uint32_t now=millis();
#if defined(AGON_EXTENDER_PARALLEL_BOOT_CANDIDATE)
    using BlockResult=agon::extender::transport::P4BlockCoordinator::Result;
    if(s.failure) {
      // Report once before reset recovery clears the original reason. USB
      // stdout only; no shared-UART output or successful-path instrumentation.
      if(!failureReported)printf("Console transport fault: %s\n",s.failure);
      failureReported=true;s.parallel.cancel();
    }
    const auto blockResult=block.poll(now,!used&&!discard&&
#if defined(AGON_EXTENDER_EXEXT_STREAM)
                                     (s.parallelVdu.active() || (s.cached<0&&s.pos>=4)),
#else
                                     s.cached<0&&s.pos>=4,
#endif
                                     !s.count&&!transmitting);
#if defined(AGON_EXTENDER_PARALLEL_PROBE)
    // LC03-B physical phase diagnosis: USB only, on phase/result changes.
    // Observations never advance the owner or stand in for peer evidence.
    static unsigned lastBlockPhase=~0u,lastBlockResult=~0u;
    const unsigned blockPhase=unsigned(s.parallel.handover.phase());
    if(blockPhase!=lastBlockPhase || unsigned(blockResult)!=lastBlockResult) {
      printf("Parallel state ms=%lu phase=%u result=%u pending=%u count=%u tx=%u boundary=%u clock=%d valid=%d ready_n_command=%u failure=%s\n",
        (unsigned long)now,blockPhase,unsigned(blockResult),s.parallel.pending(),s.count,transmitting,
        !used&&!discard&&s.cached<0&&s.pos>=4,
        gpio_get_level(gpio_num_t(console_board::kClock)),
        gpio_get_level(gpio_num_t(console_board::kValid)),
        unsigned(s.parallel.handover.readyN()),s.failure?s.failure:"none");
      lastBlockPhase=blockPhase;lastBlockResult=unsigned(blockResult);
    }
#endif
    if(blockResult==BlockResult::exclusive) {
      // The admitted block already has bounded peer/deadline checks. Sleeping
      // one RTOS tick at every held handshake phase adds milliseconds to even
      // a one-byte exchange and stalls MOS keyboard/query foreground work.
      // Re-enter this sole owner promptly, as the ordinary parser loop does;
      // interrupts and higher-priority tasks remain enabled throughout.
      return;
    }
    if(blockResult==BlockResult::cleanupFault) {
      vTaskDelay(pdMS_TO_TICKS(1));return;
    }
    const bool blockDrain=blockResult==BlockResult::drain;
    // No parser, USB admission or UART writer runs while release is unresolved.
    if(!blockDrain && !startup.poll(now,restoreUart,cancelTransport)) {
      vTaskDelay(pdMS_TO_TICKS(1));return;
    }
    if(!blockDrain)block.recovered();
#if defined(AGON_EXTENDER_EXEXT_STREAM)
    if(!s.parallelVdu.retire())s.fail("parallel stream receipt");
#endif
#if defined(AGON_EXTENDER_PARALLEL_DATA_CHECK)
    if(!console_data_check->retire())s.fail("data check guards");
    agon::extender::transport::P4ParallelDataCheck::Snapshot dataSnapshot;
    if(console_data_check->takeSnapshot(dataSnapshot)) {
      // Private receive/echo attribution only, after reciprocal UART recovery.
      // Bounded USB stdout; no shared-UART diagnostics or payload-path logging.
      char first[33]{},last[33]{};
      constexpr char hex[]="0123456789abcdef";
      for(unsigned i=0;i<dataSnapshot.count;++i) {
        first[i*2]=hex[dataSnapshot.first[i]>>4];first[i*2+1]=hex[dataSnapshot.first[i]&15];
        last[i*2]=hex[dataSnapshot.last[i]>>4];last[i*2+1]=hex[dataSnapshot.last[i]&15];
      }
      printf("Parallel data snapshot direction=%u length=%u fnv=%08lx first=%s last=%s\n",
        unsigned(dataSnapshot.direction),unsigned(dataSnapshot.length),
        (unsigned long)dataSnapshot.fnv,first,last);
      if(dataSnapshot.independent)
        printf("Parallel independent direction=%u length=%u mismatches=%u first_offset=%u actual=%02x expected=%02x prepared_fnv=%08lx\n",
          unsigned(dataSnapshot.direction),unsigned(dataSnapshot.length),
          unsigned(dataSnapshot.mismatches),unsigned(dataSnapshot.firstMismatch),
          unsigned(dataSnapshot.actual),unsigned(dataSnapshot.expected),
          (unsigned long)dataSnapshot.preparedFnv);
    }
#endif
#if defined(AGON_EXTENDER_PARALLEL_PROBE)
    agon::extender::transport::P4ParallelProbe::Receipt receipt;
    if(console_probe->take(micros(),receipt)) {
      char descriptor[33];
      constexpr char hex[]="0123456789abcdef";
      for(unsigned i=0;i<16;++i) {
        descriptor[i*2]=hex[receipt.descriptor[i]>>4];
        descriptor[i*2+1]=hex[receipt.descriptor[i]&15];
      }
      descriptor[32]=0;
      printf("Parallel probe descriptor=%s direction=%u length=%u crc=%08lx first=%02x last=%02x guards=%u pattern=%s elapsed_us=%lu\n",
        descriptor,unsigned(receipt.direction),unsigned(receipt.length),(unsigned long)receipt.crc,
        unsigned(receipt.first),unsigned(receipt.last),unsigned(receipt.guards),
        receipt.direction?(receipt.pattern?"1":"0"):"na",(unsigned long)receipt.elapsedUs);
    }
#endif
    // Only complete, already queued packets may drain. Do not pump USB,
    // pop keys, tick repeat, parse another VDU or enqueue a service response.
    if(!s.parallel.pending()) {
#endif
    s.session.expire(now);s.parallel.expire(now);
    agon::extender::input::usbhost::pump(
      [&](const uint8_t *p,size_t n){keyboard.report(p,n,now,emit);},
      [&](bool attached){if(!attached) {
        keyboard.disconnect(emit);
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
        agon::extender::input::remoteLocked([](auto &r){r.physicalLost();return 0;});
#endif
      }},
      [&](){keyboard.lost(emit);});
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
    agon::extender::input::remoteLocked([&](auto &r){r.physicalNeutral(keyboard.neutral());r.tick(now);return 0;});
#endif
    if(console_overload) {
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
      agon::extender::input::remoteLocked([](auto &r){r.cancel(agon::extender::input::RemoteKeyboard::transport);return 0;});
#endif
      if(!console_keys.releaseAll())s.fail("key release capacity");
      keyboard.lost([](agon::extender::input::ProcessedKey){});console_overload=false;
    }
#if defined(AGON_EXTENDER_PARALLEL_BOOT_CANDIDATE)
    }
#endif
    uart_event_t event;
    while(xQueueReceive(console_events,&event,0)==pdTRUE)
      if(event.type==UART_FIFO_OVF || event.type==UART_FRAME_ERR || event.type==UART_PARITY_ERR)
        s.fail("UART receive corruption");
    if(transmitting) {
      auto result=uart_wait_tx_done(UART_NUM_1,0);
      if(result==ESP_OK) {
        timing::Scope completed(timing::Phase::TxComplete);
        transmitting=false;
      }
      else if(result!=ESP_ERR_TIMEOUT)s.fail("TX completion");
      else if(now-tx_at>=5000) {
#if defined(AGON_EXTENDER_PARALLEL_BOOT_CANDIDATE)
        // The ordinary cancellation helper rebinds UART pads. The private
        // shared-bus owner must instead finish native cleanup and a NEW fence
        // before discarding queues; its boot recovery owns any later restore.
        s.fail("TX stalled");return;
#else
        console_cancel_tx();s.count=0;transmitting=false;s.session.cancel();s.parallel.cancel();
        console_keys.reset();keyboard.admissionBoundary();
        agon::extender::input::processedKeyboard().reset();
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
        agon::extender::input::remoteLocked([](auto &r){r.boundary(agon::extender::input::RemoteKeyboard::transport);return 0;});
#endif
        console_locale_pending=console_admit_pending=false;
        printf("ExCom UART blocked; awaiting fresh admission\n");
#endif
      }
    }
    // Stock's IDF writer refills available FIFO space before wire-idle.
    // Keep this owner nonblocking so its existing CTS-stall cancellation,
    // keyboard ordering and admission lifecycle can still run.
    if(s.count) {
      timing::Scope enqueue(timing::Phase::TxEnqueue, s.count);
      unsigned n=std::min<unsigned>(128,std::min<unsigned>(s.count,sizeof(s.output)-s.read_pos));
      int sent=uart_tx_chars(UART_NUM_1,reinterpret_cast<const char *>(s.output+s.read_pos),n);
      if (sent > 0) enqueue.units(static_cast<std::uint32_t>(sent));
      if(sent<0)s.fail("TX enqueue");
      else if(sent) {s.read_pos=(s.read_pos+sent)%sizeof(s.output);s.count-=sent;transmitting=true;tx_at=now;}
    }
#if defined(AGON_EXTENDER_PARALLEL_BOOT_CANDIDATE)
    if(blockDrain)return;
#endif
#if defined(AGON_EXTENDER_EXEXT_STREAM)
    if(s.parallelVdu.active()) {
      // Control has its own recognizer while VDU parameters/uploads remain in
      // the retained parser. A complete temporarily blocked OFFER/STOP stays
      // here while the outer parser consumes its ring; no byte is discarded.
      uint8_t b;
      if(used==3+CONSOLE_SIZE && consoleControl(processor,incoming+3))used=0;
      for(unsigned budget=0;used<3+CONSOLE_SIZE && budget<32 &&
          uart_read_bytes(UART_NUM_1,&b,1,0)==1;++budget) {
        if(!used) {if(b!=23){s.fail("non-control UART in ExExt");break;}partial_at=now;}
        incoming[used++]=b;
        if((used==2 && b!=0) || (used==3 && b!=CONSOLE_OPCODE)) {
          s.fail("invalid ExExt control carrier");break;
        }
        if(used==3+CONSOLE_SIZE) {
          if(consoleControl(processor,incoming+3))used=0;
          break;
        }
      }
      if(used && uint32_t(now-partial_at)>=1000)s.fail("ExExt control timeout");
    }
#endif
    if(!parseCommands)return;
    if(console_admit_pending && !s.count && !transmitting) {
      keyboard.admit();console_admit_pending=console_locale_pending=false;
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
      agon::extender::input::remoteLocked([&](auto &r){r.admit(keyboard.locale);return 0;});
#endif
      printf("ExCom native keyboard admitted\n");
    }
    // Stock send_packet admits its full reply before the next parser command.
    // A blocking read here must not strand a partial reply in software beyond
    // the peer's framing timeout. The final FIFO can drain independently.
    if(!s.count) {
      // Batch timing avoids timestamp/atomic overhead on each UART byte.
      // Context: 1 admitted ExCom, 0 preactivation. Counts are batch progress,
      // not a claim of complete commands, visible frames or eZ80 execution.
      timing::Scope parse(timing::Phase::Parser, s.session.active() ? 1 : 0);
#if defined(AGON_EXTENDER_FRAME_TIMING)
      const auto rx_before = s.diagnostic_rx_bytes;
#endif
      agon::extender::input::ProcessedKey key;
      bool have_key=!s.parallel.pending() && console_keys.pop(key);
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
      if(!have_key && !s.parallel.pending() && !s.count && !transmitting)
        have_key=agon::extender::input::remoteLocked([&](auto &r){return r.take(key,now);});
#endif
      if(have_key) {
        if(!agon::extender::input::processedKeyboard().push(key))s.fail("processed key queue");
        processor->processNext();
      } else if(s.session.active()) {
        unsigned budget=64;
        do {processor->processNext();} while(s.session.active() && !s.parallel.pending() && s.available() && !s.count && --budget);
      }
      else {
        uint8_t b;
        // Minimal preactivation recognizer: stock keyboard setup/poll exception
        // and fixed control envelope only. No ordinary VDU is reachable here.
        for(unsigned budget=0;budget<32 && uart_read_bytes(UART_NUM_1,&b,1,0)==1;++budget) {
          if(discard) { --discard;continue; }
          if(!used) {if(b!=23)continue;partial_at=now;need=3;}
          incoming[used++]=b;
          if(used==2 && b!=0){used=0;continue;}
          if(used==3) {
            if(b==CONSOLE_OPCODE)need=3+CONSOLE_SIZE;
#if defined(AGON_EXTENDER_SD_SERVICE)
            else if(b==0xF6)need=4;
#endif
#if defined(AGON_EXTENDER_TELEMETRY)
            else if(b==0xF5)need=4;
#endif
            else if(b==0x80 || b==0x81)need=4;
            else {used=0;continue;}
          }
#if defined(AGON_EXTENDER_SD_SERVICE)
          if(used==4 && incoming[2]==0xF6) {
            if(b<SD_HEADER || b>SD_MAX_RECORD) {discard=b;used=0;continue;}
            need=4+b;
          }
#endif
#if defined(AGON_EXTENDER_TELEMETRY)
          if(used==4 && incoming[2]==0xF5) {
            if(b!=agon::extender::telemetry::SnapshotSize) {discard=b;used=0;continue;}
            need=4+b;
          }
#endif
          if(used==need) {
            if(incoming[2]==CONSOLE_OPCODE)consoleControl(processor,incoming+3);
#if defined(AGON_EXTENDER_SD_SERVICE)
            else if(incoming[2]==0xF6)
              agon::extender::storage::sdReceive(incoming+4,incoming[3],now);
#endif
#if defined(AGON_EXTENDER_TELEMETRY)
            else if(incoming[2]==0xF5)
              agon::extender::telemetry::receive(incoming+4,incoming[3],now);
#endif
            else {s.feed(incoming);processor->processNext();}
            used=0;break;
          }
        }
        if((used || discard) && uint32_t(now-partial_at)>=250) {
#if defined(AGON_EXTENDER_SD_SERVICE)
          // A partial SD envelope has lost framing; require owned transport
          // recovery instead of interpreting its late body as console input.
          if(discard || (used>=3 && incoming[2]==0xF6))s.fail("incomplete SD envelope");
#endif
#if defined(AGON_EXTENDER_TELEMETRY)
          if(discard || (used>=3 && incoming[2]==0xF5))s.fail("incomplete telemetry envelope");
#endif
          used=discard=0;
        }
        // Cursor/event housekeeping still belongs to the retained processor.
        if(!used)processor->processNext();
      }
#if defined(AGON_EXTENDER_FRAME_TIMING)
      parse.units(s.diagnostic_rx_bytes - rx_before);
#endif
    }
    agon::extender::screen_text::poll(processor->getContext().get(), canvasW, canvasH);
#if defined(AGON_EXTENDER_PARALLEL_BOOT_CANDIDATE)
    if(s.parallel.pending())return;
#endif
    keyboard.repeat_delay=kbRepeatDelay;keyboard.repeat_rate=kbRepeatRate;
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
    agon::extender::input::remoteLocked([&](auto &r){r.repeat(kbRepeatDelay,kbRepeatRate);return 0;});
#endif
    keyboard.tick(now,emit);
    agon::extender::input::usbhost::setLeds(keyboard.ledState());
#if defined(AGON_EXTENDER_SD_SERVICE)
    // Service records wait behind complete keyboard/reply packets. Only this
    // task touches the UART queue; HTTP callbacks never send bytes themselves.
    if(!used && !discard && console_keys.empty() &&
       !s.count && !transmitting && !console_admit_pending) {
      uint8_t record[SD_MAX_RECORD];
      unsigned n=agon::extender::storage::sdTake(record,now);
      if(n) {
#if AGON_EXTENDER_ADMISSION_PROBE
        using namespace agon::extender::storage;
        portENTER_CRITICAL(&sd_mutex);auto inject=admission_probe.race;admission_probe.race=0;portEXIT_CRITICAL(&sd_mutex);
        if(inject) {const uint8_t key[]={0x81,4,'x',0,0,1};s.write(key,sizeof(key));}
#endif
        s.write(0x8D);s.write(uint8_t(n));s.write(record,n);
      }
    }
#endif
    if(agon::extender::input::processedKeyboard().queryFault())
      s.fail("virtual-key query queue overflow");
    if(s.failure) {
#if defined(AGON_EXTENDER_PARALLEL_BOOT_CANDIDATE)
      // Re-enter the physical owner at the top of the loop. Do not take the
      // ordinary UART-rebinding fault path on shared parallel/UART wiring.
      return;
#else
      s.parallel.cancel();
#if defined(AGON_EXTENDER_TELEMETRY)
      agon::extender::telemetry::reset();
#endif
#if defined(AGON_EXTENDER_REMOTE_KEYBOARD)
      agon::extender::input::remoteLocked([](auto &r){r.boundary(agon::extender::input::RemoteKeyboard::transport);return 0;});
#endif
      keyboard.pause();console_cancel_tx();
      ESP_ERROR_CHECK(uart_set_hw_flow_ctrl(UART_NUM_1,UART_HW_FLOWCTRL_CTS,0));
      ESP_ERROR_CHECK(uart_set_rts(UART_NUM_1,1));
      printf("ExCom fault: %s; reset P4 before retry\n",s.failure);
      for(;;)delay(1000);
#endif
    }
    // E07P: stock VDP 2.16.0 processLoop has no hardware-path sleep here.
    // Keep the same continuously serviced owner; unconditional delay delayed
    // newly queued replies. Existing stock-shaped IDLE watchdog policy remains.
  };
#if defined(AGON_EXTENDER_EXEXT_STREAM)
  s.progress=[&](){step(false);};
#endif
  for(;;)step(true);
}
