#!/usr/bin/env python3
"""Offline report for paired fixed-source conversion controls; no bench access."""
import argparse, csv, hashlib, html, json
from pathlib import Path
from static_conversion import summarize

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    owner_path=args.evidence/'no-scanout-owner.json'
    owner=json.loads(owner_path.read_text())
    assert owner['outcome']=='completed-and-restored', 'Do not claim an unfinished control/restoration batch completed'
    pairs={};excluded=[];inputs={}
    inputs[str(owner_path)]=digest(owner_path)
    for folder in sorted(args.evidence.glob('BENCH-009-*')):
        record=json.loads((folder/'run.json').read_text())
        if not (folder/'telemetry.json').exists():raise ValueError(f'Unfinished control: {folder}')
        assert digest(folder/'telemetry.json')==record['telemetry_sha256']
        assert digest(folder/'controller.py')==record['host_runner_sha256']
        inputs[str(folder/'run.json')]=digest(folder/'run.json')
        inputs[str(folder/'telemetry.json')]=digest(folder/'telemetry.json')
        if record['outcome'].startswith('invalid-'):
            excluded.append(dict(run=folder.name,mode=record['mode'],reason=record['invalid_reason']))
            continue
        variant=record.get('variant','normal')
        assert record['outcome']==('measured-visual-pass' if variant=='normal' else 'measured-scanout-absent')
        if variant=='normal':assert record['visual_acceptance']=='pass'
        mode=record['mode'];key=(mode,variant)
        assert key not in pairs, 'Do not silently select among duplicate controls'
        summary=summarize(json.loads((folder/'telemetry.json').read_text()),mode,record['display']['height'],record['fixture']['tag'],variant)
        pairs[key]=(record,summary,folder)
    assert set(pairs)=={(m,v) for m in (20,8,136,21,149) for v in ('normal','convert-off')}
    rows=[]
    for mode in (20,8,136,21,149):
        on,on_summary,on_folder=pairs[mode,'normal']
        off,off_summary,off_folder=pairs[mode,'convert-off']
        assert on['fixture']['sha256']==off['fixture']['sha256'], 'The same fixed pattern must run in both variants'
        on_ms=on_summary['median_normalized_frame_ms']['rgb888_expand']
        off_ms=off_summary['median_normalized_frame_ms']['rgb888_expand']
        rows.append(dict(mode=mode,width=on['display']['width'],height=on['display']['height'],colours=on['display']['colors'],double_buffered=on['display']['double_buffered'],scanout_on_expansion_ms=on_ms,scanout_on_expansion_equivalent_fps=1000/on_ms,scanout_off_expansion_ms=off_ms,scanout_off_expansion_equivalent_fps=1000/off_ms,off_time_difference_percent=100*(off_ms-on_ms)/on_ms,scanout_on_preparation_ms=on_summary['median_conversion_attempt_ms'],scanout_on_preparation_equivalent_fps=on_summary['equivalent_conversion_attempt_frames_per_second'],scanout_off_preparation_ms=off_summary['median_conversion_attempt_ms'],scanout_off_preparation_equivalent_fps=off_summary['equivalent_conversion_attempt_frames_per_second'],accepted_hdmi_submissions_per_second=on_summary['median_submissions_per_second'],dma_scanout_hz=on_summary['median_scanout_hz'],on_run=on_folder.name,off_run=off_folder.name,on_summary=on_summary,off_summary=off_summary))
    rows.sort(key=lambda row:row['scanout_on_expansion_ms'],reverse=True)
    args.output.mkdir(parents=True,exist_ok=False)
    dataset=dict(scope='Fixed-source RGB888 conversion, not drawing-command completion or physical displayed FPS',rows=rows,excluded=excluded,inputs=inputs)
    (args.output/'results.json').write_text(json.dumps(dataset,indent=2)+'\n')
    fields=[key for key in rows[0] if not key.endswith('_summary')]
    with (args.output/'results.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        writer.writerows({key:row[key] for key in fields} for row in rows)
    body=[];detail=[]
    for row in rows:
        m=row['mode'];label=f'{m}: {row["width"]}×{row["height"]}, {row["colours"]} colours, '+('double' if row['double_buffered'] else 'single')
        body.append(f'<tr><th>{label}</th><td>{row["scanout_on_expansion_ms"]:.2f}<br><small>{row["scanout_on_expansion_equivalent_fps"]:.1f} frames/s</small></td><td>{row["scanout_off_expansion_ms"]:.2f}<br><small>{row["scanout_off_expansion_equivalent_fps"]:.1f} frames/s</small></td><td>{row["off_time_difference_percent"]:+.1f}%</td><td>{row["accepted_hdmi_submissions_per_second"]:.1f}/s</td><td>{row["dma_scanout_hz"]:.2f} Hz</td></tr>')
        phases=[]
        for key,label in (('row_lock_wait','Row lock waiting'),('row_read_compose','Native-row read/composition'),('rgb888_expand','RGB888 expansion')):
            a=row['on_summary']['median_normalized_frame_ms'][key];b=row['off_summary']['median_normalized_frame_ms'][key]
            phases.append(f'<tr><th>{label}</th><td>{a:.3f} ms · {1000/a:.1f} equivalent frames/s</td><td>{b:.3f} ms · {1000/b:.1f} equivalent frames/s</td></tr>')
        a=row['scanout_on_preparation_ms'];b=row['scanout_off_preparation_ms']
        phases.append(f'<tr><th>Full preparation attempt</th><td>{a:.3f} ms · {1000/a:.1f} equivalent frames/s</td><td>{b:.3f} ms · {1000/b:.1f} equivalent frames/s</td></tr>')
        phases.append(f'<tr><th>Cache writeback/submission</th><td>{row["on_summary"]["median_cache_submit_ms"]:.3f} ms</td><td>Absent</td></tr>')
        svg=(pairs[m,'normal'][2]/'reference.svg').read_text()
        detail.append(f'<details><summary>{label}: phases and reference chart</summary><div class="scroll"><table><thead><tr><th>Phase</th><th>Scanout on</th><th>Scanout absent</th></tr></thead><tbody>'+''.join(phases)+f'</tbody></table></div><figure>{svg}<figcaption>Expected colour chart; all five HDMI charts passed Author visual review. This is a reference drawing, not a captured HDMI frame.</figcaption></figure><p>Runs: <code>{row["on_run"]}</code> / <code>{row["off_run"]}</code></p></details>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Static HDMI conversion controls</title><style>body{font:16px system-ui;max-width:1200px;margin:32px auto;padding:0 20px;color:#e7eef5;background:#111923}h1{font-size:28px}table{border-collapse:collapse;width:100%}th,td{text-align:left;padding:12px;border-bottom:1px solid #354352}small,figcaption{color:#b7c6d5}thead{background:#202c3b}a{color:#8bd3ff}.scroll{overflow:auto}details{margin:20px 0;padding:14px;background:#182434}summary{cursor:pointer}figure{max-width:640px}svg{width:100%;height:auto}code{overflow-wrap:anywhere}li{margin:10px 0}</style><h1>Static HDMI conversion controls</h1><p>The Agon draws each chart once. The P4 repeatedly reads that unchanged image and expands it into RGB888. Each result is the median of three ten-second window means; all five colour charts passed visual review.</p><p><a href="results.csv">Download CSV</a> · <a href="results.json">Data and provenance</a></p><h2>RGB888 expansion</h2><p>Worst expansion time with scanout active first. Equivalent frames/s = 1000 ÷ milliseconds for this phase alone. The on/off time difference uses scanout-on as baseline: 100 × (off − on) / on; negative is faster without scanout.</p><div class="scroll"><table><thead><tr><th>VDP mode</th><th>Scanout on<br>ms/image</th><th>Scanout absent<br>ms/image</th><th>Off time difference</th><th>Accepted HDMI buffers</th><th>DMA cadence</th></tr></thead><tbody>'''+''.join(body)+'''</tbody></table></div><h2>What these measurements mean</h2><ol><li>Expansion includes the CPU conversion loop and its writes into the RGB888 buffer. Native-row preparation, lock waiting and cache writeback are measured separately.</li><li>Full preparation includes row preparation, expansion, instrumentation/loop overhead and any initial writable-buffer wait. It excludes cache submission and the trailing wait for buffer reuse. It repeats even when content is unchanged.</li><li>Scanout-on uses the DMA frame clock. Scanout-absent retains equal RGB888 allocations and matching single/double allocation selection but uses a software 60 Hz clock, no panel submission/cache flush and no DMA ownership wait. The comparison measures this whole change in operating conditions, not an independently isolated memory-bus transaction.</li><li>Accepted buffers contain the same static image. Submission rate is not animation FPS; DMA cadence is not unique-image delivery. Physical displayed FPS was not measured.</li><li>Row timings are normalized from mean row wall times by image height. Values are phase-instrumented wall means, not CPU-only times or per-frame percentile distributions. Ordinary firmware was restored after the controls.</li></ol><h2>Per-mode details</h2>'''+''.join(detail)+f'<p>{len(excluded)} initial no-scanout runs are excluded because the diagnostic branch incorrectly cleared all720p pixels on every attempt. Their raw evidence remains retained.</p></html>'
    (args.output/'index.html').write_text(page)
    (args.output/'provenance.json').write_text(json.dumps(dict(generator_sha256=digest(Path(__file__)),analysis_source_sha256=digest(Path(__file__).with_name('static_conversion.py')),inputs=inputs,outputs={p.name:digest(p) for p in args.output.iterdir() if p.is_file()}),indent=2)+'\n')
    print(args.output/'index.html')

if __name__=='__main__':main()
