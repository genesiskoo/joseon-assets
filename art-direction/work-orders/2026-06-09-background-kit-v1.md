# Work Order: Background Kit v1

## Objective

조선헌터스의 대표 배경 4종을 같은 시각 언어로 뽑는다.

## Targets

1. 마을: 산자락 초가와 기와가 섞인 저녁 마을, 장승, 사당, 등불, 안개
2. 숲: 신목과 부적이 있는 금지된 소나무 숲, 달빛, 돌계단, 귀화
3. 던전: 조선식 봉인 던전, 왕릉 또는 지하 묘실, 석문, 제기, 붕괴된 돌벽
4. 조선 대표: 조선시대가 한눈에 읽히는 궁궐 외곽, 한양 성문, 산성, 문루

## Style Anchor

- `joseon_active_working_v1`

## Shared Prompt Block

```text
late Joseon dark fantasy concept art, Korean historical visual language, painterly but readable game production art, matte surfaces, controlled brush texture, clean silhouettes, low-saturation ink black, deep navy, muted crimson, aged gold accents, weathered wood and paper talismans, soft atmospheric lighting, restrained rim light, no glossy 3D rendering, no cyberpunk neon, no modern clothing, no Western plate armor
```

## Per-Asset Focus

- Village: warm human settlement with an ominous sealed feeling
- Forest: sacred forbidden zone, quiet and dangerous
- Dungeon: sealed royal or shrine space, oppressive depth, old stone and wood
- Joseon representative: iconic architecture silhouette that instantly says Joseon

## Lighting Control

- Use ambient-dominant fill lighting.
- Keep rim light extremely weak or absent.
- Prefer overcast moonlight, mist, and sky fill over edge glow.
- Do not push buildings or totems into luminous outlines.

## Output Folder

`workbench/probes/gpt-image2/background-kit-2026-06-09/`

## Logging

Record each file in `art-direction/manifests/generations.csv` with `prompt_version=background-kit-v1`.
