# 1093 빈 장비 칸 그림 (게임 카드 #1093 · 부모 #664)

PD 2026-11-02 「시안A로」 → 「합쳐」.

| 파일 | 내용 |
|---|---|
| `sheet_A_ink_shadow.png` | **채택** — 먹 그림자(수묵 실루엣) 5×2 시트 1983×793 · sha256 `39b46e6408aef4b7b6a701fed2fe872a342b410285eb0b70e4963270822dce6b` |
| `sheet_B_brass.png` | 기각 — 놋쇠 음각 |
| `sheet_C_baekmyo.png` | 기각 — 한지 백묘 |
| `prompt_[ABC].txt` | 갈래별 프롬프트 전문 |

- 생성 = Codex CLI 0.147 내장 image_gen(`gpt-5.6-sol`, D-102) · 참조 = 옛 코드 선 그림 사진 1장.
- 시트 순서: 1행 머리(흑립)·호신부·오른손(칼)·갑옷(도포)·보조 도사 도구 / 2행 가락지·허리띠·신·보조 홍사·보조 부채.
- 게임 반입 = `python tools/intake_equip_ghost.py sheet_A_ink_shadow.png` → `assets/sprites/ui/equip_ghost/*.png`(밝기 = 알파).
- 함정: Codex CLI 0.147 `-s workspace-write` = Windows 샌드박스 도우미 없음(code-mode host 죽음) → 저장소 밖 빈 폴더에서 `-s danger-full-access`. `--image`는 뒤 인자를 다 먹으니 프롬프트 앞에 `--`.
