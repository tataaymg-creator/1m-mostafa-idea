#!/usr/bin/env python3
"""Rough cut of LOOK from the 480p drafts (no credits).
Usage: python3 tools/rough_cut.py SRC_DIR OUT.mp4
SRC_DIR holds G01.mp4 ... named by run id (see favorites.md for the takes)."""
import os, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
work = os.path.join(os.path.dirname(os.path.abspath(out)), "seg"); os.makedirs(work, exist_ok=True)
W, H = 854, 480
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "24",
       "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]
PILLAR = f"crop=640:480:107:0,pad={W}:{H}:107:0:black"          # 4:3 from the centre
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_AR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
segs = []

def clip(name, run, ss=0.0, to=None, vf="", af="", crop=True):
    p = os.path.join(work, f"{len(segs):02d}_{name}.mp4")
    v = ",".join(x for x in [vf, PILLAR if crop else ""] if x) or "null"
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(ss)] + (["-to", str(to)] if to else []) + \
          ["-i", os.path.join(src, run + ".mp4"), "-vf", v + ",setsar=1", "-af", (af or "anull")] + ENC + [p]
    subprocess.run(cmd, check=True); segs.append(p)

def card(name, dur, color="black", vf=""):
    p = os.path.join(work, f"{len(segs):02d}_{name}.mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color={color}:s={W}x{H}:r=24:d={dur}",
           "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", str(dur),
           "-vf", (vf or "null") + ",setsar=1"] + ENC + [p]
    subprocess.run(cmd, check=True); segs.append(p)

# 1 · Morning
card("open_black", 2)
for r in ["G01", "G03", "G04", "G05", "G06", "G07", "G08"]: clip(r, r)
clip("G09", "G09", crop=False)                                     # flash 1
# 2 · Hair
clip("G10", "G10"); clip("G11", "G11")
clip("G12", "G12", crop=False)                                     # flash 2
# 4 · The song & the dance (G13 dropped)
clip("G14", "G14")
clip("G15a", "G15a", crop=False)                                   # radio insert
clip("G15", "G15", ss=2.875, vf="hflip", crop=False)               # flash 3: radio part cut, mirrored so she reads as the passenger
for r in ["G16", "G17", "G18"]: clip(r, r)
# 5 · The knock: one knock shot used twice, graded down for the night
clip("G46_night", "G46", vf="eq=brightness=-0.12:saturation=0.8:gamma=0.85")
for r in ["G20", "G21", "G22", "G23"]: clip(r, r)
# 6 · Dinner: spill as a jump cut, flash 4 cut out of G35 inside it
clip("G25a", "G25", to=4.0)
clip("G27a", "G35", ss=0.0, to=1.4, crop=False)
clip("G27b", "G35", ss=2.8, to=3.9, crop=False, vf="fade=t=out:st=3.4:d=0.5:c=white")
clip("G25b", "G25", ss=4.0)
# 7 · Bedtime (G28 dropped)
clip("G29", "G29"); clip("G30", "G30")
# 8 · The road (memory, full frame)
for r in ["G31", "G32", "G33", "G34", "G35"]: clip(r, r, crop=False)
card("white", 1.5, "white"); card("black", 1.5)
clip("G36", "G36", crop=False)
# 8 → 9 · match cut: asphalt full frame, floor in 4:3
clip("G37a", "G37", to=4.125, crop=False); clip("G37b", "G37", ss=4.125)
# 9 · The floor (G38 dropped)
clip("G39", "G39")
# 10 · The bag
for r in ["G40", "G41", "G42b"]: clip(r, r)
# 11 · Daylight: the frame opens from 4:3 to 16:9 across G43
def g43():
    # the frame opens from 4:3 to 16:9: two black bars slide out between 1 s and 5 s
    p = os.path.join(work, f"{len(segs):02d}_G43.mp4")
    k = "max(0\\,min(1\\,(t-1)/4))"
    fc = (f"color=black:s=107x{H}:r=24[b1];color=black:s=107x{H}:r=24[b2];"
          f"[0:v][b1]overlay=x='-107*{k}':y=0:eval=frame:shortest=1[v1];"
          f"[v1][b2]overlay=x='747+107*{k}':y=0:eval=frame:shortest=1,setsar=1[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(src, "G43.mp4"), "-filter_complex", fc,
                    "-map", "[v]", "-map", "0:a"] + ENC + [p], check=True)
    segs.append(p)
g43()
clip("G44", "G44", crop=False)
# 12 · The door
clip("G46", "G46", crop=False)
for r in ["G47", "G48", "G49k"]: clip(r, r, crop=False)
clip("G49z", "G49z", to=6.0, crop=False, vf="fade=t=out:st=5.0:d=1.0", af="afade=t=out:st=5.0:d=1.0")
card("black_end", 1)
card("title", 4, vf=f"drawtext=fontfile={FONT}:text='LOOK':fontcolor=white:fontsize=64:x=(w-tw)/2:y=(h-th)/2-24,"
                    f"drawtext=fontfile={FONT_AR}:text='بُصّ':text_shaping=1:fontcolor=white@0.8:fontsize=40:x=(w-tw)/2:y=(h/2)+40,"
                    "fade=t=in:st=0:d=0.6,fade=t=out:st=3.3:d=0.7")
card("quote", 5, vf=f"drawtext=fontfile={FONT}:text='Grief is love that keeps setting the table.':fontcolor=white:fontsize=30:x=(w-tw)/2:y=(h-th)/2,"
                    "fade=t=in:st=0:d=0.8,fade=t=out:st=4.2:d=0.8")
lst = os.path.join(work, "list.txt")
open(lst, "w").write("".join(f"file '{p}'\n" for p in segs))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", out], check=True)
print(out)
