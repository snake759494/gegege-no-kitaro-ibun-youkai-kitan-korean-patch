# 게게게의 키타로 이문요괴기담 PS2 한글패치

일본판 **ゲゲゲの鬼太郎 異聞妖怪奇譚 (SLPM-65337, 코나미, 2003)**용 비공식 한국어 패치 **v1.0.3**입니다. 키타로와 요괴들이 등장하는 PS2 시뮬레이션 RPG의 게임 내 텍스트, 대사 글꼴과 캐릭터 이름표를 한글화했습니다. 이번 릴리즈는 사용자가 정상 진행을 확인한 `Kitaro_KR_UI_candidate_20260916.iso`와 동일한 구성입니다. 검증 규칙을 적용해 UI 스프라이트 99장과 메뉴 배경 9장의 한글화를 다시 적용했습니다.

[정식 릴리즈 다운로드](https://github.com/snake759494/gegege-no-kitaro-ibun-youkai-kitan-korean-patch/releases/latest) · [제작 설명](TECHNICAL.md) · [개발 빌드](BUILD.md) · [검수 기록](REVIEW.md) · [실행 확인 기록](runtime_test.md) · [변경 기록](CHANGELOG.md)

릴리즈 첨부 파일은 **`Kitaro_Ibun_Youkai_Kitan_PS2_KO_v1.0.3.xdelta` 하나**입니다. 저장소에는 제작 소스(`tools/`), 번역 원본(`script_ko.tsv`), 대조용 원문 덤프(`script_jp.tsv`), 글리프 대응표와 검증 기록을 공개합니다. 원본 및 패치 적용 ISO, 게임에서 추출한 바이너리, 글꼴 TTF, 스크린샷, 외부 실행 파일은 배포하지 않습니다. GitHub의 Source code ZIP/TAR는 공개 소스 압축본입니다.

## 적용할 원본

| 항목 | 값 |
| --- | --- |
| 대상 | 수정되지 않은 PS2 일본판 SLPM-65337 ISO (UDF+ISO9660, DVD 단층) |
| 원본 ISO 크기 | 2,316,861,440 바이트 |
| 원본 ISO MD5 | `a3ba2caa94c05e13aa0191f6850367b8` |
| 원본 ISO SHA-1 | `cb93181769e8e9825e1a7cb8e6502cbf87859f31` |
| 원본 ISO SHA-256 | `89ce33d0bf65b33f1fdd9ef3bae28a9700a4b0e700199f73d45633d620ad1186` |
| xdelta 크기 | 664,194 바이트 |
| xdelta SHA-256 | `0fc656455dbb51761598a81126d0159d92dcc1efdba38cdc5b396ff88c389110` |
| 결과 ISO 크기 | 2,316,861,440 바이트 (원본과 동일) |
| 결과 ISO SHA-1 | `64c3d7a4586c02a60acbf78302ba0ceb0d41ce36` |
| 결과 ISO SHA-256 | `b673e0832b9bd4e23ddf6527b836e8c90bab81e04b05502900bd4b7e6a9a9ca3` |

실제 배포 파일에서 계산한 값입니다. 원본 게임은 별도로 준비해야 합니다. 파일명보다 크기와 해시가 중요하며, 이전 한글판이나 다른 덤프에 덧씌우지 마세요. 패치는 ISO 안의 데이터 파일 5개(`D_MOJI.BIN`, `D_MESS.BIN`, `D_CHFONT.BIN`, `D_SYS.BIN`, `D_BG.BIN`)를 **같은 크기로 제자리에서 덮어쓰기만** 하므로 파일 시스템 배치와 실행 파일(`SLPM_653.37`)은 원본 그대로입니다.

## 패치 적용 방법

1. 릴리즈에서 xdelta를 받습니다.
2. xdelta3를 지원하는 도구의 **Apply Patch**에서 Patch는 xdelta, Source는 위 해시의 원본 ISO, Output은 새 이름의 ISO로 지정합니다.
3. 결과 ISO의 SHA-256을 위 표와 비교합니다.
4. PCSX2 등에서 새 ISO를 엽니다. 원본 ISO로 만든 **상태 저장(save state)에는 옛 글꼴이 VRAM에 남을 수 있으므로** 새로 부팅하고 메모리 카드 저장으로 이어 하세요. 메모리 카드 세이브 데이터는 그대로 호환됩니다(실행 파일과 세이브 형식을 바꾸지 않았습니다).

PowerShell에서 원본 확인 및 명령줄 적용:

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath '.\Gegege no Kitarou Ibun Youkai Kitan.iso'
Get-FileHash -Algorithm SHA256 -LiteralPath '.\Gegege no Kitarou Ibun Youkai Kitan.iso'
.\xdelta3.exe -d -s '.\Gegege no Kitarou Ibun Youkai Kitan.iso' '.\Kitaro_Ibun_Youkai_Kitan_PS2_KO_v1.0.3.xdelta' '.\Kitaro_KR_v1.0.3.iso'
Get-FileHash -Algorithm SHA256 -LiteralPath '.\Kitaro_KR_v1.0.3.iso'
```

원본·패치·결과의 해시를 자동 검사하고 기존 출력 파일을 덮어쓰지 않는 자체 도구도 제공합니다:

```powershell
python apply_release.py --xdelta '.\xdelta3.exe' --source '.\Gegege no Kitarou Ibun Youkai Kitan.iso' --patch '.\Kitaro_Ibun_Youkai_Kitan_PS2_KO_v1.0.3.xdelta' --output '.\Kitaro_KR_v1.0.3.iso'
```

외부 도구 실행 파일은 포함하지 않습니다. [xdelta 공식 프로젝트](https://github.com/jmacd/xdelta)를 참고하세요. 패치는 xdelta 3.1.0으로 만들었습니다.

## 작업 범위

- **텍스트** — `D_MESS.BIN`의 메시지 13,481개 중 13,458개를 한국어로 번역. 나머지 23개는 숫자·기호·`?????` 같은 더미라 번역 대상이 아닙니다. 스토리 전 챕터(프롤로그~엔딩), 전투·필드 명령과 도움말, 기술명 512개, 아이템, 챕터 타이틀, 임무 목표, 세이브·로드 시스템 메시지, 요괴 대도감, 모노노케WEB 게시판, 요괴타임스 신문 기사, 유닛 이름 목록, 디버그 메뉴까지 포함합니다.
- **글꼴** — 대사 글꼴 `D_MOJI.BIN`의 한자 영역과 빈 블록에 KS X 1001 완성형 한글 2,350자를 서울한강체 Bold로 그려 넣었습니다. 원본 한자와 같은 22×22 px 잉크 영역, 같은 4단계 안티에일리어싱 값을 씁니다.
- **이름표** — 대사창의 캐릭터 이름 플레이트 138장(`D_CHFONT.BIN`, 96×32 4bpp) 전부 한글화.
- **UI 이미지** — `D_SYS.BIN`의 스프라이트 99장(전투·메뉴 버튼, 상태 이상, 챕터 타이틀 44장, 장소 간판 등)과 `D_BG.BIN`의 휴대폰·상점·신문 메뉴 배경 9장을 한글화했습니다. 원본 헤더·팔레트·오프셋·파일 크기를 보존하며 지정한 픽셀 밖 변경을 거부합니다.
- **의도적으로 남긴 것** — 타이틀 화면의 게임 로고(`D_BG.BIN` #66), 요괴타임스의 눈알 일러스트 로고, KONAMI 로고는 원본 아트 그대로입니다.
- **그 밖의 미적용 이미지** — `D_EFF.BIN`의 효과 라벨과 `D_TXD.BIN`·`D_BTTF~1.BIN`의 맵 텍스처는 원본입니다.

레이아웃은 원본에서 실측한 규칙을 따릅니다. 대사창은 한 줄 34 half-unit(전각 17자) 이하 3줄, 넘치면 다음 대사창으로 분할합니다. 요괴 대도감(20/21), 게시판(34/37), 임무 목표(28/3), 세이브 패널(36/6)은 영역별 규칙을 따로 둡니다. 자세한 규칙은 [제작 설명](TECHNICAL.md)에 있습니다.

## 검증 및 알려진 한계

정식 릴리즈는 배포 구분이며 전체 플레이 검증 완료를 뜻하지 않습니다.

- **자동 검수** — 기존 텍스트 13,458/13,458 왕복 일치 기록을 유지합니다(텍스트 페이로드 동일). 재적용 이미지는 허용 영역 밖 변경 0, 11개 회귀 검사 통과. [이미지 검증 규칙과 결과](IMAGE_VALIDATION.md)를 참고하세요. `qa_img_report.txt`는 과거 검사 기록입니다.
- **정독 검수** — 일본어/한국어 13,458쌍을 처음부터 끝까지 한 줄씩 대조했습니다. 자동 검수로는 잡히지 않는 오역(妖怪血液→"혈장", 音楽配信→"배신" 등)과 일본식 한자어를 고쳤습니다. 목록은 [검수 기록](REVIEW.md)에 있습니다.
- **xdelta 왕복** — 원본에 배포 패치를 다시 적용한 결과가 사용자가 확인한 ISO와 SHA-256이 일치합니다. ISO 전체 비교에서 위 5개 파일 밖의 변경은 0바이트입니다.
- **재현성** — 기존 대사·글꼴·이름표는 동일하며, SYS·BG 원본 지문·수정 범위와 이번 배포 해시는 [release_verification.json](release_verification.json)에 기록했습니다. BG 독립 재생성 결과도 일치합니다.
- **에뮬레이터** — PCSX2 v2.9.52에서 새 게임부터 병원 탐색까지 진행 및 이동·회전을 확인했습니다. 사용자가 재적용 후보의 정상 진행을 확인하고 릴리즈를 요청했습니다. 기존 프리징의 근본 원인은 미확정이며, 4가지 구성의 통제 비교·전체 이미지 실행·전체 챕터 완주·실기는 미검증입니다. [실행 확인 기록](runtime_test.md)을 참고하세요.
- **알려진 표시 특성** — 요괴 대도감 이름·게시판처럼 원본이 한 줄에 여러 항목을 붙여 쓰는 곳은 한국어가 길어지면 원본보다 페이지가 늘어날 수 있습니다(자동 검수 4항목이 원본이 페이지 넘김을 쓰는 영역에서만 허용). 원문의 강조 표시(`<8b>/<8c>`)와 가운뎃점(`<87>`)은 한국어에서 일반 문장부호로 바꿨습니다.

오류 제보에는 패치 버전, 결과 ISO 해시, 에뮬레이터 버전, 장소·재현 순서와 상태 저장 사용 여부를 적어 주세요. 대사 오류는 화면에 보이는 문장을 그대로 적어 주면 `script_ko.tsv`에서 바로 찾을 수 있습니다. 게임 이미지와 추출 바이너리는 이슈에 첨부하지 마세요.

## 권리와 글꼴

원작 및 게임 텍스트의 권리는 각 권리자에게 있습니다. 이 프로젝트는 코나미의 공식 한국어판이나 공식 승인 프로젝트가 아닙니다. [권리 안내](RIGHTS.md)와 [글꼴 출처](FONT_CREDITS.md)를 참고하세요.
