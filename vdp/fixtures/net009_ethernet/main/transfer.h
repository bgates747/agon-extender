#pragma once

#include "bw_codec.h"

namespace net009 {
struct Arm {
    uint32_t nonce;
    uint32_t baud;
    uint32_t millis;
    bool upload;
};

struct Result {
    const char *error = nullptr;
    uint32_t rx_frames = 0;
    uint32_t tx_frames = 0;
    uint8_t received[n8bw::max_frame]{};
    size_t received_size = 0;
};

// The socket must be nonblocking. The caller owns and closes it.
Result transfer(int socket, const Arm &arm, int64_t (*now_us)());
}
