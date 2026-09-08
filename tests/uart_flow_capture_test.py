from pathlib import Path
import runpy
import unittest
api=runpy.run_path(str(Path(__file__).resolve().parents[1]/"scripts/capture_uart_flow.py"))
BUILD="uart-flow-probe-r01-b2026-09-08-00-00-00Z"
RECORDS=["UART FLOW FORWARD RELEASE min_hold_ms=1000", "UART FLOW REQUEST count=6 hex=464C4F570D0A",
         "UART FLOW ACK QUEUED cts=stop", "UART FLOW ACK SENT count=9 hex=464C4F5741434B0D0A",
         "UART FLOW BLOCKED QUEUED cts=stop", "UART FLOW BLOCKED TIMEOUT cancelled=1",
         "UART FLOW PASS received=6 ack=9 blocked=1 cancelled=1"]
def log(records=RECORDS): return "".join(x+" build="+BUILD+"\r\n" for x in records).encode()
class FlowCaptureTests(unittest.TestCase):
    def test_success(self): self.assertTrue(api['verdict'](log(),BUILD)[0])
    def test_missing_each_stage(self):
        for n in range(len(RECORDS)):
            self.assertFalse(api['verdict'](log(RECORDS[:n]+RECORDS[n+1:]),BUILD)[0])
    def test_duplicate_stage_wrong_id_bad_bytes_wrong_order(self):
        for data in [log()+log(RECORDS[:1]),log().replace(BUILD.encode(),b"wrong"),
                     log().replace(b"464C4F570D0A",b"00"),log(list(reversed(RECORDS)))]:
            self.assertFalse(api['verdict'](data,BUILD)[0])
    def test_late_failure_and_restart(self):
        for suffix in [b"UART FLOW FAIL late\n",b"UART FLOW EVENT type=2\n",b"UART FLOW RECEIVER reboot\n"]:
            self.assertFalse(api['verdict'](log()+suffix,BUILD)[0])
    def test_readiness_requires_stopped_cts(self):
        good=("UART FLOW WAIT received=0 cts=1 build="+BUILD+"\r\n").encode()
        self.assertTrue(api['receiver_ready'](good,BUILD))
        for bad in [good.replace(b"cts=1",b"cts=0"), good.replace(b"received=0",b"received=1"),good+log()]:
            with self.assertRaises(RuntimeError): api['receiver_ready'](bad,BUILD)
if __name__=='__main__': unittest.main()
