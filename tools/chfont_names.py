#!/usr/bin/env python3
"""D_CHFONT.BIN -> PNG. Pre-rendered character name plates.

Layout (verified): file = 64 sub-blocks of 0x2000 bytes. Each sub-block:
  0x00..0x3F : 4 entries x 16 bytes  (u32 flags, u32 data_off, u32 vram_off, u32 w|h<<16)
               data_off = 0x68 + k*0x600, w=0x60 (96), h=0x20 (32)
  0x40..0x4F : u32 0, u32 0x10, then 4 x u16 RGBA5551 palette (0x0000, 0x7FFF, gray, dark)
  0x68..     : 4 images, 96x32, 4bpp (low nibble = left pixel), 0x600 bytes each
Only palette indices 0..3 are used. Sub-blocks whose images are all zero are empty slots.
"""
import sys, os, struct
import numpy as np
from PIL import Image

SUB = 0x2000; W, H = 96, 32; IMG = W * H // 2

def images(data):
    for s in range(len(data) // SUB):
        base = s * SUB
        pal = struct.unpack_from('<4H', data, base + 0x48)
        for k in range(4):
            off = base + 0x68 + k * IMG
            a = np.frombuffer(data[off:off + IMG], dtype=np.uint8)
            px = np.stack([a & 0xF, a >> 4], axis=1).reshape(H, W)
            yield s, k, pal, px

def rgba5551(v, opaque=True):
    # PS2 CT16: bit15 is alpha but the game expands it via TEXA; treat every non-zero palette slot as opaque.
    r = (v & 0x1F) << 3; g = ((v >> 5) & 0x1F) << 3; b = ((v >> 10) & 0x1F) << 3
    return (r, g, b, 255 if opaque else 0)

def main(bin_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    data = open(bin_path, 'rb').read()
    items = list(images(data))
    nonempty = [(s, k, pal, px) for s, k, pal, px in items if px.any()]
    print(f"{len(items)} slots, {len(nonempty)} non-empty")
    # contact sheet: 8 columns
    cols = 8; rows = (len(items) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * (W + 4), rows * (H + 4)), (0, 0, 0, 255))
    for i, (s, k, pal, px) in enumerate(items):
        lut = np.array([rgba5551(pal[j]) if j < 4 else (255, 0, 255, 255) for j in range(16)], dtype=np.uint8)
        lut[0] = (0, 0, 0, 0)  # index 0 = transparent
        rgba = lut[px]
        im = Image.fromarray(rgba, 'RGBA')
        r, c = divmod(i, cols)
        sheet.paste(im, (c * (W + 4) + 2, r * (H + 4) + 2), im)
        if px.any():
            im.save(os.path.join(out_dir, f'name_{s:02d}_{k}.png'))
    # also a grayscale index-only sheet (raw palette index * 85) for editing
    g = np.zeros((rows * (H + 4), cols * (W + 4)), dtype=np.uint8)
    for i, (s, k, pal, px) in enumerate(items):
        r, c = divmod(i, cols)
        g[r*(H+4)+2:r*(H+4)+2+H, c*(W+4)+2:c*(W+4)+2+W] = np.clip(px, 0, 3) * 85
    Image.fromarray(g).save(os.path.join(out_dir, 'D_CHFONT_all_index.png'))
    sheet.save(os.path.join(out_dir, 'D_CHFONT_all_color.png'))
    print("saved", out_dir)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
