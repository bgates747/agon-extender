"""Actual MODE/cursor helper, sanitizers and compiled bad-code controls; no device."""
from pathlib import Path
import argparse,json,subprocess,shutil
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False,parents=True)
src=Path(__file__).resolve().parent;header=(src/'uart0_reply_burst.hpp').read_text()
mutants={
 'stale-flags':header.replace('    io.clear_replies();','    // omitted clear'),
 'ignore-mode':header.replace('if(!io.mode_matches())return false;','if(false)return false;'),
 'ignore-cursor':header.replace('if(io.x()!=x||io.y()!=y)return false;','if(false)return false;'),
 'either-response':header.replace('if(mode&&cursor)return true;','if(mode||cursor)return true;'),
 'retry-refusal':header.replace('if(!io.write(request,sizeof(request)))return false;','if(!io.write(request,sizeof(request)))if(!io.write(request,sizeof(request)))return false;'),
}
rows=[]
for name,h in [('control',header),*mutants.items()]:
 if name!='control':assert h!=header,name
 d=a.output/name;d.mkdir();(d/'uart0_reply_burst.hpp').write_text(h);shutil.copyfile(src/'test_uart0_reply_burst.cpp',d/'test.cpp')
 cmd=['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(d/'test.cpp'),'-o',str(d/'check')]
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=60);(d/'compile.log').write_text(r.stdout+r.stderr);assert r.returncode==0,name
 r=subprocess.run([str(d/'check')],capture_output=True,text=True,timeout=30);(d/'run.log').write_text(r.stdout+r.stderr)
 assert (r.returncode==0)==(name=='control'),(name,r.returncode)
 rows.append(dict(name=name,compiled=True,returncode=r.returncode,expected_pass=name=='control'))
report=dict(passed=True,no_hardware=True,query_kinds=['MODE','cursor'],logical_reply_bytes_per_burst=14,negative_controls=rows,
 cases=['zero/nonzero/mixed cursor','both response orderings','stale flags','missing independent flag','wrong MODE/cursor','refused write/no retry','cancel','24bit clock wrap','stopped clock fuse'])
(a.output/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
