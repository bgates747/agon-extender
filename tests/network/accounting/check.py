#!/usr/bin/env python3
"""Finite source/model/actual socket checks only; never bench, server or firmware."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,time
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--baseline-root',type=Path,required=True);a=p.parse_args()
R=Path(__file__).resolve().parents[3];D=a.output.resolve();D.mkdir(parents=True,exist_ok=False)
T=Path(__file__).resolve().parent;B=R/'vdp/video/extender/network/messages'
report=dict(passed=False,scope='Actual model/recorder/TcpClient with deterministic clock and link-wrapped POSIX; no external socket/hardware/firmware execution',steps=[])
started=time.monotonic()
names=sorted({*T.rglob('*.cpp'),*T.rglob('*.h'),Path(__file__),
 *B.glob('*.hpp'),*B.glob('*.cpp'),R/'scripts/build_p4.py',R/'scripts/validate_p4_build.py',
 R/'vdp/build/p4-profiles.json',
 R/'vdp/video/extender/network/wired_network_service.cpp',
 R/'vdp/video/extender/transport/console_hardware.inc',
 a.baseline_root.resolve()/'vdp/video/extender/network/messages/tcp_client.cpp'})
inputs={str(n):hashlib.sha256(n.read_bytes()).hexdigest() for n in names}
def run(label,argv):
 with (D/(label+'.log')).open('x') as f:
  result=subprocess.run(list(map(str,argv)),stdout=f,stderr=subprocess.STDOUT,timeout=90,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1:abort_on_error=1'))
 report['steps'].append(dict(label=label,argv=list(map(str,argv)),returncode=result.returncode));assert result.returncode==0,label
 return (D/(label+'.log')).read_text()
try:
 common=['c++','-std=c++17','-Wall','-Wextra','-Werror','-O2','-g','-pthread','-I'+str(R/'vdp/video'),'-I'+str(T/'fake')]
 sanitizers=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
 run('model-link',common+sanitizers+[T/'model.cpp','-o',D/'model']);run('model-run',[D/'model'])
 wrap=['-Wl,--wrap='+x for x in ['socket','fcntl','connect','close','recv','send']]
 outputs={}
 for enabled in (False,True):
  arm='on' if enabled else 'off'
  argv=common+sanitizers+(['-DAGON_EXTENDER_NM_ACCOUNTING=1',B/'accounting.cpp'] if enabled else [])+[T/'socket.cpp',B/'tcp_client.cpp',*wrap,'-o',D/('socket-'+arm)]
  run('socket-'+arm+'-link',argv);outputs[arm]=run('socket-'+arm+'-run',[D/('socket-'+arm)])
 assert outputs['off'].splitlines()[0]==outputs['on'].splitlines()[0]
 frames=[json.loads(x) for x in outputs['on'].splitlines()[1:]];assert len(frames)==2
 for sample in frames:
  assert sample['schema']=='p4-nm-accounting-r01' and sample['cpu_accounting'] is False and sample['inclusive_nonadditive'] and not sample['quiescence_proven']
  assert not sample['saturated'] and not sample['clock_invalid'] and not sample['lifecycle_invalid']
  rows={r['metric']:r for r in sample['rows']}
  assert rows['socket_read']['calls']==4 and rows['socket_read']['units']==1 and rows['socket_read']['would_block']==1 and rows['socket_read']['closed']==1 and rows['socket_read']['errors']==1
  assert rows['socket_write']['calls']==3 and rows['socket_write']['units']==1 and rows['socket_write']['would_block']==1 and rows['socket_write']['errors']==1
 assert frames[0]['rows'][4]['active']==1 and frames[1]['rows'][4]['active']==0
 assert frames[1]['rows'][5]['calls']==200 and frames[1]['rows'][5]['active']==0
 # Actual OFF source object is compared with the unchanged installed-source
 # TcpClient at each optimization, including relocation-bearing disassembly.
 for opt in ('-Os','-O2'):
  files=[];dis=[]
  for name,root in [('base',a.baseline_root.resolve()),('off',R)]:
   obj=D/(name+opt[1:]+'.o');files.append(obj)
   run(name+opt[1:]+'-compile',['c++','-std=c++17',opt,'-I'+str(root/'vdp/video'),'-c',root/'vdp/video/extender/network/messages/tcp_client.cpp','-o',obj])
   text=run(name+opt[1:]+'-disassembly',['objdump','-dr',obj]);dis.append('\n'.join(text.splitlines()[3:]))
  assert dis[0]==dis[1], 'Default-OFF actual socket object changed at '+opt
  symbols=run('off'+opt[1:]+'-symbols',['nm','-C',files[1]]);assert 'accounting::' not in symbols
 runtime_outputs={}
 for enabled in (False,True):
  arm='on' if enabled else 'off'
  argv=common+sanitizers+(['-DAGON_EXTENDER_NM_ACCOUNTING=1',B/'accounting.cpp'] if enabled else [])+[T/'runtime.cpp',B/'tcp_client.cpp',*wrap,'-o',D/('runtime-'+arm)]
  run('runtime-'+arm+'-link',argv);runtime_outputs[arm]=run('runtime-'+arm+'-run',[D/('runtime-'+arm)])
 assert runtime_outputs['off'].splitlines()[0]==runtime_outputs['on'].splitlines()[0]
 sample=json.loads(runtime_outputs['on'].splitlines()[1]);rows={r['metric']:r for r in sample['rows']}
 assert not any((sample['saturated'],sample['clock_invalid'],sample['lifecycle_invalid']))
 assert all(r['active']==0 for r in rows.values())
 assert rows['submit']['calls']==1 and rows['submit']['units']==20
 assert rows['queue_wait']['calls']==1 and rows['queue_wait']['units']==20
 assert rows['peer_request']['calls']==1 and rows['peer_request']['units']==14
 assert rows['work_complete_attempt']['calls']==1 and rows['work_complete_attempt']['units']==14
 assert rows['take_reply']['units']==14
 # Exercise actual selector rather than a parallel test-only flag model.
 import importlib.util
 spec=importlib.util.spec_from_file_location('accounting_build',R/'scripts/build_p4.py')
 import sys;sys.path.insert(0,str(R/'scripts'))
 build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
 doc=json.loads((R/'vdp/build/p4-profiles.json').read_text())
 off=build.select_display_profile(doc,'p4-console','p4-pc','hdmi',network_messages=True)
 on=build.select_display_profile(doc,'p4-console','p4-pc','hdmi',network_messages=True,nm_accounting=True)
 assert 'AGON_EXTENDER_NM_ACCOUNTING=1' not in off['definitions']
 assert 'AGON_EXTENDER_NM_ACCOUNTING=1' in on['definitions']
 assert 'video/extender/network/messages/accounting.cpp' in on['sources'] and 'video/extender/network/messages/accounting.cpp' not in off['sources']
 for kw in ({'nm_accounting':True},{'nm_accounting':True,'network_messages':True,'network_parallel':True}):
  try:build.select_display_profile(doc,'p4-console','p4-pc','hdmi',**kw)
  except SystemExit:pass
  else:raise AssertionError('Unsupported accounting profile admitted')
 assert inputs=={str(n):hashlib.sha256(n.read_bytes()).hexdigest() for n in names}, 'Source input changed during checks'
 report.update(passed=True,actual_runtime_reply_equal=True,actual_selector_checked=True,actual_socket_output_equal=True,off_object_equivalence=['-Os','-O2'],threaded_recorder_events=200,exclusive_CPU_claim=False)
finally:
 report['seconds']=time.monotonic()-started
 report['inputs']=inputs
 (D/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
