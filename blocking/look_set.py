"""LOOK - shared blocking module: one grey-box apartment, one car interior,
colour-coded mannequins, cameras and the outline look.

Axes: metres, Z up, floor Z = 0.
Apartment plan (wall centre lines):
  Main room (dining north, living south)  x 0..5,   y 0..9   curtains on the west wall (x = 0)
  Kitchen                                 x 5..8.2, y 6..9   door from the dining room on x = 5
  Hallway                                 x 5..12,  y 4.6..6 opens off the main room on x = 5,
                                                             front door at x = 12
  Nour's room                             x 9..12,  y 1.6..4.6  door from the hall on y = 4.6
  Landing                                 x 12..15, y 3..7.6
Car: its own scene, origin at the middle of the car floor, +Y forward, +X to the right,
left-hand drive.

Every figure is built in its own local frame (faces +Y, own right +X) and placed with a
location and a Z rotation. Nothing in the scene carries text, numbers or labels.
"""
import math
import os

import bpy  # noqa: F401  (loads bmesh/mathutils when run as a module)
import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

# ---------------------------------------------------------------- colours
COL = {
    "adam": (0.10, 0.32, 0.90),
    "doll-wife": (0.88, 0.10, 0.10),
    "doll-daughter": (0.95, 0.72, 0.00),
    "layla": (0.55, 0.18, 0.80),
    "nour": (1.00, 0.45, 0.00),
    "mona": (0.10, 0.62, 0.22),
}
SCALE = {"adam": 1.0, "doll-wife": 0.97, "doll-daughter": 0.64,
         "layla": 0.95, "nour": 0.64, "mona": 0.95}
SET_LINE = (0.55, 0.55, 0.55)
WHITE = (1.0, 1.0, 1.0)
FLOOR_FILL = (0.86, 0.86, 0.86)
CEIL_FILL = (0.93, 0.93, 0.93)

H = 2.75          # apartment ceiling height
WT = 0.15         # wall thickness
DOOR_H = 2.1

_mats = {}
SET_OBJS = []
FIG_OBJS = []


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()
    SET_OBJS.clear()
    FIG_OBJS.clear()
    sc = bpy.context.scene
    for name in ("Set", "Figures", "Cameras"):
        c = bpy.data.collections.new(name)
        sc.collection.children.link(c)


def coll(name):
    return bpy.data.collections[name]


def mat(name, rgb):
    if name not in _mats:
        m = bpy.data.materials.new(name)
        m.diffuse_color = (*rgb, 1.0)
        _mats[name] = m
    return _mats[name]


# ---------------------------------------------------------------- bmesh primitives
def _rot_to(vec):
    """Rotation matrix taking +Z onto vec."""
    return Vector((0, 0, 1)).rotation_difference(vec.normalized()).to_matrix().to_4x4()


def bm_box(bm, center, size, rot=None):
    m = Matrix.Translation(Vector(center))
    if rot is not None:
        m = m @ rot.to_4x4()
    m = m @ Matrix.Diagonal((*size, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=m)


def bm_sphere(bm, center, radii, rot=None, seg=(14, 9)):
    m = Matrix.Translation(Vector(center))
    if rot is not None:
        m = m @ rot.to_4x4()
    m = m @ Matrix.Diagonal((*radii, 1.0))
    bmesh.ops.create_uvsphere(bm, u_segments=seg[0], v_segments=seg[1], radius=1.0, matrix=m)


def bm_cyl(bm, p1, p2, r, seg=12, r2=None):
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    if d.length < 1e-6:
        return
    m = Matrix.Translation((p1 + p2) / 2) @ _rot_to(d)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=r if r2 is None else r2, depth=d.length, matrix=m)


def bm_capsule(bm, p1, p2, r):
    bm_cyl(bm, p1, p2, r)
    bm_sphere(bm, p1, (r, r, r), seg=(10, 6))
    bm_sphere(bm, p2, (r, r, r), seg=(10, 6))


def mesh_obj(name, bm, collection, fill, line, mat_tag):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    ob.data.materials.append(mat(f"fill_{mat_tag}", fill))
    ob.data.materials.append(mat(f"line_{mat_tag}", line))
    return ob


# ---------------------------------------------------------------- set helpers
def set_part(name, build, fill=WHITE, line=SET_LINE, tag="set"):
    """build(bm) adds geometry. Returns the object."""
    bm = bmesh.new()
    build(bm)
    ob = mesh_obj(name, bm, coll("Set"), fill, line, tag if fill == WHITE else f"{tag}_{name}")
    SET_OBJS.append(ob)
    return ob


def box(name, x0, x1, y0, y1, z0, z1, fill=WHITE):
    return set_part(name, lambda bm: bm_box(bm, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                                            (x1 - x0, y1 - y0, z1 - z0)), fill=fill)


def wall(name, axis, at, a0, a1, openings=(), h=H, t=WT, base=0.0):
    """Wall along `axis` ('x' or 'y') at the other coordinate `at`, from a0 to a1.
    openings: list of (b0, b1, top, bottom)."""
    segs = []
    cur = a0
    for (b0, b1, top, bot) in sorted(openings):
        segs.append((cur, b0, base, h))
        if bot > base:
            segs.append((b0, b1, base, bot))
        segs.append((b0, b1, top, h))
        cur = b1
    segs.append((cur, a1, base, h))

    def build(bm):
        for (s0, s1, z0, z1) in segs:
            if s1 - s0 < 1e-4 or z1 - z0 < 1e-4:
                continue
            if axis == "x":
                bm_box(bm, ((s0 + s1) / 2, at, (z0 + z1) / 2), (s1 - s0, t, z1 - z0))
            else:
                bm_box(bm, (at, (s0 + s1) / 2, (z0 + z1) / 2), (t, s1 - s0, z1 - z0))
        # skirting and door casings so wall edges read
        for (b0, b1, top, bot) in openings:
            for b in (b0, b1):
                if axis == "x":
                    bm_box(bm, (b, at, top / 2 + bot / 2), (0.07, t + 0.05, top - bot))
                else:
                    bm_box(bm, (at, b, top / 2 + bot / 2), (t + 0.05, 0.07, top - bot))
            if axis == "x":
                bm_box(bm, ((b0 + b1) / 2, at, top), (b1 - b0 + 0.07, t + 0.05, 0.07))
            else:
                bm_box(bm, (at, (b0 + b1) / 2, top), (t + 0.05, b1 - b0 + 0.07, 0.07))
    return set_part(name, build)


def skirting(name, pts, z=0.09):
    """Thin skirting along a closed or open polyline, inset into the room."""
    def build(bm):
        for p, q in zip(pts[:-1], pts[1:]):
            c = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, z / 2)
            sx = abs(q[0] - p[0]) or 0.03
            sy = abs(q[1] - p[1]) or 0.03
            bm_box(bm, c, (sx, sy, z))
    return set_part(name, build)


def chair(name, x, y, yaw_deg, seat=0.46, back=True, w=0.44):
    r = Euler((0, 0, math.radians(yaw_deg))).to_matrix()

    def P(lx, ly, lz):
        return Vector((x, y, 0)) + r @ Vector((lx, ly, lz))

    def build(bm):
        bm_box(bm, P(0, 0, seat - 0.03), (w, w, 0.05), r)
        for sx in (-1, 1):
            for sy in (-1, 1):
                bm_box(bm, P(sx * (w / 2 - 0.03), sy * (w / 2 - 0.03), (seat - 0.05) / 2), (0.04, 0.04, seat - 0.05), r)
        if back:
            bm_box(bm, P(0, -w / 2 + 0.02, seat + 0.25), (w, 0.04, 0.5), r)
    return set_part(name, build)


def table(name, x0, x1, y0, y1, h=0.75, top=0.04, cloth=0.0):
    def build(bm):
        bm_box(bm, ((x0 + x1) / 2, (y0 + y1) / 2, h - top / 2), (x1 - x0 + 2 * cloth, y1 - y0 + 2 * cloth, top))
        if cloth:
            # hanging lace: four skirts
            d = 0.22
            bm_box(bm, ((x0 + x1) / 2, y0 - cloth, h - d / 2), (x1 - x0 + 2 * cloth, 0.01, d))
            bm_box(bm, ((x0 + x1) / 2, y1 + cloth, h - d / 2), (x1 - x0 + 2 * cloth, 0.01, d))
            bm_box(bm, (x0 - cloth, (y0 + y1) / 2, h - d / 2), (0.01, y1 - y0 + 2 * cloth, d))
            bm_box(bm, (x1 + cloth, (y0 + y1) / 2, h - d / 2), (0.01, y1 - y0 + 2 * cloth, d))
        for lx in (x0 + 0.05, x1 - 0.05):
            for ly in (y0 + 0.05, y1 - 0.05):
                bm_box(bm, (lx, ly, (h - top) / 2), (0.05, 0.05, h - top))
    return set_part(name, build)


def curtain(name, axis, at, a0, a1, z0=0.08, z1=2.62, pleats=True, depth=0.12):
    """Closed curtain panel standing just in front of a wall."""
    def build(bm):
        n = max(2, int((a1 - a0) / 0.16))
        for i in range(n):
            s0 = a0 + (a1 - a0) * i / n
            s1 = a0 + (a1 - a0) * (i + 1) / n
            dz = depth if (i % 2 == 0 or not pleats) else depth * 0.55
            if axis == "y":
                bm_box(bm, (at + dz / 2, (s0 + s1) / 2, (z0 + z1) / 2), (dz, s1 - s0, z1 - z0))
            else:
                bm_box(bm, ((s0 + s1) / 2, at - dz / 2, (z0 + z1) / 2), (s1 - s0, dz, z1 - z0))
    return set_part(name, build)


def window_frame(name, axis, at, a0, a1, z0, z1):
    def build(bm):
        t = 0.06
        if axis == "y":
            bm_box(bm, (at + 0.03, (a0 + a1) / 2, z0), (0.06, a1 - a0, t))
            bm_box(bm, (at + 0.03, (a0 + a1) / 2, z1), (0.06, a1 - a0, t))
            for a in (a0, (a0 + a1) / 2, a1):
                bm_box(bm, (at + 0.03, a, (z0 + z1) / 2), (0.06, t, z1 - z0))
        else:
            bm_box(bm, ((a0 + a1) / 2, at - 0.03, z0), (a1 - a0, 0.06, t))
            bm_box(bm, ((a0 + a1) / 2, at - 0.03, z1), (a1 - a0, 0.06, t))
            for a in (a0, (a0 + a1) / 2, a1):
                bm_box(bm, (a, at - 0.03, (z0 + z1) / 2), (t, 0.06, z1 - z0))
    return set_part(name, build)


def pendant(name, x, y, z_ceiling, drop=0.7, r=0.22):
    def build(bm):
        bm_cyl(bm, (x, y, z_ceiling), (x, y, z_ceiling - drop + r * 0.5), 0.008, seg=6)
        bm_sphere(bm, (x, y, z_ceiling - drop + r * 0.3), (r, r, r * 0.55))
    return set_part(name, build)


def door_slab(name, hinge, width, open_deg, closed_dir, h=DOOR_H, t=0.045):
    """Door leaf hinged at `hinge` (x, y). closed_dir: unit (dx, dy) from hinge along the
    closed leaf. open_deg rotates it about the hinge (positive = counter-clockwise)."""
    a = math.radians(open_deg)
    dx, dy = closed_dir
    ux = dx * math.cos(a) - dy * math.sin(a)
    uy = dx * math.sin(a) + dy * math.cos(a)
    yaw = math.atan2(uy, ux)
    r = Euler((0, 0, yaw)).to_matrix()

    def build(bm):
        c = (hinge[0] + ux * width / 2, hinge[1] + uy * width / 2, h / 2)
        bm_box(bm, c, (width, t, h), r)
        # handle
        hc = Vector((hinge[0] + ux * (width - 0.08), hinge[1] + uy * (width - 0.08), 1.0))
        n = r @ Vector((0, 1, 0))
        bm_box(bm, hc + n * 0.05, (0.12, 0.03, 0.025), r)
        bm_box(bm, hc - n * 0.05, (0.12, 0.03, 0.025), r)
    return set_part(name, build)


# ---------------------------------------------------------------- mannequins
def yaw_to(dx, dy):
    """Z rotation (deg) that turns a figure's +Y toward (dx, dy)."""
    return math.degrees(math.atan2(-dx, dy))


def _ik(root, target, a, b, pole):
    d_vec = target - root
    d = min(max(d_vec.length, 1e-4), (a + b) * 0.999)
    u = d_vec.normalized()
    pv = (pole - root)
    v = pv - u * pv.dot(u)
    if v.length < 1e-6:
        v = u.orthogonal()
    v.normalize()
    cos_a = max(-1.0, min(1.0, (a * a + d * d - b * b) / (2 * a * d)))
    sin_a = math.sqrt(max(0.0, 1 - cos_a * cos_a))
    mid = root + u * (a * cos_a) + v * (a * sin_a)
    end = root + u * d
    return mid, end


class Figure:
    """A mannequin. pose keys (all optional):
       pelvis (x,y,z) local; lean, tyaw, troll (deg); pyaw (deg, hips/feet)
       hyaw, hpitch (+down), hroll (deg) relative to the torso, or look=(x,y,z) world
       lhand/rhand: world (x,y,z) target, or ('mouth',) / ('head_off', (dx,dy,dz))
       lfoot/rfoot: local ankle targets
       lelbow/relbow, lknee/rknee: local pole points
       missing: set of parts to leave out ('larm', 'rarm')
       wig: (dx, dy, dz) local head offset of the wig cap, None for no wig
       props: list of (kind, where) carried in the figure's colour
    """

    def __init__(self, key, loc, yaw=0.0, pose=None, rot=None, name=None):
        self.key = key
        self.name = name or key
        self.s = SCALE[key]
        self.pose = dict(pose or {})
        self.loc = Vector(loc)
        if rot is None:
            rot = Euler((0, 0, math.radians(yaw)))
        rm = rot if isinstance(rot, Matrix) else rot.to_matrix()
        self.M = Matrix.Translation(self.loc) @ rm.to_4x4()
        self.Mi = self.M.inverted()
        self._solve()

    # local <-> world
    def W(self, p):
        return self.M @ Vector(p)

    def L(self, p):
        return self.Mi @ Vector(p)

    def _solve(self):
        s, P = self.s, self.pose
        rad = math.radians
        pel = Vector(P.get("pelvis", (0, 0, 0.98 * s)))
        Rt = (Euler((0, 0, rad(P.get("tyaw", 0)))).to_matrix() @
              Euler((rad(-P.get("lean", 0)), 0, 0)).to_matrix() @
              Euler((0, rad(P.get("troll", 0)), 0)).to_matrix())
        Rp = Euler((0, 0, rad(P.get("pyaw", P.get("tyaw", 0) * 0.4)))).to_matrix()
        up, right = Rt @ Vector((0, 0, 1)), Rt @ Vector((1, 0, 0))
        neck = pel + up * 0.52 * s
        if P.get("look") is not None:
            d = Rt.inverted() @ (self.L(P["look"]) - (neck + up * 0.13 * s))
            hyaw = math.degrees(math.atan2(-d.x, d.y))
            hpitch = math.degrees(math.atan2(-d.z, math.hypot(d.x, d.y)))
        else:
            hyaw, hpitch = P.get("hyaw", 0), P.get("hpitch", 0)
        self.hyaw, self.hpitch = hyaw, hpitch
        Rh = (Rt @ Euler((0, 0, rad(hyaw))).to_matrix() @
              Euler((rad(-hpitch), 0, 0)).to_matrix() @
              Euler((0, rad(P.get("hroll", 0)), 0)).to_matrix())
        head = neck + (Rh @ Vector((0, 0, 0.13 * s)))
        J = dict(pelvis=pel, neck=neck, head=head, chest=pel + up * 0.36 * s)
        self.Rt, self.Rh, self.Rp = Rt, Rh, Rp
        ua, fa, th, sh = 0.30 * s, 0.28 * s, 0.45 * s, 0.45 * s
        for side, sg in (("l", -1), ("r", 1)):
            shoulder = neck - up * 0.05 * s + right * sg * 0.19 * s
            J[f"{side}shoulder"] = shoulder
            tgt = P.get(f"{side}hand")
            if tgt is None:
                tl = shoulder + up * -(ua + fa) * 0.97 + right * sg * 0.04 * s + (Rt @ Vector((0, 0.05 * s, 0)))
            elif isinstance(tgt, tuple) and tgt and tgt[0] == "mouth":
                tl = head + Rh @ Vector((0.0, 0.14 * s, -0.06 * s))
            elif isinstance(tgt, tuple) and tgt and tgt[0] == "head_off":
                tl = head + Rh @ Vector(tgt[1])
            else:
                tl = self.L(tgt)
            pole = P.get(f"{side}elbow")
            pole = Vector(pole) if pole is not None else shoulder + right * sg * 0.25 * s - (Rt @ Vector((0, 0.35 * s, 0))) - up * 0.3 * s
            el, wr = _ik(shoulder, tl, ua, fa, pole)
            J[f"{side}elbow"], J[f"{side}wrist"] = el, wr
            hip = pel + Rp @ Vector((sg * 0.095 * s, 0, -0.03 * s))
            J[f"{side}hip"] = hip
            ft = P.get(f"{side}foot")
            ft = Vector(ft) if ft is not None else Vector((hip.x, hip.y, 0.08 * s))
            kp = P.get(f"{side}knee")
            kp = Vector(kp) if kp is not None else hip + (Rp @ Vector((0, 0.6 * s, 0)))
            kn, an = _ik(hip, ft, th, sh, kp)
            J[f"{side}knee"], J[f"{side}ankle"] = kn, an
        self.J = J

    def joint(self, k):
        return self.W(self.J[k])

    def build(self):
        s, J, P = self.s, self.J, self.pose
        missing = set(P.get("missing", ()))
        bm = bmesh.new()
        Rt, Rh, Rp = self.Rt, self.Rh, self.Rp
        up = Rt @ Vector((0, 0, 1))
        # torso
        bm_sphere(bm, J["pelvis"] + up * 0.05 * s, (0.155 * s, 0.11 * s, 0.13 * s), Rt)
        bm_sphere(bm, J["chest"], (0.17 * s, 0.11 * s, 0.19 * s), Rt)
        bm_cyl(bm, J["pelvis"] + up * 0.05 * s, J["chest"], 0.125 * s)
        bm_cyl(bm, J["neck"] - up * 0.03 * s, J["neck"] + (Rh @ Vector((0, 0, 0.06 * s))), 0.05 * s)
        # head with nose and two eye bumps so facing reads
        bm_sphere(bm, J["head"], (0.085 * s, 0.1 * s, 0.115 * s), Rh)
        bm_sphere(bm, J["head"] + Rh @ Vector((0, 0.1 * s, -0.012 * s)), (0.02 * s, 0.03 * s, 0.022 * s), Rh, seg=(8, 6))
        for e in (-1, 1):
            bm_sphere(bm, J["head"] + Rh @ Vector((e * 0.036 * s, 0.085 * s, 0.022 * s)), (0.016 * s,) * 3, seg=(8, 6))
        wig = P.get("wig")
        if wig is not None:
            bm_sphere(bm, J["head"] + Rh @ Vector(wig) + Rh @ Vector((0, -0.012 * s, 0.03 * s)),
                      (0.094 * s, 0.1 * s, 0.1 * s), Rh, seg=(12, 7))
        for side in ("l", "r"):
            if f"{side}arm" not in missing:
                bm_capsule(bm, J[f"{side}shoulder"], J[f"{side}elbow"], 0.046 * s)
                bm_capsule(bm, J[f"{side}elbow"], J[f"{side}wrist"], 0.04 * s)
                d = (J[f"{side}wrist"] - J[f"{side}elbow"]).normalized()
                bm_sphere(bm, J[f"{side}wrist"] + d * 0.05 * s, (0.045 * s, 0.045 * s, 0.045 * s), seg=(10, 6))
            bm_capsule(bm, J[f"{side}hip"], J[f"{side}knee"], 0.07 * s)
            bm_capsule(bm, J[f"{side}knee"], J[f"{side}ankle"], 0.055 * s)
            fy = P.get(f"{side}foot_yaw")
            fr = Euler((0, 0, math.radians(fy))).to_matrix() if fy is not None else Rp
            bm_box(bm, J[f"{side}ankle"] + fr @ Vector((0, 0.07 * s, -0.035 * s)), (0.09 * s, 0.25 * s, 0.07 * s), fr)
        for kind, where in P.get("props", ()):
            _prop(bm, kind, where, self)
        bm.transform(self.M)
        ob = mesh_obj(self.name, bm, coll("Figures"), WHITE, COL[self.key], self.key)
        FIG_OBJS.append(ob)
        self.obj = ob
        return ob


def _prop(bm, kind, where, fig):
    """Props carried by a figure: drawn in its colour. `where` is a local point
    (or a joint name); built before the figure transform."""
    s = fig.s
    if isinstance(where, str):
        c = fig.J[where]
    else:
        c = fig.L(where)
    R = Euler((0, 0, 0)).to_matrix()
    if kind == "plate":
        bm_cyl(bm, c - Vector((0, 0, 0.01)), c + Vector((0, 0, 0.01)), 0.12, seg=16)
    elif kind == "dish":
        bm_box(bm, c, (0.3, 0.22, 0.06))
    elif kind == "brush":
        bm_box(bm, c, (0.05, 0.05, 0.22))
    elif kind == "paper":
        bm_box(bm, c, (0.22 * 1.0, 0.004, 0.30))
    elif kind == "paper_flat":
        bm_box(bm, c, (0.24, 0.30, 0.006))
    elif kind == "book":
        bm_box(bm, c, (0.24, 0.30, 0.02))
    elif kind == "sleeve":
        bm_cyl(bm, c - Vector((0.08, 0, 0)), c + Vector((0.08, 0, 0)), 0.035 * s / 0.64 * 0.64 + 0.02)
    elif kind == "sandal":
        bm_box(bm, c, (0.07, 0.15, 0.03))
    elif kind == "cloth":
        bm_box(bm, c, (0.32, 0.26, 0.05))
    del R


def place_figures(figs):
    for f in figs:
        f.build()


# ---------------------------------------------------------------- loose props (set colour)
def prop_plate(name, x, y, z, r=0.13, food=False):
    def build(bm):
        bm_cyl(bm, (x, y, z), (x, y, z + 0.018), r, seg=18)
        if food:
            bm_sphere(bm, (x, y, z + 0.03), (r * 0.6, r * 0.6, 0.025), seg=(10, 6))
    return set_part(name, build)


def prop_cup(name, x, y, z, on_side=False, yaw=0.0):
    def build(bm):
        if on_side:
            d = Vector((math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), 0)) * 0.05
            c = Vector((x, y, z + 0.037))
            bm_cyl(bm, c - d, c + d, 0.037, seg=14, r2=0.032)
        else:
            bm_cyl(bm, (x, y, z), (x, y, z + 0.1), 0.032, seg=14, r2=0.037)
    return set_part(name, build)


def prop_fork(name, x, y, z):
    return box(name, x - 0.01, x + 0.01, y - 0.09, y + 0.09, z, z + 0.006)


# ---------------------------------------------------------------- cameras
CAMS = []


def camera(name, loc, aim, lens, primary=False, roll=0.0):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36.0
    cd.sensor_fit = "HORIZONTAL"
    cd.clip_start = 0.03
    cd.clip_end = 600.0
    ob = bpy.data.objects.new(name, cd)
    coll("Cameras").objects.link(ob)
    ob.location = Vector(loc)
    d = Vector(aim) - Vector(loc)
    q = d.to_track_quat("-Z", "Y")
    ob.rotation_euler = q.to_euler()
    if roll:
        ob.rotation_euler.rotate_axis("Z", math.radians(roll))
    CAMS.append(ob)
    if primary:
        bpy.context.scene.camera = ob
    return ob


# ---------------------------------------------------------------- look + save
def outline_pass(cam):
    lens = cam.data.lens
    k = 2 * math.atan(18.0 / lens) / 1280.0
    cl = cam.location
    for ob in SET_OBJS + FIG_OBJS:
        bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        # distance to the nearest bound-box point, not the centre: walls are long
        lo = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
        hi = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
        near = Vector((min(max(cl.x, lo.x), hi.x), min(max(cl.y, lo.y), hi.y), min(max(cl.z, lo.z), hi.z)))
        dist = max((near - cl).length, 0.25)
        px = 2.8 if ob in FIG_OBJS else 1.3
        mod = ob.modifiers.new("outline", "SOLIDIFY")
        mod.thickness = dist * k * px
        mod.offset = 1.0
        mod.use_flip_normals = True
        mod.use_rim = False
        mod.material_offset = 1


def look_setup():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.render.resolution_percentage = 100
    sc.render.fps = 24
    sh = sc.display.shading
    sh.light = "FLAT"
    sh.color_type = "MATERIAL"
    sh.show_backface_culling = True
    sh.show_cavity = False
    sh.show_object_outline = False
    sh.show_shadows = False
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("World")
    w.color = (1, 1, 1)
    sc.world = w
    sc.frame_start, sc.frame_end = 1, 1
    # viewport: same flat look, through the active camera, so a viewport render matches
    for scr in bpy.data.screens:
        for area in scr.areas:
            if area.type != "VIEW_3D":
                continue
            for sp in area.spaces:
                if sp.type != "VIEW_3D":
                    continue
                s = sp.shading
                s.type = "SOLID"
                s.light = "FLAT"
                s.color_type = "MATERIAL"
                s.background_type = "VIEWPORT"
                s.background_color = (1, 1, 1)
                s.show_backface_culling = True
                s.show_cavity = False
                s.show_object_outline = False
                s.show_shadows = False
                sp.overlay.show_floor = False
                sp.overlay.show_axis_x = False
                sp.overlay.show_axis_y = False
                sp.overlay.show_axis_z = False
                sp.clip_start = 0.02
                sp.clip_end = 600.0
                if sp.region_3d is not None:
                    sp.region_3d.view_perspective = "CAMERA"


def check(figs):
    """Print where every named figure's head lands in each camera, and whether it is hidden."""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    dg = bpy.context.evaluated_depsgraph_get()
    out = []
    for cam in CAMS:
        line = [cam.name + ":"]
        for f in figs:
            p = f.joint("head")
            v = world_to_camera_view(sc, cam, p)
            inside = 0 <= v.x <= 1 and 0 <= v.y <= 1 and v.z > 0
            tag = "out"
            if inside:
                d = p - cam.location
                hit, loc, _n, _i, ob, _m = sc.ray_cast(dg, cam.location, d.normalized(), distance=d.length - 0.13 * f.s)
                tag = f"hidden by {ob.name}" if hit and ob.name != f.name else "seen"
            line.append(f"{f.name} x={v.x:.2f} y={v.y:.2f} {tag}")
        out.append("  ".join(line))
    return out


def save_blend(tag, figs, out_dir):
    primary = bpy.context.scene.camera
    outline_pass(primary)
    look_setup()
    report = check(figs)
    path = os.path.join(out_dir, f"{tag}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
    return path, report
