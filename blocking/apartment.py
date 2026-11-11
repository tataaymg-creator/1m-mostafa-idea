"""LOOK - the grey-box apartment (all rooms on one plan) and the car interior.
See look_set.py for axes and the floor plan."""
import math

from mathutils import Vector

from look_set import (CEIL_FILL, DOOR_H, FLOOR_FILL, H, WT, bm_box, bm_cyl, bm_sphere, box, chair,
                      curtain, door_slab, pendant, set_part, skirting, table, wall, window_frame)

# ------------------------------------------------------------------ fixed positions used by shots
TABLE = dict(x0=1.55, x1=2.45, y0=6.2, y1=7.6)          # dining table, long axis N-S
SEAT_ADAM = (1.12, 6.9)        # west side, facing east (curtains behind him)
SEAT_WIFE = (2.0, 5.83)        # south end, facing north (screen left in the frontal)
SEAT_CHILD = (2.0, 7.97)       # north end, facing south (screen right in the frontal)
SOFA = dict(x0=2.85, x1=4.75, y0=0.5, y1=1.45)          # faces north
SOFA_SEAT_Z = 0.45
SOFA_W, SOFA_MID, SOFA_E = 3.28, 3.8, 4.32              # three seat centres (x)
SOFA_Y = 0.98
ARMCHAIR = (4.25, 2.85)
STAND_WIFE = (0.98, 0.5)       # sewing corner, left stand
STAND_CHILD = (0.48, 0.92)     # right stand, nearer the curtains
HALL_Y = 5.3
FRONT_DOOR_X = 12.0
NOUR_DOOR = (10.0, 10.8)
BED = dict(x0=9.07, x1=10.97, y0=1.67, y1=2.62, top=0.5)
CONSOLE = dict(x0=8.4, x1=9.4, y0=4.67, y1=5.0, h=0.8)


def yaw_deg(dx, dy):
    return math.degrees(math.atan2(dy, dx))


def build_apartment(st=None):
    """st: state of the set at the first frame of the run.
       living_curtains: 'closed' | 'open'
       dining_curtains: 'closed' (always in this film)
       front_door: degrees open (0 closed)
       bag: True while the sealed bag is on the console
       table: 'empty' | 'breakfast' | 'dinner' | 'spilled' | 'knocked' | 'drawing'
       child_chair_turned: True for the sandal shot
       wife_chair_out: chair pulled out at the south end (when the adult is elsewhere)
       stands: 'empty' | 'used'
       landing_dish: True when yesterday's dish is on the mat
    """
    st = dict(st or {})
    # ---------------- floor and ceilings
    box("floor", -0.3, 15.3, -0.3, 9.3, -0.12, 0.0, fill=FLOOR_FILL)
    box("ceiling_main", -0.1, 5.1, -0.1, 9.1, H, H + 0.1, fill=CEIL_FILL)
    box("ceiling_kitchen", 5.0, 8.3, 5.95, 9.1, H, H + 0.1, fill=CEIL_FILL)
    box("ceiling_hall", 5.0, 12.1, 4.55, 6.05, H, H + 0.1, fill=CEIL_FILL)
    box("ceiling_back", 8.2, 12.1, 5.95, 9.1, H, H + 0.1, fill=CEIL_FILL)
    box("ceiling_nour", 8.95, 12.05, 1.55, 4.65, H, H + 0.1, fill=CEIL_FILL)
    box("ceiling_landing", 12.0, 15.1, 2.9, 7.7, 3.3, 3.4, fill=CEIL_FILL)

    # ---------------- walls
    wall("wall_main_W", "y", 0.0, -0.075, 9.075)
    wall("wall_main_S", "x", 0.0, 0.0, 5.0)
    wall("wall_main_N", "x", 9.0, 0.0, 5.0)
    wall("wall_main_E", "y", 5.0, -0.075, 9.075,
         openings=[(4.85, 5.75, DOOR_H, 0.0), (6.45, 7.35, DOOR_H, 0.0)])
    wall("wall_kitchen_N", "x", 9.0, 5.0, 8.2, openings=[(6.0, 6.9, 2.1, 1.05)])
    wall("wall_kitchen_E", "y", 8.2, 6.0, 9.0)
    wall("wall_hall_N", "x", 6.0, 5.0, 12.0, openings=[(6.2, 7.0, DOOR_H, 0.0), (8.6, 9.4, DOOR_H, 0.0)])
    wall("wall_hall_S", "x", 4.6, 5.0, 12.0, openings=[(NOUR_DOOR[0], NOUR_DOOR[1], DOOR_H, 0.0)])
    wall("wall_back_N", "x", 9.0, 8.2, 12.0)
    wall("wall_east", "y", 12.0, 1.525, 9.075, openings=[(4.85, 5.75, DOOR_H + 0.05, 0.0)])
    wall("wall_nour_S", "x", 1.6, 9.0, 12.0)
    wall("wall_nour_W", "y", 9.0, 1.525, 4.6, openings=[(2.95, 3.85, 2.2, 0.95)])
    wall("wall_landing_E", "y", 15.0, 2.925, 7.675, h=3.3)
    wall("wall_landing_S", "x", 3.0, 12.0, 15.0, h=3.3, openings=[(12.5, 13.2, 2.3, 1.2)])
    wall("wall_landing_N", "x", 7.6, 12.0, 15.0, h=3.3)
    wall("wall_landing_W_top", "y", 12.0, 2.925, 7.675, h=3.3, base=H)

    # skirting so the floor line reads in the flat look
    skirting("skirt_main", [(0.09, 0.09), (4.91, 0.09), (4.91, 8.91), (0.09, 8.91), (0.09, 0.09)])
    skirting("skirt_hall", [(5.0, 4.69), (11.91, 4.69), (11.91, 5.91), (5.0, 5.91)])
    skirting("skirt_nour", [(9.09, 1.69), (11.91, 1.69), (11.91, 4.51), (9.09, 4.51), (9.09, 1.69)])
    skirting("skirt_kitchen", [(5.09, 6.09), (8.11, 6.09), (8.11, 8.91), (5.09, 8.91)])

    # ---------------- main room: dining (north half)
    curtain("curtain_dining", "y", 0.075, 5.75, 8.7)
    t = TABLE
    table("dining_table", t["x0"], t["x1"], t["y0"], t["y1"], cloth=0.06)
    chair("chair_adam", SEAT_ADAM[0] - 0.05, SEAT_ADAM[1], -90)
    if st.get("wife_chair_out"):
        chair("chair_wife", SEAT_WIFE[0] + 0.25, SEAT_WIFE[1] - 0.25, 20)
    elif not st.get("no_wife_chair"):
        chair("chair_wife", SEAT_WIFE[0], SEAT_WIFE[1] - 0.04, 0)
    if st.get("child_chair_turned"):
        chair("chair_child", SEAT_CHILD[0], SEAT_CHILD[1] + 0.12, 0)        # turned out, faces north
    else:
        chair("chair_child", SEAT_CHILD[0], SEAT_CHILD[1] + 0.04, 180)
    # the fourth chair stands against the north wall, so the near side of the table stays empty
    chair("chair_spare", 1.0, 8.62, 180)
    box("sideboard", 2.6, 4.2, 8.5, 8.93, 0.0, 0.86)
    box("sideboard_top", 2.57, 4.23, 8.47, 8.95, 0.86, 0.89)
    box("clock", 3.25, 3.55, 8.65, 8.8, 0.89, 1.15)
    box("picture_1", 2.75, 3.15, 8.91, 8.93, 1.45, 1.85)
    box("picture_2", 3.45, 4.0, 8.91, 8.93, 1.4, 1.85)
    pendant("pendant_dining", 2.0, 6.9, H, drop=0.75)
    _table_dressing(st.get("table", "empty"))

    # ---------------- main room: living (south half)
    lc = st.get("living_curtains", "closed")
    if lc == "closed":
        curtain("curtain_living", "y", 0.075, 0.15, 4.35)
    else:
        window_frame("window_living", "y", 0.075, 0.6, 3.9, 0.55, 2.45)
        curtain("curtain_living_a", "y", 0.075, 0.15, 0.6)
        curtain("curtain_living_b", "y", 0.075, 3.9, 4.35)
    _sofa()
    table("coffee_table", 3.3, 4.3, 1.8, 2.35, h=0.45, top=0.05)
    box("rug", 2.65, 4.95, 1.55, 3.4, 0.0, 0.012)
    _armchair(*ARMCHAIR, yaw=yaw_deg_fig(SOFA_MID - ARMCHAIR[0], SOFA_Y - ARMCHAIR[1]))
    set_part("floor_lamp", lambda bm: (bm_cyl(bm, (2.62, 0.32, 0.0), (2.62, 0.32, 0.03), 0.16),
                                        bm_cyl(bm, (2.62, 0.32, 0.03), (2.62, 0.32, 1.45), 0.02, seg=8),
                                        bm_cyl(bm, (2.62, 0.32, 1.38), (2.62, 0.32, 1.68), 0.27, r2=0.17)))
    box("bookshelf", 4.62, 4.93, 2.25, 3.2, 0.0, 1.85)
    box("picture_living_1", 4.91, 4.93, 3.4, 3.85, 1.45, 1.9)
    pendant("pendant_living", 3.2, 2.6, H, drop=0.45)

    # sewing corner (south-west)
    box("sewing_table", 1.6, 2.5, 0.08, 0.6, 0.72, 0.76)
    for lx in (1.64, 2.46):
        for ly in (0.12, 0.56):
            box(f"sewing_leg_{lx}_{ly}", lx - 0.025, lx + 0.025, ly - 0.025, ly + 0.025, 0.0, 0.72)
    box("sewing_machine", 1.85, 2.25, 0.2, 0.42, 0.76, 1.02)
    chair("sewing_chair", 2.02, 0.92, 180)
    box("fabric_shelf_1", 1.45, 2.65, 0.08, 0.32, 1.85, 1.88)
    box("fabric_shelf_2", 1.45, 2.65, 0.08, 0.32, 2.2, 2.23)
    set_part("mirror", lambda bm: bm_box(bm, (1.3, 0.14, 0.95), (0.45, 0.04, 1.85),
                                         rot=_rx(-8)))
    for (sx, sy), hh in ((STAND_WIFE, 1.62), (STAND_CHILD, 1.1)):
        nm = f"stand_{sx}"
        set_part(nm, lambda bm, sx=sx, sy=sy, hh=hh: (bm_cyl(bm, (sx, sy, 0.0), (sx, sy, 0.025), 0.17),
                                                      bm_cyl(bm, (sx, sy, 0.025), (sx, sy, hh), 0.015, seg=8)))

    # ---------------- kitchen
    box("k_sink_unit", 7.58, 8.13, 7.98, 8.92, 0.0, 0.9)
    box("k_stove", 7.55, 8.13, 7.3, 7.95, 0.0, 0.92)
    box("k_stove_back", 8.02, 8.13, 7.3, 7.95, 0.92, 1.15)
    box("k_pot", 7.7, 7.92, 7.45, 7.67, 0.92, 1.05)
    box("k_counter", 7.55, 8.13, 6.07, 7.25, 0.0, 0.9)
    box("k_radio_shelf", 7.9, 8.13, 6.3, 7.1, 1.6, 1.64)
    box("k_radio", 7.95, 8.1, 6.55, 6.9, 1.64, 1.86)
    box("k_wall_cabinet", 7.75, 8.13, 7.95, 8.85, 1.55, 2.25)
    curtain("k_curtain", "x", 8.925, 6.0, 6.9, z0=1.05, z1=2.1, depth=0.05)
    box("k_stool", 6.0, 6.32, 8.4, 8.72, 0.0, 0.62)
    pendant("k_bulb", 6.7, 7.5, H, drop=0.85, r=0.05)
    # glazed door kitchen <-> hall (closed)
    door_slab("door_kitchen_hall", (6.2, 6.0), 0.8, 0, (1, 0))

    # ---------------- hallway
    box("console", CONSOLE["x0"], CONSOLE["x1"], CONSOLE["y0"], CONSOLE["y1"], CONSOLE["h"] - 0.04, CONSOLE["h"])
    for lx in (CONSOLE["x0"] + 0.03, CONSOLE["x1"] - 0.03):
        for ly in (CONSOLE["y0"] + 0.03, CONSOLE["y1"] - 0.03):
            box(f"console_leg_{lx}_{ly}", lx - 0.02, lx + 0.02, ly - 0.02, ly + 0.02, 0.0, CONSOLE["h"] - 0.04)
    box("hall_mirror", 8.55, 9.25, 4.68, 4.71, 1.25, 1.95)
    box("mail", 8.9, 9.25, 4.72, 4.95, 0.8, 0.86)
    box("plant_pot", 8.48, 8.66, 4.72, 4.9, 0.8, 0.98)
    if st.get("bag", True):
        box("bag", 8.75, 9.1, 4.75, 4.97, 0.8, 0.84)
    box("coat_hooks", 10.9, 11.4, 5.91, 5.93, 1.6, 1.68)
    door_slab("door_hall_back", (8.6, 6.0), 0.8, 25, (1, 0))
    fd = st.get("front_door", 0)
    # front door hinged on the north jamb, opens inward (into the hall)
    door_slab("front_door", (FRONT_DOOR_X - 0.03, 5.75), 0.9, -fd, (0, -1))
    pendant("pendant_hall", 8.5, HALL_Y, H, drop=0.4)

    # ---------------- Nour's room
    b = BED
    box("bed_base", b["x0"], b["x1"], b["y0"], b["y1"], 0.15, 0.3)
    box("bed_mattress", b["x0"] + 0.02, b["x1"] - 0.02, b["y0"] + 0.02, b["y1"] - 0.02, 0.3, 0.44)
    box("bed_head", b["x0"] - 0.04, b["x0"] + 0.01, b["y0"], b["y1"], 0.0, 0.95)
    box("bed_foot", b["x1"] - 0.01, b["x1"] + 0.04, b["y0"], b["y1"], 0.0, 0.72)
    box("bed_pillow", b["x0"] + 0.05, b["x0"] + 0.45, b["y0"] + 0.1, b["y1"] - 0.1, 0.44, 0.55)
    box("nightstand", 9.08, 9.52, 2.72, 3.15, 0.0, 0.6)
    set_part("night_light", lambda bm: bm_sphere(bm, (9.3, 2.93, 0.62), (0.09, 0.09, 0.08)))
    curtain("curtain_nour", "y", 9.075, 2.85, 3.95, z0=0.9, z1=2.25, depth=0.06)
    table("nour_desk", 9.1, 9.75, 3.95, 4.5, h=0.58, top=0.04)
    chair("nour_chair", 9.42, 3.7, 0, seat=0.32, w=0.32)
    box("nour_shelf", 9.08, 9.3, 3.9, 4.5, 1.5, 1.53)
    set_part("nour_rug", lambda bm: bm_cyl(bm, (10.3, 3.35, 0.0), (10.3, 3.35, 0.012), 0.42, seg=24))
    for i, (yy, zz) in enumerate(((1.9, 1.5), (2.3, 1.55), (1.95, 1.15), (2.35, 1.15))):
        box(f"scribble_{i}", 9.95 + i * 0.32, 10.2 + i * 0.32, 1.67, 1.68, zz, zz + 0.28)
    door_slab("door_nour", (NOUR_DOOR[0], 4.6), 0.78, -90, (1, 0))

    # ---------------- landing
    if st.get("landing_dish"):
        box("dish_yesterday", 12.3, 12.6, 5.6, 5.82, 0.012, 0.07)
    box("doormat", 12.1, 12.65, 4.95, 5.65, 0.0, 0.015)
    for i in range(12):
        y1 = 6.9 - i * 0.28
        box(f"stair_{i}", 13.75, 14.95, y1 - 0.28, y1, 0.0, 0.17 * (i + 1))
    set_part("railing", lambda bm: (bm_cyl(bm, (13.72, 7.1, 1.0), (13.72, 3.55, 3.04), 0.03),
                                     bm_cyl(bm, (13.72, 7.1, 0.0), (13.72, 7.1, 1.0), 0.025)))
    for i in range(0, 12, 2):
        y1 = 6.9 - i * 0.28
        set_part(f"baluster_{i}", lambda bm, y1=y1, i=i: bm_cyl(bm, (13.72, y1 - 0.14, 0.17 * (i + 1)),
                                                                 (13.72, y1 - 0.14, 0.17 * (i + 1) + 0.95), 0.012, seg=6))
    pendant("pendant_landing", 13.0, 5.3, 3.3, drop=0.5, r=0.18)


def _rx(deg):
    from mathutils import Euler
    return Euler((math.radians(deg), 0, 0)).to_matrix()


def yaw_deg_fig(dx, dy):
    return math.degrees(math.atan2(-dx, dy))


def _sofa():
    s = SOFA

    def build(bm):
        bm_box(bm, ((s["x0"] + s["x1"]) / 2, (s["y0"] + s["y1"]) / 2, 0.21), (s["x1"] - s["x0"], s["y1"] - s["y0"], 0.32))
        bm_box(bm, ((s["x0"] + s["x1"]) / 2, s["y0"] + 0.12, 0.62), (s["x1"] - s["x0"], 0.24, 0.5))
        for x in (s["x0"] + 0.1, s["x1"] - 0.1):
            bm_box(bm, (x, (s["y0"] + s["y1"]) / 2, 0.5), (0.2, s["y1"] - s["y0"], 0.26))
        for cx in (SOFA_W, SOFA_MID, SOFA_E):
            bm_box(bm, (cx, s["y0"] + 0.62, SOFA_SEAT_Z - 0.04), (0.5, 0.7, 0.08))
        for xx in (s["x0"] + 0.06, s["x1"] - 0.06):
            for yy in (s["y0"] + 0.06, s["y1"] - 0.06):
                bm_box(bm, (xx, yy, 0.025), (0.05, 0.05, 0.05))
    set_part("sofa", build)


def _armchair(x, y, yaw):
    from mathutils import Euler
    r = Euler((0, 0, math.radians(yaw))).to_matrix()

    def P(lx, ly, lz):
        return Vector((x, y, 0)) + r @ Vector((lx, ly, lz))

    def build(bm):
        bm_box(bm, P(0, 0.02, 0.3), (0.62, 0.6, 0.22), r)
        bm_box(bm, P(0, -0.3, 0.62), (0.62, 0.14, 0.7), r)
        for sx in (-1, 1):
            bm_box(bm, P(sx * 0.33, 0.0, 0.55), (0.07, 0.62, 0.05), r)
            bm_box(bm, P(sx * 0.33, 0.25, 0.37), (0.05, 0.05, 0.36), r)
        for sx in (-1, 1):
            for sy in (-1, 1):
                bm_box(bm, P(sx * 0.28, sy * 0.25, 0.1), (0.05, 0.05, 0.2), r)
    set_part("armchair", build)


def _table_dressing(state):
    """Plates, forks, cup and food as they stand at the first frame of the run."""
    from look_set import prop_cup, prop_fork, prop_plate
    if state == "empty":
        return
    z = 0.755
    food = state in ("breakfast", "dinner", "spilled", "knocked")
    if state in ("set", "breakfast", "dinner", "spilled", "knocked"):
        prop_plate("plate_adam", 1.78, 6.9, z, food=food)
        prop_plate("plate_wife", 2.0, 6.42, z, food=food)
        prop_plate("plate_child", 2.0, 7.4, z, r=0.1, food=food)
        prop_fork("fork_adam", 1.78, 7.08, z)
        prop_fork("fork_wife", 2.17, 6.42, z)
        prop_fork("fork_child", 2.14, 7.4, z)
    if state in ("set", "breakfast", "dinner", "spilled"):
        prop_cup("cup", 2.22, 7.42, z)
    if state == "spilled":
        box("water_on_cloth", 2.05, 2.5, 7.25, 7.62, z, z + 0.003)
    if state == "knocked":
        box("water_on_cloth", 2.0, 2.5, 7.0, 7.62, z, z + 0.003)
        prop_cup("cup", 2.3, 7.08, z, on_side=True, yaw=-35)
    if state in ("dinner", "spilled"):
        set_part("water_jug", lambda bm: bm_cyl(bm, (1.8, 7.22, z), (1.8, 7.22, z + 0.22), 0.06, seg=14, r2=0.05))
    if state == "drawing":
        prop_cup("cup", 2.3, 6.32, z)
        set_part("drawing", lambda bm: bm_box(bm, (2.22, 6.32, z + 0.13), (0.03, 0.3, 0.22), rot=_ry(-14)))


def _ry(deg):
    from mathutils import Euler
    return Euler((0, math.radians(deg), 0)).to_matrix()


# ====================================================================== car
CAR = dict(driver=(-0.37, 0.0), passenger=(0.37, 0.0), rear_right=(0.38, -0.88))
SEAT_Z_FRONT = 0.38
SEAT_Z_REAR = 0.40
WHEEL_C = Vector((-0.37, 0.43, 0.83))


def build_car():
    box("ground", -150, 150, -150, 300, -0.02, 0.0, fill=FLOOR_FILL)
    # road strip and centre dashes, to read the direction of travel
    box("road", -3.5, 3.5, -40, 300, 0.0, 0.004)
    for i in range(40):
        y0 = 4 + i * 7
        box(f"dash_{i}", -1.82, -1.72, y0, y0 + 3, 0.004, 0.008)
    off = Vector((1.8, 0, 0))      # car drives in the right-hand lane

    def B(name, x0, x1, y0, y1, z0, z1):
        return box(name, x0 + off.x, x1 + off.x, y0, y1, z0, z1)

    B("car_floor", -0.74, 0.74, -1.5, 1.05, 0.10, 0.17)
    B("car_roof", -0.72, 0.72, -1.05, 0.62, 1.32, 1.38)
    B("car_dash", -0.72, 0.72, 0.72, 1.05, 0.5, 0.88)
    B("car_dash_top", -0.72, 0.72, 0.8, 1.15, 0.86, 0.9)
    B("car_hood", -0.8, 0.8, 1.15, 2.3, 0.62, 0.86)
    B("car_trunk", -0.8, 0.8, -2.3, -1.5, 0.62, 0.9)
    B("car_rear_shelf", -0.7, 0.7, -1.48, -1.15, 0.86, 0.9)
    B("car_console", -0.1, 0.1, 0.0, 0.72, 0.17, 0.42)
    for sx in (-1, 1):
        B(f"car_door_{sx}", sx * 0.74 - 0.03, sx * 0.74 + 0.03, -1.45, 1.05, 0.17, 0.86)
        B(f"car_sill_{sx}", sx * 0.74 - 0.05, sx * 0.74 + 0.05, -1.5, 1.05, 0.0, 0.17)
        set_part(f"car_pillars_{sx}", lambda bm, sx=sx: (
            bm_cyl(bm, off + Vector((sx * 0.70, 1.0, 0.88)), off + Vector((sx * 0.66, 0.6, 1.33)), 0.035),
            bm_cyl(bm, off + Vector((sx * 0.72, -0.38, 0.86)), off + Vector((sx * 0.70, -0.38, 1.33)), 0.05),
            bm_cyl(bm, off + Vector((sx * 0.70, -1.05, 1.33)), off + Vector((sx * 0.72, -1.48, 0.88)), 0.05)))
        # wheels outside, for the exterior read
        for wy in (1.55, -1.45):
            set_part(f"car_wheel_{sx}_{wy}", lambda bm, sx=sx, wy=wy: bm_cyl(
                bm, off + Vector((sx * 0.72, wy, 0.3)), off + Vector((sx * 0.86, wy, 0.3)), 0.3, seg=18))
    for nm, (sx, sy) in (("car_seat_driver", CAR["driver"]), ("car_seat_passenger", CAR["passenger"])):
        set_part(nm, lambda bm, sx=sx, sy=sy: (
            bm_box(bm, off + Vector((sx, sy + 0.02, SEAT_Z_FRONT - 0.06)), (0.5, 0.5, 0.12)),
            bm_box(bm, off + Vector((sx, sy - 0.27, 0.68)), (0.5, 0.1, 0.62), rot=_rx(-12)),
            bm_box(bm, off + Vector((sx, sy - 0.31, 0.98)), (0.24, 0.08, 0.12), rot=_rx(-12))))
    set_part("car_rear_bench", lambda bm: (
        bm_box(bm, off + Vector((0, -0.75, SEAT_Z_REAR - 0.06)), (1.36, 0.48, 0.12)),
        bm_box(bm, off + Vector((0, -1.08, 0.7)), (1.36, 0.1, 0.62), rot=_rx(-14))))
    for i in range(14):
        a0 = 2 * math.pi * i / 14
        a1 = 2 * math.pi * (i + 1) / 14

        def ring(bm, a0=a0, a1=a1):
            r = 0.19
            tilt = _rx(-62)
            p0 = WHEEL_C + off + tilt @ Vector((r * math.cos(a0), r * math.sin(a0), 0))
            p1 = WHEEL_C + off + tilt @ Vector((r * math.cos(a1), r * math.sin(a1), 0))
            bm_cyl(bm, p0, p1, 0.016, seg=6)
        set_part(f"car_wheelrim_{i}", ring)
    set_part("car_column", lambda bm: bm_cyl(bm, WHEEL_C + off, off + Vector((-0.37, 0.75, 0.7)), 0.035))
    set_part("car_gear", lambda bm: (bm_cyl(bm, off + Vector((0, 0.42, 0.42)), off + Vector((0, 0.45, 0.6)), 0.012, seg=6),
                                      bm_sphere(bm, off + Vector((0, 0.45, 0.62)), (0.03, 0.03, 0.03))))
    B("car_mirror", -0.11, 0.11, 0.55, 0.58, 1.18, 1.25)
    for sx in (-1, 1):
        B(f"car_visor_{sx}", sx * 0.37 - 0.2, sx * 0.37 + 0.2, 0.42, 0.6, 1.3, 1.32)
    # swim ring on the rear shelf
    set_part("car_swim_ring", lambda bm: bm_sphere(bm, off + Vector((0.3, -1.3, 1.0)), (0.22, 0.06, 0.16)))
    return off
