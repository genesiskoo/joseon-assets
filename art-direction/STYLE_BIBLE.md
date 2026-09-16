# Joseon Hunters Style Bible v2

## 목표

조선풍 가공 세계의 **조선 그루브 판타지**를 그린다(D-019/D-037). 능청스러운 인물과 경쾌한 액션이 기본이다. PC·NPC·배경이 한 화가의 작품처럼 이어지도록 선, 얼굴 단순화, 명암, 재질 밀도를 공유한다. 키아트·캐릭터·배경 원화와 3D 제작 참고를 대상으로 하며, 캐릭터·타일의 최종 게임 자산은 D-066/D-067의 3D GLB 파이프라인을 따른다.

## 기준과 우선순위

- 외형 정본은 D-068: [승인 카탈로그](../sheets/approved-2026-09-17/SELECTION.md)의 도호 D03 / 귀새 G02 / 청연 C01 / 구미호 F01→F03.
- 공통 인물 그림체는 **선택한 도호 D03의 정제된 2D 일러스트**를 우선 참조한다. [단독 마스터](../workbench/production/artwork-sequence-2026-09-17/01_doho_D03_master.png)는 해당 선택에서 파생한 작업용 참조다.
- 2026-09-17 PD 피드백: “npc+pc+배경 그림스타일이랑 톤 맞춰야됨”, “npc랑 주인공 그림스타일 너무 달라 맞춰야됨”. 이것은 기존 D-037/D-068 적용 보정이며 새 외형 선택이나 게임 반입 승인이 아니다.
- [NPC 보정 세트](../workbench/production/npc-style-alignment-2026-09-17/README.md)는 검토 후보다. 기존 외형 정본·reference-sets.yaml의 승인 상태를 자동 변경하지 않는다.

## 공통 시각 언어

- 한국 시각 어휘: 한복·도포·갓·흑립·비녀·노리개·부적·목조건축·기와·장승·산성·사당. 시대 고증을 의무화하지 않는다.
- 선: 가늘고 또렷한 어두운 윤곽선, 의도적인 굵기 변화. 얼굴·손·천·소품에 같은 선의 성격을 쓴다.
- 얼굴: 그려진 눈·코·입과 큰 면으로 단순화한다. 피부는 기본색과 소수의 큰 그림자, 제한적인 부드러운 전이. 노인은 백발·턱/볼 형태·수염·자세·몇 개의 나이 선으로 표현한다.
- 재질: 무광, 큰 옷주름과 정돈된 색면. 금속에만 작은 절제된 하이라이트. 얼굴 모공, 잔주름 묘사, 천 얼룩·직조 노이즈로 사실성을 높이지 않는다.
- 색: 먹색·남색·아이보리·탁한 적색·청록·따뜻한 회색을 함께 사용한다. 인물의 식별색은 유지하며 모두를 갈색/세피아로 덮지 않는다. 새 HEX 락은 만들지 않는다.
- 조명: 한 장면 안에서 같은 광원 방향·색온도·접지 그림자를 사용한다. 낮의 마을과 어두운 던전은 밝기가 달라도 선과 재질 처리 방식은 공유한다.
- 배경: 목재·석재는 큰 면과 제한된 이음선, 기와는 묶인 행, 수목은 큰 군집으로 그린다. 원경은 인물보다 디테일과 대비를 낮춘다. 실사 배경 뒤에 일러스트 인물을 붙인 인상을 피한다.
- 계층: 주인공의 문양·장신구 복잡도와 NPC의 소박함은 달라도 된다. NPC에 도호의 별 문양·새 문양·푸른 장신구를 복제하는 것은 그림체 통일이 아니다.

## 금지 방향

- photorealistic skin, pores, photographic elderly wrinkles, coarse fabric grain, mottled stains, glossy 3D/PBR, plastic armor.
- 과한 bloom·lens flare·림라이트·네온 외곽선·파티클·의미 없는 마법진.
- 무속 공포나 무겁고 처참한 인상을 기본 톤으로 삼는 것.
- 한국적 정체성을 압도하는 사무라이 갑옷·선협식 복식·서양 플레이트 아머, 현대 총기·차량·거리 복장.
- 노인 NPC를 아동 체형으로 줄이거나, 그림체를 맞춘다는 이유로 무조건 젊게 만드는 것.

## 참조 이미지 운영

1. **렌더링 스타일 기준**과 **외형/구도 참고**를 입력별로 명시한다. 스타일 기준은 D03를 우선하며 1~3장 이내로 유지한다.
2. 실사풍으로 실패한 NPC 이미지를 얼굴 보정 입력에 재사용하지 않는다. 의상·역할·소품만 문장으로 옮기고 D03만 참조해 얼굴 비교부터 다시 만든다.
3. 얼굴 비교 후보 → 해당 얼굴로 전신 → PC·NPC·배경 통합 장면 순서로 확인한다. 성공 전 대량 파생하지 않는다.
4. NPC 재생성에는 보정 얼굴/전신 후보를 일관되게 사용한다. 기존 실사풍 15번 NPC와 U01 통합 시도는 이력으로만 남긴다.
5. 배경 참고를 넣을 때는 구도·건축만 따르고 그 배경의 실사 질감은 따르지 말라고 명시한다.
6. 새 결과는 workbench에 보존한다. 사용자 선택 전에 공식 자산을 덮어쓰거나 승인 플래그를 올리지 않는다.

## 공통 프롬프트 핵심

```text
Use the selected Doho D03 as the rendering-style authority for every character and environment element. Crisp slender drawn contours, stylized eye/nose/mouth construction, smooth skin in a few broad values, matte cloth with controlled folds. Preserve distinct adult ages and identities. Draw elders with designed face shapes, grey hair and a few purposeful age lines, never photographic wrinkles. Quiet background masses use the same drawing medium. Match light direction, color temperature and shadow treatment across the scene. No photoreal skin, coarse fabric grain, mottled stains, sepia wash or realistic scenery behind illustrated characters.
```

## 직접 검수

- 같은 크기의 PC/NPC 얼굴을 나란히 놓았을 때 눈·코·입의 선, 피부 명암, 머리카락 묘사가 한 그림체인가.
- NPC의 연령·역할·표정이 유지되며 실사 피부나 아동 비율로 돌아가지 않았는가.
- 전신에서 얼굴·손·옷이 같은 방식으로 그려졌는가. 주인공의 문양이 NPC로 전이되지 않았는가.
- 통합 장면에서 인물만 선명한 합성물처럼 뜨지 않는가. 공통 광원과 접지, 배경 디테일 계층이 맞는가.
- 작은 게임 크기로 번역할 수 있는 색 덩어리·실루엣인가. 원화 생성만으로 3D 반입 검증을 통과한 것으로 보지 않는다.
