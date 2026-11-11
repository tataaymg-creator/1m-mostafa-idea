"""LOOK blocking v2 - animated runs.

Solid colour-coded mannequins (one object per body part, keyed every frame so the
joints stay connected), grey set, cameras that cut on the run's timecodes through
timeline markers. 24 fps, frame 1 = 0.0 s.
"""
import math
import random

import bpy  # noqa: F401
import bmesh
from mathutils import Euler, Matrix, Quaternion, Vector

import look_set as L

FPS = 24
F84, F63, F47, F29, F18, F12 = 19.99, 29.37, 41.40, 69.43, 113.65, 171.27

SOLID = {
    "adam": (0.10, 0.30, 0.90),
    "doll-wife": (0.85, 0.10, 0.10),
    "doll-daughter": (1.00, 0.80, 0.00),
    "layla": (0.58, 0.22, 0.85),
    "nour": (1.00, 0.48, 0.00),
    "mona": (0.10, 0.62, 0.22),
}

TRACKS, PROPS, CAMSEGS, VISKEYS, ANIMSET = [], [], [], [], []


def reset():
    L.reset()
    for lst in (TRACKS, PROPS, CAMSEGS, VISKEYS, ANIMSET):
        lst.clear()


def smat(name, rgb):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1.0)
    return m


def new_obj(name, bm, rgb, coll="Figures"):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    L.coll(coll).objects.link(ob)
    ob.data.materials.append(smat("mat_" + name.split(".")[0].split("_")[0], rgb) if coll == "Figures" else smat(name, rgb))
    ob.rotation_mode = "QUATERNION"
    return ob


# ====================================================================== pose interpolation
def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_vec(v):
    return isinstance(v, (tuple, list, Vector)) and len(v) in (2, 3) and all(_is_num(x) for x in v)


def _lerp(a, b, u):
    if _is_num(a) and _is_num(b):
        return a + (b - a) * u
    if _is_vec(a) and _is_vec(b) and len(a) == len(b):
        return tuple(x + (y - x) * u for x, y in zip(a, b))
    return a if u < 0.5 else b


def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


class K:
    """A key: time, root location (x, y[, z]), yaw in degrees (or a 3x3 Matrix), pose dict."""

    def __init__(self, t, loc, yaw, pose, ease="smooth"):
        self.t = t
        self.loc = tuple(loc) if len(loc) == 3 else (loc[0], loc[1], 0.0)
        self.yaw = yaw
        self.pose = dict(pose)
        self.ease = ease


class Track:
    """A figure through the run. keys: list of K. root: optional callable t -> (loc, Matrix3).
    Values inside a pose may be callables (t, S) -> value, S = figures already solved this frame."""

    def __init__(self, key, keys=None, name=None, root=None, wig=None, missing_until=None):
        self.key, self.name = key, name or key
        self.keys = sorted(keys or [], key=lambda k: k.t)
        self.root = root
        self.wig = wig                    # callable t -> wig offset (head frame) or None
        self.missing_until = missing_until  # {'larm': t} part hidden until t
        self._resolve()
        TRACKS.append(self)

    def _rot(self, k):
        return k.yaw if isinstance(k.yaw, Matrix) else Euler((0, 0, math.radians(k.yaw))).to_matrix()

    def _resolve(self):
        # give every key explicit hand and foot targets and numeric head angles,
        # so neighbouring keys can be interpolated joint by joint
        for k in self.keys:
            p = k.pose
            static = {a: b for a, b in p.items() if not callable(b)}
            try:
                f = L.Figure(self.key, k.loc, pose=static, rot=self._rot(k))
            except Exception:
                continue
            for side in ("l", "r"):
                h = p.get(f"{side}hand")
                if h is None or (isinstance(h, tuple) and h and isinstance(h[0], str)):
                    p[f"{side}hand"] = tuple(f.joint(f"{side}wrist"))
                if p.get(f"{side}foot") is None:
                    p[f"{side}foot"] = tuple(f.J[f"{side}ankle"])
            if "look" in p and not callable(p["look"]):
                p["hyaw"], p["hpitch"] = f.hyaw, f.hpitch
                del p["look"]
            for fld in ("lean", "tyaw", "troll", "hyaw", "hpitch", "hroll"):
                p.setdefault(fld, 0.0)
            p.setdefault("pyaw", p["tyaw"] * 0.4)

    def root_at(self, t):
        return self.at(t, None, root_only=True)

    def at(self, t, S, root_only=False):
        ks = self.keys
        if t <= ks[0].t:
            a = b = ks[0]
            u = 0.0
        elif t >= ks[-1].t:
            a = b = ks[-1]
            u = 0.0
        else:
            i = max(j for j in range(len(ks)) if ks[j].t <= t)
            a, b = ks[i], ks[i + 1]
            u = (t - a.t) / (b.t - a.t)
            u = smooth(u) if b.ease == "smooth" else u
        if self.root is not None:
            loc, R = self.root(t)
        else:
            loc = _lerp(a.loc, b.loc, u)
            if isinstance(a.yaw, Matrix) or isinstance(b.yaw, Matrix):
                qa, qb = self._rot(a).to_quaternion(), self._rot(b).to_quaternion()
                R = qa.slerp(qb, u).to_matrix()
            else:
                ya, yb = a.yaw, b.yaw
                while yb - ya > 180:
                    yb -= 360
                while yb - ya < -180:
                    yb += 360
                R = Euler((0, 0, math.radians(ya + (yb - ya) * u))).to_matrix()
        if root_only:
            return Vector(loc), R
        pose = {}
        for fld in set(a.pose) | set(b.pose):
            va, vb = a.pose.get(fld, b.pose.get(fld)), b.pose.get(fld, a.pose.get(fld))
            v = va if va is vb else _lerp(va, vb, u)
            if callable(v):
                v = v(t, S)
            pose[fld] = v
        f = L.Figure(self.key, loc, pose=pose, rot=R, name=self.name)
        f.t = t
        return f


# ====================================================================== figure parts
def build_parts(tr):
    s = L.SCALE[tr.key]
    rgb = SOLID[tr.key]
    parts = {}

    def mk(name, fn):
        bm = bmesh.new()
        fn(bm)
        parts[name] = new_obj(f"{tr.name}_{name}", bm, rgb)

    mk("torso", lambda bm: (L.bm_sphere(bm, (0, 0, 0.05 * s), (0.155 * s, 0.11 * s, 0.13 * s)),
                            L.bm_sphere(bm, (0, 0, 0.36 * s), (0.17 * s, 0.11 * s, 0.19 * s)),
                            L.bm_cyl(bm, (0, 0, 0.05 * s), (0, 0, 0.36 * s), 0.125 * s)))

    def head(bm):
        L.bm_cyl(bm, (0, 0, -0.03 * s), (0, 0, 0.06 * s), 0.05 * s)
        c = Vector((0, 0, 0.13 * s))
        L.bm_sphere(bm, c, (0.085 * s, 0.1 * s, 0.115 * s))
        L.bm_sphere(bm, c + Vector((0, 0.1 * s, -0.012 * s)), (0.02 * s, 0.03 * s, 0.022 * s), seg=(8, 6))
        for e in (-1, 1):
            L.bm_sphere(bm, c + Vector((e * 0.036 * s, 0.085 * s, 0.022 * s)), (0.016 * s,) * 3, seg=(8, 6))
    mk("head", head)
    if tr.wig is not None:
        mk("wig", lambda bm: L.bm_sphere(bm, (0, -0.012 * s, 0.03 * s), (0.094 * s, 0.1 * s, 0.1 * s), seg=(12, 7)))
    ua, fa, th, sh = 0.30 * s, 0.28 * s, 0.45 * s, 0.45 * s
    for side in ("l", "r"):
        mk(f"{side}uarm", lambda bm: L.bm_capsule(bm, (0, 0, 0), (0, 0, ua), 0.046 * s))
        mk(f"{side}farm", lambda bm: (L.bm_capsule(bm, (0, 0, 0), (0, 0, fa), 0.04 * s),
                                      L.bm_sphere(bm, (0, 0, fa + 0.05 * s), (0.045 * s,) * 3, seg=(10, 6))))
        mk(f"{side}thigh", lambda bm: L.bm_capsule(bm, (0, 0, 0), (0, 0, th), 0.07 * s))
        mk(f"{side}shin", lambda bm: L.bm_capsule(bm, (0, 0, 0), (0, 0, sh), 0.055 * s))
        mk(f"{side}foot", lambda bm: L.bm_box(bm, (0, 0.07 * s, -0.035 * s), (0.09 * s, 0.25 * s, 0.07 * s)))
    tr.parts = parts
    tr.rec = {n: [] for n in parts}


def _qdir(d):
    return Vector((0, 0, 1)).rotation_difference(d) if d.length > 1e-6 else Quaternion()


def record(tr, f):
    M3 = f.M.to_3x3()
    W = f.joint
    rec = tr.rec
    rec["torso"].append((W("pelvis"), (M3 @ f.Rt).to_quaternion()))
    hq = (M3 @ f.Rh).to_quaternion()
    rec["head"].append((W("neck"), hq))
    if "wig" in rec:
        off = Vector(tr.wig(f.t))
        rec["wig"].append((W("head") + (M3 @ f.Rh) @ off, hq))
    for side in ("l", "r"):
        for part, a, b in (("uarm", "shoulder", "elbow"), ("farm", "elbow", "wrist"),
                           ("thigh", "hip", "knee"), ("shin", "knee", "ankle")):
            pa, pb = W(side + a), W(side + b)
            rec[side + part].append((pa, _qdir(pb - pa)))
        fy = f.pose.get(f"{side}foot_yaw")
        fr = Euler((0, 0, math.radians(fy))).to_matrix() if fy is not None else (M3 @ f.Rp)
        rec[side + "foot"].append((W(side + "ankle"), fr.to_quaternion()))


# ====================================================================== props
class Prop:
    """A loose object. build(bm) at its own origin; track(t, S) -> (loc, quat or None)."""

    def __init__(self, name, build, rgb, track, scale_track=None, coll="Figures"):
        bm = bmesh.new()
        build(bm)
        self.obj = new_obj(name, bm, rgb, coll=coll)
        self.track, self.scale_track = track, scale_track
        self.rec, self.srec = [], []
        PROPS.append(self)


def follow(fig, joint, off=(0, 0, 0), frame="world"):
    def fn(t, S):
        f = S[fig]
        if frame == "world":
            return f.joint(joint) + Vector(off), None
        return f.joint(joint) + f.M.to_3x3() @ Vector(off), f.M.to_3x3().to_quaternion()
    return fn


def mid_hands(fig, off=(0, 0, 0)):
    def fn(t, S):
        f = S[fig]
        return (f.joint("lwrist") + f.joint("rwrist")) / 2 + Vector(off), f.M.to_3x3().to_quaternion()
    return fn


def static(loc, yaw=0.0):
    q = Euler((0, 0, math.radians(yaw))).to_quaternion()
    return lambda t, S: (Vector(loc), q)


def phases(*segs):
    """segs: (t_end, fn) in order; fn used while t < t_end, the last one after."""
    def fn(t, S):
        for te, g in segs:
            if t < te:
                return g(t, S)
        return segs[-1][1](t, S)
    return fn


def vis(obj, keys):
    """keys: [(t, visible)]"""
    VISKEYS.append((obj, keys))


# ====================================================================== cameras
class Cam:
    def __init__(self, name, t0, t1, loc, aim, fov_lens, loc1=None, aim1=None, hand=None, roll=0.0):
        cd = bpy.data.cameras.new(name)
        cd.lens, cd.sensor_width, cd.sensor_fit = fov_lens, 36.0, "HORIZONTAL"
        cd.clip_start, cd.clip_end = 0.02, 800.0
        self.obj = bpy.data.objects.new(name, cd)
        L.coll("Cameras").objects.link(self.obj)
        self.t0, self.t1 = t0, t1
        self.loc, self.aim, self.loc1, self.aim1 = loc, aim, loc1, aim1
        self.hand, self.roll = hand, roll
        self.rec = []
        self._fixed = None
        CAMSEGS.append(self)

    def sample(self, t, S):
        if self._fixed is None:
            ev = lambda v: Vector(v(S) if callable(v) else v)  # noqa: E731
            self._fixed = (ev(self.loc), ev(self.aim),
                           ev(self.loc1) if self.loc1 is not None else None,
                           ev(self.aim1) if self.aim1 is not None else None)
        l0, a0, l1, a1 = self._fixed
        u = smooth((t - self.t0) / max(1e-6, self.t1 - self.t0))
        loc = l0.lerp(l1, u) if l1 is not None else l0
        aim = a0.lerp(a1, u) if a1 is not None else a0
        e = (aim - loc).to_track_quat("-Z", "Y").to_euler()
        if self.roll:
            e.rotate_axis("Z", math.radians(self.roll))
        self.rec.append((self.frame(t), loc.copy(), e))

    @staticmethod
    def frame(t):
        return int(round(t * FPS)) + 1


HAND = {"gentle": (0.012, 0.3, 1.5), "tremor": (0.015, 0.4, 0.4), "rough": (0.045, 1.5, 0.3),
        "breath": (0.006, 0.15, 2.0)}


# ====================================================================== baking
def _fcurves(ob, path):
    ad = ob.animation_data
    act = ad.action
    try:
        from bpy_extras import anim_utils
        fcs = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot).fcurves
    except Exception:
        fcs = act.fcurves
    return sorted((fc for fc in fcs if fc.data_path == path), key=lambda fc: fc.array_index)


def bake(ob, path, frames, values):
    ob.keyframe_insert(path, frame=frames[0])
    for fc in _fcurves(ob, path):
        i = fc.array_index
        kp = fc.keyframe_points
        n = len(frames)
        while len(kp) > 0:
            kp.remove(kp[0], fast=True)
        kp.add(n)
        co = []
        for fr, v in zip(frames, values):
            co += [fr, v[i]]
        kp.foreach_set("co", co)
        kp.foreach_set("handle_left", co)
        kp.foreach_set("handle_right", co)
        for k in kp:
            k.interpolation = "LINEAR"
        fc.update()


def run_bake(duration):
    sc = bpy.context.scene
    n = int(round(duration * FPS))
    sc.frame_start, sc.frame_end = 1, n
    for tr in TRACKS:
        build_parts(tr)
    frames = list(range(1, n + 1))
    for fr in frames:
        t = (fr - 1) / FPS
        S = {}
        for tr in TRACKS:
            f = tr.at(t, S)
            S[tr.name] = f
            record(tr, f)
        for p in PROPS:
            loc, q = p.track(t, S)
            p.rec.append((Vector(loc), q if q is not None else Quaternion()))
            if p.scale_track:
                p.srec.append(tuple(p.scale_track(t)))
        for c in CAMSEGS:
            if c.t0 - 1e-6 <= t < c.t1 - 1e-6 or (fr == n and abs(c.t1 - duration) < 1e-6 and t >= c.t0):
                c.sample(t, S)
    for tr in TRACKS:
        for name, ob in tr.parts.items():
            locs = [r[0] for r in tr.rec[name]]
            qs = []
            prev = None
            for r in tr.rec[name]:
                q = r[1].copy()
                if prev is not None:
                    q.make_compatible(prev)
                qs.append(q)
                prev = q
            bake(ob, "location", frames, [tuple(v) for v in locs])
            bake(ob, "rotation_quaternion", frames, [tuple(q) for q in qs])
        if tr.missing_until:
            for part, tm in tr.missing_until.items():
                for nm in (f"{part[0]}uarm", f"{part[0]}farm"):
                    vis(tr.parts[nm], [(0.0, False), (tm, True)])
    for p in PROPS:
        qs, prev = [], None
        for _, q in p.rec:
            q = q.copy()
            if prev is not None:
                q.make_compatible(prev)
            qs.append(q)
            prev = q
        bake(p.obj, "location", frames, [tuple(r[0]) for r in p.rec])
        bake(p.obj, "rotation_quaternion", frames, [tuple(q) for q in qs])
        if p.srec:
            bake(p.obj, "scale", frames, p.srec)
    rng = random.Random(7)
    for c in CAMSEGS:
        ob = c.obj
        ob.rotation_mode = "XYZ"
        fr = [r[0] for r in c.rec]
        bake(ob, "location", fr, [tuple(r[1]) for r in c.rec])
        bake(ob, "rotation_euler", fr, [tuple(r[2]) for r in c.rec])
        if c.hand:
            amp, deg, period = HAND[c.hand]
            for path, a in (("location", amp), ("rotation_euler", math.radians(deg))):
                for fc in _fcurves(ob, path):
                    m = fc.modifiers.new("NOISE")
                    m.strength = 4 * a
                    m.scale = period * FPS
                    m.phase = rng.uniform(0, 100)
        mk = sc.timeline_markers.new(ob.name, frame=Cam.frame(c.t0))
        mk.camera = ob
    if CAMSEGS:
        sc.camera = CAMSEGS[0].obj
    for ob, keys in VISKEYS:
        for t, v in keys:
            f = Cam.frame(t)
            ob.hide_viewport = not v
            ob.hide_render = not v
            ob.keyframe_insert("hide_viewport", frame=f)
            ob.keyframe_insert("hide_render", frame=f)
    sc.frame_set(1)


# ====================================================================== look
def look():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1280, 720, 100
    sc.render.fps = FPS
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("World")
    w.color = (0.92, 0.92, 0.92)
    sc.world = w
    for ob in L.SET_OBJS:
        n = ob.name
        if n.startswith(("floor", "rug", "nour_rug", "doormat", "road", "ground")):
            g = 0.55 if not n.startswith(("rug", "nour_rug", "doormat")) else 0.48
        elif n.startswith("ceiling"):
            g = 0.88
        elif n.startswith(("wall", "skirt")):
            g = 0.8
        elif n.startswith(("curtain", "k_curtain")):
            g = 0.66
        elif n.startswith("dash"):
            g = 0.95
        else:
            g = 0.62
        ob.data.materials.clear()
        ob.data.materials.append(smat(f"set_{int(g * 100)}", (g, g, g)))

    def shade(s):
        s.light = "STUDIO"
        s.color_type = "MATERIAL"
        s.show_cavity = True
        s.cavity_type = "BOTH"
        s.show_shadows = False
        s.show_backface_culling = True
        s.show_object_outline = False
    shade(sc.display.shading)
    for scr in bpy.data.screens:
        for area in scr.areas:
            if area.type != "VIEW_3D":
                continue
            for sp in area.spaces:
                if sp.type != "VIEW_3D":
                    continue
                sp.shading.type = "SOLID"
                shade(sp.shading)
                sp.overlay.show_floor = False
                sp.overlay.show_axis_x = sp.overlay.show_axis_y = sp.overlay.show_axis_z = False
                sp.clip_start, sp.clip_end = 0.02, 800.0
                if sp.region_3d is not None:
                    sp.region_3d.view_perspective = "CAMERA"


def report():
    """Where each figure's head lands in the camera live at the start of each segment."""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    out = []
    for c in CAMSEGS:
        f = Cam.frame(c.t0)
        sc.frame_set(f)
        sc.camera = c.obj
        dg = bpy.context.evaluated_depsgraph_get()
        line = [f"{c.obj.name} @{c.t0:.1f}s:"]
        for tr in TRACKS:
            p = tr.parts["head"].matrix_world @ Vector((0, 0, 0.13 * L.SCALE[tr.key]))
            v = world_to_camera_view(sc, c.obj, p)
            if 0 <= v.x <= 1 and 0 <= v.y <= 1 and v.z > 0:
                d = p - c.obj.matrix_world.translation
                hit, _l, _n, _i, ob, _m = sc.ray_cast(dg, c.obj.matrix_world.translation, d.normalized(), distance=d.length - 0.1)
                tag = "seen" if not hit or ob.name.startswith(tr.name + "_") else f"behind {ob.name}"
                line.append(f"{tr.name}({v.x:.2f},{v.y:.2f}) {tag}")
            else:
                line.append(f"{tr.name} out")
        out.append("  ".join(line))
    if CAMSEGS:
        sc.camera = CAMSEGS[0].obj
    sc.frame_set(1)
    return out
