"""Passive Nurples UART attribution; no firmware, serial or GPIO operations.

Reuse the maintained physical-channel decoder/packing contract. The caller
owns browser readiness and the single fixture reset after delivered samples.
"""
import argparse,datetime,json,subprocess,sys,time,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--helper-dir',type=Path,default=Path(__file__).resolve().parents[2]/'AUDIT-005/scripts');a=p.parse_args()
sys.path.insert(0,str(a.helper_dir));import capture_trace as helper
helper.SAMPLES=80*helper.RATE
out=a.output;out.mkdir(parents=True,exist_ok=False)
record=dict(procedure='QUAL-003 N04ad passive Nurples attribution',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sample_rate_hz=helper.RATE,expected_samples=helper.SAMPLES,script_sha256=helper.sha(__file__),helper_sha256=helper.sha(a.helper_dir/'capture_trace.py'),acquisition_pass=False)
process=None
try:
 assert shutil.disk_usage(out).free>helper.SAMPLES*3,'Insufficient acquisition/packing space'
 connection=helper.discover(out);raw=out/'logic.raw'
 cmd=['sigrok-cli','--loglevel','2','--driver','fx2lafw:conn='+connection,'--config',f'samplerate={helper.RATE}','--channels','D1,D3,D4,D6','--samples',str(helper.SAMPLES),'--output-format','binary','--output-file',str(raw)]
 record['argv']=cmd
 with (out/'sigrok.log').open('wb') as log:
  process=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);start=time.monotonic()
  while time.monotonic()-start<5:
   assert process.poll() is None,'Capture stopped before readiness'
   if raw.exists() and raw.stat().st_size>=65536:break
   time.sleep(.05)
  else:raise RuntimeError('No samples delivered; caller must not reset')
  (out/'ready.json').write_text(json.dumps(dict(delivered_bytes=raw.stat().st_size,utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))+'\n')
  process.wait(timeout=110)
 record['acquisition_wall_seconds']=time.monotonic()-start;record['exit_code']=process.returncode
 record['raw_sha256']=helper.pack_raw(raw,out/'logic.sr');record['acquisition']=helper.inspect(out/'logic.sr');record['acquisition_pass']=process.returncode==0 and record['acquisition']['acquisition_pass']
except Exception as e:record['error']=str(e)
finally:
 if process is not None and process.poll() is None:
  process.terminate()
  try:process.wait(timeout=5)
  except subprocess.TimeoutExpired:process.kill();process.wait()
 record['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'capture-result.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2),flush=True)
raise SystemExit(not record['acquisition_pass'])
