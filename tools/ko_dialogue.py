#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Translate early-game dialogue (sub-file 0x16000, msgs 0..37) to Korean with proper layout:
- word-wrap each box to <= LINE_MAX half-units per line (fullwidth glyph = 2, ASCII = 1)
- at most MAX_LINES (3) lines per dialogue box; overflow auto-advances with 0x1E (page break)
- 0x1D = line break, 0x1E = box/page break, 0x1F = message end
Rebuilds the whole 0x2000-byte sub-file, recomputing the offset table; other messages untouched."""
import sys, struct
sys.path.insert(0, 'tools')
from hangul_font import ksx1001_hangul
from mess_parse import parse_table

BASE = 0x16000; REGION = 0x2000
LINE_MAX = 34            # half-units per line (original max was 36; margin against soft-wrap)
MAX_LINES = 3

KSX = ksx1001_hangul(); KIDX = {c: i for i, c in enumerate(KSX)}
PUNC1 = {' ': 0x20, '!': 0x21, '"': 0x22, '(': 0x28, ')': 0x29, ',': 0x2c,
         '.': 0x2e, '?': 0x3f, '~': 0x7e, ':': 0x3a}
for ch in '0123456789': PUNC1[ch] = ord(ch)
OPEN, CLOSE, ELLIPSIS = 0x89, 0x8a, 0x1ac

def char_width(ch):
    if ch in ' ' or (ch in PUNC1 and ch not in '') or ('A' <= ch <= 'Z') or ('a' <= ch <= 'z'):
        return 1 if (ch == ' ' or ch in PUNC1 or ('A' <= ch <= 'Z') or ('a' <= ch <= 'z')) else 2
    return 2                       # Hangul, 「 」 …  = fullwidth

def word_width(w):
    return sum(char_width(c) for c in w)

def layout(script):
    """script: Korean text; '@' = forced box break; single spaces separate words.
    Returns list of boxes, each a list of line-strings."""
    boxes = []
    for seg in script.split('@'):
        words = [w for w in seg.split(' ')]
        lines = []; cur = ''; cur_w = 0
        for word in words:
            if word == '':
                continue
            ww = word_width(word)
            if cur == '':
                cur, cur_w = word, ww
            elif cur_w + 1 + ww <= LINE_MAX:
                cur += ' ' + word; cur_w += 1 + ww
            else:
                lines.append(cur); cur, cur_w = word, ww
            while cur_w > LINE_MAX:      # a single word longer than a line: hard split
                # find split point by width
                acc = 0; idx = 0
                for i, c in enumerate(cur):
                    w = char_width(c)
                    if acc + w > LINE_MAX: break
                    acc += w; idx = i + 1
                lines.append(cur[:idx]); cur = cur[idx:]; cur_w = word_width(cur)
        if cur: lines.append(cur)
        for i in range(0, len(lines), MAX_LINES):
            boxes.append(lines[i:i + MAX_LINES])
        if not lines:
            boxes.append([''])
    return boxes

def enc_char(ch, out, missing):
    if ch == '「': out.append(OPEN)
    elif ch == '」': out.append(CLOSE)
    elif ch == '…': out += bytes([ELLIPSIS >> 8, ELLIPSIS & 0xFF])
    elif ch in PUNC1: out.append(PUNC1[ch])
    elif 'A' <= ch <= 'Z' or 'a' <= ch <= 'z': out.append(ord(ch))
    else:
        try:
            c = 0x200 + KIDX[ch]; out += bytes([c >> 8, c & 0xFF])
        except KeyError:
            missing.append(ch)

def encode(script):
    boxes = layout(script); out = bytearray(); missing = []
    for bi, box in enumerate(boxes):
        if bi: out.append(0x1E)                  # box/page break
        for li, line in enumerate(box):
            if li: out.append(0x1D)              # line break
            for ch in line: enc_char(ch, out, missing)
    out.append(0x1F)
    return bytes(out), missing, boxes

TL = {
 0: "21세기가 되어… 어느새 벌써 몇 해가 지났다.",
 1: "달력으로는 시대가 바뀌었지만… 세상은 아무것도 변하지 않았다.",
 2: "확실히 고층 빌딩의 수는 엄청난 기세로 계속 늘고 있다.",
 3: "과학도 발전했다.",
 4: "하지만… 인간은 이 시대가 되어도 조금도 나아지지 않았다.",
 5: "나라와 나라의 다툼은 여전하고, 젊은이의 마음도 거칠어져만 간다.",
 6: "오히려… 옛날보다 나빠진 게 아닐까…?",
 7: "인간의 세계가 균형을 잃고 있는 거라면…",
 8: "오랜 세월 인간과 함께 살아온 \"그들\"은 얌전히 있을까?",
 9: "이런… 정전인가?",
 10: "……………………",
 11: "인간들은 그들의 보금자리를 빼앗고, 제 세상인 양 살아왔다.",
 12: "이제는 그들의 존재를… 믿지 않는 사람도 많을 것이다.",
 13: "하지만, 그들은 있다.",
 14: "오히려 지금이기에 그들은 인간 세계를 노릴지도 모른다…",
 15: "이 위험을 알려 두어야만 한다.",
 16: "그들에게… \"요괴\"를 상대할 수 있는, 가장 믿음직한 인물에게…!",
 17: "안 되겠군… 편지지도 봉투도 다 떨어졌던가…",
 18: "…아아! 맞다. 지금은 그런 게 없어도 연락되는 시대였지.",
 19: "  전략",
 20: "  전략",
 21: "  전략  게게게의 키타로 님",
 22: "  전략  게게게의 키타로 님",
 23: "「후우~, 살 것 같구나!」",
 24: "「아버지, 물 온도는 어떠세요?」",
 25: "「음, 지금 계절엔 이 정도가 딱 좋아, 나무랄 데 없구나!@완전히 찻잔 목욕의 \"요령\"을 터득했구나… 키타로!」",
 26: "「요즘 심심했으니까요.@덕분에 아버지 목욕 준비가 완전히 능숙해져 버렸어요」",
 27: "「음, 옛날과 비교하면 확실히 요괴 관련 사건 수는 줄었지.@인간과 자연의 거리가 멀어져 요괴와 마주칠 기회가 줄었기 때문이겠지」",
 28: "「그렇네요… 쓸쓸한 얘기지만. 그래도 사건이 적은 건 좋은 일이죠」",
 29: "「음… 그렇구나」",
 30: "(살벌한 뉴스는 여전히 많지만… 요괴가 얽힌 사건은 없는 것 같군…)",
 31: "「키타로. 전부터 물어보려 했다만…@그 딸깍딸깍하는 물건은 무엇이냐? 새로운 요괴 TV냐?」",
 32: "「네? 아아, 이거요. 이건 요괴 컴퓨터예요」",
 33: "「호오, 그게 컴퓨터라는 물건이냐. 그래서 무엇을 하고 있느냐?」",
 34: "「요괴넷으로 사건을 조사하고 있어요」",
 35: "「요괴넷?」",
 36: "「네. 지금은 인터넷으로 앉은 자리에서 온 세상의 정보를 볼 수 있으니까요」",
 37: "「…… 키타로. 요즘 자주, 그 컴퓨터인지 뭔지 앞에 앉아 있는 것 같다만…」",
}

def main():
    d = bytearray(open('extract/D_MESS.BIN', 'rb').read())
    tbl = parse_table(bytes(d), BASE); n = len(tbl)
    end = bytes(d).find(b'\x1f', tbl[-1]) + 1
    orig = [bytes(d[tbl[k]:(tbl[k+1] if k+1 < n else end)]) for k in range(n)]
    contents = []; missing = {}; report = []
    for k in range(n):
        if k in TL:
            enc, miss, boxes = encode(TL[k])
            if miss: missing[k] = miss
            contents.append(enc)
            over = [(bi, len(b)) for bi, b in enumerate(boxes) if len(b) > MAX_LINES]
            report.append((k, len(boxes), max((len(b) for b in boxes), default=0),
                           max((sum(char_width(c) for c in ln) for b in boxes for ln in b), default=0)))
        else:
            contents.append(orig[k])
    if missing:
        for k, m in missing.items(): print(f"MISSING msg {k}: {''.join(sorted(set(m)))}")
        sys.exit(1)
    print("msg | boxes | maxlines/box | maxlinewidth")
    for k, nb, ml, mw in report:
        flag = "  <-- OVER" if (ml > MAX_LINES or mw > 36) else ""
        print(f"{k:3d} |   {nb}   |      {ml}       |     {mw}{flag}")
    table_bytes = n * 2; pos = table_bytes; offsets = []
    for c in contents: offsets.append(pos); pos += len(c)
    print(f"total {pos} / region {REGION}")
    if pos > REGION: print("OVER BUDGET"); sys.exit(1)
    newsub = bytearray(REGION)
    for k in range(n):
        struct.pack_into('<H', newsub, 2*k, offsets[k] - 2*k)
    for k in range(n):
        newsub[offsets[k]:offsets[k]+len(contents[k])] = contents[k]
    d[BASE:BASE+REGION] = newsub
    open('D_MESS_ko.BIN', 'wb').write(d); assert len(d) == 814667
    print("wrote D_MESS_ko.BIN")

if __name__ == '__main__':
    main()
