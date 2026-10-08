from pathlib import Path
exec(Path(__file__).with_name('implement558.py').read_text(encoding='utf-8').split("write('core/combat_trace.gd'")[0])
edit('core/combat_trace.gd',lambda s: replace(s, 'out["clip_position"] = exact(mixer.current_animation_position)', 'out["clip_position"] = exact(mixer.current_animation_position) if not String(mixer.current_animation).is_empty() else "not_playing"'))
edit('tests/test_combat_trace.gd',lambda s: replace(replace(replace(replace(s, 'const SCENARIO := preload("res://tests/e2e/scenarios/balance_boss.gd")','var _scenario_script: GDScript'), '\tawait process_frame\n\t_directory', '\tawait process_frame\n\t_scenario_script = load("res://tests/e2e/scenarios/balance_boss.gd")\n\t_directory'), 'var scenario := SCENARIO.new()', 'var scenario: RefCounted = _scenario_script.new()'), 'mode + " flush/disable・원 RNG/연결 복원"', 'mode + " flush/disable·원 RNG/연결 복원"'))
print('FIX558 empty animation and deferred test script load')
