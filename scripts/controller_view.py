#!/usr/bin/env python3
"""Host-only F310 inspection and recording; no P4/Agon connection.

Run on the Linux desktop with its project interpreter. --headless supports a
finite input observation; --validate replays a capture without opening a device.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time

from controller_input import AXES, BUTTONS, STICKS, TRIGGERS, Observer, validate_capture

BG, PANEL, TEXT, DIM, GREEN, AMBER = '#101820', '#1c2a36', '#ffffff', '#b9c9d6', '#6df2b0', '#ffd166'


class Viewer:
    def __init__(self, observer, record_dir, seconds=None):
        import tkinter as tk
        self.tk = tk
        self.observer = observer
        self.record_dir = Path(record_dir)
        self.root = tk.Tk()
        self.root.title('Extender controller review — Oryx input only')
        self.root.geometry('1280x900')
        self.root.minsize(1080, 820)
        self.root.configure(bg=BG)
        self.root.option_add('*Font', ('DejaVu Sans', 15))
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.root.bind('<Escape>', lambda event: self.close())
        self.label('Controller input — Oryx only', 23, bold=True).pack(pady=(10, 0))
        self.status = self.label('Waiting for F310 in X mode', 17)
        self.status.pack()
        self.metrics = self.label('', 13, DIM)
        self.metrics.pack()
        self.canvas = tk.Canvas(self.root, bg=BG, height=345, highlightthickness=0)
        self.canvas.pack(fill='x', padx=12)
        self.table = tk.Frame(self.root, bg=BG)
        self.table.pack(fill='x', padx=18)
        headers = ['Axis', 'Native', '8-bit preview', 'Centre / rest', 'Observed range', 'Distinct', 'Min step / GCD']
        for column, title in enumerate(headers):
            tk.Label(self.table, text=title, bg=BG, fg=AMBER, font=('DejaVu Sans', 13, 'bold')).grid(row=0, column=column, sticky='w', padx=8)
            self.table.columnconfigure(column, weight=1)
        self.rows = {}
        for row, code in enumerate((*STICKS, *TRIGGERS), 1):
            cells = []
            for column in range(7):
                item = tk.Label(self.table, text=AXES[code] if column == 0 else '—', bg=BG,
                                fg=TEXT, font=('DejaVu Sans', 15), anchor='w')
                item.grid(row=row, column=column, sticky='ew', padx=8, pady=3)
                cells.append(item)
            self.rows[code] = cells
        self.explanation = self.label('Move each stick slowly, circle the edges, then squeeze each trigger separately.', 14, DIM)
        self.explanation.pack(pady=(8, 0))
        self.label('Observed steps describe this session, not proven sensor precision. No dead zone or game response applied.', 12, DIM).pack()
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(pady=8)
        self.record_button = tk.Button(bar, text='Start recording', command=self.toggle_record,
                                      bg=PANEL, fg=TEXT, padx=12)
        self.record_button.pack(side='left', padx=5)
        self.rest_button = tk.Button(bar, text='Measure rest (2 s)', command=self.rest,
                                    bg=PANEL, fg=TEXT, padx=12)
        self.rest_button.pack(side='left', padx=5)
        tk.Button(bar, text='Clear observations', command=self.reset_stats,
                  bg=PANEL, fg=TEXT, padx=12).pack(side='left', padx=5)
        tk.Button(bar, text='Close / Escape', command=self.close,
                  bg=PANEL, fg=TEXT, padx=12).pack(side='left', padx=5)
        self.record_status = self.label('Not recording', 12, DIM)
        self.record_status.pack()
        self.history = self.label('Button history: no transitions yet', 13, DIM)
        self.history.pack()
        self.label('Unplug clears the display. Replug reconnects automatically; press counts restart for that connection.', 12, DIM).pack(pady=4)
        self.closed = False
        self.deadline = time.monotonic() + seconds if seconds else None
        self.last_paint = 0.0
        self.rest_message = ''
        self.tick()

    def label(self, text, size, colour=TEXT, bold=False):
        return self.tk.Label(self.root, text=text, fg=colour, bg=BG,
                             font=('DejaVu Sans', size, 'bold' if bold else 'normal'))

    def rest(self):
        if self.observer.state:
            self.observer.state.start_rest(time.monotonic_ns())
            self.rest_message = 'Release both sticks; measuring rest for two seconds…'

    def reset_stats(self):
        if self.observer.state:
            self.observer.state.reset_stats()

    def toggle_record(self):
        if self.observer.recorder:
            self.observer.stop_recording()
        else:
            name = datetime.now(timezone.utc).strftime('controller-%Y-%m-%d-%H-%M-%S-%fZ.jsonl')
            try:
                self.observer.start_recording(self.record_dir / name)
            except OSError as error:
                self.observer.record_error = str(error)

    def tick(self):
        if self.closed:
            return
        self.observer.poll()
        if self.observer.state:
            result = self.observer.state.sample_rest(time.monotonic_ns())
            if result:
                self.observer.log('rest', session=self.observer.session, measurement=result)
                self.rest_message = 'Rest centre applied to preview only.' if result['accepted'] else 'Rest rejected: stick too far from centre. Release both sticks and retry.'
                self.rest_message += ' ' + '  '.join(f"{AXES[int(k)]}: {v['minimum']}…{v['maximum']}" for k, v in result['axes'].items())
        if time.monotonic() - self.last_paint >= 1/30:
            self.paint()
            self.last_paint = time.monotonic()
        if self.deadline and time.monotonic() >= self.deadline:
            self.close()
        else:
            self.root.after(8, self.tick)

    def paint(self):
        state = self.observer.state
        self.status.config(text=('Connected — ' if state else '') + self.observer.message,
                           fg=GREEN if state else AMBER)
        self.rest_button.config(state='normal' if state else 'disabled')
        if state:
            now = time.monotonic_ns()
            recent = sum(t >= now - 1_000_000_000 for t in state.report_times)
            age = f'{(now-state.last_report_ns)/1e6:.0f} ms' if state.last_report_ns else 'no changes yet'
            self.metrics.config(text=f'Change reports last 1 s: {recent}   Total: {state.reports}   Last change: {age}   Input gaps: {state.dropped}   Connection: {self.observer.sessions}')
        else:
            self.metrics.config(text='No live controller state. Waiting for one Logitech F310 in XInput mode.')
            self.rest_message = ''
        self.record_button.config(text='Stop recording' if self.observer.recorder else 'Start recording')
        if self.observer.record_error:
            rec = 'Recording error: ' + self.observer.record_error
        elif self.observer.recorder:
            rec = 'Recording: ' + self.observer.record_path
        else:
            rec = 'Saved: ' + self.observer.last_record_path if self.observer.last_record_path else 'Not recording'
        self.record_status.config(text=rec, fg=AMBER if self.observer.record_error else DIM)
        if self.rest_message:
            self.explanation.config(text=self.rest_message, wraplength=max(900, self.root.winfo_width()-30))
        self.canvas.delete('all')
        width = max(1000, self.canvas.winfo_width())
        for side, codes, x in [('Left stick', (0, 1), width*.18), ('Right stick', (3, 4), width*.46)]:
            y, radius = 135, 92
            self.canvas.create_text(x, 22, text=side, fill=TEXT, font=('DejaVu Sans', 18, 'bold'))
            self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, outline=DIM, width=2)
            self.canvas.create_line(x-radius, y, x+radius, y, fill=DIM)
            self.canvas.create_line(x, y-radius, x, y+radius, fill=DIM)
            self.canvas.create_oval(x-5, y-5, x+5, y+5, outline=AMBER, width=2)
            if state:
                u, v = [state.axes[k].unit(state.values[k], state.centres.get(k)) for k in codes]
                px, py = x+u*radius, y+v*radius
                self.canvas.create_oval(px-10, py-10, px+10, py+10, fill=GREEN, outline=TEXT)
            else:
                self.canvas.create_text(x, y+32, text='Disconnected', fill=AMBER, font=('DejaVu Sans', 13))
        for title, code, x in [('LT', 2, width*.68), ('RT', 5, width*.79)]:
            self.canvas.create_text(x, 22, text=title, fill=TEXT, font=('DejaVu Sans', 18, 'bold'))
            self.canvas.create_rectangle(x-25, 45, x+25, 220, outline=DIM, width=2)
            if state:
                value = state.values[code]
                frac = state.axes[code].unit(value, unipolar=True)
                self.canvas.create_rectangle(x-23, 219-frac*172, x+23, 219, fill=GREEN, outline='')
                self.canvas.create_text(x, 240, text=str(value), fill=TEXT, font=('DejaVu Sans', 17))
        hx, hy = (state.values[16], state.values[17]) if state else (0, 0)
        x, y = width*.92, 125
        self.canvas.create_text(x, 22, text='D-pad', fill=TEXT, font=('DejaVu Sans', 18, 'bold'))
        for title, dx, dy in [('↑', 0, -1), ('↓', 0, 1), ('←', -1, 0), ('→', 1, 0)]:
            active = bool(state) and ((dx and hx == dx) or (dy and hy == dy))
            self.canvas.create_rectangle(x+dx*37-17,y+dy*37-17,x+dx*37+17,y+dy*37+17,
                                         fill=GREEN if active else PANEL, outline=DIM)
            self.canvas.create_text(x+dx*37,y+dy*37,text=title,fill=BG if active else TEXT,font=('DejaVu Sans', 18))
        for index, (code, name) in enumerate(BUTTONS.items()):
            col, row = index % 6, index // 6
            x0, y0 = 5+col*width/6, 265+row*38
            active = state and code in state.pressed
            count = state.presses[code] if state else 0
            self.canvas.create_rectangle(x0,y0,x0+width/6-10,y0+32,
                                         fill=GREEN if active else PANEL, outline=DIM)
            self.canvas.create_text(x0+(width/6-10)/2,y0+16,text=f'{name}  [{count}]',
                                    fill=BG if active else TEXT,font=('DejaVu Sans', 14, 'bold'))
        for code, cells in self.rows.items():
            if not state:
                values = ['—']*6
            else:
                info, stats = state.axes[code], state.stats[code]
                unipolar = code in TRIGGERS
                centre = info.minimum if unipolar else state.centres.get(code, info.centre)
                values = [state.values[code], info.byte(state.values[code], centre, unipolar), centre,
                          f'{stats.minimum} … {stats.maximum}', len(stats.values),
                          f'{stats.smallest_step if stats.smallest_step is not None else "—"} / {stats.step_gcd or "—"}']
            for cell, value in zip(cells[1:], values):
                cell.config(text=str(value))
        if state and state.history:
            text = '   |   '.join(f'{BUTTONS[code]} {"down" if down else "up"}' for _,code,down in list(state.history)[-4:])
        else:
            text = 'No transitions yet'
        self.history.config(text='Button history: ' + text)

    def close(self):
        if not self.closed:
            self.closed = True
            self.observer.close()
            self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', help='Explicit stable /dev/input/by-id/...-event-joystick path')
    parser.add_argument('--headless', action='store_true', help='No GUI; requires --seconds')
    parser.add_argument('--seconds', type=float, help='Finite observation/UI duration')
    parser.add_argument('--record', type=Path, help='Record immediately to a new JSONL file')
    parser.add_argument('--record-dir', type=Path, default=Path('captures'), help='Directory for GUI recording button')
    parser.add_argument('--validate', type=Path, help='Replay/check a recorded stream; opens no input device')
    args = parser.parse_args()
    if args.seconds is not None and (not math.isfinite(args.seconds) or args.seconds <= 0):
        parser.error('--seconds must be finite and positive')
    if args.headless and args.seconds is None:
        parser.error('--headless requires a bounded --seconds')
    if args.validate:
        print(json.dumps(validate_capture(args.validate), indent=2))
        return 0
    observer = Observer(args.device)
    try:
        if args.record:
            observer.start_recording(args.record)
        if args.headless:
            end = time.monotonic() + args.seconds
            while time.monotonic() < end:
                observer.poll()
                time.sleep(.005)
            print(json.dumps(observer.summary(), indent=2))
        else:
            Viewer(observer, args.record_dir, args.seconds).run()
    except KeyboardInterrupt:
        pass
    finally:
        observer.close()
    if observer.record_error:
        parser.exit(1, 'Recording failed: '+observer.record_error+'\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
