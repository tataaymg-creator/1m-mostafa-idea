# LOOK — Task: blocking references, then rewrite the prompts

Give this file to a new session on this repository (branch `claude/wonderful-noether-yx6bsb`, environment **1m-mostafa-idea**, Higgsfield connected to the account with the project **baba look**). Do not open a pull request. Do not generate any video in this task.

## Where things stand

- Story, 87-shot list, character sheets, 12 location plates and 14 props are finished. All 33 are registered as elements in **baba look** (`elements.md`).
- `prompts.md` holds 49 runs (G01–G49) built by `tools/build_prompts.py`. **These prompts are wrong and must be rewritten.** They were written with the `higgsfield-timed-prompts` skill, not with `seedance-clean`, which is the skill the director wants.
- The run plan itself is still good: which shots are grouped into which run, the durations, the elements per run, the dialogue and its timing, and the action beats. Keep those; rewrite the form.

## Fixed decisions (do not change)

- Model: **Seedance 2.5 Draft**. Every run is **16:9**. Audio on.
- Present-day scenes are framed centre-safe, because they are cropped to 4:3 in the edit.
- Continuous action is one run of 4 to 30 seconds with cuts inside it, not many 5-second runs.
- Dialogue is English only: "Daddy", "sweetheart", "Mommy". No Arabic words.
- Tags are `@` plus the element's own name, for example `@adam`, `@doll-wife`, `@L02_dining`.
- Film rules in `story.md`: the mannequins stay rigid objects that only move in Adam's hands; the crash stays off screen; the drawing stays unseen until shot 76; yellow is the only saturated colour in the present; all text on screen stays blank.

## Part 1 — Blocking references

Purpose: keep every figure in the same place across shots and runs. Use the `blender-blocking` skill to build the sets, and the `tig-blocking-map` skill if a colour-coded staging map suits a setup better. A blocking image carries **geometry only**: positions, facing, camera angle. Faces, clothes, colours and the room's look still come from the character and location elements.

Build one grey-box apartment from the location images in `locations/`, so all rooms share one floor plan, plus one car interior. Colour-code the figures the same way everywhere:

| Figure | Colour |
|---|---|
| Adam | blue |
| Adult mannequin (`doll-wife`) | red |
| Child mannequin (`doll-daughter`) | yellow |
| Layla | purple |
| Nour | orange |
| Mona | green |

Setups that need a blocking image (one image per camera angle used):

| Setup | Runs | Positions |
|---|---|---|
| Dining table, frontal | G05, G24, G26 | Adam centre on the curtain side facing camera; adult mannequin at the left end; child mannequin at the right end; near side empty |
| Dining table, through the kitchen doorway | G03 | Same seats, seen through the door frame |
| Dining table, side angle | G25 | Same seats, camera at the room side, curtains at frame left |
| Dining chair, sandal | G08 | Child mannequin on a chair turned out from the table; Adam kneeling in front |
| Living room wide | G10, G16, G18, G43, G44 | Sofa centre; armchair front left; dancers in front of the sofa; child mannequin mid-sofa; in G43/G44 both mannequins side by side on the sofa, adult at left |
| Sofa two-shot | G11, G22 | Child mannequin mid-sofa; Adam at its right in G11, crouched at its left in G22 |
| Kitchen | G14, G20 | Adam at the stove; adult mannequin standing in the doorway, foreground left |
| Sewing corner | G45 | Adult mannequin on the left stand, child on the right stand, Adam beside the child |
| Hallway | G21, G40, G47, G49 | Adam centre of the hall, back to camera; front door at the far end; console on the right |
| Nour's room | G29, G30, G38, G39 | Bed on the left wall; Adam on the bed edge, in the doorway at far right, and on the floor against the bed |
| Car, from the back seat | G32 | Adam front left driving; Layla front right |
| Car, back seat | G09, G12, G32, G33, G34 | Nour back right, behind Layla, belted |
| Car, from the driver's side | G15, G27, G32, G33, G35 | Layla in profile in the front right seat |
| Landing | G23, G48 | Mona on the doormat facing the door at the right; Adam in the doorway |

Inserts with no figures (G01 stove, G02 top shot, G06, G07, G13, G19, G31, G36, G41, G46) need no blocking image.

Deliver for Part 1:

- The `.blend` files in a `blocking/` folder in the repo, and one 16:9 image per setup.
- Each image uploaded and registered in **baba look** as an element named `B##_setup-name` (for example `B01_dining-frontal`), with the list added to `elements.md`.
- Show the images to the director and wait for approval before Part 2.

## Part 2 — Rewrite all 49 prompts with `seedance-clean`

Load the `seedance-clean` skill and follow it for every run. What the current prompts get wrong against that skill:

| Now | Required |
|---|---|
| Opens with a logline and a LOOK style block near the top | Opens on SCENE CONTEXT and ACTIVE REFERENCES; style lives in its home blocks, format in a STYLE suffix at the end |
| Blocks: REFERENCES, LOOK, CHARACTERS, WHERE, BEHIND, SHOTS, SOUND, KEEP CONSISTENT | Blocks in the skill's order: SCENE CONTEXT, ACTIVE REFERENCES, LOCATION MAP, FIRST FRAME / BLOCKING, FORMAT MODE, OPTICS, CAMERA, ACTION, PERFORMANCE, PHYSICS, LIGHTING, AUDIO, STYLE, POSITIVE LOCKS |
| Lenses in millimetres | FOV in degrees from the skill's table (84°, 63°, 47°, 29°, 18°, 12°), per segment, with "no drift mid-segment" |
| Many negatives ("never moves", "no music", "not shown") | Positive phrasing only ("stays rigid and still", "the only sound is…", "her face stays above the frame") |
| Long appearance text repeated for each reference | Minimal anchor per tag plus "100% matches the reference" |
| Light described loosely | Source, direction, exposure and white balance in Kelvin, fixed per scene |
| Background as one line | Foreground, midground and background stated separately in LOCATION MAP |
| Emotion sometimes named ("pure joy", "peace") | Emotion as muscle movement and eye-line |
| Timecodes as `0.0–4.0s —` | `0.0s to 4.0s —` with `HARD CUT` / `MATCH CUT` lines, and a lock that cuts happen only at the stated points |
| No blocking reference | The `B##` element for the run's setup, tagged as geometry only |

Also keep each prompt sealed: no shot numbers, scene numbers, edit notes or mentions of other runs inside the prompt text. Those belong in the notes around the prompt.

Deliver for Part 2:

- Rewrite the run data in `tools/build_prompts.py` (or replace the script) and rebuild `prompts.md` and `prompts.html`; each run still lists its elements, duration and aspect, and each prompt keeps its copy button.
- Check that the timecodes in every run are contiguous and add up to the run's duration, and that every line of dialogue appears once.
- Update `HANDOFF.md` so the generating session uses the new prompts.
- Commit and push to `claude/wonderful-noether-yx6bsb`.
