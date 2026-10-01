# #534 상위 물약 4종 — #274 잔여 생산

기본 HP/MP 승인 원화의 SHA와 병 계열을 앵커로 보존한다. 2·3단 물약을 재료·형태·마개·마감으로 더 값져 보이게 만들며 기존 기본 아이콘을 수정하지 않는다. Comfy Cloud GPT Image 2.5 Flare high로 먼저 2단 HP/MP 각 1장을 생산해 실제 RGBA/알파와 형태를 확인한 후 3단을 진행한다. 프롬프트·작업 ID·참조 및 결과 SHA를 기록한다.

실제 ItemDef의 tier는 모두 1이며 효능 단계 2·3은 장비 티어가 아니다. 1×1, 80×80 RGBA, max_stack10. 아래 수치와 공유 아이콘 경로를 manifest와 실제 정의에서 대조한다. 원화 후보 제작은 아직 채택이나 게임 반입이 아니다.

| 효능 단계 | HP | MP | ilvl |
|---|---|---|---|
| 기본 | 쌍화탕40 | 생맥산25 | 1 |
| 2단 | 십전대보탕80 | 총명탕50 | 6 |
| 3단 | 경옥고140 | 공진단90 | 13 |

생성 원본과 BiRefNet clean 원본은 각각 정확한 파일 SHA로 보존한다. 원본 RGB에서 alpha0 뒤에 남은 배경색은 실제 RGBA 합성판으로 판단한다. 1차 네 병은 native→clean RGB 차이0이며 배경 제거는 alpha만 바꿨다. 패킹은 기존 clean alpha의 used bbox를 자른 뒤 premultiplied Lanczos로 비율을 유지해 80×80에 가운데 넣는다. 8% 여백을 반올림한 6px을 두고 별도 alpha 임계값·수작업 마스크·새 글자·등급 테두리·glow는 쓰지 않는다.

현재 UiSkin.item_icon의 원화 경로와 선형 필터를 실제로 호출한다. ImageTexture.take_over_path는 `res://assets/sprites/ui/icons_a/qa534/` 아래의 서로 다른 검사 경로에만 적용하여 로드된 ItemDef.icon이나 기본 PNG를 바꾸지 않는다. 실제 가방은40px/여백8, 좌판은48px/여백3, 현재 HUD벨트는42px/여백8이다. 벨트30·36px은 축소 스트레스 검사다. 원화/80px→현재 세 슬롯, 검정, 회색조를 기본 포함6종으로 렌더한다.

1차 검수에서 HP3 금속 목·각인과 MP3 운문·금속 마감은 원화/80px에서 보였다. HP1·2는 같은 종이마개 계열이며 작은 칸의 차이가 주로 병 비례·광택에 남았다. MP2·3는 가방40/벨트42에서 실루엣이 거의 같고30·36px에서 구별이 약했다. 자동 검증 PASS는 파일 계약과 렌더 실행의 결과이며 단계 구별의 채택 판정은 포함하지 않는다.

보정3은 Comfy GPT2.5→BiRefNet을 같은 API 그래프에서 실행했다. HP2는 평평한 목재 마개·넓은 목·황동 어깨띠, MP2는 넓은 목·단일 둥근 몸통, MP3는 두 몸통·넓은 황동 마개·띠로 바뀌었다. HP3은1차 clean을 그대로 유지했다. raw3/clean3은 서로 RGB 차이0이며 원본/초기 source4는 버전별로 보존했다. 실제40px 가방/42px 벨트에서 MP2·3 몸통과 마개 형태 차이가 보이고 HP2의 매끈한 평마개도 기본의 접힌 종이마개와 구별된다. 30px 벨트는 여백8 뒤 그림 높이가14px뿐이므로 운문·끈·옥알 등의 세부는 약하다. 작은 단계 구별의 근거는 실루엣·큰 마개·금속 띠이며 세부 새김만으로 등급을 읽는다고 주장하지 않는다.

1차 전체 원본·runtime80·manifest·검수 사진·raw는 `reports/534/packing_initial/`에 보존했다. 최신 결과는 `manifest.json`, 원본별 SHA/마스크와 실제 UI 기록은 `verification.json`, 원화 작업 ID/프롬프트/그래프/응답은 `reports/534/comfy_*`에 있다. `audit_receipts_534.py`는 이 카드의 텍스트/JSON에서 credential 필드·토큰·서명 URL을 검사하며 비밀 값을 출력하지 않는다.

재현은 Python(Pillow/numpy)과 현재 게임 프로젝트/Godot4.7.2를 사용한다. `--game`은 이 카드에서 hash를 기록한 게임 작업 트리다. 보정 소스 맵에는 네 item_id 각각의 generated/clean receipt 상대 경로와 고유 `source_key`를 넣는다. 원본 source는 덮어쓰지 않으며 `_v2` 원본을 추가하고, runtime80의 초기 버전은 별도 증거 폴더에서 보존한다.

```powershell
$qaGame = 'C:/Users/FORYOUCOM/.codex/worktrees/534-potion-grade-art/joseon'
$qaProd = 'workbench/production/item_icons_534'
python "$qaProd/prepare_534.py" --game $qaGame --pack --selection "$qaProd/selected_sources.json"
python "$qaProd/prepare_534.py" --diagnostic --selection "$qaProd/selected_sources.json"
& "$qaProd/render_534.ps1" -Game $qaGame
python "$qaProd/review_534.py" --game $qaGame
python "$qaProd/audit_receipts_534.py"
```

현재 패키지는 selected_sources 맵을 써서 최신 후보를 재현한다. 초기 소스/80px/원화·실제 UI판은 packing_initial에서 읽는다. 새 원본이 선택돼 있어도 기존 source 파일은 변경되지 않는다. review는 그림/정의/UI189파일의 원본 SHA, 실제6종 정의, source/clean RGB, RGBA80와5개 Godot 렌더 모드/오류0을 검증한다. game `docs/art/534_potion_grade`의 JPG6은1280폭/각300KB 이하이며 before/after 원화판·실제 UI판4장, 최종벨트·alpha판2장으로 구성한다. 검정·회색조 전체판과 PNG는 자산 reports에 보존한다. before/after의 타이틀·기본2·미보정HP3 영역은 픽셀까지 대조해 동일 구도를 확인한다.

최초 보정 패킹 때 상대 selection 경로를 절대 ROOT에 relative_to해서 ValueError가 발생했다. resolve를 먼저 적용해 교정했으며 원본과 runtime은 그대로였다. 실패 raw 전문은 `reports/534/packing/packing_failed_relative_selection.txt`, 성공 패킹/마스크/Godot raw는 같은 reports의 파일에 보존했다.

왜 이 구조인가: 현재 작은 칸에 실제 공용 UiSkin을 적용하면 단계 차이와 마스크 문제를 함께 판단할 수 있고, 소스/패킹/반입 SHA를 각각 추적할 수 있다. 기존 공유 아이콘을 덮거나 임시 ItemDef를 만드는 방식은 채택 전 표시와 데이터를 바꾸므로 기각한다.
