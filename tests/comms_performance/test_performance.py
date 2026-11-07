import copy
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from comms_performance_report import analyse, interval, read_samples


def sample(arm='uart1', pair='1', start=0, end=120):
    return dict(schema='comms-performance-sample-r01', passed=True, arm=arm, pair=pair,
                case='sink-84', scope='transfer', observer='ez80', clock='mos120',
                workload_sha256='a'*64, renderer_sha256='b'*64, logical_configuration_sha256='c'*64,
                ez80_hz=18000000, p4_hz=240000000, iterations=10, bytes_per_iteration=84,
                clock_hz=120, timer_bits=24, start=start, end=end, upper_bound_counts=240)


class PerformanceTests(unittest.TestCase):
    def test_independent_native_vdu_corpus(self):
        stream = io.BytesIO(subprocess.check_output([os.environ['COMMS_PERFORMANCE_BINARY'], '--dump'], timeout=5))
        sink = bytes((i*37+11)&255 for i in range(129))
        short = b''.join(bytes((17, i%16)) for i in range(9))
        medium = b''.join(bytes((18, 0, i%16, 25, 4, 16, 0, i*7%192, 0,
                                 25, 5, 240, 0, i*7%192, 0)) for i in range(7))
        buffer = bytes((23,0,160,0,120,2,23,0,160,0,120,0,0,4)) + bytes((i*37+11)&255 for i in range(1024))
        for expected in (sink, short, medium, buffer):
            n = struct.unpack('<I', stream.read(4))[0]
            self.assertEqual(stream.read(n), expected)
        self.assertEqual(stream.read(), b'')

    def test_positive_and_negative_changes(self):
        for counts, change in ((60, 50), (180, -50)):
            rows = [sample(), sample('parallel', end=counts)]
            result = analyse(rows)
            self.assertEqual(result['rows'][0]['elapsed_reduction_percent'], change)
            self.assertIsNone(result['cpu_utilisation_percent'])
            self.assertFalse(result['scopes_summed'])

    def test_reversed_pairs_and_tails(self):
        rows = [sample(), sample('parallel', end=60), sample('parallel', '2', end=90), sample(pair='2', end=180)]
        row = analyse(rows)['rows'][0]
        self.assertEqual(row['pairs'], 2)
        self.assertEqual(row['uart1_median_ms'], 1250)
        self.assertEqual(row['parallel_median_ms'], 625)
        self.assertEqual(row['uart1_p95_ms'], 1500)
        self.assertEqual(row['parallel_max_ms'], 750)

    def test_scopes_and_observers_not_added(self):
        rows = [sample(), sample('parallel', end=60)]
        more = copy.deepcopy(rows)
        for row in more: row['scope'] = 'vdp_execution';row['observer'] = 'p4';row['clock'] = 'p4nominal'
        self.assertEqual(len(analyse(rows + more)['rows']), 2)

    def test_missing_duplicate_failed_accuracy_records_refused(self):
        a, b = sample(), sample('parallel')
        for rows in ([a], [a, a, b], [a, dict(b, passed=False)], [dict(event='run')], []):
            with self.assertRaises(ValueError): analyse(rows)

    def test_mismatched_workload_rate_and_hidden_case_changes(self):
        a, b = sample(), sample('parallel')
        for key, value in (('workload_sha256','d'*64), ('renderer_sha256','d'*64), ('workload_sha256',None), ('clock_hz', 100), ('iterations', 20)):
            with self.assertRaises(ValueError): analyse([a, dict(b, **{key:value})])
        with self.assertRaises(ValueError):
            analyse([a, b, dict(a,pair='2',iterations=20),dict(b,pair='2',iterations=20)])

    def test_timers_bounded_wrap_and_subtick_refusal(self):
        self.assertEqual(interval(250,5,8,30),11)
        self.assertEqual(interval(0xfffffff0,16,32,100),32)
        for args in ((1,1,24,100),(0,100,8,30),(0,1,8,128),(256,1,8,30),(0,1,33,30),(False,1,8,30)):
            with self.assertRaises(ValueError): interval(*args)

    def test_partial_sample_file_not_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'samples'
            p.write_text(json.dumps(sample()))
            with self.assertRaises(ValueError): read_samples(p)
            p.write_text(json.dumps(sample())+'\n')
            self.assertEqual(len(read_samples(p)),1)


if __name__ == '__main__':
    unittest.main()
