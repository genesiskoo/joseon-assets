# #446 D1 T1 6종 실제 UI 렌더 검수

기준 = game main ec50b082 / assets main82558ef. source는내장image_gen6장, 실제Godot4.7.2GPU Compatibility 렌더3회(기존/후보/작은칸). Godot로그/빈stderr·원본PNG4·jpg4·verification을 보존한다. 현재게임의 공통UiSkin과실제ItemDef를 읽었으나 파일반입은하지 않았다. 승인D1 하단표본은before/after 동일픽셀. 데이터원본해시불변6/6, 원본/산출PNG알파·점유해시6/6. 확대판overview는Pillow, 나머지세PNG는실제GPU캡처.
