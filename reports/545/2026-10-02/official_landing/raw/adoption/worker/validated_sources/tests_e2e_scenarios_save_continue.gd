extends E2eScenario
## 저장: X(레벨업)·M(엽전) → 1층 진입 자동 저장 → 새 캐릭터로 지운 뒤 불러오기 → 복원 (design/testing.md §2)


func run() -> void:
	await t.key(KEY_X)
	await t.key(KEY_M)
	Quest.accept(GameState.flags)
	var lv: int = GameState.character.level
	var gold: int = GameState.inventory.gold
	t.check(lv >= 2, "X → 레벨업 (lv %d)" % lv)
	t.check_eq(gold, 500, "M → 엽전 500")
	await t.go_down(1)
	await t.frames(3)
	t.check(SaveSystem.has_save(), "1층 진입 → 저장 파일 존재")
	t.check(SaveSystem.save_path.ends_with("save_e2e.json"), "e2e 전용 저장 경로")
	# 지우고 불러오기
	GameState.new_character()
	t.check_eq(GameState.character.level, 1, "새 캐릭터 lv 1")
	t.check_eq(GameState.inventory.gold, 0, "새 캐릭터 엽전 0")
	var vitals: Dictionary = SaveSystem.load_into_state()
	t.check(not vitals.is_empty(), "불러오기 성공")
	t.check_eq(GameState.character.level, lv, "레벨 복원")
	t.check_eq(GameState.inventory.gold, gold, "엽전 복원")
	t.check_eq(Quest.state(GameState.flags), Quest.ACCEPTED, "퀘스트 플래그 복원")
	t.check(GameState.inventory.equipment.weapon != null and GameState.inventory.equipment.weapon.def.id == "iron_sword", "장비 복원")
	t.check_eq(GameState.max_area_level, AreaDb.level_at(AreaDb.DEFAULT_DUNGEON, 1), "최대 지역 레벨 복원 (흑랑 굴 1층)")
	t.player().combat.recompute_stats()
	await t.shot("loaded")
