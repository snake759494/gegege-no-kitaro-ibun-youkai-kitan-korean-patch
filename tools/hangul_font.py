#!/usr/bin/env python3
"""Render KS X 1001 (완성형) 2350 Hangul syllables with a TTF into D_MOJI.BIN glyph slots.

Value semantics of D_MOJI.BIN (derived from the original glyphs): 0 = transparent,
1 = full coverage, 2 = ~2/3 coverage, 3 = ~1/3 coverage (anti-aliasing levels).

Usage:
  python hangul_font.py render  FONT.ttf D_MOJI.BIN out.bin [--base 0x400] [--preview dir]
Writes out.bin plus <out>.map.tsv (glyph index, text code, char) and preview PNGs.
"""
import sys, os, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from moji_font import decode, encode, W, H, GL, sheet_labeled

SS = 8  # supersampling factor

def ksx1001_hangul():
    chars = []
    for hi in range(0xB0, 0xC9):
        for lo in range(0xA1, 0xFF):
            chars.append(bytes([hi, lo]).decode('cp949'))
    assert len(chars) == 2350
    return chars

def fit_font(ttf, chars, box_w=24, box_h=22, start=30):
    """Pick the largest font size whose union ink bbox (over all chars) fits box_w x box_h at 1x."""
    best = None
    for size in range(start * SS, 8 * SS, -1):
        f = ImageFont.truetype(ttf, size)
        x0 = y0 = 10**9; x1 = y1 = -10**9
        for ch in chars:
            b = f.getbbox(ch)
            x0 = min(x0, b[0]); y0 = min(y0, b[1]); x1 = max(x1, b[2]); y1 = max(y1, b[3])
        w = (x1 - x0) / SS; h = (y1 - y0) / SS
        if w <= box_w and h <= box_h:
            best = (size, x0, y0, x1, y1, w, h)
            break
    return best

# Coverage thresholds -> palette value. The game draws 1 = white, 2 = gray 200, 3 = gray 100 (opaque),
# and squeezes every glyph to ~0.83 of its width with bilinear filtering, so stroke cores must be solid 1s.
THRESH = (0.62, 0.38, 0.14)

def quantize(cov):
    q = np.zeros(cov.shape, np.uint8)
    q[cov >= THRESH[2]] = 3
    q[cov >= THRESH[1]] = 2
    q[cov >= THRESH[0]] = 1
    return q

def render_glyphs(ttf, chars, top_row=3, bottom_row=24, glyph_w=22):
    """Render every syllable so that the union ink box of all 2350 maps onto glyph_w x (bottom_row-top_row+1).
    The original kanji occupy about 22x22 px (cols 1..22, rows 3..24), so the Hangul union box is mapped
    onto the same 22x22 area (a slight horizontal stretch from the font's natural ~0.93 aspect)."""
    gh = bottom_row - top_row + 1
    size = 32 * SS
    f = ImageFont.truetype(ttf, size)
    x0 = y0 = 10**9; x1 = y1 = -10**9
    for ch in chars:
        b = f.getbbox(ch)
        x0 = min(x0, b[0]); y0 = min(y0, b[1]); x1 = max(x1, b[2]); y1 = max(y1, b[3])
    uw, uh = x1 - x0, y1 - y0
    print(f"union ink at {size/SS:.0f}px: {uw/SS:.1f}x{uh/SS:.1f} -> mapped to {glyph_w}x{gh} (x-stretch {glyph_w/gh/(uw/uh):.2f})")
    glyphs = np.zeros((len(chars), H, W), np.uint8)
    for i, ch in enumerate(chars):
        im = Image.new('L', (uw, uh), 0)
        ImageDraw.Draw(im).text((-x0, -y0), ch, font=f, fill=255)
        small = im.resize((glyph_w * SS, gh * SS), Image.BOX)          # anisotropic stretch, still supersampled
        cov = np.asarray(small, np.float32).reshape(gh, SS, glyph_w, SS).mean(axis=(1, 3)) / 255.0
        g = np.zeros((H, W), np.uint8)
        g[top_row:top_row + gh, (W - glyph_w) // 2:(W - glyph_w) // 2 + glyph_w] = quantize(cov)
        glyphs[i] = g
    return glyphs, (size, x0, y0, x1, y1, uw / SS, uh / SS)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['render'])
    ap.add_argument('ttf'); ap.add_argument('moji'); ap.add_argument('out')
    ap.add_argument('--base', type=lambda s: int(s, 0), default=0x400, help='first glyph index to overwrite')
    ap.add_argument('--preview', default=None)
    a = ap.parse_args()
    chars = ksx1001_hangul()
    glyphs, fit = render_glyphs(a.ttf, chars)
    orig = open(a.moji, 'rb').read()
    px = decode(orig).copy()
    n = len(chars)
    assert a.base + n <= len(px), 'does not fit'
    px[a.base:a.base + n] = glyphs
    data = encode(px)
    assert len(data) == len(orig)
    open(a.out, 'wb').write(data)
    with open(a.out + '.map.tsv', 'w', encoding='utf-8') as fp:
        fp.write('glyph_index\ttext_code\tchar\n')
        for i, ch in enumerate(chars):
            g = a.base + i
            fp.write(f'{g:#06x}\t{g - 0x100:#06x}\t{ch}\n')
    print(f'wrote {a.out}: {n} glyphs at {a.base:#x}..{a.base+n-1:#x}')
    if a.preview:
        os.makedirs(a.preview, exist_ok=True)
        sheet_labeled(glyphs, a.base, cols=32).save(os.path.join(a.preview, 'hangul_2350_labeled.png'))
        # comparison strip: original kana/kanji + hangul, raw bitmaps (top) and simulated in-game look (bottom)
        orig = decode(orig)
        samp = np.concatenate([orig[[0x32a, 0x329, 0x322, 0x325, 0x501, 0x502]], glyphs[[0, 1, 2200, 2210, 1000, 2349]]], axis=0)
        strip = np.concatenate([g for g in samp], axis=1)
        lut = np.array([0, 255, 200, 100], np.uint8)
        raw = Image.fromarray(lut[strip])
        sim = raw.resize((round(raw.width * 0.83), round(raw.height * 1.07)), Image.BILINEAR)
        out = Image.new('L', (raw.width * 6, raw.height * 6 + sim.height * 6 + 6), 64)
        out.paste(raw.resize((raw.width * 6, raw.height * 6), Image.NEAREST), (0, 0))
        out.paste(sim.resize((sim.width * 6, sim.height * 6), Image.NEAREST), (0, raw.height * 6 + 6))
        out.save(os.path.join(a.preview, 'compare_raw_vs_ingame_sim_6x.png'))
        print('preview written to', a.preview)

if __name__ == '__main__':
    main()
