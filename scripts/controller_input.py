"""Linux F310 observer: no EVIOCGRAB, device writes, LAN or firmware access.

Linux EV_SYN/SYN_REPORT defines report boundaries. SYN_DROPPED requires ignoring
through the next report and re-querying state; transitions across that gap are
unknown. Read the controller guide before treating observed steps as precision.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
import errno
import fcntl
import glob
import json
import math
import os
from pathlib import Path
import statistics
import struct
import time
import uuid

EV_SYN, EV_KEY, EV_ABS = 0, 1, 3
SYN_REPORT, SYN_DROPPED = 0, 3
EVENT = struct.Struct('@llHHi')  # Linux 64-bit input_event, native timeval ABI.
AXES = {0: 'Left X', 1: 'Left Y', 3: 'Right X', 4: 'Right Y',
        2: 'Left trigger', 5: 'Right trigger', 16: 'D-pad X', 17: 'D-pad Y'}
STICKS = (0, 1, 3, 4)
TRIGGERS = (2, 5)
BUTTONS = {304: 'A / South', 305: 'B / East', 307: 'Y / North',
           308: 'X / West', 310: 'LB', 311: 'RB', 314: 'Back',
           315: 'Start', 316: 'Guide', 317: 'Left click', 318: 'Right click'}


def ioc(direction, number, size):
    return (direction << 30) | (size << 16) | (ord('E') << 8) | number


def read_ioctl(fd, number, size):
    value = bytearray(size)
    fcntl.ioctl(fd, ioc(2, number, size), value, True)
    return bytes(value)


def bits(data):
    return {i for i in range(len(data) * 8) if data[i // 8] & (1 << (i % 8))}


@dataclass(frozen=True)
class Axis:
    minimum: int
    maximum: int
    fuzz: int = 0
    flat: int = 0
    resolution: int = 0

    @property
    def centre(self):
        return (self.minimum + self.maximum + 1) // 2

    def unit(self, value, centre=None, unipolar=False):
        value = max(self.minimum, min(self.maximum, value))
        if unipolar:
            return (value - self.minimum) / (self.maximum - self.minimum)
        centre = self.centre if centre is None else centre
        span = self.maximum - centre if value >= centre else centre - self.minimum
        return max(-1.0, min(1.0, (value - centre) / span)) if span else 0.0

    def byte(self, value, centre=None, unipolar=False):
        n = self.unit(value, centre, unipolar)
        return round(n * 255) if unipolar else 128 + round(n * (127 if n >= 0 else 128))


class AxisStats:
    """Bounded value inventory (F310 axis ranges are at most 65536 values)."""
    def __init__(self):
        self.values = set()
        self.previous = None
        self.minimum = self.maximum = None
        self.smallest_step = None
        self.step_gcd = 0
        self.changes = 0

    def observe(self, value):
        self.values.add(value)
        self.minimum = value if self.minimum is None else min(self.minimum, value)
        self.maximum = value if self.maximum is None else max(self.maximum, value)
        if self.previous is not None and value != self.previous:
            step = abs(value - self.previous)
            self.smallest_step = step if self.smallest_step is None else min(self.smallest_step, step)
            self.step_gcd = math.gcd(self.step_gcd, step)
            self.changes += 1
        self.previous = value

    def summary(self):
        return dict(min=self.minimum, max=self.maximum, distinct=len(self.values),
                    smallest_observed_step=self.smallest_step, step_gcd=self.step_gcd,
                    changes=self.changes)


class State:
    def __init__(self, axes, values, pressed=()):
        self.axes = axes
        self.values = dict(values)
        self.pressed = set(pressed)
        self.pending_axes = {}
        self.pending_keys = []
        self.dropping = False
        self.dropped = 0
        self.reports = 0
        self.presses = {code: 0 for code in BUTTONS}
        self.releases = {code: 0 for code in BUTTONS}
        self.history = deque(maxlen=12)
        self.report_times = deque(maxlen=512)
        self.last_report_ns = None
        self.centres = {}
        self.rest = None
        self.reset_stats()

    def reset_stats(self):
        self.stats = {code: AxisStats() for code in self.axes}
        for code, value in self.values.items():
            self.stats[code].observe(value)

    def resync(self, values, pressed):
        self.values = dict(values)
        self.pressed = set(pressed)
        self.pending_axes.clear()
        self.pending_keys.clear()
        self.dropping = False
        # Do not infer transitions or step sizes across an unknown input gap.
        for code, value in self.values.items():
            self.stats[code].previous = None
            self.stats[code].observe(value)
        self.rest = None

    def feed(self, event_type, code, value, received_ns):
        if event_type == EV_SYN and code == SYN_DROPPED:
            self.dropped += 1
            self.dropping = True
            self.pending_axes.clear()
            self.pending_keys.clear()
            self.rest = None
            return 'gap'
        if self.dropping:
            return 'resync' if event_type == EV_SYN and code == SYN_REPORT else None
        if event_type == EV_ABS and code in self.axes:
            self.pending_axes[code] = max(self.axes[code].minimum,
                                          min(self.axes[code].maximum, value))
        elif event_type == EV_KEY and code in BUTTONS and value in (0, 1):
            self.pending_keys.append((code, value))
        elif event_type == EV_SYN and code == SYN_REPORT:
            self.values.update(self.pending_axes)
            for key, down in self.pending_keys:
                if bool(down) != (key in self.pressed):
                    (self.pressed.add if down else self.pressed.discard)(key)
                    (self.presses if down else self.releases)[key] += 1
                    self.history.append((received_ns, key, bool(down)))
            for key, current in self.pending_axes.items():
                self.stats[key].observe(current)
            self.pending_axes.clear()
            self.pending_keys.clear()
            self.reports += 1
            self.last_report_ns = received_ns
            self.report_times.append(received_ns)
            return 'frame'
        return None

    def start_rest(self, now_ns):
        self.rest = (now_ns + 2_000_000_000, {code: [] for code in STICKS})

    def sample_rest(self, now_ns):
        if self.rest is None:
            return None
        end, samples = self.rest
        for code in STICKS:
            samples[code].append(self.values[code])
        if now_ns < end:
            return None
        measured = {str(code): dict(centre=int(statistics.median(v)),
                                    minimum=min(v), maximum=max(v), samples=len(v))
                    for code, v in samples.items()}
        # Reject measurements at an end stop; range-based raw preview stays valid.
        accepted = all(abs(item['centre'] - self.axes[int(code)].centre) <=
                       (self.axes[int(code)].maximum - self.axes[int(code)].minimum) * .25
                       for code, item in measured.items())
        if accepted:
            self.centres = {int(code): item['centre'] for code, item in measured.items()}
        self.rest = None
        return dict(accepted=accepted, axes=measured)

    def snapshot(self):
        return dict(axes={str(k): v for k, v in self.values.items()},
                    buttons=sorted(self.pressed), presses=dict(self.presses),
                    releases=dict(self.releases), reports=self.reports,
                    dropped=self.dropped, centres=dict(self.centres))

    def rate(self):
        if len(self.report_times) < 2:
            return 0.0
        span = (self.report_times[-1] - self.report_times[0]) / 1e9
        return (len(self.report_times) - 1) / span if span else 0.0


class Device:
    def __init__(self, path):
        if struct.calcsize('P') != 8 or EVENT.size != 24:
            raise OSError('Controller reader requires the Linux 64-bit input_event ABI')
        self.path = str(path)
        self.fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        try:
            bus, vendor, product, version = struct.unpack('4H', read_ioctl(self.fd, 2, 8))
            self.name = read_ioctl(self.fd, 6, 256).split(b'\0')[0].decode(errors='replace')
            if (vendor, product) != (0x046D, 0xC21D):
                raise OSError('Select the F310 in XInput (X) mode')
            supported_axes = bits(read_ioctl(self.fd, 0x20 + EV_ABS, 8))
            self.axes = {}
            for code in AXES:
                if code in supported_axes:
                    _, lo, hi, fuzz, flat, resolution = struct.unpack('6i', read_ioctl(self.fd, 0x40 + code, 24))
                    if not 0 < hi - lo <= 65535:
                        raise OSError('Unexpected axis bounds')
                    self.axes[code] = Axis(lo, hi, fuzz, flat, resolution)
            if set(self.axes) != set(AXES):
                raise OSError('F310 is missing required stick, trigger or hat axes')
            if not set(BUTTONS).issubset(bits(read_ioctl(self.fd, 0x20 + EV_KEY, 96))):
                raise OSError('F310 is missing required buttons')
            # Per-client clock selection; does not change device or other clients.
            fcntl.ioctl(self.fd, ioc(1, 0xA0, 4), struct.pack('i', time.CLOCK_MONOTONIC))
            self.identity = dict(name=self.name, vendor=vendor, product=product,
                                 version=version, path=self.path)
            values, pressed = self.query()
            self.state = State(self.axes, values, pressed)
        except BaseException:
            self.close()
            raise

    def query(self):
        values = {code: struct.unpack('6i', read_ioctl(self.fd, 0x40 + code, 24))[0]
                  for code in self.axes}
        return values, bits(read_ioctl(self.fd, 0x18, 96)) & set(BUTTONS)

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def events(self):
        # Bound a UI iteration. Kernel reports overflow with SYN_DROPPED.
        for _ in range(8):
            try:
                data = os.read(self.fd, EVENT.size * 512)
            except BlockingIOError:
                return
            if not data:
                raise OSError(errno.ENODEV, 'Controller disconnected')
            if len(data) % EVENT.size:
                raise OSError('Partial Linux input_event record')
            for sec, usec, kind, code, value in EVENT.iter_unpack(data):
                yield dict(kernel_ns=sec * 1_000_000_000 + usec * 1000,
                           type=kind, code=code, value=value)


def discover(selected=None):
    candidates = [selected] if selected else sorted(glob.glob('/dev/input/by-id/*event-joystick'))
    # No assumptions about event4 or paths surviving a replug.
    if not selected:
        seen = {os.path.realpath(p) for p in candidates}
        candidates += [p for p in sorted(glob.glob('/dev/input/event*')) if p not in seen]
    found, reasons = [], []
    for path in candidates:
        try:
            found.append(Device(path))
        except OSError as error:
            if selected or 'Permission' in str(error) or 'XInput' in str(error):
                reasons.append(str(error))
    if len(found) > 1:
        for dev in found:
            dev.close()
        return None, 'Multiple F310 controllers: select a stable --device path'
    return (found[0], '') if found else (None, 'Waiting for F310 in X mode' + (': ' + reasons[0] if reasons else ''))


class Recorder:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open('x', buffering=65536)
        self.origin = time.monotonic_ns()
        self.last_flush = self.origin
        self.write('header', schema='extender-controller-capture-v1',
                   utc=datetime.now(timezone.utc).isoformat(),
                   clock='Linux CLOCK_MONOTONIC nanoseconds; event-driven, not HID polling rate')

    def write(self, kind, **data):
        now = time.monotonic_ns()
        self.handle.write(json.dumps(dict(kind=kind, t_ns=now - self.origin, **data),
                                     separators=(',', ':')) + '\n')
        if now - self.last_flush >= 1_000_000_000:
            self.handle.flush()
            self.last_flush = now

    def close(self):
        if not self.handle.closed:
            self.write('end')
            self.handle.flush()
            os.fsync(self.handle.fileno())
            self.handle.close()


class Observer:
    def __init__(self, selected=None):
        self.selected = selected
        self.device = None
        self.message = 'Waiting for F310 in X mode'
        self.next_scan = 0
        self.session = None
        self.recorder = None
        self.record_error = ''
        self.record_path = None
        self.last_record_path = None
        self.started_ns = time.monotonic_ns()
        self.sessions = 0

    @property
    def state(self):
        return self.device.state if self.device else None

    def log(self, kind, **data):
        if self.recorder:
            try:
                self.recorder.write(kind, **data)
            except OSError as error:
                self.record_error = str(error)
                self.recorder.handle.close()
                self.recorder = None
                self.record_path = None

    def announce(self):
        if self.device:
            self.log('connect', session=self.session, identity=self.device.identity,
                     capabilities={str(k): vars(v) for k, v in self.device.axes.items()},
                     state=self.state.snapshot(),
                     pending_axes=dict(self.state.pending_axes),
                     pending_keys=list(self.state.pending_keys),
                     dropping=self.state.dropping)

    def start_recording(self, path):
        self.recorder = Recorder(path)
        self.record_path = str(path)
        self.last_record_path = str(path)
        self.record_error = ''
        self.announce()

    def stop_recording(self):
        if self.recorder:
            recorder, self.recorder = self.recorder, None
            self.record_path = None
            try:
                recorder.close()
            except OSError as error:
                self.record_error = str(error)
                recorder.handle.close()

    def poll(self):
        now = time.monotonic_ns()
        if not self.device and now >= self.next_scan:
            self.device, self.message = discover(self.selected)
            self.next_scan = now + 500_000_000
            if self.device:
                self.sessions += 1
                self.session = uuid.uuid4().hex
                self.message = self.device.name
                self.announce()
        if not self.device:
            return
        try:
            for event in self.device.events():
                received = time.monotonic_ns()
                self.log('event', session=self.session, received_ns=received, **event)
                action = self.state.feed(event['type'], event['code'], event['value'], received)
                if action == 'resync':
                    values, pressed = self.device.query()
                    self.state.resync(values, pressed)
                    self.log('resync', session=self.session, state=self.state.snapshot())
                elif action == 'frame':
                    self.log('frame', session=self.session, state=self.state.snapshot())
        except OSError as error:
            self.log('disconnect', session=self.session, reason=str(error))
            self.device.close()
            self.device = None
            self.session = None
            self.message = 'Disconnected — controls cleared; reconnect in X mode'
            self.next_scan = now + 500_000_000

    def close(self):
        if self.device:
            self.log('observer_close', session=self.session)
            self.device.close()
            self.device = None
        self.stop_recording()

    def summary(self):
        return dict(connected=self.device is not None, sessions=self.sessions,
                    identity=self.device.identity if self.device else None,
                    state=self.state.snapshot() if self.state else None,
                    axes={str(k): v.summary() for k, v in self.state.stats.items()} if self.state else {},
                    record_error=self.record_error)


def validate_capture(path):
    """Replay raw events and check every recorded frame, including resync baselines."""
    state = None
    session = None
    frames = events = sessions = 0
    previous_t = -1
    ended = False
    with Path(path).open() as source:
        for index, line in enumerate(source):
            row = json.loads(line)
            if row['t_ns'] < previous_t or ended:
                raise ValueError('Non-monotonic capture or records after end')
            previous_t = row['t_ns']
            kind = row['kind']
            if index == 0:
                if kind != 'header' or row.get('schema') != 'extender-controller-capture-v1':
                    raise ValueError('Unsupported capture header')
            elif kind == 'connect':
                axes = {int(k): Axis(**v) for k, v in row['capabilities'].items()}
                saved = row['state']
                state = State(axes, {int(k): v for k, v in saved['axes'].items()}, saved['buttons'])
                # Recording may begin after the observer has already counted events.
                state.presses = {int(k): v for k, v in saved['presses'].items()}
                state.releases = {int(k): v for k, v in saved['releases'].items()}
                state.reports, state.dropped = saved['reports'], saved['dropped']
                state.centres = {int(k): v for k, v in saved['centres'].items()}
                state.pending_axes = {int(k): v for k, v in row['pending_axes'].items()}
                state.pending_keys = [tuple(v) for v in row['pending_keys']]
                state.dropping = row['dropping']
                session = row['session']
                sessions += 1
            elif kind in ('event', 'frame', 'resync', 'rest'):
                if state is None or row['session'] != session:
                    raise ValueError('State record without matching live session')
                if kind == 'event':
                    state.feed(row['type'], row['code'], row['value'], row['received_ns'])
                    events += 1
                elif kind == 'resync':
                    state.resync({int(k): v for k, v in row['state']['axes'].items()}, row['state']['buttons'])
                elif kind == 'rest':
                    if row['measurement']['accepted']:
                        state.centres = {int(k): v['centre'] for k, v in row['measurement']['axes'].items()}
                elif json.loads(json.dumps(state.snapshot())) != row['state']:
                    raise ValueError('Recorded frame disagrees with replayed raw events')
                else:
                    frames += 1
            elif kind in ('disconnect', 'observer_close'):
                state = session = None
            elif kind == 'end':
                ended = True
            else:
                raise ValueError('Unknown capture record')
    if not ended:
        raise ValueError('Incomplete capture: missing clean end record')
    return dict(sessions=sessions, events=events, frames=frames, complete=True)
