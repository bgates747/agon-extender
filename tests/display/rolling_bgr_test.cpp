// Compare unchanged stock composition with the optional direct BGR painter.
// The host runner supplies independent baseline and candidate header copies.
#define AGON_EXTENDER_OVERLAY_BGR 0
#include "baseline/scene.hpp"
#undef AGON_EXTENDER_OVERLAY_BGR
namespace baseline_scanout = agon_scanout;
// Candidate header references a local copy of the same strip definitions.
#define agon_scanout candidate_scanout
#define AGON_EXTENDER_OVERLAY_BGR 1
#include "candidate/scene.hpp"
#undef agon_scanout
#undef AGON_EXTENDER_OVERLAY_BGR
#include <array>
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <vector>

#define IRAM_ATTR
namespace agon_scanout {
#include "dsi-strip-test/main/stock_sprite_body.inc"
}
namespace candidate_scanout {
#include "dsi-strip-test/main/stock_sprite_body.inc"
}
using namespace baseline_scanout;

static void copyScene(const Scene &source, candidate_scanout::Scene &destination) {
  destination.reset(source.background,source.width,source.height,source.outputWidth,source.outputHeight);
  for(unsigned i=0;i<source.count;++i) {
    const auto &s=source.sprites[i];
    assert(destination.append(s.x,s.y,s.image.width,s.image.height,
      static_cast<candidate_scanout::PixelFormat>(s.image.format),
      s.paintOptions.mode==PaintMode::XOR,s.image.data));
  }
}


static unsigned comparisons;
static std::uint32_t randomState = 0x65a0c11e;
static unsigned randomValue()
{
  randomState ^= randomState << 13;
  randomState ^= randomState >> 17;
  randomState ^= randomState << 5;
  return randomState;
}

static void compare(Scene &scene, bool canonicalBackground = false)
{
  candidate_scanout::Scene proposed;
  copyScene(scene,proposed);
  constexpr unsigned guard = 37;
  const unsigned bytes = scene.outputWidth * scene.outputHeight * 3;
  std::vector<std::uint8_t> background(bytes + guard * 2);
  for (auto &value : background) value = randomValue();
  if (canonicalBackground)
    for (unsigned i = guard; i < guard + bytes; ++i) background[i] = (background[i] >> 6) * 85;
  for (unsigned blockRows : {1U, 7U, 32U, 40U, 64U}) {
    auto baseline = background, candidate = background;
    for (unsigned first = 0; first < unsigned(scene.outputHeight); first += blockRows) {
      const unsigned rows = std::min(blockRows, unsigned(scene.outputHeight) - first);
      auto offset = guard + first * scene.outputWidth * 3;
      scene.compose(baseline.data() + offset, first, rows);
      proposed.compose( candidate.data() + offset, first, rows);
    }
    assert(baseline == candidate);
    assert(std::equal(baseline.begin(), baseline.begin() + guard, background.begin()));
    assert(std::equal(baseline.end() - guard, baseline.end(), background.end() - guard));
    ++comparisons;
    // Repeated composition of overlapping XOR sprites is order-sensitive.
    scene.compose(baseline.data() + guard, 0, scene.outputHeight);
    proposed.compose( candidate.data() + guard, 0, scene.outputHeight);
    assert(baseline == candidate);
    ++comparisons;
  }
  // An isolated caller strip may begin inside a sprite or the top pillarbox.
  for (unsigned first : {0U, 1U, 7U, 31U, 47U, 63U}) {
    if (first >= unsigned(scene.outputHeight)) continue;
    const unsigned rows = std::min(17U, unsigned(scene.outputHeight) - first);
    auto baseline = background, candidate = background;
    const auto offset = guard + first * scene.outputWidth * 3;
    scene.compose(baseline.data() + offset, first, rows);
    proposed.compose( candidate.data() + offset, first, rows);
    assert(baseline == candidate);
    ++comparisons;
  }
}

static void add(Scene &scene, int x, int y, int width, int height,
                PixelFormat format, bool xorMode, unsigned pattern)
{
  const unsigned stride = format == PixelFormat::RGBA8888 ? 4 : 1;
  std::vector<std::uint8_t> bytes(width * height * stride);
  for (unsigned n = 0; n < unsigned(width * height); ++n) {
    if (stride == 1) {
      if (pattern == 0) bytes[n] = n; // all64 colours and all4 alpha classes
      else if (pattern == 1) bytes[n] = n & 63; // entirely transparent, nonzero RGB
      else if (pattern == 2) bytes[n] = 0xc0 | (n & 63); // entirely opaque
      else bytes[n] = randomValue();
    } else {
      bytes[n * 4] = n;
      bytes[n * 4 + 1] = n * 73 + 19;
      bytes[n * 4 + 2] = n * 131 + 254;
      bytes[n * 4 + 3] = pattern == 1 ? 0 : pattern == 2 ? 255 : std::array<unsigned, 4>{0, 1, 128, 255}[n % 4];
    }
  }
  assert(scene.append(x, y, width, height, format, xorMode, bytes.data()));
  // This is deliberately the existing immutable arena, not a live-source path.
  std::fill(bytes.begin(), bytes.end(), 0x29);
}

static void exhaustiveAlphaAndChannels()
{
  for (auto format : {PixelFormat::RGBA2222, PixelFormat::RGBA8888})
    for (bool xorMode : {false, true})
      for (unsigned pattern : {0U, 1U, 2U, 3U}) {
        Scene scene;
        scene.reset(0, 64, 16, 80, 32);
        add(scene, 0, 0, 64, 16, format, xorMode, pattern);
        compare(scene);
        compare(scene, true);
      }
  // Explicit transparent-background quantization regression: all alpha zero,
  // no opaque sprite or canonical initial pixel can hide the required change.
  candidate_scanout::Scene transparent;
  transparent.reset(0, 4, 1, 4, 1);
  const std::uint8_t source[] = {1, 2, 3, 63};
  assert(transparent.append(0, 0, 4, 1, candidate_scanout::PixelFormat::RGBA2222, false, source));
  std::uint8_t expected[] = {0, 0, 0, 85, 85, 85, 170, 170, 170, 255, 255, 255};
  std::uint8_t pixels[] = {1, 2, 63, 64, 85, 127, 128, 170, 191, 192, 254, 255};
  transparent.compose(pixels, 0, 1);
  assert(std::equal(std::begin(pixels), std::end(pixels), std::begin(expected)));
  // Unknown formats never reach current staging, but must retain its baseline
  // no-paint/background-quantization behavior if a future caller adds one.
  Scene unknown;
  unknown.reset(0, 64, 16, 80, 32);
  add(unknown, -3, 2, 35, 19, static_cast<PixelFormat>(99), true, 3);
  compare(unknown);
}

static void clippedAndOverlapping()
{
  for (auto geometry : {std::array<int, 4>{684, 384, 512, 384},
                       std::array<int, 4>{848, 480, 512, 384},
                       std::array<int, 4>{684, 384, 684, 384},
                       std::array<int, 4>{848, 480, 320, 240}}) {
    const auto W = geometry[0], H = geometry[1], w = geometry[2], h = geometry[3];
    Scene scene;
    scene.reset(0, w, h, W, H);
    add(scene, -3, -5, 17, 19, PixelFormat::RGBA8888, true, 0);
    add(scene, w - 1, h - 1, 17, 19, PixelFormat::RGBA2222, true, 0);
    add(scene, -30, 29, 31, 42, PixelFormat::RGBA2222, false, 1);
    add(scene, w - 14, h - 33, 35, 50, PixelFormat::RGBA8888, false, 2);
    add(scene, 11, 27, 35, 69, PixelFormat::RGBA2222, false, 3);
    add(scene, 14, 34, 28, 62, PixelFormat::RGBA2222, true, 3);
    add(scene, 18, 40, 17, 31, PixelFormat::RGBA8888, true, 0);
    add(scene, 19, 42, 25, 29, PixelFormat::RGBA2222, false, 1);
    add(scene, 20, 43, 19, 47, PixelFormat::RGBA2222, true, 2);
    const unsigned before = scene.count;
    add(scene, w, h, 16, 16, PixelFormat::RGBA2222, false, 3);
    add(scene, -16, -16, 16, 16, PixelFormat::RGBA8888, false, 3);
    assert(scene.count == before);
    compare(scene);
    compare(scene, true);
    scene.reset(0, w, h, W, H);
    compare(scene); // no old arena entry may draw after reset
  }
}

static void maximumAndRandomScenes()
{
  Scene maximum;
  maximum.reset(0, 512, 384, 684, 384);
  for (unsigned i = 0; i < Scene::maximumSprites; ++i)
    add(maximum, 10 + i % 17, 25 + i % 37, 17 + i % 7, 15 + i % 19,
        i % 3 ? PixelFormat::RGBA2222 : PixelFormat::RGBA8888, i % 2, i % 4);
  assert(maximum.count == Scene::maximumSprites);
  compare(maximum);
  for (unsigned iteration = 0; iteration < 64; ++iteration) {
    Scene scene;
    scene.reset(0, 64, 64, 80, 80);
    const unsigned count = randomValue() % 24;
    for (unsigned i = 0; i < count; ++i)
      add(scene, int(randomValue() % 96) - 24, int(randomValue() % 96) - 24,
          1 + randomValue() % 36, 1 + randomValue() % 37,
          randomValue() % 2 ? PixelFormat::RGBA2222 : PixelFormat::RGBA8888,
          randomValue() % 2, randomValue() % 4);
    compare(scene);
  }
}

static void bothEdgeFallback()
{
  Scene control;control.reset(0,64,16,80,32);
  add(control,-4,0,80,16,PixelFormat::RGBA2222,true,3);
  candidate_scanout::Scene proposed;copyScene(control,proposed);
  assert(!candidate_scanout::supportsDirectBgr(proposed));
  compare(control);
  proposed.reset(0,64,16,80,32);
  const std::uint8_t clipped[16]={0};
  assert(proposed.append(-4,0,16,1,candidate_scanout::PixelFormat::RGBA2222,false,clipped));
  assert(candidate_scanout::supportsDirectBgr(proposed));
}

int main()
{
  bothEdgeFallback();
  exhaustiveAlphaAndChannels();
  clippedAndOverlapping();
  maximumAndRandomScenes();
  std::printf("PASS: %u exact baseline/direct BGR comparisons; arbitrary and canonical backgrounds, every alpha/colour, SET/XOR, clipping, overlap, deep-copy arena,258 sprites, strip splits and guards. No P4 speed claim.\n", comparisons);
}
