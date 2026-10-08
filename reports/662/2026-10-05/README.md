# #662 기존 BCA 우선 QA 원본

게임 main 기준 `2762068b` → `codex/662-portrait-bca-first`。기존 BCA 우선·BCA 없으면 승인 정지라는 PD 지시의 구현 검증. 신규 원화·루프 생성 없음.

`before/after` = 실제 같은 구도의 게임 PNG 2장씩. `before_e2e_raw/after_e2e_raw` = 창 모드 focused E2E raw. `full_test.raw.log` / `full_e2e_phase_1/2` = 필수 전체 시험 raw. `portrait_hashes_before.json` = 기존 초상70개 해시, 변경 후·전체 시험 후 모두 동일. 전체 GDS97+설정 재시작2/도구23/E2E138 PASS. 검토 JPG4·PD 기록은 게임 `docs/art/662_bca_priority/`와 `docs/design/dialogue_v2.md` §5. 파일별 크기·SHA는 `manifest.json`. 이 커밋은 QA 기록이며 자동 아트 push 대상이 아니다.

합계 6,052,567 bytes, 최대 1,072,058 bytes.

원본 로그·JSON의 줄끝 바이트는 이 폴더 `.gitattributes`로 보존한다. 기록한 SHA는 staged Git blob과도 대조한다.
