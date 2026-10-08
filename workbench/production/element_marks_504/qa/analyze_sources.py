"""Measure both preserved #504 rounds; never modify PNGs or generation receipts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageStat

QA = Path(__file__).resolve().parent
PACK = QA.parent
ASSETS = PACK.parents[2]
SOURCES = {
    "original": ASSETS / "reports/504/2026-10-02_round1",
    "revision1": ASSETS / "reports/504/2026-10-02_revision1",
}
IDS = ("fire", "cold", "lightning", "sal", "soul")
SIZES = (12, 14, 16, 18, 24)
TINTS = {
    "fire": [1.0, 0.49, 0.29],
    "cold": [0.51, 0.81, 1.0],
    "lightning": [0.94, 0.83, 0.38],
    "sal": [0.7, 0.48, 0.82],
    "soul": [0.55, 0.92, 0.75],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binary(alpha: Image.Image, threshold: int) -> Image.Image:
    return alpha.point(lambda value: 255 if value >= threshold else 0)


def footprint(alpha: Image.Image, threshold: int) -> dict:
    mask = binary(alpha, threshold)
    bbox = mask.getbbox()
    count = mask.histogram()[255]
    return {
        "alpha_at_least": threshold,
        "bbox_xyxy_exclusive": list(bbox) if bbox else None,
        "pixels": count,
        "fraction_of_canvas": round(count / (alpha.width * alpha.height), 6),
        "margins_ltrb_px": [bbox[0], bbox[1], alpha.width - bbox[2], alpha.height - bbox[3]] if bbox else None,
    }


def iou(first: Image.Image, second: Image.Image) -> float:
    a = binary(first, 128)
    b = binary(second, 128)
    intersection = ImageChops.darker(a, b).histogram()[255]
    union = ImageChops.lighter(a, b).histogram()[255]
    return round(intersection / union, 6) if union else 0.0


def enclosed_negative_space(alpha: Image.Image) -> dict:
    mask = binary(alpha, 128)
    for x in range(mask.width):
        for y in (0, mask.height - 1):
            if mask.getpixel((x, y)) == 0:
                ImageDraw.floodfill(mask, (x, y), 127)
    for y in range(mask.height):
        for x in (0, mask.width - 1):
            if mask.getpixel((x, y)) == 0:
                ImageDraw.floodfill(mask, (x, y), 127)
    holes = mask.point(lambda value: 255 if value == 0 else 0)
    bbox = holes.getbbox()
    return {
        "method": "Alpha<128 regions not connected to the canvas border (four-neighbor connectivity)",
        "pixels": holes.histogram()[255],
        "bbox_xyxy_exclusive": list(bbox) if bbox else None,
    }


def inspect(id: str, source_round: str, variant: str) -> tuple[dict, dict[int, Image.Image]]:
    stem = id if source_round == "original" else id + "_v2"
    filename = stem + ("_raw" if variant == "generation_raw" else "") + ".png"
    path = SOURCES[source_round] / filename
    with Image.open(path) as source:
        source.load()
        mode = source.mode
        size = list(source.size)
        rgba = source.convert("RGBA")
    alpha = rgba.getchannel("A")
    hist = alpha.histogram()
    nonempty = sum(hist[1:])
    alpha_mass = sum(value * count for value, count in enumerate(hist))
    core = binary(alpha, 224)
    core_count = core.histogram()[255]
    rgb = rgba.convert("RGB")
    channels = rgb.split()
    rgb_min = ImageChops.darker(ImageChops.darker(channels[0], channels[1]), channels[2])
    rgb_max = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    chroma_hist = ImageChops.subtract(rgb_max, rgb_min).histogram(mask=core)
    min_hist = rgb_min.histogram(mask=core)
    neutral = sum(chroma_hist[:6]) / core_count if core_count else 0.0
    bright = sum(min_hist[240:]) / core_count if core_count else 0.0
    opaque_stats = ImageStat.Stat(rgb, core)
    reduced = {side: alpha.resize((side, side), Image.Resampling.LANCZOS) for side in SIZES} if variant == "candidate" else {}
    prompt_path = path.parent / (stem + ".prompt.txt")
    report = {
        "id": id,
        "round": source_round,
        "variant": variant,
        "source": path.relative_to(ASSETS).as_posix(),
        "sha256": sha(path),
        "decoded_rgb_sha256": hashlib.sha256(rgb.tobytes()).hexdigest(),
        "decoded_alpha_sha256": hashlib.sha256(alpha.tobytes()).hexdigest(),
        "mode": mode,
        "size_px": size,
        "alpha_extrema": list(alpha.getextrema()),
        "alpha_zero_pixels": hist[0],
        "alpha_nonempty_pixels": nonempty,
        "semi_transparent_pixels": sum(hist[1:255]),
        "low_alpha_1_127_fraction_of_nonempty": round(sum(hist[1:128]) / nonempty, 6) if nonempty else None,
        "low_alpha_1_127_fraction_of_alpha_mass": round(sum(v * hist[v] for v in range(1, 128)) / alpha_mass, 6) if alpha_mass else None,
        "footprints": [footprint(alpha, threshold) for threshold in (1, 16, 64, 128, 224)],
        "core_rgb_alpha_at_least_224": {
            "pixels": core_count,
            "mean": [round(value, 6) for value in opaque_stats.mean],
            "extrema": [list(pair) for pair in opaque_stats.extrema],
            "fraction_channel_spread_le_5": round(neutral, 6),
            "fraction_all_channels_ge_240": round(bright, 6),
        },
        "technical_checks": {
            "png_1024_rgba": mode == "RGBA" and size == [1024, 1024],
            "alpha_nonempty": nonempty > 0,
            "has_transparent_pixels": hist[0] > 0,
            "bright_neutral_core": neutral >= 0.99 and bright >= 0.99,
        },
        "small_alpha_analysis": {
            "method": "Pillow LANCZOS alpha-only reduction of whole unchanged canvas; not native Godot visual evidence" if reduced else "Not applicable: preserved generation_raw has an opaque black background and is not a display candidate",
            "sizes": {
                str(side): {**footprint(image, 128), "enclosed_negative_space": enclosed_negative_space(image)}
                for side, image in reduced.items()
            },
        },
        "prompt_path": prompt_path.relative_to(ASSETS).as_posix(),
        "prompt_sha256": sha(prompt_path),
    }
    if variant == "candidate":
        report["enclosed_negative_space_alpha128"] = enclosed_negative_space(alpha)
        if id == "soul":
            report["lower_bulb_diagnostic_rgba_samples"] = {
                f"{x},{y}": list(rgba.getpixel((x, y)))
                for x, y in ((400, 760), (620, 780), (500, 800))
            }
    return report, reduced


def main() -> None:
    evidence_paths = sorted(path for folder in SOURCES.values() for path in folder.iterdir() if path.is_file())
    evidence_before = {path.relative_to(ASSETS).as_posix(): sha(path) for path in evidence_paths}
    groups = {}
    reductions_by_round = {}
    for source_round, variant in (("original", "candidate"), ("revision1", "generation_raw"), ("revision1", "candidate")):
        reports = []
        reduced = {}
        for id in IDS:
            report, reductions = inspect(id, source_round, variant)
            reports.append(report)
            reduced[id] = reductions
        groups[(source_round, variant)] = reports
        if variant == "candidate":
            reductions_by_round[source_round] = reduced
    original = groups[("original", "candidate")]
    revision_raw = groups[("revision1", "generation_raw")]
    revision = groups[("revision1", "candidate")]
    reports = original + revision_raw + revision
    technical_checks = {
        source_round: "PASS" if all(all(item["technical_checks"].values()) for item in groups[(source_round, "candidate")]) else "FAIL"
        for source_round in SOURCES
    }
    pair_checks = [
        {
            "id": candidate["id"],
            "raw_source": raw["source"],
            "candidate_source": candidate["source"],
            "decoded_rgb_unchanged": raw["decoded_rgb_sha256"] == candidate["decoded_rgb_sha256"],
            "alpha_is_different": raw["decoded_alpha_sha256"] != candidate["decoded_alpha_sha256"],
            "raw_fully_opaque": raw["alpha_extrema"] == [255, 255],
            "candidate_has_transparent_pixels": candidate["technical_checks"]["has_transparent_pixels"],
        }
        for raw, candidate in zip(revision_raw, revision)
    ]
    evidence_after = {path.relative_to(ASSETS).as_posix(): sha(path) for path in evidence_paths}
    if evidence_before != evidence_after:
        raise RuntimeError("Generation evidence changed during read-only measurement; preserve files and review concurrency.")
    source_report = {
        "card": 504,
        "schema_version": 2,
        "scope": "Preserved generation originals (10) and revision1 alpha derivatives (5); no image edit or game integration",
        "technical_candidate_raster_checks": technical_checks,
        "revision1_generation_raw": "Expected opaque-black originals; not transparent candidates and not loaded by native QA",
        "visual_acceptance": "HOLD for both rounds: native alpha-composited size review pending. Original apparent RGB halo is not a confirmed visible glow. Both soul candidates contain an enclosed alpha cutout; the earlier RGB-only original-cutout-absence verdict is withdrawn.",
        "generated_original_count": len(original) + len(revision_raw),
        "revision1_alpha_derivative_count": len(revision),
        "measured_png_count": len(reports),
        "items": reports,
        "revision1_raw_to_candidate_checks": pair_checks,
        "generation_evidence_unchanged_during_measurement": evidence_before == evidence_after,
        "preserved_generation_evidence_sha256": evidence_before,
        "whole_canvas_alpha128_iou": {
            source_round: {
                f"{left}:{right}": {str(side): iou(reduced[left][side], reduced[right][side]) for side in SIZES}
                for left, right in (("fire", "soul"), ("sal", "soul"), ("fire", "sal"))
            }
            for source_round, reduced in reductions_by_round.items()
        },
        "same_element_round_alpha128_iou": {
            id: {str(side): iou(reductions_by_round["original"][id][side], reductions_by_round["revision1"][id][side]) for side in SIZES}
            for id in IDS
        },
        "iou_limit": "Descriptive silhouette overlap only; no automatic identity or readability pass is inferred.",
        "negative_space_limit": "Alpha threshold and Pillow sampling describe topology only; source cutout presence and native-size legibility are separate findings.",
    }
    (QA / "source_check.json").write_text(json.dumps(source_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "card": 504,
        "schema_version": 2,
        "state": "both rounds unapproved; native concept-size visual review pending; not installed in game",
        "counts": {"generated_originals": 10, "revision1_alpha_derivatives": 5, "native_display_candidates": 10},
        "rounds": {
            "original": {
                "source_root": SOURCES["original"].relative_to(ASSETS).as_posix(),
                "generation_config": "CLOUD_CONFIG.json",
                "candidate_filename_pattern": "{id}.png",
                "source_processing": "none; original generation alpha is read directly",
                "native_default_output": "qa/native/original/",
                "visual_acceptance": "HOLD pending native alpha compositing; no confirmed no-glow failure; alpha contains a soul cutout despite the solid-bulb RGB view",
            },
            "revision1": {
                "source_root": SOURCES["revision1"].relative_to(ASSETS).as_posix(),
                "generation_config": "CLOUD_REVISION1.json",
                "candidate_filename_pattern": "{id}_v2.png",
                "preserved_raw_filename_pattern": "{id}_v2_raw.png",
                "source_processing": "Cloud edit on opaque black -> SplitImageWithAlpha -> BiRefNetRMBG foreground alpha -> SaveImageAdvanced; raw opaque output preserved separately",
                "decoded_rgb_raw_candidate_match": all(item["decoded_rgb_unchanged"] for item in pair_checks),
                "native_default_output": "qa/native/revision1/",
                "visual_acceptance": "HOLD pending native alpha compositing; soul crescent present at source size",
            },
        },
        "historical_receipt_note": "REVISION_SCOPE.json and CLOUD_REVISION1.json preserve earlier request wording about halos and a missing soul crescent. Those RGB-only claims are not a final original-round verdict: original alpha also has a soul cutout, and both rounds remain native-compositing HOLD.",
        "source_processing_by_qa": "none; selected PNGs read directly, generation originals and alpha derivatives never overwritten",
        "render_qa": {
            "project": "qa/project.godot",
            "script": "qa/element_mark_board.gd",
            "round_selector": "--round=original|revision1 (default original)",
            "default_output": "qa/native/<selected_round>/",
            "modes": ["color", "gray", "white"],
            "sizes_px": list(SIZES),
            "context_size_px": 80,
            "native_canvas_px": [1280, 800],
            "filter": "Godot CanvasItem linear",
            "backgrounds": {"dark_ui": [0.05, 0.045, 0.06], "representative_light_soil": [0.62, 0.56, 0.46]},
            "resisted_tint": [0.63, 0.65, 0.68],
            "color_source": "C:/workspace/joseon/ui/element_marks.gd:5-9, unchanged palette copied for concept QA",
            "not_reproduced": ["live game callers", "Label3D outline", "combat punch", "weak-target scaling", "tooltip layout"],
        },
        "assets": [
            {"id": item["id"], "round": item["round"], "variant": item["variant"], "source": item["source"], "source_sha256": item["sha256"], "size_px": item["size_px"], "mode": item["mode"], "rgb_tint": TINTS[item["id"]], "prompt": item["prompt_path"], "prompt_sha256": item["prompt_sha256"]}
            for item in reports
        ],
        "reviews": ["qa/source_check.json", "qa/visual_review.json"],
    }
    (PACK / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for item in reports:
        print(json.dumps({"id": item["id"], "round": item["round"], "variant": item["variant"], "technical_checks": item["technical_checks"], "alpha_extrema": item["alpha_extrema"], "low_alpha_fraction_of_mass": item["low_alpha_1_127_fraction_of_alpha_mass"]}, ensure_ascii=False))
    print("MEASURED #504 generated_originals=10 alpha_derivatives=5; visual_acceptance=HOLD; native_evidence=not_evaluated; evidence_unchanged=true")


if __name__ == "__main__":
    main()
