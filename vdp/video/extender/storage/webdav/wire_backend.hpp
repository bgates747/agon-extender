#pragma once
#include "staged_put.hpp"
namespace agon::extender::webdav {
// Composition implements this on the existing console-owner request/reply
// queue, NOT on a new UART writer. enter returns only after matching EMOS
// READY; exchange revalidates the live full grant on every call. No queued late
// retry.
struct Channel {
  virtual ~Channel() = default;
  virtual int enter(const Operation &, spool::Binding &,
                    std::uint32_t &fileSession) = 0;
  virtual int exchange(const spool::Binding &, const std::uint8_t *, unsigned,
                       std::uint8_t *, unsigned &) = 0;
  virtual int leave(const spool::Binding &) = 0; // matching terminal close ACK
  virtual void cancel(const spool::Binding &) = 0;
  // Healthy client cancellation may use orderly terminal cleanup. Other
  // channel implementations retain conservative cancellation by default.
  virtual void stop(const spool::Binding &b) { cancel(b); }
};
class WireBackend : public Backend {
public:
  WireBackend(Channel &channel, std::string spoolDirectory, std::uint32_t quota)
      : channel_(channel), store_(std::move(spoolDirectory), quota) {}
  int begin(const Operation &) override;
  int finish() override;
  void cancel() override;
  int stat(const std::string &, Entry &) override;
  int list(const std::string &,
           const std::function<bool(const Entry &)> &) override;
  int snapshot(const std::string &, std::uint32_t &) override;
  int readSnapshot(std::uint32_t, void *, size_t, size_t &) override;
  void releaseSnapshot() override;
  Outcome put(const std::string &, std::uint32_t, bool, Body &) override;
  Outcome mkdir(const std::string &) override;
  Outcome move(const std::string &, const std::string &, bool) override;
  Outcome copy(const std::string &, const std::string &, bool, bool) override;
  Outcome remove(const std::string &) override;

private:
  using Bytes = std::vector<std::uint8_t>;
  Channel &channel_;
  spool::Store<> store_;
  spool::Binding binding_{};
  Operation operation_;
  std::uint32_t session_ = 0, seq_ = 0, tid_ = 0, transferSize_ = 0,
                transferCrc_ = 0;
  bool active_ = false, poisoned_ = false, snapshot_ = false;
  Bytes reply_;
  static Bytes pathBytes(const std::string &);
  int rpc(unsigned, const Bytes & = {});
  int remoteRead(const std::string &, std::uint32_t, void *, unsigned,
                 unsigned &, std::uint32_t &);
  int stageDownload(const std::string &, const std::string &, std::uint32_t);
  int transfer(const std::string &, bool);
  int activate(const std::string &);
  spool::Job job(const std::string &, const std::string &, std::uint32_t, bool);
  Outcome copyTree(const std::string &, const std::string &, bool, bool,
                   unsigned, unsigned &);
  Outcome removeTree(const std::string &, unsigned, unsigned &);
};
} // namespace agon::extender::webdav
