| 항목 | 방식 | 폭×높이 px | 최대 면적 px² | 첫 | 등장 | 다 보임 | 보임 | 95% | 절정 | 피해(전부) | 95%−피해 | 절정−피해 | 효과음−절정 | 패스 | 입자 노드/양 | 빛 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| play:hit | Vfx.play | 52×49 | 242 | 0 | 7 | 10 | 20 | 8 | 11 | — | — | — | — | 1 | 0/0 | 1 |
| play:hit_crit | Vfx.play | 78×74 | 544 | 0 | 7 | 10 | 20 | 8 | 11 | — | — | — | — | 1 | 0/0 | 1 |
| play:hit_sparks | Vfx.play | 0×0 | 0 | -1 | -1 | 0 | 0 | -1 | -1 | — | — | — | — | 1 | 1/8 | 0 |
| play:slash_arc | Vfx.play scale=range×0.7 | 95×131 | 794 | 0 | 0 | 13 | 23 | 0 | 0 | — | — | — | — | 1 | 0/0 | 1 |
| basic_attack | 자동공격 1타 | 183×195 | 29110 | 3 | 14 | 8 | 71 | 18 | 18 | 18 | 0 | 0 | 0 | 6 | 1/8 | 1 |
| slash | cast Lv1 | 301×234 | 75625 | 0 | 18 | 22 | 74 | 37 | 39 | 37 | 0 | 2 | -2 | 9 | 2/18 | 2 |
| whirl_lv1 | cast Lv1 | 340×221 | 147580 | 0 | 26 | 15 | 98 | 28 | 33 | 28 | 0 | 5 | -5 | 14 | 1/8 | 2 |
| whirl_lv10 | cast Lv10 | 471×298 | 604092 | 0 | 44 | 5 | 97 | 46 | 48 | 28,44 | 2 | 4 | -4 | 40 | 1/8 | 2 |
| dash_strike | cast Lv1 | 362×306 | 184886 | 0 | 32 | 8 | 85 | 33 | 33 | 33 | 0 | 0 | 0 | 13 | 3/24 | 1 |
| leap_slash | cast Lv1 | 275×276 | 79058 | 0 | 32 | 11 | 97 | 33 | 33 | 33 | 0 | 0 | 0 | 11 | 2/18 | 1 |
| fire_lore | cast Lv1 (비행+터짐) | 210×129 | 37048 | 33 | 19 | 21 | 64 | 53 | 56 | 52 | 1 | 4 | -4 | 10 | 0/0 | 1 |
| ice_lore | cast Lv1 (비행+터짐) | 210×135 | 37963 | 33 | 17 | 21 | 65 | 51 | 55 | 50 | 1 | 5 | -5 | 12 | 0/0 | 1 |
| thunder_lore | cast Lv1 (비행+터짐) | 46×77 | 1218 | 33 | 7 | 7 | 23 | 41 | 46 | 37 | 4 | 9 | -9 | 5 | 0/0 | 1 |
| salpuri | cast Lv1 (제자리) | 142×129 | 909 | 0 | 8 | 17 | 45 | 12 | 15 | — | — | — | -15 | 2 | 0/0 | 0 |
| seal_array | cast Lv1 (화염 진) | 293×170 | 116050 | 33 | 0 | 65 | 65 | 38 | 45 | 93 | -55 | -48 | -12 | 7 | 1/10 | 1 |
| blink | cast Lv1 (3u) | 261×151 | 345 | 0 | 9 | 15 | 45 | 13 | 15 | — | — | — | -15 | 4 | 2/16 | 0 |
| mana_shield | cast Lv1 | 148×85 | 290 | 33 | 8 | 16 | 29 | 46 | 48 | — | — | — | -15 | 1 | 0/0 | 0 |
| kill_basic | 자동공격 막타(생명 1) | 198×196 | 30518 | 3 | 14 | 9 | 119 | 18 | 18 | 18 | 0 | 0 | 0 | 9 | 2/16 | 1 |
| kill_slash | 참격 막타(생명 1) | 301×234 | 91302 | 0 | 37 | 10 | 122 | 37 | 39 | 37 | 0 | 2 | -2 | 18 | 2/16 | 2 |
| kill_bisect | 평타 막타 + 두 동강(bisect_pct 100) | 198×199 | 44913 | 3 | 15 | 9 | 119 | 18 | 18 | 18 | 0 | 0 | 0 | 15 | 2/16 | 1 |

몸통(BODY) — 빼는 노드(SwordTrail, Vfx_skill_area, Vfx_mark, Stain, /MeshInstance3D(Mesh), _Outline() 밖에서 넓이 위 둘 · 폭×높이 px · 최대 면적 · 첫/95%/절정/끝 · 95%·절정 − 그 앞 피해 · 다 보임 · 소리 = 이 노드 95%에 가장 가까운 효과음 − 95%

| 항목 | 노드 | 폭×높이 | 면적 | 첫 | 95% | 절정 | 끝 | 95%−피해 | 절정−피해 | 다 보임 | 소리−95% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| play:hit | `DungeonLevel/Vfx_sheet_hit(AnimatedSprite)#1` | 52×49 | 242 | 0 | 8 | 11 | 19 | — | — | 10 | — |
| play:hit_crit | `DungeonLevel/Vfx_sheet_hit_crit(AnimatedSprite)#1` | 78×74 | 544 | 0 | 8 | 11 | 19 | — | — | 10 | — |
| play:slash_arc | `DungeonLevel/Vfx_sheet_slash_arc(AnimatedSprite)#1` | 95×131 | 794 | 0 | 0 | 0 | 22 | — | — | 13 | — |
| basic_attack | `DungeonLevel/Vfx_sheet_hit(AnimatedSprite)#1` | 52×49 | 242 | 18 | 26 | 29 | 37 | 8 | 11 | 10 | -8(hit) |
| slash | `DungeonLevel/Vfx_sheet_slash_arc(AnimatedSprite)#1` | 95×131 | 794 | 34 | 34 | 34 | 56 | -3 | -3 | 13 | 3(hit) |
|  | `DungeonLevel/Vfx_sheet_hit(AnimatedSprite)#1` | 52×49 | 242 | 37 | 45 | 48 | 56 | 8 | 11 | 10 | -8(hit) |
| whirl_lv1 | `Vfx_whirl_ring_whirl_imp/DryInk(Mesh)#1` | 327×189 | 30918 | 25 | 28 | 29 | 97 | 0 | 1 | 47 | 0(hit) |
|  | `Vfx_whirl_ring_whirl_imp/InnerRipple(Mesh)#1` | 327×189 | 17033 | 25 | 26 | 26 | 49 | -2 | -2 | 5 | 2(hit) |
| whirl_lv10 | `Vfx_whirl_ring_whirl_imp/DryInk(Mesh)#2` | 458×265 | 82416 | 44 | 47 | 48 | 96 | 3 | 4 | 51 | -3(hit) |
|  | `Vfx_whirl_ring_whirl_imp/DryInk(Mesh)#1` | 458×265 | 82416 | 25 | 28 | 29 | 96 | 0 | 1 | 56 | 0(hit) |
| dash_strike | `DungeonLevel/Vfx_streak(Mesh)#1` | 232×134 | 31169 | 22 | 22 | 22 | 39 | -11 | -11 | 18 | 11(hit) |
|  | `DungeonLevel/Vfx_sheet_dash_dust(AnimatedSprite)#1` | 97×36 | 420 | 33 | 44 | 47 | 61 | 11 | 14 | 15 | -11(hit) |
| leap_slash | `DungeonLevel/AnimatedSprite3D(AnimatedSprite)#1` | 132×49 | 782 | 33 | 44 | 47 | 61 | 11 | 14 | 15 | -11(hit) |
|  | `DungeonLevel/Vfx_sheet_hit(AnimatedSprite)#1` | 52×49 | 242 | 33 | 41 | 44 | 52 | 8 | 11 | 10 | -8(hit) |
| fire_lore | `Vfx_element_fire/GroundTrace(Mesh)#1` | 196×113 | 7346 | 52 | 54 | 54 | 96 | 2 | 2 | 33 | -2(bandit_hurt) |
|  | `Burn/Body(Mesh)#1` | 56×99 | 1615 | 52 | 52 | 52 | 96 | 0 | 0 | 35 | 0(bandit_hurt) |
| ice_lore | `Vfx_element_cold/GroundTrace(Mesh)#1` | 196×113 | 6456 | 50 | 52 | 52 | 97 | 2 | 2 | 35 | -2(bandit_hurt) |
|  | `Frozen/Body(Mesh)#1` | 71×109 | 1937 | 50 | 50 | 50 | 97 | 0 | 0 | 48 | 0(bandit_hurt) |
| thunder_lore | `Vfx_element_lightning/Form_(Mesh)#1` | 46×77 | 839 | 37 | 41 | 46 | 55 | 4 | 9 | 7 | -4(bandit_hurt) |
|  | `Vfx_element_lightning/Fragments(MultiMesh)#1` | 26×61 | 379 | 37 | 37 | 46 | 55 | 0 | 9 | 9 | 0(bandit_hurt) |
| salpuri | `DungeonLevel/Vfx_sheet_sal_burst(AnimatedSprite)#1` | 76×79 | 688 | 0 | 12 | 12 | 33 | — | — | 17 | -12(talisman_salpuri) |
|  | `DungeonLevel/Vfx_sheet_seal_ripple(AnimatedSprite)#1` | 142×82 | 222 | 0 | 14 | 15 | 44 | — | — | 15 | -14(talisman_salpuri) |
| seal_array | `AoeField_seal_fire/Body(Mesh)#1` | 293×169 | 49645 | 33 | 47 | 58 | 97 | -46 | -35 | 55 | -14(skill_seal_array) |
|  | `AoeField_seal_fire/Rim(Mesh)#1` | 293×169 | 49644 | 33 | 33 | 33 | 97 | -60 | -60 | 65 | 0(skill_seal_array) |
| blink | `DungeonLevel/Vfx_sheet_blink_in(AnimatedSprite)#1` | 136×79 | 208 | 0 | 14 | 15 | 44 | — | — | 16 | -14(skill_blink) |
|  | `DungeonLevel/Vfx_sheet_blink_out(AnimatedSprite)#1` | 107×62 | 137 | 0 | 13 | 15 | 44 | — | — | 16 | -13(skill_blink) |
| mana_shield | `DungeonLevel/Vfx_sheet_shield_on(AnimatedSprite)#1` | 148×85 | 290 | 33 | 46 | 48 | 61 | — | — | 16 | -13(skill_mana_shield) |
| kill_basic | `DungeonLevel/Vfx_sheet_blood_splat(AnimatedSprite)#1` | 67×64 | 409 | 18 | 26 | 29 | 37 | 8 | 11 | 10 | -8(hit) |
|  | `DungeonLevel/Vfx_sheet_hit(AnimatedSprite)#1` | 52×49 | 242 | 18 | 26 | 29 | 37 | 8 | 11 | 10 | -8(hit) |
| kill_slash | `Skeleton3D/tripo_node_2d7b86bc(Mesh)#1` | 99×101 | 9374 | 37 | 65 | 67 | 121 | 28 | 30 | 62 | 10(body_fall) |
|  | `DungeonLevel/Vfx_sheet_slash_arc(AnimatedSprite)#1` | 95×131 | 794 | 34 | 34 | 34 | 56 | -3 | -3 | 13 | 3(hit) |
| kill_bisect | `Skeleton3D/tripo_node_2d7b86bc(Mesh)#1` | 94×100 | 9058 | 18 | 72 | 84 | 121 | 54 | 66 | 59 | 2(body_fall) |
|  | `Weapon/Body(Mesh)#1` | 22×23 | 485 | 18 | 18 | 18 | 121 | 0 | 0 | 50 | 0(hit) |

노드별 위 3(전부) — 폭×높이 px · 최대 면적 · 첫/절정/끝 · 다 보임

| 항목 | 노드 | 폭×높이 | 면적 | 첫 | 절정 | 끝 | 다 보임 |
|---|---|---|---|---|---|---|---|
| play:hit | `DungeonLevel/Vfx_sheet_hit(AnimatedSprite)#1` | 52×49 | 242 | 0 | 11 | 19 | 10 |
| play:hit_crit | `DungeonLevel/Vfx_sheet_hit_crit(AnimatedSprite)#1` | 78×74 | 544 | 0 | 11 | 19 | 10 |
| play:slash_arc | `DungeonLevel/Vfx_sheet_slash_arc(AnimatedSprite)#1` | 95×131 | 794 | 0 | 0 | 22 | 13 |
| basic_attack | `SwordTrail#1` | 178×160 | 28496 | 3 | 18 | 33 | 8 |
|  | `DungeonLevel/Vfx_mark(Mesh)#1` | 43×24 | 1035 | 18 | 25 | 73 | 53 |
|  | `DungeonLevel/Vfx_sheet_hit(AnimatedSprite)#1` | 52×49 | 242 | 18 | 29 | 37 | 10 |
| slash | `DungeonLevel/Vfx_skill_area(Mesh)#1` | 301×174 | 52340 | 0 | 0 | 57 | 58 |
|  | `SwordTrail#1` | 120×178 | 21329 | 2 | 37 | 52 | 9 |
|  | `DungeonLevel/MeshInstance3D(Mesh)#1` | 54×27 | 1442 | 37 | 44 | 73 | 34 |
| whirl_lv1 | `DungeonLevel/Vfx_skill_area(Mesh)#1` | 340×197 | 66884 | 0 | 0 | 48 | 49 |
|  | `Vfx_whirl_ring_whirl_imp/DryInk(Mesh)#1` | 327×189 | 30918 | 25 | 29 | 97 | 47 |
|  | `SwordTrail#1` | 153×165 | 25218 | 2 | 33 | 43 | 8 |
| whirl_lv10 | `DungeonLevel/Vfx_skill_area(Mesh)#1` | 471×272 | 128227 | 0 | 0 | 48 | 49 |
|  | `DungeonLevel/Vfx_skill_area(Mesh)#2` | 471×272 | 128227 | 44 | 44 | 64 | 21 |
|  | `Vfx_whirl_ring_whirl_imp/DryInk(Mesh)#2` | 458×265 | 82416 | 44 | 48 | 96 | 51 |
| dash_strike | `SwordTrail#1` | 296×263 | 77837 | 2 | 33 | 49 | 2 |
|  | `DungeonLevel/Vfx_skill_area(Mesh)#1` | 360×208 | 74849 | 0 | 0 | 53 | 54 |
|  | `DungeonLevel/Vfx_streak(Mesh)#1` | 232×134 | 31169 | 22 | 22 | 39 | 18 |
| leap_slash | `DungeonLevel/Vfx_skill_area(Mesh)#1` | 275×159 | 43633 | 0 | 0 | 53 | 54 |
|  | `SwordTrail#1` | 179×193 | 33982 | 2 | 33 | 49 | 8 |
|  | `DungeonLevel/MeshInstance3D(Mesh)#2` | 52×25 | 1285 | 33 | 40 | 96 | 61 |
| fire_lore | `DungeonLevel/Vfx_skill_area(Mesh)#1` | 210×121 | 25329 | 52 | 52 | 72 | 21 |
|  | `Vfx_element_fire/GroundTrace(Mesh)#1` | 196×113 | 7346 | 52 | 54 | 96 | 33 |
|  | `Burn/Body(Mesh)#1` | 56×99 | 1615 | 52 | 52 | 96 | 35 |
| ice_lore | `DungeonLevel/Vfx_skill_area(Mesh)#1` | 210×121 | 25329 | 50 | 50 | 70 | 21 |
|  | `Vfx_element_cold/GroundTrace(Mesh)#1` | 196×113 | 6456 | 50 | 52 | 97 | 35 |
|  | `Frozen/Body(Mesh)#1` | 71×109 | 1937 | 50 | 50 | 97 | 48 |
| thunder_lore | `Vfx_element_lightning/Form_(Mesh)#1` | 46×77 | 839 | 37 | 46 | 55 | 7 |
|  | `Vfx_element_lightning/Fragments(MultiMesh)#1` | 26×61 | 379 | 37 | 46 | 55 | 9 |
|  | `Vfx_talisman_lightning_t/Fragments(MultiMesh)#1` | 26×60 | 313 | 33 | 33 | 36 | 4 |
| salpuri | `DungeonLevel/Vfx_sheet_sal_burst(AnimatedSprite)#1` | 76×79 | 688 | 0 | 12 | 33 | 17 |
|  | `DungeonLevel/Vfx_sheet_seal_ripple(AnimatedSprite)#1` | 142×82 | 222 | 0 | 15 | 44 | 15 |
| seal_array | `AoeField_seal_fire/Body(Mesh)#1` | 293×169 | 49645 | 33 | 58 | 97 | 55 |
|  | `AoeField_seal_fire/Rim(Mesh)#1` | 293×169 | 49644 | 33 | 33 | 97 | 65 |
|  | `DungeonLevel/Vfx_ring(Mesh)#1` | 276×159 | 40116 | 33 | 33 | 58 | 6 |
| blink | `DungeonLevel/Vfx_sheet_blink_in(AnimatedSprite)#1` | 136×79 | 208 | 0 | 15 | 44 | 16 |
|  | `DungeonLevel/Vfx_sheet_blink_out(AnimatedSprite)#1` | 107×62 | 137 | 0 | 15 | 44 | 16 |
| mana_shield | `DungeonLevel/Vfx_sheet_shield_on(AnimatedSprite)#1` | 148×85 | 290 | 33 | 48 | 61 | 16 |
| kill_basic | `SwordTrail#1` | 178×160 | 28506 | 3 | 18 | 27 | 8 |
|  | `DungeonLevel/BloodStain(Mesh)#1` | 77×44 | 3386 | 18 | 35 | 121 | 95 |
|  | `DungeonLevel/Vfx_mark(Mesh)#1` | 44×26 | 1157 | 18 | 24 | 121 | 101 |
| kill_slash | `DungeonLevel/Vfx_skill_area(Mesh)#1` | 301×174 | 52340 | 0 | 0 | 57 | 58 |
|  | `SwordTrail#1` | 120×178 | 21329 | 2 | 37 | 46 | 9 |
|  | `Skeleton3D/tripo_node_2d7b86bc(Mesh)#1` | 99×101 | 9374 | 37 | 67 | 121 | 62 |
| kill_bisect | `SwordTrail#1` | 178×160 | 28498 | 3 | 18 | 27 | 8 |
|  | `Skeleton3D/tripo_node_2d7b86bc(Mesh)#1` | 94×100 | 9058 | 18 | 84 | 121 | 59 |
|  | `Skeleton3D/tripo_node_2d7b86bc_Outline(Mesh)#1` | 94×100 | 9058 | 18 | 84 | 121 | 59 |

데우기 열쇠 15 · 원장이 쓴 열쇠 31 · 데우기 밖 18
- 데우기 밖: `M:sprite3d bb0 tr1 sh0 ds1 nd0` ← whirl_lv10, salpuri, blink
- 데우기 밖: `M:std t0 b0 s0 bb0 nd0 vc0 tex0 cull2 fog0` ← fire_lore, ice_lore, thunder_lore
- 데우기 밖: `M:std t1 b0 s0 bb0 nd0 vc0 tex0 cull0 fog0` ← fire_lore, ice_lore, blink
- 데우기 밖: `M:std t1 b1 s0 bb0 nd0 vc0 tex1 cull2 fog1` ← dash_strike
- 데우기 밖: `M:std t1 b1 s0 bb3 nd0 vc1 tex1 cull0 fog1` ← fire_lore
- 데우기 밖: `P:ppm e6 o0` ← seal_array
- 데우기 밖: `S:bisect_cut.gdshader` ← kill_slash, kill_bisect
- 데우기 밖: `S:bisect_outline.gdshader` ← kill_slash, kill_bisect
- 데우기 밖: `S:vfx_elements:ELEMENT_SHADER [unshaded,cull_disabled,depth_draw_never,blend_add,fog_disabled]` ← fire_lore, ice_lore, thunder_lore
- 데우기 밖: `S:vfx_elements:ELEMENT_SHADER [unshaded,cull_disabled,depth_draw_never,blend_mix]` ← fire_lore, ice_lore, thunder_lore
- 데우기 밖: `S:vfx_elements:FLIGHT_SHADER [unshaded,cull_disabled,depth_draw_never,blend_add,fog_disabled]` ← fire_lore, ice_lore, thunder_lore
- 데우기 밖: `S:vfx_elements:FLIGHT_SHADER [unshaded,cull_disabled,depth_draw_never,blend_mix]` ← fire_lore, ice_lore, thunder_lore
- 데우기 밖: `S:vfx_meshes:RAMP_SHADER [unshaded,cull_disabled,depth_draw_never,blend_add,fog_disabled]` ← seal_array
- 데우기 밖: `S:vfx_meshes:RAMP_SHADER [unshaded,cull_disabled,depth_draw_never,blend_mix]` ← salpuri, seal_array
- 데우기 밖: `S:vfx_status:STATUS_SHADER [unshaded,cull_disabled,depth_draw_never,blend_add,fog_disabled]` ← fire_lore, ice_lore, seal_array
- 데우기 밖: `S:vfx_status:STATUS_SHADER [unshaded,cull_disabled,depth_draw_never,blend_mix]` ← fire_lore, ice_lore, seal_array
- 데우기 밖: `S:vfx_whirl:SHAPE_SHADER [unshaded,cull_disabled,depth_draw_never,blend_add,fog_disabled]` ← whirl_lv1, whirl_lv10
- 데우기 밖: `S:vfx_whirl:SHAPE_SHADER [unshaded,cull_disabled,depth_draw_never,blend_mix]` ← whirl_lv1, whirl_lv10
