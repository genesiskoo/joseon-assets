from pathlib import Path
exec(Path(__file__).with_name('implement558.py').read_text(encoding='utf-8').split("write('core/combat_trace.gd'")[0])
write('tools/combat_trace_compare.py',Path(__file__).with_name('combat_trace_compare_v2.py').read_text(encoding='utf-8'))
def doc(text):
    text = replace(text, '실제 phase argv·engine/launcher PID·원문 SHA를 확인하고 해당 trace 경로에서 모든 실제 level/attempt를 읽는다.', '실제 phase argv의 --e2e/skip/FixedFps와 메타를 대조하고, 원본 raw ENV의 engine PID·user CLI, FILE saved/path/level/attempt와 모든 ATTEMPT·TRIES를 저장 trace와 연결한다. 원문 SHA/바이트 수를 확인하고 첫 패배·추가 시도의 파일이 양쪽에서 빠져도 누락을 실패로 잡는다. 정상 완료는 두 레벨의 TRIES가 필요하며 중단 phase의 미완료 레벨과 빈 outcome은 별도로 표시한다.')
    text = replace(text, 'trace 폴더만 주면 provenance 미제공으로 명시한다.', 'trace 폴더만 주면 provenance 미제공·실제 판 전체 보존 미검증으로 명시한다.')
    text = replace(text, '최초 관측 차이와 원인 확정을 구분한다.', '최초 event/tick/state 차이는 float-only 시계 관측과 별도 표기한다. 정확한17소수 시계 비교는 유지하며 앞선 epoch float 차이만을 전투 최초 원인으로 표시하지 않는다. 최초 관측 차이와 원인 확정을 구분한다.')
    return text
edit('docs/design/combat_trace_558.md',doc)
print('558 raw manifest provenance and separate first boundaries applied')
