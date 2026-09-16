# v1.0.3 — UI 이미지 재적용 및 검증 강화

사용자가 정상 진행을 확인한 `Kitaro_KR_UI_candidate_20260916.iso`와 동일한 결과를 만드는 패치입니다.

- 기존 대사·글꼴·이름표 한글화를 유지하고, D_SYS 스프라이트 99장과 D_BG 메뉴 배경 9장의 한글화를 재적용했습니다.
- 원본 지문, 컨테이너 경계, 파일 크기, 메타데이터 및 지정 픽셀 밖 변경을 검사합니다. 기존 ISO 재사용, 팔레트 캐시 충돌, 일부 4bpp 해석 및 검사 실패 종료 코드 문제를 수정했습니다.
- 이미지 안전성 회귀 검사 11개 통과. ISO 전체 비교에서 지정한 5개 파일 밖 변경 0. xdelta 재적용 결과가 테스트 ISO와 일치합니다.
- PCSX2 v2.9.52에서 새 게임 → 병원 탐색 및 이동·회전을 확인했고, 사용자가 후보판의 정상 진행을 확인하여 공개를 요청했습니다. 기존 프리징의 근본 원인은 미확정입니다. 4가지 구성의 통제 비교, 전체 이미지 실행, 전체 챕터 완주 및 실기는 미검증입니다.

## 다운로드 및 적용

첨부 `Kitaro_Ibun_Youkai_Kitan_PS2_KO_v1.0.3.xdelta` (664,194바이트)을 수정되지 않은 일본판 **SLPM-65337** 원본 ISO에 적용하세요. 이전 한글판에 덧씌우지 마세요. ISO와 추출 바이너리는 배포하지 않습니다.

| 항목 | 값 |
| --- | --- |
| 원본 ISO 크기 | 2,316,861,440바이트 |
| 원본 MD5 | `a3ba2caa94c05e13aa0191f6850367b8` |
| 원본 SHA-256 | `89ce33d0bf65b33f1fdd9ef3bae28a9700a4b0e700199f73d45633d620ad1186` |
| 패치 SHA-256 | `0fc656455dbb51761598a81126d0159d92dcc1efdba38cdc5b396ff88c389110` |
| 결과 ISO SHA-256 | `b673e0832b9bd4e23ddf6527b836e8c90bab81e04b05502900bd4b7e6a9a9ca3` |

[적용 방법](https://github.com/snake759494/gegege-no-kitaro-ibun-youkai-kitan-korean-patch/blob/v1.0.3/README.md) · [검증 범위](https://github.com/snake759494/gegege-no-kitaro-ibun-youkai-kitan-korean-patch/blob/v1.0.3/IMAGE_VALIDATION.md)

기존 상태 저장에는 옛 리소스가 남을 수 있으므로 새 ISO로 부팅하고 메모리 카드 저장으로 이어 하세요.
