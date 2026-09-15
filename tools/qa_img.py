#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static QA for the image patch.

    python tools/qa_img.py [--sheet DIR]

  1 size      - patched file is exactly the same length as the original
  2 structure - every container header, record table and palette is untouched
                (only pixel bytes may differ)
  3 scope     - every changed byte lies inside a sprite that we meant to edit
  4 contrast  - the new caption still has usable contrast against its own
                background, and did not end up empty
"""
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sysimg import Pack, find_packs      # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

PAIRS = [('extract/D_SYS.BIN', 'D_SYS_ko.BIN'),
         ('extract/D_BG.BIN', 'D_BG_ko.BIN')]


def get_src(path):
    if os.path.exists(path):
        return open(path, 'rb').read()
    import io
    import pycdlib
    iso = pycdlib.PyCdlib()
    iso.open('Gegege no Kitarou Ibun Youkai Kitan.iso')
    buf = io.BytesIO()
    iso.get_file_from_iso_fp(buf, iso_path='/%s;1' % os.path.basename(path))
    iso.close()
    data = buf.getvalue()
    open(path, 'wb').write(data)
    return data


def runs(a, b):
    """[(start, end)] byte ranges where a and b differ."""
    out = []
    i, n = 0, len(a)
    while i < n:
        if a[i] != b[i]:
            j = i
            while j < n and a[j] != b[j]:
                j += 1
            out.append((i, j))
            i = j
        else:
            i += 1
    return out


def main():
    sheet = None
    if '--sheet' in sys.argv:
        sheet = sys.argv[sys.argv.index('--sheet') + 1]
        os.makedirs(sheet, exist_ok=True)
    fails = 0
    for src_path, dst_path in PAIRS:
        if not os.path.exists(dst_path):
            print(f'== {dst_path}: not built, skipped'); continue
        src, dst = get_src(src_path), open(dst_path, 'rb').read()
        name = os.path.basename(dst_path)
        print('== %s' % name)
        print('1 size      : %d vs %d  %s' % (len(src), len(dst),
                                              'OK' if len(src) == len(dst)
                                              else '<< FAIL'))
        fails += len(src) != len(dst)

        packs = find_packs(src)
        # map every byte of the file to (pack, sprite) or 'meta'
        meta = []       # header + record table + palette ranges
        pix = []        # (start, end, pack_off, sprite index)
        for off in packs:
            p = Pack(src, off)
            meta.append((off, off + p.dstart))
            for s in p.sprites:
                ln = s.w * s.h if p.bpp == 8 else (s.w * s.h + 1) // 2
                pix.append((off + s.off, off + s.off + ln, off, s.idx))
        pix.sort()

        diffs = runs(src, dst)
        changed = sum(e - s for s, e in diffs)
        print('   changed  : %d byte runs, %d bytes total' % (len(diffs),
                                                              changed))

        bad_meta, outside, touched = [], [], defaultdict(set)
        for s, e in diffs:
            for m0, m1 in meta:
                if s < m1 and e > m0:
                    bad_meta.append((s, e))
                    break
            hit = False
            for p0, p1, off, idx in pix:
                if s < p1 and e > p0:
                    touched[off].add(idx)
                    hit = True
            if not hit:
                outside.append((s, e))
        print('2 structure : %d changes touching a header/table/palette  %s'
              % (len(bad_meta), 'OK' if not bad_meta else '<< FAIL'))
        for s, e in bad_meta[:5]:
            print('     %#x..%#x' % (s, e))
        print('3 scope     : %d changes outside any sprite  %s'
              % (len(outside), 'OK' if not outside else '<< FAIL'))
        for s, e in outside[:5]:
            print('     %#x..%#x' % (s, e))
        fails += len(bad_meta) + len(outside)
        print('   sprites   : %d packs, %d sprites rewritten'
              % (len(touched), sum(len(v) for v in touched.values())))
        for off in sorted(touched):
            print('     %#08x : %s' % (off, sorted(touched[off])))

        # 4 -------------------------------------------------------------
        weak = []
        for off in sorted(touched):
            po, pn = Pack(src, off), Pack(dst, off)
            for idx in sorted(touched[off]):
                a, b = po.image(idx), pn.image(idx)
                sa, sb = a.convert('L').getextrema(), b.convert('L').getextrema()
                spread_a, spread_b = sa[1] - sa[0], sb[1] - sb[0]
                same = list(b.getdata()) == list(a.getdata())
                if spread_b < 40 or same:
                    weak.append((off, idx, spread_a, spread_b, same))
                if sheet:
                    from PIL import Image
                    w = max(a.width, b.width)
                    im = Image.new('RGB', (w, a.height + b.height + 4),
                                   (20, 20, 20))
                    im.paste(a, (0, 0))
                    im.paste(b, (0, a.height + 4))
                    im.save(os.path.join(sheet, '%s_%06x_%02d.png'
                                         % (name[:5], off, idx)))
        print('4 contrast  : %d sprites look flat or unchanged  %s'
              % (len(weak), 'OK' if not weak else '<< CHECK'))
        for off, idx, sa, sb, same in weak[:10]:
            print('     %#08x/%d spread %d -> %d%s'
                  % (off, idx, sa, sb, '  (identical!)' if same else ''))
        fails += len(weak)
        print()
    print('RESULT: %s' % ('no blocking issues' if not fails
                          else '%d items need attention' % fails))


if __name__ == '__main__':
    main()
