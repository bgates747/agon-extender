"""Official buffered command 5/&C2: overwrite preallocated buffer &E100.

The eleven-byte header counts toward the transport batch boundary. Payload is
binary data, never executed VDU. No allocation is performed by this command.
"""
import hashlib
import struct

BUFFER = 0xE100
LENGTHS = (256, 4096, 4097, 8192)
HEADER_BYTES = 11


def data(length):
    return bytes((i * 73 + 19) & 255 for i in range(length))


def stream(length):
    if length not in LENGTHS:
        raise ValueError('unsupported frozen stream length')
    count = length - HEADER_BYTES
    return (bytes((23, 0, 0xA0)) + struct.pack('<H', BUFFER) +
            bytes((5, 0xC2)) + struct.pack('<HH', 0, count) + data(count))


def manifest():
    return [dict(wire_bytes=n, data_bytes=n-HEADER_BYTES,
                 sha256=hashlib.sha256(stream(n)).hexdigest()) for n in LENGTHS]


def expected_buffer(length):
    return data(length - HEADER_BYTES) + bytes([0xAA]) * (8192-length+HEADER_BYTES)
