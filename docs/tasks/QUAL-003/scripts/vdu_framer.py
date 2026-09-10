"""Bounded graphics-review framing, not a production VDU parser.

Length grammar covers the vendored Shapes/Bitmaps corpus and boot/query traffic.
Native VDP interprets each complete command. Binary buffer/bitmap payloads stay
opaque, including bytes matching the private control prefix. Unknown commands
fail closed rather than scanning ahead and misclassifying a payload as control.
The independent suite decoders validate the generated command corpus.
"""
class Incomplete(Exception):
    pass


class Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def take(self, size):
        if size < 0 or size > 2**20:
            raise ValueError('Review command length exceeds bound')
        if self.pos + size > len(self.data):
            raise Incomplete()
        out = self.data[self.pos:self.pos+size]
        self.pos += size
        return out

    def byte(self):
        return self.take(1)[0]

    def word(self):
        return int.from_bytes(self.take(2), 'little')


def command_length(data):
    r = Reader(data)
    cmd = r.byte()
    if cmd >= 32:
        return 1
    if cmd != 23:
        r.take({1:1,17:1,18:2,19:5,22:1,24:8,25:5,27:1,
                28:4,29:4,31:2}.get(cmd, 0))
        return r.pos
    sub = r.byte()
    if sub not in (0,27):
        if sub not in (1,6,7,23) and sub < 32:
            raise ValueError(f'Unsupported VDU23 subcommand {sub}')
        r.take({1:1,6:8,7:3,23:1}.get(sub,8))
        return r.pos
    op = r.byte()
    if sub == 27:
        if op in (0,4,6,7,10,18,21): r.take(1)
        elif op in (3,13,14): r.take(4)
        elif op in (32,38,53): r.take(2)
        elif op in (1,2,33):
            width, height = r.word(), r.word()
            if height: r.take((width*height*4 if op==1 else 4) if op!=33 else 1)
        elif op not in (5,8,9,11,12,15,16,17,19,20):
            raise ValueError(f'Unsupported sprite command {op}')
        return r.pos
    lengths = {0x80:1,0x81:1,0x82:0,0x84:4,0x86:0,0x96:3,
               0x9c:0,0x9d:0,0x9e:0,0x9f:0,0xc0:1,0xc8:1,0xca:0,
               0xf2:1,0xf7:16,0xf8:4,0xf9:2}
    if op in lengths:
        r.take(lengths[op]); return r.pos
    if op != 0xa0:
        raise ValueError(f'Unsupported system command {op:02x}')
    r.word()  # buffer identifier
    op = r.byte()
    if op == 0: r.take(r.word())
    elif op in (1,2,14): pass
    elif op == 13:
        while r.word() != 65535: pass
    elif op == 5:
        adjust = r.byte(); base = adjust & 15
        if base not in (0,5,6,7) or adjust & 16:
            raise ValueError('Unsupported buffer adjustment')
        r.word(); count = r.word() if adjust & 0xc0 else 1
        if base:
            r.take(4 if adjust & 32 else (count if adjust & 128 else 1))
    elif op == 32:
        operation = r.byte(); base = operation & 15
        argc = {0:0,1:0,2:1,3:1,4:1,5:2,6:2,7:2,8:2,9:2,10:2,11:6,12:2}[base]
        if base == 12: r.word()
        if argc:
            fmt = r.byte()
            if fmt & 32: raise ValueError('Unsupported matrix format')
            if operation & 32: r.take(4)
            else:
                for i in range(argc):
                    if i and operation & 64: fmt = r.byte()
                    if fmt & 32: raise ValueError('Unsupported matrix format')
                    r.take(2 if fmt & 128 else 4)
    elif op == 40:
        flags = r.byte()
        if flags >= 8: raise ValueError('Unsupported bitmap transform flags')
        r.take(4)
        if flags & 2: r.take(4)
    elif op == 72:
        flags = r.byte(); bits = flags & 7
        if bits not in (1,2,4): raise ValueError('Unsupported expansion size')
        r.word()
        if flags & 8: r.word()
        r.take(2 if flags & 16 else 1 << bits)
    else:
        raise ValueError(f'Unsupported buffer command {op}')
    return r.pos


class Framer:
    def __init__(self):
        self.pending = bytearray()

    def feed(self, data):
        self.pending.extend(data)
        commands = []
        while self.pending:
            try: length = command_length(self.pending)
            except Incomplete: break
            command = bytes(self.pending[:length]); del self.pending[:length]
            commands.append(command)
        return commands
