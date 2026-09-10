"""Local RGB222 regression: sanitizer C++ tests and actual Chromium WebGL.

Never connects to the bench. The preview/evidence live under ignored agents/.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


def main():
    spec = importlib.util.spec_from_file_location('host', ROOT /
        'docs/tasks/PORT-003/phase-f/scripts/run-host-regressions.py')
    host = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(host)
    results = []
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        sources = ['vdp/video/extender/display/presentation_snapshot_pool.cpp',
                   'vdp/video/extender/network/opaque_message.cpp',
                   'vdp/video/extender/web/browser_video_provider.cpp']
        results.append(host.compile_and_run(directory/'rgb222', sources +
            ['tests/browser_rgb222_test.cpp'], 'rgb222-publisher',
            ['-I', str(ROOT/'vdp/video'), '-Wall', '-Wextra', '-Werror']))
        results.append(host.compile_and_run(directory/'pool',
            [sources[0], 'docs/tasks/PORT-003/phase-f/tests/snapshot_pool_tests.cpp'],
            'snapshot-pool', ['-I', str(ROOT/'vdp/video'), '-Wall', '-Wextra', '-Werror']))
        results.append(host.compile_and_run(directory/'controller', host.CONTROLLER_SOURCES +
            ['docs/tasks/PORT-003/phase-f/tests/snapshot_controller_tests.cpp'],
            'snapshot-controller', host.COMPATIBILITY_FLAGS))
    subprocess.run([str(ROOT/'.venv/bin/python'),
        'docs/tasks/PORT-003/phase-f/scripts/run-network-host-tests.py',
        '--project-root', str(ROOT)], cwd=ROOT, check=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(
        Quiet, directory=str(ROOT/'vdp/video/extender/web')))
    Thread(target=server.serve_forever, daemon=True).start()
    output = ROOT/'agents/rgb222-review'
    output.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True,
                args=['--enable-unsafe-swiftshader'])
            page = browser.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            checked = page.evaluate('''async () => {
              const {parseFrame, BrowserCreditState} = await import('/frame_protocol.js');
              const {WebGL2Presenter} = await import('/webgl2_presenter.js');
              const canvas = document.createElement('canvas');
              document.body.append(canvas);
              const presenter = new WebGL2Presenter(canvas);
              const gl = presenter.gl;
              function frame(format, w=8, h=8, padding=0) {
                const stride = w * (format === 2 ? 1 : 3) + padding;
                const buffer = new ArrayBuffer(32 + stride*h);
                const bytes = new Uint8Array(buffer), v = new DataView(buffer);
                bytes.set([69,86,70,49,1,32,format,3]);
                v.setUint16(12,w,true); v.setUint16(14,h,true);
                v.setUint32(16,stride,true); v.setUint32(20,stride*h,true);
                v.setUint32(24,16667,true);
                for(let y=0;y<h;y++) for(let x=0;x<w;x++) {
                  const colour = (y*w+x)%64;
                  const start = 32+y*stride+x*(format === 2 ? 1 : 3);
                  if(format===2) bytes[start]=colour;
                  else bytes.set([(colour%4)*85, (Math.floor(colour/4)%4)*85,
                                  Math.floor(colour/16)*85],start);
                }
                return buffer;
              }
              let colours=0;
              // Format switches at constant dimensions must reallocate texture;
              // padded rows, resize, and minimum/maximum surfaces also work.
              for(const [format,w,h,pad] of [[2,8,8,0],[1,8,8,0],
                  [2,8,8,3],[1,8,8,3],[2,1,1,0],[2,1024,768,0],[2,8,8,0]]) {
                presenter.present(parseFrame(frame(format,w,h,pad)));
                const pixels = new Uint8Array(w*h*4);
                gl.readPixels(0,0,w,h,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
                if(gl.getError() !== gl.NO_ERROR) throw new Error('WebGL error');
                for(let y=0;y<h;y++) for(let x=0;x<w;x++) {
                  const c=(y*w+x)%64, offset=((h-1-y)*w+x)*4;
                  const expected=[(c%4)*85,(Math.floor(c/4)%4)*85,Math.floor(c/16)*85,255];
                  for(let k=0;k<4;k++) if(pixels[offset+k]!==expected[k])
                    throw new Error(`colour/orientation mismatch ${format} ${x},${y} ${k}`);
                  colours++;
                }
              }
              let rejected=0;
              const bad=[b=>new DataView(b).setUint8(6,99),
                b=>new DataView(b).setUint32(16,7,true),
                b=>new DataView(b).setUint32(20,63,true),
                b=>new DataView(b).setUint16(12,0,true),
                b=>new DataView(b).setUint16(12,1025,true),
                b=>new DataView(b).setUint32(28,1,true)];
              for(const mutate of bad) {
                const b=frame(2); mutate(b);
                try { parseFrame(b); } catch(e) { rejected++; }
              }
              for(const b of [frame(2).slice(0,-1),new ArrayBuffer(20)]) {
                try { parseFrame(b); } catch(e) { rejected++; }
              }
              if(rejected!==8) throw new Error('malformed frame accepted');
              const state=new BrowserCreditState(), credits=[];
              state.opened(x=>credits.push(x)); state.acceptedFrame();
              if(credits.length!==1) throw new Error('premature credit');
              state.presented(x=>credits.push(x));
              if(credits.length!==2) throw new Error('missing next credit');
              state.disconnected(); canvas.remove();
              return {colours,rejected,formatSwitches:true,paddedRows:true,credit:true};
            }''')
            page.click('#demo')
            page.wait_for_timeout(1500)
            assert page.locator('#surface').inner_text().endswith('RGB222')
            assert float(page.locator('#fps').inner_text()) > 5
            assert not errors, errors
            page.screenshot(path=str(output/'browser.png'))
            results.append({'id':'chromium-rgb222', 'status':'pass', **checked,
                            'local_demo_fps':page.locator('#fps').inner_text()})
            browser.close()
    finally:
        server.shutdown()
    (output/'results.json').write_text(json.dumps(results, indent=2)+'\n')
    print('PASS: all RGB222 colours, RGB888 fallback, resize/stride, malformed frames, credit and local presentation above 5 fps')


if __name__ == '__main__':
    main()
