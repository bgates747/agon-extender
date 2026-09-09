"""Synthetic clocks deliberately differ by an hour; missing data stays missing."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('analysis',ROOT/'scripts/analyze_browser_timing.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
browser=[{'event':'key_event','event_id':1,'ms':10,'sid':7},
 {'event':'key_send','event_id':1,'ms':11,'sid':7,'ordinal':1},
 {'event':'key_ack','ms':20,'sid':7,'ordinal':1},
 {'event':'frame_received','ms':100,'sid':8,'seq':4},
 {'event':'frame_submitted','ms':105,'sid':8,'seq':4}]
base=3_600_000_000
rows=[]
def p(us,event,id=0,a=0,b=0,c=0): rows.append(f'{len(rows)},{base+us},{event},{id},{a},{b},{c}')
p(0,'video_open',8,50)
p(1000,'key_message',7,1,0,51)
p(1500,'key_dequeue',7,1,4,1)
p(2000,'uart_submit',1,6,0x610481,0x0116)
p(3000,'vdu_received',1,97,1)
p(4000,'draw_flush_done',2)
p(5000,'snapshot',4,base+4500,base+4900)
p(6000,'video_send_start',4,50,921632)
p(7000,'video_send_end',4,50,0)
report={'rows':browser,'p4':'index,us,event,id,a,b,c\n'+'\n'.join(rows),'overwritten':0}
r=m.analyze(report)
assert r['intervals']['browser_event_to_guaranteed_frame_ms']['median_ms']==95
assert r['intervals']['p4_uart_submit_to_echo_ms']['median_ms']==1
assert r['intervals']['p4_admission_to_uart_submit_ms']['median_ms']==1
assert r['intervals']['p4_snapshot_compose_ms']['median_ms']==.4
assert r['intervals']['browser_send_to_ack_ms']['median_ms']==9
# Composition preceding flush cannot be represented as confirmed visibility.
report['p4']=report['p4'].replace(str(base+4500),str(base+3500))
assert m.analyze(report)['intervals']['browser_event_to_guaranteed_frame_ms']['n']==0
report['p4']=''
assert m.analyze(report)['intervals']['p4_uart_submit_to_echo_ms']['n']==0
print('PASS: independent clocks, guaranteed frame association, and missing/ambiguous data exclusion')
