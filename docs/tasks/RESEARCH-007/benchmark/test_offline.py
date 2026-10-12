"""Offline protocol/numerical tests and independent host CPU-kernel checks.

Synthetic serial values are ONLY parser test data, never P4 measurements.
"""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location("benchmark_results",HERE / "results.py")
results = importlib.util.module_from_spec(spec)
spec.loader.exec_module(results)

def synthetic():
    build = "ppa-clut-benchmark-r01-b2026-10-11-00-00-00Z"
    lines = [f"BENCH_STORED,{build},1,15456",f"BENCH_BEGIN,{build},1,fresh,6,4,32"]
    lines += [f"BENCH_METHOD,{i},{m}" for i,m in enumerate(results.METHODS)]
    for c,(w,h,y,region) in enumerate(results.CASES):
        lines.append(f"BENCH_CASE,{c},{w},{h},{y},{region}")
        for m in range(4):
            for s in range(32):
                operation = 100+s+m*10+c
                lines.append(f"BENCH_ROW,{c},{m},{s},1,{operation},2,{operation+3},1000")
    lines.append(f"BENCH_DONE,{build},1,5000000,768")
    return "\n".join(lines)+"\n"

class Protocol(unittest.TestCase):
    def test_complete_and_percentages(self):
        data = results.parse(synthetic())
        self.assertEqual(len(data["rows"]),768)
        group = results.summarize(data)[0]["statistics"]["total_us"]
        self.assertEqual(group,{"median":118.5,"p95":133,"worst":134})
        self.assertIn("-22.6%",results.report(data))
        with tempfile.TemporaryDirectory() as directory:
            results.write_outputs(Path(directory),synthetic())
            self.assertEqual(len((Path(directory)/"samples.csv").read_text().splitlines()),769)

    def test_saved_replay(self):
        text = synthetic().split("\n",1)[1].replace(",fresh,",",stored,")
        self.assertEqual(results.parse(text)["kind"],"stored")

    def test_reject_failures(self):
        source = synthetic()
        lines = source.splitlines()
        row = next(l for l in lines if l.startswith("BENCH_ROW"))
        variants = [source.replace(row+"\n","",1),source.replace(row,row+"\n"+row,1),
                    "\n".join(lines[:-1]),"\n".join(lines[1:]),
                    source+"BENCH_FAIL,unexpected\n",source+"BENCH_ERROR,pixels\n",
                    source.replace(row,row.replace(",1,100,2,103,",",1,100,2,999,")),
                    source.replace("BENCH_CASE,0,320,32,32,SRAM","BENCH_CASE,0,321,32,32,SRAM")]
        for variant in variants:
            with self.subTest(variant=variant[:80]),self.assertRaises(ValueError):
                results.parse(variant)
        with self.assertRaises(ValueError):
            results.parse(source,expected_build="another-build")

    def test_invalid_batch_preserves_raw(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                results.write_outputs(Path(directory),"BENCH_ERROR,pixels\n")
            self.assertEqual((Path(directory)/"serial.log").read_text(),"BENCH_ERROR,pixels\n")
            self.assertFalse((Path(directory)/"RESULTS.md").exists())

class CpuKernel(unittest.TestCase):
    def test_exact_cpu_and_reorder(self):
        compiler = shutil.which("c++")
        self.assertIsNotNone(compiler,"host C++ compiler required for CPU correctness check")
        source = r'''
        #include "cpu.h"
        #include <vector>
        #include <cassert>
        int main() {
          for (unsigned w : {320u,512u}) for(unsigned h : {32u,240u,384u}) {
            unsigned count=w*h;
            std::vector<uint8_t> linear(count), signal(count), stage(count), a(count*3+64,0xA5), b(a);
            for(unsigned i=0;i<count;++i) {linear[i]=(i*17+9)&255;signal[i^2]=linear[i];}
            cpu_signal(signal.data(),a.data(),w,h);
            cpu_linear(linear.data(),b.data(),w,h);
            assert(a==b);
            cpu_reorder(signal.data(),stage.data(),count);
            assert(stage==linear);
            for(unsigned i=0;i<count;++i) {
              assert(a[i*3]==((linear[i]>>4)&3)*85);
              assert(a[i*3+1]==((linear[i]>>2)&3)*85);
              assert(a[i*3+2]==(linear[i]&3)*85);
            }
            for(unsigned i=count*3;i<a.size();++i)assert(a[i]==0xA5);
          }
        }'''
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "test.cpp").write_text(source)
            subprocess.run([compiler,"-std=c++17","-O2","-Wall","-Wextra","-Werror",
                            "-I",str(HERE/"main"),"-I",str(ROOT/"vdp/video"),
                            str(HERE/"main/cpu.cpp"),str(path/"test.cpp"),"-o",str(path/"test")],check=True)
            subprocess.run([str(path/"test")],check=True)

if __name__=="__main__":
    unittest.main(verbosity=2)
