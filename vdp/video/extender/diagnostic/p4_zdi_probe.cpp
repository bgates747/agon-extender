/*
 * PORT-008 TEMPORARY HARDWARE-FAILURE DIAGNOSTIC — NOT PRODUCT FIRMWARE.
 *
 * This image makes an electrically isolated Olimex ESP32-P4-DevKit an
 * external ZDI observer for an Agon Light 2. It exists because running the
 * agon-recovery diagnostic on the target's onboard ESP32 replaces the stock
 * VDP and therefore destroys the failed configuration we need to observe.
 *
 * ZDI wire protocol and register operations are a deliberately narrow P4 port
 * of envenomator/agon-recovery commit
 * 95d68464afd049945e1dfd780c1c07621d565450. The original utility targets a
 * classic ESP32 and uses chip-specific direct-GPIO helpers. This diagnostic
 * substitutes portable Arduino GPIO calls and retains the original 1 us bit
 * pacing. The failed-state addresses are bound to the PORT-008 EMOS candidate
 * from agon-emos commit 59c3102; do not use this image against another build
 * and interpret the named RAM locations as though they were compatible.
 *
 * Safety boundary:
 *   - startup performs ZDI identity reads only;
 *   - operator command 'c' intentionally halts the target eZ80;
 *   - the capture reads registers, RAM, and selected I/O status;
 *   - the target remains halted and must be physically reset afterward;
 *   - this image contains no flash, reset, memory-write, or resume command.
 */

#include <Arduino.h>
#include <cstdarg>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <driver/gpio.h>
#include <fcntl.h>
#include <unistd.h>

namespace {

constexpr uint8_t kZdiTckPin = 46;
constexpr uint8_t kZdiTdiPin = 47;
constexpr uint16_t kExpectedProductId = 0x0007;

constexpr uint32_t kScrColoursAddress = 0x0BC31D;
constexpr uint32_t kGpAddress = 0x0BC33F;
constexpr uint32_t kUart0VectorPointerAddress = 0x000118;
constexpr uint32_t kUart0FirstJumpAddress = 0x000190;
constexpr uint32_t kUart0SecondJumpAddress = 0x0BD6CD;
constexpr uint32_t kSysClkFreqAddress = 0x001BA7;

constexpr uint8_t kTimer0Control = 0x80;
constexpr uint8_t kTimer0DataLow = 0x81;
constexpr uint8_t kTimer0DataHigh = 0x82;
constexpr uint8_t kPortDData = 0xA2;
constexpr uint8_t kPortDDirection = 0xA3;
constexpr uint8_t kPortDAlt1 = 0xA4;
constexpr uint8_t kPortDAlt2 = 0xA5;
constexpr uint8_t kUart0Ier = 0xC1;
constexpr uint8_t kUart0Iir = 0xC2;
constexpr uint8_t kUart0DivisorLow = 0xC0;
constexpr uint8_t kUart0DivisorHigh = 0xC1;
constexpr uint8_t kUart0Lcr = 0xC3;
constexpr uint8_t kUart0Mcr = 0xC4;
constexpr uint8_t kUart0Lsr = 0xC5;
constexpr uint8_t kUart0Msr = 0xC6;

#ifndef AGON_EXTENDER_P4_ZDI_AUTO_CAPTURE
#define AGON_EXTENDER_P4_ZDI_AUTO_CAPTURE 0
#endif

#ifndef AGON_EXTENDER_P4_ZDI_HALTED_SUPPLEMENT
#define AGON_EXTENDER_P4_ZDI_HALTED_SUPPLEMENT 0
#endif

class UsbSerialJtagConsole {
 public:
  void begin() {
    // ESP-IDF registers stdin/stdout on the P4's USB Serial/JTAG console
    // before Arduino setup() runs. Arduino Serial is a different peripheral
    // on this board and silently hid the first diagnostic build's output.
    setvbuf(stdout, nullptr, _IONBF, 0);
    const int flags = fcntl(STDIN_FILENO, F_GETFL, 0);
    if (flags >= 0) {
      fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK);
    }
  }

  void printf(const char* format, ...) {
    va_list arguments;
    va_start(arguments, format);
    vprintf(format, arguments);
    va_end(arguments);
  }

  void println() { putchar('\n'); }

  void println(const char* text) { puts(text); }

  int read() {
    uint8_t value = 0;
    return ::read(STDIN_FILENO, &value, 1) == 1 ? value : -1;
  }
};

UsbSerialJtagConsole console;

class Zdi {
 public:
  enum class Register : uint8_t {
    BreakControl = 0x10,
    WriteDataLow = 0x13,
    ReadWriteControl = 0x16,
    Instruction2 = 0x23,
    Instruction1 = 0x24,
    Instruction0 = 0x25,
    IdLow = 0x00,
    IdRevision = 0x02,
    Status = 0x03,
    ReadLow = 0x10,
    ReadMemory = 0x20,
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
  };

  void begin() {
    // Preload TCK high before enabling its output driver. This preserves the
    // recovery utility's glitch-free idle transition without relying on
    // Arduino digitalWrite(), which P4 rejects before pinMode(OUTPUT).
    gpio_set_level(static_cast<gpio_num_t>(kZdiTckPin), 1);
    gpio_config_t tckConfig = {
        .pin_bit_mask = 1ULL << kZdiTckPin,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&tckConfig);

    gpio_config_t tdiConfig = {
        .pin_bit_mask = 1ULL << kZdiTdiPin,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&tdiConfig);
  }

  int idleDataLevel() const {
    return gpio_get_level(static_cast<gpio_num_t>(kZdiTdiPin));
  }

  uint8_t readRegister(Register reg) {
    uint8_t value = 0;
    noInterrupts();
    signalStart();
    addressRegister(static_cast<uint8_t>(reg), true);
    signalContinue();
    value = readByte();
    signalDone();
    delayMicroseconds(3);
    interrupts();
    return value;
  }

  void readRegisters(Register reg, uint8_t count, uint8_t* values) {
    noInterrupts();
    signalStart();
    addressRegister(static_cast<uint8_t>(reg), true);
    while (count-- != 0) {
      signalContinue();
      *values++ = readByte();
    }
    signalDone();
    delayMicroseconds(3);
    interrupts();
  }

  void writeRegister(Register reg, uint8_t value) {
    noInterrupts();
    signalStart();
    addressRegister(static_cast<uint8_t>(reg), false);
    signalContinue();
    writeByte(value);
    signalDone();
    delayMicroseconds(3);
    interrupts();
  }

  void writeRegisters(Register reg, uint8_t count, const uint8_t* values) {
    noInterrupts();
    signalStart();
    addressRegister(static_cast<uint8_t>(reg), false);
    while (count-- != 0) {
      signalContinue();
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
           static_cast<uint16_t>(bytes[1] << 8);
  }

  uint8_t revision() { return readRegister(Register::IdRevision); }

  uint8_t status() { return readRegister(Register::Status); }

  void halt() { writeRegister(Register::BreakControl, 0x80); }

  uint32_t readCpuRegister(CpuRegister reg) {
    writeRegister(Register::ReadWriteControl, static_cast<uint8_t>(reg));
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

  void readMemory(uint32_t address, uint32_t count, uint8_t* output) {
    const uint32_t oldPc = readCpuRegister(CpuRegister::Pc);
    writeCpuRegister(CpuRegister::Pc, address);

    noInterrupts();
    signalStart();
    addressRegister(static_cast<uint8_t>(Register::ReadMemory), true);
    for (uint32_t i = 0; i < count; ++i) {
      signalContinue();
      delayMicroseconds(3);
      *output++ = readByte();
    }
    signalDone();
    delayMicroseconds(3);
    interrupts();

    writeCpuRegister(CpuRegister::Pc, oldPc);
  }

  uint8_t readIo(uint8_t port) {
    // Inject IN0 A,(port). This changes AF and status reads may have normal
    // peripheral side effects, so architectural registers are captured first.
    writeRegister(Register::Instruction2, port);
    writeRegister(Register::Instruction1, 0x38);
    writeRegister(Register::Instruction0, 0xED);
    return static_cast<uint8_t>(readCpuRegister(CpuRegister::AfMb));
  }

  void writeIo(uint8_t port, uint8_t value) {
    // Inject OUT0 (port),A. This is used only by the halted-target UART
    // supplement, which saves and restores both AF/MB and UART0 LCR around the
    // divisor-latch read. It is deliberately not exposed as a console command.
    const uint32_t oldAfMb = readCpuRegister(CpuRegister::AfMb);
    writeCpuRegister(CpuRegister::AfMb,
                     (oldAfMb & 0xFFFF00U) | static_cast<uint32_t>(value));
    writeRegister(Register::Instruction2, port);
    writeRegister(Register::Instruction1, 0x39);
    writeRegister(Register::Instruction0, 0xED);
    writeCpuRegister(CpuRegister::AfMb, oldAfMb);
  }

 private:
  void signalStart() {
    // Match agon-recovery's ordering exactly: preload ZDA high, enable its
    // output driver, hold ZCL high, then create the START falling edge.
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
    for (int bit = 0; bit < 8; ++bit) {
      value = static_cast<uint8_t>((value << 1) | (readBit() ? 1 : 0));
    }
    return value;
  }
};

Zdi zdi;
bool captureComplete = false;

void printHexDump(const char* label, uint32_t address, const uint8_t* bytes,
                  size_t count);

bool matchesCapturedCandidateWaitState() {
  // Never touch UART state merely because some eZ80 happens to be halted.
  // These bytes and address identify agon-emos commit 59c3102's inherited
  // _wait_timer0 routine, which the first valid capture found at PC 0x0009EA.
  constexpr uint32_t kExpectedPc = 0x0009EA;
  constexpr uint32_t kWaitRoutineAddress = 0x0009E0;
  constexpr uint8_t kWaitRoutine[] = {
      0xF5, 0xC5, 0xED, 0x38, 0x80, 0xF6, 0x03, 0xED, 0x39, 0x80, 0xED,
      0x00, 0x81, 0xED, 0x38, 0x82, 0xB0, 0x20, 0xF7, 0xC1, 0xF1, 0xC9,
  };

  const uint32_t observedPc =
      zdi.readCpuRegister(Zdi::CpuRegister::Pc);
  if (observedPc != kExpectedPc) {
    console.printf(
        "UART DIVISOR GATE: observed PC=%06lX, expected PC=%06lX.\n",
        static_cast<unsigned long>(observedPc),
        static_cast<unsigned long>(kExpectedPc));
    return false;
  }
  uint8_t actual[sizeof(kWaitRoutine)] = {};
  zdi.readMemory(kWaitRoutineAddress, sizeof(actual), actual);
  if (memcmp(actual, kWaitRoutine, sizeof(actual)) != 0) {
    printHexDump("UART DIVISOR GATE: observed wait routine",
                 kWaitRoutineAddress, actual, sizeof(actual));
    return false;
  }
  return true;
}

bool inspectHaltedUartDivisor() {
  if (!matchesCapturedCandidateWaitState()) {
    console.println(
        "UART DIVISOR READ REFUSED: PC and wait-routine bytes do not match the captured candidate.");
    return false;
  }

  // DLAB changes the meaning of ports C0/C1 from RBR/IER to DLL/DLH. Save the
  // complete AF/MB architectural value and original LCR, restore both exactly,
  // and do not resume the target. Reading MSR/IIR is intentionally avoided here
  // because those status reads can clear peripheral status bits.
  const uint32_t oldAfMb = zdi.readCpuRegister(Zdi::CpuRegister::AfMb);
  const uint8_t originalLcr = zdi.readIo(kUart0Lcr);
  zdi.writeIo(kUart0Lcr, static_cast<uint8_t>(originalLcr | 0x80U));
  const uint8_t divisorLow = zdi.readIo(kUart0DivisorLow);
  const uint8_t divisorHigh = zdi.readIo(kUart0DivisorHigh);
  zdi.writeIo(kUart0Lcr, originalLcr);
  zdi.writeCpuRegister(Zdi::CpuRegister::AfMb, oldAfMb);

  console.printf(
      "UART DIVISOR: UART0 LCR=%02X DIVISOR=%02X%02X; LCR and AF/MB restored.\n",
      originalLcr, divisorHigh, divisorLow);
  return true;
}

void printHexDump(const char* label, uint32_t address, const uint8_t* bytes,
                  size_t count) {
  console.printf("%s @ %06lX:", label, static_cast<unsigned long>(address));
  for (size_t i = 0; i < count; ++i) {
    console.printf(" %02X", bytes[i]);
  }
  console.println();
}

void captureFailedState() {
  if (captureComplete) {
    console.println("REFUSED: capture already completed; physically reset both boards for another run.");
    return;
  }
  if (zdi.productId() != kExpectedProductId) {
    console.println("REFUSED: expected eZ80 ZDI product ID 0x0007 is unavailable.");
    return;
  }

  console.println("CAPTURE: halting target eZ80...");
  zdi.halt();
  delay(10);

  const uint32_t afmb = zdi.readCpuRegister(Zdi::CpuRegister::AfMb);
  const uint32_t bc = zdi.readCpuRegister(Zdi::CpuRegister::Bc);
  const uint32_t de = zdi.readCpuRegister(Zdi::CpuRegister::De);
  const uint32_t hl = zdi.readCpuRegister(Zdi::CpuRegister::Hl);
  const uint32_t ix = zdi.readCpuRegister(Zdi::CpuRegister::Ix);
  const uint32_t iy = zdi.readCpuRegister(Zdi::CpuRegister::Iy);
  const uint32_t sp = zdi.readCpuRegister(Zdi::CpuRegister::Sp);
  const uint32_t pc = zdi.readCpuRegister(Zdi::CpuRegister::Pc);
  const uint8_t status = zdi.status();

  console.printf(
      "PC=%06lX SP=%06lX AF=%02lX%02lX MB=%02lX ADL=%u MADL=%u IFF1=%u HALT/SLEEP=%u\n",
      static_cast<unsigned long>(pc), static_cast<unsigned long>(sp),
      static_cast<unsigned long>(afmb & 0xFF),
      static_cast<unsigned long>((afmb >> 8) & 0xFF),
      static_cast<unsigned long>((afmb >> 16) & 0xFF),
      (status & 0x10) != 0, (status & 0x08) != 0, (status & 0x04) != 0,
      (status & 0x20) != 0);
  console.printf("BC=%06lX DE=%06lX HL=%06lX IX=%06lX IY=%06lX\n",
                static_cast<unsigned long>(bc), static_cast<unsigned long>(de),
                static_cast<unsigned long>(hl), static_cast<unsigned long>(ix),
                static_cast<unsigned long>(iy));

  uint8_t bytes[64] = {};
  const uint32_t codeStart = pc >= 16 ? pc - 16 : 0;
  zdi.readMemory(codeStart, 32, bytes);
  printHexDump("code around PC", codeStart, bytes, 32);
  zdi.readMemory(sp, 48, bytes);
  printHexDump("stack", sp, bytes, 48);
  zdi.readMemory(kSysClkFreqAddress, 4, bytes);
  printHexDump("SysClkFreq", kSysClkFreqAddress, bytes, 4);
  zdi.readMemory(kScrColoursAddress, 1, bytes);
  printHexDump("scrcolours", kScrColoursAddress, bytes, 1);
  zdi.readMemory(kGpAddress, 2, bytes);
  printHexDump("gp, serialFlags", kGpAddress, bytes, 2);
  zdi.readMemory(kUart0VectorPointerAddress, 2, bytes);
  printHexDump("UART0 vector pointer", kUart0VectorPointerAddress, bytes, 2);
  zdi.readMemory(kUart0FirstJumpAddress, 4, bytes);
  printHexDump("UART0 first jump", kUart0FirstJumpAddress, bytes, 4);
  zdi.readMemory(kUart0SecondJumpAddress, 4, bytes);
  printHexDump("UART0 second jump", kUart0SecondJumpAddress, bytes, 4);

  // Read the divisor inside the same halt epoch as the rest of the snapshot.
  // Rebooting the external P4 while the target remains halted can disturb the
  // ZDI context, so a later supplemental image is not equivalent evidence.
  inspectHaltedUartDivisor();

  const uint8_t timerControl = zdi.readIo(kTimer0Control);
  const uint8_t timerLow = zdi.readIo(kTimer0DataLow);
  const uint8_t timerHigh = zdi.readIo(kTimer0DataHigh);
  const uint8_t pdData = zdi.readIo(kPortDData);
  const uint8_t pdDirection = zdi.readIo(kPortDDirection);
  const uint8_t pdAlt1 = zdi.readIo(kPortDAlt1);
  const uint8_t pdAlt2 = zdi.readIo(kPortDAlt2);
  const uint8_t uartIer = zdi.readIo(kUart0Ier);
  const uint8_t uartIir = zdi.readIo(kUart0Iir);
  const uint8_t uartLcr = zdi.readIo(kUart0Lcr);
  const uint8_t uartMcr = zdi.readIo(kUart0Mcr);
  const uint8_t uartLsr = zdi.readIo(kUart0Lsr);
  const uint8_t uartMsr = zdi.readIo(kUart0Msr);

  console.printf("TIMER0 CTL=%02X DATA=%02X%02X\n", timerControl, timerHigh,
                timerLow);
  console.printf("PORTD DR=%02X DDR=%02X ALT1=%02X ALT2=%02X\n", pdData,
                pdDirection, pdAlt1, pdAlt2);
  console.printf("UART0 IER=%02X IIR=%02X LCR=%02X MCR=%02X LSR=%02X MSR=%02X\n",
                uartIer, uartIir, uartLcr, uartMcr, uartLsr, uartMsr);
  console.println("CAPTURE COMPLETE: target eZ80 remains halted; physically reset it after saving this report.");
  captureComplete = true;
}

}  // namespace

void setup() {
  console.begin();
  zdi.begin();
  delay(1000);
  console.println();
  console.println("Agon Extender PORT-008 P4 external ZDI probe");
  console.println("DIAGNOSTIC ONLY - NOT PRODUCT FIRMWARE");
  console.printf("P4 GPIO%u -> target ZDI TCK; P4 GPIO%u <-> target ZDI TDI; common GND\n",
                kZdiTckPin, kZdiTdiPin);
  console.printf("ZDI idle data level=%d\n", zdi.idleDataLevel());
  const uint16_t firstProductId = zdi.productId();
  const uint16_t secondProductId = zdi.productId();
  const uint16_t productId = zdi.productId();
  const uint8_t initialStatus =
      productId == kExpectedProductId ? zdi.status() : 0xFF;
  console.printf("ZDI product probes=%04X,%04X,%04X revision=%02X\n",
                firstProductId, secondProductId, productId,
                productId == kExpectedProductId ? zdi.revision() : 0);
  console.printf("ZDI initial status=%02X (active/halted=%u)\n", initialStatus,
                (initialStatus & 0x80) != 0);
  console.println(productId == kExpectedProductId
#if AGON_EXTENDER_P4_ZDI_AUTO_CAPTURE
                     ? "READY: identity gate passed for delayed one-shot capture."
#else
                     ? "READY: send lowercase 'c' to halt and capture the target."
#endif
                     : "ZDI DOWN: verify TCK, TDI, and common ground.");

#if AGON_EXTENDER_P4_ZDI_AUTO_CAPTURE
  if (firstProductId != kExpectedProductId ||
      secondProductId != kExpectedProductId ||
      productId != kExpectedProductId) {
    console.println("AUTO-CAPTURE REFUSED: all three identity probes must be 0007.");
  } else if ((initialStatus & 0x80) != 0) {
#if AGON_EXTENDER_P4_ZDI_HALTED_SUPPLEMENT
    console.println(
        "AUTO-CAPTURE BYPASSED: target is halted; attempting exact-candidate UART supplement only.");
    if (inspectHaltedUartDivisor()) {
      console.println(
          "HALTED SUPPLEMENT COMPLETE: target eZ80 remains halted; physically reset it after saving this report.");
    }
#else
    console.println("AUTO-CAPTURE REFUSED: target was already halted; reset the Agon and rerun.");
#endif
  } else {
    console.println("AUTO-CAPTURE ARMED: one-shot capture begins in 10 seconds.");
    delay(10000);
    if ((zdi.status() & 0x80) != 0) {
      console.println("AUTO-CAPTURE REFUSED: target entered ZDI mode before the capture gate.");
    } else {
      captureFailedState();
    }
  }
#endif
}

void loop() {
  const int command = console.read();
  if (command == 'c') {
    captureFailedState();
  }
  delay(10);
}
