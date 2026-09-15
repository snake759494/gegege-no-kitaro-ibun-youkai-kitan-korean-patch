# 글꼴 출처

- **서울한강체** (`SeoulHangangB.ttf`, `SeoulHangangEB.ttf`) — 서울특별시 제공. 대사 글꼴(D_MOJI.BIN의 한글 2,350자)과 캐릭터 이름표(D_CHFONT.BIN)는 서울한강체 Bold, UI 스프라이트(D_SYS.BIN, 그리고 v1.0.0에만 들어갔던 D_BG.BIN 메뉴 배경)의 한글은 서울한강체 Bold/ExtraBold를 래스터화했습니다. [서울시 서체 안내](https://www.seoul.go.kr/seoul/font.do)를 참고하세요.
- `tools/koimg.py`의 글꼴 표에는 서울한강체 Medium/Light와 나눔스퀘어 네오(SIL OFL)도 등록되어 있지만, 현재 배포본의 패치 스크립트(`patch_sys.py`, `patch_bg.py`)는 Bold/ExtraBold만 사용합니다.

TTF 파일은 저장소와 릴리즈에 포함하지 않습니다. 다시 빌드하려면 [개발 빌드](BUILD.md)의 안내대로 글꼴을 직접 받아 저장소 루트에 두세요. 게임의 일본어 글꼴 덤프는 공개하지 않습니다.
