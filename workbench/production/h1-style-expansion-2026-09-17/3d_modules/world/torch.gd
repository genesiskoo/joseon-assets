class_name Torch
extends Node3D
## Torch — 석실 횃불 (design/dungeon.md §6). 받침 상자 + 발광 불꽃 구 + 주황 OmniLight, 깜빡임.
## 왜 씬 파일 없이 코드로 만드나: DungeonBuilder가 층마다 수십 개를 절차 배치하고, 모양은 뒤에 Meshy 소품 GLB로 통째 교체될 임시 형태라
##   .tscn을 유지할 가치가 없다. 빛(OmniLight)만이 이 노드의 본질이고 메시는 껍데기.
## 정면 +Z = 바닥(방 안쪽) 방향. DungeonBuilder가 벽 면에 붙여 놓는다.

@export var light_energy: float = 3.2
@export var light_range: float = 7.0
@export var light_color: Color = Color(1.0, 0.62, 0.3)
## 깜빡임 위상 — 횃불끼리 같이 안 깜빡이게 배치 때 다르게 준다.
var seed_offset: float = 0.0

var _light: OmniLight3D
var _flame: MeshInstance3D
var _t: float = 0.0


func _ready() -> void:
	var bracket := MeshInstance3D.new()
	bracket.name = "Bracket"
	var bm := BoxMesh.new()
	bm.size = Vector3(0.14, 0.2, 0.14)
	bracket.mesh = bm
	var iron := StandardMaterial3D.new()
	iron.albedo_color = Color(0.12, 0.11, 0.1)
	iron.roughness = 0.9
	bracket.material_override = iron
	bracket.position = Vector3(0, -0.1, 0)
	add_child(bracket)

	_flame = MeshInstance3D.new()
	_flame.name = "Flame"
	var fm := SphereMesh.new()
	fm.radius = 0.1
	fm.height = 0.26
	_flame.mesh = fm
	var fire := StandardMaterial3D.new()
	fire.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	fire.albedo_color = Color(1.0, 0.6, 0.2)
	fire.emission_enabled = true
	fire.emission = Color(1.0, 0.55, 0.18)
	fire.emission_energy_multiplier = 4.0   # 글로우 임계(1.0) 위 → 번짐
	_flame.material_override = fire
	_flame.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	_flame.position = Vector3(0, 0.13, 0)
	add_child(_flame)

	_light = OmniLight3D.new()
	_light.name = "Light"
	_light.light_color = light_color
	_light.light_energy = light_energy
	_light.omni_range = light_range
	_light.omni_attenuation = 1.2   # 1.4는 웅덩이가 너무 좁았음(1층 실측) — 키프레임은 3~4칸 반경으로 퍼진다
	_light.shadow_enabled = false   # 수십 개라 그림자는 끔 — 플레이어 빛만 그림자
	_light.position = Vector3(0, 0.15, 0.25)  # 벽에서 살짝 떨어져 벽면도 밝힌다
	add_child(_light)


func _process(delta: float) -> void:
	_t += delta
	# 두 주파수 곱 + 잔떨림 = 규칙적이지 않은 촛불 흔들림
	var f := 0.84 + 0.16 * sin(_t * 9.0 + seed_offset) * sin(_t * 4.3 + seed_offset * 0.7) + 0.05 * sin(_t * 23.0 + seed_offset)
	_light.light_energy = light_energy * f
	_flame.scale = Vector3(1.0, 0.85 + 0.25 * f, 1.0)
