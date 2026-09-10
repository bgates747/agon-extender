"""Reject misleading saved benchmark evidence, including partial and duplicate runs."""
import csv
import io
from pathlib import Path
import tempfile
import unittest
from analyze import read_results, ENTRIES, PAYLOADS


class ResultsTest(unittest.TestCase):
    def data(self):
        rows=[]
        for repeat in range(1,4):
            for route in ('legacy','excom'):
                for entry in ENTRIES:
                    for payload in PAYLOADS:
                        rows.append(dict(row=len(rows)+1,repeat=repeat,route=route,entry=entry,payload=payload,
                            chunks=512,bytes=32768,t0=16777210,t1=34,t2=36,send_ticks=40,tail_ticks=2,
                            total_ticks=42,send_status=0,reply_status=0,pixel_r=255 if payload=='points' else 0,
                            pixel_g=255 if payload=='points' else 0,pixel_b=255 if payload=='points' else 0,
                            pixel_index=15 if payload=='points' else 0,mode=0,width=640,height=480,colours=16,valid=1))
        return rows

    def read(self,rows,footer='# complete;rows=48;status=0;legacy_return=0'):
        stream=io.StringIO(); writer=csv.DictWriter(stream,fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'result.csv'
            path.write_text('# mode=suite;\n'+stream.getvalue()+footer+'\n')
            return read_results(path)

    def test_clock_wrap(self):
        self.assertEqual(len(self.read(self.data())),48)

    def test_failures(self):
        for field,value in [('valid',0),('reply_status',15),('send_ticks',0),('pixel_r',255),('bytes',32767)]:
            with self.subTest(field=field):
                rows=self.data();rows[0][field]=value
                with self.assertRaises(ValueError):self.read(rows)

    def test_duplicate(self):
        rows=self.data();rows[1]=dict(rows[0],row=2)
        with self.assertRaises(ValueError):self.read(rows)

    def test_partial(self):
        with self.assertRaises(ValueError):self.read(self.data(), '# failed;rows=48;status=15')
        with self.assertRaises(ValueError):self.read(self.data()[:-1])

    def test_extended_completion_keeps_stock_timeout(self):
        rows=self.data()
        for row in rows:
            row.update(setup_first_status=15,setup_reply_ticks=66,
                       first_reply_status=0,reply_wait_ticks=2)
        self.assertEqual(self.read(rows)[0]['setup_first_status'],'15')
        for field in ('setup_reply_ticks','reply_wait_ticks'):
            with self.subTest(field=field):
                bad=[dict(row) for row in rows];bad[0][field]=601
                with self.assertRaises(ValueError):self.read(bad)


if __name__=='__main__':unittest.main()
