"""#1069 시안 — KBS FBX 여러 개의 구간을 이어 붙여(겹쳐 섞기) 한 동작으로 · Root 이동 이어 주기 · 끝 = 첫 자세(이동은 남김) · 몸 돌기 줄이기 → FBX.
    blender -b --factory-startup --python chain.py -- --out=<fbx> --name=<clip> --segs='[["<fbx>", 시작, 끝, 배속], …]' --xfade=6 [--blend_end=12] [--yawk=0.5]
배속 = 원본 30fps 기준 재생 배율. 출력 60fps. 구간 끝이 원본보다 길면(달리기 두 바퀴) 시작을 원본 길이로 넘겨 Root 이동을 이어 센다.
"""
import bpy, sys, math, json
from mathutils import Vector, Matrix, Quaternion

o = {}
for a in sys.argv[sys.argv.index("--") + 1:]:
    k, _, v = a.lstrip("-").partition("="); o[k] = v
OUT_FPS = 60
segs = json.loads(o["segs"])
XF = int(o.get("xfade", "6"))
bpy.ops.wm.read_factory_settings(use_empty=True)


def fcurves(a):
    for layer in a.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    yield fc


acts = {}
arm = None
for path, *_ in segs:
    if path in acts:
        continue
    before = set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=path)
    act = [x for x in bpy.data.actions if x not in before][0]
    if arm is None:
        arm = [x for x in bpy.data.objects if x.type == "ARMATURE"][0]
    acts[path] = act
main_act = acts[segs[-1][0]]          # 결과를 쓸 동작 = 마지막 구간 파일 것
arm.animation_data.action = main_act
chans = {(fc.data_path, fc.array_index): fc for fc in fcurves(main_act)}
lookup = {p: {(fc.data_path, fc.array_index): fc for fc in fcurves(a)} for p, a in acts.items()}
ROOT_LOC = 'pose.bones["Root"].location'


def sample(path, src, key):
    """원본 프레임 src(끝 넘으면 돌려 감고 Root 이동은 한 바퀴씩 더함)."""
    a = acts[path]
    f0, f1 = a.frame_range
    span = f1 - f0
    laps = 0
    while src > f1:
        src -= span; laps += 1
    fc = lookup[path].get(key)
    if fc is None:
        return None
    v = fc.evaluate(src)
    if key[0] == ROOT_LOC and laps:
        v += laps * (fc.evaluate(f1) - fc.evaluate(f0))
    return v


# 구간마다 출력 길이 · 구간 i는 앞 구간 끝 XF 프레임과 겹친다
plan, t = [], 0
for path, a, b, spd in segs:
    n = int(round((b - a) / 30.0 / spd * OUT_FPS))
    start = t if not plan else t - XF
    plan.append((path, a, b, start, n))
    t = start + n
N = t
print("PLAN", [(p.split("/")[-1], a, b, s, n) for p, a, b, s, n in plan], "N", N, "sec %.3f" % (N / OUT_FPS))

vals = {k: [0.0] * (N + 1) for k in chans}
root_off = [0.0, 0.0, 0.0]
seg_vals = []
for si, (path, a, b, start, n) in enumerate(plan):
    sv = {}
    for k in chans:
        arr = []
        for i in range(start, start + n + 1):
            src = a + (b - a) * (i - start) / float(n)
            v = sample(path, src, k)
            if v is None:
                v = sample(segs[-1][0], segs[-1][1], k)
            arr.append(v)
        sv[k] = arr
    # Root 이동 이음: 이 구간 첫 값 = 앞 구간이 이 구간 시작 시각에 있던 값
    if seg_vals:
        pstart, pv = seg_vals[-1]
        for c in range(3):
            k = (ROOT_LOC, c)
            if k in sv:
                prev_at = pv[k][start - pstart]
                d = prev_at - sv[k][0]
                sv[k] = [x + d for x in sv[k]]
    seg_vals.append((start, sv))

groups = {}
for k in chans:
    groups.setdefault(k[0], {})[k[1]] = k


def mix(i):
    """출력 프레임 i의 (구간 값들, 가중치)."""
    out = []
    for si, (start, sv) in enumerate(seg_vals):
        n = plan[si][4]
        if start <= i <= start + n:
            out.append((si, sv, i - start))
    if len(out) == 1:
        return [(out[0], 1.0)]
    (s0, v0, j0), (s1, v1, j1) = out[0], out[1]
    w = (i - seg_vals[s1][0]) / float(max(1, XF))
    w = w * w * (3 - 2 * w)
    return [((s0, v0, j0), 1 - w), ((s1, v1, j1), w)]


for i in range(N + 1):
    m = mix(i)
    for path, g in groups.items():
        quat = path.endswith("rotation_quaternion") and len(g) == 4
        if len(m) == 1:
            (_, sv, j), _ = m[0]
            for c, k in g.items():
                vals[k][i] = sv[k][j]
            continue
        ((_, va, ja), wa), ((_, vb, jb), wb) = m
        if quat:
            qa = Quaternion([va[g[c]][ja] for c in range(4)])
            qb = Quaternion([vb[g[c]][jb] for c in range(4)])
            if qa.dot(qb) < 0:
                qb.negate()
            r = qa.slerp(qb, wb)
            for c in range(4):
                vals[g[c]][i] = r[c]
        else:
            for c, k in g.items():
                vals[k][i] = va[k][ja] * wa + vb[k][jb] * wb

# 끝 = 마지막 구간 원본 첫 자세로 (Root 이동은 남김)
be = int(o.get("blend_end", "0"))
if be:
    b0 = N - be
    last_path, la = segs[-1][0], segs[-1][1]
    for path, g in groups.items():
        if path == ROOT_LOC:
            continue
        quat = path.endswith("rotation_quaternion") and len(g) == 4
        rest = {k: sample(last_path, la, k) for k in g.values()}
        for i in range(b0, N + 1):
            w = (i - b0) / float(be); w = w * w * (3 - 2 * w)
            if quat:
                q = Quaternion([vals[g[c]][i] for c in range(4)])
                r0 = Quaternion([rest[g[c]] for c in range(4)])
                if q.dot(r0) < 0:
                    r0.negate()
                r = q.slerp(r0, w)
                for c in range(4):
                    vals[g[c]][i] = r[c]
            else:
                for k in g.values():
                    vals[k][i] = vals[k][i] * (1 - w) + rest[k] * w

if o.get("center"):   # 미리보기 구도용: 이동 길의 가운데를 원점에
    for c in range(3):
        kk = (ROOT_LOC, c)
        if kk in vals:
            mid = (vals[kk][0] + vals[kk][-1]) / 2.0
            vals[kk] = [x - mid for x in vals[kk]]
for k, fc in chans.items():
    kp = fc.keyframe_points
    kp.clear(); kp.add(N + 1)
    co = []
    for i in range(N + 1):
        co += [float(i), vals[k][i]]
    kp.foreach_set("co", co)
    kp.foreach_set("interpolation", [1] * (N + 1))
    fc.update()
sc = bpy.context.scene
sc.render.fps = OUT_FPS
sc.frame_start, sc.frame_end = 0, N

# 몸 돌기 줄이기 — 골반 자리를 축으로 Root를 돌린다(이동 길은 그대로)
k = float(o.get("yawk", "0"))
root = arm.pose.bones["Root"]; hips = arm.pose.bones["Hips"]
mw = arm.matrix_world
up_arm = (mw.to_3x3().inverted() @ Vector((0, 0, 1))).normalized()


def hip_yaw():
    f = (mw @ hips.matrix).to_3x3() @ Vector((0, 0, 1))
    return math.atan2(f.x, f.y)


def unwrap(ys):
    for i in range(1, len(ys)):
        ys[i] = ys[i - 1] + (ys[i] - ys[i - 1] + math.pi) % (2 * math.pi) - math.pi
    return ys


ys, piv, base = [], [], []
for i in range(N + 1):
    sc.frame_set(i); ys.append(hip_yaw()); piv.append(hips.head.copy()); base.append(root.matrix.copy())
ys = unwrap(ys)
print("YAW rel", round(math.degrees(min(ys) - ys[0])), round(math.degrees(max(ys) - ys[0])))
if k:
    root.rotation_mode = "QUATERNION"
    for i in range(N + 1):
        c = k * (ys[i] - ys[0])
        p = piv[i]
        R = Matrix.Translation(p) @ Matrix.Rotation(c, 4, up_arm) @ Matrix.Translation(-p)
        sc.frame_set(i)
        root.matrix = R @ base[i]
        root.keyframe_insert("rotation_quaternion", frame=i)
        root.keyframe_insert("location", frame=i)
    ys2 = []
    for i in range(N + 1):
        sc.frame_set(i); ys2.append(hip_yaw())
    ys2 = unwrap(ys2)
    print("YAW_AFTER rel", round(math.degrees(min(ys2) - ys2[0])), round(math.degrees(max(ys2) - ys2[0])))
travel = []
for i in (0, N):
    sc.frame_set(i); travel.append(mw @ hips.head)
print("TRAVEL m %.2f" % (travel[1] - travel[0]).xy.length)
for x in list(bpy.data.objects):
    if x.type == "ARMATURE" and x != arm:
        bpy.data.objects.remove(x)
main_act.name = o["name"]
bpy.ops.export_scene.fbx(filepath=o["out"], object_types={"ARMATURE"}, add_leaf_bones=False, bake_anim=True,
                         bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                         bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0)
print("WROTE", o["out"], "frames", N + 1)
