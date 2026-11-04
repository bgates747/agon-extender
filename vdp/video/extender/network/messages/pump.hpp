// NET-003 bounded synchronous nonblocking stream pump. The owner serializes
// lifecycle and all core access. Io is not a socket owner and cannot reconnect.
#pragma once
#include "channel.hpp"
namespace agon::extender::network::messages {
enum class IoState { Progress, WouldBlock, Closed, Error };
struct IoResult { IoState state; std::size_t size{}; };
class Io {
public:
    virtual ~Io() = default;
    virtual IoResult read(std::uint8_t*, std::size_t) noexcept = 0;
    virtual IoResult write(const std::uint8_t*, std::size_t) noexcept = 0;
};
struct PumpCursor { unsigned nextDirection{}; };
struct PumpResult { std::size_t calls{}, bytes{}; Result result{Result::Ok}; };

template<std::size_t Max, std::size_t Depth>
PumpResult pump(Channel<Max, Depth>& channel, std::uint32_t token, Io& io, PumpCursor& cursor,
                std::size_t operationBudget, std::size_t byteBudget) noexcept {
    PumpResult report;
    std::array<std::uint8_t, 256> scratch{};
    // Check ownership even when no data is queued; stale pumps do no I/O.
    const auto state = channel.feed(token, nullptr, 0).result;
    if (state != Result::Ok) { report.result = state; return report; }
    while (report.calls < operationBudget && report.bytes < byteBudget) {
        bool progressed = false;
        const auto first = cursor.nextDirection;
        for (unsigned step = 0; step < 2; ++step) {
            const auto direction = (first + step) % 2;
            if (report.calls == operationBudget || report.bytes == byteBudget) break;
            const auto view = channel.pending(token);
            const auto capacity = direction == 0 ? view.size : channel.readCapacity(token);
            const auto n = std::min({capacity, scratch.size(), byteBudget - report.bytes});
            if (!n) continue;
            const auto result = direction == 0 ? io.write(view.data, n) : io.read(scratch.data(), n);
            ++report.calls; cursor.nextDirection = (direction + 1) % 2;
            if (result.state != IoState::Progress && result.size) {
                report.result = channel.fail(token, Fault::InvalidIo); return report;
            }
            if (result.state == IoState::WouldBlock) continue;
            if (result.state == IoState::Error || result.state == IoState::Closed) {
                const auto reason = result.state == IoState::Error ? Fault::Io :
                    (channel.partialReceive() ? Fault::Truncated : Fault::PeerClosed);
                report.result = channel.fail(token, reason); return report;
            }
            if (!result.size || result.size > n) {
                report.result = channel.fail(token, Fault::InvalidIo); return report;
            }
            if (direction == 0) report.result = channel.sent(token, result.size);
            else {
                const auto fed = channel.feed(token, scratch.data(), result.size);
                report.result = fed.result;
                if (fed.consumed != result.size && report.result == Result::Ok)
                    report.result = channel.fail(token, Fault::InvalidIo);
            }
            report.bytes += result.size; progressed = true;
            if (report.result != Result::Ok) return report;
        }
        if (!progressed) break;
    }
    return report;
}
} // namespace agon::extender::network::messages
