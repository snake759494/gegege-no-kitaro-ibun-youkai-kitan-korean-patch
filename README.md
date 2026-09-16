# 게게게의 키타로 이문요괴기담 PS2 한글패치

일본판 **ゲゲゲの鬼太郎 異聞妖怪奇譚 (SLPM-65337, 코나미, 2003)**용 비공식 한국어 패치 **v1.0.2**입니다. 키타로와 요괴들이 등장하는 PS2 시뮬레이션 RPG의 게임 내 텍스트, 대사 글꼴과 캐릭터 이름표를 한글화했습니다. 이번 릴리즈는 사용자가 문제 구간 이후 진행을 확인한 `Kitaro_DIAG_SYS.iso`와 동일한 구성입니다. UI 스프라이트와 메뉴 배경은 일본어 원본을 유지합니다.

[정식 릴리즈 다운로드](https://github.com/snake759494/gegege-no-kitaro-ibun-youkai-kitan-korean-patch/releases/latest) · [제작 설명](TECHNICAL.md) · [개발 빌드](BUILD.md) · [검수 기록](REVIEW.md) · [실행 확인 기록](runtime_test.md) · [변경 기록](CHANGELOG.md)

릴리즈 첨부 파일은 **`Kitaro_Ibun_Youkai_Kitan_PS2_KO_v1.0.2.xdelta` 하나**입니다. 저장소에는 제작 소스(`tools/`), 번역 원본(`script_ko.tsv`), 대조용 원문 덤프(`script_jp.tsv`), 글리프 대응표와 검증 기록을 공개합니다. 원본 및 패치 적용 ISO, 게임에서 추출한 바이너리, 글꼴 TTF, 스크린샷, 외부 실행 파일은 배포하지 않습니다. GitHub의 Source code ZIP/TAR는 공개 소스 압축본입니다.

## 적용할 원본

| 항목 | 값 |
| --- | --- |
| 대상 | 수정되지 않은 PS2 일본판 SLPM-65337 ISO (UDF+ISO9660, DVD 단층) |
| 원본 ISO 크기 | 2,316,861,440 바이트 |
| 원본 ISO MD5 | `a3ba2caa94c05e13aa0191f6850367b8` |
| 원본 ISO SHA-1 | `cb93181769e8e9825e1a7cb8e6502cbf87859f31` |
| 원본 ISO SHA-256 | `89ce33d0bf65b33f1fdd9ef3bae28a9700a4b0e700199f73d45633d620ad1186` |
| xdelta 크기 | 413,626 바이트 |
| xdelta SHA-256 | `21a7fc0f1a89b0576b6cdfb2135d735f61ffc6fce242d6481bef3abc1b6d696c` |
| 결과 ISO 크기 | 2,316,861,440 바이트 (원본과 동일) |
| 결과 ISO SHA-1 | `4e6da164ba49b6163ac0c7676e2d8a5566334bc5` |
| 결과 ISO SHA-256 | `77cc14cdeea44274e6b6b89e0b37dd0ae11504876561aff510f10d7200b4acf8` |

실제 배포 파일에서 계산한 값입니다. 원본 게임은 별도로 준비해야 합니다. 파일명보다 크기와 해시가 중요하며, 이전 한글판이나 다른 덤프에 덧씌우지 마세요. 패치는 ISO 안의 데이터 파일 3개(`D_MOJI.BIN`, `D_MESS.BIN`, `D_CHFONT.BIN`)를 **같은 크기로 제자리에서 덮어쓰기만** 하므로 파일 시스템 배치와 실행 파일(`SLPM_653.37`)은 원본 그대로입니다.

## 패치 적용 방법

1. 릴리즈에서 xdelta를 받습니다.
2. xdelta3를 지원하는 도구의 **Apply Patch**에서 Patch는 xdelta, Source는 위 해시의 원본 ISO, Output은 새 이름의 ISO로 지정합니다.
3. 결과 ISO의 SHA-256을 위 표와 비교합니다.
4. PCSX2 등에서 새 ISO를 엽니다. 원본 ISO로 만든 **상태 저장(save state)에는 옛 글꼴이 VRAM에 남을 수 있으므로** 새로 부팅하고 메모리 카드 저장으로 이어 하세요. 메모리 카드 세이브 데이터는 그대로 호환됩니다(실행 파일과 세이브 형식을 바꾸지 않았습니다).

PowerShell에서 원본 확인 및 명령줄 적용:

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath '.\Gegege no Kitarou Ibun Youkai Kitan.iso'
Get-FileHash -Algorithm SHA256 -LiteralPath '.\Gegege no Kitarou Ibun Youkai Kitan.iso'
.\xdelta3.exe -d -s '.\Gegege no Kitarou Ibun Youkai Kitan.iso' '.\Kitaro_Ibun_Youkai_Kitan_PS2_KO_v1.0.2.xdelta' '.\Kitaro_KR_v1.0.2.iso'
Get-FileHash -Algorithm SHA256 -LiteralPath '.\Kitaro_KR_v1.0.2.iso'
```

원본·패치·결과의 해시를 자동 검사하고 기존 출력 파일을 덮어쓰지 않는 자체 도구도 제공합니다:

```powershell
python apply_release.py --xdelta '.\xdelta3.exe' --source '.\Gegege no Kitarou Ibun Youkai Kitan.iso' --patch '.\Kitaro_Ibun_Youkai_Kitan_PS2_KO_v1.0.2.xdelta' --output '.\Kitaro_KR_v1.0.2.iso'
```

외부 도구 실행 파일은 포함하지 않습니다. [xdelta 공식 프로젝트](https://github.com/jmacd/xdelta)를 참고하세요. 패치는 xdelta 3.1.0으로 만들었습니다.

## 작업 범위

- **텍스트** — `D_MESS.BIN`의 메시지 13,481개 중 13,458개를 한국어로 번역. 나머지 23개는 숫자·기호·`?????` 같은 더미라 번역 대상이 아닙니다. 스토리 전 챕터(프롤로그~엔딩), 전투·필드 명령과 도움말, 기술명 512개, 아이템, 챕터 타이틀, 임무 목표, 세이브·로드 시스템 메시지, 요괴 대도감, 모노노케WEB 게시판, 요괴타임스 신문 기사, 유닛 이름 목록, 디버그 메뉴까지 포함합니다.
- **글꼴** — 대사 글꼴 `D_MOJI.BIN`의 한자 영역과 빈 블록에 KS X 1001 완성형 한글 2,350자를 서울한강체 Bold로 그려 넣었습니다. 원본 한자와 같은 22×22 px 잉크 영역, 같은 4단계 안티에일리어싱 값을 씁니다.
- **이름표** — 대사창의 캐릭터 이름 플레이트 138장(`D_CHFONT.BIN`, 96×32 4bpp) 전부 한글화.
- **UI 이미지 미적용** — `D_SYS.BIN`은 v1.0.2에서 원본으로 되돌렸습니다. 기존에 한글화했던 스프라이트 99장(전투·메뉴 버튼, 상태 이상, 챕터 타이틀 44장, 장소 간판 등)은 일본어로 표시됩니다. 대사·명령 등 `D_MESS.BIN`에서 읽는 텍스트와 이름표는 한국어를 유지합니다.
- **의도적으로 남긴 것** — 타이틀 화면의 게임 로고(`D_BG.BIN` #66), 요괴타임스의 눈알 일러스트 로고, KONAMI 로고는 원본 아트 그대로입니다.
- **그 밖의 미적용 이미지** — `D_BG.BIN`의 메뉴 배경은 v1.0.1부터 원본을 유지합니다. `D_EFF.BIN`의 효과 라벨과 `D_TXD.BIN`·`D_BTTF~1.BIN`의 맵 텍스처도 원본입니다.

레이아웃은 원본에서 실측한 규칙을 따릅니다. 대사창은 한 줄 34 half-unit(전각 17자) 이하 3줄, 넘치면 다음 대사창으로 분할합니다. 요괴 대도감(20/21), 게시판(34/37), 임무 목표(28/3), 세이브 패널(36/6)은 영역별 규칙을 따로 둡니다. 자세한 규칙은 [제작 설명](TECHNICAL.md)에 있습니다.

## 검증 및 알려진 한계

정식 릴리즈는 배포 구분이며 전체 플레이 검증 완료를 뜻하지 않습니다.

- **자동 검수** — `tools/qa_text.py` 재실행: 13,458/13,458 왕복 일치, 잔류 가나·한자 0, 줄 제한 초과 0, 차단 문제 없음. [qa_img_report.txt](qa_img_report.txt)는 이번 배포에서 제외된 UI 이미지의 과거 정적 검사 기록입니다.
- **정독 검수** — 일본어/한국어 13,458쌍을 처음부터 끝까지 한 줄씩 대조했습니다. 자동 검수로는 잡히지 않는 오역(妖怪血液→"혈장", 音楽配信→"배신" 등)과 일본식 한자어를 고쳤습니다. 목록은 [검수 기록](REVIEW.md)에 있습니다.
- **xdelta 왕복** — 검증 도구로 원본에 배포 패치를 적용한 결과의 SHA-256이 테스트한 ISO와 일치합니다. 원본 ISO와 전체 비교해 위 3개 파일 밖의 바이트가 전부 동일함도 확인했습니다.
- **재현성** — 포함된 3개 파일의 소스 재빌드 일치 기록과 이번 배포 해시는 [release_verification.json](release_verification.json)에 있습니다.
- **에뮬레이터** — PCSX2 v2.9.52에서 프롤로그 탐색의 시점 회전·이동 반응을 확인했고 사용자가 해당 구간 이후 진행을 확인했습니다. `D_SYS.BIN`이 멈춤의 원인이라고 확정한 것은 아니며, 자동 입력 해제와 방향 입력을 함께 확인했습니다. 전체 챕터 완주와 실제 PS2 기기는 미검증입니다. [실행 확인 기록](runtime_test.md)을 참고하세요.
- **알려진 표시 특성** — 요괴 대도감 이름·게시판처럼 원본이 한 줄에 여러 항목을 붙여 쓰는 곳은 한국어가 길어지면 원본보다 페이지가 늘어날 수 있습니다(자동 검수 4항목이 원본이 페이지 넘김을 쓰는 영역에서만 허용). 원문의 강조 표시(`<8b>/<8c>`)와 가운뎃점(`<87>`)은 한국어에서 일반 문장부호로 바꿨습니다.

오류 제보에는 패치 버전, 결과 ISO 해시, 에뮬레이터 버전, 장소·재현 순서와 상태 저장 사용 여부를 적어 주세요. 대사 오류는 화면에 보이는 문장을 그대로 적어 주면 `script_ko.tsv`에서 바로 찾을 수 있습니다. 게임 이미지와 추출 바이너리는 이슈에 첨부하지 마세요.

## 권리와 글꼴

원작 및 게임 텍스트의 권리는 각 권리자에게 있습니다. 이 프로젝트는 코나미의 공식 한국어판이나 공식 승인 프로젝트가 아닙니다. [권리 안내](RIGHTS.md)와 [글꼴 출처](FONT_CREDITS.md)를 참고하세요.
