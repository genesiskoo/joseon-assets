# #716 피해 숫자 v2 — 판정 영상·사진 (2026-10-10)

같은 대본 `_feel_numbers_demo`를 판 A(지금 숫자)·판 N716(새 숫자, 치명 「강」)·판 N716L(새 숫자, 치명 「약」)로 한 번씩 창 모드 60fps로 찍었다. Movie Maker가 시계를 고정하므로 영상 1프레임 = 물리 1틱이다.
게임 저장소 작업 트리 `claude/716-damage-numbers` @ d7289d93 + 이 대본(같은 내용이 게임 커밋 8e77f1bd test(#716) `_feel_numbers_demo`)으로 찍었다. 실제 출력 크기는 1280×720이다(`manifest.json`의 1920×1080은 요청값).
판 d는 실험장 판(손잡이 `node:HUD/DamageNumbers.style`)으로만 켰다. raw 로그 첫 줄로 확인: 판 A = `NUMDEMO INFO plate=A style=a` · 판 N716 = `plate=N716 style=d` · 판 N716L = `plate=N716L style=d_soft`.

```
python tools/capture_slice.py --scenario _feel_numbers_demo --fps 60 "--user-args=--feel-lab=<A|N716|N716L>" --out C:/workspace/joseon-assets/reports/716/<A|N716|N716L>
python C:/workspace/joseon-assets/reports/716/_scripts/events.py      # 세 판 raw 로그 → events.json + 같은 숫자인가 표
python C:/workspace/joseon-assets/reports/716/_scripts/make_media.py  # 나란히 영상 셋
python C:/workspace/joseon-assets/reports/716/_scripts/stills.py <게임 저장소>/docs/art/716_damage_numbers   # 판정 사진 여섯
python C:/workspace/joseon-assets/reports/716/_scripts/measure.py     # 캡처 픽셀 대비·색약 ΔE 표 (_measure/table.md)
```

## 대본 (클립마다 같은 출발)
도호가 들녘 원형 정거장 가운데서 0.5초 서 있다가 시작한다. 산적은 선딜 99·무게 0·멈춤·보상 없음 몸이다. 클립마다 전투 난수(PlayerCombat._rng)와 게임 난수를 같은 씨앗(716)으로 시작한다. 피해 범위·치명률·무기 불은 대본이 한 대마다 직접 넣는다.
- `01_basic` 칼 연타(다섯 몸 무리): 보통 셋 → 큰 타격 90 → 칼+무기 불(불 우세 16) → 칼+무기 불(불 30% 16)
- `02_crit` 한 몸: 보통 12 → 치명 20 → 큰 치명 121
- `03_fire` 무리 셋: 화염부 던지기(터짐 + 화상 틱) → 부적 진(불) 틱
- `04_cold` 무리 셋: 빙결부 던지기 → 부적 진(한기) 틱
- `05_aoe8` 둘레 여덟: 회오리베기(치명 40%, 셋 처치)
- `06_kill` 칼 처치 → 치명 처치 → 화염부 처치
- `07_bulgasari_heat` 불가살이(멈춤): 철갑 칼 둘(회색) → 달아오름 → 칼 둘(판 a = 주황 채움, 판 d = 주황 후광). 몸이 커서 숫자가 작고 머리 위 대사와 겹친다. 판정용으로는 약하므로 사진에서는 뺐다.

**같은 숫자인지 확인한 결과**(`events.json`): 세 판 모두 프레임 수가 같다. 01·02·05·07은 피해 숫자·몸·치명까지 판 A와 같다. 부적 던지기 터짐 숫자만 판마다 1~4 다르다(03·04 첫 터짐, 06 화염부 처치). 부적 비행 쪽 난수가 씨앗 밖이라 그렇고, #698 README의 화염부와 같은 현상이다. 진 틱·화상 틱 숫자는 같다.

## 판정용 (가공본, h264 crf 24)
| 파일 | 내용 |
|---|---|
| `716_A_N716_sbs.mp4` | 「지금」 \| 「새 숫자(강)」을 나란히 놓고 클립 7개를 1배속으로 잇는다(36.5초, 7.0MB). 왼쪽 귀에 지금, 오른쪽 귀에 새 숫자 소리. 오른쪽 아래 f = 클립 프레임. |
| `716_A_N716_slow025.mp4` | 같은 나란히를 0.25배로 늦췄다. 클립마다 숫자가 튀는 창만 담았다(59.8초, 7.7MB, 소리 없음). 창 = 01 f204~340 · 02 f37~224 · 03 f75~200 · 04 f72~150 · 05 f56~137 · 06 f37~247 · 07 f160~240. |
| `716_N716_N716L_sbs.mp4` | 「새 숫자(강)」 \| 「새 숫자(약)」, 1배(36.5초, 7.0MB). 둘은 치명 움직임만 다르다. 색·합치기·처치는 같다. |

판정 사진 6장은 게임 저장소 `docs/art/716_damage_numbers/`에 있다. 치명·불·광역 8·섞인 한 방과 처치를 지금/새 숫자로 견준 4장, 새 숫자(강)의 치명·불을 적록 색약 시뮬과 견준 2장이다.

## 캡처 픽셀 판정 (`_measure/table.md`, 사양 §7 기준 = 채움 중앙 ≥ 4.5:1 · 불↔금니 색약 ΔE ≥ 12)
게임 저장소 `docs/design/damage_numbers_v2_log.md` §8에 표와 읽는 법을 적었다. 요약:
- 물리 12.4 · 한기 8.6 · 치명 6.3~11.1 · 불 처치 6.6이다. 부적 화염 터짐은 4.5로 기준선에 딱 걸렸고, 칼+무기 불은 5.1이다.
- **틱은 미달이다**: 화상 틱 3.7, 진(불) 틱 3.6이다(숯불 #D9623A 알파 0.75, 18). 판 A의 화상 틱은 5.6이었다.
- 불↔금니 색약 ΔE76: 화면에서 22.6~44.0으로 기준 ≥ 12를 넘는다. 헥스로 셈하면 15.0이다.

## 판별 원본 (capture_slice 산출)
`A/`·`N716/`·`N716L/` 아래의 `capture_raw.log`(NUMDEMO 줄 = 피해 프레임·양·몸·치명·처치), `manifest.json`, `contact_*.jpg`, `README.md`는 git에 있다.
**git에 넣지 않은 것**(D-100 — 카드 합 ≥ 50MB · 원본 ≥ 10MB)은 이 PC에만 둔다. 드라이브로 옮길 때는 `JoseonHunters_raw/716/`에 둔다.

| 파일 | 크기 | SHA256 앞 16 |
|---|---|---|
| `A/capture_master.avi` | 233,752,120 B | 01d306883f338d8d |
| `N716/capture_master.avi` | 233,995,978 B | d297719ffd2f6f83 |
| `N716L/capture_master.avi` | 233,926,398 B | 48863a2c36ddc523 |
| `<판>/0N_<클립>.mp4` (클립 7 × 판 3, crf 18 + 게임 소리) | 판마다 약 16.3MB | — |

`_frames/`(프레임 png)·`_segments/`(조각 영상·ffmpeg 그래프)·`_labels/`·`_measure/*.png`(마스크 확인 그림)는 스크립트로 다시 만들 수 있어서 넣지 않았다.

## 보조 스크립트 (`_scripts/`)
- `events.py` — raw 로그를 `events.json`과 표로 바꾼다.
- `make_media.py` — 나란히 영상을 만든다.
- `stills.py` — 판정 사진과 색약 사본을 만든다.
- `measure.py` — 캡처 픽셀 대비와 ΔE를 잰다.
- `colorsci.py` — Machado 2009 적록 색약 행렬, CIELAB, ΔE76/2000, WCAG 대비 계산을 담았다.
- `strip.py`·`grid.py` — 확인용 띠와 눈금을 그린다.
