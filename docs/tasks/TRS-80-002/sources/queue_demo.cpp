// SPDX-License-Identifier: GPL-3.0-only
// Synthetic peer; no UART, HTTP server, filesystem or target hardware.
#include <cassert>
#include <cstdio>
#include <cstring>
#include "extender/storage/sd_service.hpp"

using agon::extender::storage::SdService;

int main() {
    SdService queue;
    unsigned char request[SD_MAX_RECORD]{}, peer[SD_MAX_RECORD]{};
    unsigned char out[SD_MAX_RECORD]{};
    unsigned length = 0;
    sd_header(request, SD_REQUEST, 3, 1, SD_HELLO, 0, 0);
    sd_seal(request);

    int status = queue.post(request, SD_HEADER, out, length, 0);
    assert(status == 503 && length == 0);
    std::printf("Offline request: %d\n", status);

    sd_header(peer, SD_PRESENCE, 11, 0, 0, 0, 0);
    sd_seal(peer);
    bool accepted = queue.receive(peer, SD_HEADER, 0);
    assert(accepted && queue.online(0));
    std::puts("Synthetic peer announces boot 11");

    status = queue.post(request, SD_HEADER, out, length, 1);
    assert(status == 202);
    std::printf("HELLO queued: %d\n", status);
    unsigned sent = queue.take(out, 1);
    assert(sent == SD_HEADER && std::memcmp(out, request, sent) == 0);
    std::puts("First request delivered; pretend its reply was lost");
    sent = queue.take(out, 400);
    assert(sent == 0);
    sent = queue.take(out, 401);
    assert(sent == SD_HEADER && std::memcmp(out, request, sent) == 0);
    std::puts("400 ms later: retry contains exactly the same bytes");

    sd_header(peer, SD_RESPONSE, 3, 1, SD_HELLO, SD_OK, 8);
    sd_put32(peer + SD_HEADER, 11); // Synthetic application boot identity.
    sd_put16(peer + SD_HEADER + 4, 212);
    sd_put16(peer + SD_HEADER + 6, 15);
    sd_seal(peer);
    accepted = queue.receive(peer, SD_HEADER + 8, 410);
    assert(accepted);
    status = queue.post(request, SD_HEADER, out, length, 411);
    assert(status == 200 && length == SD_HEADER + 8);
    assert(std::memcmp(out, peer, length) == 0);
    sent = queue.take(out, 900);
    assert(sent == 0);
    std::printf("Identical poll returns cached completion: %d (%u bytes)\n",
                status, length);
    std::puts("PASS: production queue exercised with a synthetic peer");
}
