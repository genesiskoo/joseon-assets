# #393 개별 아이콘 이미지 생성 프롬프트 세트

도구: Codex 내장 image_gen. 각 주제는 **독립적인 1장**으로 생성했다. `results/A_painted.png`는 **채색·먹선·무광 명암·한정된 악센트**의 화풍 참조, `results/D1_inventory_objects.png`는 **다칸 독립 물체** 참조, `references/H1_approved_reference.png`는 도호의 **왼쪽 H1 복장** 참조. 참조 이미지의 문자/레이아웃/아이콘 픽셀을 복사하지 않는다.

## 공통 프롬프트 — 소지품 11종

“Joseon Hunters, dark Joseon fantasy isometric ARPG. Generate ONE premium hand-painted Korean inventory OBJECT, not a square icon tile. Full isolated object with naturally cut out transparent alpha, no frame, panel, slot, cast-shadow floor, label, decorative border, watermark or extra object. Faithful Korean silhouette, D1 Diablo2R-style item presentation, A painterly restrained palette. Matte broad value planes, selective worn material highlights, thin ink contour, warm upper-left light. Readable after reducing to 40px per occupied inventory cell. Preserve subject's full outline and safe edge space. No Western medieval, Gothic, Chinese imperial or Japanese costume cues.”

각 호출에는 아래 하나의 주제를 넣었다.

| ID | 점유 | 주제 / 배제 |
|---|---:|---|
| hwando | 1×3 | 도호의 짧은 한국 환도 한 자루, 완만히 휜 은빛 칼날·작은 둥근 코등이·검은 손잡이·작은 붉은 매듭. 전장 세로 실루엣; 서양 십자 가드와 카타나 제외. |
| cotton_dopo | 2×3 | 착용자 없는 짙은 남색 무명 도포, 흰 깃·무광 접힘·낮은 붉은 허리띠. H1 의복만 참조; 갑옷·인물 제외. |
| leather_shoes | 2×2 | 조선식 낮은 갈색 가죽신 두 짝, 살짝 들린 앞코·두툼한 바느질 밑창. 현대 끈·발목 부츠 제외. |
| paeraengi | 2×2 | 검게 그을린 대나무 패랭이 한 점, 넓은 챙·낮은 둥근 갓몸·묶는 붉은 끈. 흑립이나 서양 마녀 모자 제외. |
| mukham | 1×2 | 세로형 낡은 나무 묵함, 먹돌/붓 도구의 조선 공예 질감, 절제된 놋쇠 결구. 서양 마법책·검집 제외. |
| cotton_belt | 2×1 | 옅은 무명 허리띠를 가운데 묶은 가로 실루엣, 거친 천 가장자리. 금속 챔피언 벨트 제외. |
| silver_ring | 1×1 | 한 개의 무광 은가락지, 넓고 단순한 공예 표면. 보석 반지·후광 제외. |
| jade_charm | 1×1 | 옥색 타원 옥패 한 점, 붉은 매듭·작은 술. 뚜렷한 구멍/새김; 금빛 프레임 제외. |
| hp_potion | 1×1 | 낮고 넓은 갈색 도기 탕약 항아리, 무명 천 마개·작은 붉은 매듭. 유리 판타지 포션 제외. |
| mp_potion | 1×1 | 길고 가는 청자 이중호리 영약병, 푸른 끈. 탕약과 흑백에서도 다른 실루엣; 유리병 제외. |
| talisman_fire | 1×1 | 오래된 노란 종이 화염부 한 장, 명확한 붉은 한자 **火**, 먹선과 닳은 끝. 스킬 폭발 이펙트·여러 장 제외. |

## 공통 프롬프트 — 스킬 6종

“Create ONE polished square action illustration for a 128px Korean dark fantasy skill icon, A painted art direction. Joseon Hunters H1 Doho: adult clean-shaven Korean male, black gat, dark navy layered robe, white collar, muted red sash; restrained matte chiaroscuro and ink outlines. Strong single gesture and 3–4 value groups readable at 30px, dark quiet background, no lettering, slot frame, watermark or fantasy UI. Sword skills are purely physical with ivory brush action strokes, no elemental spell from the body. Talismans carry fire or frost effects. Compose as a tight narrative miniature; one action per image.”

| ID | 주제 |
|---|---|
| slash | 몸통과 환도가 보이는 결연한 **대각** 한 번 베기, 하나의 넓은 미색 획. |
| lunge | 낮게 전진한 **수평** 찌르기/베기, 칼끝과 도포가 전진 방향을 만든다. |
| whirlwind | 허리 높이 회전 검무, **원형** 한 번의 붓획 안에 인물·검이 보인다. |
| fire_talisman | 노란 부적 한 장을 중심으로 작은 붉은 화염, 불꽃이 실루엣을 가리지 않는다. |
| frost_talisman | 부적 한 장 주변의 각진 옅은 청색 서리 파편, 화염부와 다른 방향성. |
| power_shield | 도호 앞·옆을 감싸는 방어 호, 공격 장풍이 아닌 보호 자세. |

### 재생성/후처리

위 문구는 이번 생산에 쓴 **재생산용 프롬프트 세트**다. 도구별 미세 표현과 이미지 생성의 비결정성 때문에 원본 재현은 `source/` PNG와 `manifest.json` SHA-256을 기준으로 한다. `prepare_assets.py`가 알파 문턱 16, 여백 8%, LANCZOS 축소, 어두운 스킬 바탕 합성을 적용한다.
