"""Execute the maintained split-upload read loop; fake only its I/O boundary."""
from pathlib import Path
import resource
import subprocess
import tempfile
import unittest

from p4_transport_reset_test import method

ROOT = Path(__file__).resolve().parents[1]
READ = ROOT / 'vdp/video/extender/transport/console_stream.hpp'


def source(body):
    return r'''#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <functional>
#include <vector>
static unsigned clockNow, sleeps;
unsigned millis() { return clockNow++; }
void vTaskDelay(unsigned n) { assert(n == 1); ++sleeps; }
constexpr int UART_NUM_1 = 1;
#define pdMS_TO_TICKS(n) (n)
int uart_read_bytes(int, void *, size_t, unsigned) { assert(false); return 0; }
struct Session { bool active() const { return true; } };
struct Owner { bool owned = false; bool pending() const { return owned; } };
struct Queue {
 bool live = true; std::vector<uint8_t> bytes;
 bool active() const { return live; }
 size_t available() const { return bytes.size(); }
 size_t read(uint8_t *p, size_t n) {
  n = std::min(n, bytes.size());
  std::copy_n(bytes.begin(), n, p); bytes.erase(bytes.begin(), bytes.begin()+n);
  return n;
 }
};
struct Reader {
 uint8_t setup[4]{}; unsigned pos = 4; int cached = -1;
 const char *failure = nullptr;
 Session session; Owner parallel; Queue parallelVdu;
 std::function<void()> progress;
 unsigned getTimeout() const { return 40; }
''' + body + r'''
};
int main(int argc, char **) {
 uint8_t out[8]{}; Reader r; unsigned calls = 0;
 clockNow = sleeps = 0;
 r.parallel.owned = true;
 r.progress = [&]() {
  ++calls;
  if (calls == 4) { r.parallel.owned = false; r.parallelVdu.bytes = {1,2,3,4}; }
 };
 assert(r.readBytes(out,4) == 4 && calls == 4 && !r.parallel.pending());
 if (argc == 1) assert(sleeps == 0); // old unconditional delay fails here
 else return sleeps == 3 ? 0 : 1;
 assert((std::vector<uint8_t>(out,out+4) == std::vector<uint8_t>{1,2,3,4}));

 r = Reader{}; calls = clockNow = sleeps = 0;
 r.progress = [&]() { if (++calls == 4) r.parallelVdu.bytes = {5,6}; };
 assert(r.readBytes(out,2) == 2 && calls == 4 && sleeps == 3);

 r = Reader{}; calls = clockNow = sleeps = 0;
 r.setup[0] = 9; r.setup[1] = 8; r.setup[2] = 7; r.setup[3] = 6;
 r.pos = 2; r.cached = 5; r.parallelVdu.bytes = {4}; r.parallel.owned = true;
 r.progress = [&]() { ++calls; r.parallel.owned = false; r.parallelVdu.bytes = {3,2,1}; };
 assert(r.readBytes(out,7) == 7 && calls == 1 && sleeps == 0);
 assert((std::vector<uint8_t>(out,out+7) == std::vector<uint8_t>{7,6,5,4,3,2,1}));

 r = Reader{}; clockNow = sleeps = 0;
 assert(r.readBytes(out,2) == 0 && clockNow >= 40 && sleeps > 0);

 r = Reader{}; calls = clockNow = sleeps = 0;
 r.parallel.owned = true;
 r.progress = [&]() { ++calls; r.failure = "peer fault"; };
 assert(r.readBytes(out,2) == 0 && calls == 1 && sleeps == 0);
 assert(r.readBytes(nullptr,2) == 0 && r.readBytes(out,0) == 0);
}
'''


class ProgressTests(unittest.TestCase):
    def test_owned_progress_idle_split_timeout_and_fault(self):
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        body = method(READ, 'size_t readBytes(uint8_t *p, size_t n) override')
        body = body.replace(' override', '')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'progress.cpp'
            exe = path.with_suffix('')
            for old in (False, True):
                actual = body
                if old:
                    actual = actual.replace(
                        'if(!parallelVdu.available() && !parallel.pending())',
                        'if(!parallelVdu.available())')
                    self.assertNotEqual(actual, body)
                path.write_text(source(actual))
                subprocess.run(['c++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                                '-DAGON_EXTENDER_EXEXT_STREAM',
                                '-fsanitize=address,undefined',
                                '-fno-sanitize-recover=all', str(path), '-o', str(exe)],
                               check=True)
                if old:
                    # Prove both the old sleep count and the regression assertion.
                    subprocess.run([str(exe), 'old-count'], check=True, timeout=5)
                    failed = subprocess.run([str(exe)], capture_output=True, timeout=5)
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertIn(b'sleeps == 0', failed.stderr)
                else:
                    subprocess.run([str(exe)], check=True, timeout=5)


if __name__ == '__main__':
    unittest.main()
