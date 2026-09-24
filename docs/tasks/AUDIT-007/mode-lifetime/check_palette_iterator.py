#!/usr/bin/env python3
"""Extract the retained method unchanged into a small ASan lifetime reproducer.
This tests C++ container lifetime only, not P4 scheduling or graphics output.
"""
import argparse,pathlib,subprocess
p=argparse.ArgumentParser();p.add_argument('source',type=pathlib.Path);p.add_argument('output',type=pathlib.Path);a=p.parse_args()
s=a.source.read_text();start=s.index('void VGAPalettedController::deletePalette(uint16_t paletteId)');end=s.index('\n\nvoid VGAPalettedController::deleteSignalList',start)
method=s[start:end]
a.output.mkdir(parents=True,exist_ok=True)
unit='''#include <unordered_map>
#include <cstdint>
#include <cstdlib>
#define AGON_STOCK_PALETTE_GUARD
#define heap_caps_free free
struct VGAPalettedController {
 struct Item { void *signals; Item *next; };
 std::unordered_map<uint16_t,void*> m_signalMaps;
 Item *m_signalList=nullptr;
 void deletePalette(uint16_t);
};
'''+method+'''
int main() {
 VGAPalettedController c;
 c.m_signalMaps[0]=malloc(16);
 c.m_signalMaps[1]=malloc(16);
 c.m_signalMaps[2]=malloc(16);
 c.deletePalette(65535);
 free(c.m_signalMaps.at(0));
 return c.m_signalMaps.size()!=1;
}
'''
f=a.output/'repro.cpp';f.write_text(unit)
subprocess.run(['g++','-g','-O1','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(f),'-o',str(a.output/'repro')],check=True)
r=subprocess.run([str((a.output/'repro').resolve())],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(a.output/'result.txt').write_bytes(r.stdout)
print('Exit:',r.returncode);print(r.stdout.decode(errors='replace')[:3000])
raise SystemExit(0 if r.returncode and b'heap-use-after-free' in r.stdout else 1)
