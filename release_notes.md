# v1.0.2 — 진행 확인 구성 배포

사용자가 문제 구간 이후 진행을 확인한 `Kitaro_DIAG_SYS.iso`를 기준으로 만든 패치입니다.

- 대사·글꼴·캐릭터 이름표 한글화 유지: `D_MESS.BIN`, `D_MOJI.BIN`, `D_CHFONT.BIN` 3개만 변경합니다.
- `D_SYS.BIN`을 일본어 원본으로 복원했습니다. 메뉴·전투 UI, 상태 이상, 챕터 타이틀 등 기존 한글 이미지 99장은 일본어로 표시됩니다. `D_BG.BIN`도 원본을 유지합니다.
- PCSX2 v2.9.52에서 방향 입력에 따른 회전·이동을 확인한 뒤 사용자가 이후 진행을 확인했습니다. 이 결과만으로 D_SYS가 멈춤의 원인이라고 확정하지 않습니다. 전체 게임 완주·실기는 미검증입니다.
- 텍스트 자동 검수 통과(13,458/13,458 왕복 일치). ISO 전체 비교에서 3개 파일 외 변경 없음. 원본에 xdelta를 다시 적용한 결과는 테스트 ISO와 SHA-256이 일치합니다.

## 다운로드 및 적용

첨부 파일은 `Kitaro_Ibun_Youkai_Kitan_PS2_KO_v1.0.2.xdelta` 하나(413,626바이트)입니다. 수정되지 않은 일본판 **SLPM-65337** 원본 ISO에 적용하세요. 이전 한글판에 덧씌우지 마세요. ISO와 추출 바이너리는 배포하지 않습니다.

| 항목 | 값 |
| --- | --- |
| 원본 ISO 크기 | 2,316,861,440바이트 |
| 원본 MD5 | `a3ba2caa94c05e13aa0191f6850367b8` |
| 원본 SHA-256 | `89ce33d0bf65b33f1fdd9ef3bae28a9700a4b0e700199f73d45633d620ad1186` |
| 패치 SHA-256 | `21a7fc0f1a89b0576b6cdfb2135d735f61ffc6fce242d6481bef3abc1b6d696c` |
| 결과 ISO SHA-256 | `77cc14cdeea44274e6b6b89e0b37dd0ae11504876561aff510f10d7200b4acf8` |

적용 방법은 [README](https://github.com/snake759494/gegege-no-kitaro-ibun-youkai-kitan-korean-patch/blob/v1.0.2/README.md), 확인 범위는 [실행 기록](https://github.com/snake759494/gegege-no-kitaro-ibun-youkai-kitan-korean-patch/blob/v1.0.2/runtime_test.md)에 있습니다. 기존 상태 저장은 옛 리소스를 보유할 수 있으므로 새 ISO로 부팅해 메모리 카드 저장을 이용하세요.
