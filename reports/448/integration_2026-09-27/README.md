# #448 실제 공통 UI 렌더 검수

기준 game=2c272968ee27c118af8d7a920161a8dc9fabd1f7 / assets-main=16f913dcdaaf948762709f88994ee96213bd3392. 내장 image_gen 원본6장, 실제 Godot4.7.2 Forward+ 렌더3회 PASS·stderr0. 현재 ItemDef·UiSkin을 사용하며 게임 파일은 미반입. 승인표본 픽셀은before/after 동일, 원본/현재데이터/최종알파·점유6/6 검증. overview는Pillow확대 접촉판, 나머지3개는실제GPU캡처.
