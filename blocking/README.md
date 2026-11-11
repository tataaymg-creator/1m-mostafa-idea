# LOOK — blocking v2 (animated .blend per run)

One `.blend` per run, named after the run (`G10_blocking_v2.blend`). Each file plays the whole run at 24 fps: the figures act on the prompt's timecodes and the camera cuts at the stated points. They are geometry only (who is where, which way they face, where the camera is and how it moves); faces, clothes and light come from the elements. Nothing in the scene has text on it.

v1 (white figures with coloured outlines, single frames) has been removed; it is still in the git history.

## Colour key (solid mannequins, grey set)

| Colour | Figure |
|---|---|
| blue | Adam (also Adam in the memory) |
| red | adult mannequin, its loose arm, the cardigan |
| yellow | child mannequin, its wig, the sandal, the sleeve |
| purple | Layla |
| orange | Nour, her drawing |
| green | Mona, her dish |
| grey | set and loose props |

## How to use

- Open a file and press play. The 3D view is already looking through the camera.
- Each cut is a timeline marker bound to its own camera, named with its segment and timing, for example `CAM_B_6-10s_CU-adam`. Playback switches cameras at the cut.
- Handheld segments have noise on the camera. Present-day shots are locked unless the prompt moves them.
- To make your own playblast, use View > Viewport Render Animation (1280×720, 24 fps).

## Rebuilding

```bash
blender -b -P build_v2.py
```

```bash
blender -b -P build_v2.py -- G10 G16
```

- `runs.py`: every run, with its keys, props and cameras.
- `rig.py`: the animated mannequins, props, cameras, baking and the look.
- `apartment.py`: the apartment and the car.
- `look_set.py`: shared primitives and the pose solver.

The files were built with Blender 5.2 LTS. On 4.x, rebuild them from the scripts.

## Lenses (the seedance-clean FOV table, 36 mm sensor, horizontal)

| FOV | 84° | 63° | 47° | 29° | 18° | 12° |
|---|---|---|---|---|---|---|
| Lens | 20.0 mm | 29.4 mm | 41.4 mm | 69.4 mm | 113.7 mm | 171.3 mm |
| Used for | car from the back seat | wides, room masters, car close-ups | MS, inserts | CU | radio and gearshift inserts | the wig ECU |

## Runs and carried-over state

| Run | Length | Cuts | State and action |
|---|---|---|---|
| G03 | 10 s | 6.0 | Empty plates laid. Adam walks in from the right at 0.8 s and sets a toast plate in front of the adult (2.2 s) and the child (3.4 s), then stands between them. |
| G05 | 6 s | — | Breakfast plates and the cup by the small plate. Adam seated, looks at the child, then the adult at 3.5 s. |
| G08 | 10 s | 5.0 | Child's chair turned out. Adam kneels and buckles the sandal (3.6 s), touches his temple (6.8 s), shakes his head (8.0 s), looks up. |
| G09 | 5 s | 2.5 | Car. Nour's buckle, then her hand smooths the belt; legs swinging. |
| G10 | 5 s | — | Adult in the armchair. Adam carries the child in from the left, sets it mid-sofa (3.0 s), settles its head (4.3 s). |
| G11 | 15 s | 6.0, 10.0 | Brushing; a glance at the armchair (3.0 s); the wig slides off (7.6 s); he puts it back (11–13 s). |
| G12 | 6 s | 3.0 | Car. Layla's hand reaches back to Nour's hair at 4.0 s. |
| G14 | 13 s | 4.0, 9.0 | Adult standing in the kitchen doorway. Radio dial; stirring and swaying; taste at 5.0 s; open hand to the doorway at 11.0 s. |
| G15 | 10 s | 3.0, 7.0 | Car. Layla on the radio, singing, looks at Adam (5.6 s), her hand over his on the gearshift. |
| G16 | 8 s | — | Dance in front of the sofa, a half turn over 8 s; the child mid-sofa. |
| G18 | 10 s | 4.0 | Arm on the rug. Then the adult sits on the sofa's west end; the arm goes back in at 6.6 s; her hand goes to his forehead at 7.8 s. |
| G20 | 5 s | — | Adam frozen by the radio, eyes on the dining-room door; switches the radio off at 2.6 s. |
| G21 | 8 s | — | Bag on the console. Adam mid-hall, back to camera; his head lowers at 6.0 s. |
| G22 | 10 s | 5.0 | Child mid-sofa, the adult on the west end. Finger to his lips (0.8 s), turn toward the hall (5.0 s), back to the child (7.6 s). |
| G23 | 4 s | — | Mona sets the dish on the mat and walks off toward the stairs. |
| G24 | 10 s | 6.0 | Dinner. Looks between them; pours into the cup; it overflows. |
| G25 | 5 s | — | Wet cloth, cup upright. Adam's head down, lifts at 4.2 s. |
| G26 | 5 s | — | Cup on its side. Grips the table; looks left (1.5 s), then right (2.6 s); lets go. |
| G27 | 5 s | 2.5 | Car. Truck headlights approach in the driver's POV; Layla turns from the back seat to the road. |
| G29 | 16 s | 6.0, 12.0 | Blanket pulled to the chin, rabbit moved to the shoulder, the kiss (7.0–9.2 s), then Adam at the door with his hand on the switch. |
| G30 | 10 s | 5.5 | Adam stops in the doorway; frontal push-in from the corridor. |
| G32 | 15 s | 4.0, 8.0, 12.0 | Car. Hands on the gearshift; Nour drawing; Layla looks back; mirror insert. |
| G33 | 14 s | 4.0, 8.0, 11.0 | Car. Nour holds the paper up (0.8 s); Adam flips the visor (4.6 s); paper raised higher; Layla touches his arm. |
| G34 | 8 s | 5.0 | Car. Adam turns his head back to Nour; his POV of the paper. |
| G35 | 5 s | 2.5 | Car. Layla looks to the road; the truck fills the windshield. |
| G38 | 5 s | — | Child in bed, wig slipped, blanket at the neck, rabbit by the shoulder. |
| G39 | 12 s | 8.5 | Adam pushes up to sitting against the bed (1.5 s), cries, hands to eyes (7.0 s), head down on his knees. |
| G40 | 5 s | — | Bag on the console. Adam walks up the hall, stops and turns to the console at 3.5 s. |
| G43 | 6 s | — | Both mannequins on the sofa. Adam pulls the curtains open (1.0–3.0 s). |
| G44 | 11 s | 5.0 | Curtains open. Adam steps in (3.5 s), unbuttons the cardigan (5.6, 6.3, 7.0 s), slides it off (8.0 s), lifts it to his face (9.4 s). |
| G45 | 6 s | — | Both mannequins bare on the stands, no wigs. Sleeve onto the child's shoulder (1.5 s); Adam steps back (3.5 s). |
| G47 | 5 s | — | No bag. Adam walks to the door: chain at 2.8 s, handle at 3.6 s. |
| G48 | 11 s | 5.0 | Yesterday's dish at Mona's feet. The door opens at 0.8 s and Adam is in it. |
| G49 | 6 s | — | Drawing on the cup at the table corner (foreground left); front door open; Mona steps in and holds him; he folds at 2.8 s. |

Runs with no figures (G01, G02, G06, G07, G13, G19, G31, G36, G41, G46) and G04, G17, G28, G37 and G42 have no blocking file.

## Decisions to check

1. **Kitchen door.** It is on the dining room's east wall, facing the curtains, so G03 (looking through it) and G14 (looking into the kitchen) both work.
2. **Fourth dining chair.** It stands against the north wall, so the near side of the table stays empty.
3. **Left and right.** Where a prompt's "its right" and "screen right" disagree, the screen side wins (G11, G22).
4. **G20.** "Toward the hallway" is read as toward the dining-room door.
5. **G14.** The stove is on the back wall, so Adam stands three-quarter to the camera, not side-on.
6. **G45.** Adam stands between the two stands, on the child's screen-left side.
7. **G49.** The adult's dining chair is pulled out so the foreground corner stays clear.
8. **G18 and G22.** The adult is on the sofa's west end from G18's second shot until dinner.
9. **No mouth or face animation.** Body, head, hands and camera only.
