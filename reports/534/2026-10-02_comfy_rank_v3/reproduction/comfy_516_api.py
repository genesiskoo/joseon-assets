"""One-off, resumable Comfy Cloud generation for card #516.

The API key is read from the repository's ignored .env and is never written.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import requests


ROOT = Path(r"C:\workspace\joseon")
CARD = 516
SIZE_PRESET = "(2K) 1728x2304 (3:4)"
REPORT = ROOT / "._tmp" / "assets_516" / "reports" / "516"
BASE = "https://cloud.comfy.org"
SOURCE_GRAPH = REPORT / "gumiho_boss_516_D2_single_reveal_00001.api.json"
SOURCE_IMAGE = REPORT / "gumiho_boss_516_C_source_single.png"

COMMON = (
    "Use the supplied image as the exact identity and garment reference. One and only one "
    "adult Korean woman, the same face, narrow amber eyes, subtle asymmetric smile, black "
    "hair in a loose low knot with a plain wooden hairpin. Preserve her ordinary Joseon inn "
    "hostess work clothes: faded deep-indigo cotton jeogori with the same off-white collar "
    "and side tie, worn dark brown chima, simple pale linen apron, no jewelry or ornament. "
    "A quiet, unnervingly alluring expression conveyed only through her eyes, small smile "
    "and economical gesture; believable commoner, not a court lady or courtesan. "
    "Dark Joseon fantasy game key art, matte hand-painted illustration, controlled warm "
    "lantern light against cool shadows, restrained saturation, tactile wood and cloth, "
    "clear readable silhouette for a 3D isometric action RPG. Anatomically coherent hands. "
    "Single uninterrupted image, no split panels, no lettering, no border, no duplicate "
    "face, no fox ears, no tails, no elaborate headdress, no exposed skin, no Chinese or "
    "Japanese costume, no modern objects, no shiny photorealistic skin. "
)

PROMPTS = {
    "C2": COMMON + (
        "Full-length character concept, three-quarter front view: she stands behind a rough "
        "inn table and offers a small earthenware cup toward the viewer, the other hand resting "
        "lightly beneath her chin. One foot slightly forward under the chima, practical dark "
        "cloth shoes fully visible. The entire figure from hairpin to both shoes fits within "
        "the frame with clear space below her feet. Background suggests a modest dark wooden "
        "Joseon jumak interior, but keep her body and costume unobscured."
    ),
    "C3": COMMON + (
        "Full-length alternate concept, three-quarter side view at the threshold of a modest "
        "Joseon jumak on a rainy night. She lifts a plain paper lantern in one hand and makes "
        "a slight inviting gesture with the other, glancing back over her shoulder as if she "
        "has already recognized the traveler. Her posture is graceful but entirely plausible "
        "for a working innkeeper. Show her whole figure, apron and hem, both simple shoes and "
        "wet stone ground with breathing room around her. Keep clothing identical to the reference."
    ),
    "C4": COMMON + (
        "Full-length alternate concept, direct front view inside a modest Joseon jumak. "
        "She is quietly tying her pale linen apron after serving guests, with a plain cup "
        "set on the nearby low counter. Her head is slightly tilted and her gaze meets the "
        "viewer with a knowing, almost imperceptible smile. Give her a distinct, self-possessed "
        "stance with one hand at the waist knot and the other touching the counter. Preserve "
        "ordinary workwear and full head-to-toe body, both practical cloth shoes clearly "
        "visible below the hem, no cropped feet."
    ),
    "C5": (
        "Use the supplied full-body inn hostess image as the exact identity and clothing "
        "reference. One and only one adult Korean woman, same narrow amber eyes, black hair "
        "in a loose low knot and plain wooden pin, same faded deep-indigo work jeogori, "
        "dark brown chima, off-white collar and pale worn linen apron. Reveal that this "
        "ordinary Joseon jumak hostess is an ancient gumiho boss, but do not redesign her "
        "as royalty or a courtesan. She stands calmly in the now-empty dark wooden inn, "
        "still holding the small earthenware cup; her half-smile is intimate and predatory. "
        "From behind her body emerge exactly nine enormous separate fox tails, individually "
        "readable from root to tip, charcoal black with subtle deep-russet and gold rim light; "
        "they spread like a dark fan above and to both sides without hiding her face, apron, "
        "hands, hem or both cloth shoes. The room's shadows bend subtly toward her. Full "
        "head-to-toe character within frame, one face, two hands, two feet, no duplicated "
        "body. Dark Joseon fantasy boss concept, matte painted illustration, tactile cloth "
        "and wood, clear silhouette at isometric game scale, restrained warm lamp light, "
        "not photorealistic, no fox ears, no crown, no jewelry, no exposed skin, no Chinese "
        "or Japanese costume, no text or split panels."
    ),
}

SEEDS = {"C2": 5162201, "C3": 5162301, "C4": 5162401, "C5": 5162501}


def key() -> str:
    for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("COMFY_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("COMFY_API_KEY missing")


def check(response: requests.Response) -> requests.Response:
    if not response.ok:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:800]}")
    return response


def submit(label: str) -> None:
    job_path = REPORT / f"gumiho_boss_{CARD}_{label}.job.json"
    if job_path.exists():
        raise RuntimeError(f"Existing job record; refusing a duplicate charge: {job_path}")
    api_key = key()
    headers = {"X-API-Key": api_key}
    source_image = REPORT / "gumiho_boss_516_C2_00001.png" if label == "C5" else SOURCE_IMAGE
    if not source_image.exists():
        raise RuntimeError(f"Missing input image: {source_image}")
    with source_image.open("rb") as image:
        result = check(requests.post(
            f"{BASE}/api/upload/image",
            headers=headers,
            files={"image": image},
            data={"type": "input", "overwrite": "true"},
            timeout=60,
        )).json()
    graph = json.loads(SOURCE_GRAPH.read_text(encoding="utf-8"))
    graph.pop("5", None)
    graph.pop("7", None)
    graph["3"]["inputs"]["image"] = result["name"]
    graph["8"]["inputs"]["model.images.image_1"] = ["3", 0]
    graph["8"]["inputs"]["model.seed"] = SEEDS[label]
    graph["8"]["inputs"]["model.size_preset"] = SIZE_PRESET
    graph["8"]["inputs"]["prompt"] = PROMPTS[label]
    graph["2"]["inputs"]["filename_prefix"] = f"gumiho_boss_{CARD}_{label}"
    graph_path = REPORT / f"gumiho_boss_{CARD}_{label}.api.json"
    graph_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    response = check(requests.post(
        f"{BASE}/api/prompt",
        headers={**headers, "Content-Type": "application/json"},
        json={"prompt": graph, "extra_data": {"api_key_comfy_org": api_key}},
        timeout=60,
    )).json()
    if response.get("error"):
        raise RuntimeError(str(response["error"]))
    record = {
        "prompt_id": response["prompt_id"],
        "phase": label,
        "source": source_image.name,
        "source_sha256": hashlib.sha256(source_image.read_bytes()).hexdigest(),
        "uploaded_name": result["name"],
        "model": "ByteDanceSeedreamNodeV3/seedream 5.0 pro",
        "size": SIZE_PRESET,
        "seed": SEEDS[label],
    }
    job_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"submitted {label}: {response['prompt_id']}", flush=True)


def collect(label: str) -> None:
    api_key = key()
    headers = {"X-API-Key": api_key}
    record = json.loads((REPORT / f"gumiho_boss_{CARD}_{label}.job.json").read_text(encoding="utf-8"))
    prompt_id = record["prompt_id"]
    status = check(requests.get(
        f"{BASE}/api/job/{prompt_id}/status", headers=headers, timeout=30,
    )).json()["status"]
    print(f"{label}: {status}", flush=True)
    if status != "success":
        return
    history = check(requests.get(
        f"{BASE}/api/history_v2/{prompt_id}", headers=headers, timeout=30,
    )).json()[prompt_id]
    outputs = history["outputs"]
    images = outputs.get("2", {}).get("images", [])
    if not images:
        raise RuntimeError(f"No saved image in output 2. Output nodes: {list(outputs)}")
    info = images[0]
    response = requests.get(
        f"{BASE}/api/view", headers=headers,
        params={"filename": info["filename"], "subfolder": info.get("subfolder", ""), "type": info.get("type", "output")},
        allow_redirects=False, timeout=30,
    )
    if response.status_code != 302:
        raise RuntimeError(f"Output redirect HTTP {response.status_code}: {response.text[:500]}")
    # Signed storage URL is self-authenticating; never forward the Cloud API key.
    blob = check(requests.get(response.headers["Location"], timeout=60)).content
    path = REPORT / f"gumiho_boss_{CARD}_{label}_00001.png"
    path.write_bytes(blob)
    record["output_name"] = info["filename"]
    record["output_sha256"] = hashlib.sha256(blob).hexdigest()
    (REPORT / f"gumiho_boss_{CARD}_{label}.job.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"saved {path} ({len(blob)} bytes)", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("submit", "collect"))
    parser.add_argument("label", choices=tuple(PROMPTS))
    args = parser.parse_args()
    try:
        (submit if args.action == "submit" else collect)(args.label)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
