#!/usr/bin/env python3
"""Validate and publish approved assets into the sibling Godot project."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifests" / "godot.json"
PUBLISHABLE_STATUSES = {"approved", "published"}


class PublishError(Exception):
    pass


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise PublishError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PublishError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise PublishError(f"JSON root must be an object: {path}")
    return data


def resolve_inside(root: Path, relative: str, label: str) -> Path:
    raw = Path(relative)
    if raw.is_absolute():
        raise PublishError(f"{label} must be relative: {relative}")
    resolved = (root / raw).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise PublishError(f"{label} escapes its root: {relative}") from exc
    return resolved


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_info(path: Path) -> Tuple[int, int, bool]:
    with path.open("rb") as handle:
        signature = handle.read(8)
        if signature != b"\x89PNG\r\n\x1a\n":
            raise PublishError(f"not a PNG file: {path}")
        length = struct.unpack(">I", handle.read(4))[0]
        chunk_type = handle.read(4)
        if chunk_type != b"IHDR" or length != 13:
            raise PublishError(f"invalid PNG IHDR: {path}")
        width, height, _, color_type, _, _, _ = struct.unpack(
            ">IIBBBBB", handle.read(13)
        )
    return width, height, color_type in {4, 6}


def select_assets(
    manifest: Dict[str, Any], requested_ids: Iterable[str]
) -> List[Dict[str, Any]]:
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        raise PublishError("manifest.assets must be an array")

    requested = set(requested_ids)
    seen = set()
    selected: List[Dict[str, Any]] = []

    for asset in assets:
        if not isinstance(asset, dict):
            raise PublishError("each manifest asset must be an object")
        asset_id = asset.get("id")
        if not isinstance(asset_id, str) or not asset_id:
            raise PublishError("each asset needs a non-empty string id")
        if asset_id in seen:
            raise PublishError(f"duplicate asset id: {asset_id}")
        seen.add(asset_id)

        if requested and asset_id not in requested:
            continue
        if asset.get("status") not in PUBLISHABLE_STATUSES:
            continue
        selected.append(asset)

    missing = requested - seen
    if missing:
        raise PublishError(f"unknown asset ids: {', '.join(sorted(missing))}")
    return selected


def validate_asset(
    asset: Dict[str, Any], target_root: Path
) -> Tuple[Path, Path, str]:
    asset_id = asset["id"]
    source_rel = asset.get("source")
    target_rel = asset.get("target")
    if not isinstance(source_rel, str) or not source_rel:
        raise PublishError(f"{asset_id}: source is required")
    if not isinstance(target_rel, str) or not target_rel:
        raise PublishError(f"{asset_id}: target is required")
    if not target_rel.startswith("assets/"):
        raise PublishError(f"{asset_id}: target must be under assets/: {target_rel}")
    if target_rel.endswith(".import"):
        raise PublishError(f"{asset_id}: .import files are Godot-owned")

    source = resolve_inside(ROOT, source_rel, f"{asset_id}.source")
    target = resolve_inside(target_root, target_rel, f"{asset_id}.target")
    if not source.is_file():
        raise PublishError(f"{asset_id}: source not found: {source}")

    constraints = asset.get("constraints", {})
    if not isinstance(constraints, dict):
        raise PublishError(f"{asset_id}: constraints must be an object")

    expected_format = constraints.get("format")
    if expected_format and source.suffix.lower() != f".{str(expected_format).lower()}":
        raise PublishError(
            f"{asset_id}: expected {expected_format}, got {source.suffix.lstrip('.')}"
        )

    if source.suffix.lower() == ".png":
        width, height, alpha = png_info(source)
        expected_width = constraints.get("width")
        expected_height = constraints.get("height")
        expected_alpha = constraints.get("alpha")
        if expected_width is not None and width != expected_width:
            raise PublishError(
                f"{asset_id}: width {width}, expected {expected_width}"
            )
        if expected_height is not None and height != expected_height:
            raise PublishError(
                f"{asset_id}: height {height}, expected {expected_height}"
            )
        if expected_alpha is not None and alpha != bool(expected_alpha):
            raise PublishError(
                f"{asset_id}: alpha={alpha}, expected {bool(expected_alpha)}"
            )

    return source, target, sha256(source)


def atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent)
    )
    os.close(descriptor)
    temp_path = Path(temp_name)
    try:
        shutil.copy2(source, temp_path)
        os.replace(temp_path, target)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def write_lock(
    lock_path: Path,
    manifest_path: Path,
    records: List[Dict[str, Any]],
) -> None:
    merged = {}
    if lock_path.is_file():
        existing = load_json(lock_path)
        for record in existing.get("assets", []):
            if isinstance(record, dict) and isinstance(record.get("id"), str):
                merged[record["id"]] = record
    for record in records:
        merged[record["id"]] = record

    payload = {
        "schema_version": 1,
        "manifest": str(manifest_path.relative_to(ROOT)),
        "assets": [merged[asset_id] for asset_id in sorted(merged)],
    }
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def run_godot_import(target_root: Path) -> None:
    godot = shutil.which("godot") or shutil.which("godot4")
    if not godot:
        raise PublishError("Godot executable not found; use --skip-import")
    result = subprocess.run(
        [godot, "--headless", "--path", str(target_root), "--import"],
        check=False,
    )
    if result.returncode != 0:
        raise PublishError(f"Godot import failed with exit code {result.returncode}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish manifest-selected assets to joseon-hunters."
    )
    parser.add_argument(
        "command",
        choices=("check", "plan", "publish"),
        help="validate, preview changes, or copy changed assets",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="manifest path (default: manifests/godot.json)",
    )
    parser.add_argument(
        "--target",
        type=Path,
        help="override Godot project root",
    )
    parser.add_argument(
        "--asset",
        action="append",
        default=[],
        help="limit work to an asset id; may be repeated",
    )
    parser.add_argument(
        "--skip-import",
        action="store_true",
        help="do not run Godot headless import after publish",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest.resolve()
    manifest = load_json(manifest_path)
    if manifest.get("schema_version") != 1:
        raise PublishError("unsupported manifest schema_version")

    target_root = (
        args.target.resolve()
        if args.target
        else (ROOT / manifest.get("target_project", "../joseon-hunters")).resolve()
    )
    if not (target_root / "project.godot").is_file():
        raise PublishError(f"Godot project not found: {target_root}")

    selected = select_assets(manifest, args.asset)
    if not selected:
        print("[publish] no publishable assets selected")
        return 0

    records = []
    changed = 0
    planned_changes = 0
    claimed_targets = {}
    print(f"[publish] command={args.command}")
    print(f"[publish] manifest={manifest_path}")
    print(f"[publish] target={target_root}")

    for asset in selected:
        source, target, source_hash = validate_asset(asset, target_root)
        target_key = str(target)
        if target_key in claimed_targets:
            raise PublishError(
                f"{asset['id']}: target also claimed by "
                f"{claimed_targets[target_key]}: {target.relative_to(target_root)}"
            )
        claimed_targets[target_key] = asset["id"]
        target_hash: Optional[str] = sha256(target) if target.is_file() else None
        action = "same" if target_hash == source_hash else (
            "update" if target_hash else "add"
        )
        if action != "same":
            planned_changes += 1
        print(f"  {action.upper():6} {asset['id']}")
        print(f"         {source.relative_to(ROOT)}")
        print(f"      -> {target.relative_to(target_root)}")

        if args.command == "publish" and action != "same":
            atomic_copy(source, target)
            copied_hash = sha256(target)
            if copied_hash != source_hash:
                raise PublishError(f"{asset['id']}: checksum mismatch after copy")
            changed += 1

        records.append(
            {
                "id": asset["id"],
                "source": str(source.relative_to(ROOT)),
                "target": str(target.relative_to(target_root)),
                "sha256": source_hash,
                "status": asset["status"],
            }
        )

    if args.command == "publish":
        lock_rel = manifest.get("lock_file", "manifests/godot.lock.json")
        lock_path = resolve_inside(ROOT, lock_rel, "lock_file")
        write_lock(lock_path, manifest_path, records)
        if changed and not args.skip_import:
            run_godot_import(target_root)
        print(f"[publish] copied={changed} lock={lock_path.relative_to(ROOT)}")
    else:
        print(
            f"[publish] validated={len(records)} "
            f"planned_changes={planned_changes}"
        )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PublishError as error:
        print(f"[publish] error: {error}", file=sys.stderr)
        raise SystemExit(1)
