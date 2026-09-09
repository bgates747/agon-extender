"""Exercise maintained input helper, event queue, callbacks and serializer.

Compile the exact retained method bodies with a bounded variable/context fake;
do not substitute a second packet constructor. Full P4 integration is separately
compiled and must pass the physical test. Optional output is the actual host
serializer's twelve-event byte stream for the paired eZ80 emulator review.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def function(text, signature):
    start = text.index(signature)
    brace = text.index('{', start)
    depth = 1
    end = brace+1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]+'\n'


def verify(output=None):
    video = ROOT/'vdp/video'
    source = (video/'vdu_stream_processor.h').read_text()
    helpers = (video/'extender/input/unavailable_input_adapter.hpp').read_text()
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        defines = [line for line in (video/'agon.h').read_text().splitlines()
                   if re.match(r'#define\s+(VDPVAR_|PACKET_|CALLBACK_)', line)]
        (temp/'constants.inc').write_text('\n'.join(defines)+'\n')
        parts = [function(helpers, name) for name in (
            'inline void setKeyboardLayout(', 'inline bool getKeyboardKey(',
            'inline std::uint8_t packKeyboardModifiers(', 'inline bool shiftKeyPressed(',
            'inline bool ctrlKeyPressed(', 'inline void getKeyboardState(',
            'inline void setKeyboardState(')]
        parts += [function(source, name) for name in (
            'void VDUStreamProcessor::send_packet(', 'inline void VDUStreamProcessor::sendKeyboardData(',
            'void VDUStreamProcessor::processEventQueue(',
            'void VDUStreamProcessor::handleKeyboardAndMouse(')]
        parts += [function((video/'vdu_sys.h').read_text(), 'void VDUStreamProcessor::sendGeneralPoll(')]
        parts += [function((video/'extender/diagnostic/keyboard_probe_stream.hpp').read_text(),
                           'inline constexpr agon::extender::input::ProcessedKey keyboardProbeEvents[]')+';']
        (temp/'retained.inc').write_text('\n'.join(parts))
        binary = temp/'keyboard-test'
        subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-Wno-unused-parameter',
                        '-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(temp),'-I'+str(video),
                        str(ROOT/'tests/processed_keyboard_test.cpp'),'-o',str(binary)], check=True)
        subprocess.run([str(binary), *([str(output.resolve())] if output else [])], check=True)
    print('PASS: processed FIFO and retained keyboard callbacks/serializer')
    if output:
        paths = [Path(__file__), ROOT/'tests/processed_keyboard_test.cpp',
                 video/'agon.h', video/'vdu_stream_processor.h', video/'vdu_sys.h',
                 video/'vdp_variables.h', video/'utils/thread_safe_variant_deque.h',
                 video/'extender/input/processed_keyboard.hpp',
                 video/'extender/input/unavailable_input_adapter.hpp',
                 video/'extender/diagnostic/keyboard_probe_stream.hpp']
        sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        output.with_suffix('.json').write_text(json.dumps({
            'outcome':'pass', 'packet_sha256':sha(output),
            'scope':'retained sender methods with variable/context fake; not P4 runtime',
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'source_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)),
            'inputs':{str(p.relative_to(ROOT)):sha(p) for p in paths},
        },indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-packets', type=Path)
    verify(parser.parse_args().emit_packets)
