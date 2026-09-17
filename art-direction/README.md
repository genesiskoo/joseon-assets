# Joseon Hunters Art Direction Set

이 폴더는 GPT Image 계열로 컨셉아트, 캐릭터, 배경, 키아트를 만들 때 쓰는 프로젝트 공통 프롬프트 세트다.

## 사용 순서

1. `STYLE_BIBLE.md`에서 고정 스타일 원칙을 확인한다.
2. `manifests/reference-sets.yaml`에서 사용할 style, character, environment anchor를 고른다.
3. `prompts/common.md`의 공통 블록을 먼저 붙인다.
4. 작업 종류에 맞는 템플릿을 하나 고른다.
5. 생성 후 `manifests/generations.csv`에 모델, 프롬프트 버전, 레퍼런스 세트, 결과 경로, 리뷰 상태를 기록한다.

## 구성

```text
art-direction/
├── STYLE_BIBLE.md
├── anchors/       # 앵커 운영 규칙, 원본 이미지는 복제하지 않음
├── prompts/       # 공통·캐릭터·배경·키아트·프롭 템플릿
├── work-orders/   # 실제 생성 작업 단위 프롬프트
└── manifests/     # 레퍼런스 세트와 생성 이력
```

## 핵심 규칙

- `character-ref`, `style-ref`, `environment-ref`는 API 필드명이 아니라 이 저장소의 역할 구분이다.
- GPT Image 2에는 참조 이미지를 배열로 전달하고, 각 이미지의 역할은 프롬프트에서 명시한다.
- 스타일 앵커는 색, 선, 명암, 재질, 화면 밀도만 가져온다.
- 캐릭터 앵커는 얼굴, 헤어, 의상, 실루엣을 유지한다.
- 신규 생성보다 승인본 기반 편집과 파생을 우선한다.
- 승인 전 결과는 `workbench/`에 보존하고 공식 에셋을 덮어쓰지 않는다.
