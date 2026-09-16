"""Create isolated candidate from pinned local r43 build; never edit parent."""
from pathlib import Path
import argparse,configparser,subprocess,shutil,json,datetime,hashlib
p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
a.parent=a.parent.resolve();a.out=a.out.resolve();a.out.mkdir(exist_ok=False)
subprocess.run(['cp','-a','--reflink=auto',str(a.parent/'source'),str(a.out/'source')],check=True)
code=Path(__file__).resolve().parent;v=a.out/'source/vdp/video';dest=v/'extender/diagnostics/rle2';dest.mkdir(parents=True)
for n in ('rle2.hpp','bench.hpp'):shutil.copy2(code/n,dest/n)
f=v/'extender/network/wired_network_service.cpp';s=f.read_text();s='#include "extender/diagnostics/rle2/bench.hpp"\n'+s;s=s.replace('config.max_uri_handlers = 6;', 'config.max_uri_handlers = 7;');needle='  httpd_uri_t video{};';assert needle in s;s=s.replace(needle,'''  httpd_uri_t codec{};codec.uri="/diagnostics/rle2";codec.method=HTTP_GET;codec.handler=&rle2bench::handler;
  if(httpd_register_uri_handler(server,&codec)!=ESP_OK){http_fault_=true;stopHttp();return false;}
'''+needle);f.write_text(s)
f=v/'vdu_buffered.h';s=f.read_text();s='#include "extender/diagnostics/rle2/rle2.hpp"\n'+s;start=s.index('void VDUStreamProcessor::bufferDecompress(');pos=s.index('\n\t// Validate the compression header',start);s=s[:pos]+'\n'+(code/'asset.inc').read_text()+s[pos:];f.write_text(s)
shutil.copy2(a.parent/'sdkconfig',a.out/'sdkconfig');c=configparser.ConfigParser(interpolation=None);c.optionxform=str;c.read(a.parent/'platformio.ini');c['platformio']['build_dir']=str(a.out/'build');c['env:p4-console']['board_build.esp-idf.sdkconfig_path']=str(a.out/'sdkconfig')
with (a.out/'platformio.ini').open('w') as f:c.write(f)
identity='rle2-p4-r01-b'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-%H-%M-%SZ')
m=dict(build_id=identity,parent_build_id=json.loads((a.parent/'manifest.json').read_text())['build_id'],contract_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),inputs={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in code.iterdir() if x.is_file()})
(a.out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(identity)
