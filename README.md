# joseon-assets

## 2026-09-17 H1 기준 정리

현재 제작 기준은 [H1 승인본](sheets/approved-2026-09-17-h1/SELECTION.md)과 [최신 제작 갤러리](workbench/production/h1-style-expansion-2026-09-17/index.html)다. 이전 키아트·화풍 후보·구버전 일러스트100장은 [아카이브](archive/art-history-2026-09-17/index.html)에 보관한다. 아래 기존 목록의 구버전 경로도 아카이브 위치를 따른다.

조선헌터스 아트 에셋 저장소. 컨셉아트, 캐릭터 레퍼런스 시트, 픽셀 스프라이트, 레퍼런스 이미지 등 게임 제작에 쓰이는 모든 시각 에셋을 관리한다.

---

## 폴더 구조

```
joseon-assets/
├── sheets/          # 공식 캐릭터 레퍼런스 시트 (Pixellab cref 입력용)
├── archive/art-history-2026-09-17/concept/         # 컨셉아트 및 일러스트
├── archive/art-history-2026-09-17/magazine/        # 매거진·카드 스타일 프로모 이미지
├── sprites/         # 픽셀 스프라이트시트 + Aseprite 소스
├── reference/       # 내부 참고 자료 + 외부 수집 레퍼런스
├── video/           # 영상 파일
├── 2026/            # 월별 생성 에셋 (날짜 기반 아카이브)
├── landing/         # 랜딩 페이지용 에셋
├── maps/            # 맵 이미지
├── art-direction/   # 공통 스타일 바이블·프롬프트 템플릿·레퍼런스 세트
├── inbox/           # 새 에셋 단기 드롭존
├── workbench/       # 미승인 후보·프로브·테스트
├── catalog/         # 경로·해시·이동·중복 manifest
└── archive/         # 중복·변형·레거시 보관
```

---

## sheets/ — 공식 캐릭터 레퍼런스 시트

Pixellab `create_character` 및 `animate_character` 호출 시 `reference_image`로 쓰는 **cref 파일**이 여기 있다. 각 캐릭터 폴더에 두 가지 버전을 둔다:

| 파일 패턴 | 설명 |
|-----------|------|
| `*_ref_sheet.png` | cref 원본 (4방향 턴어라운드 기본형) |
| `*_master_sheet.png` | 상세 마스터 시트 (장비·컬러팔레트·디자인노트 포함) |

```
sheets/
├── doho/
│   ├── doho_ref_sheet.png        # 도호 cref (4방향, 흑립·도복·검)
│   └── doho_master_sheet.png     # 도호 마스터 시트 (장비·소재 상세)
├── gwisae/
│   ├── gwisae_ref_sheet.png      # 귀새 cref (4방향, 붉은 한복·가면·도)
│   └── gwisae_master_sheet.png   # 귀새 마스터 시트
└── cheongyeon/
    ├── cheongyeon_ref_sheet.png   # 청연 cref (4방향, 흰 한복·부채·방울)
    └── cheongyeon_master_sheet.png
```

> **cref 매핑 (D-025):** cref1=도호 / cref2=귀새 / cref3=청연

---

## archive/art-history-2026-09-17/concept/ — 컨셉아트 및 일러스트

캐릭터별 서브폴더로 분류. 고화질 일러스트, 액션 컨셉, 마스터 시트(개념 검증용).

```
archive/art-history-2026-09-17/concept/
├── doho/
│   ├── doho_art_action1.png       # 도호 액션 컨셉 (검+달밤)
│   ├── doho_art_action2.png       # 도호 액션 컨셉 (마법진+부적)
│   ├── doho_art_dungeon.png       # 도호 던전 분위기 (묘지 배경)
│   ├── doho_master_sheet.png      # 도호 마스터 시트 (5방향+장비 목록)
│   ├── doho_v4_anime.png          # 도호 v4 아니메 스타일
│   └── doho_v4_semi.png           # 도호 v4 세미리얼 스타일
├── gwisae/
│   ├── gwisae_art_action1.png     # 귀새 액션 컨셉 A
│   ├── gwisae_art_action2.png     # 귀새 액션 컨셉 B
│   └── gwisae_master_sheet.png    # 귀새 마스터 시트 (Haneul 턴어라운드+마스크 3종)
├── cheongyeon/
│   ├── cheongyeon_art_action1.png # 청연 액션 컨셉 (부채 술법)
│   ├── cheongyeon_art_blue.png    # 청연 청색 한복 버전
│   ├── cheongyeon_ref_turnabout.png  # 청연 레드 한복 턴어라운드
│   ├── cheongyeon_pixel_ref.png   # 청연 픽셀 스타일 레퍼런스
│   ├── cheongyeon_master_sheet_v1.png
│   └── cheongyeon_master_sheet_v2.png
├── gumiho/
│   ├── gumiho_art_9tail.png       # 구미호 구미 전신 (달밤+사당)
│   ├── gumiho_art_face.png        # 구미호 얼굴 클로즈업 (황금 눈+혈흔)
│   └── gumiho_art_standing.png    # 구미호 전신 (혈흔 한복+불꽃)
├── npc/
│   ├── general_master_sheet.png   # 장군 NPC 마스터 시트 (파란 갑옷)
│   └── yungeom_ref_sheet.png      # 윤검(호위도사) 레퍼런스 시트
├── keyart_trio_v1.jpg             # 3인 키아트 가로형 (조선판타지)
├── keyart_trio_v2.png             # 3인 키아트 세로형
└── keyart_trio_action.png         # 3인 액션 단체컷
```

화풍·구도 프로브는 공식 컨셉과 섞지 않고 `workbench/probes/`에 둔다.

---

## archive/art-history-2026-09-17/magazine/ — 매거진·카드 스타일 프로모

캐릭터 소개용 매거진 커버, 캐릭터 파일 카드. SNS·마케팅 소재로 활용.

```
archive/art-history-2026-09-17/magazine/
├── doho_modern_orient.png         # 도호 Modern Orient 매거진 커버
├── cheongyeon_magazine_card.png   # 청연 조선판타지 매거진 카드
├── cheongyeon_char_no01.png       # 청연 캐릭터 파일 No.01
├── gwisae_heritage_cover.png      # 귀새 Heritage & Fantasy 커버
├── gwisae_veiled_blade_card.png   # 귀새 화무향도 카드 No.07
├── gwisae_char_file_no06.png      # 귀새 캐릭터 파일 No.06
├── yungeom_card_v1.png            # 윤검 호위도사 카드 (YG-0137)
└── yungeom_card_v2.png            # 윤검 호위도사 카드 v2 (Royal Guard)
```

---

## sprites/ — 픽셀 스프라이트

Pixellab 생성 스프라이트시트 및 Aseprite 소스 파일.

```
sprites/
├── doho_cref1_spritesheet.png     # 도호 4방향 스프라이트시트 (그린BG)
├── doho_sheet_4dir.png            # 도호 4방향 strip (투명BG)
├── doho_128_dir0~3.png            # 도호 128px 단일 방향 프레임 4종
├── doho_256_dir0~3.png            # 도호 256px 단일 방향 프레임 4종
├── doho_sprite.aseprite           # 도호 Aseprite 소스
├── gwisae_cref2_spritesheet.png   # 귀새 4방향 스프라이트시트
├── cheongyeon_cref3_spritesheet.png   # 청연 4방향 스프라이트시트 v1
└── cheongyeon_cref3a_spritesheet.png  # 청연 4방향 스프라이트시트 v2 (축제 의상)
```

테스트 스프라이트와 작업 소스는 `workbench/tests/sprites/`에 둔다.

> 캔버스 규격과 방향 정책은 `joseon/docs/04_ART_STYLE_GUIDE.md`와 최신 `DECISIONS.md`를 따른다.

---

## reference/ — 레퍼런스

```
reference/
├── internal/
│   ├── ui_mockup/                 # 프로젝트 UI 목업
│   └── sprites/                   # 프로젝트 스프라이트 방향 참고
└── external/
    └── unclassified/              # 해시명 외부 레퍼런스, 출처·태그 정리 대기
```

---

## video/

```
video/
├── gumiho_vid1.mp4   # 구미호 모션 레퍼런스 1
└── gumiho_vid2.mp4   # 구미호 모션 레퍼런스 2
```

---

## inbox/ — 드롭존

**새 파일은 여기 던지되 같은 작업 세션 안에서 분류한다.**

- 미승인 후보·프로브·테스트 → `workbench/`
- 승인된 공식 에셋 → 목적 폴더
- 배포 복제본 → `landing/` 또는 `2026/YYYY/MM/`

---

## art-direction/ — 스타일·프롬프트 세트

GPT Image 계열로 컨셉아트, 캐릭터, 배경, 키아트를 만들 때 쓰는 공통 운영 세트.

```
art-direction/
├── STYLE_BIBLE.md                 # 조선 다크판타지 공통 스타일 원칙
├── anchors/                       # 앵커 운영 규칙, 원본 이미지는 manifest로 참조
├── prompts/                       # 공통·캐릭터·배경·키아트·프롭 템플릿
├── work-orders/                   # 실제 생성 작업 단위 프롬프트
└── manifests/                     # 레퍼런스 세트와 생성 이력
```

`character-ref`, `style-ref`, `environment-ref`는 API 필드명이 아니라 이 저장소의 역할 구분이다. GPT Image 2에는 참조 이미지를 배열로 전달하고, 각 이미지의 역할은 프롬프트에서 명시한다.

---

## archive/ — 보관

```
archive/
└── duplicates/
    ├── exact/      # canonical과 SHA-256 완전 동일
    └── variants/   # 중복 이름이지만 내용은 다른 변형
```

정리 manifest와 로그는 `catalog/`, `docs/ASSET_CLEANUP_LOG_2026-06-07.md`를 참조한다.

---

## 네이밍 컨벤션

| 규칙 | 예시 |
|------|------|
| 소문자 + 언더스코어 | `doho_art_action1.png` |
| 캐릭터 접두사 | `doho_`, `gwisae_`, `cheongyeon_`, `gumiho_` |
| 버전 suffix | `_v1`, `_v2`, `_v3` |
| 방향 suffix (스프라이트) | `_dir0`~`_dir3` |
| 한글·공백·특수문자 금지 | ← ChatGPT 자동 파일명 그대로 쓰지 말 것 |

---

## 관련 문서

- GPT Image 2 게임 에셋 활용 전략 (Codex 작성) → `docs/gpt-image2_asset_strategy.md`
- 조선헌터스 아트 디렉션 세트 → `art-direction/README.md`
- 이미지 생성 조명 프롬프트 가이드 → `docs/image-generation-lighting-prompt-guide.md`
- 에셋 정리 로그 → `docs/ASSET_CLEANUP_LOG_2026-06-07.md`
- 정리 manifest → `catalog/`
- 캐릭터 캔버스·Layer·컬러 규격 → `joseon/docs/04_ART_STYLE_GUIDE.md`
- 아트 결정 락 (D-007, D-022, D-030, D-034) → `joseon/docs/DECISIONS.md`
- 컨셉아트 발주 리스트 → `joseon/docs/design/concept_art_list.md`
- Pixellab 파이프라인 메모 → `~/.claude/projects/.../memory/pixellab-doho-character.md`
