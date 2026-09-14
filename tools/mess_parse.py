#!/usr/bin/env python3
"""Parse D_MESS.BIN: a concatenation of message sub-files (mess_%03x.bin).
Each sub-file = table of u16 self-relative offsets (entry i at 2i -> 2i+val), followed by
messages. Message bytes: 0x20..0x7F = 1-byte ASCII glyph; lead 0x00..0x0B + 1 byte = 2-byte
code (glyph = code + 0x200); other bytes = control codes (0x1D newline, 0x1F end, 0x80+ params).
"""
import struct, sys

def parse_table(d, base):
    tbl = []; i = 0
    while base + 2 * i + 2 <= len(d):
        v = struct.unpack_from('<H', d, base + 2 * i)[0]; tgt = base + 2 * i + v
        if v == 0 and not tbl: return []
        if tbl and (tgt < tbl[-1] or base + 2 * i >= tbl[0]): break
        if tgt > len(d): return []
        tbl.append(tgt); i += 1
    return tbl

def parse_all(d):
    """Yield (subfile_index, base, table) for every sub-file."""
    base = 0; k = 0
    while base + 4 <= len(d):
        tbl = parse_table(d, base)
        if not tbl: break
        # end of last message: first 0x1F at/after last target
        last = tbl[-1]
        e = d.find(b'\x1f', last)
        end = (e + 1) if e >= 0 else len(d)
        yield k, base, tbl, end
        k += 1
        base = (end + 3) & ~3

def tokens(seg):
    j = 0
    while j < len(seg):
        b = seg[j]
        if b < 0x0C and j + 1 < len(seg):
            yield ('code', (b << 8) | seg[j + 1], j); j += 2
        elif 0x20 <= b < 0x80:
            yield ('ascii', b, j); j += 1
        else:
            yield ('ctl', b, j); j += 1

if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    subs = list(parse_all(d))
    total = sum(len(t) for _, _, t, _ in subs)
    print(f'{len(subs)} sub-files, {total} messages, last end {subs[-1][3]:#x} of {len(d):#x}')
    for k, base, tbl, end in subs[:5] + subs[-3:]:
        print(f'  sub {k:3d}: base {base:#x} entries {len(tbl)} end {end:#x}')
