"""LOOK - every blocking setup: the state of the set and the figures at the FIRST FRAME
of the run, carried over from the runs before it, plus its camera(s).

Each entry builds one .blend. The first camera is the active one (the image to render);
any further cameras are other angles in the same run that use the same positions."""
import math
import os

import bpy  # noqa: F401  (loads bmesh/mathutils when run as a module)
import bmesh
from mathutils import Euler, Matrix, Vector

import look_set as L
from apartment import (ARMCHAIR, BED, CAR, SEAT_ADAM, SEAT_CHILD, SEAT_WIFE, SEAT_Z_FRONT,
                       SEAT_Z_REAR, SOFA_E, SOFA_MID, SOFA_SEAT_Z, SOFA_W, SOFA_Y, STAND_CHILD,
                       STAND_WIFE, WHEEL_C, build_apartment, build_car)
from look_set import Figure, yaw_to

SH = {}

# Lenses that give the seedance-clean field-of-view table exactly (horizontal FOV).
F84, F63, F47, F29, F18, F12 = 19.99, 29.37, 41.40, 69.43, 113.65, 171.27


def shot(tag):
    def deco(fn):
        SH[tag] = fn
        return fn
    return deco


# ------------------------------------------------------------------ pose presets
def stand(s, **kw):
    d = dict(pelvis=(0, 0, 0.98 * s))
    d.update(kw)
    return d


def walk(s, **kw):
    d = dict(pelvis=(0, 0, 0.95 * s), lfoot=(-0.1 * s, 0.24 * s, 0.08 * s), rfoot=(0.1 * s, -0.22 * s, 0.13 * s),
             lean=4, lhand=None, rhand=None)
    d.update(kw)
    return d


def sit(s, seat, **kw):
    hz = seat + 0.07 * s
    fy = 0.45 * s if s > 0.8 else 0.3
    fz = 0.08 * s if s > 0.8 else max(0.08, hz - 0.5 * s)
    d = dict(pelvis=(0, -0.04, hz), lfoot=(-0.11 * s, fy, fz), rfoot=(0.11 * s, fy, fz),
             lknee=(-0.11 * s, 1.0, hz + 0.6), rknee=(0.11 * s, 1.0, hz + 0.6))
    d.update(kw)
    return d


def kneel_heels(s, **kw):
    d = dict(pelvis=(0, -0.05, 0.36 * s), lfoot=(-0.12, -0.3, 0.06), rfoot=(0.12, -0.3, 0.06),
             lknee=(-0.12, 1.0, 0.0), rknee=(0.12, 1.0, 0.0), lean=35)
    d.update(kw)
    return d


def kneel_up(s, **kw):
    d = dict(pelvis=(0, -0.02, 0.62 * s), lfoot=(-0.12, -0.42, 0.06), rfoot=(0.12, -0.42, 0.06),
             lknee=(-0.12, 1.0, -0.3), rknee=(0.12, 1.0, -0.3), lean=10)
    d.update(kw)
    return d


def crouch(s, **kw):
    d = dict(pelvis=(0, -0.08, 0.38 * s), lfoot=(-0.16, 0.12, 0.08), rfoot=(0.16, 0.12, 0.08),
             lknee=(-0.25, 1.0, 1.0), rknee=(0.25, 1.0, 1.0), lean=25)
    d.update(kw)
    return d


def floor_sit(s, **kw):
    d = dict(pelvis=(0, 0, 0.13), lfoot=(-0.14, 0.5, 0.08), rfoot=(0.14, 0.5, 0.08),
             lknee=(-0.2, 0.4, 1.5), rknee=(0.2, 0.4, 1.5), lean=-4)
    d.update(kw)
    return d


def hands_lap(fig_loc, yaw, s, seat):
    r = Euler((0, 0, math.radians(yaw))).to_matrix()
    c = Vector((fig_loc[0], fig_loc[1], 0.0))
    return (tuple(c + r @ Vector((-0.1 * s, 0.25 * s, seat + 0.15 * s))),
            tuple(c + r @ Vector((0.1 * s, 0.25 * s, seat + 0.15 * s))))


WIG = (0, 0, 0)


def mannequin_seated(key, loc, yaw, seat, **kw):
    s = L.SCALE[key]
    lh, rh = hands_lap(loc, yaw, s, seat)
    p = sit(s, seat, lhand=lh, rhand=rh, wig=WIG)
    p.update(kw)
    return Figure(key, (loc[0], loc[1], 0), yaw, p)


def mannequin_standing(key, loc, yaw, base=0.0, **kw):
    s = L.SCALE[key]
    p = stand(s, wig=WIG)
    p.update(kw)
    return Figure(key, (loc[0], loc[1], base), yaw, p)


def lying_child(wig=WIG, blanket_to=None):
    """Child mannequin on its back in Nour's bed, head on the pillow (west)."""
    s = L.SCALE["doll-daughter"]
    # on its back, head west on the pillow, the head end raised a little by the pillow
    rot = Euler((0, math.radians(6), 0)).to_matrix() @ Euler((math.radians(90), 0, math.radians(-90))).to_matrix()
    y = (BED["y0"] + BED["y1"]) / 2
    f = Figure("doll-daughter", (BED["x0"] + 0.27 + 1.63 * s, y, 0.53), pose=stand(s, wig=wig), rot=rot)
    return f


def blanket(x0):
    L.box("blanket", x0, BED["x1"] - 0.02, BED["y0"] + 0.03, BED["y1"] - 0.03, 0.44, 0.6)


def rabbit(at=(9.6, 1.86)):
    x, y = at
    L.set_part("rabbit", lambda bm: (L.bm_sphere(bm, (x, y, 0.56), (0.07, 0.06, 0.08)),
                                      L.bm_sphere(bm, (x - 0.08, y, 0.62), (0.05, 0.05, 0.05))))


def loose_arm(name, p1, p2, key="doll-wife"):
    """The adult mannequin's detached arm: its own object in the mannequin's colour."""
    s = L.SCALE[key]
    bm = bmesh.new()
    p1, p2 = Vector(p1), Vector(p2)
    mid = p1 + (p2 - p1) * 0.52
    L.bm_capsule(bm, p1, mid, 0.046 * s)
    L.bm_capsule(bm, mid, p2, 0.04 * s)
    L.bm_sphere(bm, p2 + (p2 - p1).normalized() * 0.05, (0.045 * s,) * 3)
    ob = L.mesh_obj(name, bm, L.coll("Figures"), L.WHITE, L.COL[key], key)
    L.FIG_OBJS.append(ob)
    return ob


# ====================================================================== DINING
def dining_figs(adam_pose=None, child_kw=None):
    wife = mannequin_seated("doll-wife", SEAT_WIFE, 0, 0.46)
    child = mannequin_seated("doll-daughter", SEAT_CHILD, 180, 0.46, **(child_kw or {}))
    p = sit(1.0, 0.46, lhand=(1.72, 7.12, 0.775), rhand=(1.72, 6.68, 0.775), look=child.joint("head"))
    if adam_pose:
        p.update(adam_pose)
    adam = Figure("adam", (SEAT_ADAM[0], SEAT_ADAM[1], 0), -90, p)
    return [adam, wife, child]


FRONTAL = dict(loc=(4.95, 6.9, 1.18), aim=(1.9, 6.9, 1.0))


@shot("B01a_dining-frontal_G05")
def b01a():
    build_apartment(dict(table="breakfast"))
    figs = dining_figs()
    L.camera("CAM_G05_wide-frontal", FRONTAL["loc"], FRONTAL["aim"], F63, primary=True)
    return figs


@shot("B01b_dining-frontal_G24")
def b01b():
    build_apartment(dict(table="dinner"))
    figs = dining_figs(
        adam_pose=dict(lean=28, lhand=(1.86, 7.05, 0.79), rhand=(1.86, 6.75, 0.79),
                       lelbow=(-0.3, 0.3, -0.6), relbow=(0.3, 0.3, -0.6)),
        child_kw=dict(lhand=(2.2, 7.6, 0.79)))
    figs[0] = Figure("adam", (SEAT_ADAM[0], SEAT_ADAM[1], 0), -90,
                     dict(sit(1.0, 0.46), lean=28, lhand=(1.86, 7.05, 0.79), rhand=(1.86, 6.75, 0.79),
                          look=figs[2].joint("head")))
    L.camera("CAM_G24_wide-frontal", FRONTAL["loc"], FRONTAL["aim"], F63, primary=True)
    L.camera("CAM_G24_s2_insert-cup", (2.95, 7.2, 1.05), (2.22, 7.45, 0.8), F47)
    return figs


@shot("B01c_dining-frontal_G26")
def b01c():
    build_apartment(dict(table="knocked"))
    wife = mannequin_seated("doll-wife", SEAT_WIFE, 0, 0.46)
    child = mannequin_seated("doll-daughter", SEAT_CHILD, 180, 0.46)
    adam = Figure("adam", (SEAT_ADAM[0], SEAT_ADAM[1], 0), -90,
                  dict(sit(1.0, 0.46), lean=8, lhand=(1.5, 7.1, 0.76), rhand=(1.5, 6.7, 0.76), hpitch=-3))
    L.camera("CAM_G26_CU-adam", (3.1, 6.9, 1.15), adam.joint("head") + Vector((0, 0, -0.04)), F29, primary=True)
    return [adam, wife, child]


@shot("B02_dining-kitchen-door_G03")
def b02():
    build_apartment(dict(table="set"))
    wife = mannequin_seated("doll-wife", SEAT_WIFE, 0, 0.46)
    child = mannequin_seated("doll-daughter", SEAT_CHILD, 180, 0.46)
    # first frame: Adam is not in yet (he walks in from the right at 0.8 s); his chair is empty
    L.camera("CAM_G03_wide-through-kitchen-door", (6.0, 6.9, 1.42), (2.0, 6.9, 0.98), F63, primary=True)
    return [wife, child]


@shot("B03_dining-side_G25")
def b03():
    build_apartment(dict(table="spilled"))
    figs = dining_figs(adam_pose=dict(look=None, hpitch=38, lean=12, lhand=(1.66, 7.1, 0.77), rhand=(1.66, 6.7, 0.77)))
    figs[0] = Figure("adam", (SEAT_ADAM[0], SEAT_ADAM[1], 0), -90,
                     dict(sit(1.0, 0.46), hpitch=38, lean=12, lhand=(1.66, 7.1, 0.77), rhand=(1.66, 6.7, 0.77)))
    L.camera("CAM_G25_wide-side", (4.25, 5.15, 1.3), (1.95, 7.0, 0.95), F63, primary=True)
    return figs


@shot("B04_dining-chair-sandal_G08")
def b04():
    build_apartment(dict(table="breakfast", child_chair_turned=True))
    wife = mannequin_seated("doll-wife", SEAT_WIFE, 0, 0.46)
    child = mannequin_seated("doll-daughter", (SEAT_CHILD[0], SEAT_CHILD[1] + 0.12), 0, 0.46)
    foot = child.joint("rankle")
    adam = Figure("adam", (2.0, 8.66, 0), 180,
                  kneel_heels(1.0, lhand=tuple(foot + Vector((0.03, 0.0, -0.01))),
                              rhand=tuple(foot + Vector((-0.04, 0.05, 0.02))),
                              look=foot, props=[("sandal", tuple(foot + Vector((-0.04, 0.04, -0.02))))]))
    L.camera("CAM_G08_CU-hands-low", (2.8, 8.2, 0.36), tuple(foot + Vector((0, 0, 0.05))), F47, primary=True)
    L.camera("CAM_G08_s2_CU-adam", (2.45, 8.02, 0.62), adam.joint("head"), F29)
    return [adam, wife, child]


# ====================================================================== LIVING ROOM
LIVING = dict(loc=(4.2, 7.0, 1.5), aim=(2.75, 1.3, 0.95))


def wife_in_armchair():
    yaw = yaw_to(SOFA_MID - ARMCHAIR[0], SOFA_Y - ARMCHAIR[1])
    r = Euler((0, 0, math.radians(yaw))).to_matrix()
    loc = Vector((ARMCHAIR[0], ARMCHAIR[1], 0)) + r @ Vector((0, 0.06, 0))
    return mannequin_seated("doll-wife", tuple(loc), yaw, 0.42)


def child_on_sofa(x=SOFA_MID, **kw):
    return mannequin_seated("doll-daughter", (x, SOFA_Y), 0, SOFA_SEAT_Z, **kw)


@shot("B05a_living-wide_G10")
def b05a():
    build_apartment(dict(table="breakfast"))
    wife = wife_in_armchair()
    a_loc = Vector((4.6, 2.05, 0))
    yaw = yaw_to(SOFA_MID - a_loc.x, SOFA_Y + 0.6 - a_loc.y)
    ra = Euler((0, 0, math.radians(yaw))).to_matrix()
    # child mannequin held rigid across his chest: head to his left, legs out to his right
    zc = (ra @ Vector((-1, 0, 0.5))).normalized()
    yc = (ra @ Vector((0, 0.35, 1))) - zc * (ra @ Vector((0, 0.35, 1))).dot(zc)
    yc.normalize()
    xc = yc.cross(zc)
    rc = Matrix((xc, yc, zc)).transposed()
    s = L.SCALE["doll-daughter"]
    pelvis_target = a_loc + ra @ Vector((0.1, 0.34, 1.05))
    c_loc = pelvis_target - rc @ Vector((0, 0, 0.98 * s))
    child = Figure("doll-daughter", tuple(c_loc), pose=stand(s, wig=WIG), rot=rc)
    adam = Figure("adam", tuple(a_loc), yaw,
                  walk(1.0, rhand=tuple(child.W((0, -0.05, 0.3))), lhand=tuple(child.W((0, -0.1, 1.0))),
                       look=child.joint("head")))
    L.camera("CAM_G10_wide", LIVING["loc"], LIVING["aim"], F63, primary=True)
    return [adam, wife, child]


@shot("B05b_living-wide_G16")
def b05b():
    build_apartment(dict(table="breakfast"))
    child = child_on_sofa()
    wife = Figure("doll-wife", (3.52, 2.75, 0), 90,
                  stand(0.97, wig=WIG, lhand=(3.05, 2.6, 1.3), rhand=(3.37, 3.18, 1.28),
                        lelbow=(-0.3, 0.2, -0.1)))
    adam = Figure("adam", (3.21, 2.75, 0), -90,
                  stand(1.0, rhand=(3.62, 2.62, 1.05), lhand=(3.37, 3.2, 1.3), hyaw=12, hroll=-8, hpitch=6))
    L.camera("CAM_G16_wide", LIVING["loc"], LIVING["aim"], F63, primary=True)
    return [adam, wife, child]


@shot("B05c_living-wide_G18")
def b05c():
    build_apartment(dict(table="breakfast"))
    child = child_on_sofa()
    wife = Figure("doll-wife", (3.21, 2.75, 0), -90, stand(0.97, wig=WIG, missing=("larm",)))
    adam = Figure("adam", (3.52, 2.75, 0), 90,
                  stand(1.0, lhand=(3.25, 2.58, 1.0), rhand=(3.25, 2.93, 1.0), look=(3.25, 3.15, 0.0), lean=8))
    loose_arm("doll-wife_loose-arm", (3.1, 3.12, 0.05), (3.53, 3.2, 0.05))
    L.camera("CAM_G18_wide", LIVING["loc"], LIVING["aim"], F63, primary=True)
    return [adam, wife, child]


@shot("B05d_living-sofa-edge_G18-s2")
def b05d():
    build_apartment(dict(table="breakfast"))
    child = child_on_sofa()
    wife = mannequin_seated("doll-wife", (SOFA_W, SOFA_Y), 0, SOFA_SEAT_Z, missing=("larm",))
    sh = wife.joint("lshoulder")
    a_loc = (2.98, 1.78)
    adam = Figure("adam", (a_loc[0], a_loc[1], 0), yaw_to(sh.x - a_loc[0], sh.y - a_loc[1]),
                  kneel_up(1.0, lhand=tuple(sh + Vector((-0.06, 0.12, -0.05))),
                           rhand=tuple(sh + Vector((0.02, 0.22, -0.18))), look=sh))
    loose_arm("doll-wife_loose-arm", tuple(sh + Vector((-0.02, 0.03, -0.01))), tuple(sh + Vector((-0.05, 0.42, -0.25))))
    L.camera("CAM_G18_s2_MCU", (3.15, 3.25, 1.15), (3.1, 1.4, 1.02), F47, primary=True)
    return [adam, wife, child]


@shot("B05e_living-wide_G43")
def b05e():
    build_apartment(dict(table="dinner", living_curtains="closed"))
    wife = mannequin_seated("doll-wife", (4.06, SOFA_Y), 0, SOFA_SEAT_Z)
    child = mannequin_seated("doll-daughter", (3.54, SOFA_Y), 0, SOFA_SEAT_Z)
    adam = Figure("adam", (0.45, 2.2, 0), 90,
                  stand(1.0, lhand=(0.2, 1.72, 1.5), rhand=(0.2, 2.68, 1.5)))
    L.camera("CAM_G43_MS", LIVING["loc"], (2.35, 1.4, 0.95), F63, primary=True)
    return [adam, wife, child]


@shot("B05f_living-wide_G44")
def b05f():
    build_apartment(dict(table="dinner", living_curtains="open"))
    wife = mannequin_seated("doll-wife", (4.06, SOFA_Y), 0, SOFA_SEAT_Z)
    child = mannequin_seated("doll-daughter", (3.54, SOFA_Y), 0, SOFA_SEAT_Z)
    a = (4.55, 1.88)
    adam = Figure("adam", (a[0], a[1], 0), yaw_to(4.06 - a[0], SOFA_Y - a[1]), stand(1.0, look=wife.joint("head")))
    L.camera("CAM_G44_wide", LIVING["loc"], LIVING["aim"], F63, primary=True)
    return [adam, wife, child]


# ====================================================================== SOFA TWO-SHOT
@shot("B06a_sofa-two-shot_G11")
def b06a():
    build_apartment(dict(table="breakfast"))
    wife = wife_in_armchair()
    child = child_on_sofa()
    hd = child.joint("head")
    adam = Figure("adam", (SOFA_W, SOFA_Y, 0), 0,
                  sit(1.0, SOFA_SEAT_Z, tyaw=-62, pyaw=-25, lean=14,
                      rhand=tuple(hd + Vector((-0.07, -0.05, 0.07))), lhand=tuple(hd + Vector((-0.06, -0.07, -0.08))),
                      look=hd, props=[("brush", tuple(hd + Vector((-0.07, -0.05, 0.12))))]))
    L.camera("CAM_G11_MCU-two-shot", (3.62, 3.15, 1.05), (3.56, SOFA_Y, 0.98), F29, primary=True)
    L.camera("CAM_G11_s3_CU-adam", (3.95, 2.55, 1.12), adam.joint("head"), F29)
    return [adam, wife, child]


@shot("B06b_sofa-two-shot_G22")
def b06b():
    build_apartment(dict(table="breakfast"))
    child = child_on_sofa()
    wife = mannequin_seated("doll-wife", (SOFA_W, SOFA_Y), 0, SOFA_SEAT_Z)
    hd = child.joint("head")
    a = (4.26, 1.52)
    adam = Figure("adam", (a[0], a[1], 0), yaw_to(hd.x - a[0], hd.y - a[1]),
                  crouch(1.0, pelvis=(0, -0.08, 0.3), rhand=("mouth",), look=hd))
    L.camera("CAM_G22_CU-two-shot", (3.98, 2.9, 1.0), (4.02, 1.25, 0.93), F29, primary=True)
    L.camera("CAM_G22_s2_CU-adam", (4.55, 3.1, 1.0), adam.joint("head"), F29)
    return [adam, wife, child]


# ====================================================================== KITCHEN
@shot("B07a_kitchen_G14")
def b07a():
    build_apartment(dict(table="breakfast"))
    wife = mannequin_standing("doll-wife", (5.02, 7.08), -90)
    adam = Figure("adam", (7.2, 7.62, 0), -62,
                  stand(1.0, rhand=(7.78, 7.56, 1.06), look=wife.joint("head"), tyaw=18))
    L.camera("CAM_G14_s2_MS", (4.3, 6.58, 1.55), (7.3, 7.5, 1.25), F47, primary=True)
    L.camera("CAM_G14_s3_CU-adam", (5.85, 7.15, 1.6), adam.joint("head"), F29)
    return [adam, wife]


@shot("B07b_kitchen_G20")
def b07b():
    build_apartment(dict(table="breakfast"))
    adam = Figure("adam", (7.2, 7.3, 0), -35, stand(1.0, look=(5.0, 6.9, 1.6)))
    L.camera("CAM_G20_CU-adam", (7.1, 6.14, 1.63), adam.joint("head"), F29, primary=True)
    return [adam]


# ====================================================================== SEWING CORNER
@shot("B08_sewing-corner_G45")
def b08():
    build_apartment(dict(table="dinner", living_curtains="open"))
    face = (2.9, 3.3)
    wife = mannequin_standing("doll-wife", STAND_WIFE, yaw_to(face[0] - STAND_WIFE[0], face[1] - STAND_WIFE[1]),
                              base=0.025, wig=None)
    child = mannequin_standing("doll-daughter", STAND_CHILD, yaw_to(face[0] - STAND_CHILD[0], face[1] - STAND_CHILD[1]),
                               base=0.025, wig=None)
    sh = child.joint("rshoulder")
    a = (0.98, 1.22)
    adam = Figure("adam", (a[0], a[1], 0), yaw_to(sh.x - a[0], sh.y - a[1]),
                  stand(1.0, lhand=tuple(sh + Vector((0.02, 0.06, 0.04))), rhand=tuple(sh + Vector((0.08, -0.06, 0.02))),
                        look=sh, lean=10, props=[("sleeve", tuple(sh + Vector((0.04, 0.0, 0.03))))]))
    L.camera("CAM_G45_wide", (2.95, 3.35, 1.35), (1.3, 0.5, 1.0), F63, primary=True)
    return [adam, wife, child]


# ====================================================================== HALLWAY
HALL = dict(loc=(4.85, 5.22, 1.55), aim=(12.0, 5.3, 1.3))


@shot("B09a_hallway_G21")
def b09a():
    build_apartment(dict(table="breakfast", bag=True))
    adam = Figure("adam", (8.6, 5.3, 0), -90, stand(1.0))
    L.camera("CAM_G21_wide", HALL["loc"], HALL["aim"], F63, primary=True)
    return [adam]


@shot("B09b_hallway_G40")
def b09b():
    build_apartment(dict(table="dinner", bag=True))
    adam = Figure("adam", (6.25, 5.28, 0), -90, walk(1.0))
    L.camera("CAM_G40_wide", HALL["loc"], HALL["aim"], F63, primary=True)
    return [adam]


@shot("B09c_hallway_G47")
def b09c():
    build_apartment(dict(table="drawing", bag=False, living_curtains="open"))
    adam = Figure("adam", (9.8, 5.3, 0), -90, walk(1.0))
    L.camera("CAM_G47_wide", HALL["loc"], HALL["aim"], F63, primary=True)
    return [adam]


@shot("B09d_hallway-from-dining_G49")
def b09d():
    build_apartment(dict(table="drawing", bag=False, living_curtains="open", front_door=90, landing_dish=True,
                         wife_chair_out=True))
    wife = mannequin_standing("doll-wife", STAND_WIFE, yaw_to(2.9 - STAND_WIFE[0], 3.3 - STAND_WIFE[1]), base=0.025, wig=None)
    child = mannequin_standing("doll-daughter", STAND_CHILD, yaw_to(2.9 - STAND_CHILD[0], 3.3 - STAND_CHILD[1]), base=0.025, wig=None)
    adam = Figure("adam", (11.72, 5.3, 0), -90, stand(1.0, hpitch=32))
    mona = Figure("mona", (12.38, 5.3, 0), 90,
                  walk(0.95, lhand=(12.0, 5.12, 1.25), rhand=(12.0, 5.48, 1.25)))
    L.camera("CAM_G49_wide", (0.4, 5.45, 1.15), (12.0, 5.3, 1.25), F63, primary=True)
    return [adam, mona, wife, child]


# ====================================================================== NOUR'S ROOM
NOUR_WIDE = dict(loc=(11.85, 2.45, 1.45), aim=(9.3, 3.55, 0.95), lens=F63)


@shot("B10a_nour-room_G29")
def b10a():
    build_apartment(dict(table="dinner"))
    child = lying_child()
    blanket(9.95)
    rabbit((9.28, 1.86))
    chest = child.joint("chest")
    adam = Figure("adam", (10.22, 2.84, 0), 0,
                  sit(1.0, 0.44, tyaw=72, pyaw=20, lean=30,
                      lhand=tuple(chest + Vector((0.05, -0.12, 0.1))), rhand=tuple(chest + Vector((0.05, 0.14, 0.1))),
                      look=child.joint("head")))
    L.camera("CAM_G29_MS-bed-foot", (11.75, 3.45, 1.4), (10.0, 2.5, 0.75), F47, primary=True)
    return [adam, child]


@shot("B10b_nour-room-wide_G29-s3")
def b10b():
    build_apartment(dict(table="dinner"))
    child = lying_child()
    blanket(9.6)
    rabbit()
    a = (10.4, 4.38)
    adam = Figure("adam", (a[0], a[1], 0), yaw_to(9.8 - a[0], 2.2 - a[1]),
                  stand(1.0, lhand=(10.9, 4.52, 1.2), look=child.joint("head")))
    L.camera("CAM_G29_s3_wide", NOUR_WIDE["loc"], NOUR_WIDE["aim"], NOUR_WIDE["lens"], primary=True)
    return [adam, child]


@shot("B10c_nour-room-doorway_G30")
def b10c():
    build_apartment(dict(table="dinner"))
    child = lying_child()
    blanket(9.6)
    rabbit()
    adam = Figure("adam", (10.4, 4.42, 0), 0, walk(1.0, rhand=(10.8, 4.52, 1.25)))
    L.camera("CAM_G30_CU-profile", (11.9, 4.3, 1.62), adam.joint("head"), F29, primary=True)
    L.camera("CAM_G30_s2_CU-frontal", (10.4, 5.85, 1.62), adam.joint("head"), F29)
    return [adam, child]


@shot("B10d_nour-room-floor_G38")
def b10d():
    build_apartment(dict(table="dinner"))
    child = lying_child(wig=(0.065, 0.0, -0.03))
    blanket(9.6)
    rabbit()
    L.camera("CAM_G38_low-floor", (9.9, 3.4, 0.42), child.joint("head") + Vector((0.15, 0, 0)), F63, primary=True)
    return [child]


@shot("B10e_nour-room-floor_G39")
def b10e():
    build_apartment(dict(table="dinner"))
    child = lying_child(wig=(0.065, 0.0, -0.03))
    blanket(9.6)
    rabbit()
    adam = Figure("adam", (10.1, 2.87, 0), 0, floor_sit(1.0, hpitch=10))
    L.camera("CAM_G39_MS", (10.2, 4.45, 0.9), (10.1, 2.9, 0.65), F47, primary=True)
    L.camera("CAM_G39_s2_wide", NOUR_WIDE["loc"], NOUR_WIDE["aim"], NOUR_WIDE["lens"])
    return [adam, child]


# ====================================================================== CAR
def car_figs(off, nour="drawing", layla_hand="gear", adam_rhand="gear"):
    gear = off + Vector((0, 0.45, 0.65))
    wl = off + WHEEL_C + Vector((-0.17, -0.05, 0.03))
    wr = off + WHEEL_C + Vector((0.17, -0.05, 0.03))
    dl = off + Vector((CAR["driver"][0], CAR["driver"][1], 0))
    pl = off + Vector((CAR["passenger"][0], CAR["passenger"][1], 0))
    rl = off + Vector((CAR["rear_right"][0], CAR["rear_right"][1], 0))

    def car_sit(s, seat, **kw):
        p = sit(s, seat, **kw)
        if s > 0.8:
            p.update(lfoot=(-0.11 * s, 0.62, 0.22), rfoot=(0.11 * s, 0.62, 0.22))
        return p
    adam = Figure("adam", tuple(dl), 0,
                  car_sit(1.0, SEAT_Z_FRONT, lean=-8, lhand=tuple(wl),
                          rhand=tuple(gear if adam_rhand == "gear" else wr)))
    lh, rh = hands_lap(pl, 0, 0.95, SEAT_Z_FRONT)
    layla = Figure("layla", tuple(pl), 0,
                   car_sit(0.95, SEAT_Z_FRONT, lean=-8, lhand=tuple(gear + Vector((0, 0, 0.04))) if layla_hand == "gear" else lh,
                           rhand=rh))
    s = L.SCALE["nour"]
    if nour == "drawing":
        book = rl + Vector((0, 0.24, SEAT_Z_REAR + 0.22))
        nf = Figure("nour", tuple(rl), 0,
                    sit(s, SEAT_Z_REAR, lhand=tuple(book + Vector((-0.07, -0.02, 0.03))),
                        rhand=tuple(book + Vector((0.05, 0.05, 0.03))), hpitch=38, lean=12,
                        props=[("book", tuple(book))]))
    else:
        paper = rl + Vector((-0.08, 0.36, 0.93))
        nf = Figure("nour", tuple(rl), 0,
                    sit(s, SEAT_Z_REAR, lean=18, lhand=tuple(paper + Vector((-0.11, -0.01, -0.04))),
                        rhand=tuple(paper + Vector((0.11, -0.01, -0.04))), hpitch=-5,
                        props=[("paper", tuple(paper))]))
    return adam, layla, nf


@shot("B11_car-from-back-seat_G32")
def b11():
    off = build_car()
    adam, layla, nour = car_figs(off)
    L.camera("CAM_G32_from-back-seat", tuple(off + Vector((-0.02, -0.72, 1.02))), tuple(off + Vector((0, 8, 0.95))), F84, primary=True)
    return [adam, layla, nour]


@shot("B12a_car-back-seat_G09")
def b12a():
    off = build_car()
    adam, layla, nour = car_figs(off, layla_hand="lap", adam_rhand="wheel")
    L.camera("CAM_G09_s2_CU-legs", tuple(off + Vector((-0.08, -0.6, 0.55))), tuple(nour.joint("rknee") + Vector((0, 0.02, -0.12))), F63, primary=True)
    L.camera("CAM_G12_CU-nour", tuple(off + Vector((-0.02, -0.68, 0.93))), nour.joint("head"), F63)
    L.camera("CAM_G32_s2_CU-nour", tuple(off + Vector((-0.08, -0.42, 1.0))), nour.joint("head") + Vector((0, 0.08, -0.06)), F47)
    return [adam, layla, nour]


@shot("B12b_car-back-seat-paper_G33")
def b12b():
    off = build_car()
    adam, layla, nour = car_figs(off, nour="paper", layla_hand="lap", adam_rhand="wheel")
    L.camera("CAM_G33_CU-nour-from-front", tuple(off + Vector((-0.15, 0.1, 1.12))), nour.joint("head") + Vector((0, 0.05, -0.04)), F47, primary=True)
    L.camera("CAM_G34_s2_POV-adam", tuple(off + Vector((-0.15, 0.0, 1.12))), nour.joint("head") + Vector((-0.05, 0.1, 0.0)), F63)
    return [adam, layla, nour]


@shot("B13_car-driver-side_G15")
def b13():
    off = build_car()
    adam, layla, nour = car_figs(off, layla_hand="lap", adam_rhand="wheel")
    L.camera("CAM_G15_CU-layla-from-driver", tuple(off + Vector((-0.12, 0.2, 1.08))), layla.joint("head"), F63, primary=True)
    L.camera("CAM_G33_s2_MCU-adam-from-passenger", tuple(off + Vector((0.22, 0.24, 1.06))), adam.joint("head") + Vector((0, 0, -0.08)), F63)
    L.camera("CAM_G34_CU-adam-from-behind", tuple(off + Vector((-0.05, -0.55, 1.12))), adam.joint("head"), F47)
    return [adam, layla, nour]


# ====================================================================== LANDING
@shot("B14a_landing_G23")
def b14a():
    build_apartment(dict(table="dinner"))
    mona = Figure("mona", (12.42, 5.3, 0), 90,
                  stand(0.95, lhand=(12.15, 5.18, 0.95), rhand=(12.15, 5.42, 0.95), props=[("dish", (12.12, 5.3, 0.95))]))
    L.camera("CAM_G23_floor-level", (12.95, 7.0, 0.28), (12.15, 5.3, 0.3), F63, primary=True)
    return [mona]


@shot("B14b_landing_G48")
def b14b():
    build_apartment(dict(table="drawing", bag=False, living_curtains="open", front_door=90, landing_dish=True))
    mona = Figure("mona", (12.58, 5.3, 0), 90,
                  stand(0.95, lhand=(12.3, 5.18, 0.98), rhand=(12.3, 5.42, 0.98), props=[("dish", (12.27, 5.3, 0.98))]))
    adam = Figure("adam", (11.86, 5.3, 0), -90, stand(1.0, look=mona.joint("head")))
    L.camera("CAM_G48_wide-two-shot", (14.25, 6.95, 1.55), (12.25, 5.25, 1.3), F47, primary=True)
    L.camera("CAM_G48_s2_CU-adam", (13.45, 5.8, 1.62), adam.joint("head"), F29)
    return [mona, adam]


# ------------------------------------------------------------------ build one
def build(tag, out_dir=None):
    out_dir = out_dir or os.path.dirname(os.path.abspath(__file__))
    L.reset()
    L.CAMS.clear()
    figs = SH[tag]()
    for f in figs:
        if not hasattr(f, "obj"):
            f.build()
    if tag.startswith("B10"):
        print("    child head z", round(figs[-1].joint("head").z, 3))
    return L.save_blend(tag + "_v1", figs, out_dir)
