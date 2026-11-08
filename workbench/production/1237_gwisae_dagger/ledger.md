# #1237 귀새 휜 단검 — 3D 장부 (modeling_bible §6)

**바이블 칸** = 무기(손에 드는 소품 — §2 표에 칸 없음 → 중간 소품 값 준용) · **서비스** = Meshy API(D-114) · **면 수 상한** = target_polycount 3,000 · 텍스처 2K 생성 → 반입 1,024(PD 「더 디테일하게」 — 소품 512보다 올림) · **예산** = **39크레딧 = 여러 방향 그림 9 + 3D 30 — PD 승인 2026-11-08 「B · 39크레딧」**.

## 입력 원화 (Codex · 2026-11-08)

참조 = G02 보드에서 단검 부분 잘라낸 것(`sheets/approved-2026-09-17/catalog_gwisae_G01-G03.png`) + H1 시트(화풍만). 프롬프트 = `art/gwisae_dagger_<a|b>.prompt.txt`. 묘사 = 「휜 단검」(「곡도」 말 금지 — guisae_character_v1 §7.2).

| 파일 | 무엇 | SHA-256 | 판정 |
|---|---|---|---|
| `art/gwisae_dagger_a.png` | A — G02 그대로 · 넓은 휜 날 · 민 칼날 | `98f4f69dafb9733716a51d2a8f8bab1663e29bea61e396ecc0f6470c4693cb61` | 기각(B 채택) |
| `art/gwisae_dagger_b.png` | B — 디테일 판 · 칼등 홈 · 구름 코등이 · 고리 새김 · 매듭 술 | `7e591a76349c22f46ed29621db332b0f4ad6243ce9e32a78db459c04f573a5f1` | ✅ 채택 (PD 11-08) |

## 3D

| 물건 | 게임 id | 입력 | 서비스 · 작업 | 설정 | 결과 | 판정 | 차감 | 잔액(전 → 후) |
|---|---|---|---|---|---|---|---|---|
| 여러 방향 그림 | — | `art/gwisae_dagger_b.png` | Meshy image_to_image `01a1b91c-5d01-70db-ac65-bae6ea6a9fc7` | nano-banana-pro · generate_multi_view | `art/multiview_0..2.png`(앞 · 날 옆 · 뒤 — 모양 일치) | 채택 | 9 | 1,918 → 1,909 |
| 휜 단검 | `gwisae_dagger` | 위 세 장 | Meshy multi_image_to_3d `01a1b91c-fbef-70ea-a16f-b328194f0930` | latest · remesh · triangle · 3,000 · 2k · PBR 끔 · image_enhancement 끔 · auto_size 끔 · glb | 삼각형 3,048 · 정점 6,261 · 긴 변 1.90(정규화) | 채택(구름 코등이 · 고리 · 매듭 술 유지 · 술은 조금 가늘어짐) | 30 | 1,909 → 1,879 |

**합계 39크레딧**(예산 그대로).

| 파일 | SHA-256 | 비고 |
|---|---|---|
| `glb/gwisae_dagger_meshy.glb` | `ac26487a1424caba13d57717bde1974716cbd2fd932debcfa5f7ed4c8f973e27` | Meshy 원본(2,588,400 B · 텍스처 2K) |
| 게임 `assets/models/weapons/gwisae_dagger.glb` | `d358cd5ab1024531a92f3afe88dcdbc86a121ef39b67b477d9649fd5e94228cd` | `tools/blender/weapon_intake.py --grip=0.60 --flip=1 --length=0.42` · 칼끝 +0.343 · 자루 끝 −0.077 · 텍스처 1,024 · 무광 |

## 착륙 (2026-11-08)

- 게임 main `da8a13cc1`(PD 「그대로 합쳐」 · 작업 트리 커밋 050726390) — `data/models/gwisae.tres` weapon_scene = `gwisae_dagger.glb` · 가벼운 시험 단위 + e2e 16/16 PASS.

## 남은 것

- 손 보정값은 산적 단검 것 그대로(같은 축) — 주먹 쥐기 · 보정 다시 재기 = G4 #1222.
- 게임 거리에서 날이 산적 단검(코드 모양, 날 6cm)보다 가늘게 읽힌다 — PD 판정 11-08 「그대로 합쳐」 = 길이 0.42 유지.
