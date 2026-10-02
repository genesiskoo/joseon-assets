extends RefCounted
## #550: git 작성자·AGENTS의 실제 도구. 원문 법적 고지는 배포에도 포함한다.
const LINES := [
	"기획·제작·개발    jaehoi koo (genesiskoo)",
	"AI 개발 보조       Claude Code · Codex",
	"아트·3D 제작       GPT Image · Comfy · Tripo · Meshy",
	"동작·음악 제작     Mixamo · Suno",
	"게임 엔진            Godot Engine — MIT",
	"대화 시스템        Nathan Hoad · Dialogue Manager — MIT",
	"궁서 폰트            Batang and Gungsuh Project Authors — OFL 1.1",
	"개발 도구            Godot AI · Aseprite Wizard — MIT",
	"조선헌터스 · 첫 막 제작 중",
]
const DIALOGUE_LICENSE := """
MIT License

Copyright (c) 2022-present Nathan Hoad and Dialogue Manager contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


const GODOT_AI_LICENSE := """
MIT License

Copyright (c) 2025 Godot AI contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

const ASEPRITE_LICENSE := """
The MIT License (MIT)

Copyright (c) 2020 Vinicius Gerevini

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


static func license_text() -> String:
	var sections: PackedStringArray = ["Godot Engine\n" + Engine.get_license_text(), "Dialogue Manager\n" + DIALOGUE_LICENSE, "Godot AI\n" + GODOT_AI_LICENSE, "Aseprite Wizard\n" + ASEPRITE_LICENSE,
		"Gungsuh / Batang font\n" + FileAccess.get_file_as_string("res://assets/fonts/gungsuh/OFL.txt")]
	var engine_licenses: Dictionary = Engine.get_license_info()
	for name in engine_licenses:
		sections.append("Godot third-party license: " + String(name) + "\n" + String(engine_licenses[name]))
	for component in Engine.get_copyright_info():
		var label := String(component.get("name", ""))
		for part in component.get("parts", []):
			sections.append(label + "\n" + "\n".join(part.get("copyright", [])) + "\nLicense: " + String(part.get("license", "")))
	return "\n\n".join(sections)
