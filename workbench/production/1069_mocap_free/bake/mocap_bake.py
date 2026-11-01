"""#1069 mocap retime — KBS FBX 구간을 게임 박자로 다시 재고(anim_retime) · 끝을 첫 자세로 돌리고 · Root 반대 회전으로 몸 돌기를 줄여 FBX로."""
import bpy, sys, math, json
from mathutils import Vector, Matrix, Quaternion
sys.path.insert(0, "C:/workspace/joseon/tools/blender")
import anim_retime as AR
o = {}
for a in sys.argv[sys.argv.index("--")+1:]:
    k, _, v = a.lstrip("-").partition("="); o[k] = v
OUT_FPS = 60
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=o["fbx"])
arm = [x for x in bpy.data.objects if x.type == "ARMATURE"][0]
act = arm.animation_data.action
sc = bpy.context.scene
src_fps = sc.render.fps
rng = [float(x) for x in o["range"].split(",")]
rt = json.loads(o["retime"])
rt = AR._norm_retime(o["name"], rt, rng, None)
tm = AR.build_timing({"src": o["name"], "range": rng, "retime": rt}, src_fps, OUT_FPS)
n = tm.n
print("TIMING n=%d len=%.3f out=%s src=%s impact=%s" % (n, tm.length, tm.out, tm.src, tm.impact()))

def fcurves(a):
    for layer in a.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                for fc in cb.fcurves:
                    yield fc
fcs = list(fcurves(act))
src_at = [tm.src_at(i) for i in range(n + 1)]
vals = {fc: [fc.evaluate(s) for s in src_at] for fc in fcs}

# 끝 되돌리기: blend 시작 출력 프레임부터 끝까지 첫 출력 프레임 값으로 (쿼터니언은 묶어서 반구 맞춤)
b0 = int(o.get("blend_from", n))
if b0 < n:
    groups = {}
    for fc in fcs:
        groups.setdefault((fc.data_path), {})[fc.array_index] = fc
    for path, g in groups.items():
        quat = path.endswith("rotation_quaternion") and len(g) == 4
        for i in range(b0, n + 1):
            w = AR.smooth((i - b0) / float(max(1, n - b0)))
            if quat:
                q = Quaternion([vals[g[k]][i] for k in range(4)])
                t = Quaternion([vals[g[k]][0] for k in range(4)])
                if q.dot(t) < 0: t.negate()
                r = q.slerp(t, w)
                for k in range(4): vals[g[k]][i] = r[k]
            else:
                for fc in g.values():
                    vals[fc][i] = vals[fc][i] * (1 - w) + vals[fc][0] * w

for fc in fcs:
    v = vals[fc]
    kp = fc.keyframe_points
    kp.clear(); kp.add(n + 1)
    co = []
    for i in range(n + 1): co += [float(i), v[i]]
    kp.foreach_set("co", co)
    kp.foreach_set("interpolation", [1] * (n + 1))   # LINEAR
    fc.update()
sc.render.fps = OUT_FPS
sc.frame_start, sc.frame_end = 0, n

# 몸 돌기 줄이기: 골반 방향(세계 수평) 변화의 k만큼 Root를 반대로 돌린다
k = float(o.get("yawk", "0"))
root = arm.pose.bones["Root"]; hips = arm.pose.bones["Hips"]
mw = arm.matrix_world
up_arm = (mw.to_3x3().inverted() @ Vector((0, 0, 1))).normalized()
def hip_yaw():
    m = (mw @ hips.matrix).to_3x3()
    f = m @ Vector((0, 0, 1))
    return math.atan2(f.x, f.y)
yaws = []
for i in range(n + 1):
    sc.frame_set(i); yaws.append(hip_yaw())
un = [yaws[0]]
for y in yaws[1:]:
    d = (y - un[-1] + math.pi) % (2 * math.pi) - math.pi
    un.append(un[-1] + d)
print("YAW deg min/max rel", round(math.degrees(min(un) - un[0])), round(math.degrees(max(un) - un[0])))
if k:
    root.rotation_mode = "QUATERNION"
    base = {}
    for i in range(n + 1):
        sc.frame_set(i); base[i] = root.matrix.copy()
    for i in range(n + 1):
        c = k * (un[i] - un[0])   # Z축 +c 회전 = atan2(x,y) 쪽 -c
        p = base[i].to_translation()
        R = Matrix.Translation(p) @ Matrix.Rotation(c, 4, up_arm) @ Matrix.Translation(-p)
        sc.frame_set(i)
        root.matrix = R @ base[i]
        root.keyframe_insert("rotation_quaternion", frame=i)
        root.keyframe_insert("location", frame=i)
au = []
for i in range(n + 1):
    sc.frame_set(i); au.append(hip_yaw())
for i in range(1, len(au)):
    au[i] = au[i - 1] + (au[i] - au[i - 1] + math.pi) % (2 * math.pi) - math.pi
print("YAW_AFTER deg min/max rel", round(math.degrees(min(au) - au[0])), round(math.degrees(max(au) - au[0])))
act.name = o["name"]
bpy.ops.export_scene.fbx(filepath=o["out"], object_types={"ARMATURE"}, use_selection=False, add_leaf_bones=False,
                         bake_anim=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                         bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0)
print("WROTE", o["out"], "frames", n + 1, "impact", tm.impact())
