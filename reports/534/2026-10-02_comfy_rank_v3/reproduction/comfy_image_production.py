"""Resume explicit Comfy Cloud image workflows; never submit an existing job record."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

import requests
from PIL import Image
import comfy_516_api as cloud

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

def checked(response, secret):
    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text.replace(secret, '<redacted>')}")
    return response

def submit(config, spec):
    report = Path(config["report"])
    report.mkdir(parents=True, exist_ok=True)
    label = spec["id"]
    job = report / f"{label}.job.json"
    if job.exists():
        raise RuntimeError(f"Existing job record; duplicate charge refused: {job}")
    secret = cloud.key()
    headers = {"X-API-Key": secret}
    graph = {"2": {"class_type": "SaveImageAdvanced", "inputs": {"filename_prefix": f"{config['card']}/{label}",
             "format": "png", "format.bit_depth": "8-bit", "format.input_color_space": "sRGB", "images": ["8", 0]}},
             "8": {"class_type": "OpenAIGPTImageNodeV2", "inputs": {"prompt": spec["prompt"],
                    "model": config["model"], "model.size": "Custom", "model.custom_width": spec["width"],
                    "model.custom_height": spec["height"], "model.background": spec["background"],
                    "model.quality": spec.get("quality", "high"), "n": 1, "seed": spec["seed"]}}}
    removing = spec.get("workflow") == "background_remove"
    generating_clean = spec.get("workflow") == "image_generate_clean"
    if removing:
        assert len(spec["references"]) == 1
        graph["8"] = {"class_type": "BiRefNetRMBG", "inputs": {"image": ["21", 0],
                      "model": "BiRefNet-general", "mask_blur": 0, "mask_offset": 0,
                      "invert_output": False, "refine_foreground": False, "background": "Alpha"}}
    if generating_clean:
        graph["3"] = {"class_type": "SaveImageAdvanced", "inputs": {"filename_prefix": f"{config['card']}/{label}_raw",
                     "format": "png", "format.bit_depth": "8-bit", "format.input_color_space": "sRGB", "images": ["8", 0]}}
        graph["10"] = {"class_type": "SplitImageWithAlpha", "inputs": {"image": ["8", 0]}}
        graph["9"] = {"class_type": "BiRefNetRMBG", "inputs": {"image": ["10", 0],
                      "model": "BiRefNet-general", "mask_blur": 0, "mask_offset": 0,
                      "invert_output": False, "refine_foreground": False, "background": "Alpha"}}
        graph["2"]["inputs"]["images"] = ["9", 0]
    sources = []
    for index, reference in enumerate(spec.get("references", []), 1):
        path = Path(reference["path"])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != reference["sha256"]:
            raise RuntimeError(f"Reference SHA mismatch: {path.name}")
        with path.open("rb") as source:
            upload = checked(requests.post(cloud.BASE + "/api/upload/image", headers=headers,
                             files={"image": (path.name, source, "image/png")},
                             data={"type": "input", "overwrite": "false"}, timeout=60), secret).json()
        node = str(20 + index)
        graph[node] = {"class_type": "LoadImage", "inputs": {"image": upload["name"]}}
        if not removing:
            graph["8"]["inputs"][f"model.images.image_{index}"] = [node, 0]
        sources.append({"path": str(path), "role": reference["role"], "sha256": digest})
    write(report / f"{label}.api.json", graph)
    (report / f"{label}.prompt.txt").write_text(spec["prompt"] + "\n", encoding="utf-8", newline="\n")
    record = {"card": config["card"], "asset": label, "provider": "Comfy Cloud", "model": config["model"],
              "reference_images": sources, "prompt_sha256": hashlib.sha256(spec["prompt"].encode("utf-8")).hexdigest(),
              "width": spec["width"], "height": spec["height"], "background_requested": spec["background"],
              "quality": spec.get("quality", "high"), "seed": spec["seed"], "workflow": spec.get("workflow", "image_generate"), "deterministic_seed_guaranteed": False,
              "state": "submitting", "submitted_at": datetime.now(timezone.utc).isoformat()}
    write(job, record)
    try:
        result = checked(requests.post(cloud.BASE + "/api/prompt", headers={**headers, "Content-Type": "application/json"},
                         json={"prompt": graph, "extra_data": {"api_key_comfy_org": secret}}, timeout=45), secret).json()
    except Exception:
        record["state"] = "submission_outcome_unknown"
        write(job, record)
        raise
    if result.get("error"):
        record["state"] = "rejected_before_queue"
        record["error"] = json.loads(json.dumps(result, ensure_ascii=False).replace(secret, "<redacted>"))
        write(job, record)
        print(json.dumps(record["error"], ensure_ascii=False))
        return
    record.update({"state": "submitted", "prompt_id": result["prompt_id"]})
    write(job, record)
    print(f"{label}: submitted {result['prompt_id']}", flush=True)

def collect(config, spec):
    report = Path(config["report"])
    label = spec["id"]
    job = report / f"{label}.job.json"
    record = json.loads(job.read_text(encoding="utf-8"))
    if record["state"] in ("downloaded", "failed_recorded", "rejected_before_queue"):
        print(f"{label}: {record['state']}")
        return
    if not record.get("prompt_id"):
        raise RuntimeError("Unknown submission outcome: no acknowledged ID; never resubmit")
    secret = cloud.key()
    headers = {"X-API-Key": secret}
    prompt_id = record["prompt_id"]
    status = checked(requests.get(cloud.BASE + f"/api/job/{prompt_id}/status", headers=headers, timeout=30), secret).json()
    record.update({"state": status["status"], "status_response": status})
    write(job, record)
    print(f"{label}: {status['status']}", flush=True)
    if status["status"] not in ("success", "error", "failed", "failure"):
        return
    response = requests.get(cloud.BASE + f"/api/history_v2/{prompt_id}", headers=headers, timeout=35)
    if response.status_code == 404 and status["status"] != "success":
        safe = status
    else:
        raw = checked(response, secret).json()
        safe = json.loads(json.dumps(raw.get(prompt_id, raw), ensure_ascii=False).replace(secret, "<redacted>"))
        safe.pop("prompt", None)
    write(report / f"{label}.history.json", safe)
    if status["status"] != "success":
        record["state"] = "failed_recorded"
        record["raw_error"] = safe
        (report / f"{label}.failure.raw.txt").write_text(json.dumps(safe, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")
        write(job, record)
        print(json.dumps(record["raw_error"], ensure_ascii=False))
        return
    raw_pictures = safe.get("outputs", {}).get("3", {}).get("images", [])
    if raw_pictures:
        assert len(raw_pictures) == 1
        raw_info = raw_pictures[0]
        raw_response = requests.get(cloud.BASE + "/api/view", headers=headers,
            params={"filename": raw_info["filename"], "subfolder": raw_info.get("subfolder", ""), "type": raw_info.get("type", "output")},
            allow_redirects=False, timeout=30)
        raw_blob = checked(requests.get(raw_response.headers["Location"], timeout=90), secret).content if raw_response.status_code == 302 else checked(raw_response, secret).content
        (report / f"{label}_raw.png").write_bytes(raw_blob)
        record.update({"raw_output": f"{label}_raw.png", "raw_output_sha256": hashlib.sha256(raw_blob).hexdigest()})
    pictures = safe.get("outputs", {}).get("2", {}).get("images", [])
    if len(pictures) != 1:
        raise RuntimeError(f"Expected exactly one image: {pictures}")
    info = pictures[0]
    response = requests.get(cloud.BASE + "/api/view", headers=headers,
                 params={"filename": info["filename"], "subfolder": info.get("subfolder", ""), "type": info.get("type", "output")},
                 allow_redirects=False, timeout=30)
    blob = checked(requests.get(response.headers["Location"], timeout=90), secret).content if response.status_code == 302 else checked(response, secret).content
    path = report / f"{label}.png"
    path.write_bytes(blob)
    with Image.open(path) as picture:
        picture.verify()
    with Image.open(path) as picture:
        record.update({"actual_dimensions": list(picture.size), "actual_mode": picture.mode})
        if "A" in picture.getbands():
            alpha = picture.getchannel("A")
            record["alpha_extrema"] = list(alpha.getextrema())
            record["has_transparent_pixels"] = alpha.getextrema()[0] < 255
        else:
            record["has_transparent_pixels"] = False
    record.update({"state": "downloaded", "output": path.name, "output_sha256": hashlib.sha256(blob).hexdigest(), "output_bytes": len(blob)})
    write(job, record)
    print(f"{label}: saved {record['actual_dimensions']} {record['actual_mode']}, alpha={record['has_transparent_pixels']}", flush=True)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("submit", "collect"))
    parser.add_argument("config", type=Path)
    parser.add_argument("labels", nargs="+")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    for label in args.labels:
        spec = next(x for x in config["jobs"] if x["id"] == label)
        (submit if args.action == "submit" else collect)(config, spec)
