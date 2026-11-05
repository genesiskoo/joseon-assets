"""GLB에 박힌 베이스컬러 이미지 바이트를 옆 파일(<글b 이름>_<이미지 이름>.jpg)로 그대로 쓴다 — Godot 추출이 옛 옆 파일을 안 덮을 때(#793과 같은 길).
    python side_tex.py <작업 트리> <glb> <옆 파일 경로>"""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]).resolve() / "tools"))
sys.stdout.reconfigure(encoding="utf-8")
import albedo_ops as A  # noqa: E402

js, b = A.read_glb(sys.argv[2])
i = A.base_color_image(js)
im = js["images"][i]
bv = js["bufferViews"][im["bufferView"]]
data = b[bv.get("byteOffset", 0): bv.get("byteOffset", 0) + bv["byteLength"]]
assert im.get("mimeType") == "image/jpeg" and data[:3] == b"\xff\xd8\xff", (im.get("mimeType"), data[:4])
out = Path(sys.argv[3])
assert out.suffix.lower() == ".jpg" and out.stem.endswith("_" + im["name"]), (out, im["name"])
out.write_bytes(data)
print("옆 파일", out.name, len(data), "B · sha256", hashlib.sha256(data).hexdigest()[:12])
