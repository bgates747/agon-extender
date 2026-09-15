"""Validate parser native-wait attribution alongside its unchanged refresh trace."""
import argparse,json,re,statistics
from pathlib import Path
from analyze_refresh_trace import analyze

def summarize(v):
 s=sorted(v);return dict(count=len(s),mean=statistics.mean(s),p95=s[(len(s)*95+99)//100-1],maximum=max(s))
def read(text,nonce,expected=2400):
 trace=analyze(text,nonce,expected)
 heads=list(re.finditer(r'NPNATIVE begin '+re.escape(nonce)+r' (\d+) ([01])\r?\n',text));assert len(heads)==1
 h=heads[0];assert tuple(map(int,h.groups()))==(expected,0)
 tail=text[h.end():];end=re.search(r'NPNATIVE end '+re.escape(nonce)+r'\r?\n',tail);assert end
 rows=[tuple(map(int,x)) for x in re.findall(r'NPNATIVE row (\d+) (\d+) (\d+) (\d+) (\d+)\r?\n',tail[:end.start()])]
 assert len(rows)==expected and [r[0] for r in rows]==list(range(expected))
 assert all(r[2]<=r[1] and (r[3]>0 or r[1]==r[2]==0) for r in rows)
 window=rows[120:]
 return dict(scope='Diagnostic parser-native mutex acquisition and RX backlog; probe overhead excludes parity qualification',completion_trace=trace,native_wait_ms=summarize([r[1]/1000 for r in window]),largest_acquisition_ms=summarize([r[2]/1000 for r in window]),native_acquisitions_per_refresh=summarize([r[3] for r in window]),rx_buffered_bytes_at_enqueue=summarize([r[4] for r in window]),worst_wait_rows=sorted(rows,key=lambda r:r[1],reverse=True)[:12]),rows
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('capture',type=Path);p.add_argument('--nonce',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 result,rows=read(a.capture.read_text(errors='replace'),a.nonce)
 a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
