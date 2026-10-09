| 항목 | 방식 | 폭×높이 px | 최대 면적 px² | 첫 | 등장 | 다 보임 | 보임 | 절정 | 피해 | 절정−피해 | 효과음−절정 | 패스 | 입자 노드/양 | 빛 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| play:hit | Vfx.play | 52×49 | 211 | 0 | 9 | 11 | 21 | 14 | -1 | — | — | 1 | 0/0 | 1 |
| play:hit_crit | Vfx.play | 78×74 | 475 | 0 | 9 | 11 | 21 | 14 | -1 | — | — | 1 | 0/0 | 1 |
| play:hit_sparks | Vfx.play | 0×0 | 0 | -1 | -1 | 0 | 0 | -1 | -1 | — | — | 1 | 1/8 | 0 |
| play:slash_arc | Vfx.play scale=range×0.7 | 130×131 | 746 | 0 | 0 | 17 | 24 | 5 | -1 | — | — | 1 | 0/0 | 1 |
| basic_attack | 자동공격 1타 | 197×203 | 30166 | 4 | 14 | 9 | 70 | 19 | 18 | 1 | -1 | 8 | 3/21 | 1 |
| slash | cast Lv1 | 426×270 | 128346 | 0 | 0 | 59 | 74 | 40 | 37 | 3 | -3 | 11 | 4/31 | 2 |
| whirl_lv1 | cast Lv1 | 481×278 | 260444 | 0 | 27 | 23 | 98 | 35 | 28 | 7 | -7 | 16 | 3/21 | 2 |
| whirl_lv10 | cast Lv10 | 667×452 | 1201649 | 0 | 45 | 5 | 97 | 48 | 28 | 20 | -4 | 40 | 3/21 | 2 |
| dash_strike | cast Lv1 | 454×333 | 234680 | 0 | 31 | 10 | 85 | 34 | 33 | 1 | -1 | 15 | 3/24 | 1 |
| leap_slash | cast Lv1 | 389×309 | 122382 | 0 | 26 | 22 | 97 | 34 | 33 | 1 | -1 | 13 | 4/31 | 1 |
| fire_lore | cast Lv1 (비행+터짐) | 296×171 | 69932 | 33 | 20 | 21 | 64 | 58 | 52 | 6 | -6 | 10 | 1/12 | 1 |
| ice_lore | cast Lv1 (비행+터짐) | 296×179 | 71114 | 33 | 18 | 21 | 65 | 56 | 50 | 6 | -6 | 12 | 1/12 | 1 |
| thunder_lore | cast Lv1 (비행+터짐) | 61×105 | 1514 | 33 | 8 | 7 | 24 | 47 | 37 | 10 | -10 | 6 | 1/12 | 1 |
| salpuri | cast Lv1 (제자리) | 203×146 | 978 | 0 | 12 | 14 | 46 | 19 | -1 | — | -19 | 3 | 1/12 | 0 |
| seal_array | cast Lv1 (화염 진) | 415×239 | 200871 | 33 | 0 | 65 | 65 | 41 | 93 | -52 | -8 | 7 | 2/22 | 1 |
| blink | cast Lv1 (3u) | 312×180 | 632 | 0 | 11 | 12 | 46 | 16 | -1 | — | -16 | 4 | 2/16 | 0 |
| mana_shield | cast Lv1 | 207×117 | 531 | 33 | 10 | 12 | 29 | 49 | -1 | — | -16 | 1 | 0/0 | 0 |
| kill_basic | 자동공격 막타(생명 1) | 198×202 | 32905 | 4 | 14 | 9 | 118 | 25 | 18 | 7 | -7 | 10 | 4/38 | 1 |
| kill_slash | 참격 막타(생명 1) | 426×270 | 153606 | 0 | 37 | 22 | 122 | 44 | 37 | 7 | -7 | 20 | 4/38 | 2 |
| kill_bisect | 평타 막타 + 두 동강 강제 | 198×202 | 33873 | 4 | 14 | 9 | 118 | 25 | 18 | 7 | -7 | 10 | 4/38 | 1 |

무리별(노드 이름) 위 3 — 폭×높이 px · 최대 면적 · 첫/절정/끝 · 다 보임

| 항목 | 무리 | 폭×높이 | 면적 | 첫 | 절정 | 끝 | 다 보임 |
|---|---|---|---|---|---|---|---|
| play:hit | `DungeonLevel/Vfx_sheet_hit(AnimatedSprite)` | 52×49 | 211 | 0 | 14 | 20 | 11 |
| play:hit_crit | `DungeonLevel/Vfx_sheet_hit_crit(AnimatedSprite)` | 78×74 | 475 | 0 | 14 | 20 | 11 |
| play:slash_arc | `DungeonLevel/Vfx_sheet_slash_arc(AnimatedSprite)` | 130×131 | 746 | 0 | 5 | 23 | 17 |
| basic_attack | `SwordTrail` | 178×160 | 28497 | 4 | 19 | 34 | 8 |
|  | `DungeonLevel/Vfx_mark(Mesh)` | 76×42 | 3187 | 18 | 26 | 73 | 52 |
|  | `DungeonLevel/Vfx_sheet_hit(AnimatedSprite)` | 52×49 | 211 | 18 | 32 | 38 | 11 |
| slash | `DungeonLevel/Vfx_skill_area(Mesh)` | 426×246 | 104679 | 0 | 0 | 58 | 59 |
|  | `SwordTrail` | 120×178 | 21329 | 3 | 38 | 53 | 9 |
|  | `DungeonLevel/MeshInstance3D(Mesh)` | 68×33 | 2269 | 37 | 45 | 73 | 33 |
| whirl_lv1 | `DungeonLevel/Vfx_skill_area(Mesh)` | 481×278 | 133768 | 0 | 0 | 49 | 50 |
|  | `Vfx_whirl_ring_whirl_imp/DryInk(Mesh)` | 463×267 | 61838 | 26 | 30 | 97 | 47 |
|  | `Vfx_whirl_ring_whirl_imp/InnerRipple(Mesh)` | 462×267 | 34068 | 26 | 27 | 50 | 5 |
| whirl_lv10 | `DungeonLevel/Vfx_skill_area(Mesh)` | 667×385 | 512908 | 0 | 44 | 65 | 6 |
|  | `Vfx_whirl_ring_whirl_imp/DryInk(Mesh)` | 648×374 | 329671 | 26 | 49 | 96 | 45 |
|  | `Vfx_whirl_ring_whirl_imp/Helix_(Mesh)` | 559×420 | 257822 | 26 | 51 | 95 | 15 |
| dash_strike | `DungeonLevel/Vfx_skill_area(Mesh)` | 454×262 | 118778 | 0 | 0 | 54 | 55 |
|  | `SwordTrail` | 296×263 | 77837 | 3 | 34 | 50 | 2 |
|  | `DungeonLevel/Vfx_streak(Mesh)` | 252×146 | 36735 | 22 | 22 | 40 | 19 |
| leap_slash | `DungeonLevel/Vfx_skill_area(Mesh)` | 389×225 | 87266 | 0 | 0 | 54 | 55 |
|  | `SwordTrail` | 179×193 | 33982 | 3 | 34 | 50 | 8 |
|  | `DungeonLevel/MeshInstance3D(Mesh)` | 54×25 | 1614 | 33 | 50 | 96 | 59 |
| fire_lore | `DungeonLevel/Vfx_skill_area(Mesh)` | 296×171 | 50658 | 52 | 52 | 73 | 22 |
|  | `Vfx_element_fire/GroundTrace(Mesh)` | 278×160 | 14693 | 53 | 55 | 96 | 33 |
|  | `Vfx_element_fire/Form_(Mesh)` | 106×106 | 2689 | 53 | 58 | 85 | 19 |
| ice_lore | `DungeonLevel/Vfx_skill_area(Mesh)` | 296×171 | 50658 | 50 | 50 | 71 | 22 |
|  | `Vfx_element_cold/GroundTrace(Mesh)` | 278×160 | 12912 | 51 | 53 | 97 | 35 |
|  | `Frozen/Body(Mesh)` | 100×142 | 3538 | 50 | 50 | 97 | 48 |
| thunder_lore | `Vfx_element_lightning/Form_(Mesh)` | 61×105 | 1514 | 38 | 47 | 56 | 7 |
|  | `Vfx_talisman_lightning_t/Form_(Mesh)` | 57×40 | 444 | 33 | 34 | 36 | 4 |
|  | `Area3D/Paper(Mesh)` | 21×16 | 321 | 33 | 33 | 36 | 4 |
| salpuri | `DungeonLevel/Vfx_sheet_sal_burst(AnimatedSprite)` | 76×79 | 570 | 0 | 18 | 34 | 13 |
|  | `DungeonLevel/Vfx_sheet_seal_ripple(AnimatedSprite)` | 203×116 | 408 | 0 | 19 | 45 | 13 |
| seal_array | `AoeField_seal_fire/Rim(Mesh)` | 415×239 | 99289 | 33 | 33 | 97 | 65 |
|  | `DungeonLevel/Vfx_ring(Mesh)` | 390×225 | 83318 | 33 | 33 | 59 | 6 |
|  | `AoeField_seal_fire/Body(Mesh)` | 378×219 | 82660 | 33 | 97 | 97 | 39 |
| blink | `DungeonLevel/Vfx_sheet_blink_in(AnimatedSprite)` | 194×111 | 381 | 0 | 16 | 45 | 13 |
|  | `DungeonLevel/Vfx_sheet_blink_out(AnimatedSprite)` | 153×88 | 251 | 0 | 16 | 45 | 12 |
| mana_shield | `DungeonLevel/Vfx_sheet_shield_on(AnimatedSprite)` | 207×117 | 531 | 33 | 49 | 61 | 12 |
| kill_basic | `SwordTrail` | 178×160 | 28506 | 4 | 19 | 28 | 8 |
|  | `DungeonLevel/BloodStain(Mesh)` | 107×62 | 6556 | 18 | 36 | 121 | 94 |
|  | `DungeonLevel/Vfx_mark(Mesh)` | 62×33 | 2058 | 18 | 26 | 121 | 100 |
| kill_slash | `DungeonLevel/Vfx_skill_area(Mesh)` | 426×246 | 104679 | 0 | 0 | 58 | 59 |
|  | `SwordTrail` | 120×178 | 21329 | 3 | 38 | 47 | 9 |
|  | `Skeleton3D/tripo_node_2d7b86bc(Mesh)` | 132×137 | 17977 | 37 | 69 | 121 | 13 |
| kill_bisect | `SwordTrail` | 178×160 | 28498 | 4 | 19 | 28 | 8 |
|  | `DungeonLevel/MeshInstance3D(Mesh)` | 108×62 | 9640 | 18 | 36 | 121 | 96 |
|  | `DungeonLevel/Vfx_sheet_blood_splat(AnimatedSprite)` | 67×64 | 357 | 18 | 32 | 38 | 11 |

데우기 열쇠 15 · 원장이 쓴 열쇠 31 · 데우기 밖 18
- 데우기 밖: `M:sprite3d bb0 tr1 sh0 ds1 nd0` ← whirl_lv10, salpuri, blink
- 데우기 밖: `M:std t0 b0 s0 bb0 nd0 vc0 tex0 cull2 fog0` ← fire_lore, ice_lore, thunder_lore
- 데우기 밖: `M:std t1 b0 s0 bb0 nd0 vc0 tex0 cull0 fog0` ← fire_lore, ice_lore, blink
- 데우기 밖: `M:std t1 b1 s0 bb0 nd0 vc0 tex1 cull2 fog1` ← dash_strike
- 데우기 밖: `M:std t1 b1 s0 bb3 nd0 vc1 tex1 cull0 fog1` ← fire_lore, ice_lore, thunder_lore
- 데우기 밖: `P:ppm e6 o0` ← seal_array
- 데우기 밖: `S:bisect_cut.gdshader` ← kill_slash
- 데우기 밖: `S:bisect_outline.gdshader` ← kill_slash
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
