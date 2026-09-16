#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build D_SYS_ko.BIN: Korean captions painted into the sprite containers.

    python tools/patch_sys.py [--preview DIR]

Reads extract/D_SYS.BIN, rewrites every text sprite listed below in place
(sizes never change, so the ISO can be patched LBA-for-LBA) and writes
D_SYS_ko.BIN into the project root.
"""
import os
import sys
import argparse
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sysimg import Pack                      # noqa: E402
import koimg                                 # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'extract', 'D_SYS.BIN')
DST = os.path.join(ROOT, 'D_SYS_ko.BIN')

WHITE, BLACK = (255, 255, 255), (0, 0, 0)

# --------------------------------------------------------------------------
# 44 chapter titles - one 4bpp sprite per container
# --------------------------------------------------------------------------
CHAPTERS = [
    (0x484800, '「홀림의 날갯소리…요사한 자장가」'),
    (0x489000, '「깨어진 휴식…어둠 밝히는 사악한 웃음」'),
    (0x48d800, '「홀린 영혼·말 없는 마성의 소녀」'),
    (0x492000, '「홍련의 정념·강습…불꽃 두른 목」'),
    (0x496000, '「괴기! 하늘을 나는 사자머리」'),
    (0x49a000, '「채워지지 않는 갈증·생명을 빠는 집」'),
    (0x49e000, '「꾸며진 함정·강림…불꽃의 신」'),
    (0x4a2000, '「감미로운 숙성·요괴 절임의 숲」'),
    (0x4a6000, '「해후…불멸의 어둠」'),
    (0x4a9800, '「집결·설국 요괴 연합」'),
    (0x4ad000, '「이국의 괴이·젊음을 앗는 석상」'),
    (0x4b1000, '「복마의 미궁 아키요시동」'),
    (0x4b4000, '「닫힌 길·영하의 파수꾼」'),
    (0x4b8000, '「사투! 대결 누라리횬」'),
    (0x4bc000, '「새로운 자객」'),
    (0x4be800, '「파란의 출항·유전의 항로」'),
    (0x4c2800, '「요괴 돼지 묶인 동굴」'),
    (0x4c6000, '「요화요란·환상의 낙원」'),
    (0x4ca000, '「피에 굶주린 맹아」'),
    (0x4cd000, '「정적의 숲」'),
    (0x4cf000, '「닿아라 기도여! 공포의 요괴 우귀」'),
    (0x4d3000, '「결단의 행방」'),
    (0x4d5000, '「마의 방향·인랑의 특효약」'),
    (0x4d9000, '「제물의 비명…격돌 마녀 군단」'),
    (0x4dd000, '「바라지 않은 결말」'),
    (0x4df800, '「이대 악마 등장…교토 혈전」'),
    (0x4e3800, '「밀림으로의 초대장·혈전 오가사와라」'),
    (0x4e7800, '「괴기상 잠입·일그러진 수도」'),
    (0x4eb800, '「시간을 새기는 인형관」'),
    (0x4ee800, '「향연·타워 전망대 혈전」'),
    (0x4f2800, '「늦게 온 초대객」'),
    (0x4f6000, '「새로운 싸움의 서곡」'),
    (0x4f9800, '「어둠으로부터의 탈출」'),
    (0x4fc000, '「꺼지지 않는 등불」'),
    (0x4fe000, '「빼앗긴 젊음·론론의 변신」'),
    (0x502000, '「승리를 잇는 다리」'),
    (0x504800, '「영장 오소레잔·애도의 붉은 강」'),
    (0x508800, '「구미의 혈족」'),
    (0x50a800, '「하늘을 나는 밤의 주민」'),
    (0x50d800, '「희망의 종착역」'),
    (0x510000, '「대요괴 기가」'),
    (0x512800, '「최종 혈전·키타로 대 기가」'),
    (0x516800, '「잠들지 않는 눈동자·사안의 조종 실」'),
    (0x51a800, '「완전한 부활·요괴기담의 종연」'),
]


def do_chapters(buf, preview):
    for off, txt in CHAPTERS:
        p = Pack(buf, off)
        p.data = buf
        koimg.paint(p, 0, txt, font_key='B', stroke=2, pad=2,
                    fill=WHITE, outline=BLACK, alpha_thr=100)
        if preview:
            p.image(0).save(os.path.join(preview, 'ch_%06x.png' % off))


# --------------------------------------------------------------------------
# main battle / menu UI pack
# --------------------------------------------------------------------------
def do_ui(buf, preview):
    p = Pack(buf, 0x40800)
    p.data = buf

    # 31-35: stone tab plaques - keep the plate, repaint the caption
    plate = koimg.make_plate(p, [31, 32, 33, 34, 35])
    # wording matches the text menu in D_MESS sub 0x00000 msgs 72-76
    tabs = {31: '조작가능', 32: '적극적으로', 33: '효율적으로',
            34: '반격불가', 35: '반드시방어'}
    for i, txt in tabs.items():
        koimg.paint_over(p, i, txt, plate, font_key='B', stroke=1, pad=2,
                         fill=WHITE, outline=(24, 20, 16), maxfill=0.94)

    # plain captions on transparent background
    plain = {
        36: ('반격명령', {}), 37: ('작전목적', {}),
        40: ('기 록', {}), 41: ('불러오기', {}),
        42: ('막간화면', {}), 43: ('설 정', {}),
        62: ('눈속임', {}), 63: ('독', dict(maxfill=0.9)),
        64: ('마비', dict(maxfill=0.86)), 65: ('최면', dict(maxfill=0.86)),
        66: ('다이아화', {}), 67: ('석화', dict(maxfill=0.86)),
        68: ('점착', dict(maxfill=0.86)),
        82: ('로딩중…', {}),
    }
    for i, (txt, kw) in plain.items():
        koimg.paint(p, i, txt, font_key='B', stroke=2, pad=1, **kw)

    # 79: brush stamp - keep the frame, repaint the two characters
    koimg.paint_over(p, 79, '결착', koimg.clear_inside(p, 79, (6, 6, 6, 6)),
                     font_key='EB', stroke=2, pad=6,
                     fill=(131, 41, 8), outline=(74, 24, 4), maxfill=0.96)

    # 24x24 stat chips - keep the coloured tile, swap the single glyph
    chips = {44: '명', 45: '회', 48: '공', 49: '방', 69: '출', 78: '완'}
    for i, txt in chips.items():
        f, o = koimg.analyse(p, i)
        koimg.paint_over(p, i, txt, koimg.fill_inside(p, i, 3, margin=2),
                         font_key='EB', stroke=1, pad=1,
                         fill=f, outline=o, maxfill=0.99)

    if preview:
        for i in sorted(set(list(tabs) + list(plain) + list(chips) + [79])):
            p.image(i).save(os.path.join(preview, 'ui_%02d.png' % i))


# --------------------------------------------------------------------------
# mobile-phone web pages
# --------------------------------------------------------------------------
def do_web(buf, preview):
    # 0x96800 - page logos (key colour is blue)
    p = Pack(buf, 0x96800)
    p.data = buf
    # sprite 0 (妖怪TIMES"y"出張所) is the newspaper's illustrated logo -
    # left as drawn, like the KONAMI mark; its menu entries are Korean.
    logos = {1: '모노노케WEB', 2: '요괴 "y" 쇼핑'}
    for i, txt in logos.items():
        f, o = koimg.analyse(p, i)
        koimg.paint(p, i, txt, font_key='EB', stroke=2, pad=3,
                    fill=f, outline=o, maxfill=0.88)

    # 0xd6000 - link buttons, light / highlighted pairs
    q = Pack(buf, 0xd6000)
    q.data = buf
    btns = {0: '요괴TIMES "y" 출장소', 1: '요괴TIMES "y" 출장소',
            2: '모노노케WEB', 3: '모노노케WEB',
            4: '요괴 "y" 쇼핑', 5: '요괴 "y" 쇼핑',
            6: '돌아가기', 7: '돌아가기'}
    for i, txt in btns.items():
        ink, _bg = koimg.ink_colour(q, i)
        koimg.paint_over(q, i, txt, koimg.fill_inside(q, i, (3, 3, 3, 3)),
                         font_key='B', stroke=0, pad=4, align='l',
                         fill=ink, outline=ink, maxfill=0.82)

    # 0xa6000 - description panels (4bpp, blue background)
    r = Pack(buf, 0xa6000)
    r.data = buf
    desc = [
        '요괴 회사가 운영·관리하는\n인터넷 신문입니다.\n지금까지 있었던 이야기의\n의외의 이면을 알 수 있을지도….',
        '인간이 운영·관리하는\nBBS(인터넷 게시판)입니다.\n도움이 되는 정보가\n숨겨져 있을지도….',
        '도구의 구입이나 매각을\n할 수 있습니다.',
        '지금까지 게임 중에 본\n이벤트 컷을\n감상할 수 있습니다.',
        '링크할 곳을 선택해 주세요.',
        '지금까지 게임 중에 본\n무비를 감상할 수 있습니다.',
    ]
    for i, txt in enumerate(desc):
        ink, _bg = koimg.ink_colour(r, i)
        koimg.paint_over(r, i, txt, koimg.flat_plate(r, i),
                         font_key='B', stroke=0, pad=8, align='l',
                         line_gap=4, fill=ink, outline=ink, maxfill=0.94,
                         max_pt=17)

    if preview:
        for i in logos:
            p.image(i).save(os.path.join(preview, 'web_%d.png' % i))
        for i in btns:
            q.image(i).save(os.path.join(preview, 'btn_%d.png' % i))
        for i in range(len(desc)):
            r.image(i).save(os.path.join(preview, 'desc_%d.png' % i))


# --------------------------------------------------------------------------
# shop screens
# --------------------------------------------------------------------------
def do_shop(buf, preview):
    p = Pack(buf, 0xbf800)
    p.data = buf
    sort = {4: '종류순', 5: '가격순', 6: '가나다순'}
    for i, txt in sort.items():
        f, o = koimg.analyse(p, i)
        koimg.paint(p, i, txt, font_key='B', stroke=1, pad=2,
                    fill=f, outline=o, maxfill=0.92, max_pt=17)

    q = Pack(buf, 0xd0000)
    q.data = buf
    help_ = {
        0: '도구를 구입할 수\n있습니다.',
        1: '가지고 있는 도구를\n매각할 수 있습니다.',
        2: '요괴 링크 화면으로 돌아갑니다.',
        3: '구입 화면으로',
        4: '매각 화면으로',
        5: '돌아가기',
    }
    for i, txt in help_.items():
        ink, _bg = koimg.ink_colour(q, i)
        koimg.paint_over(q, i, txt, koimg.flat_plate(q, i), font_key='B',
                         stroke=0, pad=2, align='l', line_gap=3,
                         fill=ink, outline=ink, maxfill=0.94, max_pt=15)
    if preview:
        for i in sort:
            p.image(i).save(os.path.join(preview, 'sort_%d.png' % i))
        for i in help_:
            q.image(i).save(os.path.join(preview, 'help_%d.png' % i))


# --------------------------------------------------------------------------
# vertical wooden place-name signs
# --------------------------------------------------------------------------
def do_places(buf, preview):
    p = Pack(buf, 0x147800)
    p.data = buf
    names = {0: '키타로의 집', 2: '키타로의 집',
             3: '요괴 아파트', 5: '요괴 아파트'}
    for i, txt in names.items():
        f, o = koimg.analyse(p, i)
        koimg.paint(p, i, txt, font_key='B', stroke=2, pad=4, vertical=True,
                    line_gap=-2, fill=f, outline=o, maxfill=0.92)
    if preview:
        for i in names:
            p.image(i).save(os.path.join(preview, 'place_%d.png' % i))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview')
    parser.add_argument('--output',default=DST)
    parser.add_argument('--groups',nargs='+',choices=['ui','chapters','web','shop','places'],
                        default=['ui','chapters','web','shop','places'])
    args=parser.parse_args()
    preview=args.preview
    if preview:
        os.makedirs(preview, exist_ok=True)
    src=Path(SRC).read_bytes()
    buf=bytearray(src)
    actions={'ui':do_ui,'chapters':do_chapters,'web':do_web,'shop':do_shop,'places':do_places}
    for group in args.groups:
        actions[group](buf,preview)
    from image_safety import validate
    report=validate(src,bytes(buf),'D_SYS',args.groups)
    if Path(args.output).resolve()==Path(SRC).resolve():
        raise ValueError('output must not overwrite source')
    with open(args.output, 'wb') as f:
        f.write(buf)
    Path(args.output+'.audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print('wrote', args.output, len(buf),'validated sprites',report['sprites_changed'])


if __name__ == '__main__':
    main()
