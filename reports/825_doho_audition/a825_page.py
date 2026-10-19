"""#825 오디션 듣기 판 — 음량 맞춘 mp3를 data URI로 넣은 한 장짜리 HTML."""
import base64, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1])
VOICES = [
    ("now", "지금 성우", "Professional K-Actor Lee · 지금 게임에 들어간 목소리. 「자연」 칸 = 게임 음원 그대로"),
    ("theo", "Theo", "따뜻하고 부드러운 대화체 · 중년"),
    ("harry", "Harry Kim", "즉흥 대화·팟캐스트용 · 차분하고 자연스러운 말투"),
    ("yohan", "Yohan Koo", "자신감 있고 단단한 30대"),
    ("mrk", "Mr. K", "감정 표현·자연스러운 대화체 · 젊은 편"),
]
LINES = [
    ("banter", "능청", "할매, 술부터… 아, 분위기 아니구먼.", "무당 할매가 봉인 얘기를 꺼낼 때"),
    ("swagger", "허세", "해와 달도 삼키려던 불개라더니, 내 칼은 못 삼키더구먼.", "흑랑을 잡고 김 영감에게"),
    ("serious", "진지", "보러 온 건 맞아. 네 뜻대로 할지는 다른 얘기지.", "구미원에서 구미호와 마주쳤을 때"),
]
SETS = [("a", "자연", "안정 0.5 · 태그 없음 (지금 설정)"), ("b", "연기", "안정 0.0 · 연기 태그 [능청·웃음·뜸]")]
audio = {}
for p in sorted((HERE / "listen").glob("*.mp3")):
    audio[p.stem] = "data:audio/mpeg;base64," + base64.b64encode(p.read_bytes()).decode()
data = {"voices": VOICES, "lines": LINES, "sets": SETS}
tpl = (HERE / "a825_page.html").read_text(encoding="utf-8")
html = tpl.replace("/*DATA*/", "const DATA = " + json.dumps(data, ensure_ascii=False) + ";\nconst AUDIO = " + json.dumps(audio) + ";")
OUT.write_text(html, encoding="utf-8")
print(OUT, len(html) // 1024, "KB", len(audio), "clips")
