"""Generate block-size tables from completed, bench-free evidence."""
from pathlib import Path
import json,argparse,shutil
p=argparse.ArgumentParser();p.add_argument('--native',type=Path,required=True);p.add_argument('--browser',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parent;e=root/'evidence';native=json.loads((a.native/'results.json').read_text());paired=json.loads((a.browser/'paired.json').read_text());browser=json.loads((a.browser/'results.json').read_text());variants=json.loads((a.native/'variants.json').read_text());full='srle2-o4-b4259840-r1-i0'
for name in ['paired.json','complete.json','edges.json','selected.json']:shutil.copy(a.browser/name,e/('browser-run.json' if name=='complete.json' else name))
(e/'browser.json').write_text(json.dumps([{k:v for k,v in x.items() if k!='samples'} for x in browser],indent=2)+'\n')
lines=['# Order4 block-size measurements','','All comparisons use the same isolated r03 adapter. Encode medians use20 alternating candidate/full-block pairs after two warmups. Native bytes include codec headers. Negative encode delta means faster; positive size delta means larger.','']
for case in ('retained-sprites','sprites1','noise'):
 baseline=next(x for x in native if x['case']==case and x['variant']==full);rle=next(x['bytes'] for x in native if x['case']==case and x['variant']=='rle2')
 lines += [f'## {case} — RLE2 input {rle:,} bytes','','| Block cap | Blocks | Bytes | Size vs full | Linux encode ms | Encode vs paired full |','|---|---:|---:|---:|---:|---:|']
 for v in variants:
  if v['kind']!='srle2':continue
  x=next(x for x in native if x['case']==case and x['variant']==v['id']);t=next(x for x in paired['rows'] if x['case']==case and x['variant']==v['id']);b=v['block'];label='Full input' if b==4259840 else f'{b:,} B';lines.append(f"| {label} | {(rle+b-1)//b} | {x['bytes']:,} | {(x['bytes']/baseline['bytes']-1)*100:+.1f}% | {t['encode_ms']:.3f} | {t['delta_pct']:+.1f}% |")
lines+=['','## Mixed full-size loopback replay','','Pre-encoded frames,30Hz ceiling, headless Chromium/SwiftShader. These are CPU submission cadence and browser decode costs, not P4, Ethernet or physical display measurements.','','| Block cap | Submitted fps | FPS vs full | Mean decode-wall ms |','|---|---:|---:|---:|'];paced=[x for x in browser if x['phase']=='paced'];base=next(x for x in paced if x['variant']==full)
for v in variants:
 x=next(x for x in paced if x['variant']==v['id']);label=v['id'] if v['kind']!='srle2' else 'Full input' if v['block']==4259840 else f"{v['block']:,} B";lines.append(f"| {label} | {x['fps']:.2f} | {(x['fps']/base['fps']-1)*100:+.1f}% | {x['decode_wall_ms']:.3f} |")
(root/'TABLES.md').write_text('\n'.join(lines)+'\n')
