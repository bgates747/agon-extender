"""Reject silent changes to the retained v2.16.0 dispatcher/reply contract."""
from pathlib import Path
import hashlib,re
from processed_keyboard_test import function
root=Path(__file__).resolve().parents[1]
s=(root/'vdp/video/vdu_audio.h').read_text()
# Only the unavailable sample-debug backend is excluded; its ID read is shared.
s=s.replace('\t\t\t\t\t#ifndef AGON_EXTENDER_P4_BOOT\n\t\t\t\t\t// P4 has no sample backend. Its debug command still consumes bufferId.\n','')
s=s.replace('\n\t\t\t\t\t#else\n\t\t\t\t\t(void)bufferId;\n\t\t\t\t\t#endif','')
expected={'void VDUStreamProcessor::vdu_sys_audio(': '47b6d3100a878d4177bcd81ec869843b5a1a1de71e8dedb194149c7b726deec3', 'void VDUStreamProcessor::sendAudioStatus(': '254ec9ccdf0fd92898e5fc88dae27527cf3078bf403363818b700dff38783d5c'}
for signature,digest in expected.items():
 assert hashlib.sha256(function(s,signature).encode()).hexdigest()==digest,signature
print("PASS: shared dispatcher and reply function match pinned stock v2.16.0")
