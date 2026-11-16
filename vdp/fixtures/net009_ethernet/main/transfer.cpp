#include "transfer.h"

#include <cerrno>
#include <sys/select.h>
#include <sys/socket.h>

namespace net009 {
namespace {
struct Stream {
    int socket;
    int64_t (*now_us)();
    int64_t deadline;

    bool exchange(uint8_t *data, size_t size, size_t &done, bool writing) const {
        while (done < size) {
            const auto remaining = deadline - now_us();
            if (remaining <= 0) return false;
            timeval timeout{long(remaining / 1000000), long(remaining % 1000000)};
            fd_set ready;
            FD_ZERO(&ready);
            FD_SET(socket, &ready);
            const int selected = select(socket + 1, writing ? nullptr : &ready,
                                        writing ? &ready : nullptr, nullptr, &timeout);
            if (selected < 0 && errno == EINTR) continue;
            if (selected <= 0) return false;
            const auto count = writing ? send(socket, data + done, size - done, 0)
                                       : recv(socket, data + done, size - done, 0);
            if (count < 0 && (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK))
                continue;
            if (count <= 0) return false;
            done += size_t(count);
        }
        return true;
    }

    bool write(uint32_t seq, const void *data = nullptr, size_t length = 0) const {
        uint8_t buffer[n8bw::max_frame];
        size_t done = 0;
        return exchange(buffer, n8bw::frame(buffer, seq, data, length), done, true);
    }

    const char *read(Result &result, uint32_t seq) const {
        auto *buffer = result.received;
        auto &done = result.received_size;
        done = 0;
        if (!exchange(buffer, n8bw::header_size, done, false)) return "header_io";
        const auto n = n8bw::get(buffer + 8);
        if (memcmp(buffer, "N8BW", 4) || n > n8bw::payload_size) return "header";
        if (!exchange(buffer, n8bw::header_size + n, done, false)) return "body_io";
        if (n8bw::get(buffer + 4) != seq) return "sequence";
        if (!n8bw::valid(buffer, done)) return "crc";
        return nullptr;
    }
};
}

Result transfer(int socket, const Arm &arm, int64_t (*now_us)()) {
    Result result;
    Stream stream{socket, now_us, now_us() + 10000000};
    result.error = stream.read(result, 0);
    if (result.error) return result;
    const auto *hello = result.received + n8bw::header_size;
    if (result.received_size != n8bw::header_size + 16 ||
        n8bw::get(hello) != arm.nonce || n8bw::get(hello + 4) != arm.baud ||
        n8bw::get(hello + 8) != arm.millis || n8bw::get(hello + 12) != n8bw::payload_size) {
        result.error = "hello";
        return result;
    }
    const auto finish = now_us() + int64_t(arm.millis) * 1000;
    stream.deadline = finish + 12000000;
    uint8_t payload[n8bw::payload_size];
    if (!stream.write(0, "GO", 2) || (arm.upload && !stream.write(1))) {
        result.error = "control_write";
        return result;
    }
    for (;;) {
        const auto seq = result.rx_frames + 1;
        result.error = stream.read(result, seq);
        if (result.error) return result;
        if (result.received_size == n8bw::header_size) break;
        if (!arm.upload || result.received_size != n8bw::max_frame) {
            result.error = "payload_length";
            return result;
        }
        n8bw::pattern(payload, sizeof(payload), seq, n8bw::up_salt);
        if (memcmp(payload, result.received + n8bw::header_size, sizeof(payload))) {
            result.error = "pattern";
            return result;
        }
        ++result.rx_frames;
    }
    if (arm.upload) {
        if (!result.rx_frames) result.error = "empty";
        return result;
    }
    const auto send_until = now_us() + int64_t(arm.millis) * 1000;
    stream.deadline = send_until + 12000000;
    while (now_us() < send_until) {
        const auto seq = result.tx_frames + 1;
        n8bw::pattern(payload, sizeof(payload), seq, n8bw::down_salt);
        if (!stream.write(seq, payload, sizeof(payload))) {
            result.error = "data_write";
            return result;
        }
        ++result.tx_frames;
    }
    if (!result.tx_frames) result.error = "empty";
    else if (!stream.write(result.tx_frames + 1)) result.error = "eos_write";
    return result;
}
}
