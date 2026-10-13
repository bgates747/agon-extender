"""Keep independent fixture/diagnostic identities strict when joining records."""
import unittest
import window_results as w

class DiagnosticIdentity(unittest.TestCase):
    def test_explicit_mapping_keeps_tag_and_result_identity_checks(self):
        raw=bytearray(152);raw[:8]=b'SCANR01!';raw[8]=1;raw[9]=24
        raw[10:13]=(7).to_bytes(3,'little');raw[16]=1;raw[35]=1;raw[41]=4
        raw[22]=2;raw[42:44]=b'id'
        window=dict(id=39,tag=7,start_us=1,end_us=2,scanouts=0,updates=0,phases=[])
        self.assertEqual(w.analyse(raw,window,diagnostic_id=39)['case'],1)
        with self.assertRaisesRegex(ValueError,'identity mismatch'):w.analyse(raw,window)
        with self.assertRaisesRegex(ValueError,'identity mismatch'):w.analyse(raw,dict(window,tag=8),diagnostic_id=39)
        with self.assertRaisesRegex(ValueError,'identity mismatch'):w.analyse(raw,dict(window,id=41),diagnostic_id=39)

if __name__=='__main__':unittest.main()
