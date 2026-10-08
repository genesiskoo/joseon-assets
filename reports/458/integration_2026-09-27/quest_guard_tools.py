from pathlib import Path

main = Path("C:/workspace/joseon")
body = (main / "tmp/seal_capture.py").read_text(encoding="utf-8")
body = body.replace("tmp/seal_intake_context.json", "tmp/quest_guard_context.json").replace("{card}_d1_quest_seal_intake", "{card}_quest_item_safety").replace("--icon-intake-before", "--quest-safety-before")
(main / "tmp/quest_guard_capture.py").write_text(body, encoding="utf-8")
body = (main / "tmp/seal_run.py").read_text(encoding="utf-8")
body = body.replace("tmp/seal_intake_context.json", "tmp/quest_guard_context.json")
body = body[:body.index('elif mode == "land":')] + body[body.index('else:\n    raise ValueError(mode)'):]
(main / "tmp/quest_guard_run.py").write_text(body, encoding="utf-8")
print("Prepared capture/run wrappers for current quest safety card; no landing mode.")
