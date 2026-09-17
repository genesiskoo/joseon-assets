class_name ModelDef
extends Resource
## ModelDef — 배우(도호·적·NPC) 하나의 3D 모델 반입 계약 (D-067, design/art_3d_pipeline.md §2).
## 왜 리소스인가: "파일 자리·크기·정면·애니 이름"은 아트가 도착한 뒤 검수하며 만지는 값이라 코드가 아니라 데이터(.tres)에 둔다(D-052).
## 파일이 없으면 ActorVisual이 플레이스홀더를 유지하므로, 이 리소스는 아트 도착 전에 미리 전부 연결해 둔다 — 반입 = 파일 복사만.

@export var id: String = "doho"
## GLB(또는 glTF/tscn) 경로. 없으면 플레이스홀더.
@export_file("*.glb", "*.gltf", "*.tscn") var scene_path: String = "res://assets/models/doho/doho.glb"

@export_group("보정 (검수 후 손대는 칸)")
@export var scale: float = 1.0
## 발이 땅에 박히거나 뜨면 조정.
@export var y_offset: float = 0.0
## GLB 정면이 +Z가 아니면 보정 (뒤돌아 걸으면 180).
@export var yaw_offset_deg: float = 0.0
## 검수 기준 키(유닛). model_check가 ±15% 밖이면 경고.
@export var target_height: float = 1.7
## 텍스처 nearest 필터 ("픽셀 느낌") — 아트 1차 반입 후 판정.
@export var pixel_filter: bool = false

@export_group("무기 소켓 (§2.6 — 무기는 별도 프롭, 손 본에 붙인다)")
## 무기 GLB/tscn 경로. ""이면 없음(weapon_placeholder가 켜져 있으면 임시 검).
@export_file("*.glb", "*.gltf", "*.tscn") var weapon_scene: String = ""
## 무기 파일이 없을 때 임시 검(회색 칼날)을 붙인다 — 애니 검수용. 진짜 검이 오면 끈다.
@export var weapon_placeholder: bool = false
## 붙일 본 이름. 정확히 없으면 "hand"+"right/r_" 부분 일치로 찾는다(Mixamo/Meshy RightHand, Tripo R_Hand).
@export var weapon_bone: String = "RightHand"
## 손 본 기준 보정 — 위치(유닛)·회전(도)·배율. 리그마다 손 축이 달라 뷰어(--weapon_rot=)로 맞춘 값을 적는다.
@export var weapon_offset_pos: Vector3 = Vector3.ZERO
@export var weapon_offset_rot_deg: Vector3 = Vector3.ZERO
@export var weapon_scale: float = 1.0

@export_group("이동 (art_3d_pipeline §13 — 발 미끄럼 방지)")
## 걷기/달리기 클립이 1배속에서 땅을 가는 속도(유닛/초). model_check가 "지면 속도"로 출력한 값. ActorVisual이 실제 속도 ÷ 이 값으로 재생 배율을 맞춘다.
@export var walk_speed: float = 1.05
@export var run_speed: float = 2.4
## 이 속도(유닛/초) 이상이면 run 클립(있을 때), 아래면 walk.
@export var run_threshold: float = 2.6
## 재생 배율 클램프 — 너무 느리거나 우스꽝스럽게 빠르지 않게.
@export var loco_scale_min: float = 0.75
@export var loco_scale_max: float = 1.8

@export_group("스프링본 (art_3d_pipeline §12 — 허리끈 꼬리·술 흔들림)")
## 흔들 뼈 사슬의 뿌리·끝 본 이름(같은 인덱스가 한 쌍). `tools/blender/rig_fix.py`가 만든 SashTail1→SashTail2 등. 비어 있으면 스프링본 없음.
@export var spring_roots: PackedStringArray = []
@export var spring_ends: PackedStringArray = []
## 원래 자세로 돌아가는 힘 / 움직임 감쇠 / 아래로 처지는 속도 (SpringBoneSimulator3D).
@export var spring_stiffness: float = 1.2
@export var spring_drag: float = 0.4
@export var spring_gravity: float = 0.8

@export_group("타격 (combat_v2.md §6)")
## 공격 클립별 타격 시각 = 클립 길이 대비 0~1 (오른손 속도 피크). `model_check`가 클립마다 계산해 출력한 값을 적는다. 없는 클립은 기본값.
## attack, attack2, attack3… 여러 클립이 있으면 ActorVisual이 무작위로 고른다(같은 클립 연속 금지).
@export var attack_impact: Dictionary = {}
@export_range(0.05, 0.95) var attack_impact_default: float = 0.45

@export_group("애니 이름 (부분 일치·동의어 허용, §2.3)")
@export var anim_idle: String = "idle"
@export var anim_walk: String = "walk"
@export var anim_run: String = "run"
@export var anim_attack: String = "attack"
@export var anim_hit: String = "hit"
@export var anim_die: String = "die"


func exists() -> bool:
	return scene_path != "" and ResourceLoader.exists(scene_path)


## 동작 키(idle/walk/attack/hit/die) → 이 모델에서 원하는 클립 이름.
func anim_name(kind: String) -> String:
	match kind:
		"idle": return anim_idle
		"walk": return anim_walk
		"run": return anim_run
		"attack": return anim_attack
		"hit": return anim_hit
		"die": return anim_die
	return kind
