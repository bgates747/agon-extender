// PORT-013 one-shot qualification binding; no product mode activation.
#pragma once
#include <Stream.h>
#include "general_poll_transaction.hpp"
class VDUStreamProcessor;
class GeneralPollStream final : public Stream {
 public:
  GeneralPollTransaction transaction;
  int available() override { return transaction.available(); }
  int read() override { return transaction.read(); }
  int peek() override { return transaction.peek(); }
  void flush() override { transaction.fail("unexpected flush"); }
  size_t write(uint8_t b) override { return transaction.write(b); }
  size_t write(const uint8_t *p,size_t n) override {
    size_t i=0; for (;i<n && write(p[i]);++i) {} return i;
  }
};
// VDUStreamProcessor adopts the returned heap Stream. The process task alone
// owns the transaction after construction; no concurrent UART/parser consumer.
GeneralPollStream *beginGeneralPollQualification();
void runGeneralPollQualification(VDUStreamProcessor *processor);
void rejectGeneralPollDuplexChange();
inline void setVDPProtocolDuplex(bool) { rejectGeneralPollDuplexChange(); }
