# #716 피해 숫자 v2 — 판정 영상·사진 (2026-10-10, 검수 뒤 다시 찍음)

같은 대본 `_feel_numbers_demo`를 판 A(지금 숫자)·판 N716(새 숫자, 치명 「강」)·판 N716L(새 숫자, 치명 「약」)로 한 번씩 창 모드 60fps로 찍었다. Movie Maker가 시계를 고정하므로 영상 1프레임 = 물리 1틱이다. 판 N716은 74fps로 한 번 더 찍었다(사양 S11 — 74Hz 모니터에서 54ms 박힘 = 4프레임).
게임 저장소 작업 트리 `claude/716-damage-numbers` @ **1c76784d**(검수 반영 — 판 바뀜 거둠 · 게임 시계 · 틱·속성 알파 · 출현 상한 12% · stamp_sec · 클립 5 더함)로 찍었다. 실제 출력 크기는 1280×720이다(`manifest.json`의 1920×1080은 요청값 — 이 PC 창이 화면 배율 때문에 720p로 잡힌다).
판 d는 실험장 판(손잡이 `node:HUD/DamageNumbers.style`)으로만 켰다. raw 로그 첫 줄로 확인: 판 A = `NUMDEMO INFO plate=A style=a` · 판 N716 = `plate=N716 style=d` · 판 N716L = `plate=N716L style=d_soft`. 네 번 모두 `E2E SUMMARY: 1/1 PASS`.

```
python tools/capture_slice.py --scenario _feel_numbers_demo --fps 60 "--user-args=--feel-lab=<A|N716|N716L>" --out C:/workspace/joseon-assets/reports/716/<A|N716|N716L>
python tools/capture_slice.py --scenario _feel_numbers_demo --fps 74 "--user-args=--feel-lab=N716" --out C:/workspace/joseon-assets/reports/716/N716_74fps
python C:/workspace/joseon-assets/reports/716/_scripts/events.py      # 세 판 raw 로그 → events.json + 같은 숫자인가 표
python C:/workspace/joseon-assets/reports/716/_scripts/make_media.py  # 나란히 영상(각 두 조각) + 74fps 0.25배
python C:/workspace/joseon-assets/reports/716/_scripts/stills.py <게임 저장소>/docs/art/716_damage_numbers   # 판정 사진 6 + stills/ 3 (다시 찍었으면 _frames/를 먼저 지운다)
python C:/workspace/joseon-assets/reports/716/_scripts/measure.py > _measure/table.md   # 캡처 픽셀 대비·색약 3종 ΔE 표
```

## 대본 (클립마다 같은 출발)
도호가 0.5초 서 있다가 시작한다. 산적은 선딜 99·무게 0·멈춤·보상 없음 몸이다. 클립마다 전투 난수와 게임 난수를 같은 씨앗(716)으로 시작한다. 피해 범위·치명률·무기 불은 대본이 한 대마다 직접 넣는다. 01~10은 들녘 원형 정거장, 11·12는 지역을 옮겨 찍는다(실험장 판은 지역을 옮겨도 그대로 — 로그에서 확인).
- `01_basic` 칼 연타(다섯 몸 무리): 보통 셋 → 큰 타격 90 → 칼+무기 불(불 우세 16) → 칼+무기 불(불 30% 16)
- `02_crit` 한 몸: 보통 12 → 치명 20 → 큰 치명 121
- `03_fire` 무리 셋: 화염부 던지기(터짐 + 화상 틱) → 부적 진(불) 틱
- `04_cold` 무리 셋: 빙결부 던지기 → 부적 진(한기) 틱
- `05_aoe8` 둘레 여덟: 회오리베기(치명 40%, 셋 처치)
- `06_kill` 칼 처치 → 치명 처치 → 화염부 처치
- `07_bulgasari_heat` 불가살이(멈춤): 철갑 칼 둘(회색) → 달아오름 → 칼 둘(판 a = 주황 채움, 판 d = 주황 후광)
- **`08_lightning`** 무리 셋: 벽력부 던지기(PD ② — 숫자·표식 #D8CCFF) → 부적 진(벼락) 틱
- **`09_flurry`** 한 몸: 연속 베기 Lv10(5타 · 치명 40% — 기세가 칼 값을 지우지 않게 대본이 스탯이 바뀔 때마다 다시 넣음)
- **`10_elite_alt`** 금색 우두머리 + 파란 정예 넷, Alt 이름표 켬: 칼 연타 여덟(치명 40%)
- **`11_cave`** 흑랑 굴 1층(어두움): 보통 → 치명 → 큰 치명 → 칼 처치(물리 흰) → 화염부(터짐 + 화상 틱)
- **`12_town`** 못골 흙(밝음): 11과 같은 손. 마을에선 부적을 못 던져 화염부만 빠진다.

**같은 숫자인지 확인한 결과**(`events.json`): 세 판 클립 12개 모두 프레임 수가 같다. 01·02·05·07·09·10·12는 피해 숫자·몸·치명까지 판 A와 같다. 부적 던지기 터짐 숫자(03·04·08 첫 터짐, 06·11 화염부)만 판마다 1~4 다르다. 부적 비행 쪽 난수가 씨앗 밖이라 그렇고, #698 README의 화염부와 같은 현상이다. 진 틱·화상 틱 숫자는 같다.

## 판정용 (가공본, h264 crf 24 · 파일마다 < 10MB라 클립 01~07 = `_1`, 08~12 = `_2`)
| 파일 | 내용 |
|---|---|
| `716_A_N716_sbs_1.mp4` · `_2.mp4` | 「지금」 \| 「새 숫자(강)」을 나란히, 1배. 왼쪽 귀에 지금, 오른쪽 귀에 새 숫자 소리. 오른쪽 아래 f = 클립 프레임. (7.0MB · 6.5MB) |
| `716_A_N716_slow025_1.mp4` · `_2.mp4` | 같은 나란히를 0.25배로. 클립마다 숫자가 튀는 창만(소리 없음, 7.7MB · 7.5MB). 창 = `_segments/windows.json`. |
| `716_N716_N716L_sbs_1.mp4` · `_2.mp4` | 「새 숫자(강)」 \| 「새 숫자(약)」, 1배(7.0MB · 6.5MB). 둘은 치명 움직임만 다르다. |
| `716_N716_74fps_crit_slow025.mp4` | 판 N716 **74fps 녹화**의 02 치명 → 큰 치명, 0.25배(1.3MB). 54ms 박힘이 74Hz에서 4프레임으로 어떻게 보이는지(60fps는 3프레임 — 계단). |

판정 사진 6장은 게임 저장소 `docs/art/716_damage_numbers/`에 있다: 치명 · 불 · 벼락 · 배경(흑랑 굴·못골 흙) · 섞인 한 방과 처치 · 색약 3종(적록·적색·청색). 나머지 셋(광역 8 · Alt 이름표 · 연속 베기)은 여기 `stills/`.

## 캡처 픽셀 판정 (`_measure/table.md`, 사양 §7 기준 = 채움 중앙 ≥ 4.5:1 · 불↔금니 색약 ΔE ≥ 12)
게임 저장소 `docs/design/damage_numbers_v2_log.md` §9에 표와 읽는 법을 적었다. 요약:
- 모든 숫자가 4.5:1을 넘는다. 가장 낮은 것이 불 계열 5.1(칼+무기 불 · 부적 터짐 — 옛 4.5). 틱은 5.7 · 5.4(옛 3.7 · 3.6 미달).
- 흑랑 굴·못골 흙의 물리 처치 흰 숫자 10.4 · 15.9(판 A 붉은금 3.2 · 4.4).
- 불↔금니는 색약 3종 모두 ΔE ≥ 12. **새 위험**: 벼락 ↔ 한기가 적록·적색 색약에서 ΔE76 4.7 · 3.9로 거의 같다 — 표식 모양(⚡ / ❄)이 가른다.

## 판별 원본 (capture_slice 산출)
`A/`·`N716/`·`N716L/`·`N716_74fps/` 아래의 `capture_raw.log`(NUMDEMO 줄 = 피해 프레임·양·몸·치명·처치), `manifest.json`, `contact_*.jpg`, `README.md`는 git에 있다.
**git에 넣지 않은 것**(D-100 — 카드 합 ≥ 50MB · 원본 ≥ 10MB)은 이 PC에만 둔다. 드라이브로 옮길 때는 `JoseonHunters_raw/716/`에 둔다.

| 파일 | 크기 | SHA256 앞 16 |
|---|---|---|
| `A/capture_master.avi` | 453,621,398 B | 15e5889b88717443 |
| `N716/capture_master.avi` | 454,220,950 B | 656f5284eb3d0af2 |
| `N716L/capture_master.avi` | 453,968,762 B | 8bfc5486d8ed5d1a |
| `N716_74fps/capture_master.avi` | 505,254,760 B | b96db057eb09751d |
| `<판>/NN_<클립>.mp4` (클립 12 × 판 4, crf 18 + 게임 소리) | 판마다 약 32MB | — |

`_frames/`(프레임 png)·`_segments/`(조각 영상·ffmpeg 그래프)·`_labels/`·`_measure/*.png`(마스크 확인 그림)는 스크립트로 다시 만들 수 있어서 넣지 않았다.

## 보조 스크립트 (`_scripts/`)
- `events.py` — raw 로그를 `events.json`과 표로 바꾼다.
- `make_media.py` — 나란히 영상(각 두 조각)과 74fps 0.25배 영상을 만든다.
- `stills.py` — 판정 사진(게임 저장소 6 + `stills/` 3)과 색약 3종 사본을 만든다.
- `measure.py` — 캡처 픽셀 대비와 색약 3종 ΔE를 잰다(판 A는 같은 숫자의 제 자리 상자).
- `colorsci.py` — Machado 2009 색약 행렬(적록·적색·청색, 세기 1.0), CIELAB, ΔE76/2000, WCAG 대비 계산.
- `strip.py`·`grid.py` — 확인용 띠와 눈금을 그린다.
