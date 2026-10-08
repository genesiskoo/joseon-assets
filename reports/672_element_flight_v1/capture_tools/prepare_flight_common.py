from pathlib import Path
base=Path('._tmp/672_element_flight_v1'); base.mkdir(exist_ok=True)
source=Path('._tmp/634_status_structure_v1/capture_status.gd').read_text(encoding='utf-8')
common=source[:source.index('func _capture()')]
common=common.replace('#634','#672').replace('VIDEO634','VIDEO672').replace('video634','video672')
common=common.replace('var phase := "before"','var phase := "before"\nvar status_events := []')
common=common.replace('"initial_rng": str(n._rng.state), "born_frame": frame_no', '"initial_rng": str(n._rng.state), "born_frame": frame_no, "born_engine_frame": Engine.get_process_frames(), "initial_velocity": str(n.velocity), "initial_speed": n.velocity.length()')
common=common.replace('"radius": n.burst_radius(), "mods": n.mods.duplicate(true)', '"radius": n.burst_radius(), "mods": n.mods.duplicate(true), "base_speed": n.def.throw_speed, "base_range": n.def.throw_range, "base_dot_sec": n.def.dot_sec, "base_status_sec": n.def.status_sec')
common=common.replace('"share": n.share, "accuracy": n.accuracy', '"share": n.share, "accuracy": n.accuracy, "native_lifetime": n.lifetime')
body=Path('._tmp/672_element_flight_v1/capture_body.txt')
body.write_text('pending body construction\n',encoding='utf-8',newline='\n')
(base/'capture_common.txt').write_text(common,encoding='utf-8',newline='\n')
print('common prepared; no capture execution yet')