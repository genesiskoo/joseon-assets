# D-070 — 현재 3D·인게임 기준 공통 프롬프트

STYLE_BIBLE.md와 함께 사용한다. 기존 common.md의 밝고 평평한 ambient-dominant fill보다 이 파일의 목적별 조명 규칙을 우선한다.

## 공통 블록

```text
Korean dark fantasy action RPG, consistent with the supplied actual stylized 3D game assets. Use their proportions, large color masses, matte hand-painted materials, simple geometry and restrained detail density. Deep navy, charcoal, muted mineral grey and soot brown, limited dull-red and teal identifying accents. Preserve the preferred NPC B faces, age differences and sardonic personalities. Keep Korean costume signatures. No glossy porcelain skin or intricate decorative inflation. Match PC, NPC and environment material treatment.
```

## 중립 제작 시트 추가

```text
Neutral inspection lighting, plain background, readable true albedo and full silhouettes. Show complete props and anatomy with generous margins. Do not bake dramatic shadows, colored scene lighting or rim light into the reference for texturing.
```

## 통합 장면 추가

```text
Orthographic isometric scale and camera consistent with the current game. Low ambient illumination and a few restrained local lights, deep shadow around readable playable space. Preserve visibility of face, hands, weapon and traversal surface. Use broad matte material shapes rather than photographic grime. No full-scene golden fill or pastel daylight.
```

## 참조 역할

1. 실제 3D 렌더/인게임: 색·형태·재질·조명·정보 밀도.
2. NPC B: 얼굴·표정·연령·역할.
3. D-068 카탈로그: 캐릭터 식별 요소·복식·소품.
4. 현재 타일 텍스처: 큰 소재 면·격자 모티프.

임시 박스·캡슐·디버그 UI·체커 바닥·렌더 오류를 완성 미술로 복제하지 않는다. 생성 이미지에는 '목표 시안'임을 기록하며 실제 게임 캡처와 구분한다.
