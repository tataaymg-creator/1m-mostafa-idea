# LOOK — blocking (.blend)

These are grey-box position and camera references for the Seedance runs. They carry **geometry only**: where everyone is, which way they face and where the camera stands. Faces, clothes, light and colour still come from the character and location elements.

All the rooms share one floor plan, so a figure stays in the same place from run to run. Each file shows the **first frame of its run**, with everything the earlier runs changed still in place (see the state column below).

## Colour key

Fill is white and the outline carries the colour.

| Outline | Figure | Element |
|---|---|---|
| blue | Adam (also Adam in the memory) | `adam`, `adam-before` |
| red | adult mannequin, and its loose arm | `doll-wife` |
| yellow | child mannequin | `doll-daughter` |
| purple | Layla | `layla` |
| orange | Nour | `nour` |
| green | Mona | `mona` |
| grey | set and loose props | — |

A prop a figure is holding takes that figure's colour: the sandal, brush, sleeve, Nour's book and drawing, and Mona's dish. Every head has a small nose and two eye bumps, so you can tell which way it faces. Nothing in the scene has text, numbers or labels.

## Viewport render

1. Open a file. The 3D view is already looking through the active camera, in flat white with outlines and backface culling on.
2. View > Viewport Render Image. The output is 1280×720, 16:9.
3. Some files have extra cameras for other angles in the same run, with the figures in the same positions. Select one and press Ctrl+Numpad 0 to make it active. The outline weight is set for the active camera.

Upload each image to **baba look** under the file's tag, for example `B05a_living-wide_G10`.

## Rebuilding

```bash
blender -b -P build_all.py
```

```bash
blender -b -P blocking_B05a_living-wide_G10_v1.py
```

`look_set.py` holds the mannequins, cameras and look, `apartment.py` the apartment and the car, and `shots.py` every setup. The files were built with Blender 5.2 LTS. On Blender 4.x, run the scripts to rebuild them rather than opening the 5.2 files.

## Lenses = the seedance-clean FOV table

Every camera uses one of the skill's fields of view, so the rewritten prompts can quote the blocking camera exactly (36 mm sensor, horizontal FOV):

| FOV | Lens | Used for |
|---|---|---|
| 84° | 20.0 mm | car interior from the back seat |
| 63° | 29.4 mm | wides, room masters, car close-ups in the tight cabin |
| 47° | 41.4 mm | medium shots and inserts |
| 29° | 69.4 mm | close-ups |

## Floor plan (metres, Z up)

```
 y                      N
 9 +----------+----------------+
   | DINING   |   KITCHEN      |          curtains on the whole west wall (x = 0)
   | sideboard|  stove on east |          dining table: long axis N–S,
   |  [table] =door  wall      |            Adam west side, adult S end, child N end
 6 |          +-------glz------+------------------------+
   |          =door  HALLWAY  ->  console+mirror (S) ...  | FRONT DOOR (x = 12) -> LANDING
 4.6| LIVING  +------------------+--Nour door--+----------+   stairs on the landing's east side
   | armchair  bookshelf (E)     | NOUR'S ROOM            |
   |  [sofa, faces N]            | bed on S wall, head W  |
 0 +sewing corner (SW)----------+-----------------------+
   x=0                    x=5          x=9            x=12
```

## Files

| File | Runs it serves | Camera(s) | State at the first frame |
|---|---|---|---|
| `B01a_dining-frontal_G05` | G05 | wide frontal 63° | breakfast: three plates of toast, forks, yellow cup by the small plate (screen right); Adam seated centre, hands flat |
| `B01b_dining-frontal_G24` | G24 | wide frontal 63°; insert on the cup 47° | dinner: plates of food, glass jug by Adam's hand; Adam leaning on his forearms; the child's left hand on the table edge by the cup |
| `B01c_dining-frontal_G26` | G26 | CU Adam 29° | the cup on its side, water on the cloth; Adam gripping the table edge |
| `B02_dining-kitchen-door_G03` | G03 | wide through the kitchen door 63° | plates laid, both mannequins seated, Adam's chair empty (he walks in at 0.8 s) |
| `B03_dining-side_G25` | G25 | wide side angle 63° | after the overflow: wet cloth, cup upright, jug; Adam seated, head down |
| `B04_dining-chair-sandal_G08` | G08 | low CU on the foot 47°; CU Adam 29° | child's chair at the north end turned to face away from the table; Adam kneeling, holding its right foot and the sandal |
| `B05a_living-wide_G10` | G10 | living-room master 63° | adult in the armchair facing the sofa; Adam behind the armchair carrying the child rigid across his chest |
| `B05b_living-wide_G16` | G16 | living master 63° | child mid-sofa; Adam and the adult in a dance hold in front of the coffee table |
| `B05c_living-wide_G18` | G18 | living master 63° | after the half turn: the adult's empty left shoulder toward camera, the loose arm on the rug at their feet |
| `B05d_living-sofa-edge_G18-s2` | G18 (second shot) | MCU 47° | the adult seated on the sofa's west end, arm off; Adam on his knees, fitting the arm into the socket |
| `B05e_living-wide_G43` | G43 | living master 63° | both mannequins side by side on the sofa (adult screen left); Adam at the closed curtains, a hand on each |
| `B05f_living-wide_G44` | G44 | living master 63° | curtains open; Adam in front of the sofa at screen left, facing the adult |
| `B06a_sofa-two-shot_G11` | G11 | MCU two-shot 29°; CU Adam 29° | child mid-sofa; Adam seated at its screen right, turned to it, brush in his right hand; adult in the armchair off frame left |
| `B06b_sofa-two-shot_G22` | G22 | CU two-shot 29°; CU Adam 29° | child mid-sofa, the adult where G18 left her (sofa west end, off frame); Adam crouched at screen left, finger to his lips |
| `B07a_kitchen_G14` | G14 | MS past the adult's shoulder 47°; CU Adam 29° | adult standing in the kitchen doorway, foreground left; Adam at the stove, spoon in the pot, head turned to the doorway |
| `B07b_kitchen_G20` | G20 | CU Adam 29° | Adam by the counter under the radio shelf (screen right), face turned to the dining-room door (screen left) |
| `B08_sewing-corner_G45` | G45 | sewing-corner master 63° | daylight; adult on the left stand (no wig, bare), child on the right stand (no wig, the dress); Adam between them with the sleeve at the child's shoulder |
| `B09a_hallway_G21` | G21 | hallway master 63° | bag on the console; front door shut; Adam mid-hall, back to camera |
| `B09b_hallway_G40` | G40 | hallway master 63° | bag on the console; Adam entering from behind the camera |
| `B09c_hallway_G47` | G47 | hallway master 63° | no bag; Adam walking to the door |
| `B09d_hallway-from-dining_G49` | G49 | wide from the dining room down the hall 63° | the drawing propped on the yellow cup at the table's corner, foreground left; front door open; Adam in it, head down; Mona on the threshold; both mannequins on their stands in the sewing corner |
| `B10a_nour-room_G29` | G29 | MS from the bed's foot 47° | child on its back in the bed, blanket at its waist, rabbit on the pillow; Adam on the bed edge, leaning in |
| `B10b_nour-room-wide_G29-s3` | G29 (third shot) | Nour's room master 63° | blanket to the chin, rabbit by the shoulder; Adam at the door, hand on the switch |
| `B10c_nour-room-doorway_G30` | G30 | CU profile 29°; CU frontal from the corridor 29° | Adam in the doorway facing the corridor, hand on the frame, mid-step |
| `B10d_nour-room-floor_G38` | G38 | low from the floor 63° | the child's wig slipped sideways, rabbit by the shoulder, nightstand at the head |
| `B10e_nour-room-floor_G39` | G39 | MS 47°; room master 63° | Adam sitting on the floor, back against the bed side, knees up |
| `B11_car-from-back-seat_G32` | G32 (first shot) | from the back seat 84° | Adam driving, right hand on the gearshift under Layla's left hand; Nour behind Layla with the book |
| `B12a_car-back-seat_G09` | G09, G12, G32 | low CU on Nour's legs 63°; CU Nour 63°; CU Nour 47° | Nour back right, belted, book on her knees |
| `B12b_car-back-seat-paper_G33` | G33, G34 | CU Nour from the front 47°; Adam's POV 63° | Nour holding the paper up between the front seats |
| `B13_car-driver-side_G15` | G15, G27, G32, G33, G35 | CU Layla from the driver's side 63°; MCU Adam from the passenger side 63°; Adam from behind his right shoulder 47° | Layla in profile, front right; Adam driving |
| `B14a_landing_G23` | G23 | floor-level insert 63° | Mona on the doormat facing the door, dish in her hands |
| `B14b_landing_G48` | G48 | wide two-shot 47°; CU Adam 29° | yesterday's dish at Mona's feet; Mona with the new dish; door open, Adam in the doorway |

## Decisions and deviations to check

1. **Kitchen door.** It is on the dining room's east wall, facing the curtains, not on the sideboard wall as `L02_dining` seems to show. This is the only layout where G03 works (looking through the kitchen door, the seated figures read in profile against the curtains) and G14 works (looking from the dining room into the kitchen, stove on the back wall).
2. **Fourth dining chair.** It stands against the north wall by the sideboard, so the near side of the table stays empty in every frontal.
3. **Left and right.** Where a prompt says "its right (screen right)" and the two disagree, the screen side wins. In G11 Adam sits at the child's screen right; in G22 he crouches at its screen left. In G11 the child faces the camera rather than showing its profile.
4. **G03.** The first frame has no Adam: he walks in at 0.8 s. His chair is empty.
5. **G14.** The stove is on the kitchen's back wall, so Adam stands three-quarter to the camera with his head turned to the doorway, not fully side-on.
6. **G20.** "Toward the hallway" is read as toward the dining-room door, which is the way to the hall. It lands screen left as written.
7. **Nour's room.** The door sits near the hall's far end on the right (as in G28) and is hinged on its west side. That keeps the open leaf out of the G30 profile close-up.
8. **G38.** The blanket stops just below the neck, and the head end of the body rests a little raised on the pillow. That lets the floor-level camera see the head in profile over the mattress edge.
9. **G39.** Adam is shown seated against the bed, the pose the shot settles in, rather than mid-rise from lying.
10. **G45.** Adam stands between the two stands, on the child's screen-left side, so his step back toward the sewing table is clear.
11. **G48.** The front door is shown open with Adam in it. In the run's actual first frame it is still shut and opens at 0.8 s.
12. **G49.** The adult's dining chair is pulled out from the table so the foreground corner, cup and drawing stay clear.
13. **Not built.** Angles where the figures move to new positions inside a run (G03 second shot, G29 kiss, G44 cardigan close-up) have no separate file. Inserts with no figures (G01, G02, G06, G07, G13, G19, G31, G36, G41, G46) need no blocking, and neither do G04, G17, G28, G37 and G42.
14. **Floor and ceiling tones.** They are light grey rather than white, so room corners still read in the flat look.
15. **Still frames only.** There is no animation and no handheld shake. Each file is a first frame.
