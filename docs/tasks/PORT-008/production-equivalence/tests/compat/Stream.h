#pragma once

#include <cstddef>
#include <cstdint>

class Print {
 public:
  virtual ~Print() = default;
  virtual std::size_t write(std::uint8_t byte) = 0;
  virtual std::size_t write(std::uint8_t const *bytes, std::size_t length) {
    std::size_t written = 0;
    while (written < length && write(bytes[written]) == 1) ++written;
    return written;
  }
};

class Stream : public Print {
 public:
  ~Stream() override = default;
  virtual int available() = 0;
  virtual int read() = 0;
  virtual int peek() = 0;
  virtual void flush() = 0;
};
