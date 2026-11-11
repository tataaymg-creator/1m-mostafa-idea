#!/usr/bin/env python3
"""Builds prompts.md and prompts.html: every Seedance 2.5 generation for LOOK.

Usage: python3 tools/build_prompts.py prompts.md prompts.html

Each run below is one generation. Shot durations are given per shot and the
timecodes are computed, so they are always contiguous and sum to the run length.
Inside shot text, {1.5} means "1.5 seconds after this shot starts" and is
printed as an absolute time in the run.
"""
import html
import re
import sys

# ---------------------------------------------------------------- references
REF = {
    "adam": "Adam, present day. Take his face, stubble, the healed scar at his right temple, the washed-out grey-blue shirt with rolled sleeves, charcoal trousers, bare feet, wedding ring. Ignore the white background and the three-view sheet layout.",
    "adam-before": "Adam in the memory. Take his face (clean-shaven, healthier, NO scar), light linen shirt, chinos, wedding ring. Ignore the white background and the sheet layout.",
    "layla": "Layla, his wife. Take her face, shoulder-length dark wavy hair, burgundy cardigan over a cream floral dress, slim gold watch, wedding ring. Ignore the white background and the sheet layout.",
    "nour": "Nour, their daughter, 6. Take her face, the gap of a missing front tooth, two loose braids, white t-shirt, denim shorts, yellow sandals. Ignore the white background and the sheet layout.",
    "mona": "Mona, Layla's older sister, mid-forties. Take her face, grey-streaked hair in a bun, tortoiseshell glasses, navy dress, long grey cardigan. Ignore the white background and the sheet layout.",
    "doll-wife": "the adult mannequin. A life-size shop display mannequin in matte ivory plastic, smooth head with NO eyes and NO mouth, a slightly crooked dark wig, Layla's burgundy cardigan over a plain grey dress, visible seams at neck, shoulders and wrists. Ignore the white background and the sheet layout.",
    "doll-daughter": "the child mannequin. A child-size display mannequin in matte ivory plastic, smooth head with NO eyes and NO mouth, a dark wig in two bad braids, an unfinished yellow dress with pins, white tacking thread and one sleeve missing. Ignore the white background and the sheet layout.",
    "P01_yellow-cup": "the child's yellow plastic cup. Take shape and colour. Ignore the white background.",
    "P02_table-setting": "the plates and forks: two large plain plates, one small plate, three forks. Take the objects only. Ignore the white background and their arrangement.",
    "P03_yellow-sandal": "the small yellow child's sandal with a metal buckle. Ignore the white background.",
    "P04_hairbrush": "the worn wooden hairbrush. Ignore the white background.",
    "P05_radio": "the old portable radio: grey body, round speaker grille, cream handle, two dials. Ignore the white background.",
    "P06_hospital-bag": "the sealed clear plastic hospital belongings bag with a watch, a ring, a yellow crayon stub and a folded sheet of paper inside. Its label is blank. Ignore the white background.",
    "P07_bag-contents": "the four things from the bag: a gold watch with a brown strap and cracked glass, a wedding ring, a stub of yellow crayon, a folded dirty sheet of paper. Ignore the white background.",
    "P09_drawing": "the child's crayon drawing: three figures holding hands, a strip of blue sea, a little car, a huge yellow sun. Ignore the white background.",
    "P10_rabbit": "the small worn grey stuffed rabbit, about thirty centimetres tall. Ignore the white background.",
    "P11_night-light": "the star-projector night-light dome, about twelve centimetres wide. Ignore the white background.",
    "P12_crayons": "the worn wax crayons, each about eight centimetres long and finger-thin; the yellow one is the shortest. Ignore the white background.",
    "P13_family-car": "the family car: a modest older off-white four-door sedan, no badges. Take the car only. Ignore the background.",
    "P14_foil-dish": "the oven dish covered with aluminium foil. Ignore the white background.",
    "L01_kitchen": "the kitchen, empty. Take the room exactly: window with a thin glowing curtain and the sink on the left, the white enamel gas stove in the middle, the wooden counter with the cutting board on the right, the radio on the wall shelf above it, sage walls, terrazzo floor.",
    "L02_dining": "the dining area, empty. Take the room exactly: the table with a lace cloth and four wooden chairs standing in front of the tall closed olive-grey curtains, the sideboard with a mantel clock, the pendant lamp, the kitchen doorway on the right.",
    "L03_living-dim": "the living room with the curtains closed, empty, the same camera and room as @L03b_living-day. Take the room exactly: the grey sofa with a lace throw in the middle, the floral armchair at front left, the low coffee table, the bookshelf on the left wall, the floor lamp, the sewing corner at the back right, the closed curtains on the right wall, the sewing corner with the machine, mirror and two steel stands at the back right.",
    "L03b_living-day": "the same living room, same camera, with the curtains open and morning sun coming in; the sewing corner with the machine, mirror and two steel stands at the back right. Take the daylight state of the room: sun shafts across the rug and floor, the city through the window on the right.",
    "L04_sewing-corner": "the sewing corner of the living room, empty. Take it exactly: floor lamp and sofa end on the left, the sewing table with the black machine threaded with yellow and the yellow sleeve under the needle, bentwood chair, fabric shelves and paper patterns on the wall, the tall framed mirror leaning on the wall, two bare steel mannequin stands, the closed curtains on the right.",
    "L05_hallway": "the entrance hallway, empty, with NO bag on the console. Take it exactly: glazed doors on the left, the dark front door at the far end, coat hooks, the wall mirror and the narrow console table with a dead plant and unopened mail on the right.",
    "L05b_hallway-bag": "the entrance hallway, empty, with the sealed hospital bag lying on the console under the mail. Take it exactly: glazed doors on the left, the dark front door at the far end, coat hooks, the wall mirror and the narrow console table with a dead plant, mail and the bag on the right.",
    "L06_nour-room": "Nour's bedroom at night, empty. Take it exactly: the small bed against the left wall, the rabbit on the pillow, the star night-light on the bedside table, the curtained window on the back wall, the small desk with paper and crayons on the right, the open door at far right, crayon scribbles taped above the bed, stars projected on the walls and ceiling.",
    "L07_car-front": "the car interior seen from the back seat, empty. Take the cabin exactly: left-hand drive, grey-beige fabric seats, plain grey dashboard with a simple radio, rear-view mirror, the straight desert road ahead with the low sun.",
    "L07b_car-backseat": "the car's back seat, empty. Take it exactly: grey-beige bench seat, the seatbelt on the right-hand side, the picture book with a sheet of paper and the small crayons, the swim ring on the rear shelf.",
    "L08_desert-road": "the road: a straight two-lane desert highway at golden hour, sandy shoulders, low scrub, poles, a thin line of sea on the horizon.",
    "L09_landing": "the stairwell landing outside the apartment, empty. Take it exactly: the dark wooden apartment door on the right, the doormat, the stairs with an iron railing on the left, the small frosted window.",
}

LOOKS = {
    "P": ("16:9", "Naturalistic 35mm motion-picture look with fine grain, soft contrast, not glossy. 16:9 frame, composed centre-safe: everything important stays inside the middle of the picture, and the far left and right edges hold only background. The camera is on a tripod and locked unless a shot says otherwise. Lenses 35, 50 and 85mm. The apartment is shut in: curtains closed, still dusty air, sage-green walls, grey and faded wood. Yellow is the only saturated colour in the picture."),
    "PW": ("16:9", "Naturalistic 35mm motion-picture look with fine grain, soft contrast, not glossy. 16:9 frame. The camera is on a tripod and locked. Lenses 35, 50 and 85mm. The same apartment, now with real daylight in it: sage-green walls, grey and faded wood, dust hanging in the sun. Yellow is the only saturated colour in the picture."),
    "M": ("16:9", "Naturalistic 35mm motion-picture look with fine grain. 16:9 frame. Handheld camera that breathes and stays close, 24 to 50mm, shallow focus. Golden hour: the sun is low and straight ahead of the car, warm amber light, flares, dust on the glass, wind. Skin tones warm and alive."),
}

CHAR = {
    "adam": "Adam — 38, gentle, exhausted, quiet. Speaks softly and low, a little hoarse, unhurried, in plain English. He treats the mannequins with complete tenderness and never looks at them as objects. He never eats.",
    "adam-before": "Adam — 38, relaxed, happy, clean-shaven, no scar. Speaks warmly and easily, in plain English.",
    "layla": "Layla — 34, warm, teasing, quick to laugh. Speaks brightly, in plain English.",
    "nour": "Nour — 6, stubborn, bright, proud of her drawing. A clear small child's voice, in plain English.",
    "mona": "Mona — mid-forties, tired, kind, steady. Speaks low and plainly, in plain English.",
}

MANNEQUIN_RULE = "MANNEQUIN RULE\nThe mannequins are rigid, hard, hollow plastic objects. They never blink, breathe, turn, nod, bend or shift on their own. They have no eyes and no mouth. They move only when Adam's hands move them, the way a chair moves. They never speak and nothing answers him."

KEEP = {
    "P": [
        "16:9 frame, tripod, locked camera; no zoom, no drift and no handheld unless a shot states it.",
        "Centre-safe: faces, hands and props stay in the middle of the frame, never in the outer eighth on either side.",
        "The curtains stay closed. No direct sunlight in the apartment.",
        "Yellow is the only saturated colour; everything else is muted.",
        "Nobody else is in the apartment. No reflections of a crew, no extra people.",
        "No on-screen text, no subtitles, no captions, no logos, no watermark.",
    ],
    "PW": [
        "16:9 frame, tripod, locked camera; no zoom, no drift, no handheld.",
        "Yellow is the only saturated colour; everything else is muted.",
        "No on-screen text, no subtitles, no captions, no logos, no watermark.",
    ],
    "M": [
        "16:9 frame, handheld, golden hour, sun low and straight ahead of the car.",
        "Seats never change: Adam drives in the front left seat, Layla sits in the front right seat, Nour sits in the back seat on the right, behind Layla, with her seatbelt on.",
        "Adam here is @adam-before: clean-shaven, no scar." ,
        "No crash, no impact, no injury and no blood are shown.",
        "No badges or logos on the car. No on-screen text, no subtitles, no watermark.",
    ],
}

LOOKS["ML"] = ("16:9", "Naturalistic 35mm motion-picture look with fine grain. 16:9 frame. The camera is steady or locked, not handheld. Shallow focus. The light and colour of the memory: warm, low, real.")
KEEP["ML"] = [
    "16:9 frame, steady camera, not handheld.",
    "No crash, no impact, no injury and no blood are shown.",
    "No badges or logos. No on-screen text, no subtitles, no watermark.",
]

SETTINGS = "Seedance 2.5 Draft · audio ON"

# --------------------------------------------------------------------- runs
# shot tuple: (duration, heading, text, lines)
# line tuple: (start offset, end offset, speaker, delivery, text)
RUNS = []


def run(**kw):
    RUNS.append(kw)


# ============================================================ 1 · MORNING
run(id="G01", scene="1 · Morning", nums="02, 04", look="P", refs=["adam", "L01_kitchen"],
    light="Morning. The thin kitchen curtain glows with the daylight it keeps out; one bare warm bulb.",
    logline="A 10-second, 16:9 clip in two shots: a stove igniter catches under a small pot, then a man seen from behind cuts toast into triangles at the counter. Hard cut between them.",
    where="Kitchen. Adam stands at the wooden counter on the right side of the room, his back to the camera. Nobody else.",
    behind="Behind the stove: the off-white tiled backsplash. In front of Adam: the counter with the cutting board, and above it the wall shelf with the radio.",
    shots=[
        (4, "ECU, macro, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: a burner of the white enamel gas stove, very close. Adam's hand turns the knob. At {0.3} the igniter clicks and a ring of blue flame catches under a small aluminium pot. The hand withdraws at {1.5}. The flame settles and burns steadily. BACKGROUND: soft-focus off-white tiles. Hard cut.", []),
        (6, "MS from behind, 50mm, locked",
         "Adam at the counter, seen from behind and slightly to his left, waist up, sleeves rolled. He cuts the crusts off two slices of toast with a bread knife, then at {2.5} slices them corner to corner into triangles and at {4.5} lifts them onto a plate. He hums five slow notes, slightly off key, from {1.0} to {4.0}. BACKGROUND: the wall shelf with the radio above him on the right, the stove with its blue flame at the left edge, the curtained window glowing further left. His face is not shown.", []),
    ],
    amb="Igniter click, gas hiss, a wall clock ticking, fridge hum, knife on board. Adam's quiet humming in the second shot.",
    keep=["The radio on the shelf is switched off."])

run(id="G02", scene="1 · Morning", nums="03", look="P", refs=["P02_table-setting", "P01_yellow-cup", "L02_dining"],
    light="Morning, dim. Soft grey light from the closed curtains.",
    logline="A 5-second, 16:9 top shot: a man's hands lay a wooden table for three.",
    where="Dining table. Only Adam's forearms and hands enter the frame, from the bottom edge.",
    behind="The whole frame is the table top: the cream lace tablecloth over dark wood.",
    shots=[
        (5, "Top shot straight down, 35mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the empty lace-covered table top seen from directly above. A man's hands with a wedding ring and rolled grey-blue sleeves come in from the bottom edge. At {0.5} he sets a large plate at the left, at {1.5} a large plate at the right, at {2.5} the small plate at the top centre. At {3.3} he lays one fork beside each plate. At {4.2} he sets the yellow cup beside the small plate and his hands leave the frame. BACKGROUND: lace and wood only.", []),
    ],
    amb="Ceramic on wood, forks, a wall clock ticking.",
    keep=["Exactly three plates, three forks and one yellow cup. Nothing else on the table.", "The plates are empty."])

run(id="G03", scene="1 · Morning", nums="05, 06", look="P", refs=["adam", "doll-wife", "doll-daughter", "L02_dining"],
    light="Morning, dim. The closed curtains behind the table glow and backlight the figures.",
    logline="A 10-second, 16:9 clip in two shots: seen through the kitchen doorway, a man serves breakfast to two seated silhouettes; then a close-up of him speaking to someone off screen and waiting for an answer. The two seated figures stay unreadable silhouettes.",
    where="Dining table, seen from the kitchen doorway, the closed curtains behind it. The adult figure sits at the left end of the table, the child-size figure at the right end, both in profile to the camera. Adam's chair is on the far side, centre, facing the camera. The near side is empty.",
    behind="Behind all three: the tall closed olive-grey curtains, glowing. At the right edge: the sideboard with the clock.",
    shots=[
        (6, "Wide through the kitchen doorway, 35mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the dark varnished door frame of the kitchen fills both edges of the picture as a frame within the frame. Beyond it, the laid table and two seated figures, pure dark silhouettes against the glowing curtains, completely still. At {0.8} Adam walks in from the right with a plate of toast triangles in each hand, sets one in front of the left figure at {2.2}, one in front of the right figure at {3.4}, and stays standing between them. BACKGROUND: the glowing curtains; no detail can be seen on the two silhouettes.",
         [(3.8, 5.4, "Adam", "warm, quiet, an ordinary morning", "Good morning, my loves.")]),
        (4, "CU Adam, 85mm, locked",
         "Adam's face, three-quarter, looking down and to screen right at someone seated off frame. First clear look at him: tired, gentle, unshaven, the scar at his right temple. He smiles. After the line he waits, eyebrows slightly raised, the way you wait for a reply; at {3.2} a small breath of a laugh, as if he got one. BACKGROUND: the glowing curtains, out of focus. Both seated figures are out of frame.",
         [(0.4, 2.2, "Adam", "fond, lightly scolding", "Nour, sit up straight, sweetheart.")]),
    ],
    amb="A wall clock ticking, plates on wood. After Adam's second line, only the clock: nobody answers.",
    keep=["In the wide shot the two seated figures are black silhouettes; their faces and materials cannot be read."])

run(id="G04", scene="1 · Morning", nums="07 ★", look="P", refs=["adam", "doll-wife", "L02_dining"],
    light="Morning, dim. Soft glow from the closed curtains at the side.",
    logline="A 5-second, 16:9 hero shot: a man bends to kiss his wife's forehead and the focus moves from his lips to her, and she is a mannequin. No camera move, no emphasis.",
    where="Dining table. The mannequin sits on a chair at the left end of the table. Adam stands beside it and bends down.",
    behind="Behind the mannequin's head: the closed olive-grey curtains, soft. Behind Adam: the dim room.",
    shots=[
        (5, "Over-shoulder to CU, 85mm, locked, slow rack focus",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: over the back of a seated figure's head and burgundy shoulder, out of focus in the foreground; Adam's face in focus above it as he leans down. At {1.2} his lips touch the forehead and he closes his eyes. From {1.8} to {3.5} the focus racks slowly from his lips to the head he is kissing: smooth matte ivory plastic, the edge of a wig, a seam at the neck, no eyes, no mouth. He straightens at {4.0} and leaves the top of the frame; the plastic face stays, in focus, perfectly still. BACKGROUND: curtains, soft.", []),
    ],
    amb="A wall clock. The kiss makes a small hollow tap on plastic. Nothing else.",
    keep=["The camera does not push in, tilt or move. Only the focus changes.", "No music, no sting, no sound effect on the reveal."])

run(id="G05", scene="1 · Morning", nums="08 ★", look="P", refs=["adam", "doll-wife", "doll-daughter", "P01_yellow-cup", "L02_dining"],
    light="Morning, dim. The closed curtains behind the table glow softly; faces are lit from the front by the room.",
    logline="A 6-second, 16:9 hero shot: a locked, dead-centre, symmetrical wide of a man having breakfast between two mannequins. He talks. He does not eat.",
    where="Dining table, frontal, the closed curtains directly behind it. Adam sits on the far side at the centre, facing the camera. The adult mannequin sits at the left end of the table (screen left), turned toward the table. The child mannequin sits at the right end (screen right), turned toward the table. The near side is empty.",
    behind="Behind Adam: the centre of the closed olive-grey curtains. Behind the adult mannequin: curtains and the room's left corner. Behind the child mannequin: curtains, then the sideboard with the clock at the right edge.",
    shots=[
        (6, "Wide frontal, 35mm, locked, dead centre",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the whole table square to the camera. Three plates of toast triangles, untouched; the yellow cup by the small plate at screen right. Adam sits with his hands flat beside his plate, looking at the child mannequin. He speaks to it, then turns his head to the adult mannequin at {3.5} and gives a small private smile. He does not touch his food. Both mannequins are completely still for the whole shot. BACKGROUND: the glowing curtains across the full width. Hold.",
         [(0.8, 2.8, "Adam", "light, conversational, to the child mannequin", "Mommy's almost finished your dress.")]),
    ],
    amb="A wall clock ticking. After the line, silence the length of a reply. No one answers.",
    keep=["Symmetry: Adam exactly centred, one mannequin on each side.", "Adam never eats or lifts a fork."])

run(id="G06", scene="1 · Morning", nums="09 ○", look="P", refs=["L01_kitchen"],
    light="Morning. Dim kitchen, soft glow from the curtained window.",
    logline="A 4-second, 16:9 insert: a plate is scraped into a kitchen bin that is already full of identical untouched toast triangles.",
    where="Kitchen floor by the counter. Only Adam's hand, a plate and a fork enter the frame.",
    behind="Around the bin: the speckled terrazzo floor and the base of a cream cabinet.",
    shots=[
        (4, "Insert from above, 50mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: an open pedal bin seen from above, filled with layers of dry toast triangles from other mornings. At {0.6} a man's hand with a rolled grey-blue sleeve tips a plate over it and a fork scrapes three fresh toast triangles onto the pile. At {2.8} the plate leaves and the lid swings shut. BACKGROUND: terrazzo floor.", []),
    ],
    amb="Fork scraping ceramic, a soft thud of toast, the lid closing. A wall clock, faint.",
    keep=[])

run(id="G07", scene="1 · Morning", nums="10", look="P", refs=["P06_hospital-bag", "L05b_hallway-bag"],
    light="Morning. The hallway is dim; a little cool light from the glazed doors.",
    logline="A 5-second, 16:9 insert with a very slow push-in: the console by the front door, four months of mail, a dead plant, car keys and a sealed hospital bag nobody has touched.",
    where="Entrance hallway, the narrow console table on the right wall near the front door. Nobody in frame.",
    behind="Behind the console: the sage wall and the lower edge of the wall mirror. At the left edge: the dark front door.",
    shots=[
        (5, "Insert, 50mm, very slow push-in for the whole shot",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the console top at a three-quarter angle: a slumped pile of unopened envelopes with blank faces, a dead plant in a pot, a set of car keys, and half under the mail the sealed clear plastic bag, grey with dust; a gold watch, a ring and a stub of yellow crayon show faintly through the plastic. The camera creeps toward the bag. Nothing moves except dust in the air. BACKGROUND: the wall and the mirror's lower frame.", []),
    ],
    amb="A wall clock, further away. A neighbour's door closing somewhere in the building.",
    keep=["The bag is sealed and dusty. Nothing on the console is touched.", "Envelopes and the bag's label are blank: no writing."])

run(id="G08", scene="1 · Morning", nums="11, 14", look="P", refs=["adam", "doll-daughter", "P03_yellow-sandal", "L02_dining"],
    light="Morning, dim. Low soft light under the table edge, glow from the closed curtains.",
    logline="A 10-second, 16:9 clip in two shots: a man kneels and buckles a yellow sandal onto a child mannequin's rigid foot; then a close-up of him frozen on his knees, as if the click took him somewhere else, before he shakes it off. (In the edit a 4-second memory flash sits between the two shots.)",
    where="Dining area. The child mannequin sits on a wooden chair turned away from the table. Adam kneels on the terrazzo floor in front of it.",
    behind="Behind the mannequin's legs: the chair legs and the hanging edge of the lace tablecloth. Behind Adam: the dim room and the sideboard.",
    shots=[
        (5, "CU hands, low, 50mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: a rigid ivory plastic child's foot, toes pointing straight ahead, held in Adam's left hand; the hem of the yellow dress at the top of the frame. With his right hand he slides the small yellow sandal on, feeds the strap through and at {3.6} presses the buckle shut. His hands stop dead on the click. BACKGROUND: chair legs, lace, terrazzo.", []),
        (5, "CU Adam, 85mm, locked",
         "Adam's face, still kneeling, eyes level with the mannequin's knees, which are a soft yellow blur at the frame edge. He is frozen, not breathing, eyes unfocused. He blinks twice at {1.0}. At {1.8} his right hand rises and two fingers touch the scar at his temple. At {3.0} he shakes his head once, like a man waking, and looks up at the mannequin with a thin smile. BACKGROUND: the dim room, the sideboard, out of focus.",
         [(3.6, 4.7, "Adam", "under his breath, covering", "...Where were we.")]),
    ],
    amb="Shot one: fabric, the strap, a sharp metallic buckle click. Shot two: total silence for two seconds, then the wall clock fades back in.",
    keep=["The plastic foot is rigid: the ankle and toes never flex."])

run(id="G09", scene="1 · Morning (flash 1)", nums="12, 13", look="M", refs=["nour", "L07b_car-backseat", "P12_crayons"],
    light="Low sun raking through the car's side window.",
    logline="A 5-second, 16:9 memory flash in two shots: a seatbelt clicking shut in a small hand, then a child's legs swinging off a car's back seat. Her face is never shown.",
    where="Back seat of the car. Nour sits on the right-hand side, belted. Only her hand, lap and legs are seen.",
    behind="Behind her legs: the grey-beige seat fabric, the picture book and the small crayons beside her; the car door with its window winder.",
    shots=[
        (2.5, "ECU, macro, handheld",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: a seatbelt tongue held in a small child's hand, a centimetre from its buckle on the seat. At {0.4} it snaps in. The hand lets go and smooths the belt across a white t-shirt. Golden light, dust in the air. BACKGROUND: seat fabric, soft.", []),
        (2.5, "CU, handheld, 35mm",
         "A child's bare legs hanging off the edge of the back seat, swinging in turn, yellow sandals on both feet. Beside her on the seat a few small crayons roll a little with the motion of the car. Her face stays above the frame. BACKGROUND: the door card, sunlight sliding over it.", []),
    ],
    amb="A sharp seatbelt click, then one warm second of road hum; in the second shot a child humming five notes, cut off dead at the end.",
    keep=["Nour's face is not shown in this clip.", "The crayons are small: finger-thin, about eight centimetres."])

# ============================================================== 2 · HAIR
run(id="G10", scene="2 · Hair", nums="15", look="P", refs=["adam", "doll-daughter", "doll-wife", "L03_living-dim"],
    light="Late morning. Curtains closed, the floor lamp on, dim.",
    logline="A 5-second, 16:9 wide: a man carries a child-size mannequin across the living room the way you carry a sleeping child and sets it on the sofa. Staged from behind him.",
    where="Living room. The adult mannequin already sits in the floral armchair at front left, facing the sofa. Adam enters from the left, behind the armchair, carrying the child mannequin, and crosses to the sofa in the middle of the room.",
    behind="Behind Adam as he walks: the bookshelf and the framed pictures on the left wall. Behind the sofa: the floor lamp and the sewing corner. At right: the closed curtains.",
    shots=[
        (5, "Wide, 35mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the living room exactly at the angle of @L03_living-dim, the adult mannequin seated motionless in the armchair. Adam walks in from the left with his back mostly to the camera, the child mannequin held against his chest: one arm under its stiff straight legs, which stick out sideways, his other hand cradling the back of its head. At {3.0} he lowers it carefully onto the middle of the sofa, sitting it upright, and at {4.3} settles its head with one hand. BACKGROUND: lamp and sewing corner behind the sofa.", []),
    ],
    amb="Bare footsteps on terrazzo, a small creak of hollow plastic, the wall clock.",
    keep=["The child mannequin stays stiff as a board: its legs and arms never bend or drape."])

run(id="G11", scene="2 · Hair", nums="16, 17, 20", look="P", refs=["adam", "doll-daughter", "doll-wife", "P04_hairbrush", "L03_living-dim"],
    light="Late morning. Curtains closed, warm floor lamp behind the sofa, dim.",
    logline="A 15-second, 16:9 clip in three shots: a father brushes and tries to braid a child mannequin's wig; the brush snags and the wig slides off bare plastic; then, guiltily, he straightens it. (In the edit a memory flash sits between shots two and three.)",
    where="Living room sofa. The child mannequin sits upright in the middle of the sofa, facing forward. Adam sits beside it on its right side (screen right), turned toward it. The adult mannequin sits in the armchair, off frame to screen left.",
    behind="Behind both: the lace throw on the sofa back, then the warm floor lamp and the dim sage wall.",
    shots=[
        (6, "MCU, profile two-shot, 85mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Adam in profile facing screen left, the child mannequin's wigged head in profile in front of him. He draws the wooden hairbrush down the wig with his right hand, holding a clumsy half-made braid in his left. At {3.0}, while speaking, he glances past the camera toward the armchair off screen left and smiles like a man sharing a secret. BACKGROUND: lace throw, lamp glow.",
         [(1.0, 3.4, "Adam", "low, fond, to the child mannequin", "Mommy does it better, I know."), (3.9, 5.4, "Adam", "a conspirator's whisper", "Don't tell her I said that.")]),
        (4, "ECU, macro, locked",
         "The brush in the wig, very close. At {0.8} the bristles snag. He tugs, and at {1.6} the whole wig slides sideways in one piece, exposing a bare, shiny ivory plastic scalp with a seam line. His hand stops. BACKGROUND: nothing but wig, brush and plastic.", []),
        (5, "CU Adam, 85mm, locked",
         "Adam's face, three-quarter, breath caught, eyes on the exposed plastic just below frame. At {1.0} both his hands come up into the lower frame and slide the wig back into place; at {3.0} he smooths it down twice with his palm, carefully, like stroking a child's hair. BACKGROUND: lamp glow, soft.",
         [(1.4, 2.2, "Adam", "a whisper, ashamed", "Sorry."), (3.0, 4.4, "Adam", "softer still", "Sorry, sweetheart.")]),
    ],
    amb="Brush bristles through synthetic hair, the wall clock. In shot two: a dry slide of wig on plastic. Shot three: his breathing.",
    keep=["The mannequin's head never turns or tilts by itself; only the wig moves, and only because of the brush or his hands."])

run(id="G12", scene="2 · Hair (flash 2)", nums="18, 19 ○", look="M", refs=["nour", "layla", "L07b_car-backseat"],
    light="Low sun flaring through the open side window.",
    logline="A 6-second, 16:9 memory flash in two shots: a real six-year-old laughing with the car-window wind in her hair, then her mother's hand reaching back to tuck the hair behind her ear.",
    where="Back seat. Nour sits on the right-hand side, belted, next to the open window. Layla is in the front right seat, directly in front of her; only her arm and hand reach back between seat and door.",
    behind="Behind Nour: the seat back and headrest, the swim ring on the rear shelf, golden desert rushing past the window.",
    shots=[
        (3, "CU Nour, handheld, 28mm, very close",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Nour's face filling the frame, eyes closed, laughing with her mouth open, the gap of her missing tooth showing, loose strands of her braids whipping across her face in the wind. Sun flare bursts across the lens at {1.5}. BACKGROUND: headrest, bright window.", []),
        (3, "CU, handheld, 35mm",
         "Same seat, slightly wider. A woman's left hand in a burgundy sleeve, wedding ring and slim gold watch on it, reaches back from the front seat and at {1.0} tucks the flying hair behind the girl's ear. The ring catches the sun at {1.6}. Nour opens her eyes and grins toward the front. BACKGROUND: seat back, window, desert.", []),
    ],
    amb="Wind roar through the open window, Nour's laugh, road hum; in the second shot a car radio, faint.",
    keep=["Layla's face is not shown in this clip: only her arm and hand."])

# ==================================================== 3 · SEWING CORNER
run(id="G13", scene="3 · The sewing corner", nums="21", look="P", refs=["L03_living-dim"],
    light="Late morning. Curtains closed, one thin blade of daylight at their edge, the floor lamp on.",
    logline="A 5-second, 16:9 wide with a slow push-in: a dressmaker's corner left exactly as it was, and two empty mannequin stands.",
    where="The living room, the sewing corner at the back right beyond the sofa. Nobody in frame.",
    behind="Left: floor lamp and sofa end. Centre: the sewing table against the sage wall, shelves of folded fabric and paper patterns above. Right of the table: the framed mirror leaning on the wall, the two bare steel stands, the closed curtains.",
    shots=[
        (5, "Wide, 35mm, slow push-in for the whole shot",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the living room exactly at the angle of @L03_living-dim. The camera pushes slowly across the room, past the sofa, toward the sewing corner at the back and its sewing machine: black, still threaded with yellow thread, a small yellow sleeve lying under its needle. The two steel stands stand empty at the right, each in a clean circle in the dust on the floor. Nothing moves but dust in the blade of light. The push ends with the machine and sleeve filling the centre of the frame. BACKGROUND: patterns on the wall, fabric shelves.", []),
    ],
    amb="The wall clock. At 3.5s, from another room, a radio dial clicks on and soft static begins.",
    keep=["Both stands are empty. No mannequins, no people.", "The paper patterns are blank shapes: no writing."])

# ================================================= 4 · SONG AND DANCE
run(id="G14", scene="4 · The song & the dance", nums="22, 23, 26", look="P", refs=["adam", "doll-wife", "P05_radio", "L01_kitchen"],
    light="Evening. The curtain is dark now; the bare warm bulb lights the kitchen.",
    logline="A 13-second, 16:9 clip in three shots: a hand tunes an old radio to a warm old song; a man cooks and talks to a mannequin he has stood in the kitchen doorway; then, close on him, he holds out a hand and asks her to dance. (In the edit a memory flash sits between shots two and three.)",
    where="Kitchen. Adam stands at the stove in the middle of the room. The adult mannequin stands upright in the kitchen doorway, at the left edge of frame in the foreground, facing into the kitchen toward him.",
    behind="Behind Adam: the tiled backsplash, the dark curtained window to his left, the shelf with the radio to his right. Behind the mannequin: the dark varnished door frame.",
    shots=[
        (4, "Insert, macro, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the old radio on its wall shelf, close. Adam's fingers turn the right-hand dial slowly. Static, fragments, and at {2.4} a warm, slow, old-fashioned song settles in. His hand rests on the radio for a moment and leaves at {3.5}. BACKGROUND: the sage wall.", []),
        (5, "MS, 50mm, locked",
         "Adam at the stove, side-on to camera, stirring a pot with a wooden spoon and swaying slightly to the song. The adult mannequin stands in the left foreground in the doorway, seen from behind its shoulder, perfectly still. He tastes from the spoon at {1.0}, then speaks over his shoulder toward it with a half smile. BACKGROUND: backsplash, shelf and radio.",
         [(2.0, 4.2, "Adam", "teasing, easy, over his shoulder", "You always say I put too much salt.")]),
        (4, "CU Adam, 85mm, locked",
         "Adam's face turned toward the doorway, a real smile, eyes wet. At {0.8} he wipes his hands on a cloth below frame. At {2.0} he holds one open hand out toward the doorway off screen left. BACKGROUND: the stove and the warm bulb, soft.",
         [(2.3, 3.4, "Adam", "quiet, shy, sincere", "Dance with me.")]),
    ],
    amb="Radio static resolving into the song, which then plays small and thin from the radio for the rest of the clip. A pot simmering, the wooden spoon.",
    music="The only music is the song coming from the radio: a warm, slow, old-fashioned instrumental waltz, small and tinny. It will be replaced by the film's own song in the edit.",
    keep=["The mannequin in the doorway stands rigid and never reacts."])

run(id="G15", scene="4 · The song & the dance (flash 3)", nums="24, 25 ★, 29", look="M", refs=["layla", "adam-before", "L07_car-front"],
    light="Low sun through the windshield, gold on her face.",
    logline="A 10-second, 16:9 memory flash in three shots: a woman's fingers turn up the car radio; she sings along badly in the passenger seat, laughs at herself and turns to look at her husband; her hand rests on his on the gearshift.",
    where="Front of the car. Adam drives in the front left seat; Layla sits in the front right seat. The camera is on Adam's side, looking across at her.",
    behind="Behind Layla: her side window, golden desert sliding past, her headrest. Below: the plain grey dashboard with the simple radio.",
    shots=[
        (3, "Insert, macro, handheld",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the simple car radio in the grey dashboard. A woman's hand, burgundy cuff, gold watch, wedding ring, turns the volume knob up at {0.8}; her fingers tap the dashboard twice in time. BACKGROUND: dashboard, a flare off the glass.", []),
        (4, "CU Layla, handheld, 35mm, from the driver's side",
         "Layla in left profile in the passenger seat, hair moving in the wind, singing along with the tune with no words, slightly flat, then breaking into a laugh at herself at {1.6}. At {2.6} she turns her head and looks straight toward the driver, into the lens, still smiling. This is the first clear view of her face. BACKGROUND: her window, the desert, the sun flaring behind her hair.", []),
        (3, "Insert, macro, handheld",
         "The gearshift between the seats. Adam's right hand rests on it; Layla's left hand lies over his, and her thumb strokes his knuckle slowly, twice. Both wedding rings in the light. BACKGROUND: seat fabric, the handbrake.", []),
    ],
    amb="The same warm old-fashioned waltz, brighter and fuller through car speakers. Road hum, wind. Layla hums and la-las along without words, then laughs.",
    music="The only music is the song from the car radio. It will be replaced by the film's own song in the edit.",
    keep=["Layla sings sounds only, no words.", "Adam's face is not shown in this clip: only his hand."])

run(id="G16", scene="4 · The song & the dance", nums="27 ★", look="P", refs=["adam", "doll-wife", "doll-daughter", "L03_living-dim"],
    light="Evening. Curtains closed; the floor lamp is the only light, warm, with deep shadow around it.",
    logline="An 8-second, 16:9 hero shot, the poster of the film: a locked symmetrical wide of a man slow-dancing with a mannequin in lamplight while a child mannequin sits on the sofa facing them.",
    where="Living room. Adam and the adult mannequin stand in the open floor in front of the sofa, centre frame. The child mannequin sits upright in the middle of the sofa behind them, facing the camera.",
    behind="Behind the dancers: the sofa with the child mannequin, the glowing floor lamp, the dim sewing corner. Right: the closed curtains. Left: the bookshelf.",
    shots=[
        (8, "Wide, 35mm, locked, symmetrical",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Adam holding the adult mannequin upright against him in a dance hold: his right arm around its waist carrying its weight, its rigid left arm laid over his shoulder, his left hand holding its stiff right hand out to the side, his cheek against its wig. He shuffles in a slow circle, turning a quarter turn by {4.0} and a half turn by {8.0}; the mannequin turns with him as one rigid piece, its feet dragging lightly on the rug. His eyes are closed. The child mannequin on the sofa does not move. The camera does not move. BACKGROUND: sofa, lamp, sewing corner.", []),
    ],
    amb="The waltz, small and distant, from the radio in the kitchen. His bare feet shuffling on the rug. The wall clock.",
    music="The only music is the distant radio song from the kitchen. It will be replaced by the film's own song in the edit.",
    keep=["The mannequin's body, neck and arms stay rigid; it is carried, it does not dance.", "He turns; the camera does not."])

run(id="G17", scene="4 · The song & the dance", nums="28, 30", look="P", refs=["adam", "doll-wife", "L03_living-dim"],
    light="Evening. Warm floor lamp from behind, deep shadow.",
    logline="An 8-second, 16:9 clip in two shots: a man's face at peace against a mannequin's plastic cheek; then the mannequin's arm slips out of its shoulder socket and slides down his back. (In the edit a memory flash sits between them.)",
    where="Living room, in front of the sofa. Adam holds the adult mannequin in a dance hold, its left arm over his right shoulder.",
    behind="Behind them: the warm glow of the floor lamp and the dim sage wall, out of focus.",
    shots=[
        (4.5, "CU, 85mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Adam's face in three-quarter view pressed against the mannequin's smooth ivory cheek, his eyes closed, the crooked wig against his forehead. He sways very slightly. A long slow breath out at {2.0}; the smallest smile. The plastic face beside his is blank and still. BACKGROUND: lamp glow.", []),
        (3.5, "CU on his shoulder and back, 85mm, locked",
         "Adam's right shoulder and upper back, the mannequin's burgundy-sleeved arm lying over it with its ivory hand hanging open. At {0.8} the arm drops a centimetre with a pop as it leaves the shoulder socket. At {1.4} it slides down his back, sleeve and all, and falls out of the bottom of the frame at {2.6}. Adam stops moving. BACKGROUND: lamp glow, wall.", []),
    ],
    amb="The distant radio waltz and his breathing. In shot two: a dry plastic pop, cloth sliding.",
    music="The only music is the distant radio song. It will be replaced by the film's own song in the edit.",
    keep=["The arm comes away as a clean plastic part: a hollow socket, no damage, nothing organic."])

run(id="G18", scene="4 · The song & the dance", nums="31, 32 ★", look="P", refs=["adam", "doll-wife", "doll-daughter", "L03_living-dim"],
    light="Evening. Warm floor lamp, deep shadow.",
    logline="A 10-second, 16:9 clip in two shots: the mannequin's arm lies on the floor while he stands holding a one-armed figure; then, on his knees, he pushes the arm back into its socket far too gently and presses the plastic hand to his forehead.",
    opens="Opens mid-situation: the dance has just stopped; the mannequin's left arm has fallen off.",
    where="Living room, in front of the sofa. Adam stands centre holding the adult mannequin upright; the detached arm lies on the rug at their feet. The child mannequin sits in the middle of the sofa behind them.",
    behind="Behind them: the sofa with the child mannequin, the floor lamp, the dim sewing corner; the closed curtains at right.",
    shots=[
        (4, "Wide, 35mm, locked, the same frame as the dance",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the detached burgundy-sleeved arm rocking on the rug and coming to rest by {1.2}. Adam stands over it, holding the one-armed mannequin upright by the waist, the empty sleeve-hole at its left shoulder toward the camera. He stares down at the arm and does not move. BACKGROUND: sofa, child mannequin, lamp.", []),
        (6, "MCU, 50mm, a slight handheld breath — the first unsteady camera in the present",
         "Adam on his knees beside the mannequin, which he has sat on the edge of the sofa. He holds the loose arm in both hands and works its ball joint back into the shoulder socket, gently and too fast, fumbling. At {2.6} it clicks in. At {3.8} he lifts the ivory plastic hand and holds it against his forehead, eyes shut. BACKGROUND: the sofa back, lace throw, lamp glow.",
         [(0.4, 2.2, "Adam", "rushed, breaking, barely voiced", "I'm sorry. I'm sorry."), (4.2, 5.4, "Adam", "a whisper into the plastic hand", "Did I hurt you?")]),
    ],
    amb="A hollow plastic knock rocking to stillness. The radio waltz carries on, small and indifferent. In shot two: plastic on plastic, a click, his breath.",
    music="The only music is the distant radio song. It will be replaced by the film's own song in the edit.",
    keep=["The mannequin never reacts. Nothing answers him."])

# ========================================================= 5 · THE KNOCK
run(id="G19", scene="5 · The knock", nums="33", look="P", refs=["L05b_hallway-bag"],
    light="Evening. The hallway is dark; a line of yellowish stairwell light under the front door.",
    logline="A 4-second, 16:9 insert: the front door from inside as three knocks shake its chain.",
    where="Entrance hallway, close on the inside of the front door. Nobody in frame.",
    behind="The dark varnished front door fills the frame; the brass chain and handle at the right; a slice of sage wall at the edge.",
    shots=[
        (4, "Insert, 50mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the upper half of the door, the brass chain hanging slack across its latch. Stillness for a second. Three firm knocks at {1.0}, {1.5} and {2.0}; with each one the chain jumps and swings. It settles, still trembling, by {3.5}. BACKGROUND: door and wall only.", []),
    ],
    amb="Three knocks on solid wood, the chain rattling. Under them, faint from the kitchen, the radio waltz.",
    music="The only music is the faint radio song from another room.",
    keep=["The door stays closed."])

run(id="G20", scene="5 · The knock", nums="34", look="P", refs=["adam", "P05_radio", "L01_kitchen"],
    light="Evening. The bare warm bulb.",
    logline="A 5-second, 16:9 close-up: a man freezes at the sound of knocking, then reaches up and turns the radio off.",
    where="Kitchen. Adam stands by the counter under the shelf with the radio, at the right side of the room.",
    behind="Behind Adam: the tiled backsplash and the stove, soft. Above and beside him at screen right: the shelf with the radio.",
    shots=[
        (5, "CU Adam, 85mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Adam's face, turned sharply toward the hallway off screen left, completely still, listening, not breathing. At {1.8}, without looking away, he reaches his right hand up to the radio at the edge of frame and at {2.6} turns the dial; it clicks off. He stays frozen in the silence, eyes on the hallway. BACKGROUND: backsplash, stove.", []),
    ],
    amb="The radio waltz until 2.6s, then a click and total silence. The wall clock. A pot simmering faintly.",
    music="The radio song stops dead at 2.6s. No music after that.",
    keep=[])

run(id="G21", scene="5 · The knock", nums="35", look="P", refs=["adam", "L05b_hallway-bag"],
    light="Evening. The hallway is dark; yellowish stairwell light in a line under the front door.",
    logline="An 8-second, 16:9 wide down the hallway: a man stands small and still in the middle of the hall while a woman speaks to him through the closed front door.",
    where="Entrance hallway. Adam stands in the middle of the hall, his back to the camera, facing the front door at the far end. The speaker is outside the door and never seen.",
    behind="In front of Adam: the dark front door with a line of light under it, broken by the shadows of two feet. Left: the glazed doors. Right: the mirror and the console with the mail and the bag.",
    shots=[
        (8, "Wide, 35mm, locked, deep focus",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the hallway exactly at the angle of @L05b_hallway-bag. Adam stands dead still in the centre, seen from behind, arms at his sides. Under the door, the two foot-shadows shift once at {2.5}. He does not move, except that at {6.0} his head lowers a little. BACKGROUND: door, light line, console.",
         [(0.6, 1.4, "Mona (off screen, through the door)", "low, steady", "Adam."), (1.8, 3.4, "Mona (off screen, through the door)", "gentle, certain", "I know you're in there."), (4.0, 5.4, "Mona (off screen, through the door)", "tired", "It's been four months..."), (6.2, 7.6, "Mona (off screen, through the door)", "her voice gives a little", "I lost them too.")]),
    ],
    amb="Silence in the apartment, the wall clock. Mona's voice is muffled by the wooden door, with a little stairwell echo behind it.",
    keep=["Mona is never seen. The door stays closed.", "Adam says nothing in this clip."])

run(id="G22", scene="5 · The knock", nums="36 ★, 38", look="P", refs=["adam", "doll-daughter", "L03_living-dim"],
    light="Evening. Warm floor lamp behind the sofa, deep shadow.",
    logline="A 10-second, 16:9 clip in two shots: a father crouches by a child mannequin and puts a finger to his lips; then, alone in close-up, he listens to footsteps going away and for one second his face shows that he knows. (In the edit an insert sits between them.)",
    where="Living room sofa. The child mannequin sits upright in the middle of the sofa. Adam crouches on the floor in front of it, at its left (screen left), his face level with its face.",
    behind="Behind the mannequin: the lace throw and the lamp glow. Behind Adam: the dark room toward the hallway.",
    shots=[
        (5, "CU two-shot, 85mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Adam's face in profile at screen left, close to the blank ivory face of the child mannequin at screen right. He raises one finger to his lips at {0.8} and holds it there, eyes bright, as if it were a game; he gives a tiny nod at {4.0}. The mannequin is perfectly still. BACKGROUND: lace, lamp.",
         [(1.4, 2.0, "Adam", "the softest whisper", "Shh."), (2.4, 4.0, "Adam", "whispered, playful", "We're playing the quiet game.")]),
        (5, "CU Adam, 85mm, locked",
         "Adam alone, frontal, still crouched, head turned slightly toward the hallway off screen left, listening. From {1.0} to {2.2} his jaw trembles and his eyes fill: somewhere, he knows. At {2.6} he swallows, breathes in, and the pleasant mask comes back; he turns to the mannequin off screen right, bright. BACKGROUND: lamp glow, dim wall.",
         [(3.4, 4.5, "Adam", "bright, false, a little too loud", "Who wants dinner?")]),
    ],
    amb="Near silence, the wall clock. In shot two: footsteps going down a stairwell beyond the door, fading out by 2.5s.",
    keep=["The mannequin never moves or reacts."])

run(id="G23", scene="5 · The knock", nums="37 ○", look="P", refs=["mona", "P14_foil-dish", "L09_landing"],
    light="Evening. A dim stairwell bulb, greenish-grey walls.",
    logline="A 4-second, 16:9 floor-level insert on the landing: a woman sets a foil-covered dish down in front of the closed apartment door and walks away. Her face is never shown.",
    where="The landing outside the apartment. The closed apartment door on the right, the doormat in front of it. Mona stands at the door; only her shoes, the hem of her navy dress and long grey cardigan, and her hands are seen.",
    behind="Behind the dish: the bottom of the dark wooden door and the doormat. Left: the first steps of the staircase and its iron railing.",
    shots=[
        (4, "Insert, floor level, 35mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the doormat and the foot of the closed door, a woman's flat shoes standing on the mat. At {0.6} she bends her knees and her two hands lower the foil-covered dish onto the mat, centred against the door. Her hand rests flat on the foil for a moment, leaves at {2.2}, and the shoes turn and walk out of frame to the left toward the stairs by {3.4}. The dish stays. BACKGROUND: door, mat, stairs.", []),
    ],
    amb="Foil crinkling, the dish on the mat, then footsteps going down the stairs with a stairwell echo.",
    keep=["Mona's face is never in frame.", "The apartment door stays closed."])

# ========================================================== 6 · DINNER
run(id="G24", scene="6 · Dinner & the headlights", nums="39, 40", look="P", refs=["adam", "doll-wife", "doll-daughter", "P01_yellow-cup", "L02_dining"],
    light="Night. The curtains behind the table are black; one pendant lamp lights the table in a pool, the room around it dark.",
    logline="A 10-second, 16:9 clip in two shots: the breakfast tableau again, at night, steam rising off three plates while he promises them the sea; then an insert of him pouring water into the yellow cup and not stopping.",
    where="Dining table, frontal, the closed curtains directly behind it. Adam sits on the far side at the centre, facing the camera. The adult mannequin sits at the left end (screen left). The child mannequin sits at the right end (screen right). The near side is empty.",
    behind="Behind Adam: the dark closed curtains. Behind the adult mannequin: curtains and darkness. Behind the child mannequin: curtains, then the sideboard with the clock at the right edge.",
    shots=[
        (6, "Wide frontal, 35mm, locked, dead centre — identical to the breakfast frame",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the whole table square to the camera under the pendant lamp. Three plates of hot rice and stew, steam rising from each, untouched; the yellow cup by the small plate at screen right; a glass water jug by Adam's hand. He leans forward on his forearms, looking from the child mannequin to the adult one as he speaks. Neither moves. He does not eat. BACKGROUND: dark curtains.",
         [(0.6, 2.4, "Adam", "warm, a promise", "Tomorrow we go to the sea."), (2.8, 3.6, "Adam", "earnest", "I promise."), (4.0, 5.6, "Adam", "quieter, to himself as much as them", "This time we'll get there.")]),
        (4, "Insert, 50mm, locked",
         "The yellow cup on the lace cloth, close, the child mannequin's ivory hand resting rigid on the table edge beside it. Adam's hand tilts the glass jug and water fills the cup; at {1.6} it reaches the brim and he keeps pouring. It overflows, runs down the yellow plastic and spreads dark through the lace. He does not stop. BACKGROUND: the lit tablecloth, darkness beyond.", []),
    ],
    amb="The wall clock, steam, forks untouched. In shot two: water pouring, then spilling onto cloth; far outside, a truck horn.",
    keep=["Symmetry in the wide: Adam exactly centred, one mannequin on each side.", "Adam never eats or lifts a fork."])

run(id="G25", scene="6 · Dinner & the headlights", nums="41 ★", look="P", refs=["doll-wife", "doll-daughter", "adam", "L02_dining"],
    light="Night. Pendant lamp over the table. A narrow gap between the curtains.",
    logline="A 5-second, 16:9 hero shot: a vehicle passes in the street and its headlights come through the gap in the curtains, sweep across the wall and slide over two blank plastic faces. Only the light moves.",
    where="Dining table seen from the side. The adult mannequin sits at the near end of the table in profile; the child mannequin sits at the far end, facing it. Adam sits between them on the curtain side, a dark shape, head down.",
    behind="Behind the mannequins: the sage wall with the two framed pictures and the sideboard. At frame left: the closed curtains with a finger-wide gap.",
    shots=[
        (5, "Wide, side angle, 35mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the table in the lamp's pool, the two mannequins motionless, Adam still. At {1.0} a hard white bar of light enters through the gap in the curtains at frame left, sweeps along the wall, crosses the adult mannequin's eyeless face at {2.0} and the child mannequin's face at {2.8}, throwing their shadows across the wall, and is gone by {3.8}. Nothing in the room moves. Adam's head lifts a little at {4.2}. BACKGROUND: wall, pictures, sideboard.", []),
    ],
    amb="A heavy engine approaching, passing low in the street and fading. Water dripping from the table edge.",
    keep=["The light does all the moving. The camera, the mannequins and the furniture are still."])

run(id="G26", scene="6 · Dinner & the headlights", nums="44", look="P", refs=["adam", "P01_yellow-cup", "L02_dining"],
    light="Night. Pendant lamp from above, hard on his face.",
    logline="A 5-second, 16:9 close-up: he comes back from the memory gripping the table edge, the cup on its side, and ends the evening.",
    opens="Opens mid-situation: the yellow cup has been knocked over and water covers the table.",
    where="Dining table. Adam sits on the far side at the centre, facing the camera. The mannequins are off frame at left and right.",
    behind="Behind Adam: the dark closed curtains.",
    shots=[
        (5, "CU Adam, 85mm, a slight handheld breath",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Adam's face, eyes wide, breathing hard through his nose, both hands gripping the table edge at the bottom of the frame; in the foreground the yellow cup lies on its side, water running off the table. He looks slowly to screen left at {1.5}, then to screen right at {2.6}, at each of them. He lets go of the table. BACKGROUND: dark curtains.",
         [(3.2, 3.9, "Adam", "flat, emptied", "...It's late."), (4.1, 4.8, "Adam", "almost inaudible", "Bedtime.")]),
    ],
    amb="Water dripping onto the floor. His breathing. The wall clock.",
    keep=[])

run(id="G27", scene="6 · Dinner & the headlights (flash 4)", nums="42, 43", look="M", refs=["layla", "L07_car-front", "L08_desert-road"],
    light="Dusk: the sun is almost down, the sky orange going blue, the cabin dim.",
    logline="A 5-second, 16:9 memory flash in two shots: through the windshield, a desert road at dusk and headlights blooming far ahead; then Layla's face turning to the road as her smile drops. No impact.",
    where="Front of the car. The first shot is the driver's view through the windshield. In the second, Layla sits in the front right seat, seen from the driver's side.",
    behind="Behind Layla: her side window and the darkening desert.",
    shots=[
        (2.5, "Driver's POV through the windshield, handheld, 24mm",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the dashboard top and the straight two-lane road at dusk through dusty glass. Far ahead a pair of headlights swells and blooms across the dirt on the windshield until the glare covers most of the glass at {2.2}. BACKGROUND: darkening desert, poles.", []),
        (2.5, "CU Layla, handheld, 35mm",
         "Layla in profile, smiling toward the back seat; at {0.6} her eyes go to the road ahead and the smile falls off her face as white light climbs over it. The frame burns out to pure white over the last half second. BACKGROUND: window, dusk.", []),
    ],
    amb="Road hum and a truck horn rising steadily through both shots; cut to nothing on the last frame.",
    keep=["No collision is shown: the clip ends on white before anything happens.", "Adam is not seen in this clip."])

# ========================================================= 7 · BEDTIME
run(id="G28", scene="7 · Bedtime", nums="45", look="P", refs=["adam", "doll-daughter", "L06_nour-room"],
    light="Night. A dark corridor; the only light is the warm star glow from the open bedroom door ahead.",
    logline="A 5-second, 16:9 wide from behind: a man carries a child-size mannequin down a dark corridor toward a room glowing with a star night-light.",
    where="A narrow dark corridor inside the apartment. Adam walks away from the camera down its centre, carrying the child mannequin. The open door of Nour's room is at the far end on the right.",
    behind="Ahead of Adam: the open bedroom door, amber light and drifting star shapes spilling onto the corridor wall and floor. The corridor walls are dark sage.",
    shots=[
        (5, "Wide from behind, 35mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Adam's silhouette from behind, mid-corridor, walking slowly away. The child mannequin lies across his arms, its stiff legs sticking straight out to one side, the braided wig hanging over his elbow, a flash of yellow dress in the glow. He reaches the bedroom door at {4.0} and turns into it sideways so the rigid legs clear the frame. BACKGROUND: the glowing doorway, stars on the wall.", []),
    ],
    amb="Slow bare footsteps. Water dripping, far behind, fading out.",
    keep=["The mannequin stays stiff: nothing about it hangs or drapes like a sleeping child except the wig."])

run(id="G29", scene="7 · Bedtime", nums="46, 47, 48", look="P", refs=["adam", "doll-daughter", "P10_rabbit", "L06_nour-room"],
    light="Night. A small bedside lamp and the star night-light; warm amber on deep blue. After the lamp goes off, only the stars.",
    logline="A 16-second, 16:9 clip in three shots: he tucks the child mannequin into bed and sets the rabbit beside it; he kisses its forehead and stays a moment too long while projected stars drift over his face; from the doorway he switches off the lamp and only the stars remain.",
    where="Nour's bedroom. The bed is against the left wall, the bedside table with the night-light at its head. The child mannequin lies on its back in the bed. Adam sits on the edge of the bed, then stands in the open doorway at the far right.",
    behind="Behind the bed: the sage wall with the taped crayon scribbles, stars drifting across it. Behind Adam when he sits: the curtained window and the small desk. Behind him in the doorway: the black corridor.",
    shots=[
        (6, "MS, 50mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the bed from its foot at a three-quarter angle, the child mannequin lying flat and straight on its back, head on the pillow. Adam, seated on the bed's edge, pulls the patterned blanket up to its plastic chin at {1.5} and smooths it over the stiff shape. At {3.5} he takes the small grey rabbit from the pillow and tucks it beside the mannequin's shoulder, under the blanket's edge. BACKGROUND: scribbles on the wall, stars.", []),
        (6, "CU Adam, 85mm, locked",
         "Adam's face from the side as he leans down and at {1.0} kisses the ivory forehead. He stays there, lips on the plastic, eyes closed, a moment too long, until {3.2}. Star shapes drift slowly over his face and the pillow. He pulls back a few centimetres and speaks. BACKGROUND: the amber dome of the night-light, soft.",
         [(3.8, 4.8, "Adam", "a whisper", "Tomorrow, the sea."), (5.0, 5.8, "Adam", "barely there", "Sleep now.")]),
        (4, "Wide, 35mm, locked",
         "The room exactly at the angle of @L06_nour-room. Adam stands at the open door at far right, his hand on the light switch. He looks back at the bed for a second and at {1.6} presses the switch: the bedside lamp goes out. Only the night-light dome and its slow stars remain; he is a black silhouette in the doorway. BACKGROUND: the bed with the small shape under the blanket at left.", []),
    ],
    amb="Blanket fabric, the faint tick of the night-light motor, his breathing. A light switch click at 13.6s. No clock in this room.",
    keep=["The rabbit is small: about thirty centimetres, smaller than the pillow.", "The mannequin lies rigid; the blanket shows a stiff straight shape."])

run(id="G30", scene="7 · Bedtime", nums="49 ★, 50 ★", look="P", refs=["adam", "L06_nour-room"],
    light="Night. Only the star night-light: slow amber stars over deep blue; his face half in darkness.",
    logline="A 10-second, 16:9 hero clip in two shots: in the doorway, about to leave, he stops; a child's voice behind him says two words; he does not turn around. The camera never shows the bed.",
    where="The open doorway of Nour's bedroom. Adam stands in it facing out toward the dark corridor, the room behind him. The bed is behind him and off frame for the whole clip.",
    behind="Behind Adam: the dim bedroom wall with stars drifting across it. In front of him: the black corridor.",
    shots=[
        (5.5, "CU, profile in the doorway, 85mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Adam in right profile, facing screen right toward the corridor, one hand on the door frame, mid-step. He is leaving. At {1.0} he stops for no reason and stands. Three seconds of nothing. On the voice at {3.6} his whole body locks; his fingers tighten on the frame. He does not turn. BACKGROUND: stars sliding over the wall behind him.",
         [(3.6, 5.2, "Nour (off screen, behind him, close and clear)", "soft, patient, a child asking", "Daddy... look.")]),
        (4.5, "CU face, frontal, 85mm, very slow push-in",
         "Adam's face from the corridor side, the starlit room out of focus behind his shoulder. He stares straight ahead, past the camera. His eyes fill and one tear goes. He shakes his head a fraction as he whispers. On the second voice at {3.0} he shuts his eyes hard. BACKGROUND: blurred stars; the bed is not visible.",
         [(1.0, 2.4, "Adam", "a cracked whisper, not turning", "...Not now, sweetheart."), (3.0, 4.0, "Nour (off screen, brighter, with the acoustics of a car interior)", "delighted, insisting", "Daddy, LOOK!")]),
    ],
    amb="Dead silence and the faint tick of the night-light motor. From 8.5s a warm road hum swells under Nour's second line and is cut off on the last frame.",
    keep=["Adam never turns around. The camera never cuts to or shows the bed or the mannequin.", "Nour is heard only; no child appears."])

# ========================================================= 8 · THE ROAD
run(id="G31", scene="8 · The road", nums="51", look="ML", refs=["P13_family-car", "L08_desert-road"],
    light="Golden hour, sun low ahead of the car.",
    logline="A 5-second, 16:9 exterior: a modest off-white family sedan on a two-lane desert road at golden hour, a line of sea on the horizon, a swim ring pressed against its back window.",
    where="The desert highway. The car drives in the right-hand lane toward the sea and the sun. The camera travels alongside it on its left, slightly behind.",
    behind="Beyond the car: sandy shoulder, low scrub, poles, the thin blue line of sea, the low sun ahead.",
    shots=[
        (5, "Wide exterior, 35mm, smooth tracking alongside",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the off-white sedan in three-quarter rear view, driving steadily, the camera keeping pace beside it. A bright inflatable swim ring is pressed against the inside of the rear window; three heads are dim shapes inside. The camera drifts forward along the car's side until the low sun flares past the roof at {4.0}. BACKGROUND: desert, sea line, sun.", []),
    ],
    amb="Tyres on asphalt, wind, and from inside the car, muffled, the warm old-fashioned waltz on its radio.",
    music="The only music is the song from the car radio, muffled. It will be replaced by the film's own song in the edit.",
    keep=["The road is empty: no other vehicles.", "Smooth tracking, not shaky."])

run(id="G32", scene="8 · The road", nums="52, 53, 54, 55", look="M", refs=["adam-before", "layla", "nour", "L07_car-front", "L07b_car-backseat"],
    light="Golden hour, sun low through the windshield.",
    logline="A 15-second, 16:9 clip in four shots, the family in the car: the two parents from behind, hands joined; the girl drawing on her knees; the mother looking back at her; the father's smiling eyes in the mirror.",
    where="Inside the car, fixed for the whole clip. Adam drives in the front left seat. Layla sits in the front right seat. Nour sits in the back seat on the right, behind Layla, belted, a picture book on her knees with a sheet of paper on it.",
    behind="Behind Adam and Layla (seen from the back seat): the windshield, the straight road and the low sun. Behind Nour: the seat back, her headrest, the swim ring on the rear shelf, the side window with desert passing. Behind Layla when she looks back: her window and the dashboard edge.",
    shots=[
        (4, "From the back seat, between the front seats, handheld, 24mm",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: exactly the angle of @L07_car-front, now with Adam at the wheel on the left and Layla on the right, seen from behind, the sun flaring between them. Layla's left hand lies on Adam's right hand on the gearshift. She sways and la-las along with the radio, flat; at {2.2} he turns his head a little toward her and laughs. BACKGROUND: windshield, road, sun.", []),
        (4, "CU Nour, handheld, 50mm",
         "Nour in the back right seat, head bent over the paper on the book on her knees, drawing hard with a short yellow crayon, the tip of her tongue between her teeth where the tooth is missing. She hums five notes. The drawing itself is hidden by her arm and the angle. BACKGROUND: seat back, swim ring, bright window.", []),
        (4, "CU Layla, handheld, 35mm, from the driver's side",
         "Layla twists in her seat and looks back over her left shoulder at Nour at {0.4}, amused, then turns to Adam off screen left and speaks. BACKGROUND: her window, golden desert.",
         [(1.2, 2.6, "Layla", "mock outrage, laughing under it", "An hour she's been drawing."), (2.8, 3.8, "Layla", "to Adam, delighted", "She won't show me.")]),
        (3, "CU rear-view mirror, handheld, macro",
         "The rear-view mirror against the bright windshield. In it, only Adam's eyes, creased with a smile, flicking up to look at the back seat as he speaks, then back to the road. BACKGROUND: glare, the road out of focus.",
         [(0.6, 2.4, "Adam", "warm, playful, calling back", "What are you drawing, Nour?")]),
    ],
    amb="The waltz on the car radio, road hum, wind at a cracked window, a crayon scratching paper, Nour's hum, Layla's wordless singing and Adam's laugh.",
    music="The only music is the song from the car radio. It will be replaced by the film's own song in the edit.",
    keep=["The drawing is never visible.", "Nour's crayon is yellow, short and finger-thin."])

run(id="G33", scene="8 · The road", nums="56, 57, 58, 59", look="M", refs=["adam-before", "layla", "nour", "L07_car-front", "L07b_car-backseat"],
    light="Golden hour, sun low and straight ahead, strong in Adam's eyes.",
    logline="A 14-second, 16:9 clip in four shots: the girl holds her finished drawing up for her father; he says one minute, he is driving; she insists; her mother laughs and tells him to look. We only ever see the back of the paper.",
    opens="Opens mid-situation: the family is driving; Nour has just finished her drawing.",
    where="Inside the car, fixed for the whole clip. Adam drives in the front left seat. Layla sits in the front right seat. Nour sits in the back seat on the right, behind Layla, belted.",
    behind="Behind Nour: the seat back, her headrest, the swim ring on the rear shelf, the bright rear window. Behind Adam: his side window and the desert. Behind Layla: her side window.",
    shots=[
        (4, "CU Nour, handheld, 50mm, from the front looking back",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Nour finishing a last stroke with the yellow crayon. At {0.8} she lifts the sheet in both hands and holds it up toward the front seats, beaming. We see only the back of the paper, the sun glowing through it: vague coloured shapes, nothing readable. BACKGROUND: rear window, swim ring, glare.",
         [(1.4, 2.8, "Nour", "bursting with pride", "Daddy, look!")]),
        (4, "MCU Adam, handheld, 35mm, from the passenger side",
         "Adam at the wheel in right profile, eyes on the road, squinting into the low sun, smiling. At {0.6} he reaches up and flips the sun visor down. He answers without turning his head. BACKGROUND: his window, desert.",
         [(1.4, 2.4, "Adam", "easy, amused", "One minute, sweetheart."), (2.6, 3.6, "Adam", "light", "I'm driving.")]),
        (3, "CU Nour, handheld, 50mm",
         "Nour leaning forward against her seatbelt, holding the paper higher, right up between the front seats, its back still to us. BACKGROUND: rear window, glare.",
         [(0.4, 2.4, "Nour", "sing-song, stretching the word, will not give up", "Daddyyy. Look!")]),
        (3, "CU Layla, handheld, 35mm, from the driver's side",
         "Layla laughing, her left hand coming across to touch Adam's arm at {0.6}. BACKGROUND: her window, the sun flaring.",
         [(0.8, 2.6, "Layla", "laughing, giving in", "Look at it, or she'll never stop.")]),
    ],
    amb="The waltz on the car radio, road hum, wind, paper rustling.",
    music="The only music is the song from the car radio. It will be replaced by the film's own song in the edit.",
    keep=["The front of the drawing is never visible: only its back, glowing.", "Adam keeps his eyes on the road for this whole clip."])

run(id="G34", scene="8 · The road", nums="60 ★, 61", look="M", refs=["adam-before", "nour", "L07_car-front", "L07b_car-backseat"],
    light="Golden hour, the sun pouring through the rear window behind Nour and across Adam's face.",
    logline="An 8-second, 16:9 hero clip in two shots, slow motion: he turns his head back to look, and his face opens into pure joy; then his view of his daughter, so backlit that the drawing is burned out by the sun.",
    where="Inside the car. Adam drives in the front left seat and turns his head to the right and back. Nour sits in the back seat on the right, belted, holding the paper up toward him.",
    behind="Behind Adam: his side window, the desert, golden. Behind Nour: the rear window blazing with sun, the swim ring a soft shape.",
    shots=[
        (5, "CU Adam, handheld, 50mm, slow motion, from the back seat side",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Adam's face in left three-quarter view from behind his right shoulder, eyes on the road, a smile already starting. From {0.5} to {2.5}, in slow motion, he turns his head to the right and back toward the camera. As his eyes land on what she is holding, at {3.0}, his whole face opens: delight, pride, love, a laugh beginning. This is the happiest image in the film. Sunlight slides across his face. BACKGROUND: his window, gold.", []),
        (3, "His POV, handheld, 35mm, slow motion",
         "Nour in the back right seat, beaming, missing tooth, holding the sheet of paper up in both hands toward us. The sun is directly behind it and behind her: the paper is a blazing white-gold rectangle, completely burned out, with her fingers dark at its edges and her face glowing beside it. BACKGROUND: the rear window, pure sun.", []),
    ],
    amb="All sound drops to a muffled underwater hush. Only a child humming five notes stays clear and close. No radio, no engine.",
    keep=["The drawing is still never seen: the sun burns it out completely.", "Slow motion in both shots.", "Nothing outside the car is shown through the windshield in this clip."])

run(id="G35", scene="8 · The road", nums="62, 63", look="M", refs=["layla", "L07_car-front"],
    light="Golden hour tipping into glare: white light building from ahead.",
    logline="A 5-second, 16:9 clip in two shots: Layla's eyes go to the road and her smile falls as she says his name; then, through the windshield, headlights filling the glass. It ends on white. No impact.",
    where="Front of the car. Layla sits in the front right seat, seen from the driver's side. Then the view straight through the windshield.",
    behind="Behind Layla: her side window. Through the windshield: the road and the oncoming lights.",
    shots=[
        (2.5, "CU Layla, handheld, 35mm",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Layla laughing, looking toward Adam. At {0.5} her eyes flick to the road ahead; the smile falls; white light rises across her face. BACKGROUND: window, gold.",
         [(1.3, 2.0, "Layla", "sharp, cut off", "Adam—")]),
        (2.5, "Through the windshield, handheld, shaking, 24mm",
         "The dusty windshield from between the seats: two huge headlights and the high flat front of a truck, bleaching the glass, growing until at {1.8} the whole frame is white. Hold pure white to the end. BACKGROUND: nothing but light.", []),
    ],
    amb="A truck horn, full and close, through both shots. On the last frame everything cuts to silence.",
    keep=["No collision, no glass breaking, no impact: the clip ends on pure white.", "Adam and Nour are not seen in this clip."])

run(id="G36", scene="8 · The road", nums="65 ★", look="ML", refs=["P12_crayons", "L08_desert-road"],
    light="Dusk, after sunset: blue-grey ambient light, an orange hazard light blinking out of focus.",
    logline="A 5-second, 16:9 hero shot on the ground: a yellow crayon rolls slowly across asphalt at dusk and stops against crumbs of safety glass. The camera is locked. No people.",
    where="The road surface. The camera lies on the asphalt. Nobody in frame.",
    behind="Far out of focus: the sandy shoulder, a soft orange light blinking on and off about once a second, the dark blue sky.",
    shots=[
        (5, "Ground-level macro, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: coarse asphalt in close-up filling the lower two thirds of the frame, a scatter of small glittering cubes of safety glass at right of centre. At {0.5} a short yellow wax crayon rolls slowly in from the left, crosses the frame, and at {3.2} comes to rest against the glass crumbs. It rocks once and is still. The orange light keeps blinking in the blur behind. BACKGROUND: blur, dusk.", []),
    ],
    amb="Near silence. A thin high tone. A hazard-light relay ticking slowly, like a clock.",
    keep=["Only the crayon is yellow and sharp. No bodies, no blood, no car, no debris other than the small glass crumbs.", "This shot is locked, not handheld."])

run(id="G37", scene="8 → 9 · Asphalt to floor (match cut)", nums="66 ★, 67 ★", look="ML", refs=["adam", "L06_nour-room"],
    light="Shot one: dusk, blue-grey, an orange hazard light blinking. Shot two: night, amber projected stars turning slowly.",
    logline="A 10-second, 16:9 hero clip built on one MATCH CUT: an extreme close-up of a man's open eye, his cheek on asphalt at dusk; cut to the same eye, same size, same angle, his cheek on a bedroom floor four months later. Keep the eye exactly centred in both shots.",
    where="Shot one: Adam lies on his left side on the road, his left cheek on the asphalt, the camera on the ground a few centimetres from his face. Shot two: Adam lies in exactly the same position on the terrazzo floor of Nour's bedroom.",
    behind="Shot one: blurred asphalt, the orange blink, dusk sky. Shot two: blurred terrazzo floor, the edge of the small round rug, slow stars on the wall.",
    shots=[
        (4, "ECU, ground level, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Adam's right eye, open, filling the centre of the frame, the bridge of his nose at one edge, his cheek pressed on rough asphalt along the bottom. Clean-shaven skin, dust on it, no wounds. The orange light blinks in the wet of his eye about once a second. At {1.5} a sheet of white paper drifts across the far background, out of focus. He does not blink. BACKGROUND: asphalt, dusk.", []),
        (6, "ECU, floor level, locked — MATCH CUT",
         "MATCH CUT. Same lens, same angle, same eye in the same place at the same size, same pose. On the cut frame the asphalt becomes speckled terrazzo and the orange blink becomes small amber stars turning slowly over his face. He now has stubble, and the healed scar shows at the edge of frame by his temple. He blinks, once, at {1.5}. A tear gathers and runs across the bridge of his nose at {4.0}. BACKGROUND: terrazzo, rug edge, stars.", []),
    ],
    amb="Shot one: a thin high tone, a hazard relay ticking, his shallow breath. On the cut the tick continues without a break and becomes the soft tick of the night-light motor; the tone is gone.",
    keep=["4.0s is a hard cut that changes only the ground, the light and the stubble: the eye stays in exactly the same place and size.", "No blood, no injury in either shot.", "Locked camera in both shots, not handheld."])

# ======================================================= 9 · THE FLOOR
run(id="G38", scene="9 · The floor", nums="68 ★", look="P", refs=["doll-daughter", "P10_rabbit", "L06_nour-room"],
    light="Night. Only the star night-light: amber stars drifting over deep blue.",
    logline="A 5-second, 16:9 hero shot from the floor: the bed, and under the blanket, plainly, a child-size plastic figure with its wig askew. Nothing moves. Nothing speaks.",
    where="Nour's bedroom, seen from the floor beside the bed, looking up. The child mannequin lies on its back in the bed, the blanket to its chin, the rabbit beside its shoulder. Nobody else in frame.",
    behind="Behind the bed: the sage wall, the taped scribbles, slow stars. At the head of the bed: the glowing dome on the bedside table.",
    shots=[
        (5, "Low angle from the floor, 35mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the side of the bed from floor level, the mattress edge across the lower frame. On the pillow, in profile, the smooth ivory head of the child mannequin: no eyes, no mouth, the braided wig slipped sideways off a bare plastic scalp, a seam at the neck above the blanket. The small grey rabbit beside it. It is an object under a blanket. Only the projected stars move, slowly, across it and the wall. BACKGROUND: wall, scribbles, stars.", []),
    ],
    amb="Silence. The faint tick of the night-light motor.",
    keep=["Absolutely nothing moves except the projected stars.", "No voice, no breath, no music."])

run(id="G39", scene="9 · The floor", nums="69 ★, 70 ○", look="P", refs=["adam", "L06_nour-room"],
    light="Night going to dawn. Amber stars on deep blue; by the last shot the edge of the curtain turns from blue to grey-gold.",
    logline="A 12-second, 16:9 hero clip in two shots: he pulls himself up against the bed and finally breaks, silently, then aloud, the first real crying in the film; then a wide of the room as dawn reaches the window and he has not moved.",
    where="Nour's bedroom. Adam sits on the floor with his back against the side of the bed, at the left of the room. The bed and what lies in it are behind and above him.",
    behind="Behind Adam: the side of the bed and the hanging edge of the patterned blanket. In the wide: the curtained window on the back wall, the desk at right, the open door at far right.",
    shots=[
        (8.5, "MS, 50mm, locked, no cut",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Adam on the floor, pushing himself up from lying to sitting, his back coming to rest against the bed frame at {1.5}, knees drawn up. He stares at nothing. At {2.5} his face folds and he cries without sound, mouth open, shoulders shaking; at {5.0} the sound comes, low and broken; he presses the heels of his hands into his eyes at {7.0}. Stars drift over him. The shape in the bed above him is only a dark edge of blanket. BACKGROUND: bed side, blanket.", []),
        (3.5, "Wide, 35mm, locked",
         "The room at the angle of @L06_nour-room. Adam sits small against the bed, head down on his knees, not moving. Over the shot the line of light at the edge of the curtain changes from night blue to pale grey-gold and the projected stars fade against the brightening wall. BACKGROUND: window, desk, door.", []),
    ],
    amb="His crying: silent at first, then voiced. The night-light motor. In the last shot, the first birds outside.",
    music="From 5.0s, very sparse score: five single slow piano notes. It will be replaced by the film's own score in the edit.",
    keep=["The crying is real and unpretty; he never looks at the camera.", "The mannequin is not shown clearly in this clip."])

# ========================================================= 10 · THE BAG
run(id="G40", scene="10 · The bag", nums="71", look="P", refs=["adam", "L05b_hallway-bag"],
    light="Dawn. Grey-blue light through the glazed doors; the hallway is cold and pale.",
    logline="A 5-second, 16:9 wide down the hallway: he walks slowly to the console by the front door and stops in front of it.",
    where="Entrance hallway. Adam walks away from the camera down the middle of the hall toward the front door, then stops at the console on the right wall.",
    behind="Ahead of Adam: the dark front door. Right: the mirror and the console with the mail, the dead plant and the bag. Left: the glazed doors, pale with dawn.",
    shots=[
        (5, "Wide, 35mm, locked — the same hallway frame as the knock",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the hallway exactly at the angle of @L05b_hallway-bag, Adam entering the bottom of the frame from behind the camera, barefoot, seen from behind. He walks slowly up the hall. At {3.5} he stops at the console and turns to face it, his profile toward us, looking down at what is on it. His hands hang at his sides. BACKGROUND: front door, console, mirror.", []),
    ],
    amb="Bare feet on terrazzo. First birds, faint. The building asleep.",
    music="One long held piano note. It will be replaced by the film's own score in the edit.",
    keep=["He does not touch anything on the console in this clip."])

run(id="G41", scene="10 · The bag", nums="72, 73, 74", look="P", refs=["adam", "P06_hospital-bag", "P07_bag-contents", "L05b_hallway-bag"],
    light="Dawn. Cold pale light from the left; the console top in soft grey.",
    logline="A 14-second, 16:9 clip in three shots: his hands lift the sealed hospital bag out from under the mail and tear it open; a top shot of what was in it, laid on the wood; his hands unfold the sheet of paper, its back to us.",
    where="The console by the front door. Adam stands at it; only his hands and forearms are in frame in all three shots.",
    behind="Under his hands: the dark wood of the console top, dusty, with envelopes pushed to one side. Behind: the sage wall.",
    shots=[
        (4.5, "CU hands, 50mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the console top, the dusty sealed bag half under a slide of blank envelopes. Adam's hands come in; at {0.8} he draws the bag out and dust slides off it. He holds it in both hands, thumbs on the seal, and does not move until {2.6}. Then he tears the seal open along the top. BACKGROUND: wood, envelopes, wall.", []),
        (5, "Top shot straight down, 35mm, locked — an echo of the three plates",
         "The console top from directly above. One at a time his hand sets down, in a row: at {0.5} the gold watch with the brown strap, its glass cracked, its hands stopped; at {1.6} a wedding ring; at {2.6} a short stub of yellow crayon; at {3.6} a sheet of paper folded in four, creased and dirty. His hand withdraws. BACKGROUND: dark dusty wood only.", []),
        (4.5, "CU hands, 50mm, locked",
         "His hands lift the folded paper from the wood and unfold it, once at {1.2}, twice at {2.6}, holding it upright toward his own face. We see only the back of the sheet: grey-white paper, fold lines, faint colour ghosting through. His thumbs tremble. BACKGROUND: wall, soft.", []),
    ],
    amb="Envelopes sliding, thick plastic tearing, a watch, a ring and a crayon set on wood, paper unfolding, his breath.",
    keep=["The front of the drawing is not visible in this clip.", "The watch glass is cracked and its hands do not move.", "No writing on the bag, the envelopes or the paper."])

run(id="G42", scene="10 · The bag", nums="75 ★", look="P", refs=["adam", "L05b_hallway-bag"],
    light="Dawn. Cold pale light from the left, a little warmth beginning in it.",
    logline="A 6-second, 16:9 hero close-up with a very slow push-in: his face as he finally looks at his daughter's drawing. Grief, and then, impossibly, a breath of a laugh.",
    where="The hallway by the console. Adam stands holding the unfolded sheet of paper in both hands just below the frame; its top edge shows at the bottom of the picture, back to us.",
    behind="Behind Adam: the sage wall and the edge of the wall mirror, out of focus.",
    shots=[
        (6, "CU Adam, 85mm, very slow push-in for the whole shot",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Adam's face, eyes lowered to the paper he holds. His eyes move over it slowly. At {1.2} his face breaks, brows drawing together, tears coming; at {2.6}, through it, a short breath of a laugh escapes him and he half smiles, wrecked. He nods very slightly as he speaks, eyes never leaving the paper. BACKGROUND: wall, mirror edge.",
         [(3.2, 4.4, "Adam", "a whisper, breaking and smiling at once", "...I'm looking, sweetheart."), (4.8, 5.6, "Adam", "softer, steadier", "I'm looking.")]),
    ],
    amb="His breath, the paper trembling slightly. Birds outside.",
    music="Sparse piano: the five notes, slowly. It will be replaced by the film's own score in the edit.",
    keep=["The front of the drawing is not visible.", "His eyes stay on the paper for the whole shot."])

# ====================================================== 11 · DAYLIGHT
run(id="G43", scene="11 · Daylight", nums="77 ★", look="PW", refs=["adam", "doll-wife", "doll-daughter", "L03_living-dim", "L03b_living-day"],
    light="Morning. The shot begins in the closed-curtain gloom and ends in full sun.",
    logline="A 6-second, 16:9 hero shot: he drags the heavy curtains open and daylight floods the living room for the first time in the film. (Keep him and the window in the centre of the frame.)",
    where="Living room. Adam stands at the curtains on the right-hand wall, his back to the room. Both mannequins sit side by side on the sofa in the middle of the room, facing forward.",
    behind="Behind Adam: the olive-grey curtains, then the window and the city. Left of him: the sofa with the two mannequins, the coffee table, the armchair, the bookshelf.",
    shots=[
        (6, "MS, 35mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the room as in @L03_living-dim, dim, Adam in the centre-right of frame from behind, a hand on each curtain. At {1.0} he pulls them apart in one long drag, rings scraping. Hard morning sun bursts in and by {3.0} the room looks as in @L03b_living-day: sun shafts across the rug and floor, dust swirling thick in the beam, the city in the window. He stands in the light with his arms still out, squinting, then lets them drop at {5.0}. The two mannequins on the sofa are lit flat and plain by the sun and do not move. BACKGROUND: window, city.", []),
    ],
    amb="Curtain rings scraping on the rail. Then the street, alive for the first time: traffic, voices, a street vendor calling without distinct words, sparrows.",
    keep=["The mannequins never move.", "Composition is centre-safe: nothing important in the outer sixth of the frame on either side."])

run(id="G44", scene="11 · Daylight", nums="78, 79", look="PW", refs=["adam", "doll-wife", "doll-daughter", "L03b_living-day"],
    light="Morning. Hard sunlight from the open window on the right.",
    logline="An 11-second, 16:9 clip in two shots: in hard daylight he stands looking at two mannequins on the sofa, objects in borrowed clothes; then his hands unbutton the burgundy cardigan, fold it and press it to his face for one breath.",
    where="Living room, curtains open. The adult mannequin sits at the left of the sofa and the child mannequin at the right, side by side, facing forward. Adam stands in front of the sofa at screen left, facing them, his back three-quarters to the camera.",
    behind="Behind the mannequins: the lace throw on the sofa back, the floor lamp (off), the sewing corner. Right: the open window, sun and city. Behind Adam: the bookshelf wall.",
    shots=[
        (5, "Wide, 35mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the room exactly at the angle of @L03b_living-day. Adam stands still, arms at his sides, looking at the sofa. In the sun the two figures are plainly things: scuffed plastic, visible seams, a cheap crooked wig, pins glinting in the yellow dress. Dust drifts through the light. At {3.5} he takes one step toward the adult mannequin. BACKGROUND: sewing corner, window.", []),
        (6, "CU hands, 50mm, locked",
         "Adam's hands at the front of the burgundy cardigan on the adult mannequin's rigid torso. He undoes three buttons, top to bottom, at {0.6}, {1.3} and {2.0}, slides the cardigan off the stiff shoulders at {3.0}, and folds it once against his chest. At {4.4} he lifts it and presses it to his face, into frame, eyes closed, and breathes in. BACKGROUND: the grey dress on the ivory torso, sunlight.", []),
    ],
    amb="Street sound through the open window. Buttons, wool sliding off plastic, one long breath in.",
    keep=["The mannequins never move; the adult one is handled like a shop dummy.", "No music in this clip."])

run(id="G45", scene="11 · Daylight", nums="80 ★", look="PW", refs=["adam", "doll-wife", "doll-daughter", "L03b_living-day"],
    light="Morning. The curtains at the right are open; sun falls across the sewing table and the stands.",
    logline="A 6-second, 16:9 hero shot: both mannequins are back on their stands in the sewing corner. He lays the loose yellow sleeve over the small one's shoulder and steps back.",
    where="The living room in daylight, the sewing corner at the back right beyond the sofa. The adult mannequin stands on the left steel stand, bare: no wig, no cardigan, no dress, plain ivory plastic. The child mannequin stands on the right stand, no wig, still wearing the unfinished yellow dress. Adam stands beside the child mannequin, on its left.",
    behind="Foreground: the armchair and the corner of the dining table. Midground: the sofa and the coffee table, sun across the rug. Background: the two mannequins on their stands by the framed mirror, the sewing table and machine, the open window and sunlight at right.",
    shots=[
        (6, "Wide, 35mm, locked — the living-room frame, the sewing corner at the back",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the living room exactly at the angle of @L03b_living-day, the sewing corner at the back in daylight, the two mannequins upright on their stands where the clean circles were. Adam holds the small yellow sleeve in both hands. At {1.5} he lays it over the child mannequin's bare shoulder, where the missing sleeve belongs, and smooths it once. At {3.5} he takes two steps back toward the sewing table and stands looking at them, hands empty. The needle of the machine is bare now. BACKGROUND: mirror, open curtains, sun.", []),
    ],
    amb="Street sound, softer. Cloth on plastic. His two steps.",
    music="Warm, quiet score: piano, the five notes. It will be replaced by the film's own score in the edit.",
    keep=["The mannequins are shop objects on stands: rigid, bald, eyeless, still.", "The yellow dress and sleeve are the only saturated colour."])

# ======================================================= 12 · THE DOOR
run(id="G46", scene="12 · The door", nums="81", look="PW", refs=["L05_hallway"],
    light="Morning. Daylight reaches the hallway from the open rooms; the door is no longer in darkness.",
    logline="A 4-second, 16:9 insert: the front door from inside, three knocks, softer than last time.",
    where="Entrance hallway, close on the inside of the front door. Nobody in frame.",
    behind="The dark varnished front door fills the centre of the frame; brass chain and handle at right; sage wall at both edges.",
    shots=[
        (4, "Insert, 50mm, locked — the same insert as the first knock",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the upper half of the door, the brass chain slack across its latch, soft daylight on the wood. Three gentle knocks at {1.0}, {1.6} and {2.2}; the chain barely trembles. Stillness. BACKGROUND: door, wall.", []),
    ],
    amb="Three soft knocks on wood. Distant street sound from inside the apartment.",
    keep=["The door stays closed in this clip."])

run(id="G47", scene="12 · The door", nums="82", look="PW", refs=["adam", "L05_hallway"],
    light="Morning. Daylight from the rooms behind the camera; the hallway is clear and pale.",
    logline="A 5-second, 16:9 wide down the hallway: this time he walks all the way to the door, slides the chain and puts his hand on the handle.",
    where="Entrance hallway. Adam walks away from the camera down the middle of the hall to the front door at the far end.",
    behind="Ahead of Adam: the front door. Right: the mirror and the console, with the mail and the dead plant and NO bag. Left: the glazed doors, bright.",
    shots=[
        (5, "Wide, 35mm, locked — the same hallway frame as the knock",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the hallway exactly at the angle of @L05_hallway, Adam already in the middle of the hall, seen from behind, walking steadily to the door. He reaches it at {2.2}. At {2.8} he slides the chain off; at {3.6} his hand closes on the handle. He stands, shoulders rising with one breath, and does not open it yet. BACKGROUND: door, console, mirror.", []),
    ],
    amb="Bare footsteps, the chain sliding and dropping, one breath.",
    keep=["The door is still closed on the last frame.", "There is no plastic bag on the console."])

run(id="G48", scene="12 · The door", nums="83, 84 ★", look="PW", refs=["mona", "adam", "P14_foil-dish", "L09_landing"],
    light="Morning. The stairwell is dim and grey-green; warm daylight spills out of the apartment as the door opens.",
    logline="An 11-second, 16:9 clip in two shots: from the landing, the door opens on him, and Mona, holding a covered dish, understands before he speaks; then close on him as he tries, fails, and finally says it.",
    where="The landing outside the apartment. Mona stands on the doormat facing the door, a foil-covered dish in both hands; yesterday's identical dish sits on the floor by her feet. Adam stands in the doorway, inside, facing her.",
    behind="Behind Mona: the stairs with the iron railing and the small frosted window. Behind Adam: the bright hallway of the apartment, daylight.",
    shots=[
        (5, "Wide two-shot from the landing, 50mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: Mona from behind and to the side at screen left, in three-quarter back view, facing the closed dark door at screen right, the dish in her hands, the other dish at her feet. At {0.8} the door opens inward and warm daylight falls across her. Adam stands in the doorway: grey-blue shirt, bare feet, eyes red. They look at each other. Her face, seen in three-quarter profile, changes at {3.0}: she understands. She does not speak. BACKGROUND: stairs behind her, bright hallway behind him.", []),
        (6, "CU Adam, 85mm, locked",
         "Adam's face in the doorway, frontal, lit softly from the stairwell, the bright hall behind him. He opens his mouth at {0.8} and nothing comes. He looks down, swallows, looks back up at her at {2.4}. Then he says it, plainly, for the first time; after it his face gives way. BACKGROUND: the daylit hallway, out of focus.",
         [(3.2, 5.0, "Adam", "quiet, plain, the first true sentence", "They're gone, Mona.")]),
    ],
    amb="The door latch and hinge, stairwell echo, street sound from inside the apartment. No one speaks until Adam's line.",
    keep=["Mona says nothing in this clip.", "Two foil dishes: one in her hands, one on the floor by her feet."])

run(id="G49", scene="12 · The door", nums="85 ★", look="PW", refs=["adam", "mona", "P09_drawing", "P01_yellow-cup", "L05_hallway"],
    light="Morning. The open front door is the brightest thing in the frame; the foreground is in soft shade.",
    logline="A 6-second, 16:9 hero wide from inside the apartment: she steps in and holds him, two silhouettes in the bright doorway, while in the soft foreground the drawing stands propped against the yellow cup.",
    where="Inside the apartment, looking down the hallway to the open front door. Adam stands just inside the doorway; Mona steps in from the landing and embraces him. In the near foreground, at the lower left, the corner of the lace-covered dining table with the drawing leaning upright against the yellow cup.",
    behind="Behind the two figures: the open door and the bright stairwell, burning out. Hallway walls, console and mirror at the sides.",
    shots=[
        (6, "Wide, 35mm, locked",
         "THE VERY FIRST FRAME OF THE CLIP IS THIS: the hallway receding to the open door, Adam a dark figure in it, his head down. In the foreground, soft and out of focus, the yellow cup and the crayon drawing propped against it: the huge yellow sun, three small figures, a strip of blue. At {1.0} Mona steps over the threshold and puts her arms around him; he stands rigid, then at {2.8} folds into her, his forehead on her shoulder. They hold, two silhouettes in the light. At {5.0} the focus eases forward to the drawing. BACKGROUND: the bright doorway.", []),
    ],
    amb="Street sound, far. Cloth, one long shaking breath out.",
    music="Full, warm score: piano and strings completing the five-note tune. It will be replaced by the film's own score in the edit.",
    keep=["The camera does not move; only the focus shifts at the end.", "The drawing shows no words."])

EDIT_ONLY = [
    ("01", "Black screen, 6s", "Sound only: road hum, wind, crayon on paper, a child humming five notes, a woman's soft laugh, a seatbelt click. Build it from the audio of G09, G12 and G32."),
    ("64", "White to black, 3s", "The white at the end of G35, held, then cut to black. A thin high tone."),
    ("76 ★", "The drawing, 5s", "Use the real image @P09_drawing full frame with a slow drift in the edit. Do not regenerate it: a video model will redraw it."),
    ("02–75", "4:3 crop", "Crop every present-day shot before the curtains to 4:3 from the centre."),
    ("77", "Aspect change", "Animate the crop from 4:3 open to 16:9 across G43."),
    ("86", "Title, 4s", "Black. Title: LOOK. The child's five-note hum, unfinished."),
    ("87", "Credits card, 3s", "One card, plus an AI-tools disclosure if the rules ask for one."),
]

ELEMENT_IDS = [
    ("adam", "9c70b944-13a8-4231-93db-404db1428192"), ("adam-before", "bfb6bcd3-e1df-4cdb-9d4d-fb1e5aadaad1"),
    ("layla", "e712cf1e-37e2-40f8-b6a7-199f095de10b"), ("nour", "c28a7770-b7af-4503-a6a5-ee7e13731382"),
    ("mona", "fc203cad-8f11-4cb7-af5d-9f7e3aaeee2f"), ("doll-wife", "31a8cb88-f0e0-40b5-ac7c-f17e5e7caa36"),
    ("doll-daughter", "28cdcfad-7312-4812-ac4e-a0215f63b939"),
]


# ------------------------------------------------------------------ build
def fmt(t):
    return f"{t:.1f}"


def build_prompt(r):
    aspect, look = LOOKS[r["look"]]
    out = [r["logline"]]
    if r.get("opens"):
        out.append(r["opens"])
    out.append("\nREFERENCES")
    for h in r["refs"]:
        out.append(f"@{h} — {REF[h]}")
    out.append("\nLOOK\n" + look + " " + r["light"])
    chars = [CHAR[h] for h in r["refs"] if h in CHAR]
    if chars:
        out.append("\nCHARACTERS\n" + "\n".join(chars))
    has_doll = any(h.startswith("doll-") for h in r["refs"])
    if has_doll:
        out.append("\n" + MANNEQUIN_RULE)
    out.append("\nWHERE EVERYONE IS — fixed for the whole clip\n" + r["where"])
    out.append("\nWHAT IS BEHIND EACH OF THEM\n" + r["behind"])
    out.append("\nSHOTS")
    t = 0.0
    lines = []
    for dur, head, text, ls in r["shots"]:
        start = t

        def sub(m, start=start):
            return fmt(start + float(m.group(1))) + "s"
        body = re.sub(r"\{(\d+(?:\.\d+)?)\}", sub, text)
        for a, b, who, how, words in ls:
            assert b <= dur + 1e-6 and a < b, (r["id"], words)
            body += f" {fmt(start + a)}–{fmt(start + b)}s, {who}, {how}: \"{words}\""
            lines.append(f"{fmt(start + a)}s {who} \"{words}\"")
        out.append(f"{fmt(start)}–{fmt(start + dur)}s — {head}. {body}")
        t += dur
    assert abs(t - round(t)) < 1e-6 and 4 <= t <= 30, (r["id"], t)
    r["dur"] = int(round(t))
    out.append("\nSOUND")
    out.append(r.get("music") or "No music, no score, no stings.")
    out.append("Ambience: " + r["amb"])
    if lines:
        out.append("Voices: clean, close, natural dialogue recording, dry, no echo unless stated. All speech is in English.")
        out.append("Lines, each spoken exactly once and nothing else: " + " · ".join(lines))
        out.append("No added words, no other voices, no narration.")
    else:
        out.append("No dialogue. No voices, no narration, no added words.")
    keep = []
    for h in r["refs"]:
        if h in CHAR:
            name = CHAR[h].split(" — ")[0]
            keep.append(f"{name}'s face, hair and clothes exactly as @{h} in every frame.")
    if "adam" in r["refs"] and r["look"] not in ("M", "ML"):
        keep.append("Adam always has the stubble and the healed scar at his right temple.")
    if has_doll:
        keep.append("The mannequins are rigid plastic objects with no eyes and no mouth; they never move, blink or breathe on their own.")
    base = [k for k in KEEP[r["look"]] if not ("@adam-before" in k and "adam-before" not in r["refs"])]
    if r["look"] == "M" and not any(h in r["refs"] for h in ("adam-before", "layla", "nour")):
        base = [k for k in base if not k.startswith("Seats never change")]
    keep += base + r.get("keep", [])
    if lines:
        keep.append("Each line is spoken once, at its time, by its speaker; nobody else speaks.")
    out.append("\nKEEP CONSISTENT")
    out += ["- " + k for k in keep]
    return "\n".join(out), aspect


def main(md_path, html_path):
    built = []
    for r in RUNS:
        p, aspect = build_prompt(r)
        built.append((r, p, aspect))
    total = sum(r["dur"] for r, _, _ in built)
    md = ["# LOOK — Seedance 2.5 prompts", "",
          f"**{len(built)} generations · {total} seconds of footage** for the 87-shot film. "
          "Every block is one generation: attach the listed elements, paste the prompt, set the duration and aspect, run it as a draft, and finalise the takes you like in 1080p.", "",
          "## Settings for every run", "",
          "- Model: **Seedance 2.5 Draft**. Generate a liked draft again in 1080p.",
          "- Audio on. Radio song and score in the clips are placeholders; the film's own 5-note music replaces them in the edit.",
          "- Aspect: **16:9 for every run.** The present (scenes 1–10) is framed centre-safe and cropped to 4:3 in the edit; the frame opens to full width on the curtain shot.",
          "- `@name` in a prompt is the element of that name in the project *baba look*. Attach exactly the elements listed above each prompt.",
          "- All dialogue is English. \"Baba\" is now \"Daddy\", \"habibti\" is \"sweetheart\", \"Mama\" is \"Mommy\".",
          "- Continuous action is one run with timed shots inside it. Where a memory flash interrupts a scene, the scene is still one run and the flash is cut in during the edit.",
          "- ★ marks a hero shot. ○ marks a shot that can be dropped.", "",
          "## Run list", "",
          "| Run | Scene | Shots | Length | Aspect | Elements to attach |", "|---|---|---|---|---|---|"]
    for r, _, aspect in built:
        md.append(f"| [{r['id']}](#{r['id'].lower()}) | {r['scene']} | {r['nums']} | {r['dur']}s | {aspect} | "
                  + ", ".join(f"`{h}`" for h in r["refs"]) + " |")
    md += ["", "## Made in the edit, not generated", "", "| Shot | What | How |", "|---|---|---|"]
    for s, w, h in EDIT_ONLY:
        md.append(f"| {s} | {w} | {h} |")
    md += ["", "## Prompts", ""]
    for r, p, aspect in built:
        md += [f"### {r['id']}", "",
               f"**{r['scene']} · shots {r['nums']} · {r['dur']}s · {aspect}**  ",
               f"{SETTINGS} · duration {r['dur']}s · aspect {aspect}  ",
               "Attach: " + ", ".join(f"`{h}`" for h in r["refs"]), "",
               "```text", p, "```", ""]
    open(md_path, "w").write("\n".join(md))

    e = html.escape
    rows = "".join(
        f"<tr><td><a href='#{r['id']}'>{r['id']}</a></td><td>{e(r['scene'])}</td><td>{e(r['nums'])}</td>"
        f"<td>{r['dur']}s</td><td>{aspect}</td><td>{e(', '.join(r['refs']))}</td></tr>" for r, _, aspect in built)
    cards = "".join(
        f"<section id='{r['id']}'><header><h2>{r['id']}</h2><div class='meta'><b>{e(r['scene'])}</b> · shots {e(r['nums'])}"
        f" · <span class='pill'>{r['dur']}s</span> <span class='pill'>{aspect}</span></div>"
        f"<button onclick=\"cp(this)\">Copy prompt</button></header>"
        f"<div class='att'>Attach: {''.join(f'<code>{e(h)}</code>' for h in r['refs'])}</div>"
        f"<pre>{e(p)}</pre></section>" for r, p, aspect in built)
    edit = "".join(f"<tr><td>{e(s)}</td><td>{e(w)}</td><td>{e(h)}</td></tr>" for s, w, h in EDIT_ONLY)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LOOK Prompts</title><style>
:root{{--bg:#f6f4ef;--fg:#1d1c1a;--mut:#6b675f;--card:#fff;--line:#ddd8cc;--acc:#b8860b}}
@media(prefers-color-scheme:dark){{:root{{--bg:#151412;--fg:#ece8df;--mut:#9a958a;--card:#1f1e1b;--line:#35322c;--acc:#e3b341}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}}
main{{max-width:980px;margin:0 auto;padding:24px 16px 80px}}h1{{font-size:28px;margin:0 0 4px}}h2{{margin:0;font-size:20px}}
p.lead{{color:var(--mut);margin:0 0 20px}}ul{{padding-left:20px}}
.tw{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:13px;margin:8px 0 24px}}td,th{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}}
a{{color:var(--acc)}}section{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin:18px 0}}
header{{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center}}.meta{{flex:1;min-width:200px;color:var(--mut)}}
.pill{{border:1px solid var(--line);border-radius:99px;padding:1px 8px;color:var(--fg);font-size:12px}}
button{{background:var(--acc);color:#111;border:0;border-radius:6px;padding:7px 12px;font-weight:600;cursor:pointer}}
.att{{margin:10px 0;font-size:13px;color:var(--mut)}}code{{background:var(--bg);border:1px solid var(--line);border-radius:4px;padding:1px 5px;margin:0 3px 3px 0;display:inline-block;color:var(--fg)}}
pre{{white-space:pre-wrap;word-break:break-word;background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:12px;font:13px/1.5 ui-monospace,monospace;margin:0}}
</style></head><body><main>
<h1>LOOK — Seedance 2.5 prompts</h1>
<p class="lead">{len(built)} generations · {total} seconds of footage · 87-shot film</p>
<ul><li><b>Seedance 2.5 Draft</b>, audio on. Generate liked drafts again in 1080p.</li>
<li><b>16:9 for every run.</b> The present is framed centre-safe and cropped to 4:3 in the edit.</li>
<li>Attach exactly the elements listed on each card; <code>@name</code> in the prompt is that element.</li>
<li>All dialogue is English: Daddy, sweetheart, Mommy.</li>
<li>Radio song and score in the clips are placeholders for the film's own music.</li></ul>
<h2>Run list</h2><div class="tw"><table><tr><th>Run</th><th>Scene</th><th>Shots</th><th>Length</th><th>Aspect</th><th>Elements</th></tr>{rows}</table></div>
<h2>Made in the edit</h2><div class="tw"><table><tr><th>Shot</th><th>What</th><th>How</th></tr>{edit}</table></div>
{cards}</main><script>
function cp(b){{const t=b.closest('section').querySelector('pre').innerText;navigator.clipboard.writeText(t).then(()=>{{b.textContent='Copied';setTimeout(()=>b.textContent='Copy prompt',1200)}})}}
</script></body></html>"""
    open(html_path, "w").write(page)
    print(len(built), "runs,", total, "seconds")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
