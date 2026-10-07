#!/usr/bin/env python3
"""Make an offline RGB-001 completion comparison from retained report JSON only.

NORMAL and OFF are separate plots. Completion includes EMOS routing, command
transport, drawing and the reply; double buffering additionally waits for its
ordinary buffer swap. Neither plot measures physical displayed frame rate.
"""
import argparse, datetime, hashlib, html, json
from pathlib import Path


def build(report, output):
    import plotly.graph_objects as go
    from plotly.offline import get_plotlyjs
    raw = report.read_bytes()
    data = json.loads(raw)
    assert data['comparison'], 'Require matched native/direct NORMAL results'
    assert not output.exists(), 'Preserve generated evidence; select a fresh output'
    plots = []
    colors = {20: '#ab4e04', 8: '#2464b4', 136: '#8a39a0'}
    for variant in ['normal', 'off']:
        fig = go.Figure()
        maximum = 16.667
        points = 0
        for mode in [20, 8, 136]:
            rows = [r for r in data['comparison'] if r['mode'] == mode and
                    r.get('native_' + variant + '_completion_median_ms') and
                    r.get('rgb888_' + variant + '_completion_median_ms')]
            x = [r['native_' + variant + '_completion_median_ms'] for r in rows]
            y = [r['rgb888_' + variant + '_completion_median_ms'] for r in rows]
            if not rows:
                continue
            points += len(rows)
            maximum = max(maximum, max(x), max(y))
            descriptions = [f"Mode {mode}, case {r['case']}: {r['family']} {r['workload']}, "
                            f"level {r['level']}, {r['style']}<br>"
                            f"Native {a:.3f} ms ({1000 / a:.1f} fps equivalent)<br>"
                            f"RGB888 {b:.3f} ms ({1000 / b:.1f} fps equivalent)<br>"
                            f"Time difference {(b - a) / a * 100:+.1f}%"
                            for r, a, b in zip(rows, x, y)]
            fig.add_trace(go.Scatter(x=x, y=y, mode='markers', name=f'Mode {mode}',
                                    marker=dict(size=10, color=colors[mode]), text=descriptions,
                                    hovertemplate='%{text}<extra></extra>'))
        maximum *= 1.08
        fig.add_shape(type='line', x0=0, y0=0, x1=maximum, y1=maximum,
                      line=dict(color='#555', dash='dash'))
        fig.add_vline(x=1000 / 60, line_color='#c52e33', line_dash='dot')
        fig.add_hline(y=1000 / 60, line_color='#c52e33', line_dash='dot')
        fig.update_layout(title=f'{variant.upper()}: {points} matched workload points',
                          template='plotly_white', height=600,
                          xaxis=dict(title='Native median completion (ms)', range=[0, maximum]),
                          yaxis=dict(title='Direct RGB888 median completion (ms)', range=[0, maximum]))
        plots.append(fig.to_html(full_html=False, include_plotlyjs=False,
                                config={'responsive': True, 'toImageButtonOptions': {'format': 'svg'}}))
    rows = []
    for r in data['comparison']:
        rows.append('<tr>' + ''.join(f'<td>{html.escape(str(v))}</td>' for v in [
            r['mode'], r['case'], f"{r['family']} {r['workload']} / {r['level']} / {r['style']}",
            f"{r['native_completion_ms']:.3f}", f"{r['native_completion_equivalent_fps']:.1f}",
            f"{r['rgb888_completion_ms']:.3f}", f"{r['rgb888_completion_equivalent_fps']:.1f}",
            f"{r['rgb888_vs_native_completion_percent']:+.1f}%",
            f"{r['rgb888_normal_application_updates_per_second']:.1f}",
            f"{r['rgb888_normal_hdmi_submissions_per_second']:.1f}",
            f"{r['rgb888_normal_dma_scanout_hz']:.1f}"]) + '</tr>')
    script = get_plotlyjs()
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>RGB888 completion comparison</title>'
    page += '<style>body{font:16px system-ui;margin:2em auto;max-width:1400px;padding:0 1em;color:#17252c;background:#f7fafb}table{border-collapse:collapse;background:white}td,th{padding:.5em;border:1px solid #ccd5da;text-align:right}td:nth-child(3){text-align:left}section{background:white;margin:1.5em 0;padding:1em}p{max-width:95ch}</style>'
    page += '<h1>Rendering directly into HDMI memory</h1><p>One bounded matched pass of the unchanged r04 workloads. Above the diagonal, direct RGB888 completion is slower. Red lines mark the 16.67 ms budget. Hover for milliseconds and equivalent fps; drag to zoom and export SVG from the toolbar.</p>'
    page += '<p>Completion includes EMOS routing, transport, drawing and the reply. Mode 136 includes its vblank-synchronised swap. NORMAL uses HDMI; OFF disables both presentation and DMA while retaining allocations and a software 60 Hz clock. This pair does not isolate DMA alone. Single-buffer counters do not prove complete, tear-free physical frames.</p>'
    page += '<script>' + script + '</script>' + ''.join('<section>' + p + '</section>' for p in plots)
    page += '<h2>HDMI-active results</h2><p>Worst direct RGB888 median completion first. Difference = (RGB888 − native) / native × 100%. Equivalent fps is 1000/ms for completion alone. Fixture updates, accepted HDMI submissions and DMA scanout are separate counts.</p><div style="overflow:auto"><table><thead><tr>'
    page += ''.join('<th>' + h + '</th>' for h in ['Mode', 'Case', 'Workload', 'Native ms', 'Native eq fps', 'RGB888 ms', 'RGB888 eq fps', 'Time difference', 'Fixture updates/s', 'HDMI submits/s', 'DMA Hz'])
    page += '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div><p>' + html.escape(data['scope']) + '</p></html>'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page)
    digest = lambda b: hashlib.sha256(b).hexdigest()
    receipt = dict(generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   report_sha256=digest(raw), generator_sha256=digest(Path(__file__).read_bytes()),
                   html_sha256=digest(page.encode()), plotly_js_sha256=digest(script.encode()),
                   matched_normal_pairs=len(data['comparison']), scope='Offline visualization; no bench operations')
    output.with_suffix('.provenance.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    receipt = build(args.report, args.output)
    print(json.dumps(dict(output=str(args.output.resolve()), matched_normal_pairs=receipt['matched_normal_pairs'])))


if __name__ == '__main__':
    main()
