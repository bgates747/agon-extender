"""Exercise the actual native USB report decoder with sanitizers."""
from pathlib import Path
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temp:
    binary = Path(temp)/'usb-keyboard'
    subprocess.run(['c++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', '-I'+str(ROOT/'vdp/video'),
                    str(ROOT/'tests/usb_boot_keyboard_test.cpp'), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
