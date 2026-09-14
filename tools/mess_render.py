#!/usr/bin/env python3
"""Render messages of a D_MESS sub-file to a stacked PNG using the D_MOJI font, for visual matching.
Usage: python mess_render.py D_MESS.BIN D_MOJI.BIN BASE_HEX START COUNT OUT.png"""
import sys, struct
import numpy as np
from PIL import Image
sys.path.insert(0, 'tools')
from moji_font import decode as decode_font, W, H
from mess_parse import parse_table, tokens

def main():
    mess = open(sys.argv[1], 'rb').read()
    px = decode_font(open(sys.argv[2], 'rb').read())
    base = int(sys.argv[3], 16); start = int(sys.argv[4]); count = int(sys.argv[5]); out = sys.argv[6]
    tbl = parse_table(mess, base)
    end_of_file = None
    lut = np.array([0, 255, 200, 100], np.uint8)
    rows = []
    for k in range(start, min(start + count, len(tbl))):
        s = tbl[k]; e = tbl[k + 1] if k + 1 < len(tbl) else mess.find(b'\x1f', s) + 1
        seg = mess[s:e]
        line_glyphs = [[]]
        for typ, val, off in tokens(seg):
            if typ == 'ascii': line_glyphs[-1].append(val)
            elif typ == 'code': line_glyphs[-1].append(val + 0x200)
            elif typ == 'ctl' and val == 0x1D: line_glyphs.append([])   # newline
            elif typ == 'ctl' and val == 0x1E: line_glyphs.append([-1]); line_glyphs.append([])  # box break marker
            # other control codes ignored for rendering
        for gl in line_glyphs:
            wpx = max(1, len(gl)) * W
            img = np.zeros((H, wpx), np.uint8)
            if gl == [-1]:
                img[H//2-1:H//2+1, :] = 90   # box-break separator bar
            else:
                for i, g in enumerate(gl):
                    if 0 <= g < len(px): img[:, i*W:(i+1)*W] = lut[px[g]]
            # label with index
            rows.append((k, img))
    maxw = max(im.shape[1] for _, im in rows) if rows else W
    labelw = 60
    canvas = np.full((len(rows) * (H + 4), labelw + maxw), 30, np.uint8)
    from PIL import ImageDraw, ImageFont
    pil = Image.fromarray(canvas)
    d = ImageDraw.Draw(pil); f = ImageFont.load_default()
    for r, (k, im) in enumerate(rows):
        y = r * (H + 4)
        arr = np.array(pil)
        arr[y:y+H, labelw:labelw+im.shape[1]] = im
        pil = Image.fromarray(arr)
        d = ImageDraw.Draw(pil)
        d.text((2, y + 6), f"{k}", fill=255, font=f)
    pil.save(out)
    print(f"rendered messages {start}..{start+count-1} of sub-file {base:#x} -> {out} ({len(tbl)} msgs in sub-file)")

if __name__ == '__main__':
    main()
