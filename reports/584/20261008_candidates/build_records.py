"""Preserve #584 outputs and record read-only measurements; no image repair."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

MAPPING = {
    "584_neutral_a": "neutral_a_v1.png",
    "584_neutral_b": "neutral_b_v1.png",
    "584_neutral_a_v2": "neutral_a_fit_attempt_v2_rejected.png",
    "584_neutral_b_v2": "neutral_b_fit_attempt_v2_rejected.png",
    "584_smile_a": "smile_a_v1.png",
    "584_smile_b": "smile_b_v1.png",
    "584_turnaround_a": "turnaround_a_v1.png",
    "584_turnaround_b": "turnaround_b_v1.png",
}
PRODUCTION = Path("workbench/production/dokkaebi-584")
REPORT = Path("reports/584/20261008_candidates")
MATTE = (230, 230, 230, 255)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bbox(mask):
    yy, xx = np.nonzero(mask)
    return None if not len(xx) else [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1]


def centroid(mask):
    yy, xx = np.nonzero(mask)
    return None if not len(xx) else [round(float(xx.mean()), 6), round(float(yy.mean()), 6)]


def measure(path: Path, asset: str):
    with Image.open(path) as im:
        source_mode = im.mode
        width, height = im.size
        rgba = np.array(im.convert("RGBA"))
    alpha = rgba[:, :, 3]
    m = alpha > 16
    b = bbox(m)
    values, counts = np.unique(alpha, return_counts=True)
    result = {
        "width": width, "height": height, "source_mode": source_mode,
        "alpha_present_in_source": "A" in source_mode or source_mode == "P",
        "alpha_min": int(alpha.min()), "alpha_max": int(alpha.max()),
        "alpha_0_pixels": int((alpha == 0).sum()), "alpha_255_pixels": int((alpha == 255).sum()),
        "alpha255_fraction_among_alpha_gt16": round(float((alpha == 255).sum()) / int(m.sum()), 9) if m.any() else 0,
        "alpha_histogram": {str(int(v)): int(c) for v, c in zip(values, counts)},
        "bbox_alpha_gt16_exclusive": b, "centroid_alpha_gt16": centroid(m),
        "alpha_occupied_pixels_gt16": int(m.sum()),
        "threshold_method": "RGBA alpha > 16; bbox right/bottom are exclusive; no alignment or rescaling",
        "canvas_edges_alpha_gt16": {"left_pixels": int(m[:, 0].sum()), "right_pixels": int(m[:, -1].sum()), "top_pixels": int(m[0, :].sum()), "bottom_pixels": int(m[-1, :].sum())},
    }
    if b:
        result.update({
            "top_margin_px": b[1], "top_margin_percent": round(100 * b[1] / height, 6),
            "bottom_clearance_px": height - b[3], "bottom_extent_percent": round(100 * b[3] / height, 6),
            "left_clearance_px": b[0], "right_clearance_px": width - b[2],
        })
    if asset != "turnaround":
        target_top = round(height * 0.08)
        result["dialogue_contract_diagnostics"] = {
            "requested_size": [1024, 1536], "actual_size_matches": [width, height] == [1024, 1536],
            "requested_top_margin_percent": 8, "nominal_cap_top_px": target_top,
            "alpha_gt16_pixels_in_nominal_top_margin": int(m[:target_top, :].sum()),
            "has_fully_opaque_pixel": bool((alpha == 255).any()),
            "has_transparent_background_pixel": bool((alpha == 0).any()),
            "geometry_clearance_measurement_is_not_semantic_crop_proof": True,
            "import_ready": False,
            "reason": "Visual/framing review remains unresolved; alpha statistics are diagnostics, not an import approval. No local repair applied.",
        }
    else:
        result["turnaround_diagnostics"] = {"requested_size": [3072, 1536], "actual_size_matches": [width, height] == [3072, 1536], "orthographic_and_identity_consistency": "requires visual review; not proven by alpha/bbox", "is_3d_asset": False}
    return result


def pair(neutral: Path, smile: Path):
    n = np.array(Image.open(neutral).convert("RGBA"))
    s = np.array(Image.open(smile).convert("RGBA"))
    if n.shape != s.shape:
        return {"comparable_same_canvas": False, "neutral_shape": list(n.shape), "smile_shape": list(s.shape)}
    nm, sm = n[:, :, 3] > 16, s[:, :, 3] > 16
    nb, sb = bbox(nm), bbox(sm)
    nc, sc = centroid(nm), centroid(sm)
    union = int((nm | sm).sum())
    same = np.all(n == s, axis=2)
    lower = np.zeros(nm.shape, dtype=bool)
    lower[int(n.shape[0] * 0.4):] = True
    lower &= nm | sm
    return {
        "comparable_same_canvas": True, "threshold_alpha_gt": 16,
        "alignment": "native canvas; no translation, warp or scale fit",
        "intersection_pixels": int((nm & sm).sum()), "union_pixels": union,
        "alpha_occupancy_iou": round(int((nm & sm).sum()) / union, 9),
        "silhouette_iou_caveat": "Alpha occupancy is only a silhouette proxy and includes any non-character alpha contamination; this is not a semantically segmented character-only silhouette IoU.",
        "neutral_bbox_exclusive": nb, "smile_bbox_exclusive": sb,
        "smile_minus_neutral_top_px": sb[1] - nb[1],
        "smile_minus_neutral_bbox_center_px": [round((sb[i] + sb[i + 2] - nb[i] - nb[i + 2]) / 2, 6) for i in range(2)],
        "smile_minus_neutral_mask_centroid_px": [round(sc[i] - nc[i], 6) for i in range(2)],
        "exact_rgba_equal_percent_canvas": round(float(same.mean()) * 100, 6),
        "diagnostic_lower_60pct_union_pixels": int(lower.sum()),
        "diagnostic_lower_60pct_changed_rgba_percent": round(float((~same & lower).sum()) / int(lower.sum()) * 100, 6),
        "diagnostic_roi_caveat": "Lower 60% is a fixed canvas diagnostic, not a semantic facial mask; changed pixels are not an identity verdict.",
        "expression_only_pixel_preservation": "not established by this diagnostic; manual facial-region review is also required",
        "automatic_pass": False,
    }


def preview(source: Path, destination: Path):
    with Image.open(source) as im:
        rgba = im.convert("RGBA")
        source_size = list(rgba.size)
        if rgba.width > 1280:
            rgba = rgba.resize((1280, round(rgba.height * 1280 / rgba.width)), Image.Resampling.LANCZOS)
        matte = Image.new("RGBA", rgba.size, MATTE)
        matte.alpha_composite(rgba)
        rgb = matte.convert("RGB")
        for quality in range(92, 49, -2):
            rgb.save(destination, "JPEG", quality=quality, optimize=True, subsampling=0)
            if destination.stat().st_size <= 300000:
                break
        else:
            raise RuntimeError(f"Preview exceeds 300000B: {destination}")
    return {"path": destination.as_posix(), "width": rgb.width, "height": rgb.height, "bytes": destination.stat().st_size, "sha256": sha(destination), "jpeg_quality": quality, "source_size": source_size, "conversion": "aspect-preserving width reduction only if width>1280; transparent pixels composited onto constant #E6E6E6 for JPEG; no crop or repair; original PNG unchanged"}


def remove_owned_csv_rows(contents: bytes) -> bytes:
    """Keep every unrelated CSV row byte-identical, including multiline rows."""
    decoded = contents.decode("utf-8-sig")
    lines = decoded.splitlines(keepends=True)
    reader = csv.reader(io.StringIO(decoded, newline=""))
    kept = []
    start = 0
    for row in reader:
        end = reader.line_num
        if len(row) <= 7 or not row[7].startswith(PRODUCTION.as_posix() + "/"):
            kept.extend(lines[start:end])
        start = end
    if start < len(lines):
        kept.extend(lines[start:])
    prefix = b"\xef\xbb\xbf" if contents.startswith(b"\xef\xbb\xbf") else b""
    return prefix + "".join(kept).encode("utf-8")


def verify(root: Path):
    manifest = json.loads((root / REPORT / "manifest.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader(io.StringIO((root / "art-direction/manifests/generations.csv").read_text(encoding="utf-8-sig"))))
    owned_rows = [r for r in rows if r["output_path"].startswith(PRODUCTION.as_posix() + "/")]
    expected_count = len(manifest["assets"])
    assert len(owned_rows) == expected_count, "One row per preserved #584 original required"
    assert len([a for a in manifest["assets"] if a["status"] == "review"]) == 6
    assert len(list((root / REPORT).glob("*.jpg"))) == 6
    assert not manifest["approved"] and not manifest["game_imported"]
    total = 0
    for asset in manifest["assets"]:
        raw = root / asset["preserved_path"]
        assert raw.stat().st_size == asset["bytes"] and sha(raw) == asset["sha256"]
        assert raw.stat().st_size < 10000000
        total += raw.stat().st_size
        source = Path(asset["source_path"])
        if source.exists():
            assert raw.read_bytes() == source.read_bytes(), "Original source differs"
        row = next(r for r in owned_rows if r["output_path"] == asset["preserved_path"])
        assert row["review_status"] == asset["status"] and row["prompt_version"] == asset["key"]
        request = next(j for j in json.loads((root / PRODUCTION / "generation_requests.json").read_text(encoding="utf-8"))["jobs"] if j["key"] == asset["key"])
        assert (root / asset["prompt_path"]).read_text(encoding="utf-8") == request["prompt"] + "\n"
        if "preview" in asset:
            preview_path = root / asset["preview"]["path"]
            assert preview_path.stat().st_size == asset["preview"]["bytes"] <= 300000
            assert sha(preview_path) == asset["preview"]["sha256"]
            with Image.open(preview_path) as im:
                assert im.width <= 1280 and im.format == "JPEG"
    assert total == manifest["original_total_bytes"] < 50000000
    print(json.dumps({"verification": "PASS", "originals": expected_count, "byte_hash_verified": expected_count, "original_total_bytes": total, "previews": 6, "csv_owned_rows": len(owned_rows), "game_import_ready": False}, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--jobs", type=Path)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--verify-only", action="store_true")
    args = p.parse_args()
    if args.verify_only:
        verify(args.root.resolve())
        return
    if not args.jobs:
        p.error("--jobs is required for first-time preservation")
    jobs = json.loads(args.jobs.read_text(encoding="utf-8"))
    root = args.root.resolve()
    raw = root / PRODUCTION / "raw"
    prompts = root / PRODUCTION / "prompts"
    report = root / REPORT
    for directory in (raw, prompts, report):
        directory.mkdir(parents=True, exist_ok=True)
    assets = []
    filenames = {j["key"]: MAPPING.get(j["key"], j["key"].removeprefix("584_") + ".png") for j in jobs["jobs"]}
    source_to_output = {j["source_path"]: (PRODUCTION / "raw" / filenames[j["key"]]).as_posix() for j in jobs["jobs"]}
    for job in jobs["jobs"]:
        source = Path(job["source_path"])
        destination = raw / filenames[job["key"]]
        shutil.copy2(source, destination)
        if sha(source) != sha(destination) or source.stat().st_size != destination.stat().st_size:
            raise RuntimeError(f"Byte-preservation failed: {job['key']}")
        prompt_relative = (PRODUCTION / "prompts" / (job["key"] + ".txt")).as_posix()
        (root / prompt_relative).write_text(job["prompt"] + "\n", encoding="utf-8")
        refs = []
        for ref in job["reference_paths"]:
            ref_path = Path(ref)
            refs.append({"actual_input_path": ref, "repository_path_if_preserved": source_to_output.get(ref, ref.replace("C:\\workspace\\joseon-assets\\", "").replace("\\", "/")), "sha256": sha(ref_path), "bytes": ref_path.stat().st_size, "role": "leftmost H1 style only" if job["asset"] == "neutral" else "prompt-defined reference role; see exact prompt"})
        data = {**{k: job[k] for k in ("key", "candidate", "asset", "status")},
                "approved": False, "game_imported": False, "is_3d_asset": False,
                "source_path": str(source), "preserved_path": source_to_output[job["source_path"]],
                "bytes": destination.stat().st_size, "sha256": sha(destination), "byte_identical_to_source": True,
                "source_file_mtime_utc": datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat(),
                "mtime_caveat": "Filesystem metadata only; actual tool generation timestamp was not exposed.",
                "prompt_path": prompt_relative, "references": refs, "measurement": measure(destination, job["asset"]),
                "large_original_git_policy": "below 10000000B/file and 50000000B/card originals total"}
        if job["status"] == "review":
            jpg = report / f"{job['asset']}_{job['candidate'].lower()}.jpg"
            data["preview"] = preview(destination, jpg)
            data["preview"]["path"] = jpg.relative_to(root).as_posix()
        if job["status"] == "rejected":
            if job["asset"] == "fit_attempt_v2":
                data["rejection_reason"] = "A: fit edit extended to full body and changed original crop/geometry; alpha255 and requested fit still failed." if job["candidate"] == "A" else "B: requested top/side clearance and opaque alpha255 still failed; do not use as a corrected fit."
            else:
                data["rejection_reason"] = job.get("rejection_reason", "Facial-only edit introduced visible black background contamination and outside-face changes; silhouette preservation failed.")
        assets.append(data)
    total = sum(a["bytes"] for a in assets)
    if total >= 50000000 or any(a["bytes"] >= 10000000 for a in assets):
        raise RuntimeError("Large raw threshold reached; do not stage originals. Local originals preserved.")
    bykey = {a["key"]: a for a in assets}
    comparisons = {}
    for letter in "AB":
        neutral = next(a for a in assets if a["candidate"] == letter and a["asset"] == "neutral")
        smiles = [a for a in assets if a["candidate"] == letter and (a["asset"] == "smile" or a["asset"].startswith("facial_edit"))]
        comparisons[letter] = {a["key"]: pair(root / neutral["preserved_path"], root / a["preserved_path"]) for a in smiles}
    manifest = {"card": 584, "recorded_at_utc": datetime.now(timezone.utc).isoformat(), "tool": jobs["tool"], "model": jobs["model"], "tool_generation_time_exposed": False, "tool_generation_parameters_exposed": "prompt and reference paths supplied by root; exact model/version not exposed", "approved": False, "game_imported": False, "three_dimensional_generation_performed": False, "steam_ai_disclosure_required_if_used": True, "original_total_bytes": total, "git_storage_policy": {"file_threshold_bytes": 10000000, "card_original_threshold_bytes": 50000000, "thresholds_reached": False, "oversize_action": "Keep local copy; root moves public material to Release or private material to JoseonHunters_raw/584; README stores location/size/SHA, no git raw."}, "jpeg_preview_count": 6, "previews_are_import_assets": False, "anchor_role": jobs["anchor_role"], "assets": assets, "neutral_smile_comparisons": comparisons, "visual_review": "pending direct inspection; see README after inspection"}
    write_json(root / PRODUCTION / "generation_requests.json", jobs)
    write_json(report / "manifest.json", manifest)
    write_json(report / "measurements.json", {"assets": {a["key"]: a["measurement"] for a in assets}, "neutral_smile_comparisons": comparisons})
    shutil.copy2(Path(__file__), report / "build_records.py")
    csv_path = root / "art-direction/manifests/generations.csv"
    contents = csv_path.read_bytes()
    preserved_unrelated_csv = remove_owned_csv_rows(contents)
    output = io.StringIO(newline="")
    w = csv.writer(output, lineterminator="\n")
    for a in assets:
        note = "#584 unapproved/unimported 2D candidate; generated_at is source file mtime only; prompt, SHA256, actual dimensions and failed alpha/framing diagnostics in reports/584/20261008_candidates/manifest.json."
        if a["status"] == "rejected":
            note += " Rejected fit attempt: " + a["rejection_reason"]
        elif a["asset"] == "smile" or a["asset"].startswith("facial_edit"):
            note += " Expression-only pixel/silhouette preservation is not established."
        elif a["asset"] == "turnaround":
            note += " Four-view concept only; not a 3D model or proven orthographic rigging reference."
        w.writerow([a["source_file_mtime_utc"], jobs["tool"], jobs["model"], a["key"], "dokkaebi_" + a["asset"], "joseon_h1_style_leftmost_only" if a["asset"] == "neutral" else "584_neutral_" + a["candidate"].lower(), "; ".join(r["actual_input_path"] for r in a["references"]), a["preserved_path"], a["status"], note])
    csv_path.write_bytes(preserved_unrelated_csv + (b"" if preserved_unrelated_csv.endswith(b"\n") else b"\n") + output.getvalue().encode("utf-8"))
    print(json.dumps({"original_total_bytes": total, "assets": [{"key": a["key"], "bytes": a["bytes"], "size": [a["measurement"]["width"], a["measurement"]["height"]], "mode": a["measurement"]["source_mode"], "alpha": [a["measurement"]["alpha_min"], a["measurement"]["alpha_max"]], "bbox": a["measurement"]["bbox_alpha_gt16_exclusive"], "preview_bytes": a.get("preview", {}).get("bytes")} for a in assets], "neutral_smile_comparisons": comparisons}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
