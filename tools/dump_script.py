#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dump every D_MESS message as readable Japanese text using glyph_map.json.
Output TSV: base<TAB>index<TAB>text   ('|' = line break 0x1D, '@' = box break 0x1E)"""
import sys, json
sys.path.insert(0, 'tools')
from mess_parse import parse_table, tokens

CTL = {0x85: '、', 0x86: '。', 0x89: '「', 0x8a: '」', 0x80: '〝', 0x1D: '|', 0x1E: '@'}

def sub_bases(d):
    out = []
    for base in range(0, len(d), 0x800):
        t = parse_table(d, base)
        if len(t) >= 3 and t[0] == base + 2*len(t): out.append(base)
    return out

def main():
    d = open('extract/D_MESS.BIN', 'rb').read()
    gm = {int(k, 16): v for k, v in json.load(open('glyph_map.json', encoding='utf-8')).items()}
    bases = sub_bases(d)
    rows = []
    for i, base in enumerate(bases):
        nxt = bases[i+1] if i+1 < len(bases) else len(d)
        end = d.rfind(b'\x1f', base, nxt) + 1
        tbl = parse_table(d, base); n = len(tbl)
        for k in range(n):
            s = tbl[k]; e = tbl[k+1] if k+1 < n else end
            if e <= s: continue
            out = []
            for typ, val, off in tokens(d[s:e]):
                if typ == 'code':
                    out.append(gm.get(val + 0x200, f'<g{val+0x200:03x}>'))
                elif typ == 'ascii':
                    out.append(chr(val))
                else:
                    if val == 0x1F: continue
                    out.append(CTL.get(val, f'<{val:02x}>'))
            t = ''.join(out)
            if t.strip(): rows.append((base, k, t))
    with open('script_jp.tsv', 'w', encoding='utf-8') as f:
        f.write('base\tindex\ttext\n')
        for base, k, t in rows: f.write(f'{base:#07x}\t{k}\t{t}\n')
    print(f"dumped {len(rows)} messages to script_jp.tsv")

if __name__ == '__main__':
    main()
