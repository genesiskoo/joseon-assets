from pathlib import Path
exec(Path(__file__).with_name('implement558.py').read_text(encoding='utf-8').split("write('core/combat_trace.gd'")[0])
edit('tests/test_balance_rng.gd',lambda text: replace(text,
    '\tDamageCalc.sure_hit = sure0\n\tawait create_timer(1.2).timeout',
    '''\tDamageCalc.sure_hit = sure0
\t# 실제 Main 준비 검사가 켠 Ogg 루프도 시험 종료 전에 정리한다.
\t# audio 스레드의 playback 참조를 남긴 채 quit하지 않으며 실전 오디오 정책은 바꾸지 않는다.
\tfor child in root.get_node("Audio").get_children():
\t\tif child is AudioStreamPlayer:
\t\t\tchild.stop()
\tawait create_timer(1.2).timeout'''))
print('558 live-Main unit playback teardown applied')
