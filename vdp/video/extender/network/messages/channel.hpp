// NET-003 experimental message core; not wired into a console or EMOS build.
// One serialized owner calls every method. A network worker must never hold a
// console/display lock across I/O. Views are synchronous borrows, invalid after
// any mutation; an adapter MUST NOT retain them for DMA/asynchronous writes.
//
// This prototype uses a four-byte little-endian length and opaque payload. It
// defines no published LAN/EMOS ABI, firmware capacity, reconnect or game policy.
// Fixed storage is intentional: busy never overwrites an accepted record.
#pragma once
#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>

namespace agon::extender::network::messages {
enum class Result { Ok, Empty, Busy, TooLarge, TooSmall, Invalid, Stale, Faulted, Exhausted };
enum class Fault { None, PeerClosed, Truncated, Io, InvalidLength, InvalidIo };
enum class State { Closed, Open, Faulted };
struct View { const std::uint8_t* data{}; std::size_t size{}; };
struct Progress { Result result; std::size_t consumed; };

// MaxPayload and Depth are explicit per-experiment allocations, not defaults or
// supported hardware limits. Two lanes each reserve Depth*(MaxPayload+4) bytes.
template<std::size_t MaxPayload, std::size_t Depth>
class Channel final {
    static_assert(MaxPayload > 0 && MaxPayload <= UINT32_MAX);
    static_assert(MaxPayload <= std::numeric_limits<std::size_t>::max() - 4);
    static_assert(Depth > 0);
    struct Frame { std::array<std::uint8_t, MaxPayload + 4> bytes{}; std::size_t size{}; };
    struct Queue {
        std::array<Frame, Depth> frames{};
        std::size_t head{}, count{};
        Frame& front() noexcept { return frames[head]; }
        Frame& back() noexcept { return frames[(head + count) % Depth]; }
        void pop() noexcept { head = (head + 1) % Depth; --count; }
        void clear() noexcept { head = count = 0; }
    };
public:
    explicit Channel(std::uint32_t previousGeneration = 0) noexcept : generation_(previousGeneration) {}
    Channel(const Channel&) = delete;
    Channel& operator=(const Channel&) = delete;
    Result open(std::uint32_t& token) noexcept {
        token = 0;
        if (state_ != State::Closed) return Result::Busy;
        if (generation_ == UINT32_MAX) return Result::Exhausted;
        token_ = ++generation_; token = token_; state_ = State::Open; fault_ = Fault::None;
        return Result::Ok;
    }
    Result close(std::uint32_t token) noexcept {
        if (!matches(token)) return Result::Stale;
        // Explicit close retires unread/uncertain records. No reconnect/replay.
        tx_.clear(); rx_.clear(); txOffset_ = headerUsed_ = payloadUsed_ = expected_ = 0;
        token_ = 0; state_ = State::Closed; return Result::Ok;
    }
    Result fail(std::uint32_t token, Fault reason) noexcept {
        if (!matches(token)) return Result::Stale;
        if (reason == Fault::None) return Result::Invalid;
        if (state_ == State::Open) { state_ = State::Faulted; fault_ = reason; }
        // Retain pending TX for diagnostics only, and allow complete RX to drain.
        // TX acceptance means local storage, never peer application delivery.
        return Result::Faulted;
    }
    Result send(std::uint32_t token, const std::uint8_t* data, std::size_t size) noexcept {
        const auto valid = writable(token); if (valid != Result::Ok) return valid;
        if (size > MaxPayload) return Result::TooLarge;
        if (size && !data) return Result::Invalid;
        if (tx_.count == Depth) return Result::Busy;
        auto& frame = tx_.back();
        const auto length = static_cast<std::uint32_t>(size);
        for (unsigned i = 0; i < 4; ++i) frame.bytes[i] = std::uint8_t(length >> (8 * i));
        if (size) std::memcpy(frame.bytes.data() + 4, data, size);
        frame.size = size + 4; ++tx_.count; return Result::Ok;
    }
    Result receive(std::uint32_t token, std::uint8_t* out, std::size_t capacity,
                   std::size_t& size) noexcept {
        size = 0;
        if (!matches(token)) return Result::Stale;
        if (!rx_.count) return state_ == State::Faulted ? Result::Faulted : Result::Empty;
        const auto& frame = rx_.front(); size = frame.size;
        if (capacity < size) return Result::TooSmall;
        if (size && !out) return Result::Invalid;
        if (size) std::memcpy(out, frame.bytes.data(), size);
        rx_.pop(); return Result::Ok;
    }
    View pending(std::uint32_t token) const noexcept {
        if (writable(token) != Result::Ok || !tx_.count) return {};
        const auto& frame = tx_.frames[tx_.head];
        return {frame.bytes.data() + txOffset_, frame.size - txOffset_};
    }
    Result sent(std::uint32_t token, std::size_t bytes) noexcept {
        const auto valid = writable(token); if (valid != Result::Ok) return valid;
        const auto view = pending(token);
        if (!bytes || bytes > view.size) return Result::Invalid;
        txOffset_ += bytes;
        if (txOffset_ == tx_.front().size) { tx_.pop(); txOffset_ = 0; }
        return Result::Ok;
    }
    std::size_t readCapacity(std::uint32_t token) const noexcept {
        if (writable(token) != Result::Ok || rx_.count == Depth) return 0;
        return headerUsed_ < 4 ? 4 - headerUsed_ : expected_ - payloadUsed_;
    }
    Progress feed(std::uint32_t token, const std::uint8_t* data, std::size_t size) noexcept {
        const auto valid = writable(token); if (valid != Result::Ok) return {valid, 0};
        if (size && !data) return {Result::Invalid, 0};
        std::size_t used = 0;
        while (used < size) {
            if (rx_.count == Depth) return {Result::Busy, used};
            if (headerUsed_ < 4) {
                const auto n = std::min(size - used, 4 - headerUsed_);
                std::memcpy(header_.data() + headerUsed_, data + used, n);
                headerUsed_ += n; used += n;
                if (headerUsed_ != 4) continue;
                expected_ = 0;
                for (unsigned i = 0; i < 4; ++i) expected_ |= std::uint32_t(header_[i]) << (8 * i);
                if (expected_ > MaxPayload) {
                    fail(token, Fault::InvalidLength); return {Result::Faulted, used};
                }
            }
            const auto n = std::min(size - used, expected_ - payloadUsed_);
            if (n) std::memcpy(rx_.back().bytes.data() + payloadUsed_, data + used, n);
            payloadUsed_ += n; used += n;
            if (payloadUsed_ == expected_) {
                rx_.back().size = expected_; ++rx_.count;
                headerUsed_ = payloadUsed_ = expected_ = 0;
            }
        }
        return {Result::Ok, used};
    }
    bool partialReceive() const noexcept { return headerUsed_ != 0; }
    State state() const noexcept { return state_; }
    Fault fault() const noexcept { return fault_; }
    std::size_t pendingSends() const noexcept { return tx_.count; }
    std::size_t pendingReceives() const noexcept { return rx_.count; }
private:
    bool matches(std::uint32_t token) const noexcept { return token && token == token_; }
    Result writable(std::uint32_t token) const noexcept {
        if (!matches(token)) return Result::Stale;
        return state_ == State::Open ? Result::Ok : Result::Faulted;
    }
    Queue tx_, rx_;
    std::array<std::uint8_t, 4> header_{};
    std::size_t txOffset_{}, headerUsed_{}, payloadUsed_{}, expected_{};
    std::uint32_t generation_{}, token_{};
    State state_{State::Closed};
    Fault fault_{Fault::None};
};
} // namespace agon::extender::network::messages
