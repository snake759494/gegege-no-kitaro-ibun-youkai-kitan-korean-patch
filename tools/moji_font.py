#!/usr/bin/env python3
"""D_MOJI.BIN <-> PNG converter for GeGeGe no Kitaro: Ibun Youkai Kitan (PS2, SLPM-65337).

Format of D_MOJI.BIN (verified visually):
  * 3584 glyphs, each 24 px wide x 26 px tall, 2 bits per pixel, 4 pixels per byte.
    Pixel order inside a byte is NOT plain MSB-first: pixel 0 = bits 5..4, pixel 1 = bits 7..6,
    pixel 2 = bits 1..0, pixel 3 = bits 3..2 (each nibble holds two pixels, low pair first;
    high nibble first). Verified by minimising horizontal roughness over all 24 orders and by
    in-game rendering; the naive MSB-first order shows every vertical stroke as a doubled line.
  * 6 bytes per row, 156 bytes per glyph, glyphs stored back-to-back, no header.
  * Glyph index = block*256 + n. Blocks 0,1,2 are identical (ASCII/symbols),
    block 3 = kana, blocks 4..11 = kanji, blocks 12,13 are identical filler.
  * Pixel values 0..3 are palette indices (0 = transparent). In the PNG they are
    stored as gray 0/85/170/255 so that value = gray // 85 (editing sheet only).
  * In-game palette (from the ELF at 0x280820): 0 = transparent, 1 = white, 2 = gray 200, 3 = gray 100,
    all opaque. Viewing sheets use that palette. The game also draws each glyph squeezed to roughly
    2/3 of its width, which is why vertical strokes are stored as doubled lines.

Usage:
  python moji_font.py extract D_MOJI.BIN out_dir        # writes sheets + per-block PNGs
  python moji_font.py inject  sheet.png D_MOJI.BIN out.bin   # sheet must be the 64-col 1:1 layout
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, BPP = 24, 26, 2
VIEW_LUT = np.array([0, 255, 200, 100], dtype=np.uint8)   # in-game palette as gray
GL = W * H * BPP // 8          # 156
COLS_1TO1 = 64

def decode(data):
    n = len(data) // GL
    a = np.frombuffer(data[:n * GL], dtype=np.uint8)
    px = np.stack([(a >> 4) & 3, (a >> 6) & 3, a & 3, (a >> 2) & 3], axis=1)
    return px.reshape(n, H, W)

def encode(glyphs):
    g = glyphs.reshape(-1, 4).astype(np.uint16)  # 4 pixels per byte
    b = (g[:, 0] << 4) | (g[:, 1] << 6) | g[:, 2] | (g[:, 3] << 2)
    return b.astype(np.uint8).tobytes()

def sheet_1to1(px, cols=COLS_1TO1):
    n = len(px); rows = (n + cols - 1) // cols
    img = np.zeros((rows * H, cols * W), dtype=np.uint8)
    for i in range(n):
        r, c = divmod(i, cols)
        img[r*H:(r+1)*H, c*W:(c+1)*W] = px[i] * 85
    return Image.fromarray(img)

def sheet_labeled(px, start_index, cols=16, gap=2, label_w=44, label_h=14):
    """Grid with hex labels: row label = index of first glyph in row, column label = low nibble."""
    n = len(px); rows = (n + cols - 1) // cols
    cw, ch = W + gap, H + gap
    img = Image.new('L', (label_w + cols * cw, label_h + rows * ch), 40)
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    for c in range(cols):
        d.text((label_w + c * cw + 8, 1), f"{c:X}", fill=200, font=font)
    for r in range(rows):
        d.text((2, label_h + r * ch + 8), f"{start_index + r*cols:04X}", fill=200, font=font)
    arr = np.array(img)
    for i in range(n):
        r, c = divmod(i, cols)
        y = label_h + r * ch; x = label_w + c * cw
        arr[y:y+H, x:x+W] = VIEW_LUT[px[i]]
    return Image.fromarray(arr)

def cmd_extract(bin_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    data = open(bin_path, 'rb').read()
    px = decode(data)
    n = len(px)
    sheet_1to1(px).save(os.path.join(out_dir, 'D_MOJI_1to1_64col.png'))
    sheet_labeled(px, 0, cols=32).save(os.path.join(out_dir, 'D_MOJI_all_labeled.png'))
    for b in range(n // 256):
        sheet_labeled(px[b*256:(b+1)*256], b*256, cols=16).save(
            os.path.join(out_dir, f'D_MOJI_block{b:02d}_{b*256:04X}-{b*256+255:04X}.png'))
    print(f"{n} glyphs -> {out_dir}")

def cmd_inject(png_path, bin_path, out_path):
    orig = open(bin_path, 'rb').read()
    n = len(orig) // GL
    img = np.array(Image.open(png_path).convert('L'))
    rows = (n + COLS_1TO1 - 1) // COLS_1TO1
    assert img.shape == (rows * H, COLS_1TO1 * W), f"expected {(rows*H, COLS_1TO1*W)}, got {img.shape}"
    q = np.clip((img.astype(np.int32) + 42) // 85, 0, 3).astype(np.uint8)
    glyphs = np.zeros((n, H, W), dtype=np.uint8)
    for i in range(n):
        r, c = divmod(i, COLS_1TO1)
        glyphs[i] = q[r*H:(r+1)*H, c*W:(c+1)*W]
    out = encode(glyphs)
    assert len(out) == n * GL
    open(out_path, 'wb').write(out + orig[n*GL:])
    print(f"wrote {out_path} ({len(out)} bytes of glyph data)")

if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'extract':
        cmd_extract(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 5 and sys.argv[1] == 'inject':
        cmd_inject(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(__doc__); sys.exit(1)
