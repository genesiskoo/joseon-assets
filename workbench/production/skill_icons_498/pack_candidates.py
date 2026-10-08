"""#498: provenance-preserving resize, hash checks, and native QA JPEG compression."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image

PACK = Path(__file__).resolve().parent
ASSETS = PACK.parents[2]
REPORT = ASSETS / "reports" / "498"
ROUND = REPORT / "2026-10-02_round1"
REVISION = REPORT / "2026-10-02_revision1"
SELECTED = {
    "leap_slash": ("도약 베기", "active", "round1"),
    "seal_array": ("부적 진", "active", "revision1"),
    "blade_storm": ("칼바람", "active", "revision1"),
    "breath": ("조식", "passive", "revision1"),
    "combo": ("연격", "passive", "round1"),
    "pouch": ("부적 주머니", "passive", "revision1"),
    "scatter": ("부적 흩뿌리기", "passive", "round1"),
    "sword_mastery": ("검 숙련", "passive", "round1"),
    "talisman_rain": ("부적 비", "active", "round1"),
    "thrust": ("찌르기", "active", "round1"),
}
EXISTING = {"slash": "참격", "lunge": "돌진 베기", "whirlwind": "회오리"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(ASSETS).as_posix()


def local_reference(recorded_path: str) -> Path:
    normalized = recorded_path.replace("\\", "/")
    # Requests remain immutable; only resolving their local copy changes after checkout relocation.
    for marker in ("/workbench/production/skill_icons_498/", "/reports/498/"):
        if marker in normalized:
            return ASSETS / (marker.lstrip("/") + normalized.split(marker, 1)[1])
    return Path(recorded_path)


def resize(source: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        if image.size != (1024, 1024):
            raise ValueError(f"Unexpected original size: {source}: {image.size}")
        image.convert("RGBA").resize((128, 128), Image.Resampling.LANCZOS).save(output)


def provenance(source: Path) -> dict:
    job_path = source.with_suffix(".job.json")
    job = json.loads(job_path.read_text(encoding="utf-8"))
    if job["state"] != "downloaded" or sha(source) != job["output_sha256"]:
        raise ValueError(f"Original job/hash does not match: {source}")
    prompt_path = source.with_suffix(".prompt.txt")
    prompt_bytes = prompt_path.read_bytes()
    # The preserved text artifact has one trailing LF; the job hashes the sent prompt itself.
    sent_prompt_sha = hashlib.sha256(prompt_bytes.removesuffix(b"\n")).hexdigest()
    if sent_prompt_sha != job["prompt_sha256"]:
        raise ValueError(f"Prompt hash does not match: {prompt_path}")
    for reference in job.get("reference_images", []):
        if sha(local_reference(reference["path"])) != reference["sha256"]:
            raise ValueError(f"Reference hash does not match: {reference['path']}")
    return {
        "asset": job["asset"],
        "source": rel(source),
        "source_sha256": sha(source),
        "source_size": job["actual_dimensions"],
        "job_id": job["prompt_id"],
        "provider": job["provider"],
        "model": job["model"],
        "quality": job["quality"],
        "job_record": rel(job_path),
        "prompt_record": rel(prompt_path),
        "prompt_sha256": job["prompt_sha256"],
        "prompt_file_sha256": sha(prompt_path),
        "workflow_record": rel(source.with_suffix(".api.json")),
        "history_record": rel(source.with_suffix(".history.json")),
        "reference_images": job.get("reference_images", []),
        "state": job["state"],
    }


def pack(game_root: Path) -> None:
    originals = []
    candidates = []
    for uid, (name, kind, version) in SELECTED.items():
        base = ROUND / f"{uid}.png"
        originals.append(provenance(base))
        source = REVISION / f"{uid}_v2.png" if version == "revision1" else base
        if version == "revision1":
            originals.append(provenance(source))
            resize(base, PACK / "qa" / "revision_before" / f"{uid}.png")
        output = PACK / "game" / f"{uid}.png"
        resize(source, output)
        candidates.append({
            "id": uid, "display_name": name, "kind": kind,
            "selected_version": version, "selected_source": rel(source),
            "source_sha256": sha(source), "game_path": output.relative_to(PACK).as_posix(),
            "game_sha256": sha(output), "game_size": [128, 128], "mode": "RGBA",
            "alpha_extrema": list(Image.open(output).getchannel("A").getextrema()),
            "review_status": "candidate_for_pd_review", "game_intake": False,
        })
    references = []
    for uid, name in EXISTING.items():
        source = game_root / "assets" / "sprites" / "ui" / "icons_a" / "skills" / f"{uid}.png"
        target = PACK / "qa" / "approved" / f"{uid}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        with Image.open(target) as image:
            size = list(image.size)
        if size != [128, 128]:
            raise ValueError(f"Unexpected existing icon size: {source}: {size}")
        references.append({"id": uid, "display_name": name, "kind": "approved",
                           "game_path": target.relative_to(PACK).as_posix(), "sha256": sha(target),
                           "source_path": source.as_posix(), "size": size})
    snapshots = []
    for source_rel, target_rel in [
        ("ui/ui_skin.gd", "qa/ui_skin_snapshot.gd"),
        ("assets/sprites/ui/skin/slot.png", "qa/assets/sprites/ui/skin/slot.png"),
    ]:
        source, target = game_root / source_rel, PACK / target_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        snapshots.append({"source": source.as_posix(), "snapshot": target_rel, "sha256": sha(target)})
    write_json(PACK / "manifest.json", {
        "card": 498, "status": "unapproved_candidates", "runtime_connected": False,
        "game_intake_count": 0, "packing_method": "full-frame RGBA Lanczos 1024 to 128; no semantic editing",
        "original_count": 14, "candidate_count": 10, "originals": originals,
        "candidates": candidates, "existing_approved": references, "ui_snapshots": snapshots,
        "ui_sizes": {"raw": [128, 60, 48, 30], "hud_small": {"slot": 30, "padding": 3},
                     "hud_main": {"slot": 60, "padding": 5}, "skill_tree": {"slot": 48, "padding": 3}},
        "native_qa": {"project": "qa/project.godot", "script": "qa/qa_godot.gd",
                      "size": [1280, 720], "modes": ["overview", "sizes_a", "sizes_b", "revisions"],
                      "output_dir": "reports/498/native_qa", "captured": False},
    })
    check()


def check() -> None:
    manifest = json.loads((PACK / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["card"] == 498 and len(manifest["candidates"]) == 10
    assert manifest["original_count"] == len(manifest["originals"]) == 14
    assert manifest["game_intake_count"] == 0 and not manifest["runtime_connected"]
    selected = []
    for original in manifest["originals"]:
        source = ASSETS / original["source"]
        assert provenance(source) == original
    for candidate in manifest["candidates"]:
        output, source = PACK / candidate["game_path"], ASSETS / candidate["selected_source"]
        assert sha(output) == candidate["game_sha256"] and sha(source) == candidate["source_sha256"]
        with Image.open(output) as packed, Image.open(source) as raw:
            expected = raw.convert("RGBA").resize((128, 128), Image.Resampling.LANCZOS)
            assert packed.mode == "RGBA" and packed.size == (128, 128)
            assert packed.tobytes() == expected.tobytes()
        selected.append({"id": candidate["id"], "version": candidate["selected_version"], "status": "PASS"})
    for reference in manifest["existing_approved"]:
        assert sha(PACK / reference["game_path"]) == reference["sha256"]
    for snapshot in manifest["ui_snapshots"]:
        assert sha(PACK / snapshot["snapshot"]) == snapshot["sha256"]
    write_json(REPORT / "packing_qa.json", {"card": 498, "status": "PASS", "originals": 14,
                                          "unchanged_originals_prompts_references": True, "selected": selected,
                                          "rgba128": True, "pixel_equals_full_frame_lanczos": True,
                                          "existing_approved_copies": 3, "game_intake_count": 0,
                                          "semantic_visual_review_automated": False})
    print("PACKING_498_PASS originals14/selected10/revision4/RGBA128/Lanczos/hashes/references/existing3/intake0")


def compress_native() -> None:
    outputs = []
    for source in sorted((REPORT / "native_qa").glob("native_*.png")):
        with Image.open(source) as image:
            image = image.convert("RGB")
            if image.width != 1280:
                raise ValueError(f"Native capture width must be 1280: {source}")
            target = source.with_suffix(".jpg")
            for quality in (88, 84, 80, 76, 72, 68, 64, 60):
                image.save(target, "JPEG", quality=quality, optimize=True)
                if target.stat().st_size <= 300_000:
                    break
            if target.stat().st_size > 300_000:
                raise ValueError(f"Could not fit JPEG byte budget: {target}")
            outputs.append({"source": rel(source), "output": rel(target), "bytes": target.stat().st_size,
                            "size": list(image.size), "quality": quality, "sha256": sha(target)})
    if not outputs:
        raise FileNotFoundError("No native_*.png captures exist; root must capture first")
    write_json(REPORT / "native_qa" / "jpeg_qa.json", {"card": 498, "status": "PASS", "outputs": outputs})
    print(f"JPEG_498_PASS native captures={len(outputs)} width1280 bytes<=300000; original PNG preserved")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--compress-native", action="store_true")
    args = parser.parse_args()
    if args.compress_native:
        compress_native()
    elif args.check:
        check()
    elif args.game_root:
        pack(args.game_root.resolve())
    else:
        parser.error("Choose --game-root, --check, or --compress-native")


if __name__ == "__main__":
    main()
