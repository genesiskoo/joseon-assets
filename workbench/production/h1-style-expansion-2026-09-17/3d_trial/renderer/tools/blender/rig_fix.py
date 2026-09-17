# tools/blender/rig_fix.py — Meshy 자동 리그 손질 (Blender 헤드리스). design/art_3d_pipeline.md §12.
#   blender --background --python tools/blender/rig_fix.py -- --src=<rigged.glb> --out=<fixed.glb> [--hem=0.40] [--waist=0.98] [--sash_y=-0.145] [--fist=both] [--palm=down]
# 하는 일 (정점 좌표는 바인드(rest) 기준, 높이 = Blender z, 정면 = -y):
#   1) 치마 재가중치: 높이 hem~waist 구간의 정점에서 종아리·발 뼈 가중치를 없애고 골반(Hips)↔허벅지(UpLeg) 그라데이션으로 바꾼다.
#      중앙(|x|<0.18)은 양쪽 허벅지를 섞어 앞·뒤 가운데가 찢어지지 않게 한다. (Meshy 리그는 치맛자락을 종아리에 붙여 무릎이 접히면 자락이 접힘)
#   2) 허리끈 꼬리 보조 뼈: 정면(-y) 돌출 정점(허리끈 꼬리·술·펜던트)을 Hips 아래 새 뼈 SashTail1→SashTail2에 묶는다 → Godot SpringBoneSimulator3D가 흔든다.
#   3) 머리 과점유: 턱 아래(z<1.40)에 남은 Head 가중치를 neck으로 옮긴다.
#   4) 잡동사니(Icosphere) 제거, 4영향 정규화, NLA 트랙(클립 8~9) 그대로 GLB 내보내기(JPEG 텍스처, 30fps).
#   5) 주먹(검 파지): Meshy 7은 주먹 T-pose 입력에도 손을 펼쳐 뽑는다(GT1·D03 실측). 손가락 뼈가 없으니 rest 정점을 직접 만다 —
#      너클선 뒤 손가락 정점을 원호(반지름 R = 손가락 길이 / 말림각)로 감고, 엄지는 밑동을 축으로 손바닥 쪽으로 접는다.
#      원호 중심선 = 손아귀 = 검 손잡이 축 → `<out>_fist.json`(Blender 좌표)에 적고 `tools/weapon_socket.gd`가 ModelDef 보정값으로 바꾼다.
#      옵션: --fist=both|right|left|none(기본 both) --knuckle=0.45(손 길이 대비 너클 위치) --curl=170(말림각°) --thumb=110(엄지 접힘°) --adduct=0.3(벌어진 손가락 모음) --palm=down|up|front(T포즈 손바닥 방향, Meshy = down)
# 왜 Blender인가: 가중치·뼈 추가는 GLTFDocument(Godot)로도 가능하지만 Blender의 armature 편집·정규화·glTF 내보내기가 검증돼 있고,
#   결과를 곧바로 렌더로 확인할 수 있다. 헤드리스 스크립트라 캐릭터마다 재실행 가능(MCP 불요).
import bpy, sys, os, math, json
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opts = dict(a.lstrip("-").split("=", 1) for a in argv if "=" in a)
src = opts["src"]
out = opts["out"]
HEM = float(opts.get("hem", 0.40))
WAIST = float(opts.get("waist", 0.98))
SASH_Y = float(opts.get("sash_y", -0.145))   # 이보다 앞(-y)이면 허리끈 꼬리/술
SASH_X = float(opts.get("sash_x", 0.10))
SASH_Z = (float(opts.get("sash_z0", 0.45)), float(opts.get("sash_z1", 0.97)))
CENTER_BLEND = 0.18
CHIN = float(opts.get("chin", 1.40))
FIST = opts.get("fist", "both")
KNUCKLE = float(opts.get("knuckle", 0.45)); CURL = math.radians(float(opts.get("curl", 170))); THUMB = math.radians(float(opts.get("thumb", 110)))
ADDUCT = float(opts.get("adduct", 0.3)); PALM = opts.get("palm", "down")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
mesh = next(o for o in bpy.data.objects if o.type == "MESH" and o.parent == arm)
for o in list(bpy.data.objects):
    if o.type == "MESH" and o is not mesh:
        print("== remove stray:", o.name)
        bpy.data.objects.remove(o, do_unlink=True)

mw = mesh.matrix_world
verts = mesh.data.vertices
wpos = [mw @ v.co for v in verts]
zmin = min(p.z for p in wpos)
print("== src", src, "verts", len(verts), "zmin %.3f" % zmin)

vg = {g.name: g for g in mesh.vertex_groups}
def ensure(name):
    if name not in vg:
        vg[name] = mesh.vertex_groups.new(name=name)
    return vg[name]
def weights_of(v):
    return {mesh.vertex_groups[g.group].name: g.weight for g in v.groups}
def set_weights(v, w):
    for g in mesh.vertex_groups:
        g.remove([v.index])
    for name, val in w.items():
        if val > 1e-4:
            ensure(name).add([v.index], float(val), "REPLACE")

# ---------- 1) 치마 ----------
LEG_BONES = {"LeftLeg", "RightLeg", "LeftFoot", "RightFoot", "LeftToeBase", "RightToeBase", "LeftUpLeg", "RightUpLeg", "Hips"}
n_skirt = 0
for v, p in zip(verts, wpos):
    z = p.z - zmin
    if not (HEM <= z <= WAIST):
        continue
    w = weights_of(v)
    leg_w = sum(val for name, val in w.items() if name in LEG_BONES)
    if leg_w < 0.3:
        continue   # 팔·소매 등은 건드리지 않는다
    t = min(max((WAIST - z) / (WAIST - HEM), 0.0), 1.0)        # 허리 0 → 밑단 1
    s = min(max(0.5 + p.x / (2.0 * CENTER_BLEND), 0.0), 1.0)   # 오른쪽(-x) 0 → 왼쪽(+x) 1
    thigh = 0.85 * t
    new = {name: val for name, val in w.items() if name not in LEG_BONES}
    other = sum(new.values())
    scale = max(leg_w, 0.0)
    new["Hips"] = scale * (1.0 - thigh)
    new["LeftUpLeg"] = scale * thigh * s
    new["RightUpLeg"] = scale * thigh * (1.0 - s)
    set_weights(v, new)
    n_skirt += 1
print("== skirt reweighted:", n_skirt)

# ---------- 2) 허리끈 꼬리 보조 뼈 ----------
sash = [i for i, p in enumerate(wpos) if p.y < SASH_Y and abs(p.x) < SASH_X and SASH_Z[0] <= (p.z - zmin) <= SASH_Z[1]]
print("== sash candidates:", len(sash))
if sash:
    zs = [wpos[i].z - zmin for i in sash]
    z_top, z_bot = max(zs), min(zs)
    z_mid = (z_top + z_bot) * 0.5
    y_front = sum(wpos[i].y for i in sash) / len(sash)
    print("== sash z %.2f..%.2f  y_front %.3f" % (z_bot, z_top, y_front))
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.data.edit_bones
    inv = arm.matrix_world.inverted()
    def add_bone(name, parent_name, head_w, tail_w):
        b = eb.new(name)
        b.head = inv @ Vector(head_w)
        b.tail = inv @ Vector(tail_w)
        b.parent = eb[parent_name]
        b.use_connect = False
        b.use_deform = True
        return b
    add_bone("SashTail1", "Hips", (0.0, y_front, zmin + z_top), (0.0, y_front, zmin + z_mid))
    add_bone("SashTail2", "SashTail1", (0.0, y_front, zmin + z_mid), (0.0, y_front, zmin + z_bot))
    bpy.ops.object.mode_set(mode="OBJECT")
    ensure("SashTail1"); ensure("SashTail2")
    for i in sash:
        z = wpos[i].z - zmin
        f = (z_top - z) / max(z_top - z_bot, 1e-4)   # 0 = 위, 1 = 아래
        # 위쪽 15%는 Hips에 남겨 뿌리가 붙어 있게, 그 아래는 1→2로 그라데이션
        if f < 0.15:
            w = {"Hips": 1.0 - f / 0.15 * 0.5, "SashTail1": f / 0.15 * 0.5}
        else:
            g = (f - 0.15) / 0.85
            w = {"SashTail1": 1.0 - g, "SashTail2": g}
        set_weights(verts[i], w)
    print("== sash bones added, weights set")

# ---------- 3) 머리 과점유 ----------
# 턱 아래에 남은 Head 가중치(갓끈 구슬·깃·가슴이 머리에 끌려감): 목 구간(CHIN-0.10 이상)은 neck, 그 아래(가슴)는 Spine01로.
SHOULDER = CHIN - 0.10
n_head = 0
for v, p in zip(verts, wpos):
    z = p.z - zmin
    if z >= CHIN:
        continue
    w = weights_of(v)
    h = w.get("Head", 0.0)
    if h <= 0.0:
        continue
    target = "neck" if z >= SHOULDER else "Spine01"
    w[target] = w.get(target, 0.0) + h
    del w["Head"]
    set_weights(v, w)
    n_head += 1
print("== head→neck/Spine01 below chin:", n_head)

# ---------- 4) 정규화·4영향 ----------
for v in verts:
    w = weights_of(v)
    top4 = dict(sorted(w.items(), key=lambda kv: -kv[1])[:4])
    s = sum(top4.values())
    if s <= 0:
        continue
    set_weights(v, {k: val / s for k, val in top4.items()})


# ---------- 5) 주먹(검 파지) ----------
aw = arm.matrix_world
mwi = mw.inverted()
fist_report = {}
def make_fist(side):
    hb = arm.data.bones.get(side + "Hand"); fb = arm.data.bones.get(side + "ForeArm")
    if hb is None or fb is None:
        print("== fist: bones missing for", side); return
    wrist = aw @ hb.head_local; elbow = aw @ fb.head_local
    f = (wrist - elbow).normalized()                                   # 손가락 방향 = 팔뚝 축(T포즈)
    p = {"down": Vector((0, 0, -1)), "up": Vector((0, 0, 1)), "front": Vector((0, -1, 0))}[PALM]
    p = (p - f * p.dot(f)).normalized()                                # 손바닥이 향하는 쪽
    k = (f.cross(p) if side == "Right" else p.cross(f)).normalized()   # 너클 축, 엄지(정면 -y) 쪽이 +
    if (side + "Hand") not in vg:
        print("== fist: no vertex group", side); return
    gidx = vg[side + "Hand"].index
    hv = [v for v in verts if any(g.group == gidx and g.weight > 0.3 for g in v.groups)]
    if len(hv) < 20:
        print("== fist: too few hand verts", side, len(hv)); return
    P = {v.index: wpos[v.index] for v in hv}
    L_hand = max((P[i] - wrist).dot(f) for i in P)
    dk = KNUCKLE * L_hand
    L = L_hand - dk
    R = L / CURL
    K0 = wrist + f * dk
    fingers = [v for v in hv if (P[v.index] - wrist).dot(f) > dk]
    thumb = [v for v in hv if 0.02 < (P[v.index] - wrist).dot(f) < dk + 0.04 and (P[v.index] - wrist).dot(k) > 0.045]
    wmid = sum(((P[v.index] - K0).dot(k) for v in fingers), 0.0) / max(len(fingers), 1)
    for v in fingers:
        q = P[v.index] - K0
        d = q.dot(f); h = q.dot(p); w = q.dot(k)
        u = min(max(d / L, 0.0), 1.0)
        w = wmid + (w - wmid) * (1.0 - ADDUCT * u)                      # 벌어진 손가락 모음
        phi = CURL * u
        Cw = K0 + k * w + p * R                                         # 원호 중심(손아귀 축 위)
        r = f * math.sin(phi) - p * math.cos(phi)
        t = f * math.cos(phi) + p * math.sin(phi)
        v.co = mwi @ (Cw + r * (R - h) + t * max(d - L, 0.0))
    if thumb:
        base_d = min((P[v.index] - wrist).dot(f) for v in thumb)
        base = wrist + f * (base_d + 0.01) + k * 0.045
        axis = k.cross(p).normalized()                                  # 엄지가 손바닥 쪽으로 접히는 축
        for v in thumb:
            q = P[v.index] - base
            frac = min(max(q.dot(k) / 0.05, 0.0), 1.0)                  # 밑동 30% → 끝 100%
            v.co = mwi @ (base + Matrix.Rotation(THUMB * (0.3 + 0.7 * frac), 4, axis) @ q)
    grip = K0 + k * wmid + p * R
    fist_report[side] = {"grip": [round(c, 4) for c in grip], "blade_dir": [round(c, 4) for c in k], "width_dir": [round(c, 4) for c in f],
                         "wrist": [round(c, 4) for c in wrist], "hand_len": round(L_hand, 4), "R": round(R, 4), "fingers": len(fingers), "thumb": len(thumb),
                         "coords": "blender world (z up, -y front)"}
    print("== fist %s: hand %.3f m, knuckle %.3f, fingers %d, thumb %d, R %.3f, grip %s" % (side, L_hand, dk, len(fingers), len(thumb), R, tuple(round(c, 3) for c in grip)))
if FIST in ("both", "right"):
    make_fist("Right")
if FIST in ("both", "left"):
    make_fist("Left")
if fist_report:
    mesh.data.update()
    rep = os.path.splitext(out)[0] + "_fist.json"
    json.dump(fist_report, open(rep, "w"), indent=1)
    print("== fist report", rep)

# ---------- 렌더(확인용): 최대 가중치 본 색 + 허리끈 선택 흰색 ----------
import colorsys
gnames = {g.index: g.name for g in mesh.vertex_groups}
top = {}
best_of = []
for v in verts:
    best = None
    for g in v.groups:
        if best is None or g.weight > best[1]:
            best = (gnames[g.group], g.weight)
    best_of.append(best)
    if best: top[best[0]] = top.get(best[0], 0) + 1
print("== top-weight bone counts(after):", json.dumps(dict(sorted(top.items(), key=lambda kv: -kv[1])), ensure_ascii=False))
bone_color = {name: colorsys.hsv_to_rgb((i * 0.618) % 1.0, 0.8, 0.95) for i, name in enumerate(sorted(top.keys()))}
ca = mesh.data.color_attributes.new(name="bone_id", type="BYTE_COLOR", domain="POINT")
for v, best in zip(verts, best_of):
    c = bone_color.get(best[0], (0.3, 0.3, 0.3)) if best else (0.3, 0.3, 0.3)
    if best and best[0].startswith("SashTail"):
        c = (1.0, 1.0, 1.0)
    ca.data[v.index].color = (c[0], c[1], c[2], 1.0)
mesh.data.color_attributes.active_color = ca
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "FLAT"
scene.display.shading.color_type = "VERTEX"
scene.render.resolution_x = 700; scene.render.resolution_y = 900
cam_data = bpy.data.cameras.new("C"); cam_data.type = "ORTHO"; cam_data.ortho_scale = 2.0
cam = bpy.data.objects.new("Cam", cam_data); scene.collection.objects.link(cam); scene.camera = cam
arm.data.pose_position = "REST"
center = Vector((0.0, 0.0, zmin + 0.85))
out_dir = os.path.join(os.path.dirname(out), "rig_fix_render")
os.makedirs(out_dir, exist_ok=True)
for tag, off, rot in [("front", Vector((0, -10, 0)), (math.radians(90), 0, 0)), ("side", Vector((10, 0, 0)), (math.radians(90), 0, math.radians(90)))]:
    cam.location = center + off; cam.rotation_euler = rot
    scene.render.filepath = os.path.join(out_dir, "after_%s.png" % tag)
    bpy.ops.render.render(write_still=True)
if fist_report and "Right" in fist_report:
    # 오른손 클로즈업(텍스처 색): 주먹·엄지 확인용
    scene.display.shading.color_type = "TEXTURE"; scene.display.shading.light = "STUDIO"
    cam_data.ortho_scale = 0.32; scene.render.resolution_x = 600; scene.render.resolution_y = 600
    wr = Vector(fist_report["Right"]["wrist"]); fd = Vector(fist_report["Right"]["width_dir"])
    hc = wr + fd * 0.09
    for tag, off, rot in [("front", Vector((0, -2, 0)), (math.radians(90), 0, 0)), ("top", Vector((0, 0, 2)), (0, 0, 0)), ("below", Vector((0, 0, -2)), (math.radians(180), 0, 0))]:
        cam.location = hc + off; cam.rotation_euler = rot
        scene.render.filepath = os.path.join(out_dir, "fist_right_%s.png" % tag)
        bpy.ops.render.render(write_still=True)
arm.data.pose_position = "POSE"

# ---------- 내보내기 ----------
mesh.data.color_attributes.remove(ca)
bpy.data.objects.remove(cam, do_unlink=True)
if arm.animation_data:
    arm.animation_data.action = None   # 활성 액션 없이 NLA 트랙만 → 클립 8개가 각각 애니로
# fps는 임포트 때의 씬 fps(24)를 그대로 둔다 — 여기서 30으로 바꾸면 프레임 수는 그대로인 채 재생이 25% 빨라진다(실측: attack 1.50→1.23s)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_animations=True, export_animation_mode="NLA_TRACKS",
                          export_skins=True, export_all_influences=False, export_image_format="JPEG", export_jpeg_quality=92,
                          export_yup=True, export_apply=False, export_morph=False, export_lights=False, export_cameras=False)
print("== exported", out, os.path.getsize(out))
print("== DONE")
