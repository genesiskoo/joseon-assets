# #746 캐릭터 자료관 조회본 검증

- 입력 정본: `catalog/characters/catalog.json`, 49자료·8인물·9형태.
- 정본 SHA256: `ef6b8579be86d6af50c4c10c79afc684d6f9d234307732b1f942f23a7fa4cf12`.
- C 검사 입력: `reports/744/catalogue-validation.json`, ok=true. 모델 캡처 7건 current, 게임 화면 6건 indeterminate이며 월드 표시 확인과 최신성을 구별한다.
- 출력: `catalog/characters/index.html` 4,201,101B, `inline.html` 798,051B. 인라인 이미지 최대280px·WebP quality45; 자세한 원본은 로컬 경로로 확인.
- 원본·JSON·판정·검증 근거는 수정하지 않았다. 영구 assets/game 루트에서 읽었고 overlay 입력을 사용하지 않았다.
- Python7검증·JS문법·UI 기본선택/판정문구/촬영요약 및 없는 매체의 상태 분리·connected 전용 binding 회귀검사 통과. 인라인 fragment에 doctype/head/fetch 없음 확인.
- 본진 브라우저 검수: 본체 H01 추천·미승인과 실제 흑랑 모델을 나란히 확인, definition_only 인물을 현재 연결에서 제외, 원본 파일 경로 안내·독립 상태 표시 확인. 최종 조건 요약은 짧은 촬영 종류·크기·카메라·동작/시나리오와 비교 한계이며 전문은 근거 상세에 유지.

## 재빌드

```powershell
python catalog/characters/viewer/build_catalogue.py --catalog C:/workspace/joseon-assets/catalog/characters/catalog.json --assets-root C:/workspace/joseon-assets --game-root C:/workspace/joseon --validation C:/workspace/joseon-assets/reports/744/catalogue-validation.json --output catalog/characters --standalone-url file:///C:/workspace/joseon-assets/catalog/characters/index.html
python catalog/characters/viewer/test_viewer.py
node --check catalog/characters/viewer/app.js
node catalog/characters/viewer/test_ui.js
```

인라인 발표 파일은 본진이 대화의 writable visualization 경로로 복사한다. 외부 게시·유료 생성은 수행하지 않았다.

목록 썸네일은 host 버튼 바깥의 투명한 갤러리에 표시하고, native 버튼과 이미지 클릭으로 같은 선택 동작을 제공합니다. 누락된 매체 탭은 load/world 미검사·freshness 판정불가이며 모델의 성공 증거를 재사용하지 않습니다. 정적 그룹 연결과 selected 매체 연결을 구분하고 정의만 있는 binding은 연결 상세에 보존합니다.

