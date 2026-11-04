// NET-003 experimental outbound numeric-IPv4 TCP adapter. No DNS, service,
// background task or global Ethernet owner is created. Owner supplies an
// explicit connect deadline/cancellation and serializes lifecycle with pump.
#pragma once
#include "pump.hpp"
namespace agon::extender::network::messages {
enum class Connect { Closed, Connecting, Connected, Failed };
class TcpClient final : public Io {
public:
    TcpClient() noexcept = default;
    ~TcpClient() override { close(); }
    TcpClient(const TcpClient&) = delete;
    TcpClient& operator=(const TcpClient&) = delete;
    Result start(const char* numericIpv4, std::uint16_t port) noexcept;
    Connect pollConnect() noexcept;
    void close() noexcept;
    Connect state() const noexcept { return state_; }
    int error() const noexcept { return error_; }
    IoResult read(std::uint8_t*, std::size_t) noexcept override;
    IoResult write(const std::uint8_t*, std::size_t) noexcept override;
private:
    Result failed(int error) noexcept;
    int fd_{-1}, error_{};
    Connect state_{Connect::Closed};
};
} // namespace agon::extender::network::messages
