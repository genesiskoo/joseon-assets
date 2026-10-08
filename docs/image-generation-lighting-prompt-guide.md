# 이미지 생성 조명 프롬프트 가이드

> 적용 대상: GPT Image 2, Retro Diffusion, PixelLab 등 이미지 생성 도구
>
> 목적: 과도한 반사광, 전면 림라이트, 블룸 때문에 화면이 번들거리거나
> 픽셀 밀도가 지저분해지는 현상을 줄인다.

## 문제 정의

다음 현상은 조명이 풍부한 것이 아니라 시각적 우선순위가 무너진 상태로 본다.

- 피부, 천, 나무, 돌에도 금속처럼 흰 반사점이 반복된다.
- 캐릭터와 오브젝트의 외곽 전체에 밝은 테두리가 생긴다.
- 모든 모서리와 돌출부가 같은 강도로 빛난다.
- 작은 광원마다 블룸과 색 번짐이 넓게 퍼진다.
- 명암 단계보다 밝은 점과 선이 많아 형태가 잘게 부서져 보인다.
- 바닥과 소품이 젖지 않았는데도 코팅된 표면처럼 보인다.

목표는 하이라이트를 완전히 제거하는 것이 아니다. **광원, 재질, 초점 대상에
따라 필요한 곳에만 제한적으로 배치**하는 것이 목표다.

## 기본 원칙

### 1. 광원을 먼저 제한한다

- 주광원은 기본적으로 하나만 둔다.
- 보조광은 색과 방향을 명시하고 주광원보다 약하게 설정한다.
- 환경 전체가 아니라 초점 대상 주변에만 밝은 대비를 허용한다.
- `dramatic lighting`만 단독으로 쓰지 않는다. 광원 방향과 강도를 함께 쓴다.

권장 문장:

```text
One dominant soft light source from the upper left.
Weak ambient fill only, with no additional edge lights.
```

### 2. 재질의 거칠기를 명시한다

광택 억제에는 `no highlights`만 쓰는 것보다 표면 특성을 긍정적으로
지정하는 편이 안정적이다.

```text
Mostly matte, high-roughness surfaces.
Cloth, wood, stone, skin, and painted surfaces have broad value changes
instead of sharp reflective highlights.
```

재질별 기본값:

| 재질 | 기본 표현 | 허용되는 밝은 반응 |
|---|---|---|
| 천, 한지 | 무광, 확산 반사 | 넓고 부드러운 명암 |
| 목재 | 건조하고 거친 표면 | 모서리 일부의 약한 밝기 |
| 돌, 흙 | 무광, 높은 거칠기 | 면 방향에 따른 값 변화 |
| 피부 | 자연스러운 무광 | 코와 이마에 매우 약한 변화 |
| 칠기 | 반광 | 좁고 절제된 반사 |
| 금속 | 제한적 유광 | 광원 방향과 맞는 작은 반사 |
| 물, 젖은 돌 | 선택적 유광 | 수면이나 젖은 부분에만 반사 |

### 3. 하이라이트 예산을 정한다

- 가장 밝은 값은 초점 대상과 실제 발광체에만 사용한다.
- 금속, 물, 눈처럼 물리적으로 필요한 재질 외에는 날카로운 흰 점을 금지한다.
- 같은 밝기의 하이라이트를 화면 전체에 균등하게 뿌리지 않는다.
- 작은 소품은 하이라이트보다 실루엣과 고유색으로 분리한다.

권장 문장:

```text
Reserve the brightest values for the focal point and actual light sources.
Use sparse, material-specific highlights rather than highlights on every edge.
```

### 4. 림라이트는 일부 실루엣에만 쓴다

림라이트가 필요하다면 다음 조건을 모두 지정한다.

- 한 방향에서만 들어온다.
- 광원을 마주한 외곽 일부에만 생긴다.
- 실루엣 전체를 두르지 않는다.
- 흰색 외곽선처럼 보이지 않을 정도로 약하다.

```text
If rim light is present, keep it faint and localized to a few
light-facing silhouette segments. No continuous glowing outline.
```

림라이트가 필요하지 않은 맵, 오브젝트, 정면 시트에는 더 직접적으로 쓴다.

```text
No rim lighting. Separate forms with value grouping and cast shadows.
```

### 5. 블룸과 발광 범위를 분리한다

발광체 자체의 밝기와 주변으로 번지는 빛은 별개의 항목이다.

```text
Small contained glow around actual flames only.
Minimal bloom, no haze around non-emissive edges, and no glowing particles
across the whole image.
```

## 피해야 할 표현과 대체어

아래 단어가 항상 나쁜 것은 아니지만, 단독 사용하면 광택과 림라이트를
과장하는 경향이 있다.

| 주의할 표현 | 문제 | 대체 표현 |
|---|---|---|
| `cinematic lighting` | 다중 색광과 림라이트 유발 | `single-source directional lighting` |
| `dramatic rim light` | 외곽 전체가 발광 | `faint localized edge separation` |
| `glowing edges` | 모든 모서리가 빛남 | `clear silhouette through value contrast` |
| `high contrast` | 흰 점과 검은 틈이 과다 | `controlled value hierarchy` |
| `wet look` | 모든 재질이 코팅처럼 보임 | 젖은 재질과 영역을 구체적으로 지정 |
| `polished` | 표면 전체에 유광 반사 | `cleanly rendered, mostly matte` |
| `volumetric lighting` | 안개와 블룸이 과다 | `subtle directional light through thin mist` |
| `neon glow` | 색 번짐과 밝은 윤곽선 유발 | `small contained colored light source` |
| `highly detailed` | 미세 하이라이트 노이즈 증가 | `clear forms with restrained texture density` |

`cinematic composition`, `polished concept art`처럼 조명이 아닌 의미로 사용할
때도 뒤에 조명 제한 문장을 붙인다.

## 공통 붙여넣기 블록

### 짧은 실전 억제 키워드

긴 조명 설명 앞이나 뒤에 다음 문구를 짧게 반복하면 모델이 목표를
놓치는 것을 줄일 수 있다.

```text
matte lighting
soft diffuse lighting
minimal specular highlights
low contrast shading
avoid glossy surfaces
avoid plastic skin
avoid over-rendered reflections
natural skin texture
subtle rim light only
```

인물의 피부가 없는 맵과 오브젝트에는 피부 관련 문구를 빼고 다음처럼 쓴다.

```text
matte finish
minimal specular highlights
low contrast shading
avoid glossy surfaces
avoid over-rendered reflections
subtle rim light only
```

셀 애니메이션 계열에는 `flat anime cel shading`을 추가할 수 있다. 이 문구는
모든 화풍에 공통 적용하지 않고, 셀 셰이딩이 목표일 때만 사용한다.

짧은 문구만으로는 픽셀아트의 관습적인 밝은 엣지 점이 남을 수 있다.
그 경우 재질과 위치를 직접 지정한다.

```text
No shiny roof tiles, no shiny stone, no shiny pottery.
No decorative white reflection dots or edge sparkle.
Only water and exposed metal may carry small muted highlights.
```

### 기본 억제

대부분의 컨셉아트에 먼저 적용한다.

```text
Lighting treatment: one dominant directional light with weak ambient fill.
Mostly matte, high-roughness surfaces. Use broad, quiet value planes instead
of scattered sharp highlights. Reserve the brightest values for the focal
point and actual light sources. Keep specular highlights sparse and strictly
material-specific. No continuous rim light, glossy skin, glowing edges,
excessive bloom, or wet-looking surfaces unless explicitly described.
```

### 강한 억제

첫 결과가 번들거리거나 외곽선이 발광할 때 사용한다.

```text
Lighting correction: flatten the secondary light effects and simplify the
value structure. Remove decorative specular flecks from cloth, skin, wood,
stone, and ground. Eliminate the bright contour around figures and objects.
Use no rim lighting; separate silhouettes through local value contrast and
cast shadows. Keep only tiny highlights on exposed metal and actual water.
Minimal bloom around true emissive objects only.
```

### 재생성 없이 수정할 때

```text
Change only the lighting and material response. Preserve the composition,
camera, pose, design, palette, proportions, and object placement. Reduce
specular highlights by about 70 percent, remove continuous rim lighting and
edge glow, make non-metal materials matte, and simplify scattered bright
pixels into broader value groups. Keep small highlights only where physically
appropriate on metal, water, glass, or wet surfaces.
```

## 화풍별 추가 문장

### 픽셀아트 캐릭터

```text
Pixel lighting uses compact clusters and two or three controlled value steps.
Do not place single bright pixels along every contour. No one-pixel rim around
the full silhouette. Use a few grouped highlight pixels only on light-facing
metal or a designated focal detail.
```

128px 캐릭터 권장 기준:

- 가장 밝은 하이라이트 색은 전체 팔레트에서 1개만 기본 사용한다.
- 연속 림라이트는 실루엣 둘레의 10% 이하로 제한한다.
- 천과 피부의 밝은 점은 독립된 1픽셀 노이즈보다 2~6픽셀 군집으로 정리한다.
- 무기 반사는 면 전체가 아니라 날 또는 장식 한두 곳에 둔다.

### High top-down 맵과 오브젝트

```text
Use restrained overhead lighting with consistent short cast shadows.
Terrain tiles remain matte and low-contrast. Do not outline props with rim
light. Separate objects from the ground using contact shadows, value grouping,
and clear silhouettes. Specular response appears only on water, exposed metal,
glazed ceramic, or explicitly wet tiles.
```

맵에서는 밝은 모서리가 타일 경계처럼 반복되지 않도록 한다. 길, 흙, 돌벽,
지붕의 구분은 색상군과 접촉 그림자로 해결한다.

### 셀 애니메이션

```text
Clean two- or three-step cel shading with matte color shapes.
Use one controlled edge-light accent only where required by the key light.
No glossy airbrushed highlights, no luminous full-body outline, and no bloom
on non-emissive colors.
```

### 민화, 수묵, 목판화

```text
Lighting is expressed through flat color hierarchy, ink density, and negative
space rather than reflective rendering. No specular shine, rim lighting,
glossy gradients, bloom, or cinematic edge glow.
```

### HD-2D

HD-2D는 광원 효과가 과장되기 쉬우므로 다음 제한을 기본으로 붙인다.

```text
Atmospheric depth remains subtle. Volumetric light is faint and localized.
Pixel-art surfaces stay matte, with restrained reflections and no bright rim
around every sprite or prop. Use particles and bloom sparingly around actual
magic or flame sources only.
```

## 예외 처리

광택이 핵심인 소재는 전역 제한에서 제외하고 영역을 명시한다.

```text
The lacquered scabbard may have one narrow controlled reflection.
All surrounding cloth, skin, wood, and stone remain matte.
```

```text
Only the rain-wet flagstones reflect the lantern.
Dry walls, roofs, soil, characters, and props have no wet sheen.
```

이 방식으로 “광택 허용 대상”과 “무광 유지 대상”을 같은 문장에 함께 쓴다.

## 결과 검수 체크리스트

- 실제 광원과 가장 밝은 부분의 위치가 일치하는가?
- 천, 피부, 나무, 돌에 불필요한 흰 점이 있는가?
- 밝은 외곽선이 캐릭터나 오브젝트 전체를 두르고 있는가?
- 모든 소품이 같은 강도로 반짝이는가?
- 발광하지 않는 모서리에서 블룸이 발생하는가?
- 하이라이트를 지웠을 때도 실루엣과 재질이 구분되는가?
- 픽셀아트에서 밝은 단일 픽셀이 노이즈처럼 흩어져 있는가?
- 맵에서 접촉 그림자 대신 림라이트로 오브젝트를 분리하고 있지 않은가?

두 항목 이상 문제가 있으면 먼저 `강한 억제` 블록으로 조명만 수정한다.
구도와 디자인을 동시에 바꾸지 않는다.
