# #1138 소품 둘 — Meshy API로 다시 (Hunyuan3D 접음, PD 11-03 · 11-05 「추천대로」)

> 옛 = #557(2026-10-02) Comfy `TencentImageToModelNode` = Hunyuan3D 3.1 · face 5000 · 147.7크레딧(둘 합) — `docs/design/ai_provenance.md`.
> 새 = 바이블 §3.2 고정 설정 · **입력 원화는 #557 그대로**(Comfy Seedream 5.0 Pro — 3D만 Hunyuan이었다, 원화 0크레딧).

## 1. 생성 (2026-11-05)

| 소품 | 입력 | Meshy 작업 | 설정 | 결과 | 크레딧 |
|---|---|---|---|---|---|
| away_sign 「잠시 비움」 팻말 | `stall_props/refs/away_sign_concept.png` (1024²) | `01a1a906-4256-74b6-9fad-8feb6ff41e8e` | latest · should_remesh · triangle · target 1,500 · 2k · PBR 끔 · image_enhancement 끔 · auto_size 끔 · glb | **1,495면** · JPEG 텍스처 1장 · 판 앞면 = ±Z(폭 1.08 · 키 1.90 · 두께 0.26 정규화) | 30 |
| cold_cup 식은 사발 | `stall_props/refs/cold_cup_concept.png` (1024²) | `01a1a906-49b5-73d5-97a8-ff0c9917b625` | 같음 | **1,555면** · JPEG 1장 · 폭 1.86 · 키 0.86 | 30 |

- 잔액 1,978 → 1,918. 다시 뽑기 0번.
- 입력 ↔ 미리보기 = `preview/input_vs_meshy.jpg` · 원본 GLB = `glb/*_meshy_01a1a906.glb`(텍스처 포함 GLB).
- 크기는 게임이 맞춘다(`world/jumo_stall.gd` — 팻말 키 `SIGN_H` 0.95 · 사발 지름 `CUP_D` 0.15 · `ModelFit.fit_box`). 팻말 한지·글씨는 게임이 앞면(+Z)에 얹으니 판에 글씨 없음.

## 2. 반입 (PD 「합쳐」 뒤)
- `intake_model.ps1 -Src <glb> -Id props/away_sign -Budget prop` · `props/cold_cup` 같음 → 텍스처 512로 줄임(`albedo_ops shrink --max 512`).
- 사발 속 흰 술빛은 #1078 감사 B4(「속이 하얗게 뜬다」) → 반입 때 누른다.

## 3. 옛 ↔ 새 (2026-11-05)
- 네 방향 = `preview/old_new_views.jpg`(1·2줄 팻말 옛·새 · 3·4줄 사발 옛·새). 모양은 거의 같다.
- 빛깔: 옛 반입은 #557 `prep_557.ps1`이 채도를 ×0.415(팻말) · ×0.406(사발)로 눌렀다 → 새 GLB는 갈색이 짙다 — **반입 때 같은 채도 누르기**(+ 사발 속 흰 술빛 누르기, #1078 B4).

## 4. 판정판 (2026-11-05)
- PD 판정판 = https://claude.ai/artifact/7A9v8pEDbDNPhZT1fJhizE 결정 ③ · 소품은 캐릭터 자료관(D-109) 대상이 아니다.
