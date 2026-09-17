# Work Order: Key Art Calibration v1

## Objective

작업 시작용 `joseon_active_working_v1` 세트로 조선헌터스 키아트 방향을 캘리브레이션한다. 목표는 최종 홍보 이미지가 아니라, 이후 캐릭터·배경·키아트 생성의 기준이 될 스타일 샘플을 얻는 것이다.

## Reference Set

- reference_set_id: `joseon_active_working_v1`
- style-ref 1: `workbench/probes/gpt-image2/style-tests-2026-06-07/joseon-hunter-16bit-action-rpg.png`
- style-ref 2: `workbench/probes/gpt-image2/style-tests-2026-06-07/joseon-hunter-minhwa-pixel-art.png`
- style-ref 3: `concept/keyart_trio_action.png`
- character-ref: `sheets/doho/doho_ref_sheet.png`, `sheets/gwisae/gwisae_ref_sheet.png`, `sheets/cheongyeon/cheongyeon_ref_sheet.png`

## Generation Prompt

```text
Joseon dark fantasy action RPG key art calibration, late Joseon dynasty Korean visual language, painterly but readable game production art, matte surfaces, controlled brush texture, clean silhouettes, low-saturation ink black, deep navy, muted crimson, aged gold accents, weathered wood and paper talismans, soft atmospheric lighting, restrained rim light, no glossy 3D rendering, no cyberpunk neon, no modern clothing, no Western plate armor.

REFERENCE ROLES
- Image 1: primary project style anchor. Use game readability, value grouping, dark Joseon palette, and clear character-vs-monster staging.
- Image 2: secondary style anchor. Use Korean folk-art texture, muted palette, and pixel translation discipline.
- Image 3: promotional key art mood anchor. Use only the dramatic party mood; do not copy the exact composition, particle density, blue magic circle, or over-complex lighting.
- Character reference images: preserve the main party's Joseon hunter identity, costume language, weapon silhouettes, and color roles. Do not copy the turnaround sheet layout.

Create a cinematic but production-readable key art image for Joseon Hunters.

Scene:
- A cursed late-Joseon village gate at night, broken jangseung totems, paper talismans on old wood, low fog on stone ground.
- Doho stands in the foreground as a dark-robed swordsman exorcist with black gat and talismans.
- Gwisae moves from the right as a masked red-black blade dancer, threatening and elegant.
- Cheongyeon appears slightly elevated in the back-left as a white-robed shaman with fan and bells, calm and luminous.
- A large shadowy dokkaebi spirit emerges behind the gate, readable but not over-detailed.

Composition:
- Strong triangular composition with Doho first, Gwisae second, Cheongyeon third, monster fourth.
- Clear silhouettes at thumbnail size.
- Leave negative space in the upper-left for title placement.
- Dramatic but restrained lighting, one cool moonlight source and small muted blue ghost flames.

Production constraints:
- Keep particles sparse.
- Keep faces, weapons, sleeves, and talismans readable.
- Use broad shape groups that can guide later pixel art and in-game stills.
- Avoid photorealistic skin, glossy CGI, plastic armor, cyberpunk neon, sci-fi panels, modern streetwear, Japanese samurai armor, Chinese xianxia robe exaggeration, Western medieval plate armor, excessive bloom, lens flare, unreadable particles, random magic circles, over-detailed noisy background, distorted hands, extra fingers, unreadable weapon shapes.
```

## Review Criteria

- 스타일 앵커 1, 2의 팔레트와 판독성이 남았는가
- `concept/keyart_trio_action.png`의 과밀 입자와 과한 광원을 따라가지 않았는가
- 세 주인공 역할이 한눈에 구분되는가
- 조선 마을, 장승, 부적, 기와, 귀기 요소가 확실한가
- 이후 픽셀아트와 인게임 배경으로 분해 가능한 큰 형태가 있는가

## Logging

생성 후 `art-direction/manifests/generations.csv`에 다음 값을 기록한다.

```csv
generated_at,tool,model,prompt_version,asset_type,reference_set_id,reference_paths,output_path,review_status,review_notes
2026-06-08T__:__:+09:00,gpt-image,gpt-image-2,keyart-calibration-v1,keyart,joseon_active_working_v1,"see work order",workbench/probes/gpt-image2/keyart-calibration-2026-06-08/<file>.png,pending,""
```
