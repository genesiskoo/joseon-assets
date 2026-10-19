"""#825 도호 재오디션 생성 — 성우 4 + 지금 성우 × 설정 2 × 대사 3. 성공 영수증이 있으면 다시 부르지 않는다."""
import hashlib, json, sys, time, urllib.request, urllib.error
from pathlib import Path
HERE = Path(__file__).resolve().parent
ENV = Path("C:/workspace/joseon/.env")
KEY = next(l.split("=", 1)[1].strip().strip('"') for l in ENV.read_text(encoding="utf-8").splitlines() if l.startswith("ELEVENLABS_API_KEY="))
MODEL = "eleven_v4"
VOICES = {
    "now": ("v1is6KLMuZWgumQgKSOi", "지금 성우 (K-Actor Lee)"),
    "theo": ("CxErO97xpQgQXYmapDKX", "Theo — 따뜻·부드러운 대화체"),
    "harry": ("pb3lVZVjdFWbkhPKlelB", "Harry Kim — 즉흥 대화체"),
    "yohan": ("4JJwo477JUAx3HV0T7n7", "Yohan Koo — 자신감 있는 30대"),
    "mrk": ("LKOcTG4J4tYTPR9DnLeM", "Mr. K — 감정 표현 대화체"),
}
LINES = {
    "banter": ("NPC_SHAMAN_OFFER_2", "할매, 술부터… 아, 분위기 아니구먼.", "[casually] 할매, 술부터… [pause] [awkward chuckle] 아, 분위기 아니구먼."),
    "swagger": ("NPC_MERCHANT_AFTER_2", "해와 달도 삼키려던 불개라더니, 내 칼은 못 삼키더구먼.", "[smug, relaxed] 해와 달도 삼키려던 불개라더니, [chuckles] 내 칼은 못 삼키더구먼."),
    "serious": ("EV_GUMIHO_INTRO_5", "보러 온 건 맞아. 네 뜻대로 할지는 다른 얘기지.", "[low, calm] 보러 온 건 맞아. [pause] 네 뜻대로 할지는… 다른 얘기지."),
}
SETTINGS = {
    "a": ("자연 — 안정 0.5 · 태그 없음 (지금 게임과 같은 설정)", {"stability": 0.5, "similarity_boost": 0.75}, False),
    "b": ("연기 — 안정 0.0(창의) · 연기 태그", {"stability": 0.0, "similarity_boost": 0.75}, True),
}
plan = {r["id"]: r for r in json.load(open(HERE / "plan_manifest_snapshot.json", encoding="utf-8"))["lines"]}
out = HERE / "audio"; out.mkdir(exist_ok=True)
def sha(b): return hashlib.sha256(b).hexdigest()
jobs = []
for vk, (vid, _) in VOICES.items():
    for sk, (_, settings, tagged) in SETTINGS.items():
        if vk == "now" and sk == "a":
            continue  # 지금 게임 음원을 그대로 기준으로 쓴다
        for lk, (lid, plain, tags) in LINES.items():
            row = plan[lid]
            body = {"text": tags if tagged else plain, "model_id": MODEL, "language_code": "ko", "voice_settings": settings}
            if row.get("previous_text"): body["previous_text"] = row["previous_text"]
            if row.get("next_text"): body["next_text"] = row["next_text"]
            jobs.append((f"{vk}_{sk}_{lk}", vid, body))
print("JOBS", len(jobs), "chars", sum(len(b["text"]) for _, _, b in jobs))
if "--dry" in sys.argv: sys.exit(0)
for name, vid, body in jobs:
    rec_path = out / f"{name}.json"
    req_sha = sha(json.dumps({"voice_id": vid, "body": body}, ensure_ascii=False, sort_keys=True).encode())
    if rec_path.exists():
        rec = json.load(open(rec_path, encoding="utf-8"))
        if rec.get("ok") and rec.get("request_sha256") == req_sha and (out / f"{name}.mp3").exists() and sha((out / f"{name}.mp3").read_bytes()) == rec.get("mp3_sha256"):
            print("SKIP", name); continue
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
        data=json.dumps(body).encode(), headers={"xi-api-key": KEY, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    rec = {"name": name, "voice_id": vid, "request": body, "request_sha256": req_sha, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
            rec.update(ok=True, bytes=len(data), mp3_sha256=sha(data), request_id=r.headers.get("request-id"), character_cost=r.headers.get("character-cost"))
            (out / f"{name}.mp3").write_bytes(data)
            print("OK", name, len(data), "cost", rec["character_cost"])
    except urllib.error.HTTPError as e:
        rec.update(ok=False, status=e.code, error=e.read().decode("utf-8", "replace")[:500])
        print("FAIL", name, e.code, rec["error"][:200])
    json.dump(rec, open(rec_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
