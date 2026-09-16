# 개발 빌드

검증 환경은 Windows 11, Python 3.13입니다. `requirements.txt`의 라이브러리(Pillow, numpy, pycdlib)를 설치하고 xdelta3 실행 파일을 별도 준비해 저장소 루트에 `xdelta.exe`로 둡니다. 원본 ISO는 루트에 `Gegege no Kitarou Ibun Youkai Kitan.iso`라는 이름으로 두고, 글꼴은 [글꼴 출처](FONT_CREDITS.md)의 서울한강체 `SeoulHangangB.ttf`, `SeoulHangangEB.ttf`를 루트에 둡니다(`tools/koimg.py`의 글꼴 표에 있는 나머지 TTF는 현재 패치 스크립트가 쓰지 않습니다).

```powershell
python -m pip install -r requirements.txt
python tools/extract_iso.py                      # ISO -> extract/D_MOJI.BIN D_MESS.BIN D_CHFONT.BIN D_SYS.BIN D_BG.BIN
python tools/hangul_font.py render SeoulHangangB.ttf extract/D_MOJI.BIN D_MOJI_hangul2350.BIN
python tools/ko_nameplates.py                    # extract/D_CHFONT.BIN -> D_CHFONT_ko.BIN
python tools/ko_inject.py                        # script_ko.tsv + extract/D_MESS.BIN -> D_MESS_ko.BIN
python tools/qa_text.py                          # 텍스트 자동 검수 (RESULT 줄이 no blocking issues 여야 함)
python tools/build_iso.py "Gegege no Kitarou Ibun Youkai Kitan.iso" Kitaro_KR_v1.0.2.iso D_MOJI.BIN=D_MOJI_hangul2350.BIN D_MESS.BIN=D_MESS_ko.BIN D_CHFONT.BIN=D_CHFONT_ko.BIN
.\xdelta.exe -e -9 -f -s "Gegege no Kitarou Ibun Youkai Kitan.iso" Kitaro_KR_v1.0.2.iso Kitaro_Ibun_Youkai_Kitan_PS2_KO_v1.0.2.xdelta
.\xdelta.exe -d -f -s "Gegege no Kitarou Ibun Youkai Kitan.iso" Kitaro_Ibun_Youkai_Kitan_PS2_KO_v1.0.2.xdelta roundtrip.iso   # 해시가 Kitaro_KR_v1.0.2.iso와 같아야 함
```

v1.0.2는 대사·글꼴·이름표만 패치합니다. `patch_sys.py`, `patch_bg.py`, `qa_img.py`는 제외된 UI 이미지의 참고 도구이며 위 빌드에는 사용하지 않습니다. **출력 ISO는 반드시 존재하지 않는 새 경로를 지정하세요.** `build_iso.py`는 같은 크기의 기존 출력을 재사용하므로 이전 빌드를 재사용하면 제외한 이미지 패치가 남을 수 있습니다.

모든 스크립트는 저장소 루트를 기준 경로로 잡습니다(`ko_nameplates.py`, `ko_inject.py`는 루트에서 실행). `patch_bg.py`는 `extract/D_BG.BIN`이 없으면 루트의 원본 ISO에서 직접 읽습니다. 생성 파일은 모두 원본과 같은 크기이며 `build_iso.py`는 크기가 다르면 중단하고, 각 파일을 ISO 안의 원래 LBA 위치(D_MOJI 1899, D_MESS 2623, D_SYS 3021, D_BG 56654, D_CHFONT 85908)에 덮어쓴 뒤 다시 읽어 확인합니다. 파일 시스템은 재구성하지 않습니다.

번역 기준은 `script_ko.tsv`(열: base, index, korean)입니다. `@`는 강제 대사창 넘김(0x1E), `|`는 강제 줄바꿈(0x1D)이며 나머지 줄바꿈·페이지 분할은 `ko_inject.py`가 영역별 규칙으로 자동 처리합니다. 한 줄이 규칙보다 길어지거나 서브파일 용량(0x800 정렬 블록)을 넘기면 주입이 중단됩니다. KS X 1001 밖의 글자(낱자모 ㄴ, 일부 한자 등)는 주입할 수 없으므로 빠진 글자로 보고됩니다.

`script_jp.tsv`는 `tools/dump_script.py`가 `glyph_map.json`(글리프 → 유니코드, `tools/glyph_map.py`가 원본 글꼴 이미지를 JIS 글꼴과 대조해 만든 표)으로 원본 메시지를 읽어 낸 것입니다. 기계 디코딩이라 희귀 한자가 다른 글자로 나올 수 있으니 애매한 원문은 `tools/mess_render.py`로 원본 글꼴을 직접 그려 확인합니다.

이 저장소의 소스로 다시 만든 패치 파일 3개가 현재 배포본과 바이트 단위로 같은지는 [release_verification.json](release_verification.json)의 `rebuild` 항목에 기록했습니다. 빌드는 에뮬레이터를 실행하지 않습니다. 공개 저장소만으로 게임 이미지를 만들 수는 없습니다.

## 그 밖의 도구 (`tools/`)

| 파일 | 용도 |
| --- | --- |
| `moji_font.py extract\|inject` | `D_MOJI.BIN` ↔ PNG 글리프 시트 |
| `hangul_font.py render FONT.ttf D_MOJI.BIN out.bin` | TTF로 한글 2,350자를 렌더링해 글리프 슬롯에 주입, `.map.tsv` 대응표 출력 |
| `glyph_map.py`, `glyph_anchors.py` | 원본 글리프 → 유니코드 대응표 생성과 검증용 고정 쌍 |
| `dump_script.py` | `D_MESS.BIN` 전체를 `script_jp.tsv`로 덤프 |
| `mess_parse.py`, `mess_render.py` | `D_MESS.BIN` 서브파일 파서, 메시지를 원본 글꼴로 PNG 렌더링 |
| `ko_inject.py` | `script_ko.tsv` → `D_MESS_ko.BIN` (단일 주입기) |
| `ko_dialogue.py`, `ko_system.py` | 초기 개발 단계의 부분 주입기(인트로 38개 대사, 짧은 시스템 문자열). 현재 빌드는 사용하지 않음 |
| `chfont_names.py`, `ko_nameplates.py` | `D_CHFONT.BIN` 이름표 추출 / 한글 이름표 생성 |
| `sysimg.py scan\|sheet FILE [OUTDIR]` | 스프라이트 컨테이너 스캔, 컨택트 시트 추출 |
| `koimg.py` | 스프라이트 팔레트에 맞춰 한글을 그려 넣는 렌더러(라이브러리) |
| `patch_sys.py [--preview DIR]`, `patch_bg.py [--preview DIR]` | UI 스프라이트 / 메뉴 배경 한글화 |
| `qa_text.py [--full]`, `qa_img.py [--sheet DIR]` | 자동 검수 |
| `build_iso.py`, `extract_iso.py` | ISO 제자리 패치 / 원본 파일 추출 |
