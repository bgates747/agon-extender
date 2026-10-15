#!/usr/bin/env python3
"""Pi scrolling coordinator. --check is offline; execution needs a qualified adapter.

Adapters exchange JSON over stdin/stdout and own admitted EMOS CLI operations.
Fresh resident lifecycle/boot receipts are required: keyboard admission epochs
and elapsed sleeps do not prove CLI handback. There is deliberately no reset,
flash, SD-write, startup-edit or automatic-resume action. Existing rendering
masters and frozen evidence are not modified by this new, bounded runner.
"""
import argparse
import csv
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import time
import uuid

CASES = ('full-up', 'full-down', 'full-left', 'full-right',
         'partial-up', 'partial-down', 'partial-left', 'partial-right')
CAPABILITIES = {'fresh-mode', 'resident-foreground', 'peer-boot-identities',
                'cli-handback', 'input-pins', 'readonly-startup', 'completion',
                'persistent-notification'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    temporary = path.with_suffix(path.suffix + '.new')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def digest(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def validate(plan):
    if plan.get('schema') != 1:
        raise ValueError('Unknown plan schema')
    if not Path(plan['bench_lock']).is_absolute():
        raise ValueError('Require the commissioned Pi bench lock path')
    delay = plan.get('settle_seconds', 1.0)
    if not isinstance(delay, (int, float)) or not math.isfinite(delay) or delay < 1:
        raise ValueError('Monitor settling must be at least one second')
    profiles = {}
    for name, item in plan['fixtures'].items():
        path = Path(item['manifest']).resolve()
        if sha(path) != item['sha256']:
            raise ValueError('Changed fixture manifest: ' + name)
        m = json.loads(path.read_text())
        if m['fixture'] != 'pattern-scroll-r03' or not 0 <= m['mode'] < 128:
            raise ValueError('Require lifecycle-aware single-buffer scrolling fixture')
        required = {'scroll.bin', 'scroll.cfg'} | {f'c{i:02d}.vdu' for i in range(8)}
        if not required.issubset(m['files']):
            raise ValueError('Fixture manifest lacks executable, configuration or patterns')
        directory = PurePosixPath(item['sd_directory'])
        if (not str(directory).startswith('/extender/') or '..' in directory.parts
                or str(directory) != item['sd_directory']):
            raise ValueError('Invalid fixture directory')
        for file, checksum in m['files'].items():
            if PurePosixPath(file).name != file or sha(path.parent/'package'/file) != checksum:
                raise ValueError('Changed fixture file: ' + file)
        fields = (path.parent/'package/scroll.cfg').read_text().split()
        if len(fields) != 8 or [int(x) for x in fields[:7]] != [
                m['width'], m['height'], m['margin'], m['steps'], m['mode'], m['colours'], m['instrument']]:
            raise ValueError('Configuration/manifest mismatch')
        if not re.fullmatch(r'/agents/extender/results/[A-Za-z0-9_-]{1,48}\.csv', fields[7]):
            raise ValueError('Invalid result base')
        profiles[name] = dict(m, sd_directory=str(directory), result_base=fields[7],
                              manifest_sha256=item['sha256'])
    ids = set()
    if not plan['jobs']:
        raise ValueError('Empty suite')
    for job in plan['jobs']:
        identifier = job['id']
        if not re.fullmatch('[a-z0-9][a-z0-9-]{0,23}', identifier) or identifier in ids:
            raise ValueError('Invalid or duplicate job ID')
        ids.add(identifier)
        if job['target'] not in ('mb', 'ext') or job['case'] not in CASES or job['fixture'] not in profiles:
            raise ValueError('Invalid target/case/fixture')
        timeout = job.get('timeout_seconds', 120)
        if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('Invalid explicit job deadline')
    adapter = plan['adapter']
    if adapter.get('qualified'):
        if (not isinstance(adapter.get('argv'), list) or not adapter['argv'] or
                not all(isinstance(arg, str) and arg for arg in adapter['argv']) or not adapter.get('inputs')):
            raise ValueError('Qualified adapter needs argv and pinned inputs')
        for path, checksum in adapter['inputs'].items():
            if not digest(checksum) or sha(path) != checksum:
                raise ValueError('Changed adapter input')
    return profiles


def validate_result(path, job, fixture):
    rows = list(csv.reader(Path(path).read_text().splitlines()))
    header = 'case,source,mode,width,height,margin,instrument,updates,mos_ticks,missed_slots,metric,value_us,count_or_crossing'.split(',')
    if len(rows) < 3 or rows[0] != header or rows[-2][0] != 'SUITE' or len(rows[-2]) != 4:
        raise ValueError('Incomplete result envelope')
    start, end, duration = map(int, rows[-2][1:])
    if any(not 0 <= n <= 0xffffff for n in (start, end, duration)) or duration != ((end-start) & 0xffffff):
        raise ValueError('Invalid durable suite duration')
    terminal = rows[-1]
    if len(terminal) != 1 or terminal[0] not in ('PASS complete', 'FAIL incomplete', 'FAIL cleanup', 'CANCELLED'):
        raise ValueError('Missing terminal outcome')
    passed = terminal[0] == 'PASS complete'
    expected = [0 if job['target'] == 'mb' else 1] + [fixture[k] for k in
                ('mode', 'width', 'height', 'margin', 'instrument')]
    metrics = []
    for row in rows[1:-2]:
        if len(row) != 13 or row[0] != job['case']:
            raise ValueError('Wrong result case/schema')
        values = list(map(int, row[1:]))
        if values[:6] != expected or any(n < 0 or n > 0xffffffff for n in values):
            raise ValueError('Wrong result target/geometry/configuration')
        updates, ticks, missed, metric, value, count = values[6:]
        if updates > fixture['steps']:
            raise ValueError('Impossible update count')
        metrics.append(metric)
        if passed and (updates != fixture['steps'] or
                (fixture['instrument'] and metric in (9, 11) and count != fixture['steps']) or
                (fixture['instrument'] and metric in (3, 5, 10, 12) and count != 0) or
                (metric == 8 and count != 256)):
            raise ValueError('Failed counter/completion invariant')
    if passed and metrics != list(range(1, 13)):
        raise ValueError('Missing/duplicate result metrics')
    return passed, duration


class Adapter:
    def __init__(self, plan):
        self.argv = plan['adapter']['argv']
        self.inputs = plan['adapter']['inputs']

    def call(self, request):
        if any(sha(path) != checksum for path, checksum in self.inputs.items()):
            raise RuntimeError('Adapter changed after plan validation')
        result = subprocess.run(self.argv, input=json.dumps(request), text=True,
                                capture_output=True, check=False,
                                timeout=request['timeout_seconds'])
        if result.returncode:
            raise RuntimeError('Adapter failed: ' + result.stderr[-1000:])
        return json.loads(result.stdout)


class Coordinator:
    def __init__(self, plan, output, adapter, clock=time.monotonic, sleep=time.sleep):
        self.plan, self.output, self.adapter = plan, output, adapter
        self.clock, self.sleep = clock, sleep
        self.sequence = 0
        self.baseline = self.current = None
        self.safe = False
        self.summary = dict(run_id=str(uuid.uuid4()), state='preparing', jobs=[],
                            started_utc=dt.datetime.now(dt.timezone.utc).isoformat())

    def checkpoint(self):
        save(self.output/'summary.json', self.summary)

    def call(self, action, **payload):
        self.sequence += 1
        request = dict(schema=1, run_id=self.summary['run_id'], sequence=self.sequence,
                       action=action, timeout_seconds=payload.pop('timeout_seconds', 15), **payload)
        self.safe = False
        # Durable intent before side effects. An uncertain operation is never replayed.
        self.summary['pending'] = request
        self.checkpoint()
        save(self.output/f'{self.sequence:04d}-request.json', request)
        reply = self.adapter.call(request)
        save(self.output/f'{self.sequence:04d}-reply.json', reply)
        if any(reply.get(key) != request[key] for key in ('schema', 'run_id', 'sequence', 'action')):
            raise RuntimeError('Mismatched adapter receipt')
        s = reply['snapshot']
        if s.get('fresh') is not True or s['route'] not in ('mb', 'ext'):
            raise RuntimeError('No fresh EMOS mode/route receipt')
        if set(s['epochs']) != {'agon', 'p4'} or not all(isinstance(v, str) and v for v in s['epochs'].values()):
            raise RuntimeError('No authoritative peer boot identities')
        if not digest(s['startup_sha256']):
            raise RuntimeError('Missing read-only startup identity')
        for target in ('mb', 'ext'):
            mode = s['modes'][target]
            if (type(mode['number']) is not int or not 0 <= mode['number'] < 128
                    or any(type(mode[k]) is not int or mode[k] <= 0 for k in ('width', 'height', 'colours'))):
                raise RuntimeError('Unsupported entry or observed mode')
        if self.baseline and (s['epochs'] != self.baseline['epochs'] or
                              s['startup_sha256'] != self.baseline['startup_sha256']):
            raise RuntimeError('Reset/peer restart or changed startup; dispatch stopped')
        self.current = s
        self.safe = s.get('foreground') == 'cli' and s.get('cli_visible') is True
        self.summary['pending'] = None
        self.checkpoint()
        return reply

    def idle(self):
        if not self.safe:
            raise RuntimeError('No actual visible CLI handback')

    def pause(self):
        end = self.clock() + self.plan.get('settle_seconds', 1.0)
        while self.clock() < end:
            self.sleep(end-self.clock())

    def select(self, target, mode):
        self.idle()
        if self.current['route'] != target:
            self.call('select_route', target=target,
                      command='EMOS ' + ('LEGACY' if target == 'mb' else 'EXCOM') + ' --keep-display')
            self.idle()
            if self.current['route'] != target:
                raise RuntimeError('EMOS route did not commit')
        if self.current['modes'][target] != mode:
            self.call('select_mode', target=target, mode=mode,
                      command='VDU 22 ' + str(mode['number']))
            self.idle()
            if self.current['modes'][target] != mode:
                raise RuntimeError('Mode selection failed')
            self.pause()
        # Catch a reset during settling and require a fresh mode before launch.
        self.call('snapshot')
        self.idle()
        if self.current['route'] != target or self.current['modes'][target] != mode:
            raise RuntimeError('Mode/route changed before invocation')

    def restore(self):
        for target in ('mb', 'ext'):
            if self.current['modes'][target] != self.baseline['modes'][target]:
                self.select(target, self.baseline['modes'][target])
        if self.current['route'] != self.baseline['route']:
            self.call('select_route', target=self.baseline['route'], command='EMOS ' +
                      ('LEGACY' if self.baseline['route'] == 'mb' else 'EXCOM') + ' --keep-display')
            self.idle()
        self.call('snapshot')
        self.idle()
        if self.current['route'] != self.baseline['route'] or self.current['modes'] != self.baseline['modes']:
            raise RuntimeError('Baseline restoration failed')

    def run(self):
        profiles = validate(self.plan)
        if self.plan.get('ready') is not True or self.plan['adapter'].get('qualified') is not True:
            raise ValueError('Plan/adapter not qualified ready; no device action permitted')
        with Path(self.plan['bench_lock']).open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return self._run(profiles)

    def _run(self, profiles):
        self.output.mkdir(parents=True, exist_ok=False)
        save(self.output/'plan.json', self.plan)
        start = self.clock()
        failed = None
        try:
            hello = self.call('snapshot')
            if not CAPABILITIES.issubset(hello.get('capabilities', [])):
                self.safe = False
                raise RuntimeError('Adapter lacks required lifecycle capabilities')
            self.idle()
            self.baseline = json.loads(json.dumps(self.current))
            for job in self.plan['jobs']:
                fixture = profiles[job['fixture']]
                mode = dict(number=fixture['mode'], **{k: fixture[k] for k in ('width', 'height', 'colours')})
                self.select(job['target'], mode)
                result = fixture['result_base'][:-4] + f"-{job['target']}-{job['case']}-{job['id']}.csv"
                self.summary.update(state='invoking', active_job=job['id'])
                begin = self.clock()
                evidence = self.output.resolve()/'jobs'/job['id']
                evidence.mkdir(parents=True, exist_ok=False)
                launch = self.call('launch', job=job, fixture=fixture, result=result, evidence=str(evidence), commands=[
                    'CD ' + fixture['sd_directory'], 'LOAD scroll.bin',
                    'RUN &040000 ' + job['case'] + ' ' + job['id']])
                self.safe = False
                if launch.get('accepted_job') != job['id']:
                    raise RuntimeError('Test invocation unverified')
                receipt = self.call('completion', job=job, fixture=fixture, result=result,
                                    evidence=str(evidence),
                                    timeout_seconds=job.get('timeout_seconds', 120))
                self.safe = False
                if (receipt.get('job_id') != job['id'] or receipt.get('result') != result or
                        receipt.get('fixture_sha256') != fixture['files']['scroll.bin'] or
                        receipt.get('config_sha256') != fixture['files']['scroll.cfg'] or
                        receipt.get('inputs_verified') is not True or not digest(receipt.get('result_sha256'))):
                    raise RuntimeError('Missing/mismatched test evidence')
                artifact = Path(receipt['artifact']).resolve()
                artifact.relative_to(evidence)
                if sha(artifact) != receipt['result_sha256']:
                    raise RuntimeError('Result bytes disagree with receipt')
                passed, ticks = validate_result(artifact, job, fixture)
                if receipt.get('validated') is not passed:
                    raise RuntimeError('Adapter/result validation disagreement')
                self.safe = self.current.get('foreground') == 'cli' and self.current.get('cli_visible') is True
                self.idle()
                self.summary['jobs'].append(dict(id=job['id'], passed=passed,
                    elapsed_seconds=self.clock()-begin, result=result,
                    appliance_mos_ticks=ticks,
                    result_sha256=receipt['result_sha256']))
                self.checkpoint()
                if not passed:
                    raise RuntimeError('Test failed; remaining jobs not dispatched')
        except (Exception, KeyboardInterrupt) as error:
            failed = str(error) or type(error).__name__
        if self.baseline and self.safe:
            self.summary['restored'] = False
            try:
                self.restore()
                notification = self.call('notify', outcome='failed' if failed else 'complete',
                          completed=len(self.summary['jobs']), planned=len(self.plan['jobs']),
                          targets=['mb', 'ext'])
                self.idle()
                if set(notification.get('shown_targets', [])) != {'mb', 'ext'}:
                    raise RuntimeError('Persistent completion cues not verified on both displays')
                if (self.current['route'] != self.baseline['route'] or
                        self.current['modes'] != self.baseline['modes']):
                    raise RuntimeError('Notification changed restored mode/route state')
                self.summary['restored'] = True
            except (Exception, KeyboardInterrupt) as error:
                failed = (failed + '; ' if failed else '') + 'Cleanup: ' + (str(error) or type(error).__name__)
        else:
            self.summary['restored'] = False
        self.summary.update(state='stopped' if failed else 'complete', error=failed,
                            elapsed_seconds=self.clock()-start,
                            ended_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        self.checkpoint()
        return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--plan', type=Path)
    source.add_argument('--fixture-manifest', type=Path)
    parser.add_argument('--write-plan', type=Path)
    parser.add_argument('--sd-directory', default='/extender/scroll-r01')
    parser.add_argument('--bench-lock', default='/path/to/commissioned-bench.lock')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.fixture_manifest:
        if not args.write_plan or args.output:
            parser.error('--fixture-manifest requires --write-plan and no --output')
        path = args.fixture_manifest.resolve()
        plan = dict(schema=1, ready=False, settle_seconds=1,
                    readiness='Offline preparation; live adapter and hardware qualification pending',
                    bench_lock=args.bench_lock,
                    adapter=dict(qualified=False, argv=[], inputs={}),
                    fixtures=dict(current=dict(manifest=str(path), sha256=sha(path),
                                               sd_directory=args.sd_directory)),
                    jobs=[dict(id=f'{target}-{case}', target=target, case=case,
                               fixture='current', timeout_seconds=120)
                          for target in ('mb', 'ext') for case in CASES])
        validate(plan)
        with args.write_plan.open('x') as stream:
            json.dump(plan, stream, indent=2)
            stream.write('\n')
        print('Wrote stopped, unqualified 16-job plan; no adapter invoked')
        return 0
    if args.write_plan:
        parser.error('--write-plan requires --fixture-manifest')
    plan = json.loads(args.plan.read_text())
    validate(plan)
    if args.check:
        print(f"Plan/files valid: {len(plan['jobs'])} jobs; ready={plan.get('ready') is True}; "
              f"adapter_qualified={plan['adapter'].get('qualified') is True}; no adapter invoked")
        return 0
    if not args.output:
        parser.error('--output is required for explicit execution')
    return Coordinator(plan, args.output, Adapter(plan)).run()


if __name__ == '__main__':
    raise SystemExit(main())
