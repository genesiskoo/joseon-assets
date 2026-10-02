from pathlib import Path
exec(Path(__file__).with_name('implement558.py').read_text(encoding='utf-8').split("write('core/combat_trace.gd'")[0])
edit('core/combat_trace.gd',lambda s: replace(s, 'static func _body_state(key: String) -> Dictionary:', '''## 예약 타깃과 현재 Combat.target이 다를 수 있으므로 실제 e의 위치·거리를 별도로 읽는다.
static func attack_target(source: Node, target: Node) -> Dictionary:
\tvar out := {"target": body_key(target), "valid": is_instance_valid(target)}
\tif not is_instance_valid(target) or not target.is_inside_tree():
\t\treturn out
\tif target is Node3D:
\t\tout["position"] = vector(target.global_position)
\t\tvar key := body_key(source)
\t\tvar body: Node3D = _bodies[key].body.get_ref() if _bodies.has(key) else null
\t\tif is_instance_valid(body) and body.is_inside_tree():
\t\t\tvar flat: Vector3 = target.global_position - body.global_position
\t\t\tflat.y = 0.0
\t\t\tout["distance"] = exact(flat.length())
\tif "state" in target:
\t\tout["state"] = int(target.get("state"))
\tif target is CollisionObject3D:
\t\tout["collision_layer"] = target.collision_layer
\t\tout["collision_mask"] = target.collision_mask
\treturn out


static func _body_state(key: String) -> Dictionary:'''))
edit('actors/player_combat.gd',lambda s: replace(s, '{"target": TRACE.body_key(e if is_instance_valid(e) else null), "check_range":', '{"actual_target": TRACE.attack_target(self, e if is_instance_valid(e) else null), "check_range":'))
print('FIX558 actual callback target position/range evidence added')
