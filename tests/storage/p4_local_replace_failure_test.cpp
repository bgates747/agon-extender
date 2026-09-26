#include "extender/storage/local/files.hpp"
#include <cassert>
#include <filesystem>
#include <fstream>
using namespace agon::extender::local_sd;
static bool failInstall = false;
extern "C" int __real_rename(const char *, const char *);
extern "C" int __wrap_rename(const char *from, const char *to) {
  if (failInstall && std::string(from).find(".ext-upload") != std::string::npos) {
    errno = EIO;
    return -1;
  }
  return __real_rename(from, to);
}
int main() {
  char pattern[] = "/tmp/p4sd-failure-XXXXXX";
  const char *dir = mkdtemp(pattern);
  assert(dir);
  std::string target = std::string(dir) + "/old";
  { std::ofstream f(target); f << "original"; }
  {
    Upload u(target, true);
    assert(u.open()); assert(u.write("replacement", 11));
    failInstall = true;
    assert(!u.finish());
    assert(errno == EIO);
  }
  std::ifstream f(target);
  std::string content; f >> content;
  assert(content == "original");
  assert(!std::filesystem::exists(target + ".ext-upload"));
  assert(!std::filesystem::exists(target + ".ext-backup"));
  std::filesystem::remove_all(dir);
}
