"""Host checks of evidence interpretation, including false-pass controls."""
import csv
import io
import unittest
from analyze import compare, read_rows, validate_dumps
from payloads import LENGTHS, expected_buffer, stream

def rows(route='excom'):
    result=[]
    for n in LENGTHS:
        for repeat in range(6):
            result.append(dict(route=route,wire_bytes=n,repeat=repeat,submit_prt=7,
                wire_prt=10 if repeat else 60000,receipt_prt=12 if route=='exext' else (10 if repeat else 60000),
                reply_prt=20 if repeat else 60001,mos_ticks=2,flags=0,read_overhead=1,
                empty_drain_prt=2,vblank_prt=1200,vblank_mos=2,divider=256,run_ticks=1200))
    # Allow parallel M02 to precede output return: a full block can complete
    # during the ordinary output call. Do not invent a monotonic M01/M02 rule.
    if route=='exext':
        for r in result:r.update(wire_prt=6,receipt_prt=12,reply_prt=20)
    return result

def csv_text(records):
    out=io.StringIO();w=csv.DictWriter(out,fieldnames=records[0]);w.writeheader();w.writerows(records);return out.getvalue()

def dumps(records):
    return '\n'.join('I (1) extender_vdp: vdu_sys_buffered: buffer 57600, 1 streams stored\n'+
        '\n'.join(f'I (2) extender_vdp: {b:02X} ' for b in expected_buffer(r['wire_bytes'])) for r in records)

class Contract(unittest.TestCase):
    def test_exact_wire_boundaries(self):
        for n in LENGTHS:
            b=stream(n)
            self.assertEqual(len(b),n);self.assertEqual(b[:9],bytes([23,0,160,0,225,5,194,0,0]))
            self.assertEqual(int.from_bytes(b[9:11],'little'),n-11)
        self.assertEqual(len(set(stream(4096)[11:])),256)
    def test_data_integrity_rejects_corruption_and_missing_evidence(self):
        r=read_rows(csv_text(rows()),'excom');log=dumps(r)
        self.assertEqual(validate_dumps(log,r)['verified_bytes'],24*8192)
        for bad in (log.replace('extender_vdp: 13 ','extender_vdp: 12 ',1),log[:-60],log+'\nI (3) extender_vdp: 00 '):
            with self.assertRaises(ValueError):validate_dumps(bad,r)
    def test_warmups_excluded_and_different_endpoint_order_allowed(self):
        u=read_rows(csv_text(rows()),'excom');v=read_rows(csv_text(rows('exext')),'exext')
        result=compare(u,v)
        self.assertEqual(result[0]['parallel_elapsed_change_percent']['wire_prt'],-40)
        self.assertEqual(result[0]['variants']['uart']['wire_prt']['median_equivalent_cycles'],2560)
    def test_reject_incomplete_overflow_wrong_divisor_and_mislabel(self):
        for field,value in [('flags',8),('divider',16),('wire_prt',65535),('route','exext')]:
            r=rows();r[0][field]=value
            with self.assertRaises(ValueError):read_rows(csv_text(r),'excom')
        with self.assertRaises(ValueError):read_rows(csv_text(rows()[:-1]),'excom')
    def test_reject_duplicate_order(self):
        r=rows();r[1]=r[0]
        with self.assertRaises(ValueError):read_rows(csv_text(r),'excom')

if __name__=='__main__':unittest.main()
