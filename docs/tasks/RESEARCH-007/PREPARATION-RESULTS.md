# Complete indexed-expansion benchmark preparation

## Executive summary

The complete standalone P4 comparison is built and packaged, with a validated
host collector/analyzer and an explicit deployment/restoration recipe. It tests
the actual old CPU conversion against PPA indexed expansion, including a path
that pays for retaining the old byte layout. Preparation is complete; there are
no hardware correctness or performance results. The bench remains untouched.

| Item | Evidence / outcome |
|---|---|
| Build | `ppa-clut-benchmark-r01-b2026-10-12-00-21-22Z` |
| Frozen source commit | `4d12c5eb` |
| Native target build | Pass, 113.765 s, no warnings |
| Application | 235,200 bytes; SHA256 `40fb9f3783c9a8b82f5edd3d0b5e091c0820f0c1f756b529969d57f2706237fc` |
| Silicon header checks | Both images: P4 chip18, revision range1–199 includes103 |
| Actual compiled graph | 554 translation units, confined to generated project/build and pinned SDK |
| Linked calls | CPU signal/linear/reorder, PPA BLEND/CLUT, NVS storage and app entry present |
| Headers / SDK | Actual object dependencies use the CLUT override; copied CPU headers match pinned hashes; SDK tracked tree clean |
| Payload | Bootloader0x2000, partition table0x8000, application0x20000; hashes, non-overlap and merged-image bytes verified |
| Offline checks | Five pass; independent RGB/channel/lane/guard checks and complete/truncated/duplicate/error/storage/build/numerical host cases |
| Collector CLI | Processes768 labelled synthetic samples into raw serial/JSON/CSV/Markdown; these are not P4 measurements |
| Bench | No device/serial/network access, reservation, flashing, reset, SD or startup changes |

[Source and exact recipe](benchmark/README.md) explain all four methods, six
workloads, warmups, timing boundaries, source cache preparation, NVS placement,
saved-result replay and restoration. [Normalized evidence](BENCHMARK-EVIDENCE.json)
records exact hashes and retained repository-relative build locations. The ignored
local evidence index is `agents/research007/benchmark-r01/INDEX.md`; the generated
package is `agents/research007/benchmark-r01/build-r01/flash-package.tar.gz`.
Generated binaries are retained locally rather than committed to Git.

The P4 runs once automatically, checking every output pixel, guards and source
integrity after each conversion. It commits all768 samples to a separate scratch
NVS area before serial emission. Host reports compare median/p95/worst complete
elapsed times side by side, with signed percentage improvements over the old CPU
path. Source reorder, conversion/driver wait and output publication remain
separate in JSON/CSV. Elapsed cycle counts are not CPU-busy measurements.

The linear PPA case assumes a changed framebuffer layout. The reorder + PPA case
includes the cost of retaining the current `x ^ 2` signal order. PPA's transparent
second input and driver/cache overhead remain included. No HDMI scanout or game
load runs, so a conversion win alone cannot establish Nurples performance.

The factory image contains padding over ordinary NVS and is **not** the bench
write recipe. Separate verified segments preserve ordinary NVS; only the test's
64KiB scratch NVS in the product's reserved tail is written by the benchmark.

R07-B01–B04 are complete under the [contract](BENCHMARK-CONTRACT.md). R07-B05
requires fresh bench handover and installation, measurement and restoration.
The original r05 compile-only sample/evidence stay frozen. Product SDK, renderer,
EMOS, production selection and the paused ExExt work are unchanged.
