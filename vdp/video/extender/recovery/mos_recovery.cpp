/* Maintained P4 MOS recovery. Algorithm from agon-recovery commit
 * 95d68464afd049945e1dfd780c1c07621d565450 and the proven PORT-008 P4 adaptation.
 * This dedicated programmer deliberately excludes all product transports.
 * Never erases on boot: DUMP first, then RESTORE <exact payload SHA-256>.
 * See docs/mos-recovery.md. Historical signal/register ordering is preserved.
 */
#include <Arduino.h>
#include <array>
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <driver/gpio.h>
#include <driver/usb_serial_jtag.h>
#include <cstring>

#include "generated/mos_recovery_payload.hpp"

namespace {

using namespace agon_extender::diagnostic::recovery_payload;

constexpr uint8_t kZdiTckPin = 46;
constexpr uint8_t kZdiTdiPin = 47;
constexpr uint16_t kExpectedProductId = 0x0007;
constexpr uint8_t kExpectedRevision = 0xAA;
constexpr uint32_t kFlashAgentLoad = 0x040000;
constexpr uint32_t kMosLoad = 0x050000;
constexpr uint32_t kMosSizeAddress = 0x070000;
constexpr uint32_t kDoneAddress = 0x070003;
constexpr size_t kChunkSize = 256; // Yield between short ZDI bursts for IDF idle tasks.

// eZ80F92 I/O addresses copied from the same agon-recovery authority.
constexpr uint8_t kTmr0Ctl = 0x80;
constexpr uint8_t kTmr1Ctl = 0x83;
constexpr uint8_t kTmr2Ctl = 0x86;
constexpr uint8_t kTmr3Ctl = 0x89;
constexpr uint8_t kTmr4Ctl = 0x8C;
constexpr uint8_t kTmr5Ctl = 0x8F;
constexpr uint8_t kPbDdr = 0x9B;
constexpr uint8_t kPbAlt1 = 0x9C;
constexpr uint8_t kPbAlt2 = 0x9D;
constexpr uint8_t kPcDdr = 0x9F;
constexpr uint8_t kPcAlt1 = 0xA0;
constexpr uint8_t kPcAlt2 = 0xA1;
constexpr uint8_t kPdDdr = 0xA3;
constexpr uint8_t kPdAlt1 = 0xA4;
constexpr uint8_t kPdAlt2 = 0xA5;
constexpr uint8_t kCs0Lbr = 0xA8;
constexpr uint8_t kCs0Ubr = 0xA9;
constexpr uint8_t kCs0Ctl = 0xAA;
constexpr uint8_t kCs1Ctl = 0xAD;
constexpr uint8_t kCs2Ctl = 0xB0;
constexpr uint8_t kCs3Ctl = 0xB3;
constexpr uint8_t kRamCtl = 0xB4;
constexpr uint8_t kRamAddrU = 0xB5;
constexpr uint8_t kSpiCtl = 0xBA;
constexpr uint8_t kUart0Ier = 0xC1;
constexpr uint8_t kI2cCtl = 0xCB;
constexpr uint8_t kUart1Ier = 0xD1;
constexpr uint8_t kRtcCtrl = 0xED;
constexpr uint8_t kCs0Bmc = 0xF0;
constexpr uint8_t kFlashAddrU = 0xF7;
constexpr uint8_t kFlashCtrl = 0xF8;
constexpr uint8_t kFlashIrq = 0xFB;

static_assert(kMosSize > 0 && kMosSize <= 131072);
static_assert(kFlashAgentSize == 90);

void report(const char* format, ...) {
  char text[1024];
  va_list arguments;
  va_start(arguments, format);
  int n = vsnprintf(text, sizeof(text), format, arguments);
  va_end(arguments);
  if (n < 0 || n >= static_cast<int>(sizeof(text))) {
    while (true) delay(1000);
  }
  // Own USB Serial/JTAG explicitly; historical stdin/Arduino Serial did not
  // deliver input reliably. A failed output halts progression, never retries erase.
  if (usb_serial_jtag_write_bytes(text, n, pdMS_TO_TICKS(2000)) != n) {
    while (true) delay(1000);
  }
}

class Crc32 {
 public:
  void update(const uint8_t* data, size_t size) {
    while (size-- != 0) {
      value_ ^= *data++;
      for (int bit = 0; bit < 8; ++bit) {
        value_ = (value_ >> 1) ^
                 ((value_ & 1U) != 0 ? 0xEDB88320U : 0U);
      }
    }
  }
  uint32_t finish() const { return ~value_; }

 private:
  uint32_t value_ = 0xFFFFFFFFU;
};

uint32_t crc32(const uint8_t* data, size_t size) {
  Crc32 crc;
  crc.update(data, size);
  return crc.finish();
}

class Zdi {
 public:
  enum class Register : uint8_t {
    IdLow = 0x00,
    IdRevision = 0x02,
    Status = 0x03,
    BreakControl = 0x10,
    WriteDataLow = 0x13,
    ReadWriteControl = 0x16,
    Instruction2 = 0x23,
    Instruction1 = 0x24,
    Instruction0 = 0x25,
    ReadLow = 0x10,
    ReadMemory = 0x20,
    WriteMemory = 0x30,
  };

  enum class CpuRegister : uint8_t {
    AfMb = 0,
    Bc = 1,
    De = 2,
    Hl = 3,
    Ix = 4,
    Iy = 5,
    Sp = 6,
    Pc = 7,
    SetAdl = 8,
  };

  void begin() {
    gpio_set_level(static_cast<gpio_num_t>(kZdiTckPin), 1);
    gpio_config_t tck = {
        .pin_bit_mask = 1ULL << kZdiTckPin,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&tck);
    gpio_config_t tdi = {
        .pin_bit_mask = 1ULL << kZdiTdiPin,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&tdi);
  }

  uint8_t readRegister(Register reg) {
    uint8_t value = 0;
    readRegisters(reg, 1, &value);
    return value;
  }

  void readRegisters(Register reg, uint8_t count, uint8_t* values) {
    noInterrupts();
    signalStart();
    addressRegister(static_cast<uint8_t>(reg), true);
    while (count-- != 0) {
      signalContinue();
      delayMicroseconds(3);
      *values++ = readByte();
    }
    signalDone();
    delayMicroseconds(3);
    interrupts();
  }

  void writeRegister(Register reg, uint8_t value) {
    writeRegisters(reg, 1, &value);
  }

  void writeRegisters(Register reg, uint8_t count, const uint8_t* values) {
    noInterrupts();
    signalStart();
    addressRegister(static_cast<uint8_t>(reg), false);
    while (count-- != 0) {
      signalContinue();
      delayMicroseconds(3);
      writeByte(*values++);
    }
    signalDone();
    delayMicroseconds(3);
    interrupts();
  }

  uint16_t productId() {
    uint8_t bytes[2] = {};
    readRegisters(Register::IdLow, 2, bytes);
    return static_cast<uint16_t>(bytes[0]) |
           (static_cast<uint16_t>(bytes[1]) << 8);
  }

  uint8_t revision() { return readRegister(Register::IdRevision); }
  uint8_t status() { return readRegister(Register::Status); }
  void halt() { writeRegister(Register::BreakControl, 0x80); }
  void resume() { writeRegister(Register::BreakControl, 0x00); }

  uint32_t readCpuRegister(CpuRegister reg) {
    writeRegister(Register::ReadWriteControl, static_cast<uint8_t>(reg));
    if (reg == CpuRegister::SetAdl) {
      return 0;
    }
    uint8_t bytes[3] = {};
    readRegisters(Register::ReadLow, 3, bytes);
    return static_cast<uint32_t>(bytes[0]) |
           (static_cast<uint32_t>(bytes[1]) << 8) |
           (static_cast<uint32_t>(bytes[2]) << 16);
  }

  void writeCpuRegister(CpuRegister reg, uint32_t value) {
    const uint8_t bytes[3] = {
        static_cast<uint8_t>(value),
        static_cast<uint8_t>(value >> 8),
        static_cast<uint8_t>(value >> 16),
    };
    writeRegisters(Register::WriteDataLow, 3, bytes);
    writeRegister(Register::ReadWriteControl,
                  static_cast<uint8_t>(reg) | 0x80);
  }

  void readMemory(uint32_t address, size_t count, uint8_t* output) {
    writeCpuRegister(CpuRegister::Pc, address);
    noInterrupts();
    signalStart();
    addressRegister(static_cast<uint8_t>(Register::ReadMemory), true);
    while (count-- != 0) {
      signalContinue();
      delayMicroseconds(3);
      *output++ = readByte();
    }
    signalDone();
    delayMicroseconds(3);
    interrupts();
  }

  void writeMemory(uint32_t address, size_t count, const uint8_t* input) {
    writeCpuRegister(CpuRegister::Pc, address);
    noInterrupts();
    signalStart();
    addressRegister(static_cast<uint8_t>(Register::WriteMemory), false);
    while (count-- != 0) {
      signalContinue();
      delayMicroseconds(3);
      writeByte(*input++);
    }
    signalDone();
    delayMicroseconds(3);
    interrupts();
  }

  void writeMemory24(uint32_t address, uint32_t value) {
    const uint8_t bytes[3] = {
        static_cast<uint8_t>(value),
        static_cast<uint8_t>(value >> 8),
        static_cast<uint8_t>(value >> 16),
    };
    writeMemory(address, sizeof(bytes), bytes);
  }

  void injectOut(uint8_t port, uint8_t value) {
    writeRegister(Register::Instruction1, value);
    writeRegister(Register::Instruction0, 0x3E);  // LD A,value
    writeRegister(Register::Instruction1, port);
    writeRegister(Register::Instruction0, 0xD3);  // OUT (port),A
  }

  void disableInterrupts() { writeRegister(Register::Instruction0, 0xF3); }

 private:
  void signalStart() {
    gpio_set_level(static_cast<gpio_num_t>(kZdiTdiPin), 1);
    gpio_set_direction(static_cast<gpio_num_t>(kZdiTdiPin), GPIO_MODE_OUTPUT);
    gpio_set_level(static_cast<gpio_num_t>(kZdiTckPin), 1);
    gpio_set_level(static_cast<gpio_num_t>(kZdiTdiPin), 0);
  }
  void signalContinue() { writeBit(false); }
  void signalDone() { writeBit(true); }
  void writeBit(bool value) {
    gpio_set_level(static_cast<gpio_num_t>(kZdiTckPin), 0);
    gpio_set_level(static_cast<gpio_num_t>(kZdiTdiPin), value ? 1 : 0);
    gpio_set_direction(static_cast<gpio_num_t>(kZdiTdiPin), GPIO_MODE_OUTPUT);
    gpio_set_level(static_cast<gpio_num_t>(kZdiTckPin), 1);
  }
  bool readBit() {
    gpio_set_level(static_cast<gpio_num_t>(kZdiTckPin), 0);
    gpio_set_direction(static_cast<gpio_num_t>(kZdiTdiPin), GPIO_MODE_INPUT);
    const bool value =
        gpio_get_level(static_cast<gpio_num_t>(kZdiTdiPin)) != 0;
    gpio_set_level(static_cast<gpio_num_t>(kZdiTckPin), 1);
    return value;
  }
  void addressRegister(uint8_t reg, bool read) {
    for (int bit = 6; bit >= 0; --bit) {
      writeBit((reg & (1U << bit)) != 0);
    }
    writeBit(read);
  }
  void writeByte(uint8_t value) {
    for (int bit = 7; bit >= 0; --bit) {
      writeBit((value & (1U << bit)) != 0);
    }
  }
  uint8_t readByte() {
    uint8_t value = 0;
    for (int bit = 7; bit >= 0; --bit) {
      value = static_cast<uint8_t>((value << 1) | (readBit() ? 1U : 0U));
    }
    return value;
  }
};

Zdi zdi;
std::array<uint8_t, kChunkSize> scratch;

void initializeEz80() {
  zdi.halt();
  zdi.readCpuRegister(Zdi::CpuRegister::SetAdl);
  zdi.disableInterrupts();
  zdi.injectOut(kSpiCtl, 0x04);
  for (const uint8_t port : {kPbDdr, kPcDdr, kPdDdr}) zdi.injectOut(port, 0xFF);
  for (const uint8_t port : {kPbAlt1, kPcAlt1, kPdAlt1,
                             kPbAlt2, kPcAlt2, kPdAlt2}) zdi.injectOut(port, 0);
  for (const uint8_t port : {kTmr0Ctl, kTmr1Ctl, kTmr2Ctl,
                             kTmr3Ctl, kTmr4Ctl, kTmr5Ctl,
                             kUart0Ier, kUart1Ier, kI2cCtl,
                             kFlashIrq, kRtcCtrl}) zdi.injectOut(port, 0);
  zdi.injectOut(kSpiCtl, 0x04);
  zdi.injectOut(kFlashAddrU, 0x00);
  zdi.injectOut(kFlashCtrl, 0x28);
  zdi.injectOut(kRamAddrU, 0xB7);
  zdi.injectOut(kRamCtl, 0x80);
  zdi.injectOut(kCs0Lbr, 0x04);
  zdi.injectOut(kCs0Ubr, 0x0B);
  zdi.injectOut(kCs0Bmc, 0x01);
  zdi.injectOut(kCs0Ctl, 0x08);
  zdi.injectOut(kCs1Ctl, 0x00);
  zdi.injectOut(kCs2Ctl, 0x00);
  zdi.injectOut(kCs3Ctl, 0x00);
  zdi.writeCpuRegister(Zdi::CpuRegister::Sp, 0x0BFFFF);
  zdi.writeCpuRegister(Zdi::CpuRegister::Pc, 0x000000);
}

void upload(uint32_t address, const uint8_t* data, size_t size) {
  size_t done = 0;
  while (done < size) {
    const size_t count = min(kChunkSize, size - done);
    zdi.writeMemory(address + done, count, data + done);
    done += count;
    delay(1);
    if ((done % (16 * kChunkSize)) == 0 || done == size) {
      report("  uploaded %u/%u bytes\n", static_cast<unsigned>(done),
             static_cast<unsigned>(size));
    }
  }
}

uint32_t memoryCrc(uint32_t address, size_t size) {
  Crc32 crc;
  size_t done = 0;
  while (done < size) {
    const size_t count = min(kChunkSize, size - done);
    zdi.readMemory(address + done, count, scratch.data());
    crc.update(scratch.data(), count);
    done += count;
    delay(1);
  }
  return crc.finish();
}

[[noreturn]] void stopPassive(const char* reason) {
  // This path is used before recovery owns the target.  In particular, an
  // identity mismatch must not turn a failed read-only gate into an eZ80 halt.
  report("\nRECOVERY REFUSED: %s\nTarget eZ80 was not deliberately halted.\n",
         reason);
  while (true) delay(1000);
}

[[noreturn]] void stopHalted(const char* reason) {
  zdi.halt();
  report("\nRECOVERY STOP/FAIL: %s\nTarget eZ80 remains halted.\n", reason);
  while (true) delay(1000);
}

bool command(const char* expected, unsigned seconds) {
  char line[100] = {};
  size_t used = 0;
  const uint32_t started = millis();
  uint32_t announce = 0;
  while (millis() - started < seconds * 1000U) {
    if (millis() - announce > 2000) {
      report("WAIT %s\n", expected);
      announce = millis();
    }
    char ch;
    if (usb_serial_jtag_read_bytes(&ch, 1, pdMS_TO_TICKS(20)) != 1) continue;
    if (ch == '\r') continue;
    if (ch == '\n') {
      line[used] = 0;
      if (strcmp(line, expected) == 0) return true;
      report("COMMAND REFUSED\n");
      used = 0;
    } else if (used + 1 < sizeof(line)) {
      line[used++] = ch;
    } else return false;
  }
  return false;
}

uint32_t dumpFlash(const char* label, bool compare) {
  Crc32 crc;
  report("DUMP BEGIN %s 131072\n", label);
  for (uint32_t address = 0; address < 131072; address += kChunkSize) {
    zdi.readMemory(address, scratch.size(), scratch.data());
    crc.update(scratch.data(), scratch.size());
    char hex[kChunkSize * 2 + 1];
    for (size_t i = 0; i < scratch.size(); ++i) {
      snprintf(hex + i * 2, 3, "%02X", scratch[i]);
      uint8_t expected = address + i < kMosSize ? kMosImage[address + i] : 0xFF;
      if (compare && scratch[i] != expected) stopHalted("flash byte comparison failed");
    }
    report("DATA %s %06lX %s\n", label, static_cast<unsigned long>(address), hex);
    delay(1);
  }
  report("DUMP END %s %08lX\n", label, static_cast<unsigned long>(crc.finish()));
  return crc.finish();
}

[[noreturn]] void recover() {
  if (crc32(kMosImage, kMosSize) != kMosCrc32 ||
      crc32(kFlashAgent, kFlashAgentSize) != kFlashAgentCrc32) {
    stopPassive("embedded payload CRC mismatch before target mutation");
  }

  initializeEz80();
  zdi.writeMemory24(kDoneAddress, 0);
  report("Uploading corrected EMOS to eZ80 RAM...\n");
  upload(kMosLoad, kMosImage, kMosSize);
  if (memoryCrc(kMosLoad, kMosSize) != kMosCrc32) {
    stopHalted("EMOS RAM upload CRC mismatch; flash agent not started");
  }
  report("EMOS RAM CRC32 PASS: %08lX\n", static_cast<unsigned long>(kMosCrc32));

  zdi.writeMemory24(kMosSizeAddress, kMosSize);
  report("Uploading upstream 90-byte flash agent...\n");
  upload(kFlashAgentLoad, kFlashAgent, kFlashAgentSize);
  if (memoryCrc(kFlashAgentLoad, kFlashAgentSize) != kFlashAgentCrc32) {
    stopHalted("flash-agent RAM upload CRC mismatch; flash agent not started");
  }

  report("Executing upstream flash agent; no ZDI access for 10 seconds...\n");
  zdi.writeCpuRegister(Zdi::CpuRegister::Pc, kFlashAgentLoad);
  zdi.resume();
  delay(10000);
  zdi.halt();

  uint8_t done = 0;
  zdi.readMemory(kDoneAddress, 1, &done);
  if (done != 1) {
    stopHalted("flash agent did not set completion acknowledgement");
  }
  report("Flash agent acknowledged completion; verifying eZ80 flash...\n");
  if (memoryCrc(0, kMosSize) != kMosCrc32) {
    stopHalted("programmed eZ80 flash CRC mismatch");
  }

  dumpFlash("after", true);
  report("\nRECOVERY PASS\n");
  report("Programmed %u bytes; CRC32 %08lX; SHA-256 %s\n",
         static_cast<unsigned>(kMosSize),
         static_cast<unsigned long>(kMosCrc32), kMosSha256);
  report("Target eZ80 remains halted. Physically reset the Agon to boot EMOS.\n");
  while (true) delay(1000);
}

}  // namespace

void setup() {
  // The Author keeps the normal harness connected. Recovery owns no product
  // transport: explicitly release every r03 parallel/UART/control endpoint,
  // including the separate keyboard UART pair, before touching ZDI. No pulls
  // or output drivers may contend with the eZ80 or existing external bias.
  constexpr uint64_t harness = (1ULL<<9)|(1ULL<<10)|(1ULL<<11)|(1ULL<<12)|
      (1ULL<<13)|(1ULL<<14)|(1ULL<<15)|(1ULL<<17)|(1ULL<<20)|(1ULL<<21)|
      (1ULL<<22)|(1ULL<<23)|(1ULL<<26)|(1ULL<<27)|(1ULL<<32)|(1ULL<<33);
  gpio_config_t released = {.pin_bit_mask=harness, .mode=GPIO_MODE_INPUT,
      .pull_up_en=GPIO_PULLUP_DISABLE, .pull_down_en=GPIO_PULLDOWN_DISABLE,
      .intr_type=GPIO_INTR_DISABLE};
  if (gpio_config(&released) != ESP_OK) while (true) delay(1000);
  if (!usb_serial_jtag_is_driver_installed()) {
    usb_serial_jtag_driver_config_t config = {.tx_buffer_size=4096, .rx_buffer_size=256};
    if (usb_serial_jtag_driver_install(&config) != ESP_OK) while(true) delay(1000);
  }
  zdi.begin();
  delay(1000);
  report("\nMaintained P4 MOS recovery r01 - no flash writes without host arming\n");
  report("Normal harness endpoints released as inputs; only ZDI GPIO46/47 driven.\n");
  report("Payload %u bytes SHA256 %s CRC32 %08lX\n", static_cast<unsigned>(kMosSize),
         kMosSha256, static_cast<unsigned long>(kMosCrc32));
  if (crc32(kMosImage, kMosSize) != kMosCrc32 ||
      crc32(kFlashAgent, kFlashAgentSize) != kFlashAgentCrc32)
    stopPassive("embedded payload CRC mismatch");
  for (int probe = 1; probe <= 3; ++probe) {
    uint16_t product = zdi.productId();
    uint8_t revision = zdi.revision();
    report("Identity %d product=%04X revision=%02X status=%02X\n", probe, product, revision, zdi.status());
    if (product != kExpectedProductId || revision != kExpectedRevision)
      stopPassive("ZDI identity gate failed");
    delay(100);
  }
  if (!command("DUMP", 300)) stopPassive("DUMP not armed before timeout");
  zdi.halt();
  if (!(zdi.status() & 0x80)) stopHalted("target did not halt");
  report("HALTED PC=%06lX\n", static_cast<unsigned long>(zdi.readCpuRegister(Zdi::CpuRegister::Pc)));
  zdi.readCpuRegister(Zdi::CpuRegister::SetAdl);
  dumpFlash("before", false);
  char expected[90];
  snprintf(expected, sizeof(expected), "RESTORE %s", kMosSha256);
  if (!command(expected, 300)) stopHalted("RESTORE not armed before timeout; flash not written");
  // Recheck the physical target in this halt epoch, immediately before mutation.
  if (zdi.productId() != kExpectedProductId || zdi.revision() != kExpectedRevision)
    stopHalted("target identity changed after dump");
  recover();
}

void loop() { delay(1000); }
