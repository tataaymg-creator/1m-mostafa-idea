"""Exact perspective blocking of Nour's bedroom (metres), drawn with PIL.
Camera at the entrance, facing the back wall, pitched down a few degrees.
Output: locations/L06_blocking.png  (geometry reference for the plate)."""
import math
from PIL import Image, ImageDraw
W, H = 1344, 756
FOV, PITCH = 66.0, -8.0
f = (W / 2) / math.tan(math.radians(FOV / 2))
CAM = (0.2, 1.3, -0.4)
cp, sp = math.cos(math.radians(PITCH)), math.sin(math.radians(PITCH))
def cam(p):
    X, Y, Z = p[0]-CAM[0], p[1]-CAM[1], p[2]-CAM[2]
    return X, Y*cp - Z*sp, Y*sp + Z*cp          # pitch about x
def P(p):
    X, Y, Z = cam(p)
    return (W/2 + f*X/Z, H/2 - f*Y/Z)
L, R, B, F, TOP = -1.8, 1.8, 4.6, 0.6, 2.7
img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
EDGE = (35, 35, 35)
def poly(pts, col, w=2):
    q = [P(p) for p in pts]
    d.polygon(q, fill=col); d.line(q + [q[0]], fill=EDGE, width=w)
# room shell
poly([(L,0,B),(R,0,B),(R,TOP,B),(L,TOP,B)], (206,216,196))   # back wall
poly([(L,0,F),(L,0,B),(L,TOP,B),(L,TOP,F)], (184,197,174))   # left wall
poly([(R,0,F),(R,0,B),(R,TOP,B),(R,TOP,F)], (184,197,174))   # right wall
poly([(L,0,F),(R,0,F),(R,0,B),(L,0,B)], (222,215,200))       # floor
poly([(L,TOP,F),(R,TOP,F),(R,TOP,B),(L,TOP,B)], (236,233,223))
for i in range(1, 8):  # floor grid 0.5 m
    x = L + i*0.5; d.line([P((x,0,F)), P((x,0,B))], fill=(192,185,170), width=1)
for k in range(1, 9):
    z = F + k*0.5
    if z < B: d.line([P((L,0,z)), P((R,0,z))], fill=(192,185,170), width=1)
# wall openings / flat items
e = 0.003
poly([(-0.3,1.0,B-e),(0.9,1.0,B-e),(0.9,2.15,B-e),(-0.3,2.15,B-e)], (150,150,134))        # window
poly([(R-e,0,1.6),(R-e,0,2.5),(R-e,2.1,2.5),(R-e,2.1,1.6)], (96,70,50))                     # door (right wall)
for (x0,x1,y0,y1) in [(-1.55,-1.05,1.45,1.85),(-0.95,-0.5,1.5,1.85),(-1.5,-1.1,0.95,1.3),(-0.95,-0.6,1.0,1.3)]:
    poly([(x0,y0,B-e),(x1,y0,B-e),(x1,y1,B-e),(x0,y1,B-e)], (245,240,225), 1)              # drawings above bed
# solid boxes with back-face culling, sorted far -> near
objs = []
def box(x0,x1,y0,y1,z0,z1,col):
    objs.append(((x0+x1)/2, (y0+y1)/2, (z0+z1)/2, (x0,x1,y0,y1,z0,z1), col))
B0 = B
box(L, L+0.95, 0.0, 1.05, B0-0.06, B0, (105,72,48))          # headboard
box(L, L+0.95, 0.28, 0.55, B0-2.0, B0-0.06, (205,160,160))   # mattress + blanket
box(L, L+0.95, 0.0, 0.28, B0-2.0, B0-0.06, (120,84,58))      # bed frame base
box(L, L+0.95, 0.0, 0.72, B0-2.06, B0-2.0, (105,72,48))      # footboard
box(L+1.0, L+1.48, 0.0, 0.62, B0-0.42, B0, (120,86,60))      # bedside table
box(0.85, 1.75, 0.62, 0.67, B0-0.58, B0, (132,96,66))        # desk top
for lx in (0.88, 1.68):
    for lz in (B0-0.55, B0-0.06):
        box(lx, lx+0.05, 0.0, 0.62, lz, lz+0.05, (110,80,55))  # desk legs
box(1.05, 1.45, 0.38, 0.42, B0-1.0, B0-0.62, (132,96,66))    # chair seat
box(1.05, 1.45, 0.42, 0.85, B0-1.0, B0-0.96, (132,96,66))    # chair back
for lx in (1.06, 1.40):
    for lz in (B0-1.0, B0-0.67):
        box(lx, lx+0.04, 0.0, 0.38, lz, lz+0.04, (110,80,55))
box(0.85, 1.75, 1.45, 1.49, B0-0.22, B0, (108,78,54))        # shelf
def draw_box(b, col):
    x0,x1,y0,y1,z0,z1 = b
    k = lambda c, s: tuple(int(v*s) for v in c)
    faces = [([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)], (0,1,0), 1.0),
             ([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)], (0,0,-1), 0.82),
             ([(x1,y0,z0),(x1,y0,z1),(x1,y1,z1),(x1,y1,z0)], (1,0,0), 0.68),
             ([(x0,y0,z0),(x0,y0,z1),(x0,y1,z1),(x0,y1,z0)], (-1,0,0), 0.68)]
    for pts, n, s in faces:
        c = [sum(p[i] for p in pts)/4 for i in range(3)]
        v = [CAM[i]-c[i] for i in range(3)]
        if sum(n[i]*v[i] for i in range(3)) > 0:
            poly(pts, k(col, s))
for cx, cy, cz, b, col in sorted(objs, key=lambda o: -math.dist((o[0],o[1],o[2]), CAM)):
    draw_box(b, col)
# rug
cx, cz, r = 0.3, 3.0, 0.55
d.polygon([P((cx+r*math.cos(t*math.pi/18), 0.003, cz+r*math.sin(t*math.pi/18))) for t in range(36)], fill=(192,160,150), outline=EDGE)
img.save("locations/L06_blocking.png"); print("ok")
