#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inject Korean translations from script_ko.tsv into D_MESS.
TSV columns: base <TAB> index <TAB> korean   ('@' = forced dialogue-box break)
Layout rules (measured from the original): line <= LINE_MAX half-units, <= MAX_LINES per box,
word-wrap on spaces, overflow continues in a new box (0x1E). 0x1D = line break, 0x1F = end.
Each affected sub-file is rebuilt in place (offset table recomputed); untouched messages keep
their original bytes. Sub-files are 0x800-aligned, zero-padded blocks."""
import sys, struct, csv
sys.path.insert(0, 'tools')
from hangul_font import ksx1001_hangul
from mess_parse import parse_table

# Per-region layout, measured from the original text (half-units per line, lines per box).
# Dialogue boxes hold 3 lines; the encyclopedia and BBS are scrollable pages with their own
# narrower/taller areas, so wrapping the whole game at the dialogue width would overflow them.
LAYOUT = [
    (0x09000, 512, 688, 20, 21),   # youkai encyclopedia page (original max width 22)
    (0x09000,   0, 511, 34, 37),   # mononoke BBS page
    (0x09000, 689, 9999, 34, 21),  # encyclopedia names / letter animation
    (0x06000,   0, 9999, 28,  3),  # mission objectives panel (original max 30)
    (0x07000,   0, 9999, 36,  6),  # save / item panels
    (0x04000,   0, 9999, 34, 99),  # debug menus: '|' separates list items, never paginate
]
DEFAULT_LINE_MAX, DEFAULT_MAX_LINES = 34, 3
LINE_MAX, MAX_LINES = DEFAULT_LINE_MAX, DEFAULT_MAX_LINES

def layout_for(base, idx):
    for b, lo, hi, lm, ml in LAYOUT:
        if b == base and lo <= idx <= hi:
            return lm, ml
    return DEFAULT_LINE_MAX, DEFAULT_MAX_LINES
KSX = ksx1001_hangul(); KIDX = {c: i for i, c in enumerate(KSX)}
PUNC1 = {' ': 0x20, '!': 0x21, '"': 0x22, '(': 0x28, ')': 0x29, ',': 0x2c, '.': 0x2e,
         '?': 0x3f, '~': 0x7e, ':': 0x3a, '-': 0x2d, "'": 0x27, '/': 0x2f, '%': 0x25,
         '<': 0x3c, '>': 0x3e, ';': 0x3b, '+': 0x2b, '*': 0x2a, '=': 0x3d, '#': 0x23,
         '&': 0x26, '@@': 0x40, '[': 0x5b, ']': 0x5d, '_': 0x5f, '^': 0x5e,
         '`': 0x60, '{': 0x7b, '}': 0x7d}
for ch in '0123456789': PUNC1[ch] = ord(ch)

def cw(ch):
    if ch == ' ' or ch in PUNC1 or ('A' <= ch <= 'Z') or ('a' <= ch <= 'z'): return 1
    return 2                      # includes U+3000, the full-width space

def wrap_into(text, lines):
    """word-wrap one logical line into `lines`, splitting only on spaces.
    A run of spaces at the start is indentation and is kept."""
    lead = len(text) - len(text.lstrip(' '))
    cur = ' ' * lead; cur_w = lead; first = True
    for word in text.split(' '):
        if word == '': continue
        ww = sum(cw(c) for c in word)
        if first:
            cur += word; cur_w += ww; first = False
        elif cur_w + 1 + ww <= LINE_MAX:
            cur += ' ' + word; cur_w += 1 + ww
        else:
            lines.append(cur); cur, cur_w = word, ww
        while cur_w > LINE_MAX:                     # single word longer than a line
            acc = 0; idx = 0
            for i, c in enumerate(cur):
                if acc + cw(c) > LINE_MAX: break
                acc += cw(c); idx = i + 1
            lines.append(cur[:idx]); cur = cur[idx:]; cur_w = sum(cw(c) for c in cur)
    lines.append(cur)

def layout(script):
    """'@' = forced dialogue-box break, '|' = forced line break, otherwise word-wrap.
    Boxes hold at most MAX_LINES lines; the overflow continues in the next box."""
    boxes = []
    for seg in script.split('@'):
        lines = []
        for forced in seg.split('|'):
            wrap_into(forced, lines)
        if not lines: lines = ['']
        for i in range(0, len(lines), MAX_LINES):
            boxes.append(lines[i:i + MAX_LINES])
    return boxes

def enc_char(ch, out, miss):
    if ch == '　': out += bytes([0x02, 0x00])   # full-width space (glyph 0x400)
    elif ch in '·・': out.append(0x87)   # middle dot
    elif ch == '「': out.append(0x89)
    elif ch == '」': out.append(0x8a)
    elif ch == '…': out += bytes([0x01, 0xac])
    elif ch in PUNC1: out.append(PUNC1[ch])
    elif 'A' <= ch <= 'Z' or 'a' <= ch <= 'z': out.append(ord(ch))
    else:
        i = KIDX.get(ch)
        if i is None: miss.append(ch)
        else:
            c = 0x200 + i; out += bytes([c >> 8, c & 0xFF])

def encode(script, line_max=None, max_lines=None):
    global LINE_MAX, MAX_LINES
    LINE_MAX = line_max or DEFAULT_LINE_MAX
    MAX_LINES = max_lines or DEFAULT_MAX_LINES
    boxes = layout(script); out = bytearray(); miss = []
    for bi, box in enumerate(boxes):
        if bi: out.append(0x1E)
        for li, line in enumerate(box):
            if li: out.append(0x1D)
            for ch in line: enc_char(ch, out, miss)
    out.append(0x1F)
    return bytes(out), miss, boxes

def sub_bases(d):
    out = []
    for base in range(0, len(d), 0x800):
        t = parse_table(d, base)
        if len(t) >= 3 and t[0] == base + 2*len(t): out.append(base)
    return out

def main():
    src = open('extract/D_MESS.BIN', 'rb').read()
    d = bytearray(src)
    bases = sub_bases(src)
    trans = {}
    with open('script_ko.tsv', encoding='utf-8') as f:
        for row in csv.reader(f, delimiter='\t'):
            if not row or row[0] == 'base' or len(row) < 3: continue
            trans.setdefault(int(row[0], 16), {})[int(row[1])] = row[2]
    miss_all = {}; over = []
    for base, tr in sorted(trans.items()):
        i = bases.index(base)
        nxt = bases[i+1] if i+1 < len(bases) else len(src)
        end = src.rfind(b'\x1f', base, nxt) + 1
        region = nxt - base
        tbl = parse_table(src, base); n = len(tbl)
        contents = []
        for k in range(n):
            s = tbl[k]; e = tbl[k+1] if k+1 < n else end
            if k in tr:
                lm, ml = layout_for(base, k)
                enc, miss, boxes = encode(tr[k], lm, ml)
                if miss: miss_all.setdefault(base, {})[k] = miss
                if any(len(b) > ml for b in boxes): over.append((base, k))
                contents.append(enc)
            else:
                contents.append(src[s:e] if e > s else b'')
        pos = n*2; offs = []
        for c in contents: offs.append(pos); pos += len(c)
        if pos > region:
            print(f"sub {base:#07x}: OVER BUDGET {pos} > {region}"); sys.exit(1)
        blk = bytearray(region)
        for k in range(n): struct.pack_into('<H', blk, 2*k, offs[k] - 2*k)
        for k in range(n): blk[offs[k]:offs[k]+len(contents[k])] = contents[k]
        d[base:base+region] = blk
        print(f"sub {base:#07x}: {len(tr):5d} strings, {pos}/{region} bytes")
    if miss_all:
        for base, mm in miss_all.items():
            for k, m in mm.items(): print(f"MISSING sub {base:#x} msg {k}: {''.join(sorted(set(m)))}")
        sys.exit(1)
    if over: print("boxes over 3 lines:", over); sys.exit(1)
    open('D_MESS_ko.BIN', 'wb').write(d)
    assert len(d) == len(src)
    print(f"wrote D_MESS_ko.BIN ({sum(len(t) for t in trans.values())} strings total)")

if __name__ == '__main__':
    main()
