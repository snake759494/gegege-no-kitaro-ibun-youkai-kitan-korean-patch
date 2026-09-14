#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""glyph-index -> Unicode map for D_MOJI.BIN.
The kanji area is built from several JIS-ordered runs (the font was extended in batches),
so alignment uses a piecewise-monotonic DP: advancing within a run is free, starting a new
run costs LAMBDA. Similarity is an ensemble over several Japanese system fonts."""
import sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, 'tools')
from moji_font import decode
from glyph_anchors import ANCHORS

FONTS = ['C:/Windows/Fonts/msgothic.ttc', 'C:/Windows/Fonts/meiryo.ttc', 'C:/Windows/Fonts/YuGothM.ttc']
N, BLUR = 24, 1.0

def jis_list():
    out = []
    for ku in range(1, 95):
        for ten in range(1, 95):
            try: ch = bytes([0xA0+ku, 0xA0+ten]).decode('euc_jp')
            except Exception: continue
            if ch.strip() == '': continue
            out.append((ku, ch))
    return out

def normbox(a):
    ys = np.where(a.any(axis=1))[0]; xs = np.where(a.any(axis=0))[0]
    if len(ys) == 0 or len(xs) == 0: return None
    c = a[ys[0]:ys[-1]+1, xs[0]:xs[-1]+1]
    im = Image.fromarray((c*255/max(c.max(),1)).astype(np.uint8)).resize((N,N), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(BLUR))
    v = np.asarray(im, np.float32).ravel(); n = np.linalg.norm(v)
    return v/n if n else None

def render_cell(entries, fontpath, size=22):
    """Render into the game's 24x26 cell keeping the font's own relative sizes, so that
    small kana stay small (bbox normalisation would erase that difference)."""
    f = ImageFont.truetype(fontpath, size); V = []; keep = []
    for i, (ku, ch) in enumerate(entries):
        im = Image.new('L', (24, 26), 0)
        ImageDraw.Draw(im).text((1, 24 - size), ch, font=f, fill=255)
        a = np.asarray(im, np.float32) / 255.0
        a = np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), np.float32)/255.0
        v = a.ravel(); n = np.linalg.norm(v)
        if n: V.append(v/n); keep.append(i)
    return np.array(V, np.float32), keep

def game_cell(px, lo, hi):
    V = []; idx = []
    for g in range(lo, hi):
        a = (px[g] > 0).astype(np.float32)
        if not a.any(): continue
        a = np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)), np.float32)/255.0
        v = a.ravel(); n = np.linalg.norm(v)
        if n: V.append(v/n); idx.append(g)
    return np.array(V, np.float32), idx

def render_cands(entries, fontpath):
    f = ImageFont.truetype(fontpath, 48); V = []; keep = []
    for i, (ku, ch) in enumerate(entries):
        im = Image.new('L', (72, 72), 0)
        ImageDraw.Draw(im).text((10, 6), ch, font=f, fill=255)
        a = (np.asarray(im, np.float32)/255.0 > 0.35).astype(np.float32)
        v = normbox(a)
        if v is not None: V.append(v); keep.append(i)
    return np.array(V, np.float32), keep

def game_vecs(px, lo, hi):
    V = []; idx = []
    for g in range(lo, hi):
        v = normbox((px[g] > 0).astype(np.float32))
        if v is not None: V.append(v); idx.append(g)
    return np.array(V, np.float32), idx

def ensemble_sim(G, entries):
    S = None
    for fp in FONTS:
        V, keep = render_cands(entries, fp)
        s = np.full((G.shape[0], len(entries)), -1.0, np.float32)
        s[:, keep] = G @ V.T
        S = s if S is None else np.maximum(S, s)
    return S

def piecewise_dp(S, lam):
    n, m = S.shape; NEG = -1e9; ar = np.arange(m)
    dp = S[0].astype(np.float64).copy()
    bk = np.zeros((n, m), np.int32)
    for i in range(1, n):
        acc = np.maximum.accumulate(dp)
        argacc = np.maximum.accumulate(np.where(dp >= acc, ar, -1))
        pm = np.concatenate(([NEG], acc[:-1]))
        pa = np.concatenate(([-1], argacc[:-1])).astype(np.int32)
        gmax = float(dp.max()); gidx = int(np.argmax(dp))
        use_restart = (gmax - lam) > pm
        bk[i] = np.where(use_restart, gidx, pa)
        best_prev = np.where(use_restart, gmax - lam, pm)
        dp = S[i] + best_prev
    j = int(np.argmax(dp)); path = [0]*n
    for i in range(n-1, -1, -1):
        path[i] = j
        if i > 0: j = int(bk[i][j])
    return path

SMALL = {'つ':'っ','う':'ぅ','わ':'ゎ','や':'ゃ','ゆ':'ゅ','よ':'ょ','あ':'ぁ','い':'ぃ',
         'え':'ぇ','お':'ぉ','ツ':'ッ','ウ':'ゥ','ワ':'ヮ','ヤ':'ャ','ユ':'ュ','ヨ':'ョ',
         'ア':'ァ','イ':'ィ','エ':'ェ','オ':'ォ','カ':'ヵ','ケ':'ヶ'}
BIG = {v: k for k, v in SMALL.items()}

def ink_box(a):
    ys = np.where(a.any(axis=1))[0]; xs = np.where(a.any(axis=0))[0]
    return (ys[0], ys[-1], xs[0], xs[-1]) if len(ys) and len(xs) else None

def fix_bars(px, mapping, idx):
    """A long-vowel bar and an ellipsis both collapse to a flat blob under bbox
    normalisation; separate them by ink density."""
    for g in idx:
        a = px[g] > 0
        ys = np.where(a.any(axis=1))[0]; xs = np.where(a.any(axis=0))[0]
        if not len(ys) or not len(xs): continue
        y0, y1, x0, x1 = ys[0], ys[-1], xs[0], xs[-1]
        h = y1 - y0 + 1; w = x1 - x0 + 1
        if h <= 6 and w >= 2.2 * h:
            dens = float(a[y0:y1+1, x0:x1+1].mean())
            mapping[g] = 'ー' if dens > 0.75 else '…'

def main():
    jis = jis_list()
    kana_ent = [(k, c) for k, c in jis if k <= 8]
    kanji_ent = [(k, c) for k, c in jis if k >= 16]
    px = decode(open('extract/D_MOJI.BIN', 'rb').read())
    mapping = {}

    # kana/punct block: also several JIS-ordered runs (hiragana, katakana, symbols) with
    # omissions, so use the same piecewise-monotonic alignment; order alone fixes small kana.
    Gk, ik = game_vecs(px, 0x300, 0x400)
    Sk = ensemble_sim(Gk, kana_ent)
    bestk = None
    for lam in (0.05, 0.10, 0.20):
        pk = piecewise_dp(Sk, lam)
        mp = {g: kana_ent[pk[i]][1] for i, g in enumerate(ik)}
        ok = sum(1 for g, ch in ANCHORS.items() if g < 0x400 and mp.get(g) == ch)
        if bestk is None or ok > bestk[0]: bestk = (ok, lam, mp)
    nk = sum(1 for g in ANCHORS if g < 0x400)
    print(f"kana: lambda={bestk[1]} anchors {bestk[0]}/{nk}")
    mapping.update(bestk[2])
    fix_bars(px, mapping, ik)

    Gj, ij = game_vecs(px, 0x400, 0xC00)
    print(f"kanji glyphs {len(ij)}, candidates {len(kanji_ent)}; computing similarity...", flush=True)
    Sj = ensemble_sim(Gj, kanji_ent)
    best = None
    for lam in (0.02, 0.05, 0.10, 0.20, 0.40):
        path = piecewise_dp(Sj, lam)
        mp = dict(mapping)
        for i, g in enumerate(ij): mp[g] = kanji_ent[path[i]][1]
        ok = sum(1 for g, ch in ANCHORS.items() if mp.get(g) == ch)
        print(f"  lambda={lam}: anchors {ok}/{len(ANCHORS)}", flush=True)
        if best is None or ok > best[0]: best = (ok, lam, mp)
    ok, lam, mapping = best
    mapping.update(ANCHORS)          # verified pairs win over image matching
    print(f"best lambda={lam}, anchor accuracy {ok}/{len(ANCHORS)} = {ok/len(ANCHORS):.0%}")
    bad = [(hex(g), ch, mapping.get(g)) for g, ch in ANCHORS.items() if mapping.get(g) != ch]
    if bad: print("remaining mismatches:", bad)
    json.dump({hex(k): v for k, v in mapping.items()}, open('glyph_map.json','w',encoding='utf-8'),
              ensure_ascii=False, indent=0)
    print(f"wrote glyph_map.json ({len(mapping)})")

if __name__ == '__main__':
    main()
