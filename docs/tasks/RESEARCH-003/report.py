#!/usr/bin/env python3
from pathlib import Path
import json,statistics,hashlib
r=Path(__file__).resolve().parent;rows=[]
for p in sorted((r/'evidence').glob('*.json')):
 d=json.loads(p.read_text())
 if d.get('state')!='complete':continue
 v=d['device'];samples=d['samples'];dt=v['elapsed_us']/1e6
 intervals=[(b['host_ns']-a['host_ns'])/1e6 for a,b in zip(samples[60:],samples[61:])]
 intervals.sort()
 row={'case':p.stem,'mode':d['mode'],'target':d['target'],'produced_fps':v['produced']/dt,'received_fps':len(samples)/dt,'payload_mbps':d['device_window_payload_mbps'],'render_mean_ms':v['render_mean_us']/1000,'render_p95_ms':v['render_p95_us']/1000,'render_max_ms':v['render_max_us']/1000,'producer_interval_p95_ms':v['interval_p95_us']/1000,'send_mean_ms':v['send_mean_us']/1000,'send_p95_ms':v['send_p95_us']/1000,'dropped':v['dropped'],'received':len(samples),'host_interval_p95_ms':intervals[int((len(intervals)-1)*.95)] if intervals else None,'validation_ms':d['validation_ms']}
 rows.append(row)
(r/'SUMMARY.json').write_text(json.dumps(rows,indent=2)+'\n')
lines=['# Standalone P4 measured results','', '| Case | Produced/s | Received/s | Payload Mbit/s | Render mean ms | Render p95 ms | Send mean ms | Dropped slots |', '|---|---:|---:|---:|---:|---:|---:|---:|']
for d in sorted(rows,key=lambda x:(-x['target'],x['received_fps'] if x['mode']!='render' else 100)):
 lines.append(f"| {d['case']} | {d['produced_fps']:.3f} | {d['received_fps']:.3f} | {d['payload_mbps']:.3f} | {d['render_mean_ms']:.3f} | {d['render_p95_ms']:.3f} | {d['send_mean_ms']:.3f} | {d['dropped']} |")
(r/'TABLES.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
