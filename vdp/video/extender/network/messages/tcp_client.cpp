#include "tcp_client.hpp"
#include "accounting.hpp"
#include <cerrno>
#include <fcntl.h>
#if defined(ESP_PLATFORM)
#include <lwip/sockets.h>
#include <lwip/inet.h>
#else
#include <arpa/inet.h>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>
#endif
namespace agon::extender::network::messages {
Result TcpClient::failed(int error) noexcept {
    close(); error_ = error; state_ = Connect::Failed; return Result::Faulted;
}
void TcpClient::close() noexcept {
    if (fd_ >= 0) ::close(fd_);
    fd_ = -1; state_ = Connect::Closed;
}
Result TcpClient::start(const char* host, std::uint16_t port) noexcept {
    if (state_ != Connect::Closed) return Result::Busy;
    sockaddr_in address{}; address.sin_family = AF_INET; address.sin_port = htons(port);
    if (!host || !port || inet_pton(AF_INET, host, &address.sin_addr) != 1) return Result::Invalid;
    error_ = 0;
    fd_ = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (fd_ < 0) return failed(errno);
    const auto flags = fcntl(fd_, F_GETFL, 0);
    if (flags < 0 || fcntl(fd_, F_SETFL, flags | O_NONBLOCK) < 0) return failed(errno);
    if (::connect(fd_, reinterpret_cast<sockaddr*>(&address), sizeof address) == 0) {
        state_ = Connect::Connected; return Result::Ok;
    }
    if (errno != EINPROGRESS && errno != EWOULDBLOCK && errno != EINTR) return failed(errno);
    state_ = Connect::Connecting; return Result::Ok;
}
Connect TcpClient::pollConnect() noexcept {
    if (state_ != Connect::Connecting) return state_;
    pollfd poller{fd_, POLLOUT, 0};
    const auto available = ::poll(&poller, 1, 0);
    if (available < 0) {
        if (errno != EINTR) failed(errno);
        return state_;
    }
    if (!available) return state_;
    int error = 0; socklen_t length = sizeof error;
    if (getsockopt(fd_, SOL_SOCKET, SO_ERROR, &error, &length) != 0) failed(errno);
    else if (error) failed(error);
    else if (poller.revents & POLLOUT) state_ = Connect::Connected;
    else failed(ECONNABORTED);
    return state_;
}
IoResult TcpClient::read(std::uint8_t* data, std::size_t size) noexcept {
    accounting::Scope measure(accounting::Metric::SocketRead);measure.result(0,accounting::Outcome::Error);
    if (state_ != Connect::Connected || !data || !size) return {IoState::Error};
    const auto n = ::recv(fd_, data, size, 0);
    if (n > 0) {measure.result(n);return {IoState::Progress, static_cast<std::size_t>(n)};}
    if (!n) {measure.result(0,accounting::Outcome::Closed);return {IoState::Closed};}
    if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) {measure.result(0,accounting::Outcome::WouldBlock);return {IoState::WouldBlock};}
    error_ = errno; return {IoState::Error};
}
IoResult TcpClient::write(const std::uint8_t* data, std::size_t size) noexcept {
    accounting::Scope measure(accounting::Metric::SocketWrite);measure.result(0,accounting::Outcome::Error);
    if (state_ != Connect::Connected || !data || !size) return {IoState::Error};
#ifdef MSG_NOSIGNAL
    constexpr int flags = MSG_NOSIGNAL;
#else
    constexpr int flags = 0; // lwIP has no Unix SIGPIPE delivery.
#endif
    const auto n = ::send(fd_, data, size, flags);
    if (n > 0) {measure.result(n);return {IoState::Progress, static_cast<std::size_t>(n)};}
    if (n < 0 && (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR)) {measure.result(0,accounting::Outcome::WouldBlock);return {IoState::WouldBlock};}
    error_ = n < 0 ? errno : EIO; return {IoState::Error};
}
} // namespace agon::extender::network::messages
