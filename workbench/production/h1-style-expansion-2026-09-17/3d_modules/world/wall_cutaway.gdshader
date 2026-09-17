shader_type spatial;
render_mode cull_back, depth_draw_opaque;

// 벽 컷어웨이 (디아2식): 카메라와 플레이어 사이에 끼어 플레이어를 가리는 벽 조각만 반투명(해시 디더)으로.
// 알파 블렌딩 대신 ALPHA_HASH → MultiMesh 정렬 문제 없음. uniform은 DungeonLevel이 매 프레임 갱신.
uniform vec4 albedo : source_color = vec4(0.42, 0.40, 0.44, 1.0);
// 타일 킷 벽(GLB)의 텍스처 — DungeonBuilder가 material_override로 얹을 때 넘긴다. 박스 플레이스홀더는 use_tex=false.
uniform sampler2D albedo_tex : source_color, hint_default_white;
uniform bool use_tex = false;
uniform vec3 player_pos = vec3(0.0);
uniform vec3 cam_forward = vec3(0.0, -0.577, -0.577); // 카메라 → 씬 방향(정규화)
uniform float cut_radius : hint_range(0.5, 6.0) = 2.4;
uniform float cut_alpha : hint_range(0.0, 1.0) = 0.3;

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	// COLOR = MultiMesh 인스턴스 색(타일 변주·이끼, dungeon.md §6). 인스턴스 색이 없으면 1.
	ALBEDO = albedo.rgb * COLOR.rgb * (use_tex ? texture(albedo_tex, UV).rgb : vec3(1.0));
	ROUGHNESS = 1.0;
	vec3 d = world_pos - player_pos;
	float along = dot(d, cam_forward);            // 음수 = 플레이어보다 카메라 쪽(앞)에 있음
	vec3 lateral = d - cam_forward * along;       // 시선에 수직인 성분 = 화면상 거리
	if (along < -0.4 && length(lateral) < cut_radius) {
		ALPHA = cut_alpha;
		ALPHA_HASH_SCALE = 1.0;
	} else {
		ALPHA = 1.0;
	}
}
