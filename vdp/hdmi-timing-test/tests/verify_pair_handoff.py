"""Build the real standalone IRQ, EOF and reference restore paths against register fakes."""
from pathlib import Path
import os
import subprocess
import tempfile

here = Path(__file__).resolve().parent
pair_dir = here.parent / "pair"
source = (pair_dir / "pair_runtime.inc").read_text()


def region(start, stop):
    begin = source.index(start)
    return source[begin:source.index(stop, begin)]


# This diagnostic includes the actual state and callbacks. Only the target
# fence instruction is translated to its C11 host counterpart.
actual = region("enum { PAIRS_PER_FRAME", "static bool pair_wait_stop(")
actual += region("static void pair_restore(", "esp_err_t pair_driver_run(")
actual = actual.replace('asm volatile("fence iorw,iorw" ::: "memory");',
                        'atomic_thread_fence(memory_order_seq_cst);')
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp)
    (out / "device_callbacks.inc").write_text(actual)
    executable = out / "pair-handoff"
    subprocess.run([os.environ.get("CC", "cc"), "-std=c11", "-O2", "-Wall",
                    "-Wextra", "-Wno-unused-function", "-Wno-unused-const-variable",
                    "-Werror", "-I", str(out), "-I", str(pair_dir),
                    str(here / "pair_handoff_host.c"), "-o", str(executable)], check=True)
    for scenario in ("normal", "stale", "coalesced", "withheld", "invalid",
                     "early-eof", "short", "underrun", "task"):
        subprocess.run([str(executable), scenario], check=True)
