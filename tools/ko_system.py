#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Translate short system/UI strings (battle commands, character names, save labels) in D_MESS.
Each sub-file is an independent 0x800-aligned, zero-padded block: a u16 self-relative offset
table then 0x1f-terminated messages. We rebuild only the sub-files we touch, keeping every
untranslated message's original bytes, and recompute the offset table. Region end = next
sub-file base; data end within a region = last 0x1f before the padding."""
import sys, struct
sys.path.insert(0, 'tools')
from hangul_font import ksx1001_hangul
from mess_parse import parse_table

KSX = ksx1001_hangul(); KIDX = {c: i for i, c in enumerate(KSX)}
PUNC1 = {' ': 0x20, '!': 0x21, '"': 0x22, '(': 0x28, ')': 0x29, ',': 0x2c,
         '.': 0x2e, '?': 0x3f, '~': 0x7e, ':': 0x3a}
for ch in '0123456789': PUNC1[ch] = ord(ch)

def enc_char(ch, out, missing):
    if ch == '「': out.append(0x89)
    elif ch == '」': out.append(0x8a)
    elif ch == '…': out += bytes([0x01, 0xac])
    elif ch == '|': out.append(0x1D)
    elif ch == '@': out.append(0x1E)
    elif ch in PUNC1: out.append(PUNC1[ch])
    elif 'A' <= ch <= 'Z' or 'a' <= ch <= 'z': out.append(ord(ch))
    else:
        try:
            c = 0x200 + KIDX[ch]; out += bytes([c >> 8, c & 0xFF])
        except KeyError:
            missing.append(ch)

def encode(s):
    out = bytearray(); miss = []
    for ch in s: enc_char(ch, out, miss)
    out.append(0x1F)
    return bytes(out), miss

def region_bounds(d, base, bases):
    nxt = min([x for x in bases if x > base] + [len(d)])
    # data end = last 0x1f strictly before the zero padding within [base, nxt)
    end = d.rfind(b'\x1f', base, nxt) + 1
    return nxt, end

def all_bases(d):
    out = []
    for base in range(0, len(d), 0x800):
        tbl = parse_table(d, base)
        if len(tbl) >= 3 and tbl[0] == base + 2 * len(tbl):
            out.append(base)
    return out

# --- translations: {sub_base: {msg_index: korean}} ---
TRANS = {
 0x0000: {  # battle / field command menu
   1: "이동", 2: "공격", 3: "도구", 4: "설득", 5: "능력",
   6: "안테나", 7: "대기", 8: "소화", 9: "구조", 10: "조사",
 },
 0x1000: {  # character / youkai name plates
   0: "키타로", 1: "눈알아버지", 2: "쥐인간", 3: "모래뿌리기할멈", 4: "아기울음영감",
   5: "고양이소녀", 6: "이탄모멘", 7: "누리카베", 8: "시사", 9: "두레박불",
   10: "오보로구루마", 11: "우산요괴", 12: "가뭄신", 13: "와뉴도", 14: "우귀",
   15: "가타키라우와", 16: "수달", 17: "붉은혀", 18: "빠진목", 19: "해골여인",
   20: "해골", 21: "큰머리", 22: "검은중", 23: "우부메", 24: "큰지네",
   25: "호우코우", 26: "호우코우(화)", 27: "호우코우(수)", 28: "호우코우(풍)", 29: "호우코우(지)",
   30: "만년죽", 31: "요괴죽", 32: "대나무너구리", 33: "쥐인간", 34: "접이식입도",
   35: "거울사자", 36: "다이다라봇치", 37: "다이다라봇치눈", 38: "다이다라봇치입",
   39: "다이다라봇치코", 40: "다이다라봇치뇌", 41: "다이다라봇치교신자",
   42: "다이다라봇치교교주", 43: "누라리횬",
 },
 0x7000: {  # save/load menu labels (short; long memory-card warnings left untouched)
   11: "데이터 로드", 12: "데이터 세이브",
 },
}

def main():
    d = bytearray(open('extract/D_MESS.BIN', 'rb').read())
    bases = all_bases(bytes(d))
    all_missing = {}
    for base, trans in TRANS.items():
        tbl = parse_table(bytes(d), base); n = len(tbl)
        nxt, end = region_bounds(bytes(d), base, bases)
        region = nxt - base
        contents = []
        for k in range(n):
            s = tbl[k]; e = tbl[k+1] if k+1 < n else end
            orig = bytes(d[s:e]) if e > s else b''
            if k in trans:
                enc, miss = encode(trans[k])
                if miss: all_missing.setdefault(base, {})[k] = miss
                contents.append(enc)
            else:
                contents.append(orig)
        # recompute table + pack
        pos = n*2; offs = []
        for c in contents: offs.append(pos); pos += len(c)
        if pos > region:
            print(f"sub {base:#x}: OVER region {pos} > {region}"); sys.exit(1)
        newsub = bytearray(region)
        for k in range(n): struct.pack_into('<H', newsub, 2*k, offs[k] - 2*k)
        for k in range(n): newsub[offs[k]:offs[k]+len(contents[k])] = contents[k]
        d[base:base+region] = newsub
        print(f"sub {base:#06x}: {len(trans)} strings, used {pos}/{region} bytes")
    if all_missing:
        for base, mm in all_missing.items():
            for k, m in mm.items(): print(f"MISSING sub {base:#x} msg {k}: {''.join(sorted(set(m)))}")
        sys.exit(1)
    # apply on top of the Korean dialogue file if present, else original
    src = 'D_MESS_ko.BIN'
    base_d = bytearray(open(src, 'rb').read())
    for base, trans in TRANS.items():
        base_d[base:base+ (min([x for x in bases if x>base]+[len(d)]) - base)] = d[base: (min([x for x in bases if x>base]+[len(d)]))]
    open('D_MESS_ko.BIN', 'wb').write(base_d)
    assert len(base_d) == 814667
    print("merged system strings into D_MESS_ko.BIN")

if __name__ == '__main__':
    main()
