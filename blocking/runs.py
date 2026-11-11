"""LOOK blocking v2 - every run as an animated .blend: the figures act on the prompt's
timecodes and the camera cuts at the stated points (timeline markers bound to cameras).
Positions and set states carry over from run to run (see README)."""
import math
import os

import bpy  # noqa: F401
from mathutils import Euler, Matrix, Vector

import look_set as L
import rig as R
from apartment import (ARMCHAIR, BED, CAR, SEAT_ADAM, SEAT_CHILD, SEAT_WIFE, SEAT_Z_FRONT,
                       SEAT_Z_REAR, SOFA_MID, SOFA_SEAT_Z, SOFA_W, SOFA_Y, STAND_CHILD, STAND_WIFE,
                       WHEEL_C, build_apartment, build_car)
from look_set import yaw_to
from rig import F12, F18, F29, F47, F63, F84, Cam, K, Prop, Track, follow, phases, static, vis

RUNS = {}


def run(tag, dur):
    def deco(fn):
        RUNS[tag] = (fn, dur)
        return fn
    return deco


# ------------------------------------------------------------------ poses
def stand(s=1.0, **kw):
    d = dict(pelvis=(0, 0, 0.98 * s))
    d.update(kw)
    return d


def walking(s=1.0, period=1.0, **kw):
    def lf(t, S, sg=-1, ph0=0.0):
        ph = 2 * math.pi * t / period + ph0
        return (sg * 0.1 * s, 0.22 * s * math.sin(ph), 0.08 * s + 0.07 * s * max(0.0, math.cos(ph)))
    d = dict(pelvis=(0, 0, 0.95 * s), lean=4,
             lfoot=lambda t, S: lf(t, S, -1, 0.0), rfoot=lambda t, S: lf(t, S, 1, math.pi))
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


def car_sit(s, seat, **kw):
    d = sit(s, seat, **kw)
    if s > 0.8:
        d.update(lfoot=(-0.11 * s, 0.62, 0.22), rfoot=(0.11 * s, 0.62, 0.22))
    return d


def kneel_heels(**kw):
    d = dict(pelvis=(0, -0.05, 0.36), lfoot=(-0.12, -0.3, 0.06), rfoot=(0.12, -0.3, 0.06),
             lknee=(-0.12, 1.0, 0.0), rknee=(0.12, 1.0, 0.0), lean=35)
    d.update(kw)
    return d


def kneel_up(**kw):
    d = dict(pelvis=(0, -0.02, 0.62), lfoot=(-0.12, -0.42, 0.06), rfoot=(0.12, -0.42, 0.06),
             lknee=(-0.12, 1.0, -0.3), rknee=(0.12, 1.0, -0.3), lean=10)
    d.update(kw)
    return d


def crouch(**kw):
    d = dict(pelvis=(0, -0.08, 0.3), lfoot=(-0.16, 0.12, 0.08), rfoot=(0.16, 0.12, 0.08),
             lknee=(-0.25, 1.0, 1.0), rknee=(0.25, 1.0, 1.0), lean=25)
    d.update(kw)
    return d


def floor_sit(**kw):
    d = dict(pelvis=(0, 0, 0.13), lfoot=(-0.14, 0.5, 0.08), rfoot=(0.14, 0.5, 0.08),
             lknee=(-0.2, 0.4, 1.5), rknee=(0.2, 0.4, 1.5), lean=-4)
    d.update(kw)
    return d


def lap(loc, yaw, s, seat):
    r = Euler((0, 0, math.radians(yaw))).to_matrix()
    c = Vector((loc[0], loc[1], 0.0))
    return (tuple(c + r @ Vector((-0.1 * s, 0.25 * s, seat + 0.15 * s))),
            tuple(c + r @ Vector((0.1 * s, 0.25 * s, seat + 0.15 * s))))


WIG0 = (lambda t: (0, 0, 0))


def seated(key, loc, yaw, seat, wig=WIG0, name=None, **kw):
    """A figure that stays put (the mannequins, mostly)."""
    s = L.SCALE[key]
    lh, rh = lap(loc, yaw, s, seat)
    p = sit(s, seat, lhand=lh, rhand=rh)
    p.update(kw)
    return Track(key, [K(0, loc, yaw, p)], name=name, wig=wig if key.startswith("doll") else None)


def standing(key, loc, yaw, base=0.0, wig=WIG0, **kw):
    p = stand(L.SCALE[key])
    p.update(kw)
    return Track(key, [K(0, (loc[0], loc[1], base), yaw, p)], wig=wig if key.startswith("doll") else None)


def head_of(name, off=(0, 0, 0)):
    return lambda t, S: tuple(S[name].joint("head") + Vector(off))


def plate_prop(name, track):
    return Prop(name, lambda bm: L.bm_cyl(bm, (0, 0, 0), (0, 0, 0.02), 0.12, seg=16), (0.75, 0.75, 0.75), track)


# ====================================================================== DINING
FRONTAL = dict(loc=(4.95, 6.9, 1.18), aim=(1.9, 6.9, 1.0))


def wife_at_table():
    return seated("doll-wife", SEAT_WIFE, 0, 0.46)


def child_at_table(**kw):
    return seated("doll-daughter", SEAT_CHILD, 180, 0.46, **kw)


def adam_seated(keys):
    return Track("adam", [K(t, (SEAT_ADAM[0], SEAT_ADAM[1]), -90, sit(1.0, 0.46, **p)) for t, p in keys])


HANDS_FLAT = dict(lhand=(1.72, 7.12, 0.775), rhand=(1.72, 6.68, 0.775))


@run("G03", 10)
def g03():
    build_apartment(dict(table="set"))
    wife_at_table()
    child_at_table()
    w, c = (2.05, 6.42, 0.8), (2.05, 7.4, 0.8)
    a = Track("adam", [
        K(0.0, (3.05, 8.6), yaw_to(-0.4, -1.0), walking(lhand=(2.85, 8.95, 1.0), rhand=(3.25, 8.95, 1.0))),
        K(1.6, (2.68, 6.75), 150, walking(lhand=(2.4, 6.55, 1.0), rhand=(2.55, 6.4, 1.0)), ease="lin"),
        K(2.2, (2.66, 6.5), 90, stand(lean=25, rhand=w, lhand=(2.4, 6.8, 1.0))),
        K(2.8, (2.66, 7.25), 90, stand(lean=10, lhand=(2.4, 7.05, 1.0))),
        K(3.4, (2.66, 7.3), 90, stand(lean=25, lhand=c)),
        K(3.9, (2.66, 6.9), 90, stand(look=(2.0, 7.97, 0.9))),
        K(9.0, (2.66, 6.9), 90, stand(look=(2.0, 7.97, 0.9))),
        K(9.3, (2.66, 6.9), 90, stand(look=(2.0, 7.97, 1.05))),
        K(10.0, (2.66, 6.9), 90, stand(look=(2.0, 7.97, 0.9))),
    ])
    plate_prop("plate_toast_wife", phases((2.2, follow("adam", "rwrist", (0, 0, -0.03))), (99, static(w))))
    plate_prop("plate_toast_child", phases((3.4, follow("adam", "lwrist", (0, 0, -0.03))), (99, static(c))))
    Cam("CAM_A_0-6s_wide-through-kitchen-door", 0, 6, (6.0, 6.9, 1.42), (2.0, 6.9, 0.98), F63)
    Cam("CAM_B_6-10s_CU-adam", 6, 10, (1.6, 6.45, 1.5), (2.66, 6.9, 1.6), F29)
    return a


@run("G05", 6)
def g05():
    build_apartment(dict(table="breakfast"))
    wife_at_table()
    child_at_table()
    adam_seated([(0, dict(HANDS_FLAT, look=(2.0, 7.97, 0.95))), (3.2, dict(HANDS_FLAT, look=(2.0, 7.97, 0.95))),
                 (3.9, dict(HANDS_FLAT, look=(2.0, 5.83, 1.12)))])
    Cam("CAM_A_0-6s_wide-frontal", 0, 6, FRONTAL["loc"], FRONTAL["aim"], F63)


@run("G08", 10)
def g08():
    build_apartment(dict(table="breakfast", child_chair_turned=True))
    wife_at_table()
    ct = seated("doll-daughter", (SEAT_CHILD[0], SEAT_CHILD[1] + 0.12), 0, 0.46)
    foot = ct.at(0, {}).joint("rankle")
    toe = foot + Vector((-0.04, 0.12, 0.02))
    temple = ("head_off", (0.085, 0.03, 0.03))
    base = dict(lhand=tuple(foot + Vector((0.03, 0, -0.01))))
    a = Track("adam", [
        K(0.0, (2.0, 8.66), 180, kneel_heels(**base, rhand=tuple(toe), look=tuple(foot))),
        K(3.6, (2.0, 8.66), 180, kneel_heels(**base, rhand=tuple(foot + Vector((-0.05, 0.02, 0.03))), look=tuple(foot))),
        K(5.0, (2.0, 8.66), 180, kneel_heels(**base, rhand=tuple(foot + Vector((-0.05, 0.02, 0.03))), hpitch=5)),
        K(6.6, (2.0, 8.66), 180, kneel_heels(**base, rhand=tuple(foot + Vector((-0.05, 0.02, 0.03))), hpitch=5)),
        K(7.0, (2.0, 8.66), 180, kneel_heels(**base, rhand=temple, hpitch=5)),
        K(8.0, (2.0, 8.66), 180, kneel_heels(**base, rhand=temple, hpitch=5, hyaw=0)),
        K(8.2, (2.0, 8.66), 180, kneel_heels(**base, rhand=temple, hpitch=5, hyaw=14)),
        K(8.45, (2.0, 8.66), 180, kneel_heels(**base, rhand=temple, hpitch=5, hyaw=-14)),
        K(8.7, (2.0, 8.66), 180, kneel_heels(**base, rhand=temple, hpitch=0, hyaw=0)),
        K(9.4, (2.0, 8.66), 180, kneel_heels(**base, rhand=tuple(foot + Vector((0.0, 0.3, 0.3))), look=(2.0, 8.09, 0.95))),
    ])
    Prop("sandal", lambda bm: L.bm_box(bm, (0, 0, 0), (0.07, 0.15, 0.03)), R.SOLID["doll-daughter"],
         static(foot + Vector((0, 0.05, -0.04))))
    Cam("CAM_A_0-5s_CU-hands-low", 0, 5, (2.8, 8.2, 0.36), tuple(foot + Vector((0, 0, 0.05))), F47)
    Cam("CAM_B_5-10s_CU-adam", 5, 10, (2.45, 8.02, 0.62), lambda S: S["adam"].joint("head"), F29)
    return a


@run("G24", 10)
def g24():
    build_apartment(dict(table="dinner"))
    jug = bpy.data.objects.get("water_jug")
    if jug:
        L.SET_OBJS.remove(jug)
        bpy.data.objects.remove(jug)
    wife_at_table()
    child_at_table(lhand=(2.2, 7.6, 0.79))
    lean = dict(lean=28, lhand=(1.86, 7.05, 0.79), rhand=(1.86, 6.75, 0.79))
    pour = (2.12, 7.36, 0.98)
    a = adam_seated([(0, dict(lean, look=(2.0, 7.97, 0.95))), (2.3, dict(lean, look=(2.0, 7.97, 0.95))),
                     (2.9, dict(lean, look=(2.0, 5.83, 1.12))), (4.4, dict(lean, look=(2.0, 5.83, 1.12))),
                     (5.0, dict(lean, look=(2.0, 7.97, 0.95))),
                     (6.0, dict(lean=20, lhand=(1.86, 7.05, 0.79), rhand=(1.82, 7.2, 0.9), look=(2.2, 7.4, 0.8))),
                     (6.6, dict(lean=26, lhand=(1.86, 7.05, 0.79), rhand=pour, look=(2.2, 7.4, 0.8))),
                     (10.0, dict(lean=26, lhand=(1.86, 7.05, 0.79), rhand=pour, look=(2.2, 7.4, 0.8)))])
    Prop("water_jug", lambda bm: L.bm_cyl(bm, (0, 0, 0), (0, 0, 0.22), 0.06, seg=14, r2=0.05), (0.75, 0.75, 0.75),
         phases((6.0, static((1.8, 7.22, 0.755))), (99, lambda t, S: (S["adam"].joint("rwrist") + Vector((0.0, 0.05, -0.1)),
                                                                     Euler((math.radians(-25 if t > 6.6 else 0), 0, 0)).to_quaternion()))))
    spill = L.box("water_on_cloth", 2.05, 2.5, 7.25, 7.62, 0.755, 0.758)
    vis(spill, [(0, False), (7.8, True)])
    Cam("CAM_A_0-6s_wide-frontal", 0, 6, FRONTAL["loc"], FRONTAL["aim"], F63)
    Cam("CAM_B_6-10s_insert-cup", 6, 10, (2.95, 7.2, 1.05), (2.22, 7.45, 0.8), F47)
    return a


@run("G25", 5)
def g25():
    build_apartment(dict(table="spilled"))
    wife_at_table()
    child_at_table(lhand=(2.2, 7.6, 0.79))
    hd = dict(lean=12, lhand=(1.66, 7.1, 0.77), rhand=(1.66, 6.7, 0.77))
    adam_seated([(0, dict(hd, hpitch=38)), (4.2, dict(hd, hpitch=38)), (5.0, dict(hd, hpitch=18))])
    Cam("CAM_A_0-5s_wide-side", 0, 5, (4.25, 5.15, 1.3), (1.95, 7.0, 0.95), F63)


@run("G26", 5)
def g26():
    build_apartment(dict(table="knocked"))
    wife_at_table()
    child_at_table()
    g = dict(lean=8, lhand=(1.5, 7.1, 0.76), rhand=(1.5, 6.7, 0.76))
    adam_seated([(0, dict(g, hpitch=-3)), (1.5, dict(g, hpitch=-3)), (2.1, dict(g, look=(2.0, 5.83, 1.12))),
                 (2.6, dict(g, look=(2.0, 5.83, 1.12))), (3.2, dict(g, look=(2.0, 7.97, 0.95))),
                 (3.8, dict(lean=4, lhand=(1.42, 7.05, 0.68), rhand=(1.42, 6.75, 0.68), look=(2.0, 7.97, 0.95))),
                 (5.0, dict(lean=4, lhand=(1.42, 7.05, 0.68), rhand=(1.42, 6.75, 0.68), look=(2.0, 7.97, 0.95)))])
    Cam("CAM_A_0-5s_CU-adam", 0, 5, (3.1, 6.9, 1.15), (1.15, 6.9, 1.2), F29, hand="breath")


# ====================================================================== LIVING ROOM
LIVING = dict(loc=(4.2, 7.0, 1.5), aim=(2.75, 1.3, 0.95))


def wife_armchair():
    yaw = yaw_to(SOFA_MID - ARMCHAIR[0], SOFA_Y - ARMCHAIR[1])
    r = Euler((0, 0, math.radians(yaw))).to_matrix()
    loc = Vector((ARMCHAIR[0], ARMCHAIR[1], 0)) + r @ Vector((0, 0.06, 0))
    return seated("doll-wife", (loc.x, loc.y), yaw, 0.42)


def child_sofa(x=SOFA_MID, **kw):
    return seated("doll-daughter", (x, SOFA_Y), 0, SOFA_SEAT_Z, **kw)


@run("G10", 5)
def g10():
    build_apartment(dict(table="breakfast"))
    wife_armchair()
    dest = Vector((SOFA_MID, SOFA_Y + 0.62))
    a = Track("adam", [
        K(0.0, (4.45, 2.05), yaw_to(dest.x - 4.45, dest.y - 2.05), walking()),
        K(2.5, tuple(dest), 180, walking(), ease="lin"),
        K(3.0, tuple(dest), 180, stand(pelvis=(0, -0.05, 0.86), lean=35)),
        K(4.3, tuple(dest), 180, stand(pelvis=(0, -0.05, 0.88), lean=30)),
        K(5.0, tuple(dest), 180, stand(lean=10)),
    ])
    s = L.SCALE["doll-daughter"]
    yc = Vector((1, 0, 0.15)).normalized()
    zc = Vector((-0.7, 0, 0.7))
    zc = (zc - yc * zc.dot(yc)).normalized()
    rel = Matrix((yc.cross(zc), yc, zc)).transposed()
    pel_local = Vector((0, -0.04, 0.46 + 0.07 * s))
    sofa_R = Matrix.Identity(3)
    sofa_loc = Vector((SOFA_MID, SOFA_Y, 0))

    def child_root(t):
        aloc, aR = a.root_at(t)
        carry_R = aR @ rel
        carry_loc = aloc + aR @ Vector((0.08, 0.34, 1.0)) - carry_R @ pel_local
        u = R.smooth((t - 2.6) / 0.5)
        if u <= 0:
            return carry_loc, carry_R
        q = carry_R.to_quaternion().slerp(sofa_R.to_quaternion(), u)
        return carry_loc.lerp(sofa_loc, u), q.to_matrix()
    c = Track("doll-daughter", [K(0, (SOFA_MID, SOFA_Y), 0, sit(s, SOFA_SEAT_Z, lfoot=(-0.06, 0.55, 0.5), rfoot=(0.06, 0.55, 0.5),
                                                                     lhand=None, rhand=None))],
              root=child_root, wig=WIG0)
    R.TRACKS.remove(c)
    R.TRACKS.insert(R.TRACKS.index(a), c)

    def rh(t, S):
        ch = S["doll-daughter"]
        return tuple(ch.W((0, 0.28, 0.4)))

    def lh(t, S):
        ch = S["doll-daughter"]
        return tuple(ch.W((0, -0.1, 1.0)))
    for k in a.keys:
        if k.t < 3.0:
            k.pose["rhand"], k.pose["lhand"] = rh, lh
            k.pose["look"] = lambda t, S: tuple(S["doll-daughter"].joint("head"))
    a.keys[3].pose["rhand"] = lambda t, S: tuple(S["doll-daughter"].joint("head") + Vector((0.06, -0.06, 0.05)))
    Cam("CAM_A_0-5s_wide", 0, 5, LIVING["loc"], LIVING["aim"], F63)
    return a


@run("G11", 15)
def g11():
    build_apartment(dict(table="breakfast"))
    wife_armchair()

    def wig(t):
        u = R.smooth((t - 7.6) / 0.4) - R.smooth((t - 11.0) / 1.5)
        return (0.07 * u, 0.0, -0.045 * u)
    c = child_sofa(wig=wig)
    hd = c.at(0, {}).joint("head")
    body = dict(tyaw=-62, pyaw=-25, lean=14)

    def brush(t, S):
        ph = (t % 1.2) / 1.2
        return tuple(hd + Vector((-0.06, -0.06, 0.1 - 0.16 * ph)))
    braid = tuple(hd + Vector((-0.05, -0.08, -0.1)))
    a = Track("adam", [
        K(0.0, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=brush, lhand=braid, look=tuple(hd))),
        K(2.8, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=brush, lhand=braid, look=tuple(hd))),
        K(3.2, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=brush, lhand=braid, look=(4.2, 2.9, 1.0))),
        K(4.2, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=brush, lhand=braid, look=(4.2, 2.9, 1.0))),
        K(4.8, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=brush, lhand=braid, look=tuple(hd))),
        K(6.8, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=tuple(hd + Vector((-0.06, -0.06, 0.0))), lhand=braid, look=tuple(hd))),
        K(7.6, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=tuple(hd + Vector((-0.12, -0.04, 0.0))), lhand=braid, look=tuple(hd))),
        K(10.5, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=(3.6, 1.3, 0.62), lhand=(3.5, 1.3, 0.62), look=tuple(hd))),
        K(11.0, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=tuple(hd + Vector((0.0, -0.02, 0.1))), lhand=tuple(hd + Vector((-0.08, 0.0, 0.0))), look=tuple(hd))),
        K(12.4, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=tuple(hd + Vector((0.04, -0.02, 0.1))), lhand=tuple(hd + Vector((-0.08, 0.0, 0.0))), look=tuple(hd))),
        K(13.0, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=tuple(hd + Vector((-0.03, -0.04, 0.11))), lhand=braid, look=tuple(hd))),
        K(13.5, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=tuple(hd + Vector((-0.05, -0.06, 0.02))), lhand=braid, look=tuple(hd))),
        K(14.0, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=tuple(hd + Vector((-0.03, -0.04, 0.11))), lhand=braid, look=tuple(hd))),
        K(14.5, (SOFA_W, SOFA_Y), 0, sit(1.0, SOFA_SEAT_Z, **body, rhand=tuple(hd + Vector((-0.05, -0.06, 0.02))), lhand=braid, look=tuple(hd))),
    ])
    Prop("hairbrush", lambda bm: L.bm_box(bm, (0, 0, 0), (0.05, 0.05, 0.22)), R.SOLID["adam"],
         phases((10.4, follow("adam", "rwrist", (0, 0, 0.05))), (99, static((3.62, 1.28, 0.47), 90))))
    Cam("CAM_A_0-6s_MCU-two-shot", 0, 6, (3.62, 3.15, 1.05), (3.56, SOFA_Y, 0.98), F29)
    Cam("CAM_B_6-10s_ECU-wig", 6, 10, (3.62, 1.72, 1.08), tuple(hd), F12)
    Cam("CAM_C_10-15s_CU-adam", 10, 15, (3.95, 2.55, 1.12), (3.33, 1.0, 1.15), F29)
    return a


@run("G16", 8)
def g16():
    build_apartment(dict(table="breakfast"))
    child_sofa()
    mid = Vector((3.365, 2.75, 0))

    def ang(t):
        return math.radians(180.0 * t / 8.0)

    def root(side, base):
        def fn(t):
            a = ang(t)
            r = Euler((0, 0, a)).to_matrix()
            return mid + r @ Vector((side * 0.155, 0, 0)), Euler((0, 0, math.radians(base) + a)).to_matrix()
        return fn

    def pt(x, y, z):
        return lambda t, S: tuple(mid + Euler((0, 0, ang(t))).to_matrix() @ Vector((x, y, z)))

    def shuffle(sg):
        return lambda t, S: (sg * 0.1, 0.05 * math.sin(2 * math.pi * t / 2.0 + (0 if sg < 0 else math.pi)), 0.08)
    Track("doll-wife", [K(0, (0, 0), 0, stand(0.97, lhand=pt(-0.29, -0.13, 1.3), rhand=pt(0.0, 0.45, 1.28),
                                              lfoot=(-0.1, 0.06, 0.06), rfoot=(0.1, 0.06, 0.06)))],
          root=root(1, 90), wig=WIG0)
    a = Track("adam", [K(0, (0, 0), 0, stand(rhand=pt(0.255, -0.13, 1.05), lhand=pt(0.0, 0.45, 1.3),
                                           hyaw=12, hroll=-8, hpitch=6, lfoot=shuffle(-1), rfoot=shuffle(1)))],
              root=root(-1, -90))
    Cam("CAM_A_0-8s_wide", 0, 8, LIVING["loc"], LIVING["aim"], F63)
    return a


@run("G18", 10)
def g18():
    build_apartment(dict(table="breakfast"))
    child_sofa()
    w = Track("doll-wife", [K(0, (3.21, 2.75), -90, stand(0.97)),
                            K(3.99, (3.21, 2.75), -90, stand(0.97)),
                            K(4.0, (SOFA_W, SOFA_Y), 0, sit(0.97, SOFA_SEAT_Z, rhand=lap((SOFA_W, SOFA_Y), 0, 0.97, SOFA_SEAT_Z)[1])),
                            K(7.6, (SOFA_W, SOFA_Y), 0, sit(0.97, SOFA_SEAT_Z, rhand=lap((SOFA_W, SOFA_Y), 0, 0.97, SOFA_SEAT_Z)[1],
                                                            lhand=(3.08, 1.45, 0.75))),
                            K(8.0, (SOFA_W, SOFA_Y), 0, sit(0.97, SOFA_SEAT_Z, rhand=lap((SOFA_W, SOFA_Y), 0, 0.97, SOFA_SEAT_Z)[1],
                                                            lhand=lambda t, S: tuple(S["adam"].joint("head") + S["adam"].M.to_3x3() @ Vector((0, 0.16, 0.03)))))],
              wig=WIG0, missing_until={"larm": 6.6})
    R.TRACKS.remove(w)
    sh = Vector((SOFA_W - 0.18, SOFA_Y - 0.04 + 0.0, 0.97))
    kp = (2.98, 1.78)
    ky = yaw_to(sh.x - kp[0], sh.y - kp[1])
    a = Track("adam", [
        K(0, (3.52, 2.75), 90, stand(lhand=(3.25, 2.58, 1.0), rhand=(3.25, 2.93, 1.0), look=(3.3, 3.15, 0.0), lean=8)),
        K(3.99, (3.52, 2.75), 90, stand(lhand=(3.25, 2.58, 1.0), rhand=(3.25, 2.93, 1.0), look=(3.3, 3.15, 0.0), lean=8)),
        K(4.0, kp, ky, kneel_up(lhand=tuple(sh + Vector((-0.06, 0.2, -0.1))), rhand=tuple(sh + Vector((0.0, 0.3, -0.2))), look=tuple(sh))),
        K(6.6, kp, ky, kneel_up(lhand=tuple(sh + Vector((-0.03, 0.06, -0.02))), rhand=tuple(sh + Vector((0.0, 0.2, -0.12))), look=tuple(sh))),
        K(7.4, kp, ky, kneel_up(lhand=(3.08, 1.42, 0.78), rhand=(3.12, 1.45, 0.76), look=tuple(sh))),
        K(8.0, kp, ky, kneel_up(lhand=lambda t, S: tuple(S["doll-wife"].joint("lwrist") + Vector((-0.04, 0.0, 0.0))),
                                rhand=lambda t, S: tuple(S["doll-wife"].joint("lwrist") + Vector((0.04, 0.0, -0.02))),
                                lean=22, hpitch=22)),
        K(10.0, kp, ky, kneel_up(lhand=lambda t, S: tuple(S["doll-wife"].joint("lwrist") + Vector((-0.04, 0.0, 0.0))),
                                 rhand=lambda t, S: tuple(S["doll-wife"].joint("lwrist") + Vector((0.04, 0.0, -0.02))),
                                 lean=22, hpitch=22)),
    ])
    R.TRACKS.insert(R.TRACKS.index(a), w)
    # wife solved first but her hand at 8 s follows Adam: use his previous-frame head (close enough)
    w.keys[-1].pose["lhand"] = lambda t, S: tuple(a.at(t, {"doll-wife": w.at(7.6, {})}).joint("head") + Vector((0.12, 0.08, 0.03)))

    def arm_track(t, S):
        if t < 4.0:
            rock = math.radians(8) * math.exp(-3 * t) * math.cos(10 * t)
            return Vector((3.3, 3.15, 0.05)), Euler((0, rock, math.radians(95))).to_quaternion()
        f = S["adam"]
        p = (f.joint("lwrist") + f.joint("rwrist")) / 2
        return p, Euler((math.radians(60), 0, math.radians(ky))).to_quaternion()
    arm = Prop("doll-wife_loose-arm", lambda bm: (L.bm_capsule(bm, (0, 0, 0), (0, 0, 0.29), 0.045),
                                                  L.bm_capsule(bm, (0, 0, 0.29), (0, 0, 0.56), 0.039),
                                                  L.bm_sphere(bm, (0, 0, 0.61), (0.044,) * 3)),
               R.SOLID["doll-wife"], arm_track)
    vis(arm.obj, [(0, True), (6.6, False)])
    Cam("CAM_A_0-4s_wide", 0, 4, LIVING["loc"], LIVING["aim"], F63)
    Cam("CAM_B_4-10s_MCU", 4, 10, (3.15, 3.25, 1.15), (3.1, 1.4, 1.02), F47, hand="breath")
    return a


@run("G22", 10)
def g22():
    build_apartment(dict(table="breakfast"))
    c = child_sofa()
    seated("doll-wife", (SOFA_W, SOFA_Y), 0, SOFA_SEAT_Z)
    hd = tuple(c.at(0, {}).joint("head"))
    p0 = (4.26, 1.52)
    y0 = yaw_to(hd[0] - p0[0], hd[1] - p0[1])
    hall = (5.0, 5.3, 1.0)
    a = Track("adam", [
        K(0.0, p0, y0, crouch(look=hd)),
        K(0.8, p0, y0, crouch(rhand=("mouth",), look=hd)),
        K(3.8, p0, y0, crouch(rhand=("mouth",), look=hd)),
        K(4.0, p0, y0, crouch(rhand=("mouth",), look=(hd[0], hd[1], hd[2] - 0.12))),
        K(4.3, p0, y0, crouch(rhand=("mouth",), look=hd)),
        K(5.0, p0, y0, crouch(look=hall)),
        K(6.0, p0, y0, crouch(look=hall)),
        K(6.4, p0, y0, crouch(look=hall, hroll=3, hpitch=-2)),
        K(6.8, p0, y0, crouch(look=hall, hroll=-3, hpitch=2)),
        K(7.2, p0, y0, crouch(look=hall)),
        K(8.4, p0, y0, crouch(look=hd)),
        K(10.0, p0, y0, crouch(look=hd)),
    ])
    Cam("CAM_A_0-5s_CU-two-shot", 0, 5, (3.98, 2.9, 1.0), (4.02, 1.25, 0.93), F29)
    Cam("CAM_B_5-10s_CU-adam", 5, 10, (4.55, 3.1, 1.0), (4.3, 1.5, 0.98), F29)
    return a


def curtains_living(open_from=None, open_to=None):
    """Two living-room curtain panels that slide apart (scale from their outer edge)."""
    L.window_frame("window_living", "y", 0.075, 0.6, 3.9, 0.55, 2.45)

    def panel(name, a0, a1):
        def build(bm):
            n = 10
            for i in range(n):
                s0 = i / n
                s1 = (i + 1) / n
                dz = 0.12 if i % 2 == 0 else 0.07
                L.bm_box(bm, (0.075 + dz / 2, (s0 + s1) / 2 * (a1 - a0), 1.35), (dz, (s1 - s0) * abs(a1 - a0), 2.54))
        return build
    closed_l, open_l = 2.05 / 4.2, 0.45 / 4.2

    def sc(t):
        if open_from is None:
            return (1, open_l / closed_l, 1)
        u = R.smooth((t - open_from) / (open_to - open_from))
        return (1, 1 + (open_l / closed_l - 1) * u, 1)
    Prop("curtain_living_S", panel("S", 0.0, 2.05), (0.66, 0.66, 0.66), static((0, 0.15, 0.0)),
         scale_track=sc, coll="Set")
    Prop("curtain_living_N", panel("N", 0.0, -2.05), (0.66, 0.66, 0.66), static((0, 4.35, 0.0)),
         scale_track=sc, coll="Set")


@run("G43", 6)
def g43():
    build_apartment(dict(table="dinner", living_curtains="none"))
    curtains_living(1.0, 3.0)
    seated("doll-wife", (4.06, SOFA_Y), 0, SOFA_SEAT_Z)
    seated("doll-daughter", (3.54, SOFA_Y), 0, SOFA_SEAT_Z)
    a = Track("adam", [
        K(0.0, (0.45, 2.2), 90, stand(lhand=(0.2, 2.12, 1.5), rhand=(0.2, 2.28, 1.5))),
        K(1.0, (0.45, 2.2), 90, stand(lhand=(0.2, 2.12, 1.5), rhand=(0.2, 2.28, 1.5))),
        K(2.4, (0.45, 2.2), 90, stand(lhand=(0.25, 1.4, 1.5), rhand=(0.25, 3.0, 1.5), hpitch=-5)),
        K(5.0, (0.45, 2.2), 90, stand(lhand=(0.25, 1.45, 1.45), rhand=(0.25, 2.95, 1.45), hpitch=-5)),
        K(5.6, (0.45, 2.2), 90, stand(hpitch=-5)),
    ])
    Cam("CAM_A_0-6s_MS", 0, 6, LIVING["loc"], (2.35, 1.4, 0.95), F63)
    return a


@run("G44", 11)
def g44():
    build_apartment(dict(table="dinner", living_curtains="open"))
    w = seated("doll-wife", (4.06, SOFA_Y), 0, SOFA_SEAT_Z)
    seated("doll-daughter", (3.54, SOFA_Y), 0, SOFA_SEAT_Z)
    wf = w.at(0, {})
    ch = wf.joint("chest")
    p0, p1 = (4.55, 1.88), (4.3, 1.6)
    y0 = yaw_to(4.06 - p0[0], SOFA_Y - p0[1])
    y1 = yaw_to(4.06 - p1[0], SOFA_Y - p1[1])

    def btn(dz):
        return dict(lhand=tuple(ch + Vector((-0.04, 0.14, dz))), rhand=tuple(ch + Vector((0.04, 0.14, dz))))
    face = ("head_off", (0.0, 0.12, -0.02))
    a = Track("adam", [
        K(0.0, p0, y0, stand(look=tuple(wf.joint("head")))),
        K(3.5, p0, y0, stand(look=tuple(wf.joint("head")))),
        K(4.3, p1, y1, stand(lean=25, look=tuple(ch))),
        K(5.6, p1, y1, stand(lean=30, look=tuple(ch), **btn(0.12))),
        K(6.3, p1, y1, stand(lean=30, look=tuple(ch), **btn(0.02))),
        K(7.0, p1, y1, stand(lean=30, look=tuple(ch), **btn(-0.08))),
        K(8.0, p1, y1, stand(lean=30, look=tuple(ch), lhand=tuple(wf.joint("lshoulder") + Vector((0, 0.05, 0))),
                             rhand=tuple(wf.joint("rshoulder") + Vector((0, 0.05, 0))))),
        K(8.8, p1, y1, stand(lean=8, lhand=(4.22, 1.85, 1.2), rhand=(4.36, 1.85, 1.2))),
        K(9.4, p1, y1, stand(lean=4, lhand=face, rhand=face, hpitch=10)),
        K(11.0, p1, y1, stand(lean=4, lhand=face, rhand=face, hpitch=10)),
    ])
    card = Prop("cardigan", lambda bm: L.bm_box(bm, (0, 0, 0), (0.3, 0.08, 0.24)), R.SOLID["doll-wife"],
                R.mid_hands("adam", (0, 0.05, 0)))
    vis(card.obj, [(0, False), (8.0, True)])
    Cam("CAM_A_0-5s_wide", 0, 5, LIVING["loc"], LIVING["aim"], F63)
    Cam("CAM_B_5-11s_CU-hands", 5, 11, (3.55, 1.95, 1.05), tuple(ch + Vector((0, 0, -0.05))), F47)
    return a


# ====================================================================== KITCHEN
@run("G14", 13)
def g14():
    build_apartment(dict(table="breakfast"))
    standing("doll-wife", (5.02, 7.08), -90)
    radio = (8.0, 6.68, 1.74)
    pot = Vector((7.8, 7.56, 1.04))

    def stir(t, S):
        a = 2 * math.pi * t / 1.5
        return tuple(pot + Vector((0.06 * math.cos(a), 0.06 * math.sin(a), 0)))

    def sway(t, S):
        return 3 * math.sin(2 * math.pi * t / 2.4)
    wife_head = (5.02, 7.08, 1.6)
    st = (7.2, 7.62)
    a = Track("adam", [
        K(0.0, (7.35, 6.72), -90, stand(rhand=radio)),
        K(3.5, (7.35, 6.72), -90, stand(rhand=radio)),
        K(4.0, st, -62, stand(rhand=stir, tyaw=18, troll=sway, look=(7.8, 7.56, 1.0))),
        K(4.8, st, -62, stand(rhand=stir, tyaw=18, troll=sway, look=(7.8, 7.56, 1.0))),
        K(5.1, st, -62, stand(rhand=("mouth",), tyaw=18, hpitch=-5)),
        K(5.5, st, -62, stand(rhand=stir, tyaw=18, troll=sway, look=(7.8, 7.56, 1.0))),
        K(6.0, st, -62, stand(rhand=stir, tyaw=18, troll=sway, look=wife_head)),
        K(9.0, st, -62, stand(rhand=stir, tyaw=18, troll=sway, look=wife_head)),
        K(9.8, st, -20, stand(lhand=(7.2, 7.95, 0.95), rhand=(7.28, 7.95, 0.95), look=wife_head)),
        K(10.6, st, -20, stand(lhand=(7.15, 7.95, 0.95), rhand=(7.3, 7.95, 0.95), look=wife_head)),
        K(11.0, st, 30, stand(lhand=(6.75, 7.45, 1.3), look=wife_head)),
        K(13.0, st, 30, stand(lhand=(6.75, 7.45, 1.3), look=wife_head)),
    ])
    Cam("CAM_A_0-4s_insert-radio", 0, 4, (7.3, 6.2, 1.7), radio, F18)
    Cam("CAM_B_4-9s_MS", 4, 9, (4.3, 6.58, 1.55), (7.3, 7.5, 1.25), F47)
    Cam("CAM_C_9-13s_CU-adam", 9, 13, (5.85, 7.15, 1.6), (7.2, 7.6, 1.6), F29)
    return a


@run("G20", 5)
def g20():
    build_apartment(dict(table="breakfast"))
    door = (5.0, 6.9, 1.6)
    a = Track("adam", [
        K(0.0, (7.2, 7.3), -35, stand(look=door)),
        K(1.8, (7.2, 7.3), -35, stand(look=door)),
        K(2.6, (7.2, 7.3), -35, stand(look=door, rhand=(7.95, 6.75, 1.72))),
        K(3.4, (7.2, 7.3), -35, stand(look=door, rhand=(7.95, 6.75, 1.72))),
        K(4.2, (7.2, 7.3), -35, stand(look=door)),
    ])
    Cam("CAM_A_0-5s_CU-adam", 0, 5, (7.1, 6.14, 1.63), (7.2, 7.3, 1.62), F29)
    return a


# ====================================================================== SEWING CORNER
@run("G45", 6)
def g45():
    build_apartment(dict(table="dinner", living_curtains="open"))
    face = (2.9, 3.3)
    standing("doll-wife", STAND_WIFE, yaw_to(face[0] - STAND_WIFE[0], face[1] - STAND_WIFE[1]), base=0.025, wig=None)
    c = standing("doll-daughter", STAND_CHILD, yaw_to(face[0] - STAND_CHILD[0], face[1] - STAND_CHILD[1]), base=0.025, wig=None)
    sh = c.at(0, {}).joint("rshoulder")
    p0, p1 = (0.98, 1.22), (1.45, 1.5)
    y0 = yaw_to(sh.x - p0[0], sh.y - p0[1])
    y1 = yaw_to(sh.x - p1[0], sh.y - p1[1])
    hold = dict(lhand=tuple(sh + Vector((0.06, 0.08, 0.12))), rhand=tuple(sh + Vector((0.12, -0.04, 0.12))))
    lay = dict(lhand=tuple(sh + Vector((0.02, 0.06, 0.05))), rhand=tuple(sh + Vector((0.08, -0.06, 0.03))))
    a = Track("adam", [
        K(0.0, p0, y0, stand(lean=10, look=tuple(sh), **hold)),
        K(1.5, p0, y0, stand(lean=12, look=tuple(sh), **lay)),
        K(2.0, p0, y0, stand(lean=12, look=tuple(sh), lhand=tuple(sh + Vector((0.0, 0.08, 0.0))), rhand=tuple(sh + Vector((0.08, -0.06, 0.03))))),
        K(2.6, p0, y0, stand(look=tuple(sh))),
        K(3.5, p0, y0, stand(look=tuple(sh))),
        K(4.6, p1, y1, walking(look=tuple(sh)), ease="lin"),
        K(5.0, p1, y1, stand(look=tuple(sh))),
    ])
    Prop("sleeve", lambda bm: L.bm_cyl(bm, (-0.08, 0, 0), (0.08, 0, 0), 0.04), R.SOLID["doll-daughter"],
         phases((1.5, R.mid_hands("adam", (0, 0, -0.02))), (99, static(sh + Vector((0.03, 0, 0.02))))))
    Cam("CAM_A_0-6s_wide", 0, 6, (2.95, 3.35, 1.35), (1.3, 0.5, 1.0), F63)
    return a


# ====================================================================== HALLWAY
HALL = dict(loc=(4.85, 5.22, 1.55), aim=(12.0, 5.3, 1.3))


@run("G21", 8)
def g21():
    build_apartment(dict(table="breakfast", bag=True))
    a = Track("adam", [K(0, (8.6, 5.3), -90, stand()), K(6.0, (8.6, 5.3), -90, stand()),
                       K(6.8, (8.6, 5.3), -90, stand(hpitch=16))])
    Cam("CAM_A_0-8s_wide", 0, 8, HALL["loc"], HALL["aim"], F63)
    return a


@run("G40", 5)
def g40():
    build_apartment(dict(table="dinner", bag=True))
    a = Track("adam", [K(0.0, (5.55, 5.28), -90, walking()), K(3.5, (8.9, 5.3), -90, walking(), ease="lin"),
                       K(4.1, (8.9, 5.3), 180, stand(hpitch=30)), K(5.0, (8.9, 5.3), 180, stand(hpitch=34))])
    Cam("CAM_A_0-5s_wide", 0, 5, HALL["loc"], HALL["aim"], F63)
    return a


@run("G47", 5)
def g47():
    build_apartment(dict(table="drawing", bag=False, living_curtains="open"))
    a = Track("adam", [K(0.0, (8.4, 5.3), -90, walking()), K(2.2, (11.5, 5.3), -90, walking(), ease="lin"),
                       K(2.5, (11.55, 5.3), -90, stand()),
                       K(2.8, (11.55, 5.3), -90, stand(rhand=(11.93, 5.6, 1.5))),
                       K(3.6, (11.55, 5.3), -90, stand(rhand=(11.93, 5.0, 1.0))),
                       K(4.2, (11.55, 5.3), -90, stand(rhand=(11.93, 5.0, 1.0), lean=-3)),
                       K(5.0, (11.55, 5.3), -90, stand(rhand=(11.93, 5.0, 1.0)))])
    Cam("CAM_A_0-5s_wide", 0, 5, HALL["loc"], HALL["aim"], F63)
    return a


@run("G49", 6)
def g49():
    build_apartment(dict(table="drawing", bag=False, living_curtains="open", front_door=90, landing_dish=True,
                         wife_chair_out=True))
    standing("doll-wife", STAND_WIFE, yaw_to(2.9 - STAND_WIFE[0], 3.3 - STAND_WIFE[1]), base=0.025, wig=None)
    standing("doll-daughter", STAND_CHILD, yaw_to(2.9 - STAND_CHILD[0], 3.3 - STAND_CHILD[1]), base=0.025, wig=None)
    m = Track("mona", [K(0.0, (12.45, 5.3), 90, stand(0.95)), K(1.0, (12.45, 5.3), 90, stand(0.95)),
                       K(1.6, (12.05, 5.3), 90, stand(0.95, lhand=(11.62, 5.12, 1.28), rhand=(11.62, 5.48, 1.28), lean=5)),
                       K(6.0, (12.05, 5.3), 90, stand(0.95, lhand=(11.62, 5.12, 1.28), rhand=(11.62, 5.48, 1.28), lean=5))])
    a = Track("adam", [K(0.0, (11.72, 5.3), -90, stand(hpitch=32)), K(2.8, (11.72, 5.3), -90, stand(hpitch=32)),
                       K(3.6, (11.72, 5.3), -90, stand(lean=14, hpitch=30, hroll=-15, lhand=(12.15, 5.15, 1.15), rhand=(12.15, 5.45, 1.15))),
                       K(6.0, (11.72, 5.3), -90, stand(lean=14, hpitch=30, hroll=-15, lhand=(12.15, 5.15, 1.15), rhand=(12.15, 5.45, 1.15)))])
    Cam("CAM_A_0-6s_wide", 0, 6, (0.4, 5.45, 1.15), (12.0, 5.3, 1.25), F63)
    return a, m


# ====================================================================== NOUR'S ROOM
NOUR_WIDE = dict(loc=(11.85, 2.45, 1.45), aim=(9.3, 3.55, 0.95))


def lying_child(wig=WIG0):
    s = L.SCALE["doll-daughter"]
    rot = Euler((0, math.radians(6), 0)).to_matrix() @ Euler((math.radians(90), 0, math.radians(-90))).to_matrix()
    y = (BED["y0"] + BED["y1"]) / 2
    return Track("doll-daughter", [K(0, (BED["x0"] + 0.27 + 1.63 * s, y, 0.53), rot, stand(s))], wig=wig)


def blanket(x_from, x_to=None, t0=0.0, t1=0.0):
    x1 = BED["x1"] - 0.02
    ln = x1 - x_from

    def sc(t):
        if x_to is None:
            return (1, 1, 1)
        u = R.smooth((t - t0) / max(1e-6, t1 - t0))
        return ((x1 - (x_from + (x_to - x_from) * u)) / ln, 1, 1)
    Prop("blanket", lambda bm: L.bm_box(bm, (-ln / 2, 0, 0.08), (ln, BED["y1"] - BED["y0"] - 0.06, 0.16)),
         (0.58, 0.58, 0.58), static((x1, (BED["y0"] + BED["y1"]) / 2, 0.44)), scale_track=sc, coll="Set")


def rabbit(track):
    Prop("rabbit", lambda bm: (L.bm_sphere(bm, (0, 0, 0), (0.07, 0.06, 0.08)), L.bm_sphere(bm, (-0.08, 0, 0.06), (0.05,) * 3)),
         (0.5, 0.5, 0.5), track, coll="Set")


@run("G29", 16)
def g29():
    build_apartment(dict(table="dinner"))
    c = lying_child()
    blanket(9.95, 9.6, 0.2, 1.5)
    cf = c.at(0, {})
    chest, head = cf.joint("chest"), cf.joint("head")
    edge = (10.22, 2.84)
    body = dict(tyaw=72, pyaw=20, lean=30)
    tuck = dict(lhand=tuple(Vector((9.95, 1.95, 0.62))), rhand=tuple(Vector((9.95, 2.35, 0.62))))
    up = dict(lhand=tuple(Vector((9.62, 1.95, 0.64))), rhand=tuple(Vector((9.62, 2.35, 0.64))))
    a = Track("adam", [
        K(0.0, edge, 0, sit(1.0, 0.44, **body, **tuck, look=tuple(chest))),
        K(1.5, edge, 0, sit(1.0, 0.44, **body, **up, look=tuple(head))),
        K(2.4, edge, 0, sit(1.0, 0.44, **body, lhand=(9.8, 1.95, 0.62), rhand=(9.8, 2.35, 0.62), look=tuple(head))),
        K(3.0, edge, 0, sit(1.0, 0.44, **body, lhand=(9.8, 1.95, 0.62), rhand=(9.3, 1.9, 0.62), look=(9.3, 1.9, 0.6))),
        K(3.5, edge, 0, sit(1.0, 0.44, **body, lhand=(9.8, 1.95, 0.62), rhand=(9.62, 1.88, 0.62), look=tuple(head))),
        K(5.8, edge, 0, sit(1.0, 0.44, **body, lhand=(9.8, 1.95, 0.62), rhand=(9.8, 2.35, 0.62), look=tuple(head))),
        K(7.0, edge, 0, sit(1.0, 0.44, tyaw=80, pyaw=20, lean=62, lhand=(9.7, 1.95, 0.62), rhand=(9.7, 2.4, 0.62), look=tuple(head))),
        K(9.2, edge, 0, sit(1.0, 0.44, tyaw=80, pyaw=20, lean=62, lhand=(9.7, 1.95, 0.62), rhand=(9.7, 2.4, 0.62), look=tuple(head))),
        K(9.8, edge, 0, sit(1.0, 0.44, tyaw=78, pyaw=20, lean=52, lhand=(9.7, 1.95, 0.62), rhand=(9.7, 2.4, 0.62), look=tuple(head))),
        K(11.9, edge, 0, sit(1.0, 0.44, tyaw=60, pyaw=20, lean=30, look=tuple(head))),
        K(12.0, (10.4, 4.38), yaw_to(-0.6, -2.2), stand(lhand=(10.92, 4.52, 1.2), look=tuple(head))),
        K(13.4, (10.4, 4.38), yaw_to(-0.6, -2.2), stand(lhand=(10.92, 4.52, 1.2), look=tuple(head))),
        K(13.6, (10.4, 4.38), yaw_to(-0.6, -2.2), stand(lhand=(10.92, 4.5, 1.18), look=tuple(head))),
        K(16.0, (10.4, 4.38), yaw_to(-0.6, -2.2), stand(lhand=(10.92, 4.5, 1.18), look=tuple(head))),
    ])
    rabbit(phases((3.05, static((9.28, 1.86, 0.56))), (3.5, follow("adam", "rwrist", (0, 0, -0.04))), (99, static((9.62, 1.86, 0.62)))))
    Cam("CAM_A_0-6s_MS-bed-foot", 0, 6, (11.75, 3.45, 1.4), (10.0, 2.5, 0.75), F47)
    Cam("CAM_B_6-12s_CU-adam-side", 6, 12, (9.85, 3.4, 0.95), tuple(head + Vector((0.2, 0.15, 0.2))), F29)
    Cam("CAM_C_12-16s_wide", 12, 16, NOUR_WIDE["loc"], NOUR_WIDE["aim"], F63)
    return a


@run("G30", 10)
def g30():
    build_apartment(dict(table="dinner"))
    lying_child()
    blanket(9.6)
    rabbit(static((9.62, 1.86, 0.62)))
    frame = (10.8, 4.52, 1.25)
    d = (10.4, 4.42)
    a = Track("adam", [K(0.0, (10.4, 4.3), 0, walking()), K(1.0, d, 0, walking(rhand=frame), ease="lin"),
                       K(1.3, d, 0, stand(rhand=frame)), K(5.5, d, 0, stand(rhand=frame)),
                       K(6.4, d, 0, stand(rhand=frame, hyaw=4)), K(6.8, d, 0, stand(rhand=frame, hyaw=-4)),
                       K(7.2, d, 0, stand(rhand=frame, hyaw=0)), K(8.5, d, 0, stand(rhand=frame)),
                       K(8.8, d, 0, stand(rhand=frame, hpitch=8)), K(10.0, d, 0, stand(rhand=frame, hpitch=8))])
    Cam("CAM_A_0-5.5s_CU-profile", 0, 5.5, (11.9, 4.3, 1.62), (10.4, 4.42, 1.62), F29)
    Cam("CAM_B_5.5-10s_CU-frontal-pushin", 5.5, 10, (10.4, 5.85, 1.62), (10.4, 4.42, 1.62), F29, loc1=(10.4, 5.6, 1.62))
    return a


@run("G38", 5)
def g38():
    build_apartment(dict(table="dinner"))
    c = lying_child(wig=lambda t: (0.065, 0.0, -0.03))
    blanket(9.6)
    rabbit(static((9.62, 1.86, 0.62)))
    hd = c.at(0, {}).joint("head")
    Cam("CAM_A_0-5s_low-floor", 0, 5, (9.9, 3.4, 0.42), tuple(hd + Vector((0.15, 0, 0))), F63)


@run("G39", 12)
def g39():
    build_apartment(dict(table="dinner"))
    lying_child(wig=lambda t: (0.065, 0.0, -0.03))
    blanket(9.6)
    rabbit(static((9.62, 1.86, 0.62)))
    p = (10.1, 2.87)
    eyes = dict(lhand=("head_off", (-0.04, 0.11, 0.02)), rhand=("head_off", (0.04, 0.11, 0.02)))
    knees = dict(lhand=(10.02, 3.25, 0.45), rhand=(10.18, 3.25, 0.45))
    a = Track("adam", [
        K(0.0, (10.1, 3.1), 0, floor_sit(pelvis=(0, 0, 0.12), lean=-58, hpitch=-25, lhand=(9.82, 3.0, 0.06), rhand=(10.38, 3.0, 0.06))),
        K(1.5, p, 0, floor_sit(hpitch=6)),
        K(2.5, p, 0, floor_sit(hpitch=12)),
        K(4.8, p, 0, floor_sit(hpitch=22, lean=6)),
        K(5.0, p, 0, floor_sit(hpitch=26, lean=10)),
        K(6.6, p, 0, floor_sit(hpitch=20, lean=12)),
        K(7.0, p, 0, floor_sit(hpitch=20, lean=14, **eyes)),
        K(8.4, p, 0, floor_sit(hpitch=20, lean=14, **eyes)),
        K(8.5, p, 0, floor_sit(hpitch=45, lean=40, **knees)),
        K(12.0, p, 0, floor_sit(hpitch=45, lean=40, **knees)),
    ])
    Cam("CAM_A_0-8.5s_MS", 0, 8.5, (10.2, 4.45, 0.9), (10.1, 2.9, 0.65), F47)
    Cam("CAM_B_8.5-12s_wide", 8.5, 12, NOUR_WIDE["loc"], NOUR_WIDE["aim"], F63)
    return a


# ====================================================================== CAR
def car_people(off, adam_r="gear", layla_l="gear", nour="drawing", nour_kw=None, layla_kw=None, adam_kw=None):
    gear = off + Vector((0, 0.45, 0.65))
    wl = off + WHEEL_C + Vector((-0.17, -0.05, 0.03))
    wr = off + WHEEL_C + Vector((0.17, -0.05, 0.03))
    dl = off + Vector((*CAR["driver"], 0))
    pl = off + Vector((*CAR["passenger"], 0))
    rl = off + Vector((*CAR["rear_right"], 0))
    s = L.SCALE["nour"]
    book = rl + Vector((0, 0.24, SEAT_Z_REAR + 0.22))
    paper = rl + Vector((-0.08, 0.36, 0.93))
    return dict(gear=gear, wl=wl, wr=wr, dl=dl, pl=pl, rl=rl, book=book, paper=paper, s=s)


def nour_drawing(P, **kw):
    d = sit(P["s"], SEAT_Z_REAR, lhand=tuple(P["book"] + Vector((-0.07, -0.02, 0.03))),
            rhand=tuple(P["book"] + Vector((0.05, 0.05, 0.03))), hpitch=38, lean=12)
    d.update(kw)
    return d


def nour_paper(P, paper=None, **kw):
    pp = paper if paper is not None else P["paper"]
    d = sit(P["s"], SEAT_Z_REAR, lean=18, lhand=tuple(pp + Vector((-0.11, -0.01, -0.04))),
            rhand=tuple(pp + Vector((0.11, -0.01, -0.04))), hpitch=-5)
    d.update(kw)
    return d


def drive(P, rhand="gear", **kw):
    d = car_sit(1.0, SEAT_Z_FRONT, lean=-8, lhand=tuple(P["wl"]), rhand=tuple(P["gear"] if rhand == "gear" else P["wr"]))
    d.update(kw)
    return d


def layla_seat(P, **kw):
    lh, rh = lap(P["pl"], 0, 0.95, SEAT_Z_FRONT)
    d = car_sit(0.95, SEAT_Z_FRONT, lean=-8, lhand=lh, rhand=rh)
    d.update(kw)
    return d


def swing_feet(P):
    def f(sg, ph0):
        return lambda t, S: (sg * 0.07, 0.3 + 0.09 * math.sin(2 * math.pi * t / 0.9 + ph0), 0.2)
    return dict(lfoot=f(-1, 0.0), rfoot=f(1, math.pi))


def static_car_people(P, nour="drawing", adam_r="wheel", layla=None):
    Track("adam", [K(0, tuple(P["dl"]), 0, drive(P, adam_r))])
    Track("layla", [K(0, tuple(P["pl"]), 0, layla or layla_seat(P))])
    Track("nour", [K(0, tuple(P["rl"]), 0, nour_drawing(P) if nour == "drawing" else nour_paper(P))])


def truck(path, t0, t1):
    def tr(t, S):
        u = max(0.0, min(1.0, (t - t0) / (t1 - t0)))
        return Vector(path[0]).lerp(Vector(path[1]), u), Euler((0, 0, 0)).to_quaternion()
    Prop("truck", lambda bm: (L.bm_box(bm, (0, 0, 1.9), (2.5, 7.0, 3.2)), L.bm_box(bm, (0, -3.3, 0.5), (2.4, 0.4, 0.3))),
         (0.5, 0.5, 0.5), tr, coll="Set")


@run("G09", 5)
def g09():
    off = build_car()
    P = car_people(off)
    Track("adam", [K(0, tuple(P["dl"]), 0, drive(P, "wheel"))])
    Track("layla", [K(0, tuple(P["pl"]), 0, layla_seat(P))])
    buckle = P["rl"] + Vector((0.17, -0.02, 0.47))
    chest = P["rl"] + Vector((0.04, 0.1, 0.72))
    n = Track("nour", [K(0.0, tuple(P["rl"]), 0, sit(P["s"], SEAT_Z_REAR, rhand=tuple(buckle), hpitch=20, **swing_feet(P))),
                       K(0.4, tuple(P["rl"]), 0, sit(P["s"], SEAT_Z_REAR, rhand=tuple(buckle), hpitch=20, **swing_feet(P))),
                       K(1.4, tuple(P["rl"]), 0, sit(P["s"], SEAT_Z_REAR, rhand=tuple(chest), hpitch=10, **swing_feet(P))),
                       K(2.4, tuple(P["rl"]), 0, sit(P["s"], SEAT_Z_REAR, hpitch=10, **swing_feet(P)))])
    Cam("CAM_A_0-2.5s_ECU-buckle", 0, 2.5, tuple(off + Vector((0.0, -0.55, 0.62))), tuple(buckle), F18, hand="gentle")
    Cam("CAM_B_2.5-5s_CU-legs", 2.5, 5, tuple(off + Vector((-0.08, -0.6, 0.55))), tuple(P["rl"] + Vector((0.0, 0.3, 0.3))), F63, hand="gentle")
    return n


@run("G12", 6)
def g12():
    off = build_car()
    P = car_people(off)
    Track("adam", [K(0, tuple(P["dl"]), 0, drive(P, "wheel"))])
    n = Track("nour", [K(0.0, tuple(P["rl"]), 0, sit(P["s"], SEAT_Z_REAR, hpitch=-15, **swing_feet(P))),
                       K(4.3, tuple(P["rl"]), 0, sit(P["s"], SEAT_Z_REAR, hpitch=-15, **swing_feet(P))),
                       K(4.8, tuple(P["rl"]), 0, sit(P["s"], SEAT_Z_REAR, hpitch=0, hyaw=20, **swing_feet(P)))])
    nh = lambda t, S: tuple(S["nour"].joint("head") + Vector((0.07, 0.03, 0.02)))  # noqa: E731
    lh, rh = lap(P["pl"], 0, 0.95, SEAT_Z_FRONT)
    Track("layla", [K(0.0, tuple(P["pl"]), 0, layla_seat(P)), K(3.0, tuple(P["pl"]), 0, layla_seat(P)),
                    K(4.0, tuple(P["pl"]), 0, layla_seat(P, tyaw=-30, lhand=nh, look=None)),
                    K(6.0, tuple(P["pl"]), 0, layla_seat(P, tyaw=-30, lhand=nh))])
    Cam("CAM_A_0-3s_CU-nour", 0, 3, tuple(off + Vector((-0.02, -0.66, 0.93))), tuple(P["rl"] + Vector((0, -0.02, 0.86))), F63, hand="gentle")
    Cam("CAM_B_3-6s_CU-hand-and-hair", 3, 6, tuple(off + Vector((-0.1, -0.45, 0.98))), tuple(P["rl"] + Vector((0, -0.02, 0.86))), F47, hand="gentle")
    return n


@run("G15", 10)
def g15():
    off = build_car()
    P = car_people(off)
    radio = off + Vector((0.0, 0.8, 0.72))
    Track("adam", [K(0, tuple(P["dl"]), 0, drive(P, "gear"))])
    Track("nour", [K(0, tuple(P["rl"]), 0, nour_drawing(P))])

    def sway(t, S):
        return 5 * math.sin(2 * math.pi * t / 1.1)
    on = tuple(P["gear"] + Vector((0, 0, 0.04)))
    ah = (P["dl"] + Vector((0, 0, 1.12)))
    l = Track("layla", [K(0.0, tuple(P["pl"]), 0, layla_seat(P, lhand=tuple(radio + Vector((0.05, -0.05, 0))))),
                        K(0.8, tuple(P["pl"]), 0, layla_seat(P, lhand=tuple(radio + Vector((0.02, -0.04, 0.01))))),
                        K(1.3, tuple(P["pl"]), 0, layla_seat(P, lhand=tuple(radio + Vector((0.02, -0.04, 0.06))))),
                        K(1.6, tuple(P["pl"]), 0, layla_seat(P, lhand=tuple(radio + Vector((0.02, -0.04, 0.0))))),
                        K(3.0, tuple(P["pl"]), 0, layla_seat(P, hroll=sway)),
                        K(4.6, tuple(P["pl"]), 0, layla_seat(P, hroll=sway, hpitch=-12)),
                        K(5.6, tuple(P["pl"]), 0, layla_seat(P, look=tuple(ah))),
                        K(6.9, tuple(P["pl"]), 0, layla_seat(P, look=tuple(ah))),
                        K(7.0, tuple(P["pl"]), 0, layla_seat(P, lhand=on, look=tuple(P["gear"]))),
                        K(10.0, tuple(P["pl"]), 0, layla_seat(P, lhand=on, look=tuple(P["gear"])))])
    Cam("CAM_A_0-3s_insert-radio", 0, 3, tuple(off + Vector((0.28, 0.42, 1.0))), tuple(radio), F18, hand="gentle")
    Cam("CAM_B_3-7s_CU-layla", 3, 7, tuple(off + Vector((-0.12, 0.2, 1.08))), tuple(P["pl"] + Vector((0, 0, 1.1))), F63, hand="gentle")
    Cam("CAM_C_7-10s_insert-gearshift", 7, 10, tuple(off + Vector((0.22, 0.12, 0.98))), tuple(P["gear"]), F18, hand="gentle")
    return l


@run("G27", 5)
def g27():
    off = build_car()
    P = car_people(off)
    static_car_people(P, adam_r="wheel")
    for tr in R.TRACKS:
        if tr.name == "layla":
            R.TRACKS.remove(tr)
    nh = P["rl"] + Vector((0, 0, 0.9))
    Track("layla", [K(0.0, tuple(P["pl"]), 0, layla_seat(P, tyaw=20, look=tuple(nh))),
                    K(3.0, tuple(P["pl"]), 0, layla_seat(P, tyaw=20, look=tuple(nh))),
                    K(3.4, tuple(P["pl"]), 0, layla_seat(P, look=tuple(off + Vector((0, 30, 1.0)))))])
    truck(((off.x - 3.5, 220, 0), (off.x - 3.5, 40, 0)), 0, 5)
    Cam("CAM_A_0-2.5s_driver-POV", 0, 2.5, tuple(P["dl"] + Vector((0.0, 0.14, 1.1))), tuple(P["dl"] + Vector((0.1, 30, 1.0))), F63, hand="gentle")
    Cam("CAM_B_2.5-5s_CU-layla", 2.5, 5, tuple(off + Vector((-0.12, 0.2, 1.08))), tuple(P["pl"] + Vector((0, 0, 1.1))), F63, hand="gentle")


@run("G32", 15)
def g32():
    off = build_car()
    P = car_people(off)
    on = tuple(P["gear"] + Vector((0, 0, 0.04)))

    def sway(t, S):
        return 4 * math.sin(2 * math.pi * t / 1.0)
    Track("adam", [K(0.0, tuple(P["dl"]), 0, drive(P, "gear")), K(2.0, tuple(P["dl"]), 0, drive(P, "gear")),
                   K(2.4, tuple(P["dl"]), 0, drive(P, "gear", hyaw=-28)), K(3.2, tuple(P["dl"]), 0, drive(P, "gear")),
                   K(12.4, tuple(P["dl"]), 0, drive(P, "gear")), K(12.7, tuple(P["dl"]), 0, drive(P, "gear", hpitch=-12, hyaw=-10)),
                   K(13.6, tuple(P["dl"]), 0, drive(P, "gear", hpitch=-12, hyaw=-10)), K(14.0, tuple(P["dl"]), 0, drive(P, "gear"))])

    def scrib(t, S):
        return tuple(P["book"] + Vector((0.05 + 0.03 * math.sin(9 * t), 0.05 + 0.02 * math.cos(7 * t), 0.03)))
    Track("nour", [K(0, tuple(P["rl"]), 0, nour_drawing(P, rhand=scrib))])
    nh = tuple(P["rl"] + Vector((0, 0.05, 0.85)))
    ah = tuple(P["dl"] + Vector((0, 0, 1.12)))
    Track("layla", [K(0.0, tuple(P["pl"]), 0, layla_seat(P, lhand=on, troll=sway)),
                    K(8.0, tuple(P["pl"]), 0, layla_seat(P, lhand=on, troll=sway)),
                    K(8.4, tuple(P["pl"]), 0, layla_seat(P, tyaw=40, look=nh)),
                    K(10.2, tuple(P["pl"]), 0, layla_seat(P, tyaw=40, look=nh)),
                    K(10.7, tuple(P["pl"]), 0, layla_seat(P, tyaw=10, look=ah)),
                    K(15.0, tuple(P["pl"]), 0, layla_seat(P, tyaw=10, look=ah))])
    Cam("CAM_A_0-4s_from-back-seat", 0, 4, tuple(off + Vector((-0.02, -0.72, 1.02))), tuple(off + Vector((0, 8, 0.95))), F84, hand="gentle")
    Cam("CAM_B_4-8s_CU-nour", 4, 8, tuple(off + Vector((-0.08, -0.42, 1.0))), tuple(P["rl"] + Vector((0, 0.1, 0.72))), F47, hand="gentle")
    Cam("CAM_C_8-12s_CU-layla", 8, 12, tuple(off + Vector((-0.12, 0.2, 1.08))), tuple(P["pl"] + Vector((0, 0, 1.1))), F63, hand="gentle")
    Cam("CAM_D_12-15s_rear-view-mirror", 12, 15, tuple(off + Vector((0.12, 0.25, 1.12))), tuple(off + Vector((0, 0.565, 1.215))), F18, hand="gentle")


@run("G33", 14)
def g33():
    off = build_car()
    P = car_people(off)
    visor = tuple(off + Vector((-0.37, 0.5, 1.28)))
    Track("adam", [K(0.0, tuple(P["dl"]), 0, drive(P, "wheel")), K(4.4, tuple(P["dl"]), 0, drive(P, "wheel")),
                   K(4.8, tuple(P["dl"]), 0, drive(P, "wheel", lhand=visor)), K(5.4, tuple(P["dl"]), 0, drive(P, "wheel")),
                   K(14, tuple(P["dl"]), 0, drive(P, "wheel"))])
    high = P["rl"] + Vector((-0.28, 0.62, 1.0))
    n = Track("nour", [K(0.0, tuple(P["rl"]), 0, nour_drawing(P)), K(0.5, tuple(P["rl"]), 0, nour_drawing(P)),
                       K(1.1, tuple(P["rl"]), 0, nour_paper(P)), K(7.6, tuple(P["rl"]), 0, nour_paper(P)),
                       K(8.3, tuple(P["rl"]), 0, nour_paper(P, paper=high, lean=34)), K(14, tuple(P["rl"]), 0, nour_paper(P, paper=high, lean=34))])
    lh, rh = lap(P["pl"], 0, 0.95, SEAT_Z_FRONT)
    arm = lambda t, S: tuple(S["adam"].joint("relbow") + Vector((0.04, 0.05, 0.0)))  # noqa: E731
    Track("layla", [K(0.0, tuple(P["pl"]), 0, layla_seat(P)), K(11.0, tuple(P["pl"]), 0, layla_seat(P, hpitch=-10)),
                    K(11.6, tuple(P["pl"]), 0, layla_seat(P, hpitch=-10, lhand=arm)), K(14, tuple(P["pl"]), 0, layla_seat(P, hpitch=-10, lhand=arm))])

    def paper_track(t, S):
        f = S["nour"]
        if t < 0.8:
            return P["book"] + Vector((0, 0, 0.04)), Euler((math.radians(90), 0, 0)).to_quaternion()
        return (f.joint("lwrist") + f.joint("rwrist")) / 2 + Vector((0, 0.01, 0.06)), Euler((0, 0, 0)).to_quaternion()
    Prop("drawing_paper", lambda bm: L.bm_box(bm, (0, 0, 0), (0.24, 0.006, 0.3)), R.SOLID["nour"], paper_track)
    Cam("CAM_A_0-4s_CU-nour-from-front", 0, 4, tuple(off + Vector((-0.15, 0.1, 1.12))), tuple(P["rl"] + Vector((0, 0.05, 0.86))), F47, hand="gentle")
    Cam("CAM_B_4-8s_MCU-adam-from-passenger", 4, 8, tuple(off + Vector((0.22, 0.24, 1.06))), tuple(P["dl"] + Vector((0, 0, 1.02))), F63, hand="gentle")
    Cam("CAM_C_8-11s_CU-nour", 8, 11, tuple(off + Vector((-0.15, 0.1, 1.12))), tuple(P["rl"] + Vector((-0.1, 0.25, 0.9))), F47, hand="gentle")
    Cam("CAM_D_11-14s_CU-layla", 11, 14, tuple(off + Vector((-0.12, 0.2, 1.08))), tuple(P["pl"] + Vector((0, 0, 1.1))), F63, hand="gentle")
    return n


@run("G34", 8)
def g34():
    off = build_car()
    P = car_people(off)
    nh = tuple(P["rl"] + Vector((-0.05, 0.2, 0.9)))
    Track("adam", [K(0.0, tuple(P["dl"]), 0, drive(P, "wheel")), K(0.5, tuple(P["dl"]), 0, drive(P, "wheel")),
                   K(2.5, tuple(P["dl"]), 0, drive(P, "wheel", tyaw=-25, look=nh)),
                   K(8.0, tuple(P["dl"]), 0, drive(P, "wheel", tyaw=-25, look=nh, hroll=4))])
    Track("layla", [K(0, tuple(P["pl"]), 0, layla_seat(P))])
    Track("nour", [K(0, tuple(P["rl"]), 0, nour_paper(P))])
    Prop("drawing_paper", lambda bm: L.bm_box(bm, (0, 0, 0), (0.24, 0.006, 0.3)), R.SOLID["nour"],
         lambda t, S: ((S["nour"].joint("lwrist") + S["nour"].joint("rwrist")) / 2 + Vector((0, 0.01, 0.06)), None))
    Cam("CAM_A_0-5s_CU-adam-from-behind", 0, 5, tuple(off + Vector((-0.05, -0.55, 1.12))), tuple(P["dl"] + Vector((0, 0.05, 1.1))), F47, hand="gentle")
    Cam("CAM_B_5-8s_POV-adam", 5, 8, tuple(off + Vector((-0.2, 0.0, 1.12))), tuple(P["rl"] + Vector((-0.05, 0.2, 0.92))), F63, hand="gentle")


@run("G35", 5)
def g35():
    off = build_car()
    P = car_people(off)
    Track("adam", [K(0, tuple(P["dl"]), 0, drive(P, "wheel"))])
    Track("nour", [K(0, tuple(P["rl"]), 0, nour_paper(P))])
    ah = tuple(P["dl"] + Vector((0, 0, 1.12)))
    Track("layla", [K(0.0, tuple(P["pl"]), 0, layla_seat(P, look=ah, hpitch=-8)), K(0.5, tuple(P["pl"]), 0, layla_seat(P, look=ah)),
                    K(0.9, tuple(P["pl"]), 0, layla_seat(P, look=tuple(off + Vector((0, 30, 1.0)))))])
    truck(((off.x - 1.2, 70, 0), (off.x - 0.2, 6.5, 0)), 0, 4.3)
    Cam("CAM_A_0-2.5s_CU-layla", 0, 2.5, tuple(off + Vector((-0.12, 0.2, 1.08))), tuple(P["pl"] + Vector((0, 0, 1.1))), F63, hand="gentle")
    Cam("CAM_B_2.5-5s_through-windshield", 2.5, 5, tuple(off + Vector((0.0, -0.3, 1.15))), tuple(off + Vector((0, 20, 1.1))), F63, hand="rough")


# ====================================================================== LANDING
@run("G23", 4)
def g23():
    build_apartment(dict(table="dinner"))
    mat = (12.15, 5.3, 0.02)
    hold = dict(lhand=(12.15, 5.18, 0.95), rhand=(12.15, 5.42, 0.95))
    low = dict(lhand=(12.05, 5.18, 0.1), rhand=(12.05, 5.42, 0.1))
    m = Track("mona", [K(0.0, (12.42, 5.3), 90, stand(0.95, **hold)), K(0.6, (12.42, 5.3), 90, stand(0.95, **hold)),
                       K(1.6, (12.42, 5.3), 90, crouch(pelvis=(0, -0.1, 0.45), lean=30, **low)),
                       K(2.2, (12.42, 5.3), 90, crouch(pelvis=(0, -0.1, 0.45), lean=30, **low)),
                       K(2.8, (12.45, 5.32), 20, stand(0.95)),
                       K(4.0, (13.3, 6.1), -40, walking(0.95), ease="lin")])
    Prop("dish_new", lambda bm: L.bm_box(bm, (0, 0, 0), (0.3, 0.22, 0.06)), R.SOLID["mona"],
         phases((1.6, R.mid_hands("mona", (0, 0, 0))), (99, static(mat, 90))))
    Cam("CAM_A_0-4s_floor-level", 0, 4, (12.95, 7.0, 0.28), (12.15, 5.3, 0.3), F63)
    return m


@run("G48", 11)
def g48():
    build_apartment(dict(table="drawing", bag=False, living_curtains="open", front_door=90, landing_dish=True))
    fd_open = bpy.data.objects["front_door"]
    fd_shut = L.door_slab("front_door_shut", (12.0 - 0.03, 5.75), 0.9, 0, (0, -1))
    vis(fd_shut, [(0, True), (0.8, False)])
    vis(fd_open, [(0, False), (0.8, True)])
    m = Track("mona", [K(0, (12.58, 5.3), 90, stand(0.95, lhand=(12.3, 5.18, 0.98), rhand=(12.3, 5.42, 0.98))),
                       K(2.8, (12.58, 5.3), 90, stand(0.95, lhand=(12.3, 5.18, 0.98), rhand=(12.3, 5.42, 0.98))),
                       K(3.2, (12.58, 5.3), 90, stand(0.95, lhand=(12.3, 5.18, 0.98), rhand=(12.3, 5.42, 0.98), hpitch=6, hroll=4))])
    mh = (12.58, 5.3, 1.55)
    a = Track("adam", [K(0, (11.86, 5.3), -90, stand(look=mh)), K(6.2, (11.86, 5.3), -90, stand(look=mh)),
                       K(6.5, (11.86, 5.3), -90, stand(hpitch=22)), K(7.1, (11.86, 5.3), -90, stand(hpitch=22)),
                       K(7.4, (11.86, 5.3), -90, stand(look=mh)), K(8.6, (11.86, 5.3), -90, stand(look=mh)),
                       K(9.4, (11.86, 5.3), -90, stand(hpitch=14, hroll=6, lean=6))])
    Prop("dish_new", lambda bm: L.bm_box(bm, (0, 0, 0), (0.3, 0.22, 0.06)), R.SOLID["mona"], R.mid_hands("mona", (0, 0, 0)))
    Cam("CAM_A_0-5s_wide-two-shot", 0, 5, (14.25, 6.95, 1.55), (12.25, 5.25, 1.3), F47)
    Cam("CAM_B_5-11s_CU-adam", 5, 11, (13.45, 5.8, 1.62), (11.86, 5.3, 1.6), F29)
    return a, m


# ------------------------------------------------------------------ build one
def build(tag, out_dir):
    fn, dur = RUNS[tag]
    R.reset()
    fn()
    R.run_bake(dur)
    R.look()
    rep = R.report()
    path = os.path.join(out_dir, f"{tag}_blocking_v2.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)
    return path, rep
