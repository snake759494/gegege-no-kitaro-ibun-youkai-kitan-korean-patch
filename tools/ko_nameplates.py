#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Replace the pre-rendered character name plates in D_CHFONT.BIN with Korean ones.

Layout: 64 sub-blocks of 0x2000; each holds 4 images of 96x32, 4bpp (low nibble = left
pixel) starting at 0x68, 0x600 bytes each. Palette (u16 RGBA5551 at 0x48): index 0 is
transparent, 1 = white core, 2 = mid grey, 3 = dark edge - the same 4-level anti-aliasing
as the dialogue font, so Korean is rendered with the same coverage thresholds."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SUB, W, H, IMG = 0x2000, 96, 32, 96 * 32 // 2
FONT = 'SeoulHangangB.ttf'
SS = 8                       # supersampling
BOX_W, BOX_H = 92, 24        # usable area inside the 96x32 plate
THRESH = (0.62, 0.38, 0.14)  # coverage -> palette index 1 / 2 / 3

def render(text):
    """Render `text` centred in a 96x32 cell as palette indices 0..3."""
    for size in range(26, 7, -1):
        f = ImageFont.truetype(FONT, size * SS)
        b = f.getbbox(text)
        w, h = (b[2] - b[0]) / SS, (b[3] - b[1]) / SS
        if w <= BOX_W and h <= BOX_H:
            break
    im = Image.new('L', (W * SS, H * SS), 0)
    ImageDraw.Draw(im).text(((W * SS - (b[2] - b[0])) / 2 - b[0],
                             (H * SS - (b[3] - b[1])) / 2 - b[1]), text, font=f, fill=255)
    cov = np.asarray(im, np.float32).reshape(H, SS, W, SS).mean(axis=(1, 3)) / 255.0
    q = np.zeros((H, W), np.uint8)
    q[cov >= THRESH[2]] = 3
    q[cov >= THRESH[1]] = 2
    q[cov >= THRESH[0]] = 1
    return q

def pack(px):
    a = px.reshape(-1, 2)
    return ((a[:, 0] & 0xF) | (a[:, 1] << 4)).astype(np.uint8).tobytes()

NAMES = {
 "00_0":"키타로","00_1":"눈알아버지","00_2":"쥐인간","00_3":"모래뿌리기할멈",
 "01_0":"아기울음영감","01_1":"고양이소녀","01_2":"이탄모멘","01_3":"누리카베",
 "02_0":"시사","02_1":"두레박불","02_2":"오보로구루마","02_3":"우산요괴",
 "03_0":"가뭄신","03_1":"와뉴도","03_2":"우귀","03_3":"가타키라우와",
 "04_0":"수달","04_1":"붉은혀","04_2":"빠진목","04_3":"해골여인",
 "05_0":"해골","05_1":"큰머리","05_2":"검은중","05_3":"우부메",
 "06_0":"큰지네","06_1":"호우코우","06_2":"호우코우(화)","06_3":"호우코우(수)",
 "07_0":"호우코우(풍)","07_1":"호우코우(지)","07_2":"만년죽","07_3":"요괴죽",
 "08_0":"대나무너구리","08_1":"무지나","08_2":"접이식입도","08_3":"거울사자",
 "09_0":"다이다라봇치","09_1":"다이다라봇치눈","09_2":"다이다라봇치입","09_3":"다이다라봇치코",
 "10_0":"다이다라봇치뇌","10_1":"다이다라봇치교주","10_2":"다이다라봇치신자","10_3":"누라리횬",
 "11_0":"눈아이","11_1":"설녀","11_2":"설남","11_3":"합체",
 "12_0":"들여우","12_1":"하늘여우","12_2":"진흙논귀신","12_3":"타쿠로우불",
 "13_0":"타쿠로우불","13_1":"가샤도쿠로","13_2":"박쥐","13_3":"흡혈박쥐",
 "14_0":"드라큘라","14_1":"늑대인간","14_2":"프랑켄슈타인","14_3":"미라 자매",
 "15_0":"카리카","15_1":"마녀 론론","15_2":"흡혈귀 라세느","15_3":"흡혈귀 엘리트",
 "16_0":"요괴수","16_1":"요괴수","16_2":"페낭가란","16_3":"보자이",
 "17_0":"고르곤","17_1":"박쥐고양이","17_2":"치","17_3":"백베어드",
 "18_0":"흡혈화 라그레시아","18_1":"악마 부엘","18_2":"악마 베리알","18_3":"베리알 손",
 "19_0":"베리알 발","19_1":"베리알 눈","19_2":"베리알 입","19_3":"눗페라보",
 "20_0":"거대 눗페라보","20_1":"란스필","20_2":"대요괴 기가","20_3":"지네",
 "21_0":"물병사","21_1":"박쥐고양이","21_2":"마녀","21_3":"미라남",
 "22_0":"밀랍인형","22_1":"늑대인간 부하","22_2":"아리랑 석상","22_3":"성 쥐인간",
 "23_0":"마녀 론론","23_1":"두레박떨구기","23_2":"메아리","23_3":"카마이타치",
 "24_0":"천장핥기","24_1":"그렘린","24_2":"노즈치","24_3":"우물선인",
 "25_0":"가루라","25_1":"까마귀텐구","25_2":"아부라스마시",
 "48_0":"원장","48_1":"간호사","48_2":"루카","48_3":"루카의 아버지",
 "49_0":"청년",
 "50_0":"자위대원","50_1":"아기 엄마","50_2":"키타로의 어머니","50_3":"경비원",
 "51_0":"기호","51_1":"야칸즈루","51_2":"판매상","51_3":"도라지",
 "52_0":"남자아이","52_1":"시민","52_2":"아저씨","52_3":"아주머니",
 "53_0":"큰돼지","53_1":"회사원",
 "60_0":"가짜 원장","60_1":"대나무 정령","60_2":"수수께끼 요괴","60_3":"???",
 "61_0":"여자아이","61_1":"수상한 상인","61_2":"수수께끼 방화범","61_3":"전원",
 "62_0":"움직이는 석상","62_1":"석상 눗페라보","62_2":"둔갑 까마귀","62_3":"아나운서",
 "63_0":"와이드쇼 진행자","63_1":"설국 합체요괴","63_2":"요괴수 분신체","63_3":"환상의 박쥐고양이",
}

def main():
    data = bytearray(open('extract/D_CHFONT.BIN', 'rb').read())
    done = 0
    for key, text in NAMES.items():
        s, k = (int(x) for x in key.split('_'))
        off = s * SUB + 0x68 + k * IMG
        if not np.frombuffer(bytes(data[off:off + IMG]), np.uint8).any():
            print(f"  warn: slot {key} is empty in the original, skipping"); continue
        data[off:off + IMG] = pack(render(text))
        done += 1
    open('D_CHFONT_ko.BIN', 'wb').write(data)
    assert len(data) == 524288
    print(f"rewrote {done} name plates -> D_CHFONT_ko.BIN")

if __name__ == '__main__':
    main()
