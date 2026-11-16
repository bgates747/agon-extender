#!/usr/bin/env python3
"""Finite NET-009 test: Pi5 RP1 UART0 <-> ESP8266 <-> Pi5 TCP peer."""
import argparse
import ipaddress
import json
import os
import re
import secrets
import struct
import time
from pathlib import Path

import serial

from modem_bw_peer import Peer
from modem_bw_protocol import DOWN, HEADER, PAYLOAD, UP, check, frame, pattern
from modem_join import harden, load_private, wipe

RATES = (115200, 230400, 384000, 576000, 1152000)
UART_NODE = 'serial@30000'


def require_header_uart(port):
    """Reject aliases, USB, debug UART and header ttys with the wrong OF node."""
    name = Path(port).name
    if not re.fullmatch(r'ttyAMA\d+', name):
        raise ValueError('Use the owner-verified header tty, not a serial alias')
    dev = Path('/sys/class/tty', name, 'device', 'of_node').resolve(strict=True)
    if UART_NODE not in dev.parts or not any(part.startswith('rp1') for part in dev.parts):
        raise ValueError('Selected tty is not RP1 header UART0')
    consoles = Path('/proc/consoles').read_text().splitlines()
    if any(line.split()[0] == name for line in consoles):
        raise ValueError('Selected tty is a kernel console')


def write_all(port, data):
    written = port.write(data)
    if written != len(data):
        raise IOError('Short UART write')


def command(port, request, *, timeout=3, prompt=False, required=True):
    write_all(port, request)
    end = time.monotonic() + timeout
    data = bytearray()
    while time.monotonic() < end and len(data) < 8192:
        data.extend(port.read(port.in_waiting or 1))
        if (b'>' in data if prompt else b'\nOK\r\n' in data):
            return data
        if b'\nERROR\r\n' in data or b'\nFAIL\r\n' in data:
            break
    if required:
        raise RuntimeError('Modem refused or timed out in current phase')
    return data


def associate(port, credential_provider='login-keyring'):
    data = command(port, b'AT+CIFSR\r\n')
    ip = re.search(rb'STAIP,"(\d+\.\d+\.\d+\.\d+)"', data)
    if ip and ip.group(1) != b'0.0.0.0':
        return 'existing'
    credentials = load_private(credential_provider)
    request = bytearray(b'AT+CWJAP_CUR=')
    try:
        command(port, b'AT+CWMODE_CUR=1\r\n')
        count = credentials[0]
        for index, field in enumerate((memoryview(credentials)[2:2+count],
                                       memoryview(credentials)[2+count:])):
            if index:
                request.append(44)
            request.append(34)
            for byte in field:
                if byte in (34, 44, 92):
                    request.append(92)
                request.append(byte)
            request.append(34)
        request.extend(b'\r\n')
        response = command(port, request, timeout=65)
        wipe(response)
        data = command(port, b'AT+CIFSR\r\n')
        ip = re.search(rb'STAIP,"(\d+\.\d+\.\d+\.\d+)"', data)
        if not ip or ip.group(1) == b'0.0.0.0':
            raise RuntimeError('Association did not yield an IP address')
        return 'joined'
    finally:
        wipe(credentials)
        wipe(request)


def read_frame(port, deadline, retained):
    def exact(size):
        data = bytearray()
        while len(data) < size and time.monotonic() < deadline:
            block = port.read(size - len(data))
            retained.write(block)
            data.extend(block)
        if len(data) != size:
            raise TimeoutError('Incomplete UART frame')
        return data

    header = exact(HEADER.size)
    magic, _, size, _ = HEADER.unpack(header)
    if magic != b'N8BW' or size > PAYLOAD:
        raise ValueError('Invalid UART frame header')
    return header + exact(size)


def execute(port, args, result):
    result['phase'] = 'initial_at'
    command(port, b'AT\r\n')
    command(port, b'ATE0\r\n')
    result['phase'] = 'association'
    result['association'] = associate(port, args.credential_provider)
    if not args.direction:
        result.update(ok=True, phase='info_complete', command_mode=True, baud=args.old_baud)
        return
    connected = entering_transparent = False
    peer = None
    try:
        if args.baud != args.old_baud:
            result['phase'] = 'baud_transition'
            command(port, f'AT+UART_CUR={args.baud},8,1,0,0\r\n'.encode(),
                    timeout=.4, required=False)
            port.baudrate = args.baud
            time.sleep(.10)
            port.reset_input_buffer()
            command(port, b'AT\r\n')
        result['baud'] = args.baud
        result['phase'] = 'tcp_setup'
        command(port, b'AT+CIPMUX=0\r\n')
        command(port, b'AT+CIPMODE=1\r\n')
        nonce = secrets.randbits(32)
        millis = args.seconds * 1000
        peer = Peer(args.bind, args.out / 'pi', nonce, args.baud, millis, args.direction)
        command(port, f'AT+CIPSTART="TCP","{args.bind}",{peer.port}\r\n'.encode(), timeout=10)
        connected = True
        entering_transparent = True
        command(port, b'AT+CIPSEND\r\n', prompt=True)
        time.sleep(.05)
        port.reset_input_buffer()
        result['phase'] = 'data'
        with (args.out / 'uart-received.bin').open('xb') as retained:
            write_all(port, frame(0, struct.pack('<4I', nonce, args.baud, millis, PAYLOAD)))
            deadline = time.monotonic() + 8
            if check(read_frame(port, deadline, retained), 0)[1] != b'GO':
                raise ValueError('Invalid GO')
            start = time.monotonic()
            if args.direction == 'up':
                # Consume the control-only response before starting bulk.
                if check(read_frame(port, deadline, retained), 1)[1]:
                    raise ValueError('Unexpected reverse bulk data')
                while time.monotonic() - start < args.seconds:
                    seq = result['tx_frames'] + 1
                    write_all(port, frame(seq, pattern(seq, UP)))
                    result['tx_frames'] = seq
                write_all(port, frame(result['tx_frames'] + 1))
                port.flush()
            else:
                write_all(port, frame(1))
                deadline = start + args.seconds + 12
                while check(read_frame(port, deadline, retained), result['rx_frames'] + 1, DOWN)[1]:
                    result['rx_frames'] += 1
            result['transfer_seconds'] = time.monotonic() - start
            if not peer.finished.wait(5):
                raise TimeoutError('TCP peer did not complete')
            result['ok'] = (peer.result['pass'] and
                            result['tx_frames'] == peer.result['rx_frames'] and
                            result['rx_frames'] == peer.result['tx_frames'] and
                            result['tx_frames'] + result['rx_frames'] > 0)
            result['phase'] = 'data_complete'
    finally:
        try:
            if connected:
                if entering_transparent:
                    time.sleep(1.2)
                    write_all(port, b'+++')
                    port.flush()
                    time.sleep(1.2)
                    port.reset_input_buffer()
                command(port, b'AT\r\n')
                result['command_mode'] = True
                command(port, b'AT+CIPCLOSE\r\n', required=False)
                command(port, b'AT+CIPMODE=0\r\n')
                result['cleanup'] = True
        except Exception as error:
            result['cleanup_error'] = type(error).__name__
        finally:
            if peer:
                peer.close()
                result['peer'] = peer.result
        result['ok'] = result['ok'] and result.get('cleanup', False)


def main():
    harden()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--credential-provider', choices=('login-keyring', 'systemd-host'), default='login-keyring')
    parser.add_argument('--port', required=True)
    parser.add_argument('--old-baud', required=True, type=int, choices=RATES)
    parser.add_argument('--baud', type=int, choices=RATES)
    parser.add_argument('--direction', choices=('up', 'down'))
    parser.add_argument('--bind')
    parser.add_argument('--seconds', type=int, choices=(3, 10, 30, 60), default=3)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.direction and (not args.baud or not args.bind or
                           ipaddress.ip_address(args.bind).version != 4 or
                           not ipaddress.ip_address(args.bind).is_private):
        parser.error('Transfer needs an explicit baud and local private IPv4 bind')
    require_header_uart(args.port)
    args.out.mkdir(exist_ok=False)
    result = dict(ok=False, phase='open', tx_frames=0, rx_frames=0,
                  from_baud=args.old_baud, direction=args.direction, seconds=args.seconds)
    try:
        with serial.Serial(args.port, args.old_baud, timeout=.05, write_timeout=2,
                           exclusive=True, xonxoff=False, rtscts=False, dsrdtr=False) as port:
            execute(port, args, result)
    except Exception as error:
        result.update(ok=False, error_type=type(error).__name__)
    finally:
        result['tx_bytes'] = result['tx_frames'] * PAYLOAD
        result['rx_bytes'] = result['rx_frames'] * PAYLOAD
        (args.out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
