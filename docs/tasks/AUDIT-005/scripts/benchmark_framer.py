"""Add stock RTC traffic to the frozen paired-graphics review grammar.

Real FatFS requests the clock for file timestamps. That traffic was absent
from the older directory-backed graphics review; it occurs outside timing.
This is an emulator-peer separator only, never a production VDU parser.
"""
from vdu_framer import command_length, Incomplete


class Framer:
    def __init__(self):
        self.pending=bytearray()

    def feed(self,data):
        self.pending.extend(data)
        packets=[]
        while self.pending:
            if self.pending[:3]==b'\x17\0\x87':
                if len(self.pending)<4: break
                mode=self.pending[3]
                if mode not in (0,1): raise ValueError('Unsupported RTC operation')
                length=4 if mode==0 else 10
                if len(self.pending)<length: break
            else:
                try: length=command_length(self.pending)
                except Incomplete: break
            packets.append(bytes(self.pending[:length]))
            del self.pending[:length]
        return packets
