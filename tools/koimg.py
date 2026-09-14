#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render Korean text into D_SYS.BIN sprite slots.

The sprites are palette images whose index 0 is a chroma key (transparent).
We rasterise the Korean caption at 4x into two masks (with / without the
outline stroke), blend the fill colour over the outline colour, then map every
opaque pixel to the nearest entry of the pack's own palette.  That reproduces
the original outline / highlight look without needing the game's CLUT
semantics.

Text may contain '\\n' for multiple lines; `vertical=True` stacks single
characters top-to-bottom (used by the vertical wooden place-name signs).
"""
import os
import sys
import collections

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sysimg import Pack, find_packs  # noqa: E402,F401

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = {
    'B': os.path.join(ROOT, 'SeoulHangangB.ttf'),
    'EB': os.path.join(ROOT, 'SeoulHangangEB.ttf'),
    'M': os.path.join(ROOT, 'SeoulHangangM.ttf'),
    'L': os.path.join(ROOT, 'SeoulHangangL.ttf'),
    'NB': os.path.join(ROOT, 'NanumSquareNeo-cBd.ttf'),
    'NEB': os.path.join(ROOT, 'NanumSquareNeo-dEb.ttf'),
    'NHV': os.path.join(ROOT, 'NanumSquareNeo-eHv.ttf'),
}
SS = 4  # supersample factor
_FCACHE = {}


def font(key, pt):
    f = _FCACHE.get((key, pt))
    if f is None:
        f = _FCACHE[(key, pt)] = ImageFont.truetype(FONTS[key], pt)
    return f


# --------------------------------------------------------------------------
# analysing the original sprite
# --------------------------------------------------------------------------
def analyse(pack, i, key=0):
    """Guess (fill_rgb, outline_rgb) from an original text sprite."""
    pal = pack.rgb_palette()
    cnt = collections.Counter(c for c in pack.indices(i) if c != key)
    if not cnt:
        return (255, 255, 255), (0, 0, 0)
    top = sorted(((c, n) for c, n in cnt.items()), key=lambda t: -t[1])[:12]
    top = [(c, n, pal[c], sum(pal[c])) for c, n in top]
    return max(top, key=lambda t: t[3])[2], min(top, key=lambda t: t[3])[2]


# --------------------------------------------------------------------------
# text rasterising
# --------------------------------------------------------------------------
def _compose(text, f, stroke, tracking, line_gap, vertical, align):
    """Draw text at font size `f` on a generous canvas; return cropped masks."""
    if vertical:
        lines = list(text)
    else:
        lines = text.split('\n')
    asc, desc = f.getmetrics()
    lh = asc + desc + line_gap
    W = 64 + max(4, len(max(lines, key=len))) * (f.size + tracking) * 3
    H = 64 + len(lines) * lh * 2
    all_m = Image.new('L', (W, H), 0)
    fil_m = Image.new('L', (W, H), 0)
    da, df = ImageDraw.Draw(all_m), ImageDraw.Draw(fil_m)
    y = 32
    widths = []
    for ln in lines:
        if tracking:
            w = 0
            for ch in ln:
                b = da.textbbox((0, 0), ch, font=f, stroke_width=stroke)
                w += (b[2] - b[0]) + tracking
            w = max(0, w - tracking)
        else:
            b = da.textbbox((0, 0), ln, font=f, stroke_width=stroke)
            w = b[2] - b[0]
        widths.append(w)
    box = max(widths) if widths else 0
    for k, ln in enumerate(lines):
        if align == 'c':
            x = 32 + (box - widths[k]) // 2
        elif align == 'r':
            x = 32 + box - widths[k]
        else:
            x = 32
        if tracking:
            cx = x
            for ch in ln:
                da.text((cx, y), ch, font=f, fill=255,
                        stroke_width=stroke, stroke_fill=255)
                df.text((cx, y), ch, font=f, fill=255)
                b = da.textbbox((0, 0), ch, font=f, stroke_width=stroke)
                cx += (b[2] - b[0]) + tracking
        else:
            da.text((x, y), ln, font=f, fill=255,
                    stroke_width=stroke, stroke_fill=255)
            df.text((x, y), ln, font=f, fill=255)
        y += lh
    bb = all_m.getbbox()
    if bb is None:
        return None, None
    return all_m.crop(bb), fil_m.crop(bb)


def render_rgba(w, h, text, font_key='B', stroke=2, pad=1, tracking=0,
                line_gap=0, vertical=False, align='c', dx=0, dy=0, pt=None,
                fill=(255, 255, 255), outline=(0, 0, 0), maxfill=1.0,
                max_pt=None):
    """Rasterise `text` into a w*h RGBA image (alpha = ink coverage)."""
    W, H = w * SS, h * SS
    st = stroke * SS
    bw = int((w - pad * 2) * SS * maxfill)
    bh = int((h - pad * 2) * SS * maxfill)
    if pt:
        am, fm = _compose(text, font(font_key, pt * SS), st, tracking * SS,
                          line_gap * SS, vertical, align)
    else:
        lo, hi, best = 8, (max_pt * SS if max_pt else max(16, H)), None
        while lo <= hi:
            mid = (lo + hi) // 2
            am, fm = _compose(text, font(font_key, mid), st, tracking * SS,
                              line_gap * SS, vertical, align)
            if am is not None and am.width <= bw and am.height <= bh:
                best, lo = (am, fm), mid + 1
            else:
                hi = mid - 1
        if best is None:
            best = _compose(text, font(font_key, 8), st, tracking * SS,
                            line_gap * SS, vertical, align)
        am, fm = best
    big_a = Image.new('L', (W, H), 0)
    big_f = Image.new('L', (W, H), 0)
    ox = (W - am.width) // 2 + dx * SS
    oy = (H - am.height) // 2 + dy * SS
    big_a.paste(am, (ox, oy))
    big_f.paste(fm, (ox, oy))
    big_a = big_a.resize((w, h), Image.LANCZOS)
    big_f = big_f.resize((w, h), Image.LANCZOS)
    im = Image.new('RGBA', (w, h))
    ap, fp, op = big_a.load(), big_f.load(), im.load()
    for yy in range(h):
        for xx in range(w):
            a = ap[xx, yy]
            if not a:
                continue
            t = fp[xx, yy] / 255.0
            op[xx, yy] = tuple(
                int(round(outline[k] + (fill[k] - outline[k]) * t))
                for k in range(3)) + (a,)
    return im


# --------------------------------------------------------------------------
# quantising onto the pack palette
# --------------------------------------------------------------------------
def quantize(pack, im, alpha_thr=110, key=0, halo=True):
    """RGBA image -> palette indices for `pack` (index `key` = transparent)."""
    pal = pack.rgb_palette()
    cand = [c for c in range(len(pal)) if c != key]
    out = bytearray(im.width * im.height)
    px = im.load()
    cache = {}
    for y in range(im.height):
        base = y * im.width
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < alpha_thr:
                continue
            if halo and a < 255:
                # fade the outer edge toward black rather than toward the
                # chroma key, so no coloured fringe appears
                f = a / 255.0
                r, g, b = int(r * f), int(g * f), int(b * f)
            k = (r, g, b)
            c = cache.get(k)
            if c is None:
                best, bd = key, 1 << 30
                for ci in cand:
                    pr, pg, pb = pal[ci]
                    dd = (pr - r) ** 2 + (pg - g) ** 2 + (pb - b) ** 2
                    if dd < bd:
                        bd, best = dd, ci
                c = cache[k] = best
            out[base + x] = c
    return out


def paint(pack, i, text, **kw):
    """Replace sprite `i` with `text` on a transparent background."""
    s = pack.sprites[i]
    key = kw.pop('key', 0)
    fill = kw.pop('fill', None)
    outline = kw.pop('outline', None)
    if fill is None or outline is None:
        af, ao = analyse(pack, i, key)
        fill = fill or af
        outline = outline or ao
    alpha_thr = kw.pop('alpha_thr', 110)
    im = render_rgba(s.w, s.h, text, fill=fill, outline=outline, **kw)
    pack.put_indices(i, quantize(pack, im, alpha_thr=alpha_thr, key=key))
    return im


# --------------------------------------------------------------------------
# background plates (keep the original artwork, swap only the caption)
# --------------------------------------------------------------------------
def make_plate(pack, sprite_ids, bright_thr=330, key=0):
    """Per pixel take the darkest of several same-size sprites, then inpaint
    whatever is still bright (leftover strokes) from its darkest neighbour."""
    w, h = pack.sprites[sprite_ids[0]].w, pack.sprites[sprite_ids[0]].h
    pal = pack.rgb_palette()
    idxs = [pack.indices(i) for i in sprite_ids]

    def lum(c):
        return sum(pal[c])

    plate = bytearray(w * h)
    for y in range(h):
        for x in range(w):
            plate[y * w + x] = min((lum(a[y * w + x]), a[y * w + x])
                                   for a in idxs)[1]
    bright = {(x, y) for y in range(h) for x in range(w)
              if plate[y * w + x] != key and lum(plate[y * w + x]) > bright_thr}
    for (x, y) in sorted(bright):
        for r in range(1, 24):
            cands = []
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < w and 0 <= ny < h and (nx, ny) not in bright
                            and plate[ny * w + nx] != key):
                        cands.append(plate[ny * w + nx])
            if cands:
                plate[y * w + x] = min(cands, key=lum)
                break
    return plate


def clear_inside(pack, i, inset, key=0):
    """Plate = the sprite with its interior (inset from each edge) cleared."""
    s = pack.sprites[i]
    plate = bytearray(pack.indices(i))
    l, t, r, b = inset if isinstance(inset, (tuple, list)) else (inset,) * 4
    for y in range(t, s.h - b):
        for x in range(l, s.w - r):
            plate[y * s.w + x] = key
    return plate


def paint_over(pack, i, text, plate, alpha_thr=110, key=0, **kw):
    """Draw `text` on top of `plate` (index bytes) and store into sprite `i`."""
    s = pack.sprites[i]
    pal = pack.rgb_palette()
    fill = kw.pop('fill', None) or (255, 255, 255)
    outline = kw.pop('outline', None) or (0, 0, 0)
    txt = render_rgba(s.w, s.h, text, fill=fill, outline=outline, **kw)
    comp = Image.new('RGBA', (s.w, s.h))
    cp, tp = comp.load(), txt.load()
    for y in range(s.h):
        for x in range(s.w):
            pi = plate[y * s.w + x]
            tr, tg, tb, ta = tp[x, y]
            if ta >= alpha_thr:
                if pi == key:
                    cp[x, y] = (tr, tg, tb, ta)
                else:
                    f = ta / 255.0
                    pr, pg, pb = pal[pi]
                    cp[x, y] = (int(pr + (tr - pr) * f),
                                int(pg + (tg - pg) * f),
                                int(pb + (tb - pb) * f), 255)
            elif pi != key:
                cp[x, y] = pal[pi] + (255,)
    pack.put_indices(i, quantize(pack, comp, alpha_thr=alpha_thr, key=key))
    return comp


def fill_inside(pack, i, inset, key=0, margin=0):
    """Plate that keeps the sprite's border but flattens the interior to each
    row's dominant colour - erases a caption from a flat/gradient panel.

    With `margin` > 0 the row colour is sampled only from that many columns
    just outside the cleared interior, which is what small icon tiles need
    (their glyph covers most of the interior, so sampling it would keep the
    glyph instead of erasing it)."""
    s = pack.sprites[i]
    plate = bytearray(pack.indices(i))
    l, t, r, b = inset if isinstance(inset, (tuple, list)) else (inset,) * 4
    for y in range(t, s.h - b):
        o = y * s.w
        if margin:
            samp = (plate[o + max(0, l - margin):o + l]
                    + plate[o + s.w - r:o + min(s.w, s.w - r + margin)])
        else:
            samp = plate[o + l:o + s.w - r]
        row = collections.Counter(c for c in samp if c != key)
        if not row:
            continue
        bg = row.most_common(1)[0][0]
        for x in range(l, s.w - r):
            plate[o + x] = bg
    return plate


def flat_plate(pack, i):
    """Plate of a single colour: the sprite's most common index."""
    s = pack.sprites[i]
    bg = collections.Counter(pack.indices(i)).most_common(1)[0][0]
    return bytearray([bg]) * (s.w * s.h)


def ink_colour(pack, i, key=0):
    """(text_rgb, bg_rgb) for a two-tone panel: bg = most common index,
    ink = the most common index whose colour is farthest from bg."""
    pal = pack.rgb_palette()
    cnt = collections.Counter(pack.indices(i))
    bg = cnt.most_common(1)[0][0]
    if bg == key:                      # transparent sprite: no real plate
        return analyse(pack, i, key)[0], pal[key]
    br = pal[bg]
    best, bd = None, -1
    for c, n in cnt.most_common(24):
        if c == bg:
            continue
        d = sum((pal[c][k] - br[k]) ** 2 for k in range(3)) * (n ** 0.25)
        if d > bd:
            bd, best = d, c
    return (pal[best] if best is not None else (0, 0, 0)), br


# --------------------------------------------------------------------------
# painting a caption into one rectangle of a large background image
# --------------------------------------------------------------------------
def region_plate(pack, i, box, margin=6, mode='lerp', src=None):
    """Copy of the sprite with `box` erased, refilled from the pixels just
    left and right of it (per row).  'lerp' interpolates between the two
    sides, which follows a horizontal gradient; 'row' floods the dominant
    margin colour."""
    s = pack.sprites[i]
    pal = pack.rgb_palette()
    plate = bytearray(pack.indices(i))
    x0, y0, x1, y1 = box
    if mode == 'tile':
        # rebuild a periodic background by tiling a clean strip of the same
        # rows; `src` = (source x, source width), width a multiple of the
        # pattern period and (x0 - source x) likewise, so the phase matches
        sx, sw = src
        for y in range(y0, y1):
            o = y * s.w
            for x in range(x0, x1):
                plate[o + x] = plate[o + sx + (x - x0) % sw]
        return plate
    if mode == 'box':
        cnt = collections.Counter()
        for y in range(y0, y1):
            cnt.update(plate[y * s.w + x0:y * s.w + x1])
        bg = cnt.most_common(1)[0][0]
        for y in range(y0, y1):
            o = y * s.w
            for x in range(x0, x1):
                plate[o + x] = bg
        return plate
    for y in range(y0, y1):
        o = y * s.w
        left = plate[o + max(0, x0 - margin):o + x0]
        right = plate[o + x1:o + min(s.w, x1 + margin)]
        if mode == 'row':
            cnt = collections.Counter(bytes(left) + bytes(right))
            if not cnt:
                continue
            bg = cnt.most_common(1)[0][0]
            for x in range(x0, x1):
                plate[o + x] = bg
            continue
        lc = _mean_rgb(pal, left) or _mean_rgb(pal, right)
        rc = _mean_rgb(pal, right) or lc
        if lc is None:
            continue
        w = max(1, x1 - x0 - 1)
        for x in range(x0, x1):
            t = (x - x0) / w
            col = tuple(int(lc[k] + (rc[k] - lc[k]) * t) for k in range(3))
            plate[o + x] = _nearest(pal, col)
    return plate


def _mean_rgb(pal, idxs):
    if not idxs:
        return None
    n = len(idxs)
    r = sum(pal[c][0] for c in idxs) / n
    g = sum(pal[c][1] for c in idxs) / n
    b = sum(pal[c][2] for c in idxs) / n
    return (r, g, b)


_NEAR = {}


def _nearest(pal, col):
    key = (id(pal), col)
    c = _NEAR.get(key)
    if c is None:
        best, bd = 0, 1 << 30
        for ci, (pr, pg, pb) in enumerate(pal):
            d = (pr - col[0]) ** 2 + (pg - col[1]) ** 2 + (pb - col[2]) ** 2
            if d < bd:
                bd, best = d, ci
        c = _NEAR[key] = best
    return c


def paint_region(pack, i, box, text, margin=6, mode='lerp', plate=None,
                 alpha_thr=110, src=None, **kw):
    """Erase `box` from sprite `i` and draw `text` in its place."""
    s = pack.sprites[i]
    pal = pack.rgb_palette()
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    if plate is None:
        plate = region_plate(pack, i, box, margin, mode, src)
    txt = render_rgba(bw, bh, text, **kw)
    sub = Image.new('RGBA', (bw, bh))
    sp, tp = sub.load(), txt.load()
    for y in range(bh):
        o = (y0 + y) * s.w + x0
        for x in range(bw):
            tr, tg, tb, ta = tp[x, y]
            pr, pg, pb = pal[plate[o + x]]
            if ta:
                f = ta / 255.0
                sp[x, y] = (int(pr + (tr - pr) * f), int(pg + (tg - pg) * f),
                            int(pb + (tb - pb) * f), 255)
            else:
                sp[x, y] = (pr, pg, pb, 255)
    idx = quantize(pack, sub, alpha_thr=0, key=-1, halo=False)
    for y in range(bh):
        o = (y0 + y) * s.w + x0
        plate[o:o + bw] = idx[y * bw:(y + 1) * bw]
    pack.put_indices(i, plate)
    return plate


def inpaint_ink(pack, i, box, pred, dilate=2, key=None):
    """Plate that removes only the pixels matching `pred` inside `box`,
    filling each from its nearest surviving neighbour.  Keeps a noisy or
    textured background intact instead of flattening a whole rectangle."""
    s = pack.sprites[i]
    pal = pack.rgb_palette()
    plate = bytearray(pack.indices(i))
    x0, y0, x1, y1 = box
    mask = set()
    for y in range(y0, y1):
        o = y * s.w
        for x in range(x0, x1):
            if pred(pal[plate[o + x]]):
                mask.add((x, y))
    for _ in range(dilate):
        grow = set()
        for (x, y) in mask:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                           (1, 1), (1, -1), (-1, 1), (-1, -1)):
                n = (x + dx, y + dy)
                if x0 <= n[0] < x1 and y0 <= n[1] < y1 and n not in mask:
                    grow.add(n)
        mask |= grow
    for (x, y) in sorted(mask):
        for r in range(1, 40):
            got = None
            for dy in (-r, r):
                ny = y + dy
                if y0 - 4 <= ny < y1 + 4 and 0 <= ny < s.h and (x, ny) not in mask:
                    got = plate[ny * s.w + x]
                    break
            if got is None:
                for dx in (-r, r):
                    nx = x + dx
                    if 0 <= nx < s.w and (nx, y) not in mask:
                        got = plate[y * s.w + nx]
                        break
            if got is not None:
                plate[y * s.w + x] = got
                break
    return plate
