#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build D_BG_ko.BIN: Korean captions painted into the menu backgrounds.

    python tools/patch_bg.py [--preview DIR]

D_BG.BIN holds 176 full-screen 8bpp images; a handful of them are the mobile
phone / shop / newspaper screens whose labels are baked into the artwork.
Each job erases one rectangle (refilling it from the pixels beside it) and
draws the Korean caption in its place.  The file size never changes.
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sysimg import Pack, find_packs           # noqa: E402
import koimg                                  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'extract', 'D_BG.BIN')
ISO = os.path.join(ROOT, 'Gegege no Kitarou Ibun Youkai Kitan.iso')
DST = os.path.join(ROOT, 'D_BG_ko.BIN')

W = (255, 255, 255)
B = (0, 0, 0)

# ink predicates for inpaint-style plates (keep the texture, drop the glyphs)
PRED = {
    'warm': lambda c: c[0] > c[2] + 20,
    'bright': lambda c: min(c) > 165,
}

# index in find_packs order -> list of (box, korean, style)
JOBS = {
    # --- 妖怪リンク (phone link menu), 3-link and 2-link variants ----------
    68: [((104, 34, 316, 82), '요괴 링크',
          dict(fill=(255, 176, 64), outline=(72, 24, 0), stroke=2, pad=3,
               maxfill=0.86)),
         ((434, 379, 494, 409), '결정', dict(fill=W, outline=B, stroke=1,
                                             pad=2, maxfill=0.78)),
         ((541, 379, 601, 409), '뒤로', dict(fill=W, outline=B, stroke=1,
                                             pad=2, maxfill=0.78))],
    # --- 妖怪"y"ショッピング intro ---------------------------------------
    70: [((100, 60, 592, 134), '요괴 "y" 쇼핑',
          dict(fill=(238, 176, 222), outline=(96, 32, 88), stroke=2, pad=4,
               inpaint=('warm', 5), maxfill=0.62)),
         ((142, 168, 516, 250),
          '업계 최초, 요괴 E-다이렉트 숍!\n전국 어디든 배송료 무료로 배달.\n여러분의 방문을 기다리고 있습니다.',
          dict(fill=W, outline=(48, 32, 48), stroke=1, pad=4, align='l',
               line_gap=4, maxfill=0.95, max_pt=20)),
         ((424, 406, 486, 438), '결정', dict(fill=W, outline=B, stroke=1,
                                             pad=2, maxfill=0.74)),
         ((538, 406, 602, 438), '뒤로', dict(fill=W, outline=B, stroke=1,
                                             pad=2, maxfill=0.74))],
    # --- shop: 購入 / 売却 screens ----------------------------------------
    71: [((20, 20, 374, 68), '요괴 "y" 쇼핑',
          dict(fill=(255, 232, 240), outline=(96, 24, 72), stroke=2, pad=3,
               maxfill=0.84)),
         ((420, 24, 532, 62), '구 입', dict(fill=W, outline=(72, 32, 0),
                                            stroke=2, pad=3, maxfill=0.74)),
         ((476, 110, 616, 138), '다음 페이지',
          dict(fill=W, outline=B, stroke=1, pad=2, maxfill=0.80)),
         ((476, 135, 616, 163), '이전 페이지',
          dict(fill=W, outline=B, stroke=1, pad=2, maxfill=0.80)),
         ((481, 161, 528, 187), '결정', dict(fill=W, outline=B, stroke=1,
                                             pad=2, maxfill=0.74)),
         ((554, 161, 604, 187), '뒤로', dict(fill=W, outline=B, stroke=1,
                                             pad=2, maxfill=0.74)),
         ((524, 194, 602, 221), '소지금', dict(fill=W, outline=B, stroke=1,
                                               pad=2, maxfill=0.86,
                                               mode='box')),
         ((572, 221, 602, 247), '엔', dict(fill=W, outline=B, stroke=1,
                                           pad=2, maxfill=0.80, mode='box')),
         ((524, 249, 602, 277), '소유수', dict(fill=W, outline=B, stroke=1,
                                               pad=2, maxfill=0.86,
                                               mode='box')),
         ((550, 306, 602, 333), '금액', dict(fill=W, outline=B, stroke=1,
                                             pad=2, maxfill=0.86,
                                             mode='box')),
         ((572, 333, 602, 359), '엔', dict(fill=W, outline=B, stroke=1,
                                           pad=2, maxfill=0.80, mode='box'))],
    # --- もののけWEB article page -----------------------------------------
    77: [((72, 18, 438, 82), '모노노케WEB',
          dict(fill=(150, 26, 26), outline=(56, 8, 8), stroke=2, pad=3,
               maxfill=0.86)),
         ((504, 44, 553, 77), '뒤로', dict(fill=W, outline=B, stroke=1,
                                           pad=2, maxfill=0.70))],
    # --- 妖怪TIMES article page -------------------------------------------
    78: [((548, 44, 608, 84), '뒤로',
          dict(fill=(168, 236, 144), outline=(16, 56, 16), stroke=1, pad=3,
               mode='tile', src=(44, 140), maxfill=0.68))],
    # --- 妖怪TIMES topic list ---------------------------------------------
    79: [((546, 36, 606, 64), '결정',
          dict(fill=W, outline=B, stroke=1, pad=2, maxfill=0.78,
               mode='tile', src=(42, 140))),
         ((546, 64, 606, 92), '뒤로',
          dict(fill=W, outline=B, stroke=1, pad=2, maxfill=0.78,
               mode='tile', src=(42, 140))),
         ((254, 122, 388, 158), '토픽스', dict(fill=W, outline=B, stroke=1,
                                               pad=3, maxfill=0.80))],
    # --- 妖怪アパート establishing shot ------------------------------------
    87: [((228, 26, 424, 78), '요괴 아파트',
          dict(fill=(238, 238, 232), outline=(40, 36, 32), stroke=1, pad=3,
               inpaint=('bright', 5), maxfill=0.62))],
}

# 69 (2-link 妖怪リンク) and 72 (売却) share their neighbours' layout
JOBS[69] = JOBS[68]
JOBS[72] = [(b, ('매 각' if t == '구 입' else t), s) for b, t, s in JOBS[71]]


def load_src():
    if os.path.exists(SRC):
        return bytearray(open(SRC, 'rb').read())
    import pycdlib
    iso = pycdlib.PyCdlib()
    iso.open(ISO)
    buf = io.BytesIO()
    iso.get_file_from_iso_fp(buf, iso_path='/D_BG.BIN;1')
    iso.close()
    data = buf.getvalue()
    open(SRC, 'wb').write(data)
    return bytearray(data)


def main():
    preview = None
    if '--preview' in sys.argv:
        preview = sys.argv[sys.argv.index('--preview') + 1]
        os.makedirs(preview, exist_ok=True)
    buf = load_src()
    offs = find_packs(buf)
    for k in sorted(JOBS):
        p = Pack(buf, offs[k])
        p.data = buf
        for box, txt, style in JOBS[k]:
            style = dict(style)
            ink = style.pop('inpaint', None)
            if ink:
                style['plate'] = koimg.inpaint_ink(p, 0, box, PRED[ink[0]],
                                                   ink[1])
            koimg.paint_region(p, 0, box, txt, font_key='B', **style)
        if preview:
            p.image(0).save(os.path.join(preview, 'bg%03d.png' % k))
        print('bg %3d %#08x  %d captions' % (k, offs[k], len(JOBS[k])))
    with open(DST, 'wb') as f:
        f.write(buf)
    print('wrote', DST, len(buf))


if __name__ == '__main__':
    main()
