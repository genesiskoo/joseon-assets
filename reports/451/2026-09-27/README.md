# #451 가방 부적 표적 모드 검수 원본

게임 후보 `9c281bf4ebd568d67c1098494ff62629567633b9` / `codex/451-bag-talisman-target`, 기준 main `eaf57bc2`.

전체 결과는 `verification.json`. 단위 53종·설정 재실행 2단계·Godot 도구 4종·Python 도구 10종, 러너 판정 5/5, 전체 플레이 98/98종·5256검사 PASS. 실제 입력 별도 headless/창모드 각각73검사 PASS. 최종 raw SCRIPT ERROR/ERROR0.

`451_unit_100554.log`·`451_all_100757.log`·`451_target_100522.log`·`451_windowed_100656.log`는 원본 stdout/stderr 통합 로그. `initial_runner_output.txt`·`451_target_100315.log`는 초기 검수 무대 실패 원본이다. `post_validation_whitespace.json`은 통과 뒤 대본 끝 빈 줄 하나만 제거한 기록이며 실행 코드 변경 없음.

`captures_before.json`·`captures_after.json`·`baseline_restore.json`은 같은 구도 캡처와 후보 생산 파일의 복원을 검증한다. PNG는 원본, JPG는1280×720/각300KB미만이다. 배포용 여섯 장과 QA는 `docs/art/451_bag_talisman_target/`. `input_review.md`는 별도 읽기 전용 입력 경계 검수. 새 생성·크레딧 사용 없음. 후보는 아직 main 미착륙·미push.
