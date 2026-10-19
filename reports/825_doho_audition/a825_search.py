"""#825 도호 재오디션 — 라이브러리 한국어 남성 성우 검색(무료 조회)."""
import json, os, sys, urllib.request, urllib.parse
from pathlib import Path
ENV = Path("C:/workspace/joseon/.env")
KEY = next(l.split("=", 1)[1].strip().strip('"') for l in ENV.read_text(encoding="utf-8").splitlines() if l.startswith("ELEVENLABS_API_KEY="))
def get(path, **q):
    url = "https://api.elevenlabs.io" + path + ("?" + urllib.parse.urlencode(q) if q else "")
    req = urllib.request.Request(url, headers={"xi-api-key": KEY})
    return json.load(urllib.request.urlopen(req, timeout=60))
sub = get("/v1/user/subscription")
print("CREDITS", sub.get("character_count"), "/", sub.get("character_limit"), sub.get("tier"))
seen, rows = set(), []
for age in ("young", "middle_aged", ""):
    for page in range(3):
        q = {"page_size": 100, "language": "ko", "gender": "male", "page": page}
        if age: q["age"] = age
        d = get("/v1/shared-voices", **q)
        for v in d.get("voices", []):
            if v["voice_id"] in seen: continue
            seen.add(v["voice_id"])
            rows.append({k: v.get(k) for k in ("voice_id", "public_owner_id", "name", "accent", "age", "descriptive", "use_case", "category", "description", "cloned_by_count", "usage_character_count_1y", "preview_url", "verified_languages", "free_users_allowed", "notice_period")})
        if not d.get("has_more"): break
json.dump(rows, open("library_ko_male.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("VOICES", len(rows))
rows.sort(key=lambda r: -(r.get("usage_character_count_1y") or 0))
for r in rows[:60]:
    print(f'{r["voice_id"]} | {r["name"][:40]} | {r.get("age")} | {r.get("descriptive")} | {r.get("use_case")} | {r.get("category")} | use1y={r.get("usage_character_count_1y")} | {(r.get("description") or "")[:90]}')
