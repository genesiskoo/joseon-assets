class_name UiSkin
extends RefCounted
## UiSkin — 창틀·버튼·슬롯 스킨 한 곳 (design/ui_v2.md §5, 보드 #63).
##
## 왜 이 구조인가: v2 UI는 전부 `_draw`로 그리는 즉시 모드다(Control 테마·StyleBox 노드를 안 쓴다).
## 그래서 스킨을 입히는 가장 싼 길은 "그리기 헬퍼 3개를 한 곳으로 모으고, 그 안에서 텍스처가 있으면 9슬라이스로 그리는 것".
## Theme 리소스로 갈아엎는 대안은 창 3개·HUD를 전부 Control 트리로 다시 짜야 해서 기각했다.
## 텍스처가 없으면 예전 그대로 단색 사각형으로 그린다 — 자산이 아직 안 온 창도 깨지지 않는다(테스트·CI 포함).
##
## 파일 자리: `res://assets/sprites/ui/skin/{panel,button,slot}.png` (9슬라이스, 가장자리 여백은 MARGIN).

const DIR := "res://assets/sprites/ui/skin/"
## 부품별 고정 조각. 새 창판의 현판 자리만 43px, 모서리는 16px (#87 manifest).
const MARGIN := {
	"panel": [16.0, 43.0, 16.0, 15.0],
	"button": [9.0, 9.0, 9.0, 9.0],
	"title_tab": [8.0, 8.0, 8.0, 8.0],
	"slot": [8.0, 8.0, 8.0, 8.0],
}

## ── 팔레트 (#421) — 창·HUD·툴팁이 손으로 베껴 쓰던 Color(…) 중 **같은 값끼리만** 이름 하나.
## 값이 조금이라도 다른 색(흰 글자 5단·회색 4단…)은 합치지 않았다 — 합치면 그림이 바뀐다(PD 판정 뒤 후속).
## HUD 안에서만 되풀이되는 글자 색은 hud.gd 지역 상수. UI는 이펙트 오토로드(Vfx) 상수에 기대지 않는다 — 먹색은 여기 INK.
const INK := Color(0.08, 0.07, 0.09)   # 구슬 바탕 — 먹 (Vfx.INK와 같은 값, 일부러 따로 둔다)
const FRAME := Color(0.45, 0.38, 0.25)   # 놋쇠 테 — 칸·바·상점 줄·서낭단 줄
const FRAME_HIGHLIGHT := Color(0.95, 0.8, 0.35)   # 금빛 강조 테 — 우클릭 스킬·현재 서낭단
const SLOT_RIM := Color(0.36, 0.38, 0.40)   # 보통 등급 아이템 칸 테(등급이 있으면 등급 색)
const COIN := Color(0.95, 0.8, 0.3)   # 「엽전 n」 글자 — HUD·상점(살 수 있을 때)
const PRICE := Color(0.95, 0.80, 0.44)   # 엽전 수·값 — 가방·툴팁
const XP_BAR := Color(0.75, 0.6, 0.2)   # 경험치 바 채움 — HUD·캐릭터 창
const TITLE := Color(0.95, 0.88, 0.7)   # 창 제목·HUD 「Lv n」
const TEXT := Color(0.88, 0.86, 0.8)   # 본문 기본 — PanelUi.text 기본값
const TEXT_STAT := Color(0.88, 0.87, 0.82)   # 스탯·툴팁 기본 줄
const TEXT_BRIGHT := Color(0.95, 0.93, 0.88)   # 가장 밝은 글자 — 커서 이름·보통 피해 숫자
const SKILL_NAME := Color(0.95, 0.92, 0.85)   # 배운 스킬 이름 — HUD·스킬 창
const TEXT_SOFT := Color(0.7, 0.66, 0.58)   # 부제·현재 서낭단 줄
const TEXT_MUTED := Color(0.55, 0.52, 0.46)   # 안 배운 스킬의 F키·점수
const TEXT_DIM := Color(0.45, 0.42, 0.38)   # 비활성 버튼 글자·시작 화면 바닥글
const ROW := Color(0.13, 0.12, 0.11)   # 목록 줄 바탕 — 상점·서낭단
const ROW_HOVER := Color(0.2, 0.17, 0.12)   # 목록 줄 호버
const BACK_DARK := Color(0.12, 0.11, 0.1)   # 바 바탕·비활성 버튼 몸통(텍스처 없을 때)

static var _box: Dictionary = {}
static var _checked: Dictionary = {}


## 이름에 맞는 StyleBoxTexture (없으면 null). 한 번 찾아보고 결과를 기억한다 — 매 프레임 ResourceLoader를 때리지 않게.
static func _style(name: String) -> StyleBoxTexture:
	if _checked.has(name):
		return _box.get(name)
	_checked[name] = true
	var path := DIR + name + (".svg" if name == "title_tab" else ".png")
	if not ResourceLoader.exists(path):
		_box[name] = null
		return null
	var tex := load(path) as Texture2D
	if tex == null:
		_box[name] = null
		return null
	var sb := StyleBoxTexture.new()
	sb.texture = tex
	var margins: Array = MARGIN.get(name, [8.0, 8.0, 8.0, 8.0])
	for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
		sb.set_texture_margin(side, float(margins[side]))
	sb.axis_stretch_horizontal = StyleBoxTexture.AXIS_STRETCH_MODE_STRETCH
	sb.axis_stretch_vertical = StyleBoxTexture.AXIS_STRETCH_MODE_STRETCH
	_box[name] = sb
	return sb


## 스킨 자산이 하나라도 있는가 (테스트·진단용).
static func has_skin() -> bool:
	return _style("panel") != null


static func title_tab(ci: CanvasItem, r: Rect2) -> void:
	var sb := _style("title_tab")
	if sb:
		sb.draw(ci.get_canvas_item(), r)


## 창틀. 텍스처가 없으면 예전 색(어두운 판 + 금빛 테두리).
static func panel(ci: CanvasItem, r: Rect2) -> void:
	# 작은 NPC 이름표에는 43px 현판 레일을 압축하지 않는다. 먹빛 판과 가는 놋쇠 선만 공유.
	if r.size.y < 96.0 or r.size.x < 160.0:
		ci.draw_rect(r, Color(0.055, 0.055, 0.052, 0.96))
		ci.draw_rect(r, Color(0.35, 0.31, 0.23, 0.85), false, 1.0)
		return
	var sb := _style("panel")
	if sb:
		# 새 원본 중앙은 이미 낮은 채도·명도이므로 색 보정 없이 쓴다.
		sb.modulate_color = Color.WHITE
		sb.draw(ci.get_canvas_item(), r)
		return
	ci.draw_rect(r, Color(0.07, 0.06, 0.08, 0.94))
	ci.draw_rect(r, Color(0.55, 0.45, 0.28), false, 2.0)


## 버튼. state: 0 기본 · 1 호버 · 2 비활성. 텍스처는 한 장을 쓰고 상태는 색으로 구분한다(자산 3배 생성 회피).
static func button(ci: CanvasItem, r: Rect2, state: int) -> void:
	var sb := _style("button")
	if sb:
		var tints: Array[Color] = [Color(1, 1, 1), Color(1.25, 1.2, 1.05), Color(0.45, 0.44, 0.42)]
		var tint: Color = tints[clampi(state, 0, 2)]
		sb.modulate_color = tint
		sb.draw(ci.get_canvas_item(), r)
		return
	var bodies: Array[Color] = [Color(0.22, 0.19, 0.13), Color(0.35, 0.3, 0.18), BACK_DARK]
	var body: Color = bodies[clampi(state, 0, 2)]
	ci.draw_rect(r, body)
	ci.draw_rect(r, Color(0.6, 0.5, 0.3) if state != 2 else Color(0.3, 0.28, 0.24), false, 1.0)


## 격자 한 칸(가방·벨트·장비). 안쪽은 비워 둔다 — 아이템 아이콘이 그 위에 온다.
static func slot(ci: CanvasItem, r: Rect2, highlight: bool = false) -> void:
	var sb := _style("slot")
	if sb:
		sb.draw(ci.get_canvas_item(), r)
		if highlight:
			ci.draw_rect(r, Color(0.95, 0.8, 0.35, 0.9), false, 1.5)
		return
	ci.draw_rect(r, Color(0.14, 0.12, 0.11))
	ci.draw_rect(r, FRAME_HIGHLIGHT if highlight else FRAME, false, 1.5 if highlight else 1.0)


## 아이템 전용 오목한 면. 목재 슬롯은 스킬/초상에 남기고 가방 내부의 반복 장식만 없앤다 (#101).
const ITEM_EMPTY := Color(0.055, 0.055, 0.052)
const ITEM_OCCUPIED := Color(0.105, 0.12, 0.135)
enum DropState { VALID, SWAP, INVALID }


static func item_slot(ci: CanvasItem, r: Rect2, occupied: bool = false, rim: Color = SLOT_RIM) -> void:
	ci.draw_rect(r, ITEM_OCCUPIED if occupied else ITEM_EMPTY)
	ci.draw_rect(r.grow(-0.5), rim if occupied else Color(0.16, 0.165, 0.16), false, 1.0)


## 호버/커서 선택은 흰 귀퉁이, 등급은 바깥 선. 마법 청색·희귀 황색과 의미가 겹치지 않는다.
static func item_focus(ci: CanvasItem, r: Rect2, alpha: float = 1.0) -> void:
	var inner := r.grow(-3.0)
	var color := Color(0.88, 0.90, 0.88, alpha)
	for direction in [Vector2(1, 1), Vector2(-1, 1), Vector2(1, -1), Vector2(-1, -1)]:
		var corner := inner.position + Vector2(inner.size.x if direction.x < 0 else 0.0, inner.size.y if direction.y < 0 else 0.0)
		ci.draw_line(corner, corner + Vector2(7 * direction.x, 0), color, 1.5)
		ci.draw_line(corner, corner + Vector2(0, 7 * direction.y), color, 1.5)


## 놓기 상태는 바탕 위/아이콘 아래. 색 외에 체크·교환 화살표·X로도 구별한다.
static func item_drop(ci: CanvasItem, r: Rect2, state: DropState) -> void:
	var colors: Array[Color] = [Color(0.42, 0.78, 0.52), Color(0.86, 0.71, 0.36), Color(0.90, 0.39, 0.34)]
	var color: Color = colors[state]
	var inner := r.grow(-2.0)
	ci.draw_rect(inner, Color(color, 0.20))
	ci.draw_rect(inner, color, false, 2.0)
	var at := Vector2(inner.position.x + 5, inner.end.y - 13)
	match state:
		DropState.VALID:
			ci.draw_line(at + Vector2(0, 5), at + Vector2(4, 9), color, 2.0)
			ci.draw_line(at + Vector2(4, 9), at + Vector2(12, 0), color, 2.0)
		DropState.SWAP:
			ci.draw_line(at + Vector2(0, 2), at + Vector2(12, 2), color, 1.5)
			ci.draw_line(at + Vector2(12, 2), at + Vector2(8, -1), color, 1.5)
			ci.draw_line(at + Vector2(0, 8), at + Vector2(12, 8), color, 1.5)
			ci.draw_line(at + Vector2(0, 8), at + Vector2(4, 11), color, 1.5)
		DropState.INVALID:
			ci.draw_line(at, at + Vector2(10, 10), color, 2.0)
			ci.draw_line(at + Vector2(10, 0), at + Vector2(0, 10), color, 2.0)


## 구슬 유리 껍데기 — 채움(피·도력) 위에 겹쳐 덮는다. 텍스처가 없으면 아무것도 안 그린다(기존 테두리·하이라이트가 대신).
static func orb_glass(ci: CanvasItem, center: Vector2, radius: float) -> bool:
	var path := DIR + "orb.png"
	if not _checked.has("orb"):
		_checked["orb"] = true
		_box["orb"] = load(path) if ResourceLoader.exists(path) else null
	var tex: Texture2D = _box.get("orb")
	if tex == null:
		return false
	ci.draw_texture_rect(tex, Rect2(center - Vector2(radius, radius), Vector2(radius, radius) * 2.0), false, Color(1, 1, 1, 0.95))
	return true


## H1·A 원화는 알파 경계를 한 번만 읽고, 해당 텍스처에만 선형 필터를 적용한다 (#93·#439).
static var _item_art: Dictionary = {}

## 승인 물약의 효능 표시비율. 알파 여백 제거 뒤 적용하며 등급/tier와 무관하다 (#548).
const ITEM_DISPLAY_SCALES := {
	"res://assets/sprites/ui/icons_a/items/hp_potion.png": 0.75,
	"res://assets/sprites/ui/icons_a/items/mp_potion.png": 0.75,
	"res://assets/sprites/ui/icons_a/items/hp_potion_2.png": 62.0 / 72.0,
	"res://assets/sprites/ui/icons_a/items/mp_potion_2.png": 62.0 / 72.0,
}



## 실제 그림을 콘텐츠 영역에 비율 보존해 맞춘다. 기존 픽셀 아이콘 경로는 유지한다.
static func item_icon(ci: CanvasItem, r: Rect2, tex: Texture2D, alpha: float = 1.0, padding: float = 8.0) -> bool:
	if tex == null:
		return false
	if tex.resource_path.begins_with("res://assets/sprites/ui/icons_h1/") or tex.resource_path.begins_with("res://assets/sprites/ui/icons_a/"):
		if not _item_art.has(tex.resource_path):
			var source_image := tex.get_image()
			var region := Rect2(source_image.get_used_rect())
			var filtered := CanvasTexture.new()
			filtered.diffuse_texture = tex
			filtered.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
			_item_art[tex.resource_path] = {"texture": filtered, "region": region}
		var art: Dictionary = _item_art[tex.resource_path]
		var region: Rect2 = art.region
		if region.size.x <= 0.0 or region.size.y <= 0.0:
			return false
		var inner := r.grow(-padding)
		var scale_factor: float = minf(inner.size.x / region.size.x, inner.size.y / region.size.y)
		var size := region.size * maxf(scale_factor, 0.0) * float(ITEM_DISPLAY_SCALES.get(tex.resource_path, 1.0))
		var box := Rect2(inner.position + (inner.size - size) * 0.5, size)
		ci.draw_texture_rect_region(art.texture, box, region, Color(1, 1, 1, alpha))
		return true
	var side: float = minf(r.size.x, r.size.y) * 0.8
	var box := Rect2(r.position + (r.size - Vector2(side, side)) * 0.5, Vector2(side, side))
	ci.draw_texture_rect(tex, box, false, Color(1, 1, 1, alpha))
	return true


## 타이틀/시스템 메뉴의 먹빛 화면 덮개. opacity만 달리 쓰고 색을 공유한다 (#156).
static func screen_backdrop(ci: CanvasItem, rect: Rect2, opacity: float = 1.0) -> void:
	ci.draw_rect(rect, Color(0.03, 0.03, 0.04, opacity))
