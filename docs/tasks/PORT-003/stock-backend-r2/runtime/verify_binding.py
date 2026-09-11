"""Prove original bodies survive the R1 hardware and R2 access bindings."""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
R1 = HERE.parents[1] / "stock-backend-r1"
sys.path.insert(0, str(R1))
from verify_source import classic_selection, tokens, sha, CONTROLLERS


def original_selection(text):
    text = text.replace(' || defined(AGON_EXTENDER_STOCK_RUNTIME)', '')
    text = text.replace(' && !defined(AGON_EXTENDER_STOCK_RUNTIME)', '')
    text = text.replace('defined(AGON_EXTENDER_STOCK_RUNTIME)', 'defined(AGON_EXTENDER_STOCK_ROWS_PROOF)')
    text = re.sub(r'^(#(?:endif|else))\s*(?://[^\n]*|/\*[^\n]*\*/)?$', r'\1', text, flags=re.M)
    text = classic_selection(text)
    text = re.sub(r'^#define AGON_STOCK_(?:NATIVE|PALETTE|FOREGROUND)_GUARD\n', '', text, flags=re.M)
    text = re.sub(r'^.*[{}] // AGON_STOCK_NATIVE_SCOPE\n', '', text, flags=re.M)
    text = text.replace('#include "extender/display/stock_native_access.hpp"', '')
    return re.sub(r'AGON_STOCK_(?:NATIVE|PALETTE|FOREGROUND)_GUARD;', '', text)


def verify():
    gl = 'vdp/vendor/vdp-gl/src/'
    paths = [gl + f'dispdrivers/{stem}controller.{ext}' for stem in CONTROLLERS for ext in ('h','cpp')]
    paths += [gl + p for p in ('canvas.cpp','canvas.h','displaycontroller.cpp','displaycontroller.h','fabutils.cpp','fabutils.h','codepages.cpp','fabfonts.cpp','fabfonts.h')]
    # The reference is the accepted pre-binding snapshot; only the explicitly
    # listed target directives and guard entries are removed for comparison.
    records=[]
    for path in paths:
        before=subprocess.check_output(['git','show','a773b19:'+path],cwd=ROOT).decode()
        after=(ROOT/path).read_text()
        assert tokens(before)==tokens(original_selection(after)), path
        records.append({'path':path,'source_sha256':sha(after.encode()),'check':'original tokens after only named P4 binding directives/guards'})
    # Official facade/context changes beyond f94c2e4 are guard insertion only.
    for path in ('vdp/video/sprites.h','vdp/video/context.h','vdp/video/context/cursor.h','vdp/video/buffer_stream.h','vdp/video/buffers.h','vdp/video/vdu_buffered.h','vdp/video/extender/port/stock_render_utils.cpp'):
        before=subprocess.check_output(['git','show','f94c2e4:'+path],cwd=ROOT).decode()
        after=(ROOT/path).read_text()
        assert tokens(before)==tokens(original_selection(after)),path
        records.append({'path':path,'source_sha256':sha(after.encode()),'check':'R1 checkpoint plus native guards only'})
    # These existing output-interface call sites only select the new borrowed
    # native controller / stable snapshot owner. No retained VDU body changes.
    for path in ('vdp/video/agon_ps2.h','vdp/video/vdu.h','vdp/video/video.ino','vdp/video/agon_screen.h'):
        before=subprocess.check_output(['git','show','f94c2e4:'+path],cwd=ROOT).decode()
        after=(ROOT/path).read_text()
        selected=original_selection(after)
        selected=re.sub(r'^inline .* (?:activeDisplayController|displaySnapshotPool)\(\) .*\n','',selected,flags=re.M)
        selected=selected.replace('activeDisplayController()', '_VGAController.get()').replace('displaySnapshotPool()', '_VGAController->snapshotPool()')
        assert tokens(before)==tokens(selected),path
        records.append({'path':path,'source_sha256':sha((ROOT/path).read_bytes()),'check':'retained interface body; conditional owner binding and named native guards only'})
    ledger=json.loads((HERE.parent/'scanline-spans.json').read_text())
    selected=(ROOT/'vdp/video/extender/display/stock_scanline.cpp').read_bytes()
    for span in ledger['bodies']:
        source=subprocess.check_output(['git','show',ledger['body_source_checkpoint']+':'+span['source']],cwd=ROOT)
        offset=sum(map(len,source.splitlines(keepends=True)[:span['start_line']-1]))
        body=source[offset:offset+span['bytes']]
        assert sha(body)==span['sha256'] and body in selected and body in (ROOT/span['source']).read_bytes(),span
    return {'files':records,'verbatim_scanline_bodies':5}


if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
