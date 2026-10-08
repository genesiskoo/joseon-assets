# #87 생성 프롬프트 기록

입력 화풍은 #393 A 채색 시안과 D2b 소지품 판이다. 아래는 built-in image_gen에 지정한 부품별 아트 지시를 보존한 기록이다. 글자·아이콘·인게임 배경은 생성하지 않았다.

## panel_source_v1.png

Transparent-background orthographic front view of one Joseon dark-fantasy action RPG window panel. Wide rectangular empty matte soot-black lacquered Korean wood panel, restrained aged brass rectangular corner plates and traditional straight joinery. Keep the central 85% low contrast and nearly neutral dark charcoal brown, subtly visible grain; straight continuous top, bottom and side rails suitable for 9-slice stretching, fixed decorative corners only. No western baroque curves, parchment, bright reddish wood, text, glyphs, icons, objects, perspective, cast shadow or surrounding UI. Image should read clearly at a small game resolution and match the painted H1 key-art style.

## button_source_v1.png

Transparent-background orthographic front view of a single extra-wide, shallow rectangular Joseon wood UI button. Matte near-black lacquered timber, tiny worn brass corner joinery and hairline trim, quiet blank dark center for a Godot-rendered Korean label. Straight continuous horizontal rails, symmetric fixed ends suitable for 9-slice. No text, letter, symbol, icon, bevelled western ornament, parchment, perspective, cast shadow or background. Same understated painted material as the panel.

## orb_source_v1.png

Transparent-background orthographic front view of one circular Korean dark-fantasy life/mana orb rim. A narrow ring of soot-black wood and aged brass with a subtle smoky glass arc at top. Fully transparent central aperture and fully transparent exterior so the Godot red/blue fill shows through. Symmetric round outline, no liquid fill, no stat value, face, guardian statue, text, icon, perspective, cast shadow or background. Keep ornament low contrast, matching the panel material.

`prepare_skin.py`은 생성 뒤 알파 여백 제거와 리샘플만 수행하며, 결과와 수치는 `manifest.json`에 저장한다.
