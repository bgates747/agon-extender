# Agon Extender mainboard-SD transport lab — r01

Experimental source sample, 2026-09-13. This source kit lets you exercise Extender's
production record codec, bounded request queue and durable host-client tests
without an Agon, P4, SD card or network server. It is intended as a starting
point for discussing reusable transport behavior with TRS-OS developers.

## Try it

Use Linux or macOS with Python 3.10+, a C99 compiler named `cc` and a C++17
compiler named `c++`. The tests use only Python's standard library; the queue
test also requires the compiler's AddressSanitizer/UndefinedBehaviorSanitizer
runtime. The Python client uses POSIX `fcntl` locking; native Windows is not a
tested target. Start in this extracted directory:

```sh
python3 -m venv .venv
.venv/bin/python -m unittest discover -s tests -p 'test_sd*.py' -v
mkdir -p build
c++ -std=c++17 -Wall -Wextra -Werror -I vdp/video examples/queue_demo.cpp -o build/queue_demo
./build/queue_demo
```

Expect ten passing tests. The narrated demo shows offline rejection (503), a
synthetic peer's presence, queued HELLO (202), an identical retry after a lost
reply and cached completion (200). It creates no files beyond your build output
and never opens a network connection. Test scratch/state files are temporary.

## What is here

1. `vdp/video/extender/storage/sd_wire.h`: C record framing, little-endian
   fields and CRC32; maximum 240 bytes including a 20-byte header.
2. `vdp/video/extender/storage/sd_service.hpp`: the C++ P4-side queue core.
   Its caller must serialize access and supply monotonic millisecond ticks;
   the class does not supply UART, HTTP or filesystem services.
3. `scripts/sdcard.py`: the unchanged real HTTP client. The included tests
   replace its transport with synthetic responses; they cover retained exact
   retries, exclusive client-state ownership and response/path validation.
4. `examples/queue_demo.cpp`: a small synthetic peer driving the actual queue.
5. `tests/`: unchanged production tests. The C codec is cross-checked against
   Python CRC/packing; the C++ queue runs with address/undefined sanitizers.

Read the [maintained wire contract](https://github.com/bgates747/agon-extender/blob/main/docs/protocols/mainboard-sd.md)
for operation payloads and staged-file recovery semantics. The test kit covers
transport/client behavior, not disk durability or end-to-end hardware access.

Real use of `scripts/sdcard.py` needs the separately installed EMOS gateway,
foreground `sdserve` application and configured P4 firmware. Follow the
[operating guide](https://github.com/bgates747/agon-extender/blob/main/docs/mainboard-sd.md)
for those identified builds. The service owns access to the **Agon mainboard
SD card**; the P4 card is a different planned service. Whole-card access can
replace system files, and the endpoint has no authentication; use a trusted LAN.

This is a file protocol, not TRS-NET or a sector-disk server. It does not remain
available merely because TRS-OS has taken over from EMOS. No unsupported-board
firmware, TRS-OS images or guest drivers are included.

## Provenance and license

Production code/tests are copied byte-for-byte from Agon Extender; consult
`manifest.json` for the source HEAD, source path, SHA-256 and whether each file
differs from that HEAD. New task material is explicitly identified. This is an
experimental source snapshot, not a firmware release. `LICENSE` contains GPLv3 and `LICENSING.md`
records the GPL-3.0-only project policy and preservation of upstream notices.
