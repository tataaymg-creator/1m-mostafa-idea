#!/usr/bin/env python3
"""Rough cut of LOOK (final shot list, see HANDOFF-EDIT.md). Works on the 480p drafts or the 1080p clips (set W, H).
Usage: python3 tools/rough_cut.py SRC_DIR OUT.mp4
SRC_DIR holds G01.mp4 ... named by run id (see favorites.md for the takes)."""
import os, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
work = os.path.join(os.path.dirname(os.path.abspath(out)), "seg"); os.makedirs(work, exist_ok=True)
W, H = 854, 480
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "24",
       "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"]
PILLAR = ""                                                     # everything stays 16:9
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
for r in ["G01", "G03", "G04", "G05", "G06"]: clip(r, r)               # G07 dropped
clip("G08a", "G08", to=1.4)                                        # cut on the sandal buckle click
clip("G09", "G09", crop=False)                                     # flash 1: the seatbelt click
clip("G08b", "G08", ss=3.71)                                       # back on his face: "...Where were we."
# 2 · Hair
clip("G10", "G10"); clip("G11", "G11")
clip("G12", "G12", crop=False, vf="hflip")                         # flash 2, mirrored: Nour always in the back right seat
# 4 · The song & the dance (G13 dropped)
clip("G14", "G14")
clip("G15a", "G15a", crop=False)                                   # radio insert
clip("G15", "G15", ss=2.875, vf="hflip", crop=False)               # flash 3: radio part cut, mirrored so she reads as the passenger
for r in ["G16", "G17", "G18"]: clip(r, r)
# 5 · The knock: one knock shot used twice, graded down for the night
clip("G46_first", "G46")                                           # same grade as the second use
clip("G20", "G20")                                                 # radio off
clip("G22", "G22", to=4.66)                                        # "Shh. We're playing the quiet game."
clip("G21", "G21")                                                 # at the door, Mona through it
# G22 second half ("Who wants dinner?") and G23 dropped: straight to dinner
# 6 · Dinner: spill as a jump cut, flash 4 cut out of G35 inside it
clip("G25a", "G25", to=4.0)
clip("G27", "G34", ss=6.4, to=7.9, crop=False, vf="fade=t=out:st=7.4:d=0.5:c=white")  # headlights flickering in his eyes as he looks at her
clip("G25b", "G25", ss=4.0)
# 7 · Bedtime (G28 dropped)
clip("G29", "G29", to=12.0); clip("G30", "G30")                  # no door-closing wide: straight into "Daddy... look"
# 8 · The road (memory, full frame)
clip("G31", "G31", crop=False); clip("G32", "G32", crop=False)
clip("G33", "G33", crop=False)                                     # final take acc506d2 (draft G33c ce461046): no flip
clip("G34", "G34", crop=False, vf="fade=t=out:st=7.5:d=0.5:c=white")   # the truck fills the glass, cut to white (G35 dropped)
card("white", 1.5, "white"); card("black", 1.5)
clip("G36", "G36", crop=False)
# 8 → 9 · match cut: asphalt full frame, floor in 4:3
clip("G37a", "G37", to=4.125, crop=False); clip("G37b", "G37", ss=4.125)
# 9 · The floor (G38 dropped)
clip("G39", "G39")
# 10 · The bag
for r in ["G40", "G41", "G42b"]: clip(r, r)
# 11 · Daylight: the frame opens from 4:3 to 16:9 across G43
clip("G43", "G43")
clip("G44a", "G44", to=5.9, crop=False); clip("G44b", "G44", ss=7.9, crop=False)   # jump cut after the first button
# 12 · The door
clip("G46", "G46", crop=False)
clip("G47", "G47", to=3.5, crop=False)                             # cut as his hand reaches for the handle
clip("G48", "G48", crop=False)
clip("G49", "G49", crop=False, vf="fade=t=out:st=14.0:d=1.0", af="afade=t=out:st=14.0:d=1.0")   # one take: hug + tilt to the drawing
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
