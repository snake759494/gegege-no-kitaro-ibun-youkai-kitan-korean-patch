PS2 일본판 **ゲゲゲの鬼太郎 異聞妖怪奇譚 (SLPM-65337)**용 비공식 한글패치 v1.0.1입니다. **v1.0.0에서 프롤로그 탐색 중 문을 열면 게임이 멈추던 문제를 수정했습니다.** 진단 빌드로 원인이 메뉴 배경 파일(`D_BG.BIN`)의 한글화 이미지 9장으로 특정되어 이 파일을 원본으로 되돌렸습니다. 그 외에는 v1.0.0과 같습니다: 게임 내 텍스트 13,458개 전부, 대사 글꼴(한글 2,350자), 캐릭터 이름표 138장, 전투·메뉴 UI 스프라이트 99장(챕터 타이틀 44장 포함). 휴대폰·상점·신문 메뉴 배경에 그려진 라벨은 일본어로 남습니다.

**첨부 파일은 `Kitaro_Ibun_Youkai_Kitan_PS2_KO_v1.0.1.xdelta` 하나입니다. 원본 및 패치 적용 ISO는 제공하지 않습니다.** 자동 Source code 압축본에는 공개 소스·번역·검증 자료가 들어 있습니다.

| 확인 대상 | 값 |
| --- | --- |
| 원본/결과 ISO 크기 | 2,316,861,440 바이트 |
| 원본 ISO MD5 | `a3ba2caa94c05e13aa0191f6850367b8` |
| 원본 ISO SHA-256 | `89ce33d0bf65b33f1fdd9ef3bae28a9700a4b0e700199f73d45633d620ad1186` |
| xdelta SHA-256 | `5109d081f24c7f042308afd13b8e6be5b811064208135c94d7f7632a2c4a17ed` |
| 결과 ISO SHA-256 | `f3d7ba5be2e2718156eb09fa7a575453c829b2da9760b7a11d9ef2a08b3db3c9` |

해시가 일치하는 수정되지 않은 일본판 ISO에 xdelta3 Apply Patch로 적용하고 결과 해시를 확인하세요. 이전 한글 ISO에 덧씌우지 마세요. 원본 ISO로 만든 상태 저장 대신 새로 부팅하고 메모리 카드 저장을 쓰세요(세이브 데이터는 호환됩니다). [적용 방법 및 대상 안내](https://github.com/snake759494/gegege-no-kitaro-ibun-youkai-kitan-korean-patch#readme)를 참고하세요.

번역 왕복·커버리지·잔류 일본어·레이아웃·제어 코드·용어·용량 검사, 이미지 컨테이너 무손상 검사, xdelta 왕복 검사를 통과했고 일본어/한국어 13,458쌍을 한 줄씩 정독 검수했습니다([검수 기록](https://github.com/snake759494/gegege-no-kitaro-ibun-youkai-kitan-korean-patch/blob/main/REVIEW.md)). 게임 로고·요괴타임스 로고는 원본 아트를 보존했고, 메뉴 배경 라벨과 `D_EFF.BIN`의 아이템 효과 라벨과 RenderWare 텍스처의 일본어는 이번 판에서 바꾸지 않았습니다. PCSX2 인게임 확인 범위와 미확인 범위는 [runtime_test.md](https://github.com/snake759494/gegege-no-kitaro-ibun-youkai-kitan-korean-patch/blob/main/runtime_test.md)에 구분했습니다. 전체 완주와 실기 검증은 미수행입니다.
