// Adopted Stream for retained VDP parsing; one process task owns RX and TX.
#pragma once
#include <Stream.h>
#include <driver/uart.h>
#include <cstring>
#include "console_session.hpp"
#include "../input/processed_keyboard.hpp"
class ConsoleStream final : public Stream {
 public:
  agon::extender::transport::ConsoleSession session;
  uint8_t setup[4]{},output[8192]{};
  unsigned pos{4},read_pos{},count{};
  int cached{-1};
#if defined(AGON_EXTENDER_FRAME_TIMING)
  // Parser-owner-only counter; no atomic/timestamp operation per UART byte.
  uint32_t diagnostic_rx_bytes{};
#endif
  const char *failure{};
  void fail(const char *why) { if (!failure) failure=why; }
  void feed(const uint8_t *p) { std::memcpy(setup,p,4);pos=0; }
  int available() override {
    if (pos<4) return 4-pos;
    size_t n=0;if(session.active()) uart_get_buffered_data_len(UART_NUM_1,&n);
    return int(n)+(cached>=0);
  }
  int read() override {
    if(pos<4) return setup[pos++];
    if(cached>=0) {int b=cached;cached=-1;return b;}
    uint8_t b;
    const bool received=session.active() && uart_read_bytes(UART_NUM_1,&b,1,0)==1;
#if defined(AGON_EXTENDER_FRAME_TIMING)
    if (received) ++diagnostic_rx_bytes;
#endif
    return received ? b : -1;
  }
  // Stock HardwareSerial overrides Stream's byte-at-a-time fallback with an
  // IDF block read. Preserve that path through this lease/setup/peek adapter;
  // buffer uploads otherwise pay UART-driver/timer overhead for every byte.
  size_t readBytes(uint8_t *p, size_t n) override {
    if (!p || !n) return 0;
    size_t used = 0;
    while (pos < 4 && used < n) p[used++] = setup[pos++];
    if (cached >= 0 && used < n) { p[used++] = uint8_t(cached); cached = -1; }
    if (used == n || !session.active()) return used;
    const int got = uart_read_bytes(UART_NUM_1, p + used, n - used,
                                    pdMS_TO_TICKS(getTimeout()));
    if (got > 0) {
#if defined(AGON_EXTENDER_FRAME_TIMING)
      diagnostic_rx_bytes += got;
#endif
      used += size_t(got);
    }
    return used;
  }
  size_t readBytes(char *p, size_t n) override {
    return readBytes(reinterpret_cast<uint8_t *>(p), n);
  }
  int peek() override { if(pos<4)return setup[pos];if(cached<0)cached=read();return cached; }
  void flush() override { /* Stream flush does not cancel pending UART bytes. */ }
  size_t write(uint8_t b) override {
    if(count==sizeof(output)) { fail("reply queue overflow");return 0; }
    output[(read_pos+count)%sizeof(output)]=b;++count;return 1;
  }
  size_t write(const uint8_t *p,size_t n) override {size_t i=0;while(i<n && write(p[i]))++i;return i;}
};
class VDUStreamProcessor;
ConsoleStream *beginConsole();
void runConsole(VDUStreamProcessor *);
void consoleControl(VDUStreamProcessor *, const uint8_t *p);
void consoleLayout(int region);
void consolePoll();
inline void setVDPProtocolDuplex(bool) { /* UART1 is full duplex for this composition. */ }
