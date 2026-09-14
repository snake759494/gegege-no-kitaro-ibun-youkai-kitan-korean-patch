PS2 일본판 **ゲゲゲの鬼太郎 異聞妖怪奇譚 (SLPM-65337)**용 비공식 한글패치 v1.0.0 정식 배포입니다. 게임 내 텍스트 13,458개 전부, 대사 글꼴(한글 2,350자), 캐릭터 이름표 138장, 전투·메뉴 UI 스프라이트 99장(챕터 타이틀 44장 포함), 메뉴 배경 9장을 한글화했습니다.

**첨부 파일은 `Kitaro_Ibun_Youkai_Kitan_PS2_KO_v1.0.0.xdelta` 하나입니다. 원본 및 패치 적용 ISO는 제공하지 않습니다.** 자동 Source code 압축본에는 공개 소스·번역·검증 자료가 들어 있습니다.

| 확인 대상 | 값 |
| --- | --- |
| 원본/결과 ISO 크기 | 2,316,861,440 바이트 |
| 원본 ISO MD5 | `a3ba2caa94c05e13aa0191f6850367b8` |
| 원본 ISO SHA-256 | `89ce33d0bf65b33f1fdd9ef3bae28a9700a4b0e700199f73d45633d620ad1186` |
| xdelta SHA-256 | `1a75d802c950f408527744d1826d6f7bbb4e6877f9a656cabcf3d36cd9533c52` |
| 결과 ISO SHA-256 | `5f6fee80422be8ce602658b9dbce384240e932451caded9853bdac16d514b208` |

해시가 일치하는 수정되지 않은 일본판 ISO에 xdelta3 Apply Patch로 적용하고 결과 해시를 확인하세요. 이전 한글 ISO에 덧씌우지 마세요. 원본 ISO로 만든 상태 저장 대신 새로 부팅하고 메모리 카드 저장을 쓰세요(세이브 데이터는 호환됩니다). [적용 방법 및 대상 안내](https://github.com/snake759494/gegege-no-kitaro-ibun-youkai-kitan-korean-patch#readme)를 참고하세요.

번역 왕복·커버리지·잔류 일본어·레이아웃·제어 코드·용어·용량 검사, 이미지 컨테이너 무손상 검사, xdelta 왕복 검사를 통과했고 일본어/한국어 13,458쌍을 한 줄씩 정독 검수했습니다([검수 기록](https://github.com/snake759494/gegege-no-kitaro-ibun-youkai-kitan-korean-patch/blob/main/REVIEW.md)). 게임 로고·요괴타임스 로고는 원본 아트를 보존했고, `D_EFF.BIN`의 아이템 효과 라벨과 RenderWare 텍스처의 일본어는 이번 판에서 바꾸지 않았습니다. PCSX2 인게임 확인 범위와 미확인 범위는 [runtime_test.md](https://github.com/snake759494/gegege-no-kitaro-ibun-youkai-kitan-korean-patch/blob/main/runtime_test.md)에 구분했습니다. 전체 완주와 실기 검증은 미수행입니다.
