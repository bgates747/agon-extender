"""Run the actual PlatformIO selection hook against temporary target trees."""
import json
from pathlib import Path
import runpy
import tempfile
ROOT = Path(__file__).resolve().parents[1]

class Environment:
    def __init__(self, path): self.path=path
    def subst(self, value):
        return {'$PIOENV':'p4-usb-keyboard','$PROJECT_DIR':str(self.path),
                '$BUILD_DIR':str(self.path/'build')}[value]
    def BuildSources(self,*args,**kwargs): pass

with tempfile.TemporaryDirectory() as temp:
    path=Path(temp)
    for sub in ('video','pio'): (path/sub).mkdir()
    (path/'video/main.cpp').write_text('void setup() {}\n')
    (path/'pio/p4-usb-keyboard-dependencies.lock').write_text('dependencies: {}\n')
    selection={'environment':'p4-usb-keyboard','generated_build_files':['video/CMakeLists.txt'],
               'project_translation_units':['video/main.cpp'],'vendored_translation_units':[],
               'managed_dependencies':{'espressif/usb_host_hid':'1.2.1','espressif/esp-dl':'3.3.9'},
               'dependency_lock':'pio/p4-usb-keyboard-dependencies.lock'}
    def run():
        (path/'pio/p4-usb-keyboard-source-selection.json').write_text(json.dumps(selection))
        runpy.run_path(str(ROOT/'vdp/pio/select_sources.py'),
                      init_globals={'env':Environment(path),'Import':lambda *_:None})
    run()
    manifest=path/'video/idf_component.yml'
    assert '==1.2.1' in manifest.read_text()
    assert 'idf_build_set_property(DEPENDENCIES_LOCK' in (path/'CMakeLists.txt').read_text()
    assert 'pio/p4-usb-keyboard-dependencies.lock' in (path/'CMakeLists.txt').read_text()
    del selection['managed_dependencies']; del selection['dependency_lock']
    run()
    assert not manifest.exists()
    assert 'DEPENDENCIES_LOCK' not in (path/'CMakeLists.txt').read_text()
    manifest.write_text('dependencies: {custom: "1.0.0"}\n')
    try: run()
    except RuntimeError as error: assert 'non-generated' in str(error)
    else: raise AssertionError('clobbered a non-generated manifest')
    assert 'custom' in manifest.read_text()
print('PASS: target manifest/lock selection, ordinary target restoration, hand-maintained file protection')
