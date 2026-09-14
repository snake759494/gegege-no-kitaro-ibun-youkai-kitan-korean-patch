#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static QA for the Korean text patch.

    python tools/qa_text.py [--full]

Checks, in order:
  1 round-trip   - every string in script_ko.tsv is byte-identical to what
                   D_MESS_ko.BIN actually contains
  2 coverage     - JP messages with no Korean row
  3 leftovers    - kana / kanji still sitting in the Korean column
  4 layout       - messages that overflow their region's box (lines / boxes)
  5 control code - JP messages carrying <xx> codes the Korean dropped
  6 glossary     - proper nouns spelled more than one way
  7 budget       - bytes used per sub-file
"""
import csv
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ko_inject                                   # noqa: E402
from mess_parse import parse_table                 # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
if hasattr(sys.stdout, 'reconfigure'):          # Windows: keep the report UTF-8 when redirected
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

KANA = re.compile(r'[぀-ヿ一-鿿ｦ-ﾟ]')
CTL = re.compile(r'<([0-9a-f]{2})>')

# proper nouns that must be spelled the same everywhere
GLOSSARY = [
    ['키타로', '기타로'],
    ['눈알아버지', '눈알 아버지', '메다마오야지'],
    ['고양이소녀', '고양이 소녀', '네코무스메'],
    ['쥐인간', '생쥐인간', '생쥐 인간', '네즈미오토코'],
    ['모래뿌리기할멈', '스나카케바바'],
    ['아기울음영감', '코나키지지'],
    ['이탄모멘', '잇탄모멘'],
    ['누리카베'],
    ['누라리횬', '누라리횩'],
    ['백베어드', '벡베어드', '바크베어드'],
    ['드라큘라'],
    ['론론'],
    ['고곤', '고르곤'],
    ['카타키라우와', '가타키라우와'],
    ['라 세느', '라-세느', '라세느'],
    ['기가', '기이가'],
    ['우귀', '우시오니'],
    ['요괴', '요과'],
]


def load():
    jp = {}
    with open('script_jp.tsv', encoding='utf-8') as f:
        for row in csv.reader(f, delimiter='\t'):
            if not row or row[0] == 'base':
                continue
            jp[(int(row[0], 16), int(row[1]))] = row[2]
    ko = {}
    with open('script_ko.tsv', encoding='utf-8') as f:
        for row in csv.reader(f, delimiter='\t'):
            if not row or row[0] == 'base' or len(row) < 3:
                continue
            ko[(int(row[0], 16), int(row[1]))] = row[2]
    return jp, ko


def sub_bases(d):
    out = []
    for base in range(0, len(d), 0x800):
        t = parse_table(d, base)
        if len(t) >= 3 and t[0] == base + 2 * len(t):
            out.append(base)
    return out


def msg_bytes(d, bases, base, k):
    i = bases.index(base)
    nxt = bases[i + 1] if i + 1 < len(bases) else len(d)
    end = d.rfind(b'\x1f', base, nxt) + 1
    tbl = parse_table(d, base)
    s = tbl[k]
    e = tbl[k + 1] if k + 1 < len(tbl) else end
    return d[s:e]


def main():
    full = '--full' in sys.argv
    jp, ko = load()
    src = open('extract/D_MESS.BIN', 'rb').read()
    out = open('D_MESS_ko.BIN', 'rb').read()
    bases = sub_bases(src)
    fails = 0

    # 1 ------------------------------------------------------------------
    bad = []
    for (base, k), txt in sorted(ko.items()):
        lm, ml = ko_inject.layout_for(base, k)
        enc, miss, boxes = ko_inject.encode(txt, lm, ml)
        got = msg_bytes(out, bases, base, k)
        if got != enc:
            bad.append((base, k, len(enc), len(got)))
    print('1 round-trip     : %d / %d strings match the shipped BIN%s'
          % (len(ko) - len(bad), len(ko), '' if not bad else '   << FAIL'))
    for b in bad[:10]:
        print('    %#07x/%d  encoded %d B, in file %d B' % b)
    fails += len(bad)

    # 2 ------------------------------------------------------------------
    missing = [k for k in jp if k not in ko]
    print('2 coverage       : %d JP messages, %d untranslated'
          % (len(jp), len(missing)))
    for base, k in sorted(missing):
        t = jp[(base, k)]
        print('    %#07x/%-5d %s' % (base, k, t[:60]))

    # 3 ------------------------------------------------------------------
    left = [(b, k, t) for (b, k), t in sorted(ko.items()) if KANA.search(t)]
    print('3 leftovers      : %d Korean rows still containing kana/kanji%s'
          % (len(left), '' if not left else '   << CHECK'))
    for b, k, t in left[:40]:
        print('    %#07x/%-5d %s' % (b, k, t[:70]))
    fails += len(left)

    # 4 ------------------------------------------------------------------
    over_lines, grew = [], []
    per_region = defaultdict(lambda: [0, 0])
    for (base, k), txt in sorted(ko.items()):
        lm, ml = ko_inject.layout_for(base, k)
        _, _, boxes = ko_inject.encode(txt, lm, ml)
        per_region[(base, lm, ml)][0] = max(per_region[(base, lm, ml)][0],
                                            max(len(b) for b in boxes))
        per_region[(base, lm, ml)][1] = max(per_region[(base, lm, ml)][1],
                                            len(boxes))
        if any(len(b) > ml for b in boxes):
            over_lines.append((base, k))
        jt = jp.get((base, k), '')
        if len(boxes) > jt.count('@') + 1:
            grew.append((base, k, jt.count('@') + 1, len(boxes)))
    print('4 layout         : %d over the line limit, %d messages need more '
          'boxes than the original' % (len(over_lines), len(grew)))
    fixed = [g for g in grew if g[0] in (0x06000, 0x07000, 0x09000, 0x01000,
                                         0x00000)]
    if fixed:
        print('    on fixed-size panels (these are the ones that matter):')
        for base, k, a, b in fixed[:30]:
            print('    %#07x/%-5d %d -> %d boxes | %s' %
                  (base, k, a, b, ko[(base, k)][:50]))
    fails += len(over_lines) + len(fixed)
    if full:
        for (base, lm, ml), (mx, mb) in sorted(per_region.items()):
            print('    %#07x  limit %2d/%2d  worst %2d lines, %d boxes'
                  % (base, lm, ml, mx, mb))

    # 5 ------------------------------------------------------------------
    dropped = defaultdict(list)
    for (base, k), t in jp.items():
        codes = set(CTL.findall(t))
        if codes and (base, k) in ko:
            dropped[frozenset(codes)].append((base, k))
    print('5 control codes  : %d JP messages carry raw <xx> codes that the '
          'Korean cannot reproduce' % sum(len(v) for v in dropped.values()))
    for codes, items in sorted(dropped.items(), key=lambda kv: -len(kv[1])):
        b0, k0 = items[0]
        print('    %-18s x%-5d e.g. %#07x/%d  %s'
              % (','.join(sorted(codes)), len(items), b0, k0,
                 jp[(b0, k0)][:50]))

    # 6 ------------------------------------------------------------------
    print('6 glossary       :')
    body = '\n'.join(ko.values())
    for group in GLOSSARY:
        hits = [(w, body.count(w)) for w in group]
        used = [h for h in hits if h[1]]
        if len(used) > 1:
            # a longer spelling contains the shorter one, discount that
            base_w, base_n = used[0]
            others = [(w, n) for w, n in used[1:] if n]
            print('    %-14s %s   << mixed'
                  % (base_w, '  '.join('%s=%d' % h for h in used)))
        elif used:
            print('    %-14s %d' % (used[0][0], used[0][1]))

    # 7 ------------------------------------------------------------------
    print('7 budget         :')
    tr = defaultdict(dict)
    for (base, k), t in ko.items():
        tr[base][k] = t
    worst = []
    for base in sorted(tr):
        i = bases.index(base)
        nxt = bases[i + 1] if i + 1 < len(bases) else len(src)
        region = nxt - base
        tbl = parse_table(src, base)
        end = src.rfind(b'\x1f', base, nxt) + 1
        pos = len(tbl) * 2
        for k in range(len(tbl)):
            s = tbl[k]
            e = tbl[k + 1] if k + 1 < len(tbl) else end
            if k in tr[base]:
                lm, ml = ko_inject.layout_for(base, k)
                pos += len(ko_inject.encode(tr[base][k], lm, ml)[0])
            else:
                pos += max(0, e - s)
        worst.append((pos / region, base, pos, region))
    worst.sort(reverse=True)
    for r, base, pos, region in worst[:6]:
        print('    %#07x  %6d / %6d bytes  (%.0f%%)' % (base, pos, region,
                                                        r * 100))
    print()
    print('RESULT: %s' % ('no blocking issues' if not fails
                          else '%d items need attention' % fails))


if __name__ == '__main__':
    main()
