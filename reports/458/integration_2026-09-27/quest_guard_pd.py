from pathlib import Path
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
main = Path("C:/workspace/joseon")
game = Path("C:/Users/FORYOUCOM/.codex/worktrees/87-ui-wood-skin/joseon")
assets = main / "._tmp/assets_87"
ctx = json.loads((main / "tmp/quest_guard_context.json").read_text(encoding="utf-8"))
card = ctx["card"]
env = dict(os.environ, PYTHONIOENCODING="utf-8")

def run(command):
    proc = subprocess.run(command, cwd=main, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(proc.stdout.decode("utf-8-sig", errors="replace"), end="", flush=True)
    if proc.returncode:
        raise SystemExit(proc.returncode)
    return proc.stdout

assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=main).strip(), "Main has unrelated changes; preserve and stop state save"
validation = json.loads((assets / f"reports/{card}/integration_2026-09-27/verification.json").read_text(encoding="utf-8"))["validation"]
checks = validation["related_checks"]
p = main / "docs/STATE.md"
body = p.read_text(encoding="utf-8")
heading = "## 이번 주 (2026-09-27 기준)\n"
assert heading in body and f"Codex: #{card} " not in body
line = f"- 2026-09-27 Codex: #{card} 퀘스트 커서 버림 차단·툴팁 정합성 후보 game{ctx['game_commit'][:8]}/assets{ctx['assets_commit'][:8]} PD 확인. 단위53(item_ui37)/관련E2E12({checks}검사)/창70·76/부팅·러너 PASS. 정의67·PNG38 보존, 전후JPG6. WT87·자산87 깨끗함, 미병합·미push.\n"
assert len(line) <= 300
body = body.replace(heading, heading + line, 1)
body = body.replace("다음은 퀘스트 물건의 커서 버림·툴팁 정합성.", f"퀘스트 커서 버림·툴팁 #{card} 후보 PD 확인(전후6장).", 1)
p.write_text(body, encoding="utf-8", newline="\n")
run([sys.executable, "tools/doc_budget.py"])
run(["git", "add", "--", "docs/STATE.md"])
run(["git", "diff", "--cached", "--check"])
run(["git", "commit", "-m", f"docs(#{card}): 퀘스트 물건 UI 후보와 회귀검수 PD 확인 기록"])
ctx["state_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=main, text=True).strip()
question = f"현재 수정안 채택·병합 판정: 퀘스트 물건의 의도적 창 밖 버림은 막고 같은 물건을 커서에 유지, 툴팁은 들기/팔기·버리기 불가만 표시하며 판매가 제거. 일반 물건 버림·판매 안내와 가방가득참 닫기→발밑 보존→실제 이름표 회수 안전망은 유지. game{ctx['game_commit'][:8]}·검수assets{ctx['assets_commit'][:8]}, 기준{ctx['game_base'][:8]}. 단위53(item_ui37), 관련E2E12({checks}검사), 창모드before70/after76, 부팅SCRIPT ERROR0/오토로드10/10·주장면OK/러너5/5 PASS. 정의67·PNG38 SHA105 동일, 기준픽셀9 동일. 실제 전후3쌍 docs/art/{card}_quest_item_safety(각1280폭·300KB이하), 원본PNG/raw/재현대본/해시 자산 reports/{card}/integration_2026-09-27. 대화에 전후6장 표시. main은 이전승인 #457 반입 상태이며 새UI후보 미병합·미push. #169 문개방/#69 수하보스 대기. 권장: 이 수정안 채택·합쳐. 규칙 AGENTS §4: 눈·귀로 볼 카드는 PD 「합쳐」 뒤 착륙."
run([sys.executable, "tools/board.py", "pd", str(card), question])
run([sys.executable, "tools/board.py", "note", "457", f"후속 UI 정합성 #{card} 검수/커밋 완료, PD 확인. 원화/PNG와 ItemDef 수치 변경 없이 명시적 커서 버림 차단·판매가/불가능 조작 안내 제거. 실제 전후3쌍/단위53·관련E2E12 PASS, 가방 가득 참 닫기 안전망 회수도 실제 클릭으로 검증. game{ctx['game_commit'][:8]}, 미병합·미push."])
(main / "tmp/quest_guard_context.json").write_text(json.dumps(ctx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"card":card, "status":"PD confirmation", "game":ctx["game_commit"], "assets":ctx["assets_commit"], "state":ctx["state_commit"], "main_landed":False}))
