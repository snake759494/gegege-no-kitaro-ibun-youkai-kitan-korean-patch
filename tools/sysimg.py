#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D_SYS.BIN / D_EFF.BIN sprite-container reader-writer.

Container layout (verified on D_SYS.BIN):
    u16 magic (0x5f51 or 0x5f71), u16 count, u32 dataStart, u32 pad
    count * 16-byte records at +8:  u32 A, u16 w, u16 h, u16 w/2, u16 h/2, u32 nextOff
    256 * u16 RGBA5551 palette      (right before dataStart)
    pixel data, 8bpp, linear, images stored back-to-back from dataStart

The record's u32 offset field is the offset of the *following* image, so
image i lives at dataStart when i == 0 and at record[i-1].off otherwise.
"""
import struct
from PIL import Image, ImageDraw

MAGICS = (0x5f51, 0x5f71)


class Sprite:
    __slots__ = ('idx', 'off', 'w', 'h', 'A')

    def __init__(self, idx, off, w, h, A):
        self.idx, self.off, self.w, self.h, self.A = idx, off, w, h, A

    @property
    def size(self):
        return self.w * self.h


class Pack:
    """One sprite container located at `base` inside `data`."""

    def __init__(self, data, base):
        self.data = bytearray(data)
        self.base = base
        magic, self.count, self.dstart, _ = struct.unpack_from('<HHII', data, base)
        if magic not in MAGICS:
            raise ValueError('bad magic %04x at %#x' % (magic, base))
        recs = [struct.unpack_from('<IHHHHI', data, base + 8 + i * 16)
                for i in range(self.count)]
        self.paloff = base + 8 + self.count * 16
        palbytes = self.dstart - (8 + self.count * 16)
        if palbytes == 512:
            self.bpp, ncol = 8, 256
        elif palbytes == 32:
            self.bpp, ncol = 4, 16
        else:
            raise ValueError('odd palette size %d at %#x' % (palbytes, base))
        self.sprites = []
        for i, (A, w, h, _hw, _hh, nxt) in enumerate(recs):
            off = self.dstart if i == 0 else recs[i - 1][5]
            self.sprites.append(Sprite(i, off, w, h, A))
        self.palette = [struct.unpack_from('<H', data, self.paloff + i * 2)[0]
                        for i in range(ncol)]

    # ---- palette helpers -------------------------------------------------
    @staticmethod
    def rgb(v):
        return ((v & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31,
                ((v >> 10) & 31) * 255 // 31)

    def rgb_palette(self):
        return [self.rgb(v) for v in self.palette]

    # ---- pixel access ----------------------------------------------------
    def raw_len(self, i):
        s = self.sprites[i]
        return s.size if self.bpp == 8 else (s.size + 1) // 2

    def indices(self, i):
        s = self.sprites[i]
        o = self.base + s.off
        raw = self.data[o:o + self.raw_len(i)]
        if self.bpp == 8:
            return bytearray(raw)
        out = bytearray(s.size)
        for j, b in enumerate(raw):
            out[j * 2] = b & 15
            if j * 2 + 1 < s.size:
                out[j * 2 + 1] = b >> 4
        return out

    def image(self, i):
        s = self.sprites[i]
        pal = self.rgb_palette()
        im = Image.new('RGB', (s.w, s.h))
        im.putdata([pal[c] for c in self.indices(i)])
        return im

    def put_indices(self, i, idx):
        s = self.sprites[i]
        if len(idx) != s.size:
            raise ValueError('sprite %d expects %d px, got %d' % (i, s.size, len(idx)))
        o = self.base + s.off
        if self.bpp == 8:
            self.data[o:o + s.size] = bytes(idx)
        else:
            raw = bytearray(self.raw_len(i))
            for j in range(len(raw)):
                lo = idx[j * 2] & 15
                hi = (idx[j * 2 + 1] & 15) if j * 2 + 1 < s.size else 0
                raw[j] = lo | (hi << 4)
            self.data[o:o + len(raw)] = bytes(raw)


def find_packs(data, limit=None):
    """Scan 0x800-aligned offsets for sprite containers."""
    out = []
    for off in range(0, len(data) - 16, 0x800):
        magic, count, dstart, pad = struct.unpack_from('<HHII', data, off)
        if magic not in MAGICS or not (0 < count < 4096) or pad != 0:
            continue
        if dstart - (8 + count * 16) not in (512, 32):
            continue
        out.append(off)
        if limit and len(out) >= limit:
            break
    return out


def sheet(pack, cols=8, pad=2, bg=(255, 0, 255)):
    """Contact sheet of every sprite in a pack, with index labels."""
    ims = [pack.image(i) for i in range(pack.count)]
    rows = (len(ims) + cols - 1) // cols
    cw = max(im.width for im in ims) + pad * 2
    ch = max(im.height for im in ims) + pad * 2 + 10
    out = Image.new('RGB', (cw * cols, ch * rows), bg)
    dr = ImageDraw.Draw(out)
    for i, im in enumerate(ims):
        x, y = (i % cols) * cw, (i // cols) * ch
        out.paste(im, (x + pad, y + pad + 10))
        dr.text((x + 1, y), str(i), fill=(255, 255, 255))
    return out


if __name__ == '__main__':
    import os, sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'scan'
    src = sys.argv[2] if len(sys.argv) > 2 else 'extract/D_SYS.BIN'
    d = open(src, 'rb').read()
    if cmd == 'scan':
        for off in find_packs(d):
            p = Pack(d, off)
            end = max(s.off + s.size for s in p.sprites)
            print('%#08x  count=%-4d bpp=%d dstart=%#-8x end=%#-8x sizes=%s' % (
                off, p.count, p.bpp, p.dstart, end,
                sorted({(s.w, s.h) for s in p.sprites})[:6]))
    elif cmd == 'sheet':
        outdir = sys.argv[3] if len(sys.argv) > 3 else 'sheets'
        os.makedirs(outdir, exist_ok=True)
        for off in find_packs(d):
            p = Pack(d, off)
            fn = os.path.join(outdir, 'pack_%06x.png' % off)
            sheet(p).save(fn)
            print(fn, p.count)
