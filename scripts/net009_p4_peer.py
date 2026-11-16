"""USB control for one finite NET-009 P4 Ethernet arm."""

import ipaddress
import json
import time

import serial


class P4Peer:
    def __init__(self, port, source, folder, nonce, baud, milliseconds, direction):
        self.nonce = nonce
        self.result = None
        self._buffer = bytearray()
        self._port = serial.Serial(port=None, baudrate=115200, timeout=.1,
                                   write_timeout=2, exclusive=True)
        self._port.dtr = self._port.rts = False
        self._port.port = port
        self._transcript = (folder / 'p4-usb.log').open('xb')
        try:
            self._port.open()
            self._write(b'STATUS\n')
            status = self._event('status', 6)
            ip = ipaddress.IPv4Address(status['ip'])
            if not ip.is_private or ip.is_unspecified or status['source'] != source:
                raise ValueError('P4 peer identity or Ethernet address mismatch')
            self._write(f'ARM {nonce} {baud} {milliseconds} {direction}\n'.encode())
            record = self._event('armed', 5)
            self.address = record['ip']
            self.port = record['port']
            if self.address != str(ip) or not 0 < self.port <= 65535:
                raise ValueError('P4 arm address or port mismatch')
        except BaseException:
            self.close()
            raise

    def _write(self, command):
        if self._port.write(command) != len(command):
            raise IOError('Short P4 USB command')

    def _event(self, event, seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            for record in self._read(self._port.in_waiting or 1):
                if record['event'] == event and (
                    event == 'status' or record.get('nonce') == self.nonce
                ):
                    return record
                if record['event'] == 'refused' or (
                    record['event'] == 'result' and record.get('nonce') == self.nonce
                ):
                    raise RuntimeError('P4 peer refused or ended before the requested event')
        raise TimeoutError('P4 USB event deadline')

    def _read(self, size):
        block = self._port.read(min(4096, size))
        self._transcript.write(block)
        self._transcript.flush()
        self._buffer.extend(block)
        records = []
        while b'\n' in self._buffer:
            line, _, self._buffer = self._buffer.partition(b'\n')
            if not line.startswith(b'NET009 '):
                continue
            record = json.loads(line[7:])
            if record.get('event') == 'result' and record.get('nonce') == self.nonce:
                self.result = record
            records.append(record)
        if len(self._buffer) > 8192:
            raise ValueError('Oversized P4 USB response')
        return records

    def check_upload(self):
        if self._port.in_waiting:
            self._read(self._port.in_waiting)
        if self.result is not None:
            raise RuntimeError('P4 receiver returned before upload EOS')

    def finish(self, seconds=5):
        if self.result is None:
            self.result = self._event('result', seconds)
        return self.result

    def close(self):
        self._port.close()
        self._transcript.close()
