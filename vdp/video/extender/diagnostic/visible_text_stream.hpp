// PORT-014 repeatable qualification binding; no product mode activation.
#pragma once
#include <Stream.h>
#include "visible_text_transaction.hpp"
class VDUStreamProcessor;
class VisibleTextStream final : public Stream {
 public:
  VisibleTextTransaction transaction;
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
VisibleTextStream *beginVisibleTextQualification();
void runVisibleTextQualification(VDUStreamProcessor *processor);
void rejectVisibleTextDuplexChange();
inline void setVDPProtocolDuplex(bool) { rejectVisibleTextDuplexChange(); }
