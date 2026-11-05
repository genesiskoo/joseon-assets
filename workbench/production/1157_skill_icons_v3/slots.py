# #1157 새 칸 아이콘 14 — 칸별 그림 지시 (A = 인물 중심 · B = 큰 모티프 하나)
import json, sys, pathlib

COMMON = """Create ONE square production skill-icon illustration for Joseon Hunters, a Korean dark fantasy ARPG (fictional Joseon). Intended 128x128 asset, shown inside a 40x40 skill cell (about 34x34 drawing area), so it must read at tiny size. Full-bleed square, opaque dark ink background, rough broad dry-brush ink painting like the attached adopted icons, matte restrained charcoal / deep navy / ivory base. Crisp large silhouette and ONE dominant readable action or motif, broad quiet shapes instead of fine pattern noise. Keep important shapes inside the central 88 percent, feathered dark painted edges. No added border, plaque, icon frame, text, letters, numbers, UI badge, watermark or title; the UI draws its own frame. No glossy CGI, photoreal skin, neon glow, colored bloom, western magic circle, western armor, samurai or Japanese clothing, extra limbs.
If Doho appears: adult Korean man, black broad-brimmed gat, plain navy split robe, ivory collar, red waist sash, black bracers, straight Korean sword; use ONLY the LEFT H1 figure of image 1 for his identity, ignore other panels and labels.
REFERENCE ROLES: image 1 = H1 character board (left figure only, identity). image 2 = adopted skill-icon brush source: copy only painting medium, contrast, broad ink strokes and square-edge treatment, not its pose. images 3-5 = adopted icons (seal array, whirlwind, hide): match their palette, darkness and stroke weight so the new icon sits in the same set; do not copy their layouts."""

BRANCH = {
 "storm": "BRANCH COLOR LINE (호풍환우 / Wind-Rain-Thunder tree, shared by 7 icons): charcoal storm-cloud ink and slate-grey wind wash, with ONE cold indigo-teal (쪽빛) moisture accent for rain/water. Lightning, when present, is a thin hard ivory-white crack painted in ink, matte, no blue neon. A small yellow paper talisman with dull vermilion marks may appear as the summoning source.",
 "paper": "BRANCH COLOR LINE (둔갑·환술 tree, PAPER column): ivory-cream hanji paper with crisp cut and folded edges, dull vermilion (주사) brush marks, on dark ink ground. Paper is the hero material; keep it matte and fibrous.",
 "seal": "BRANCH COLOR LINE (둔갑·환술 tree, TALISMAN column): muted mustard-yellow talisman paper with dull vermilion seal script marks (not legible letters) and heavy black ink chains, matching the adopted seal-array icon.",
 "shadow": "BRANCH COLOR LINE (둔갑·환술 tree, SHADOW column): near-black ink and deep navy, the figure dissolving into ink wash, a single dull-red sash flick as the only warm accent, matching the adopted hide icon.",
}

SLOTS = {
 "gust": ("storm", "돌개바람 (active) — a small whirlwind summoned at a spot that drags nearby enemies into its centre and nicks them.",
   "Doho in three-quarter view flings a yellow talisman forward; just ahead of him a compact, tight grey ink whirlwind spins on the ground, dust and torn leaves curving INWARD toward its eye. The whirlwind is the dominant shape; Doho is secondary on one side.",
   "No figure. A single compact spiral funnel of grey-charcoal ink filling the icon, dust and debris streaks all curving inward to the centre, a tiny yellow talisman fluttering at the eye of the spiral. Strong inward-pull read."),
 "shower": ("storm", "소나기 (active) — a rain field on the ground that soaks enemies (wet status). No damage.",
   "Doho raises a yellow talisman toward a low dark cloud; a dense slanted sheet of rain falls onto a round patch of ground in front of him, puddle rings on that patch with an indigo-teal water sheen.",
   "No figure. A heavy low cloud at the top, straight slanted rain lines falling onto a round ground patch below covered in ripple rings and indigo-teal water sheen. Clear 'rain zone' read."),
 "wet_sky": ("storm", "젖은 하늘 (passive) — lightning jumps more readily between soaked enemies.",
   "Dark rain cloud above; one ivory-white lightning bolt forks into three branches, each landing on a separate rain-soaked ground puddle ring with indigo-teal sheen. Compact passive motif, no Doho.",
   "A single big raindrop shape in indigo-teal ink with a thin ivory-white lightning crack branching inside it. Very simple, one emblem."),
 "fog": ("storm", "짙은 안개 (active) — a fog bank where enemies miss and Doho cannot be seen from afar.",
   "Doho's gat and shoulders half-dissolved in thick low grey mist bands; only the hat brim, one eye area and the red sash show through. A dark enemy claw swipes through empty mist beside him, missing.",
   "No full figure. Layered horizontal bands of thick grey mist fill the icon, a faint ghostly dark silhouette barely visible inside, one black arrow passing harmlessly through the mist. Soft but high-contrast banding."),
 "sky_qi": ("storm", "하늘 기운 (passive) — summoned weather spreads wider and lasts longer.",
   "A small yellow talisman at the centre with a wide storm-cloud ring spreading outward from it in widening concentric bands of cloud and rain, the outer band reaching the icon edges. No Doho.",
   "Top of the icon: a broad storm canopy of charcoal cloud stretching edge to edge over a small horizon line, rain veils hanging from it; a tiny talisman at the canopy's centre. Emphasises breadth."),
 "waterspout": ("storm", "용오름 (active) — a large tornado that walks slowly toward the cursor, sucking enemies into it.",
   "A towering twisted waterspout column (dragon-rising, 용오름) striding across the ground, debris spiralling up it, a faint dragon-coil shape suggested in the cloud at its top; Doho small at its foot pointing it forward.",
   "No figure. One tall S-curved funnel of charcoal and indigo-teal ink from cloud to ground, debris spiralling upward, the cloud top coiled like a dragon's body. Tall vertical read, distinct from a small whirlwind."),
 "storm_call": ("storm", "호풍환우 (ultimate) — a great storm surrounds Doho; everything inside is soaked and lightning falls on its own.",
   "Doho at centre holding a yellow talisman high overhead, a huge circular storm of wind and rain swirling around him, three ivory-white lightning bolts striking the ground around the ring. Dramatic, the most powerful of the storm icons.",
   "Eye-of-the-storm view: a large swirling ring of black cloud and rain around a calm centre where a tiny Doho silhouette stands, several ivory-white lightning bolts dropping at the rim of the ring."),
 "paper_soldier": ("paper", "종이 병사 (active) — a thrown paper-doll talisman becomes a sword-carrying paper soldier that chases and cuts enemies.",
   "A cut-paper hanji soldier figure unfolding upright out of a thrown talisman: folded paper chest armour, small Joseon jeollip soldier hat, a straight hwando sword in hand, vermilion marks on its body; Doho's hand releasing it from one corner.",
   "Close-up of a single cut-paper hanji soldier standing in guard with a straight sword, crisp folded paper edges, small jeollip hat, vermilion talisman marks on the chest. Paper-doll silhouette, no human skin."),
 "scarecrow": ("paper", "허수아비 (active) — a paper scarecrow decoy that all nearby enemies attack; when broken it bursts and briefly binds them.",
   "A paper-and-straw scarecrow on a pole, plastered with yellow talismans, arms out, standing at centre; several dark enemy silhouettes at the edges all turned toward it.",
   "A paper scarecrow mid-burst: its paper body tearing into scraps and short black ink chain links flying outward in a ring. Clear burst read."),
 "paper_mastery": ("paper", "종이 숙련 (passive) — paper constructs become tougher and sharper.",
   "Two fingers of Doho holding a single taut folded hanji sheet like a blade, its edge crisp and sharp as steel, vermilion seal mark on it. Compact passive emblem.",
   "A stack of layered folded hanji paper armour scales overlapping like a tough shield, crisp edges, one vermilion seal mark. Single emblem."),
 "binding_talisman": ("seal", "속박부 (active) — a talisman stabbed into the ground; a moment later nearby enemies are bound by black ink chains.",
   "Doho's hand driving a yellow talisman down into the ground; thick black ink chains burst out from it in several directions across the ground.",
   "No figure. A yellow talisman stuck upright in the ground at the centre, thick black ink chains coiling out from it in a full ring. Strong circular bind read."),
 "exorcist_qi": ("seal", "퇴마 기운 (passive) — every bound demon adds weight to Doho's next sword blow.",
   "Doho's straight sword held point-up, its blade wrapped by stacked black ink chain rings and a small yellow talisman, heavy and charged; faint chained ghost silhouettes in the dark background.",
   "A sword blade seen close up with several stacked chain rings sliding down it like weights, a yellow talisman tied at the hilt. Single emblem."),
 "shadow_blade": ("shadow", "그림자 칼 (passive) — the first blow from hiding is a guaranteed deadly critical.",
   "Doho lunging blade-first out of a pool of black ink shadow, only the sword edge and the gat brim catching cold light, red sash flicking behind. Ambush read.",
   "No full figure. A straight sword thrusting out of solid black ink, only its edge lit, a single dull-red sash ribbon trailing from the darkness."),
 "summon_general": ("paper", "신장 부르기 (ultimate) — summons a giant paper divine general (神將) that fights beside Doho and slams the ground.",
   "A towering hanji-paper divine general in Joseon-style layered paper armour with a large paper glaive, looming behind a small Doho; vermilion talisman marks on its chest. The most powerful of the paper icons.",
   "A giant paper fist / glaive of the paper general slamming the ground, shockwave ring of paper scraps flying outward. Huge scale read."),
}

def prompt(sid, var):
    br, meaning, a, b = SLOTS[sid]
    comp = a if var == "A" else b
    return f"{COMMON}\n{BRANCH[br]}\n\nSKILL: {sid} — {meaning}\nCOMPOSITION {var}: {comp}\nOutput only ONE complete square icon, not alternatives or a sheet."

if __name__ == "__main__":
    out = pathlib.Path(__file__).parent / "prompts"
    out.mkdir(exist_ok=True)
    for sid in SLOTS:
        for v in "AB":
            (out / f"{v}_{sid}.txt").write_text(prompt(sid, v), encoding="utf-8")
    json.dump({k: {"branch": v[0], "meaning": v[1], "A": v[2], "B": v[3]} for k, v in SLOTS.items()},
              open(out / "slots.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(SLOTS) * 2, "prompts")
