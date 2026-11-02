"""joseon-assets 커밋 검사 — 자료관 장부(catalog.json)가 줄어드는 커밋을 막는다 (게임 카드 #1127).

11-02 사고: 남들이 인덱스로만 커밋하는 사이 본 폴더 작업 파일이 10-23 판에 머물러, 그대로 커밋됐다면
자료 382 → 74(순감 308)가 될 뻔했다. 장부 규칙 = 지우지 않는다(게임 docs/design/character_art_catalogue_ops.md §4).
HEAD에 있는 asset_id가 스테이징된 판에서 하나라도 빠지면 거절한다. 일부러 지울 때만 CATALOG_SHRINK_OK=1.
"""
import json
import os
import subprocess
import sys

CAT = "catalog/characters/catalog.json"


def git(*args):
    return subprocess.run(["git", *args], capture_output=True)


def asset_ids(raw):
    return {a.get("asset_id") for a in json.loads(raw.decode("utf-8")).get("assets", [])}


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    names = git("-c", "core.quotepath=false", "diff", "--cached", "--name-only", "--diff-filter=AMD")
    if CAT not in names.stdout.decode("utf-8").splitlines():
        return 0
    head = git("show", "HEAD:" + CAT)
    if head.returncode != 0:
        return 0  # HEAD에 장부가 없다(첫 등록)
    staged = git("show", ":" + CAT)
    missing = []
    if staged.returncode != 0:
        why = "장부 파일을 지우는 커밋"
    else:
        try:
            old, new = asset_ids(head.stdout), asset_ids(staged.stdout)
        except (ValueError, UnicodeDecodeError) as e:
            why = "스테이징된 장부가 JSON으로 안 읽힌다 (%s)" % e
        else:
            missing = sorted(old - new, key=str)
            if not missing:
                return 0
            why = "HEAD 자료 %d건이 빠진다 (HEAD %d → 새 판 %d)" % (len(missing), len(old), len(new))
    if os.environ.get("CATALOG_SHRINK_OK") == "1":
        print("[joseon-assets 장부 검사] CATALOG_SHRINK_OK=1 이라 통과시킴 — " + why, file=sys.stderr)
        return 0
    lines = ["[joseon-assets 장부 검사] 자료관 장부가 줄어드는 커밋이라 막았습니다: " + why]
    if missing:
        lines.append("  빠지는 asset_id 예: " + ", ".join(map(str, missing[:8])) + (" …" if len(missing) > 8 else ""))
    lines += [
        "→ 작업 파일이 낡았을 수 있습니다(남이 인덱스로만 커밋한 사이). HEAD 판 위에 내 기록만 다시 얹으세요:",
        "  git show HEAD:" + CAT + " 를 새 판으로 → 내 asset 추가 → 같은 서식(indent 2, ensure_ascii=False)으로 저장",
        "  장부 규칙 = 지우지 않는다(게임 docs/design/character_art_catalogue_ops.md §4). 일부러 지울 때만 CATALOG_SHRINK_OK=1",
    ]
    print("\n".join(lines), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
