#!/usr/bin/env python3
"""Build NET-008's stopped P4-PC UART2 appliance, never access a device."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
IDF=ROOT/'agents/build001/native-tools/esp-idf'
PIN='b774170ff46c393eeb5e495ea37936038d3f4f4f'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);p.add_argument('--build-id',required=True)
 p.add_argument('--tools-path',required=True,type=Path);p.add_argument('--python-env',required=True,type=Path);a=p.parse_args()
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True):raise SystemExit('Commit inputs before identified build')
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=IDF,text=True).strip()==PIN
 out=a.output.resolve();out.mkdir(exist_ok=False)
 project=out/'project';shutil.copytree(ROOT/'vdp/fixtures/esp8266_uart',project)
 files=[*sorted((ROOT/'vdp/fixtures/esp8266_uart').rglob('*')),Path(__file__).resolve(),ROOT/'vdp/partitions.csv',ROOT/'vdp/build/boards/p4-pc.json']
 inputs={str(x.relative_to(ROOT)):digest(x) for x in files if x.is_file()}
 sdk=out/'sdkconfig';sdk.write_text((project/'sdkconfig.defaults').read_text()+f'\nCONFIG_PARTITION_TABLE_CUSTOM=y\nCONFIG_PARTITION_TABLE_CUSTOM_FILENAME="{ROOT / "vdp/partitions.csv"}"\n')
 # Use explicit host-native overrides, as the maintained P4 builder does.
 # The historical native-tools compiler is x86-64 and its Python env is stale
 # after Pi migration; neither is a valid implicit build environment.
 tools=a.tools_path.resolve();pyenv=a.python_env.resolve()
 env=os.environ.copy();env.update(IDF_PATH=str(IDF),IDF_TOOLS_PATH=str(tools),IDF_PYTHON_ENV_PATH=str(pyenv),ESP_IDF_VERSION='5.5',IDF_COMPONENT_MANAGER='0')
 env['PATH']=os.pathsep.join([str(pyenv/'bin'),*[str(p) for p in tools.glob('tools/**/bin') if p.is_dir()],env['PATH']])
 env['ESP_ROM_ELF_DIR']=str(next(tools.glob('tools/esp-rom-elfs/*')))
 cmd=[str(pyenv/'bin/python'),str(IDF/'tools/idf.py'),'-C',str(project),'-B',str(out/'build'),'-DIDF_TARGET=esp32p4',f'-DSDKCONFIG={sdk}',f'-DNET008_BUILD_ID={a.build_id}',f'-DNET008_SOURCE_COMMIT={commit}','build']
 (out/'command.json').write_text(json.dumps({'argv':cmd,'environment':{k:env[k] for k in ['IDF_PATH','IDF_TOOLS_PATH','IDF_PYTHON_ENV_PATH','IDF_COMPONENT_MANAGER']}},indent=2)+'\n')
 start=time.monotonic()
 with (out/'build.log').open('x') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise SystemExit('Build failed; see '+str(out/'build.log'))
 layout=json.loads((out/'build/flasher_args.json').read_text());assert layout['app']['offset']=='0x20000'
 config=sdk.read_text();assert 'CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y' in config and 'CONFIG_ESP32P4_REV_MIN_FULL=100' in config
 app=out/'build'/layout['app']['file']
 assert all(digest(ROOT/n)==h for n,h in inputs.items()),'Source changed during build'
 m={'source_commit':commit,'build_id':a.build_id,'idf_commit':PIN,'board':'Olimex ESP32-P4-PC Rev C','profile':'NET-008 isolated UART2 appliance','source_inputs':inputs,
    'app':{'path':str(app),'bytes':app.stat().st_size,'sha256':digest(app),'offset':layout['app']['offset']},'duration_host_seconds':time.monotonic()-start,
    'gpio':{'tx':47,'rx':48,'baud':115200,'ldo4_mv':3300},'start_required':True,'app_only_install':True,'emulated':False,'hardware_tested':False}
 (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
if __name__=='__main__':main()
