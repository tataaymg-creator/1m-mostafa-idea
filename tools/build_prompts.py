#!/usr/bin/env python3
"""Builds prompts.md and prompts.html: every Seedance 2.5 generation for LOOK,
written to the seedance-clean structure.

Usage: python3 tools/build_prompts.py prompts.md prompts.html

{name} in text is an attached element and becomes @image1, @image2... in
attach order; <1.5> means 1.5 s after the segment starts.
"""
import html
import re
import sys

ANCHOR = {
    "adam": "Adam, 38, lean and tired; short untidy dark hair, stubble, a healed scar at his right temple; washed-out grey-blue shirt with rolled sleeves, charcoal trousers, bare feet, wedding ring; soft, low, slightly hoarse voice",
    "adam-before": "Adam, 38, healthy and relaxed; clean-shaven, smooth unmarked temples; light linen shirt, wedding ring; warm easy voice",
    "layla": "Layla, 34, warm and quick to laugh; shoulder-length dark wavy hair, burgundy cardigan over a cream floral dress, slim gold watch, wedding ring; bright voice",
    "nour": "Nour, 6; two loose braids, a gap where a front tooth is missing, white t-shirt, denim shorts, yellow sandals; clear small voice",
    "mona": "Mona, mid-forties; grey-streaked hair in a bun, tortoiseshell glasses, navy dress, long grey cardigan; low steady voice",
    "doll-wife": "adult shop mannequin: matte ivory plastic, smooth blank face with only a sculpted nose and brow, crooked dark wig, burgundy cardigan over a grey dress, seams at neck, shoulders and wrists; a rigid object",
    "doll-daughter": "child-size shop mannequin: matte ivory plastic, smooth blank face with only a sculpted nose and brow, dark wig in two uneven braids, unfinished yellow dress with pins, white tacking thread and one sleeve missing; a rigid object",
    "P01_yellow-cup": "the child's yellow plastic cup",
    "P02_table-setting": "two large plain plates, one small plate and three forks",
    "P03_yellow-sandal": "a small yellow child's sandal with a metal buckle",
    "P04_hairbrush": "a worn wooden hairbrush",
    "P05_radio": "an old portable radio: grey body, round speaker grille, cream handle, two dials",
    "P06_hospital-bag": "a sealed clear plastic belongings bag with a blank label, holding a gold watch, a ring, a yellow crayon stub and a folded sheet of paper",
    "P07_bag-contents": "a gold watch with a brown strap and cracked glass, a wedding ring, a stub of yellow crayon, a folded dirty sheet of paper",
    "P09_drawing": "a child's crayon drawing: three figures holding hands, a strip of blue sea, a little car, a huge yellow sun",
    "P10_rabbit": "a small worn grey stuffed rabbit, about 30 cm tall",
    "P12_crayons": "worn paper-wrapped wax crayons, each about 8 cm long and finger-thin, the yellow one shortest",
    "P13_family-car": "a modest older off-white four-door sedan with a plain unbadged body",
    "P14_foil-dish": "an oven dish covered with aluminium foil",
    "L01_kitchen": "the kitchen: curtained window and sink at left, white enamel gas stove at centre, wooden counter with a cutting board at right, the radio on a wall shelf above it, sage walls, terrazzo floor",
    "L02_dining": "the dining area: table with a cream lace cloth and four wooden chairs in front of tall closed olive-grey curtains, sideboard with a mantel clock at right, pendant lamp above, kitchen doorway at right",
    "L03_living-dim": "the living room, curtains closed: floral armchair front left, grey sofa with a lace throw at centre, low coffee table, bookshelf on the left wall, floor lamp glowing behind the sofa, sewing corner at the back right with the black sewing machine, a tall framed mirror and two steel stands, closed curtains on the right wall",
    "L03b_living-day": "the same living room from the same camera, curtains open, morning sun across the rug, the city in the window at right, the sewing corner at the back right",
    "F10_living-blocking": "a frame from this same living room: take the room, the camera position and where the figures sit — the adult mannequin in the floral armchair at front left, the child mannequin seated upright at the left end of the sofa beside the armchair. Use it for geometry and placement only",
    "L05_hallway": "the entrance hallway: glazed doors on the left, the dark front door at the far end, coat hooks, a wall mirror and a narrow console with a dead plant and mail on the right",
    "L05b_hallway-bag": "the entrance hallway: glazed doors on the left, the dark front door at the far end, coat hooks, a wall mirror and a narrow console on the right holding a dead plant, mail and a sealed plastic bag",
    "L06_nour-room": "a child's bedroom at night: small bed against the left wall with a rabbit on the pillow, star night-light on the bedside table, curtained window on the back wall, small desk with paper and crayons at right, open door at far right, crayon scribbles taped above the bed",
    "L07_car-front": "the car cabin seen from the back seat: left-hand drive, grey-beige fabric seats, plain grey dashboard with a simple radio, rear-view mirror, the straight desert road ahead",
    "L07b_car-backseat": "the car's back seat: grey-beige bench seat, seatbelt on the right-hand side, a picture book with a sheet of paper, small crayons, a swim ring on the rear shelf",
    "L08_desert-road": "a straight two-lane desert highway at golden hour, sandy shoulders, low scrub, poles, a thin line of sea on the horizon",
    "L09_landing": "the stairwell landing: the dark wooden apartment door at right, a doormat, stairs with an iron railing at left, a small frosted window",
}
CHARS = ("adam", "adam-before", "layla", "nour", "mona")
DOLLS = ("doll-wife", "doll-daughter")
STYLE = {
    "P": "Photoreal naturalistic film image, fine organic grain, soft contrast. A shut-in apartment palette: sage-green paint, grey upholstery and faded wood, with yellow objects carrying the only saturated colour. 16:9, composed centre-safe: faces, hands and key props sit inside the middle two-thirds of the frame.",
    "PW": "Photoreal naturalistic film image, fine organic grain, soft contrast. Daylight fills the apartment: sage-green paint, grey upholstery and faded wood made plain by the sun, with yellow objects carrying the only saturated colour. 16:9.",
    "M": "Photoreal naturalistic film image, fine organic grain, warm amber sunlight on living skin, soft lens flare and fine dust on the glass. 16:9.",
    "ML": "Photoreal naturalistic film image, fine organic grain, soft contrast, the light of a remembered evening. 16:9.",
}
TONAL = "Tonal character: wide latitude, gentle highlight roll-off, rich detail held in the shadows."
OPTIC = {
    "P": "Clean rectilinear primes, natural perspective, crisp centre, soft falloff at the edges.",
    "PW": "Clean rectilinear primes, natural perspective, crisp centre.",
    "M": "Rectilinear primes wide open, shallow focus, warm flare when the sun enters frame, natural motion blur.",
    "ML": "Rectilinear primes, shallow focus, natural motion blur.",
}
LOCKS = {
    "P": ["The camera stays on a tripod, locked, in every segment unless that segment names a move.",
          "The curtains stay closed; the light comes from lamps and the glow through the curtains.",
          "Yellow objects hold the only saturated colour.",
          "Every paper, label and envelope is blank."],
    "PW": ["The camera stays on a tripod, locked, in every segment.",
           "Yellow objects hold the only saturated colour.",
           "Every paper, label and envelope is blank."],
    "M": ["The camera is handheld, close and breathing.",
          "Every paper shows a blank back; the car is plain and unbadged."],
    "ML": ["The camera is steady in every segment.",
           "The scene stays quiet and whole: a still road, intact skin, a calm surface."],
}
SKIN = "Real skin with visible pores and fine texture, living eyes with catch-lights, breath visible in the chest and shoulders."
SETTINGS = "Seedance 2.5 Draft · 16:9 · audio ON"
RUNS = []


def run(**kw):
    RUNS.append(kw)


# ================================================================= 1 · MORNING
run(id="G01", scene="1 · Morning", nums="02, 04", look="P", attach=["adam", "L01_kitchen"],
    ctx="Early morning in the small, dim kitchen of an older city apartment. A gas burner is lit under a small pot, then {adam} stands at the counter on the right of the room, his back to the camera, cutting toast into triangles. He is alone.",
    map="Camera inside the kitchen as in {L01_kitchen}. Foreground: the white enamel stove. Midground: the wooden counter on the right with the cutting board. Background: the tiled backsplash, the wall shelf with the radio above the counter, the thin curtain over the window at left glowing with daylight.",
    first="The first frame is a front burner of the white enamel stove filling the frame, a small aluminium pot on it, {adam}'s fingers on the knob.",
    segs=[(4, None, "ECU", "12°", "locked, low at burner height",
           "His fingers turn the knob. At <0.3> the igniter clicks and a ring of blue flame catches under the pot. At <1.5> the hand withdraws. The flame burns steady and even.", []),
          (6, "HARD CUT", "MS from behind", "47°", "locked, at shoulder height, slightly to his left",
           "{adam} at the counter, waist up, seen from behind, sleeves rolled. He trims the crusts off two slices of golden toast with a bread knife, at <2.5> slices them corner to corner into triangles, and at <4.5> lifts them onto a plate. His face stays turned toward the counter.", [])],
    perf="He works slowly and carefully, like a man doing it for someone he loves. From 5.0s to 8.0s he hums five slow notes, slightly flat.",
    phys="The blue flame flickers gently in still air. The knife meets the board with soft wooden taps; crumbs fall onto the board.",
    light="Key: soft daylight glowing through the thin closed curtain at left, wrapping the room from behind. A single bare warm bulb overhead adds a small pool on the counter. The blue flame lights the pot from below in the first segment. Exposure set for the counter; the curtain glows near white. White balance 5000K. Dust haze 10%.",
    audio="Igniter click, gas hiss, a wall clock ticking, a fridge humming, knife on board, Adam's quiet hum.",
    locks=["The radio on the shelf stays silent and switched off."])

run(id="G02", scene="1 · Morning", nums="03", look="P", attach=["P02_table-setting", "P01_yellow-cup", "L02_dining"],
    ctx="Early morning at a dining table in a dim apartment. Seen from directly above, a man's hands lay the table for three: two large plates, one small plate, three forks and a yellow cup.",
    map="Camera directly above the table in {L02_dining}, looking straight down. The whole frame is the cream lace tablecloth over dark wood. The hands enter from the bottom edge.",
    first="The first frame is the empty lace-covered table top seen from directly above.",
    segs=[(5, None, "Top shot", "63°", "locked, straight down, centred on the table",
           "A man's hands with a wedding ring and rolled grey-blue sleeves come in from the bottom edge. At <0.5> he sets a large plate at the left, at <1.5> a large plate at the right, at <2.5> the small plate at the top centre, all from {P02_table-setting}. At <3.3> he lays one fork beside each plate. At <4.2> he sets {P01_yellow-cup} beside the small plate and his hands leave the frame.", [])],
    perf="Each object is placed with care and lined up square.",
    phys="Ceramic lands on lace with a soft weight; the plates sit flat with contact shadows.",
    light="Soft grey daylight from the closed curtains, low and even, slightly stronger from the top of frame. Exposure for the white plates. White balance 5000K.",
    audio="Ceramic on wood, forks on lace, a wall clock ticking.",
    locks=["The table holds exactly three plates, three forks and one yellow cup, all empty."])

run(id="G03", scene="1 · Morning", nums="05, 06", look="P", attach=["adam", "doll-wife", "doll-daughter", "L02_dining"],
    ctx="Early morning. Seen through the kitchen doorway, {adam} serves breakfast to two figures seated at the dining table against glowing closed curtains; the figures read only as black silhouettes. Then a close-up of him speaking to one of them and waiting for an answer.",
    map="Camera in the dark kitchen, looking through the doorway into {L02_dining}. Foreground: the dark varnished door frame on both edges. Midground: the table, the adult figure seated at its left end and the child-size figure at its right end, both in profile. Background: the tall closed curtains, glowing bright.",
    first="The first frame is the dark door frame framing the laid table, two still black silhouettes seated at its ends against the glowing curtains.",
    segs=[(6, None, "WS through the doorway", "63°", "locked, eye level, inside the dark kitchen",
           "The two silhouettes sit perfectly still. At <0.8> {adam} walks in from the right with a plate of toast in each hand, sets one before the left figure at <2.2> and one before the right figure at <3.4>, and stands between them, a silhouette too.",
           [(3.8, 5.4, "Adam", "warm, quiet, an ordinary morning", "Good morning, my loves.")]),
          (4, "HARD CUT", "CU", "29°", "locked, eye level, on the shadow side of his face",
           "{adam}'s face in three-quarter view, looking down and to frame right at someone seated out of frame. Tired, gentle, the scar at his right temple catching the side light. He smiles, speaks, and then holds still with his eyebrows slightly raised, waiting. At <3.2> a small breath of a laugh, as if he heard a reply.",
           [(0.4, 2.2, "Adam", "fond, lightly scolding", "Nour, sit up straight, sweetheart.")])],
    perf="His waiting is the acting: eyes fixed on one spot, lips parted, a two-second listening pause.",
    phys="The plates land with a light knock on the table. The silhouettes hold the stillness of furniture.",
    light="Strong backlight from the closed curtains; exposure set for the bright curtains, so the seated figures and Adam in the wide fall to solid black silhouettes with clean edges. In the close-up, soft window light from frame right rakes across his face, the far side in shadow. White balance 5000K.",
    audio="A wall clock ticking, plates on wood. After his second line, only the clock.",
    locks=["In the wide, the two seated figures are pure black silhouettes against the curtains."])

run(id="G04", scene="1 · Morning", nums="07 ★", look="P", attach=["adam", "doll-wife", "L02_dining"],
    ctx="Early morning at the dining table. {adam} bends to kiss the forehead of his wife, seated in profile, and the focus slides from his lips to her face: she is {doll-wife}, a mannequin.",
    map="Camera at the side of the table in {L02_dining}, at seated head height. Foreground: the mannequin's head in left profile at frame left. Midground: Adam leaning in from frame right. Background: the closed curtains, soft and glowing.",
    first="The first frame is {adam}'s face in focus as he leans down toward a seated figure whose head, in left profile at frame left, is soft and out of focus.",
    segs=[(5, None, "CU two-shot", "29°", "locked, at seated head height, a slow rack focus",
           "At <1.2> his lips touch the forehead and his eyes close. From <1.8> to <3.5> the focus racks from his lips to the head he is kissing: smooth matte ivory plastic, the edge of a wig, a seam at the neck, a blank face. At <4.0> he straightens and leaves the top of the frame; the plastic profile stays sharp and perfectly still.", [])],
    perf="A tender, ordinary kiss held for one breath, eyes closed, shoulders relaxed.",
    phys="The mannequin's head holds the same profile angle for the whole shot. His lips meet hard plastic and flatten slightly.",
    light="Soft daylight through the closed curtains behind the mannequin, a rim on the wig and the plastic profile, Adam's face lit softly from frame right. White balance 5000K.",
    audio="A wall clock. The kiss makes a small hollow tap on plastic.",
    locks=["The camera holds its position for the whole shot; only the focus moves.",
           "The mannequin stays in the same left profile from the first frame to the last."])

run(id="G05", scene="1 · Morning", nums="08 ★", look="P", attach=["adam", "doll-wife", "doll-daughter", "P01_yellow-cup", "L02_dining"],
    ctx="Early morning, a symmetrical frontal wide of the dining table. {adam} sits at the centre facing the camera, {doll-wife} at the left end and {doll-daughter} at the right end. Three plates of toast, untouched. He talks to them, his hands still beside his plate.",
    map="Camera square to the table in {L02_dining}, the closed curtains directly behind it. Foreground: the empty near edge of the table. Midground: Adam at centre, the adult mannequin at frame left, the child mannequin at frame right, both turned toward the table. Background: the glowing curtains across the full width, the sideboard with the clock at the right edge.",
    first="The first frame is the whole table dead centre and symmetrical, all three seated, {P01_yellow-cup} beside the small plate at frame right.",
    segs=[(6, None, "WS frontal", "63°", "locked, dead centre, eye level",
           "{adam} sits with his hands flat beside his plate, looking at the child mannequin, and speaks to it. At <3.5> he turns his head to the adult mannequin and gives a small private smile. Both mannequins hold perfectly still.",
           [(0.8, 2.8, "Adam", "light, conversational, to the child mannequin", "Mommy's almost finished your dress.")])],
    perf="Easy, domestic, completely sincere. After the line he waits, listening.",
    phys="The toast sits on the plates with crumbs and contact shadows; the forks lie flat.",
    light="Soft backlight from the closed curtains, gentle frontal fill from the room so the three faces read. White balance 5000K. Dust haze 10%.",
    audio="A wall clock ticking. After the line, a silence the length of a reply.",
    locks=["Perfect symmetry: Adam centred, one mannequin on each side.", "His fork and his plate stay untouched."])

run(id="G06", scene="1 · Morning", nums="09 ○", look="P", attach=["adam", "L01_kitchen"],
    ctx="Morning in the kitchen. Seen from above, the hand of {adam} scrapes a plate of untouched toast triangles into a white plastic pedal bin already full of identical dry toast from other mornings.",
    map="Camera above an open pedal bin standing on the terrazzo floor of {L01_kitchen}, beside the base of a cream cabinet.",
    first="The first frame is the open bin seen from above, filled with layers of dry golden toast triangles.",
    segs=[(4, None, "Insert from above", "47°", "locked, looking down into the bin",
           "At <0.6> {adam}'s hand and forearm, his washed-out grey-blue sleeve rolled to the elbow and his wedding ring on, tip a plate over the bin and a fork scrapes three fresh toast triangles onto the pile. At <2.8> the plate lifts away and the lid swings shut.", [])],
    perf="One practised, unhurried movement.",
    phys="The triangles slide off the plate and land with soft weight on the pile; the lid closes with a light bounce.",
    light="Soft daylight from the curtained window above the frame, even and dim. White balance 5000K.",
    audio="Fork scraping ceramic, toast landing, the lid closing. A wall clock, faint.",
    locks=["The bread is golden-brown toast cut in triangles.", "The bin is a white plastic pedal bin."])

run(id="G07", scene="1 · Morning", nums="10", look="P", attach=["P06_hospital-bag", "L05b_hallway-bag"],
    ctx="Morning in the entrance hallway. A very slow push-in on the narrow console by the front door: four months of unopened mail, a dead plant, car keys, and half buried under the mail a dusty sealed plastic belongings bag.",
    map="Camera in the hallway of {L05b_hallway-bag}, three-quarter on the console on the right wall. Foreground: the console top. Midground: the mail pile, the plant, the keys and {P06_hospital-bag}. Background: the sage wall and the lower frame of the wall mirror; the dark front door at the left edge.",
    first="The first frame is the whole console at a three-quarter angle, the bag lying half covered by a slumped pile of envelopes.",
    segs=[(5, None, "MS to insert", "47°", "slow push-in at 1 km/h for the whole shot, ending with the bag filling half the frame",
           "The camera creeps toward the bag. Through the dusty plastic a gold watch, a ring and a stub of yellow crayon show faintly. Dust drifts in the air; everything on the console lies still.", [])],
    perf="",
    phys="A grey film of dust lies on the plastic and the envelopes. The bag lies flat, its corners pinned under the mail.",
    light="Cool soft light from the glazed doors at frame left, the console in gentle shade. White balance 5000K. Dust haze 10%.",
    audio="A wall clock, further away. A neighbour's door closing somewhere in the building.",
    locks=["The bag lies half under the mail, sealed and dusty.", "The camera move is a steady push from first frame to last."])

run(id="G08", scene="1 · Morning", nums="11, 14", look="P", attach=["adam", "doll-daughter", "P03_yellow-sandal", "L02_dining"],
    ctx="Morning in the dining area. {doll-daughter} sits on a wooden chair, a yellow sandal already on its rigid plastic foot. In an extreme close-up, {adam}'s finger and thumb press the sandal's small buckle shut with a sharp click. The click freezes him; then a close-up of him on his knees, coming back to himself.",
    map="Camera low in {L02_dining}, beside a wooden chair turned out from the table. First segment: the camera is a hand's width from the mannequin's ankle. Second segment: Adam's face, kneeling on the terrazzo in front of the chair. Background: the chair legs, the hanging edge of the lace cloth, the dim sideboard.",
    first="The first frame is an extreme close-up of one smooth ivory plastic ankle and foot already sitting in {P03_yellow-sandal}; the thin yellow ankle strap is already threaded through the small metal buckle and lies loose, and {adam}'s thumb and forefinger rest on the buckle.",
    segs=[(4, None, "ECU", "12°", "locked, at ankle height",
           "His thumb draws the strap one notch tighter and at <1.6> presses the buckle's pin home; it snaps shut with a sharp click. His fingers stop dead on the click and stay resting on the buckle, perfectly still, until the end of the segment.", []),
          (6, "HARD CUT", "CU", "29°", "locked, at his kneeling eye level, on the shadow side of his face",
           "{adam}'s face, his eyes level with the mannequin's knees, which are a soft yellow blur at the frame edge. He is frozen, eyes unfocused, breath held. At <1.0> he blinks twice. At <1.8> two fingers of his right hand rise to the scar at his temple. At <3.4> he shakes his head once and looks up at the mannequin with a thin smile.",
           [(4.2, 5.4, "Adam", "under his breath, covering", "...Where were we.")])],
    perf="The freeze is total stillness, then a tiny swallow before he moves. The smile is a mask put back on.",
    phys="The plastic foot and ankle are hard and fixed; only the strap and the buckle move under his fingers. The buckle snaps shut with a sharp metallic click.",
    light="Soft daylight from the curtains at frame right, raking across his right temple so the scar reads clearly. Low fill. White balance 5000K.",
    audio="A small leather creak of the strap, then one sharp metallic buckle click. In the second segment, two seconds of silence, then the wall clock fades back in.",
    locks=["The sandal is on the foot from the first frame; the only action in the first segment is the buckle closing.", "The foot and ankle are smooth ivory plastic, the same material as the mannequin's face."])

run(id="G09", scene="1 · Morning (flash 1)", nums="12, 13", look="M", attach=["nour", "L07b_car-backseat", "P12_crayons"],
    ctx="A memory at golden hour on the back seat of a moving family car: a small hand clicks a seatbelt shut, then a girl's legs swing off the edge of the seat. She is seen from the shoulders down.",
    map="Camera close on the right-hand side of the back seat of {L07b_car-backseat}. Foreground: the seatbelt buckle, then her knees and legs. Midground: the grey-beige seat with the picture book and {P12_crayons} beside her. Background: the door card and the side window with golden desert passing.",
    first="The first frame is the side of the back seat at hip height: the seatbelt buckle standing up from the seat cushion at her left hip, her small right hand pulling the belt's metal tongue down toward it, the belt running from above her right shoulder diagonally across her white t-shirt.",
    segs=[(2.5, None, "ECU", "12°", "handheld, close, breathing",
           "Her hand pushes the metal tongue down into the buckle at her hip and at <0.6> it clicks in. The belt now crosses her body correctly: the shoulder strap diagonally from her right shoulder down across her chest to her left hip, the lap strap flat across her thighs. She lets go and pats it once. Dust glitters in the low sun.", []),
          (2.5, "HARD CUT", "CU", "63°", "handheld, close, at seat height",
           "{nour}'s legs, seen from the waist down, hang off the edge of the seat and swing in turn, yellow sandals on both feet. Beside her the small crayons roll a little with the motion of the car.", [])],
    perf="Restless, happy, six-year-old energy in the legs.",
    phys="The car sways gently at 80 km/h; the crayons roll a few centimetres and back. The seat fabric creases under her weight.",
    light="Low golden sun raking through the side window from frame right, long warm streaks across the seat, flare on the buckle. White balance 5600K.",
    audio="A sharp seatbelt click, then warm road hum; in the second segment a child humming five notes, cut off on the last frame.",
    locks=["Framing stays at her shoulders and below in both segments.", "The seatbelt is worn the normal way: shoulder strap diagonal across the chest, lap strap across the thighs, buckle at the hip.",
           "The crayons are paper-wrapped wax crayons with blunt worn tips, small and finger-thin."])

# =================================================================== 2 · HAIR
run(id="G10", scene="2 · Hair", nums="15", look="P", attach=["adam", "doll-daughter", "doll-wife", "L03_living-dim"],
    ctx="Late morning in the living room. {adam} carries {doll-daughter} across the room the way you carry a sleeping child and sits it upright on the sofa. {doll-wife} already sits in the floral armchair at front left, facing the sofa.",
    map="Camera at the room's entrance, exactly as in {L03_living-dim}. Foreground: the armchair at frame left with the adult mannequin. Midground: the sofa at centre, the coffee table, Adam's path from frame left to the sofa. Background: the floor lamp glowing, the sewing corner at the back right, the closed curtains on the right wall.",
    first="The first frame is the living room at the angle of {L03_living-dim}, the adult mannequin seated still in the armchair, Adam entering from frame left.",
    segs=[(5, None, "WS", "63°", "locked, eye level",
           "{adam} walks in from frame left, his back mostly to the camera, the child mannequin held against his chest: one arm under its stiff straight legs, which stick out sideways, his other hand cradling the back of its head. At <3.0> he lowers it onto the middle of the sofa, sitting it upright, and at <4.3> settles its head with one hand.", [])],
    perf="Slow, protective steps, his head bent toward the figure.",
    phys="The child mannequin is light, hollow and stiff as a board: its legs and arms keep their angle in his arms and on the sofa. The sofa cushion dips under its weight.",
    light="Curtains closed; the floor lamp behind the sofa is the warm key, the rest of the room in soft grey-green shade. Exposure for the sofa. White balance 4300K so the lamp reads warm amber. Dust haze 10%.",
    audio="Bare footsteps on terrazzo, a small creak of hollow plastic, the wall clock.",
    locks=[])

run(id="G11", scene="2 · Hair", nums="16, 17, 20", look="P", attach=["adam", "doll-daughter", "doll-wife", "P04_hairbrush", "L03_living-dim"],
    ctx="Late morning on the living-room sofa. {adam}, seated at the right of {doll-daughter}, brushes its wig and tries to braid it; the brush snags and the wig slides off bare plastic; then, guiltily, he puts it back. {doll-wife} sits in the armchair out of frame to the left.",
    map="Camera beside the sofa in {L03_living-dim}. Midground: the child mannequin upright in the middle of the sofa, facing forward; Adam seated at its right (frame right), turned toward it. Background: the lace throw on the sofa back, the warm floor lamp, the dim sage wall.",
    first="The first frame is {adam} in left profile at frame right, the child mannequin's wigged head in profile at frame left, {P04_hairbrush} in his right hand on the wig.",
    segs=[(6, None, "MCU two-shot in profile", "29°", "locked, at seated head height",
           "He draws the brush down the wig, holding a clumsy half-made braid in his left hand. At <3.0>, still speaking, he glances past the camera toward the armchair and smiles like a man sharing a secret.",
           [(1.0, 3.4, "Adam", "low, fond, to the child mannequin", "Mommy does it better, I know."),
            (3.9, 5.4, "Adam", "a conspirator's whisper", "Don't tell her I said that.")]),
          (4, "INSERT CUT", "ECU", "12°", "locked, on the brush in the wig",
           "At <0.8> the bristles snag. He tugs, and at <1.6> the whole wig slides sideways in one piece, uncovering a bare shiny ivory plastic scalp with a seam line. His hand stops.", []),
          (5, "HARD CUT", "CU", "29°", "locked, on the shadow side of his face",
           "{adam}'s face in three-quarter view, breath caught, eyes on the plastic just below frame. At <1.0> both his hands slide the wig back into place; at <3.0> he smooths it down twice with his palm, like stroking a child's hair.",
           [(1.4, 2.2, "Adam", "a whisper, ashamed", "Sorry."),
            (3.0, 4.4, "Adam", "softer still", "Sorry, sweetheart.")])],
    perf="Clumsy, loving fingers. In the last segment his lips press together and his eyes stay down.",
    phys="The mannequin's head holds its angle; only the wig moves, pulled by the brush and by his hands. Synthetic hair slides as one cap.",
    light="Warm floor-lamp key from behind the sofa, a rim on the wig and on Adam's profile; soft grey fill from the room. White balance 4300K.",
    audio="Bristles through synthetic hair, the wall clock; a dry slide of wig on plastic; his breathing.",
    locks=["The child mannequin faces forward in every segment."])

run(id="G12", scene="2 · Hair (flash 2)", nums="18, 19 ○", look="M", attach=["nour", "layla", "L07b_car-backseat"],
    ctx="A memory at golden hour in the back of a moving car: {nour}, belted in the back right seat by an open window, laughs with her eyes closed as the wind whips her hair; then her mother's hand reaches back from the front seat and tucks the hair behind her ear.",
    map="Camera in the back of {L07b_car-backseat}, close on Nour. Foreground: her face, then her shoulder. Midground: the seat back and headrest; Layla's arm reaching from the front right seat between seat and door. Background: the bright open window, golden desert rushing past at 80 km/h, the swim ring on the rear shelf.",
    first="The first frame is {nour}'s face filling the frame, eyes closed, mouth open in a laugh, loose strands of her braids flying.",
    segs=[(3, None, "CU", "63°", "handheld, very close",
           "She laughs, the gap of her missing tooth showing, hair whipping across her face. At <1.5> a burst of sun flare crosses the lens.", []),
          (3, "HARD CUT", "CU", "47°", "handheld, slightly wider",
           "A woman's left hand in a burgundy sleeve, wedding ring and slim gold watch on it, reaches back from the front seat; at <1.0> it tucks the flying hair behind {nour}'s ear. The ring flashes in the sun at <1.6>. Nour opens her eyes and grins toward the front.", [])],
    perf="Pure, unselfconscious laughter; then a pleased grin at her mother.",
    phys="Wind lifts and whips loose hair at the open window; the hand moves against it gently.",
    light="Low golden sun through the open window, strong warm backlight on her hair, flare. White balance 5600K.",
    audio="Wind roar at the window, her laugh, road hum; a car radio, faint.",
    locks=["The front-seat woman appears only as an arm and a hand: {layla}'s burgundy sleeve, watch and ring."])

# ===================================================== 3 · THE SEWING CORNER
run(id="G13", scene="3 · The sewing corner", nums="21", look="P", attach=["L03_living-dim"],
    ctx="Late morning in an empty living room. The camera pushes slowly across the room to the dressmaker's sewing corner at the back: a black sewing machine still threaded with yellow, a small yellow sleeve under its needle, two empty steel mannequin stands beside the mirror.",
    map="Camera starts at the room's entrance exactly as in {L03_living-dim} and travels toward the back right corner. Foreground: the armchair and coffee table, passing out of frame. Midground: the sofa and floor lamp. Background, growing: the sewing table and machine, the paper patterns on the wall, the framed mirror and the two steel stands.",
    first="The first frame is the living room at the angle of {L03_living-dim}, empty and still, the sewing corner small at the back right.",
    segs=[(5, None, "WS to MS", "47°", "slow push-in at 2 km/h for the whole shot, toward the sewing machine",
           "The camera glides past the sofa toward the corner. The two steel stands stand empty, each in a clean circle in the dust on the floor. The push ends with the sewing machine and the yellow sleeve under its needle in the centre of the frame. Dust drifts in the lamp light.", [])],
    perf="",
    phys="Dust motes float in the lamp's warm beam; everything in the room holds still.",
    light="Curtains closed with one thin blade of daylight at their edge; the floor lamp is the warm key near the corner. White balance 4300K. Dust haze 15%.",
    audio="The wall clock. At 3.5s, from another room, a radio dial clicks on and soft static begins.",
    locks=["The room is empty; the two stands stay bare.", "The paper patterns are blank shapes."])

# ================================================== 4 · THE SONG & THE DANCE
run(id="G14", scene="4 · The song & the dance", nums="22, 23, 26", look="P", attach=["adam", "doll-wife", "P05_radio", "L01_kitchen"],
    ctx="Evening in the kitchen. {adam} tunes the old radio to a warm old song, cooks at the stove while {doll-wife} stands rigid in the doorway where he has placed her, and then, close on him, holds out a hand and asks her to dance.",
    map="Camera inside {L01_kitchen}. Foreground left: the adult mannequin standing in the doorway, seen from behind its shoulder. Midground: Adam at the stove, side-on. Background: the tiled backsplash, the dark curtained window at left, the wall shelf with {P05_radio} at right.",
    first="The first frame is {P05_radio} on its wall shelf, close, {adam}'s fingers on its right-hand dial.",
    segs=[(4, None, "Insert", "12°", "locked, on the radio",
           "His fingers turn the dial slowly through static, and at <2.4> a warm, slow, old-fashioned waltz settles in. His hand rests on the radio and leaves at <3.5>.", []),
          (5, "HARD CUT", "MS", "47°", "locked, eye level",
           "{adam} at the stove, side-on, stirring a pot with a wooden spoon and swaying slightly to the music. {doll-wife} stands in the left foreground in the doorway, perfectly still. At <1.0> he tastes from the spoon, then speaks over his shoulder toward the doorway with a half smile.",
           [(2.0, 4.2, "Adam", "teasing, easy, over his shoulder", "You always say I put too much salt.")]),
          (4, "HARD CUT", "CU", "29°", "locked, on the shadow side of his face",
           "{adam}'s face turned toward the doorway, a real smile, eyes wet. At <0.8> he wipes his hands on a cloth below frame. At <2.0> he holds one open hand out toward the doorway at frame left.",
           [(2.3, 3.4, "Adam", "quiet, shy, sincere", "Dance with me.")])],
    perf="Lightness in his shoulders for the first time; in the close-up his chin trembles once before the line.",
    phys="Steam rises from the pot; the spoon drips. The mannequin's weight rests evenly on both feet.",
    light="Night outside; the bare warm bulb overhead is the key, the stove flame a small blue accent. White balance 4300K so the bulb reads amber.",
    audio="Radio static resolving into the song, which keeps playing small and tinny from the radio. A pot simmering, the wooden spoon. The only music is that radio song.",
    locks=["The mannequin in the doorway stands rigid in one pose for the whole clip."])

run(id="G15", scene="4 · The song & the dance (flash 3)", nums="24, 25 ★, 29", look="M", attach=["layla", "adam-before", "L07_car-front"],
    ctx="A memory at golden hour in the front of a moving car. {layla}, in the front right seat, turns the car radio up, sings along badly, laughs at herself and turns to look at her husband; her hand rests on his on the gearshift. Adam appears only as his right hand.",
    map="Camera on the driver's side of {L07_car-front}, looking across at Layla. Foreground: the gearshift and the plain grey dashboard with its simple radio. Midground: Layla in the front right seat. Background: her side window, golden desert sliding past at 80 km/h.",
    first="The first frame is the simple car radio in the grey dashboard, a woman's hand with a burgundy cuff reaching for the volume knob.",
    segs=[(3, None, "Insert", "12°", "handheld, close",
           "At <0.8> her fingers turn the volume up; they tap the dashboard twice in time. Her gold watch and wedding ring catch the light.", []),
          (4, "HARD CUT", "CU", "47°", "handheld, from the driver's seat",
           "{layla} in left profile, hair moving in the wind, singing along in wordless la-las, slightly flat; at <1.6> she breaks into a laugh at herself; at <2.6> she turns her head and looks straight toward the driver, into the lens, still smiling.", []),
          (3, "HARD CUT", "Insert", "12°", "handheld, close, on the gearshift",
           "{adam-before}'s right hand rests on the gearshift; Layla's left hand lies over it, and her thumb strokes his knuckle slowly, twice. Both wedding rings shine.", [])],
    perf="Layla's laugh crinkles her eyes; her look to him is open, teasing, in love.",
    phys="Wind moves her hair and the collar of her cardigan; the car hums at 80 km/h.",
    light="Low golden sun through the windshield and her side window, warm on her skin, a soft flare behind her hair. White balance 5600K.",
    audio="The same warm old-fashioned waltz, fuller through car speakers; road hum, wind; Layla la-las along and laughs. The only music is that radio song.",
    locks=["Adam appears only as his right hand on the gearshift."])

run(id="G16", scene="4 · The song & the dance", nums="27 ★", look="P", attach=["adam", "doll-wife", "doll-daughter", "L03_living-dim", "F10_living-blocking"],
    ctx="Evening in the living room, lit only by the floor lamp. A locked medium two-shot, knees up: {adam} slow-dances with {doll-wife} in front of the sofa, held close, cheek to wig, while {doll-daughter} sits upright at the left end of the sofa behind them, soft in the background, exactly where it sits in {F10_living-blocking}.",
    map="Camera in the open floor of {L03_living-dim}, at chest height, 3 metres from the dancers, looking toward the sofa. Foreground: the rug. Midground: Adam and the adult mannequin in a close dance hold on the rug, framed from the knees up, centre frame. Directly behind them, between the dancers and the sofa: the low wooden coffee table with its lace doily and glass dish, its top visible behind their legs. Background: the sofa, the child mannequin seated at its left end, the glowing floor lamp.",
    first="The first frame is {adam} and the adult mannequin from the knees up, centre frame, his cheek against its wig, its rigid arm over his shoulder; behind their legs the low coffee table with the doily and glass dish; behind that the sofa with the child mannequin at its left end.",
    segs=[(8, None, "MS two-shot, knees up", "47°", "locked, chest height",
           "His right arm is around the mannequin's waist, carrying its weight; its rigid left arm lies over his shoulder; his left hand holds its stiff right hand against his chest; his cheek rests against its wig. He sways slowly from side to side and turns a few degrees, keeping both of them in the centre of the frame; the mannequin moves with him as one rigid piece. His eyes are closed.", [])],
    perf="Total peace in his face and shoulders; slow steady breathing.",
    phys="The mannequin moves only as he carries it; its joints keep their angles and its feet drag slightly. The rug creases under his bare feet.",
    light="The floor lamp is the only light, warm, behind the sofa; the dancers are rimmed in amber, the room falls to deep soft shadow. White balance 4300K.",
    audio="The waltz, small and distant from the radio in the kitchen. His bare feet shuffling. The wall clock. The only music is that radio song.",
    locks=["The camera holds still while he sways.", "The child mannequin stays seated at the left end of the sofa for the whole shot.", "The coffee table stands in the middle of the room between the dancers and the sofa in every frame, as in {L03_living-dim}."])

run(id="G17", scene="4 · The song & the dance", nums="28, 30", look="P", attach=["adam", "doll-wife", "L03_living-dim"],
    ctx="Evening in the living room, still dancing. A close-up of {adam}'s face at peace against the plastic cheek of {doll-wife}; then a close-up of his shoulder as the mannequin's arm slips out of its socket and slides down his back.",
    map="Camera close beside the dancers in front of the sofa in {L03_living-dim}. Background: the warm glow of the floor lamp and the dim sage wall, soft.",
    first="The first frame is {adam}'s face in three-quarter view pressed against the mannequin's smooth ivory cheek, eyes closed, the crooked wig against his forehead.",
    segs=[(4.5, None, "CU", "29°", "locked, at head height",
           "He sways very slightly. At <2.0> a long slow breath out and the smallest smile. The plastic face beside his is blank and still.", []),
          (3.5, "HARD CUT", "CU", "29°", "locked, on his right shoulder and upper back",
           "The mannequin's burgundy-sleeved arm lies over his shoulder, its ivory hand hanging open. At <0.8> the arm drops a centimetre with a pop as it leaves the shoulder socket. At <1.4> it slides down his back, sleeve and all, and falls out of the bottom of the frame at <2.6>. Adam stops moving.", [])],
    perf="Eyes closed, brow smooth, lips slightly parted: a man asleep on his feet.",
    phys="The arm is a clean hollow plastic part with a ball joint; it slides under its own weight and drops cleanly.",
    light="Warm lamp light from behind, an amber rim on his ear and the wig; soft shadow on the near side. White balance 4300K.",
    audio="The distant radio waltz and his breathing; a dry plastic pop, cloth sliding. The only music is that radio song.",
    locks=[])

run(id="G18", scene="4 · The song & the dance", nums="31, 32 ★", look="P", attach=["adam", "doll-wife", "doll-daughter", "L03_living-dim", "F10_living-blocking"],
    ctx="Evening in the living room. The left arm of {doll-wife} lies on the rug while {adam} stands holding the whole mannequin upright, wig, face and cardigan intact, one sleeve hanging empty; then he sits it in the armchair, kneels, pushes the arm back into its shoulder socket far too gently and presses the plastic hand to his forehead. {doll-daughter} sits at the left end of the sofa, as in {F10_living-blocking}.",
    map="Camera at the room's entrance as in {L03_living-dim}. Foreground: the rug with the detached arm. Midground: Adam standing centre holding the adult mannequin by the waist. Background: the child mannequin on the sofa, the floor lamp, the sewing corner.",
    first="The first frame is the detached burgundy-sleeved arm rocking on the rug at {adam}'s feet as he holds the one-armed mannequin upright.",
    segs=[(4, None, "WS", "63°", "locked, eye level, the same frame as the dance",
           "The arm, a smooth ivory plastic arm in a burgundy sleeve, rocks on the rug and comes to rest by <1.2>. He stands holding the complete mannequin upright against his side, its wigged head and blank face at his shoulder, the left cardigan sleeve hanging empty, and stares down at the arm, completely still.", []),
          (6, "HARD CUT", "MCU", "47°", "a slight handheld breath, at kneeling height",
           "The adult mannequin now sits upright in the floral armchair, whole: wig, blank face, burgundy cardigan, the empty left sleeve hanging flat. {adam} kneels beside it holding the whole detached arm in both hands from the first frame of this segment: one smooth ivory plastic arm, rounded ball joint at the top, hand at the bottom. He pushes the ball end up inside the empty sleeve and into the shoulder socket under the cardigan, gently and too fast, fumbling; the sleeve fills as the arm goes in. At <2.6> it clicks into place and the plastic hand now hangs at the end of the sleeve, joined to the arm. At <3.8> he lifts that attached hand, still joined to the arm in the sleeve, and holds it against his forehead, eyes shut.",
           [(0.4, 2.2, "Adam", "rushed, breaking, barely voiced", "I'm sorry. I'm sorry."),
            (4.2, 5.4, "Adam", "a whisper into the plastic hand", "Did I hurt you?")])],
    perf="Panic in his hands, tenderness in his face; his breath comes short and his lower lip shakes.",
    phys="The arm rocks on its curve and settles; the joint seats inside the sleeve with a hard click. The mannequin keeps its head, wig and face on and sits rigid in the chair as he works.",
    light="The floor lamp as the only light, warm, from behind the sofa; his face half in shadow. White balance 4300K.",
    audio="A hollow plastic knock rocking to stillness; plastic on plastic, a click, his breath. The room is quiet apart from these sounds; the song is laid in during the edit.",
    locks=["Both mannequins stay inert; only Adam moves.", "The adult mannequin keeps its head, wig, blank face and cardigan in every frame.", "There is exactly one loose arm: on the rug in the first segment, in Adam's hands at the start of the second, then fixed in the sleeve; the hand stays joined to that arm."])

# =========================================================== 5 · THE KNOCK
run(id="G19", scene="5 · The knock", nums="33", look="P", attach=["L05b_hallway-bag"],
    ctx="Evening in the dark entrance hallway. Close on the inside of the front door, three soft knocks sound on it.",
    map="Camera in the hallway of {L05b_hallway-bag}, close on the upper half of the front door. The dark varnished door fills the frame, the brass chain and handle at right, a slice of sage wall at the edge.",
    first="The first frame is the upper half of the closed door, the brass chain hanging slack across its latch.",
    segs=[(4, None, "Insert", "47°", "locked, at chain height",
           "Stillness for a second. Three slow, gentle knocks with a knuckle at <1.0>, <1.8> and <2.6>, the knock of a tired relative. The chain gives a small shiver with each one and hangs still again by <3.5>.", [])],
    perf="",
    phys="The door stays steady in its frame; the chain barely moves.",
    light="The hallway is dark; a thin line of yellowish stairwell light glows under the door, catching the lower edge of the frame. White balance 4300K.",
    audio="Three soft, polite knocks on solid wood, a faint tick of the chain, the quiet of the hallway.",
    locks=["The door stays shut."])

run(id="G20", scene="5 · The knock", nums="34", look="P", attach=["adam", "P05_radio", "L01_kitchen"],
    ctx="Evening in the kitchen. {adam}, standing under the shelf with the radio, freezes at the sound of knocking, then reaches up and switches the radio off.",
    map="Camera in {L01_kitchen}, close on Adam at the counter. Midground: Adam, face turned to frame left toward the hallway. Background: the tiled backsplash and the stove, soft; {P05_radio} on the shelf at the right edge.",
    first="The first frame is {adam}'s face turned sharply to frame left, completely still, listening.",
    segs=[(5, None, "CU", "29°", "locked, on the shadow side of his face",
           "He holds his breath. At <1.8>, eyes still on the hallway, he reaches his right hand up to the radio at the frame edge, and at <2.6> turns the dial; it clicks off. He stays frozen in the silence.", [])],
    perf="Every muscle locked; only his eyes move, once, toward the sound.",
    phys="The dial turns with a stiff mechanical click.",
    light="The bare warm bulb overhead as key, hard on his cheekbone, the far side of his face in shadow. White balance 4300K.",
    audio="The radio waltz until 2.6s, then a click and total silence; the wall clock; a pot simmering faintly. After 2.6s the room carries only those sounds.",
    locks=[])

run(id="G21", scene="5 · The knock", nums="35", look="P", attach=["adam", "L05b_hallway-bag"],
    ctx="Evening, a deep wide down the dark hallway. {adam} stands small and still in the middle of the hall, his back to the camera, while a woman outside speaks to him through the closed front door. She is heard only.",
    map="Camera at the near end of the hallway, exactly as in {L05b_hallway-bag}. Foreground: the terrazzo floor. Midground: Adam in the centre of the hall, back to camera. Background: the dark front door at the far end with an even, unbroken line of yellowish light beneath it; glazed doors on the left, mirror and console on the right.",
    first="The first frame is the hallway at the angle of {L05b_hallway-bag}, {adam} standing dead still in the centre with his arms at his sides.",
    segs=[(8, None, "WS", "63°", "locked, eye level, deep focus",
           "He holds still. The line of light under the door stays even and unbroken. At <6.0> his head lowers a little.",
           [(0.6, 1.4, "Mona (unseen, through the door)", "low, steady", "Adam."),
            (1.8, 3.4, "Mona (unseen, through the door)", "gentle, certain", "I know you're in there."),
            (4.0, 5.4, "Mona (unseen, through the door)", "tired", "It's been four months..."),
            (6.2, 7.6, "Mona (unseen, through the door)", "her voice gives a little", "I lost them too.")])],
    perf="Stillness as resistance; his shoulders rise once and settle.",
    phys="The light under the door is one steady, even strip from edge to edge.",
    light="The hallway dark; the line of stairwell light under the door is the brightest thing in frame; faint cool spill from the glazed doors outlines Adam. White balance 4300K.",
    audio="Silence in the apartment, the wall clock. Mona's voice muffled by the wooden door, with a little stairwell echo.",
    locks=["The front door stays shut; the woman is heard only.", "Adam stays silent for the whole clip."])

run(id="G22", scene="5 · The knock", nums="36 ★, 38", look="P", attach=["adam", "doll-daughter", "L03_living-dim", "F10_living-blocking"],
    ctx="Evening in the living room. {adam} crouches by {doll-daughter}, seated at the left end of the sofa as in {F10_living-blocking}, and puts a finger to his lips as if it were a game; then a close-up of him alone, listening to footsteps going away, his face giving way for one second before the mask comes back.",
    map="Camera low by the sofa in {L03_living-dim}. Midground: the child mannequin upright at the left end of the sofa, at frame right of the shot; Adam crouched on the floor beside it (frame left), his face level with its face. Background: the lace throw and the lamp glow; the dark room toward the hallway at frame left.",
    first="The first frame is {adam}'s face in profile at frame left, close to the blank ivory face of the child mannequin at frame right.",
    segs=[(5, None, "CU two-shot", "29°", "locked, at crouching head height",
           "At <0.8> he raises one finger to his lips and holds it there, eyes bright; at <4.0> a tiny nod. The mannequin holds perfectly still.",
           [(1.4, 2.0, "Adam", "the softest whisper", "Shh."),
            (2.4, 4.0, "Adam", "whispered, playful", "We're playing the quiet game.")]),
          (5, "HARD CUT", "CU", "29°", "locked, frontal, on the shadow side",
           "{adam} alone, still crouched, head turned slightly to frame left toward the hallway, listening. From <1.0> to <2.2> his jaw trembles and his eyes fill. At <2.6> he swallows, breathes in, and his face smooths into a pleasant mask; he turns brightly to frame right.",
           [(3.4, 4.5, "Adam", "bright, false, a little too loud", "Who wants dinner?")])],
    perf="The crack lasts one second: chin dimpling, a wet blink, then a deliberate smile.",
    phys="",
    light="Warm lamp key from behind the sofa, his face half lit; deep shadow toward the hall. White balance 4300K.",
    audio="Near silence, the wall clock; in the second segment, footsteps going down a stairwell beyond the door, fading out by 2.5s.",
    locks=["The child mannequin stays motionless and faces forward."])

run(id="G23", scene="5 · The knock", nums="37 ○", look="P", attach=["mona", "P14_foil-dish", "L09_landing"],
    ctx="Evening on the stairwell landing, at floor level: a woman's hands set {P14_foil-dish} down on the doormat in front of the closed apartment door, and her shoes walk away toward the stairs. She is seen from the knees down.",
    map="Camera on the floor of {L09_landing}. Foreground: the doormat. Midground: the foot of the closed dark wooden door at frame right. Background: the first steps and the iron railing at frame left.",
    first="The first frame is the doormat and the foot of the closed door, a woman's flat shoes standing on the mat, the hem of a navy dress and a long grey cardigan above them.",
    segs=[(4, None, "Insert, floor level", "63°", "locked, on the floor",
           "At <0.6> she bends her knees and her two hands lower the dish onto the mat, centred against the door. Her hand rests flat on the foil a moment and lifts at <2.2>; her shoes turn and walk out of frame to the left toward the stairs by <3.4>. The dish stays.", [])],
    perf="A slow, careful set-down; the hand lingers on the foil.",
    phys="The foil crinkles under her palm; the dish settles flat on the mat.",
    light="A dim stairwell bulb overhead, greenish-grey walls, soft shadows under the dish. White balance 4300K.",
    audio="Foil crinkling, the dish on the mat, footsteps going down the stairs with a stairwell echo.",
    locks=["Framing stays below {mona}'s knees: shoes, hem, cardigan edge and hands.", "The apartment door stays shut."])

# ================================================================= 6 · DINNER
run(id="G24", scene="6 · Dinner & the headlights", nums="39, 40", look="P", attach=["adam", "doll-wife", "doll-daughter", "P01_yellow-cup", "L02_dining"],
    ctx="Night at the dining table, the same symmetrical frontal wide as breakfast: {adam} at the centre facing the camera, {doll-wife} at the left end, {doll-daughter} at the right end, steam rising off three untouched plates while he promises them the sea. Then an insert of him pouring water into the yellow cup until it overflows.",
    map="Camera square to the table in {L02_dining}, the curtains directly behind it, black with night. Foreground: the empty near edge of the table. Midground: Adam at centre, the adult mannequin at frame left, the child mannequin at frame right. Background: the dark curtains, the sideboard with the clock at the right edge.",
    first="The first frame is the whole table dead centre under the pendant lamp, three plates of hot rice and stew steaming, {P01_yellow-cup} beside the small plate at frame right, a glass water jug by Adam's hand.",
    segs=[(6, None, "WS frontal", "63°", "locked, dead centre, eye level",
           "{adam} leans forward on his forearms, looking from the child mannequin to the adult one as he speaks. Both hold perfectly still. His fork lies untouched.",
           [(0.6, 2.4, "Adam", "warm, a promise", "Tomorrow we go to the sea."),
            (2.8, 3.6, "Adam", "earnest", "I promise."),
            (4.0, 5.6, "Adam", "quieter, to himself as much as them", "This time we'll get there.")]),
          (4, "INSERT CUT", "Insert", "47°", "locked, at table height",
           "{P01_yellow-cup} on the lace, close, the child mannequin's rigid ivory hand resting on the table edge beside it, and from the first frame {adam}'s hand already holding a clear glass water jug just above the cup. He tilts the jug and water fills the cup; at <1.6> it reaches the brim and he keeps pouring. It overflows, runs down the yellow plastic and spreads dark through the lace.", [])],
    perf="His promise is gentle and certain; his eyes drift away from the table on the last line.",
    phys="Steam curls up from the plates. Water overflows the brim in a thin sheet, soaks into the lace and spreads in a widening dark stain.",
    light="One pendant lamp above the table makes a warm pool; the room around falls to darkness. White balance 4300K.",
    audio="The wall clock, steam; water pouring, then spilling onto cloth; far outside, a truck horn.",
    locks=["Perfect symmetry in the wide: Adam centred, one mannequin on each side.", "His plate and fork stay untouched.", "The water jug is in Adam's hand from the first frame of the insert."])

run(id="G25", scene="6 · Dinner & the headlights", nums="41 ★", look="P", attach=["doll-wife", "doll-daughter", "adam", "L02_dining"],
    ctx="Night at the dining table, seen from the side. A vehicle passes in the street and its headlights come through a narrow gap in the curtains, sweep along the wall and slide across the two blank plastic faces of {doll-wife} and {doll-daughter}. {adam} sits between them, head down.",
    map="Camera at the side of the room in {L02_dining}, the table running across the frame. Foreground: the adult mannequin at the near end, in profile. Midground: Adam, a dark shape, head down. Background: the child mannequin at the far end facing the adult one; the sage wall with two framed pictures and the sideboard; at frame left the closed curtains with a finger-wide gap.",
    first="The first frame is the table in the pendant lamp's pool, the two mannequins motionless, {adam} still, the gap in the curtains a thin dark line at frame left.",
    segs=[(5, None, "WS side angle", "63°", "locked, seated eye level",
           "At <1.0> a hard white bar of light enters through the curtain gap, sweeps along the wall, crosses the adult mannequin's blank face at <2.0> and the child mannequin's face at <2.8>, throwing their shadows across the wall, and leaves the room by <3.8>. At <4.2> Adam's head lifts a little.", [])],
    perf="Adam's stillness; the lift of his head is the only human movement.",
    phys="The light moves at the speed of a car passing at 40 km/h; shadows stretch and swing across the wall with it.",
    light="The pendant lamp as a warm base; the headlight sweep a cold hard white beam, 6500K against the room's 4300K white balance.",
    audio="A heavy engine approaching, passing low in the street and fading; water dripping from the table edge.",
    locks=["The light does all the moving; the room, the camera and the mannequins hold still."])

run(id="G26", scene="6 · Dinner & the headlights", nums="44", look="P", attach=["adam", "P01_yellow-cup", "L02_dining"],
    ctx="Night at the dining table. {adam}, at the centre facing the camera, comes back from a memory gripping the table edge; the yellow cup lies on its side in a spreading pool of water. He ends the evening.",
    map="Camera close and frontal on Adam at the table in {L02_dining}. Foreground: {P01_yellow-cup} on its side, water running off the table edge. Midground: Adam, hands on the table edge. Background: the dark closed curtains.",
    first="The first frame is {adam}'s face, eyes wide, breathing hard through his nose, both hands gripping the table edge at the bottom of the frame, the fallen yellow cup in the foreground.",
    segs=[(5, None, "CU", "29°", "a slight handheld breath, at seated eye level",
           "At <1.5> he looks slowly to frame left, at <2.6> to frame right, at each of them. He lets go of the table.",
           [(3.2, 3.9, "Adam", "flat, emptied", "...It's late."),
            (4.1, 4.8, "Adam", "almost inaudible", "Bedtime.")])],
    perf="Knuckles white on the edge, a vein at his temple, then the hands loosen and his shoulders drop.",
    phys="Water runs off the table edge in a thin stream and drips onto the floor.",
    light="The pendant lamp overhead, hard on his brow and cheekbones, eyes in shadow under the brow. White balance 4300K.",
    audio="Water dripping onto the floor, his breathing, the wall clock.",
    locks=[])

run(id="G27", scene="6 · Dinner & the headlights (flash 4)", nums="42, 43", look="M", attach=["layla", "L07_car-front", "L08_desert-road"],
    ctx="A memory at dusk in a moving car: through the windshield, headlights bloom far ahead on the desert road; then {layla}, in the front right seat, turns from the back seat to the road and her smile falls as white light climbs over her face. The clip ends on white.",
    map="First segment: the driver's view through the dusty windshield of {L07_car-front} onto the road of {L08_desert-road} at dusk. Second segment: camera on the driver's side looking across at Layla, her side window behind her.",
    first="The first frame is the dashboard top and the straight two-lane road at dusk through dusty glass, a pair of small headlights far ahead.",
    segs=[(2.5, None, "POV through the windshield", "84°", "handheld, at driver eye level",
           "The far headlights swell and bloom across the dirt on the windshield until the glare covers most of the glass at <2.2>.", []),
          (2.5, "HARD CUT", "CU", "47°", "handheld, from the driver's seat",
           "{layla} in left profile, smiling toward the back seat; at <0.6> her eyes go to the road ahead and the smile falls away as white light climbs over her face. The frame burns out to pure white over the last half second.", [])],
    perf="Her smile drains in a single beat: lips part, eyes widen, brows lift.",
    phys="Glare blooms through dust and smears on the glass.",
    light="Dusk: the sky orange going blue, the cabin dim; the oncoming headlights a cold white that rises to fill the frame. White balance 5600K.",
    audio="Road hum and a truck horn rising steadily through both segments; silence on the last frame.",
    locks=["The clip ends on pure white with the road clear and the car whole."])

# ================================================================ 7 · BEDTIME
run(id="G28", scene="7 · Bedtime", nums="45", look="P", attach=["adam", "doll-daughter", "L06_nour-room"],
    ctx="Night. Seen from inside a child's bedroom lit by a star night-light, {adam} comes in through the open door from the dark corridor, carrying {doll-daughter} in his arms, and walks toward the bed.",
    map="Camera inside {L06_nour-room}, in the corner by the window, looking toward the open door at far right. Foreground: the end of the bed and the small round rug. Midground: the floor between the door and the bed, stars drifting over it. Background: the open doorway and the black corridor beyond.",
    first="The first frame is the open bedroom doorway, the corridor beyond it dark, and {adam} stepping through it into the room, the child mannequin lying across his arms, its stiff legs straight out to one side, the braided wig hanging over his elbow.",
    segs=[(5, None, "WS", "63°", "locked, eye level, facing the door",
           "He comes in slowly at 2 km/h, turning sideways through the door at <0.5> so the rigid legs clear the frame, and walks toward the bed and the camera. A flash of yellow dress catches the amber glow; stars slide over him. At <4.0> he stops beside the bed, the mannequin still in his arms.", [])],
    perf="Careful, quiet steps; his head bent over the figure.",
    phys="The mannequin keeps its rigid straight shape in his arms; only the wig's braids swing.",
    light="The room lit only by the warm star night-light on the bedside table; amber stars drift over the walls, the floor and Adam; the corridor behind him stays dark. White balance 4300K.",
    audio="Slow bare footsteps; the faint tick of the night-light motor; water dripping, far away, fading out.",
    locks=["He walks into the room, from the doorway toward the bed.", "The mannequin stays in his arms for the whole shot."])

run(id="G29", scene="7 · Bedtime", nums="46, 47, 48", look="P", attach=["adam", "doll-daughter", "P10_rabbit", "L06_nour-room"],
    ctx="Night in a child's bedroom. {adam} tucks {doll-daughter} into bed and sets the stuffed rabbit beside it; he kisses its forehead and stays a moment too long as projected stars drift over his face; from the doorway he switches off the lamp and only the stars remain.",
    map="Camera inside {L06_nour-room}. The bed against the left wall, the bedside table with the star night-light at its head, the small desk at right, the open door at far right. Background: the sage wall with taped crayon scribbles, stars drifting across it.",
    first="The first frame is the bed from its foot at a three-quarter angle, the child mannequin lying flat on its back, head on the pillow, {adam} seated on the bed's edge.",
    segs=[(6, None, "MS", "47°", "locked, at seated height",
           "From the first frame {P10_rabbit} already lies on the pillow beside the mannequin's head. At <1.5> he pulls the patterned blanket up to the plastic chin and smooths it over the stiff shape. At <3.5> he straightens the rabbit against the mannequin's shoulder with one hand.", []),
          (6, "HARD CUT", "CU", "29°", "locked, at pillow height, from the side",
           "{adam} leans down and at <1.0> kisses the ivory forehead; he stays there, lips on the plastic, eyes closed, until <3.2>. Star shapes drift slowly over his face and the pillow. He pulls back a few centimetres and speaks.",
           [(3.8, 4.8, "Adam", "a whisper", "Tomorrow, the sea."),
            (5.0, 5.8, "Adam", "barely there", "Sleep now.")]),
          (4, "HARD CUT", "WS", "63°", "locked, eye level, the room's angle",
           "The room at the angle of {L06_nour-room}. {adam} stands at the open door at far right, his hand on the light switch. He looks back at the bed for a second and at <1.6> presses the switch: the bedside lamp goes out, leaving the night-light dome and its slow stars; he becomes a black silhouette in the doorway.", [])],
    perf="Ritual tenderness; the held kiss shows in the stillness of his shoulders.",
    phys="The blanket drapes over a rigid straight shape. The rabbit is small, about 30 cm, smaller than the pillow.",
    light="A small warm bedside lamp and the amber star night-light on deep blue; after the switch, only the stars. White balance 4300K.",
    audio="Blanket fabric, the faint tick of the night-light motor, his breathing, a light-switch click at 13.6s.",
    locks=[])

run(id="G30", scene="7 · Bedtime", nums="49 ★, 50 ★", look="P", attach=["adam", "L06_nour-room"],
    ctx="Night, in the doorway of a child's bedroom lit only by a star night-light. {adam} is about to leave; he stops; a child's voice behind him says two words; he keeps facing the dark corridor. The bed stays behind him, out of frame.",
    map="Camera in the corridor and the doorway of {L06_nour-room}. Midground: Adam in the doorway facing out toward the corridor. Background: the dim bedroom wall behind him with stars drifting across it.",
    first="The first frame is {adam} in right profile, facing frame right toward the dark corridor, one hand on the door frame, mid-step.",
    segs=[(5.5, None, "CU profile", "29°", "locked, eye level",
           "At <1.0> he stops and stands. Three seconds of stillness. On the voice at <3.6> his whole body locks and his fingers tighten on the frame. He keeps facing the corridor.",
           [(3.6, 5.2, "Nour (unseen, behind him, close and clear)", "soft, patient, a child asking", "Daddy... look.")]),
          (4.5, "HARD CUT", "CU frontal", "29°", "very slow push-in at 0.5 km/h, from the corridor side",
           "{adam}'s face from the corridor side, the starlit room blurred behind his shoulder. He stares straight past the camera. His eyes fill and one tear runs. He shakes his head a fraction as he whispers. On the second voice at <3.0> he shuts his eyes hard.",
           [(1.0, 2.4, "Adam", "a cracked whisper, eyes ahead", "...Not now, sweetheart."),
            (3.0, 4.0, "Nour (unseen, brighter, with the sound of a car interior)", "delighted, insisting", "Daddy, LOOK!")])],
    perf="His refusal is physical: neck rigid, jaw set, eyes fixed ahead while they fill.",
    phys="",
    light="Only the star night-light: slow amber stars over deep blue behind him; his face half in darkness, an amber edge on his cheek. White balance 4300K.",
    audio="Dead silence and the faint tick of the night-light motor; from 8.5s a warm road hum swells under the second child's line and stops on the last frame.",
    locks=["Adam faces away from the room for the whole clip; the frame holds on him alone.", "The child is heard only."])

# ============================================================== 8 · THE ROAD
run(id="G31", scene="8 · The road", nums="51", look="ML", attach=["P13_family-car", "L08_desert-road"],
    ctx="A memory at golden hour: {P13_family-car} drives toward the sea on a two-lane desert road, a bright swim ring pressed against its back window, three heads dim shapes inside.",
    map="The road of {L08_desert-road}. The car drives in the right-hand lane toward the low sun and the thin line of sea. The camera travels alongside on the car's left, slightly behind. Background: sandy shoulder, low scrub, poles, sea, sun.",
    first="The first frame is the off-white sedan in three-quarter rear view, driving steadily, the camera keeping pace beside it.",
    segs=[(5, None, "WS tracking", "63°", "smooth tracking alongside at 80 km/h, drifting slowly forward along the car's side",
           "The car holds its lane. The camera drifts forward along its flank until at <4.0> the low sun flares past the roof.", [])],
    perf="",
    phys="The car rides smoothly; a light dust trail lifts from the shoulder behind the tyres.",
    light="Golden hour, the sun low ahead of the car, a warm rim on the roof and windows. White balance 5600K. Heat shimmer at 50 metres.",
    audio="Tyres on asphalt, wind rushing past the car, a soft desert breeze. The song is laid in during the edit.",
    locks=["The road ahead stays open and empty.", "The car keeps the same lane and speed for the whole shot."])

run(id="G32", scene="8 · The road", nums="52, 53, 54, 55", look="M", attach=["adam-before", "layla", "nour", "L07_car-front", "L07b_car-backseat"],
    ctx="A memory at golden hour inside a moving family car: the two parents from behind, hands joined on the gearshift; their daughter drawing on her knees; the mother looking back at her; the father's smiling eyes in the rear-view mirror.",
    map="Inside the car. {adam-before} drives in the front left seat; {layla} sits in the front right seat; {nour} sits in the back right seat behind Layla, belted, a picture book on her knees with a sheet of paper on it. Seen from the back seat: the windshield, the straight road and the low sun, as in {L07_car-front}. Behind Nour: the seat back, the swim ring on the rear shelf, the side window, as in {L07b_car-backseat}.",
    first="The first frame is the cabin from the middle of the back seat, Adam at the wheel on the left and Layla on the right, seen from behind, the sun flaring between them.",
    segs=[(4, None, "MS from the back seat", "84°", "handheld, between the front seats",
           "Layla's left hand lies on Adam's right hand on the gearshift. She sways and la-las along with the radio, flat; at <2.2> he turns his head a little toward her and laughs.", []),
          (4, "HARD CUT", "CU", "47°", "handheld, close, on the back right seat",
           "{nour}, head bent over the paper on the book on her knees, draws hard with a short yellow crayon, the tip of her tongue between her teeth where the tooth is missing. Her arm and the angle keep the drawing hidden.", []),
          (4, "HARD CUT", "CU", "47°", "handheld, from the driver's side",
           "{layla} twists in her seat and looks back over her left shoulder at Nour at <0.4>, amused, then turns to Adam at frame left and speaks.",
           [(1.2, 2.6, "Layla", "mock outrage, laughing under it", "An hour she's been drawing."),
            (2.8, 3.8, "Layla", "to Adam, delighted", "She won't show me.")]),
          (3, "HARD CUT", "ECU on the rear-view mirror", "12°", "handheld, close",
           "The rear-view mirror against the bright windshield. In it, only Adam's eyes, creased with a smile, flick up to the back seat as he speaks, then back to the road.",
           [(0.6, 2.4, "Adam", "warm, playful, calling back", "What are you drawing, Nour?")])],
    perf="A family at ease: easy laughter, shared looks, Nour's fierce concentration.",
    phys="The car sways gently at 80 km/h; wind at a cracked window moves loose hair.",
    light="Golden hour, the sun low through the windshield, warm flare, faces glowing. White balance 5600K.",
    audio="Road hum, wind at a cracked window, a crayon scratching paper, Nour humming five notes, Layla la-la-ing softly, Adam's laugh. The song is laid in during the edit.",
    locks=["Seats stay fixed: Adam drives front left, Layla front right, Nour back right behind Layla with her seatbelt on.",
           "Nour's seatbelt is worn the normal way: shoulder strap diagonal across her chest, lap strap across her thighs, buckle at her hip.",
           "The drawing stays hidden from the camera.",
           "Nour's crayon is a short, finger-thin yellow wax crayon."])

run(id="G33", scene="8 · The road", nums="56, 57, 58, 59", look="M", attach=["adam-before", "layla", "nour", "L07_car-front", "L07b_car-backseat"],
    ctx="A memory at golden hour inside the moving car: the girl in the back holds up her finished drawing for her father; he says one minute, he is driving; she insists; her mother laughs and tells him to look. The camera sees only the back of the paper.",
    map="Inside the car. {adam-before} drives in the front left seat; {layla} sits in the front right seat; {nour} sits in the back right seat behind Layla, belted. Behind Nour: the bright rear window and the swim ring, as in {L07b_car-backseat}. Behind Adam: his side window and the desert, as in {L07_car-front}.",
    first="The first frame is {nour} in the back right seat finishing a last stroke with the yellow crayon, seen from the front looking back.",
    segs=[(4, None, "CU", "47°", "handheld, from the front seats looking back",
           "The sheet of paper is in both her hands from the first frame. At <0.8> she lifts it and holds it up toward the front seats, beaming. The camera sees only the back of the paper, the sun glowing through it as soft coloured shapes.",
           [(1.4, 2.8, "Nour", "bursting with pride", "Daddy, look!")]),
          (4, "HARD CUT", "MCU", "47°", "handheld, from the passenger side",
           "{adam-before} at the wheel in right profile, eyes on the road, squinting into the low sun, smiling. At <0.6> he flips the sun visor down. He answers with his eyes on the road.",
           [(1.4, 2.4, "Adam", "easy, amused", "One minute, sweetheart."),
            (2.6, 3.6, "Adam", "light", "I'm driving.")]),
          (3, "HARD CUT", "CU", "47°", "handheld, close",
           "{nour} leans forward against her seatbelt, holding the paper higher, right up between the front seats, its back to the camera.",
           [(0.4, 2.4, "Nour", "sing-song, stretching the word", "Daddyyy. Look!")]),
          (3, "HARD CUT", "CU", "47°", "handheld, from the driver's side",
           "{layla} laughs, her left hand coming across to touch Adam's arm at <0.6>.",
           [(0.8, 2.6, "Layla", "laughing, giving in", "Look at it, or she'll never stop.")])],
    perf="Nour's whole body pleads; Adam's smile grows while his eyes hold the road.",
    phys="The paper flutters slightly in the window draught; the seatbelt presses into Nour's shoulder as she leans.",
    light="Golden hour, the sun low and straight ahead, strong in Adam's eyes; the paper glows translucent with light behind it. White balance 5600K.",
    audio="Road hum, wind at a cracked window, paper rustling. The song is laid in during the edit.",
    locks=["Seats stay fixed: Adam drives front left, Layla front right, Nour back right behind Layla with her seatbelt on.",
           "Nour's seatbelt is worn the normal way: shoulder strap diagonal across her chest, lap strap across her thighs, buckle at her hip.",
           "The paper always shows its blank glowing back to the camera.",
           "Adam's eyes stay on the road for the whole clip."])

run(id="G34", scene="8 · The road", nums="60 ★, 61", look="M", attach=["adam-before", "nour", "L07_car-front", "L07b_car-backseat"],
    ctx="A memory at golden hour, in slow motion: {adam-before}, driving in the front left seat, turns his head back to look at his daughter's drawing and his face opens into joy; then his view of {nour} in the back right seat, the paper so backlit that the sun burns it to pure white.",
    map="Inside the car. Adam in the front left seat, turning to the right and back. Nour in the back right seat, belted, holding the paper up toward him. Behind Adam: his side window and the golden desert, as in {L07_car-front}. Behind Nour: the rear window blazing with sun, as in {L07b_car-backseat}.",
    first="The first frame is {adam-before}'s face in left three-quarter view from behind his right shoulder, eyes on the road, a smile starting.",
    segs=[(5, None, "CU", "47°", "handheld, from the back seat side, slow motion",
           "From <0.5> to <2.5> he turns his head to the right and back toward the camera. As his eyes land on what she holds, at <3.0>, his whole face opens: brows lift, eyes shine, cheeks rise, a laugh begins. Sunlight slides across his face.", []),
          (3, "HARD CUT", "POV", "63°", "handheld, slow motion, at his eye line",
           "{nour} in the back right seat, beaming, missing tooth, holding the sheet up in both hands toward the camera. The sun sits directly behind the paper: it is a blazing white-gold rectangle, her fingers dark at its edges, her face glowing beside it.", [])],
    perf="The happiest face in the film, built from muscle: crow's feet, lifted cheeks, open mouth, wet bright eyes.",
    phys="Slow motion in both segments: hair and dust drift slowly through the light.",
    light="Golden hour pouring through the rear window behind Nour and across Adam's face; the paper fully burned out by the sun. White balance 5600K.",
    audio="All sound falls to a muffled underwater hush; only a child humming five notes stays clear and close.",
    locks=["Both segments play in slow motion.", "The drawing reads only as burned-out white light.", "The frame stays inside the car on the two faces."])

run(id="G35", scene="8 · The road", nums="62, 63", look="M", attach=["layla", "L07_car-front"],
    ctx="A memory at golden hour turning to glare: {layla}, in the front right seat, looks to the road and her smile falls as she says his name; then, through the windshield, the headlights of a truck fill the glass. The clip ends on pure white.",
    map="Inside {L07_car-front}. First segment: Layla in the front right seat, seen from the driver's side. Second segment: the view through the windshield from between the front seats.",
    first="The first frame is {layla} laughing, looking toward the driver at frame left.",
    segs=[(2.5, None, "CU", "47°", "handheld, from the driver's seat",
           "At <0.5> her eyes flick to the road ahead; the smile falls; white light rises across her face.",
           [(1.3, 2.0, "Layla", "sharp, cut off", "Adam—")]),
          (2.5, "HARD CUT", "WS through the windshield", "84°", "handheld, shaking 2 cm",
           "Two huge headlights and the high flat front of a truck bleach the dusty windshield, growing until at <1.8> the whole frame is white. The frame holds pure white to the end.", [])],
    perf="Her face changes in a quarter second: smile gone, eyes wide, lips parting on his name.",
    phys="Glare blooms across dust on the glass.",
    light="Warm golden light overtaken by cold white headlights rising to full white. White balance 5600K.",
    audio="A truck horn, full and close, through both segments; silence on the last frame.",
    locks=["The clip ends on pure white, the glass whole and the car steady."])

run(id="G36", scene="8 · The road", nums="65 ★", look="ML", attach=["P12_crayons", "L08_desert-road"],
    ctx="Dusk on the desert road, at ground level: a short yellow crayon from {P12_crayons} rolls slowly across the asphalt and stops against a few glittering crumbs of safety glass. An orange light blinks far out of focus.",
    map="Camera lying on the asphalt of {L08_desert-road}. Foreground: coarse asphalt filling the lower two thirds. Midground: a small scatter of glass cubes right of centre. Background, far out of focus: the sandy shoulder, a soft orange light blinking about once a second, the dark blue sky.",
    first="The first frame is coarse asphalt in close-up, a small scatter of glittering glass cubes right of centre, the orange blink soft behind.",
    segs=[(5, None, "Ground-level macro", "12°", "locked, on the ground",
           "At <0.5> the short yellow wax crayon rolls slowly in from frame left, crosses the frame at 1 km/h, and at <3.2> comes to rest against the glass crumbs. It rocks once and lies still. The orange light keeps blinking in the blur.", [])],
    perf="",
    phys="The crayon rolls with real weight, slowing on the rough surface; the glass cubes catch the blinking light.",
    light="After sunset: cool blue-grey ambient light, the orange blink as the only warm accent, the crayon the only saturated yellow. White balance 5600K.",
    audio="Near silence; a thin high tone; a slow ticking relay, like a clock.",
    locks=["The frame holds only asphalt, the crayon, the small glass crumbs and the soft orange blink.", "The camera stays locked on the ground."])

run(id="G37", scene="8 → 9 · Asphalt to floor (match cut)", nums="66 ★, 67 ★", look="ML", attach=["adam", "L06_nour-room"],
    ctx="A match cut on one eye: an extreme close-up of {adam}'s open eye, his cheek on asphalt at dusk; cut to the same eye, same size, same angle, his cheek now on the terrazzo floor of his daughter's bedroom at night, four months later.",
    map="First segment: camera on the asphalt a few centimetres from his face, Adam lying on his left side. Second segment: camera on the terrazzo floor of {L06_nour-room} in exactly the same position, Adam lying the same way.",
    first="The first frame is {adam}'s right eye, open, centred in the frame, the bridge of his nose at one edge, his cheek pressed on rough asphalt along the bottom.",
    segs=[(4, None, "ECU", "12°", "locked, at ground level",
           "Clean-shaven skin dusted with grit. An orange light blinks in the wet of his eye about once a second. At <1.5> a sheet of white paper drifts across the far background, out of focus. His eye stays open and still.", []),
          (6, "MATCH CUT", "ECU", "12°", "locked, at floor level, the same lens and position",
           "The same eye in the same place at the same size. The asphalt becomes speckled terrazzo and the orange blink becomes small amber stars turning slowly over his face; stubble now covers his cheek and the healed scar shows at the frame edge by his temple. At <1.5> he blinks once. At <4.0> a tear gathers and runs across the bridge of his nose.", [])],
    perf="The eye is alive in both: a wet surface, a catch-light, a tiny tremor of the lower lid.",
    phys="The tear runs with gravity across the nose and drops; the stars move slowly and evenly.",
    light="First segment: dusk blue-grey with an orange blink. Second segment: night, deep blue with amber projected stars. White balance 5600K in both.",
    audio="A thin high tone and a slow ticking relay, his shallow breath; across the cut the tick continues unbroken and becomes the soft tick of a night-light motor, and the tone fades away.",
    locks=["At 4.0s only the ground, the light and the stubble change; the eye keeps its exact place and size.",
           "His skin is whole and clean in both segments.", "The eye stays centred in both segments."])

# ============================================================= 9 · THE FLOOR
run(id="G38", scene="9 · The floor", nums="68 ★", look="P", attach=["doll-daughter", "P10_rabbit", "L06_nour-room"],
    ctx="Night in a child's bedroom, seen from the floor beside the bed: under the blanket, plainly, lies {doll-daughter}, a plastic figure with its wig slipped askew. Only the projected stars move.",
    map="Camera on the floor beside the bed in {L06_nour-room}, looking up. Foreground: the mattress edge across the lower frame. Midground: the mannequin's head in profile on the pillow, {P10_rabbit} beside it. Background: the sage wall, the taped scribbles, slow stars, the glowing dome on the bedside table.",
    first="The first frame is the side of the bed from floor level, the smooth ivory head of the child mannequin in profile on the pillow, the wig slipped sideways off a bare plastic scalp.",
    segs=[(5, None, "Low angle from the floor", "63°", "locked, at floor level",
           "The blank face, the seam at the neck above the blanket, the small grey rabbit beside it. It is an object under a blanket. The projected stars drift slowly across it and the wall.", [])],
    perf="",
    phys="The blanket lies flat over a rigid straight shape; the stars glide evenly.",
    light="Only the star night-light: amber stars drifting over deep blue, a soft amber edge on the plastic. White balance 4300K.",
    audio="Silence; the faint tick of the night-light motor.",
    locks=["Everything in the room is still except the projected stars."])

run(id="G39", scene="9 · The floor", nums="69 ★, 70 ○", look="P", attach=["adam", "L06_nour-room"],
    ctx="Night turning to dawn in a child's bedroom. {adam} pulls himself up to sit against the side of the bed and finally breaks: silent at first, then aloud. Then a wide of the room as the light at the curtain edge turns grey-gold and he sits where he is.",
    map="Camera inside {L06_nour-room}. Midground: Adam on the floor with his back against the side of the bed at the left of the room, knees drawn up. Background: the curtained window on the back wall, the desk at right, the open door at far right.",
    first="The first frame is {adam} on the floor beside the bed, pushing himself up from lying to sitting.",
    segs=[(8.5, None, "MS", "47°", "locked, at floor-sitting height",
           "His back comes to rest against the bed frame at <1.5>. He stares ahead. At <2.5> his face folds and he cries in silence, mouth open, shoulders shaking; at <5.0> the sound comes, low and broken; at <7.0> he presses the heels of his hands into his eyes. Stars drift over him. Above him the bed shows only as a dark edge of blanket.", []),
          (3.5, "HARD CUT", "WS", "63°", "locked, eye level, the room's angle",
           "The room at the angle of {L06_nour-room}. {adam} sits small against the bed, head down on his knees, motionless. The line of light at the curtain edge changes from night blue to pale grey-gold, and the stars fade against the brightening wall.", [])],
    perf="Real, unpretty crying: the face crumples, the chin shakes, breath catches in hiccups; his eyes stay down.",
    phys="His shoulders heave; tears wet his cheeks and the heels of his hands.",
    light="Amber stars on deep blue; in the last segment cool dawn light slowly grows at the curtain edge. White balance 4300K.",
    audio="His crying, silent at first and then voiced; the night-light motor; in the last segment the first birds. From 5.0s, very sparse score: five single slow piano notes.",
    locks=["Adam's eyes stay down, away from the lens."])

# ============================================================== 10 · THE BAG
run(id="G40", scene="10 · The bag", nums="71", look="P", attach=["adam", "L05b_hallway-bag"],
    ctx="Dawn in the hallway. {adam} walks slowly up the hall to the console by the front door and stops in front of it, looking down at what lies there.",
    map="Camera at the near end of the hallway, exactly as in {L05b_hallway-bag}. Midground: Adam's path up the centre of the hall. Background: the dark front door; on the right the mirror and the console with the mail, the dead plant and the bag; on the left the glazed doors, pale with dawn.",
    first="The first frame is the hallway at the angle of {L05b_hallway-bag}, {adam} entering the bottom of the frame from behind the camera, barefoot, seen from behind.",
    segs=[(5, None, "WS", "63°", "locked, eye level",
           "He walks slowly up the hall at 2 km/h. At <3.5> he stops at the console and turns to face it, his profile toward the camera, looking down. His hands hang at his sides.", [])],
    perf="Heavy, slow steps; his head bowed.",
    phys="",
    light="Cool grey-blue dawn light through the glazed doors at frame left; the hallway pale and cold. White balance 5000K.",
    audio="Bare feet on terrazzo; first birds, faint. One long held piano note.",
    locks=["His hands stay at his sides; the console stays untouched."])

run(id="G41", scene="10 · The bag", nums="72, 73, 74", look="P", attach=["adam", "P06_hospital-bag", "P07_bag-contents", "L05b_hallway-bag"],
    ctx="Dawn at the console by the front door, only {adam}'s hands in frame: he lifts the sealed belongings bag out from under the mail and tears it open; a top shot of the four things inside laid out on the wood; his hands unfold a folded sheet of paper, its back to the camera.",
    map="Camera at the console in {L05b_hallway-bag}. The dark dusty wood of the console top fills the frame, envelopes pushed to one side, the sage wall behind.",
    first="The first frame is the console top, {P06_hospital-bag} lying dusty and sealed half under a slide of blank envelopes.",
    segs=[(4.5, None, "CU hands", "47°", "locked, at console height",
           "{adam}'s hands come in; at <0.8> he draws the bag out and dust slides off it. He holds it in both hands, thumbs on the seal, motionless until <2.6>. Then he tears the seal open along the top.", []),
          (5, "HARD CUT", "Top shot", "47°", "locked, straight down",
           "The console top from directly above. One at a time his hand sets down the things from {P07_bag-contents} in a row: at <0.5> the gold watch with the brown strap, its glass cracked, its hands stopped; at <1.6> a wedding ring; at <2.6> a short stub of yellow crayon; at <3.6> a sheet of paper folded in four, creased and dirty. His hand withdraws.", []),
          (4.5, "HARD CUT", "CU hands", "47°", "locked, at chest height",
           "His hands lift the folded paper and unfold it, once at <1.2>, twice at <2.6>, holding it upright toward his own face. The camera sees the back of the sheet: grey-white paper, fold lines, faint colour ghosting through. His thumbs tremble.", [])],
    perf="Hesitation in the hold; then steady, deliberate hands.",
    phys="Thick plastic stretches and tears; dust falls in a small cloud. Each object lands on wood with its own weight and contact shadow. Paper unfolds stiffly along old creases.",
    light="Cold pale dawn from frame left, soft shadows on the wood. White balance 5000K.",
    audio="Envelopes sliding, thick plastic tearing, a watch, a ring and a crayon set on wood, paper unfolding, his breath.",
    locks=["The paper shows only its blank back.", "The watch hands stay stopped."])

run(id="G42", scene="10 · The bag", nums="75 ★", look="P", attach=["adam", "L05b_hallway-bag"],
    ctx="Dawn in the hallway, a very slow push-in on {adam}'s face as he finally looks at his daughter's drawing: grief, and then a breath of a laugh.",
    map="Camera in the hallway of {L05b_hallway-bag}, frontal on Adam at the console. Foreground: the top edge of the sheet of paper he holds, its back to the camera, at the bottom of the frame. Background: the sage wall and the edge of the wall mirror, soft.",
    first="The first frame is {adam}'s face, eyes lowered to the paper he holds just below the frame.",
    segs=[(6, None, "CU", "29°", "very slow push-in at 0.5 km/h for the whole shot",
           "His eyes move slowly over the paper. At <1.2> his face breaks, brows drawing together, tears coming; at <2.6> a short breath of a laugh escapes him and he half smiles. He nods very slightly as he speaks, eyes on the paper.",
           [(3.2, 4.4, "Adam", "a whisper, breaking and smiling at once", "...I'm looking, sweetheart."),
            (4.8, 5.6, "Adam", "softer, steadier", "I'm looking.")])],
    perf="Grief and love in the same face: wet eyes, a trembling lower lip, the corners of the mouth lifting.",
    phys="The paper trembles slightly in his hands at the frame edge.",
    light="Cold pale dawn from frame left with the first warmth in it, catching the tears. White balance 5000K.",
    audio="His breath, the paper; birds outside. Sparse piano: five notes, slowly.",
    locks=["The paper shows only its blank back.", "His eyes stay on the paper for the whole shot."])

# ============================================================= 11 · DAYLIGHT
run(id="G43", scene="11 · Daylight", nums="77 ★", look="PW", attach=["adam", "doll-wife", "doll-daughter", "L03_living-dim", "L03b_living-day"],
    ctx="Morning in the living room. {adam} drags the heavy curtains open and daylight floods the room. {doll-wife} and {doll-daughter} sit side by side on the sofa.",
    map="Camera at the room's entrance as in {L03_living-dim}. Midground: the sofa with the two mannequins, the coffee table, the armchair. Background right: Adam at the curtains on the right wall, back to the room. The room ends looking as in {L03b_living-day}.",
    first="The first frame is the dim room as in {L03_living-dim}, {adam} at centre-right seen from behind, a hand on each curtain.",
    segs=[(6, None, "WS", "63°", "locked, eye level",
           "At <1.0> he pulls the curtains apart in one long drag. Hard morning sun bursts in, and by <3.0> the room looks as in {L03b_living-day}: sun shafts across the rug and floor, thick dust swirling in the beam, the city in the window. He stands in the light with his arms still out, squinting, and lets them drop at <5.0>. The two mannequins on the sofa are lit flat and plain by the sun.", [])],
    perf="He squints and breathes in; his shoulders open.",
    phys="Curtain rings slide along the rail; heavy fabric swings and settles. Dust swirls thickly through the sunbeams.",
    light="The shot starts in closed-curtain gloom with the floor lamp on and ends in hard full sun from the window at frame right. White balance 5600K.",
    audio="Curtain rings scraping on the rail; then the street, alive: traffic, voices, a street vendor calling in the distance, sparrows.",
    locks=["The mannequins stay seated and still.", "Adam and the window stay in the middle of the frame."])

run(id="G44", scene="11 · Daylight", nums="78, 79", look="PW", attach=["adam", "doll-wife", "doll-daughter", "L03b_living-day"],
    ctx="Morning in the sunlit living room. {adam} stands looking at {doll-wife} and {doll-daughter} on the sofa, plainly objects in borrowed clothes; then his hands unbutton the burgundy cardigan from the adult one, fold it and press it to his face for one breath.",
    map="Camera exactly as in {L03b_living-day}. Midground: the adult mannequin at the left of the sofa and the child mannequin at the right, side by side, facing forward; Adam in front of the sofa at frame left, his back three-quarters to the camera. Background: the floor lamp switched off, the sewing corner, the open window and sun at right.",
    first="The first frame is the sunlit room at the angle of {L03b_living-day}, {adam} standing still, arms at his sides, looking at the sofa.",
    segs=[(5, None, "WS", "63°", "locked, eye level",
           "In the sun the two figures are plainly things: scuffed plastic, visible seams, a cheap crooked wig, pins glinting in the yellow dress. Dust drifts through the light. At <3.5> he takes one step toward the adult mannequin.", []),
          (6, "HARD CUT", "CU hands", "47°", "locked, at chest height",
           "His hands at the front of the burgundy cardigan on the adult mannequin's rigid torso. He undoes three buttons at <0.6>, <1.3> and <2.0>, slides the cardigan off the stiff shoulders at <3.0>, folds it once against his chest, and at <4.4> lifts it and presses it to his face, eyes closed, breathing in.", [])],
    perf="Calm, slow hands; the breath into the wool is long and shaky.",
    phys="The mannequin is handled like a shop dummy; its arms stay at their angles as the sleeves slide off. Wool folds softly.",
    light="Hard daylight from the open window at frame right, crisp shadows, dust in the beams. White balance 5600K.",
    audio="Street sound through the open window; buttons, wool sliding off plastic, one long breath in.",
    locks=["The mannequins stay still; only Adam's hands move them."])

run(id="G45", scene="11 · Daylight", nums="80 ★", look="PW", attach=["adam", "doll-wife", "doll-daughter", "L03b_living-day"],
    ctx="Morning, the sunlit living room with the sewing corner at the back: {doll-wife} and {doll-daughter} stand back on their steel stands by the mirror. {adam} lays the loose yellow sleeve over the small one's shoulder and steps back.",
    map="Camera exactly as in {L03b_living-day}. Foreground: the armchair and the corner of the dining table. Midground: the sofa and coffee table, sun across the rug. Background: the two mannequins upright on their stands by the framed mirror in the sewing corner, Adam beside the child one, the sewing table and machine, the open window at right.",
    first="The first frame is the sunlit room at the angle of {L03b_living-day}, the adult mannequin bare on the left stand, the child mannequin on the right stand in the unfinished yellow dress, {adam} beside it holding the small yellow sleeve.",
    segs=[(6, None, "WS", "63°", "locked, eye level",
           "At <1.5> he lays the sleeve over the child mannequin's bare shoulder, where the missing sleeve belongs, and smooths it once. At <3.5> he takes two steps back toward the sewing table and stands looking at them, hands empty.", [])],
    perf="Quiet completion; his hands hang loose at the end.",
    phys="The sleeve drapes softly over the hard shoulder. The stands hold the mannequins upright and still.",
    light="Morning sun from the open window at frame right falling across the corner and the stands. White balance 5600K.",
    audio="Street sound, softer; cloth on plastic; his two steps. Warm, quiet piano: the five notes.",
    locks=["The adult mannequin is bare, bald ivory plastic; the child mannequin is bald and wears only the yellow dress.",
           "The yellow dress and sleeve hold the only saturated colour."])

# ============================================================= 12 · THE DOOR
run(id="G46", scene="12 · The door", nums="81", look="PW", attach=["L05_hallway"],
    ctx="Morning. Close on the inside of the front door, three gentle knocks.",
    map="Camera in the hallway of {L05_hallway}, close on the upper half of the front door: dark varnished wood, the brass chain and handle at right, sage wall at both edges, soft daylight on the wood.",
    first="The first frame is the upper half of the closed door, the brass chain slack across its latch, soft daylight on the wood.",
    segs=[(4, None, "Insert", "47°", "locked, at chain height",
           "Three gentle knocks at <1.0>, <1.6> and <2.2>; the chain barely trembles. Stillness.", [])],
    perf="",
    phys="The chain shivers slightly and settles.",
    light="Daylight reaches the hallway from the open rooms; the door is softly lit. White balance 5600K.",
    audio="Three soft knocks on wood; distant street sound from inside the apartment.",
    locks=["The door stays shut."])

run(id="G47", scene="12 · The door", nums="82", look="PW", attach=["adam", "L05_hallway"],
    ctx="Morning, a wide down the pale hallway: {adam} walks all the way to the front door, slides the chain off and puts his hand on the handle.",
    map="Camera at the near end of the hallway, exactly as in {L05_hallway}. Midground: Adam walking up the centre. Background: the front door; the mirror and the console with mail and a dead plant on the right; the glazed doors bright on the left.",
    first="The first frame is the hallway at the angle of {L05_hallway}, {adam} already in the middle of the hall, seen from behind, walking steadily toward the door.",
    segs=[(5, None, "WS", "63°", "locked, eye level",
           "He walks at 3 km/h and reaches the door at <2.2>. At <2.8> he slides the chain off; at <3.6> his hand closes on the handle. His shoulders rise with one breath and he holds there, the door still shut.", [])],
    perf="Steady, decided steps; one breath at the door.",
    phys="The chain slides along its track and drops, swinging.",
    light="Morning daylight from the rooms behind the camera; the hallway clear and pale. White balance 5600K.",
    audio="Bare footsteps, the chain sliding and dropping, one breath.",
    locks=["The console holds mail and a dead plant only.", "On the last frame the door is still shut."])

run(id="G48", scene="12 · The door", nums="83, 84 ★", look="PW", attach=["mona", "adam", "P14_foil-dish", "L09_landing"],
    ctx="Morning on the stairwell landing. The apartment door opens on {adam}; {mona}, standing on the doormat with a foil-covered dish, sees his face and understands before he speaks. Yesterday's identical dish sits on the floor at her feet. Then a close-up of him as he tries, fails, and finally says it.",
    map="Camera on {L09_landing}. Foreground: Mona at frame left in three-quarter back view, facing the door, {P14_foil-dish} in her hands and a second identical dish on the mat at her feet. Midground: the dark wooden apartment door at frame right. Background: the stairs and railing behind her; once the door opens, the bright apartment hallway behind Adam.",
    first="The first frame is {mona} in three-quarter back view at frame left, facing the closed door at frame right, the dish in her hands, the other dish at her feet.",
    segs=[(5, None, "WS two-shot from the landing", "47°", "locked, eye level",
           "At <0.8> the door opens inward and warm daylight falls across her. {adam} stands in the doorway: grey-blue shirt, bare feet, red eyes. They look at each other. At <3.0> her face, in three-quarter profile, changes: her brows lift and soften, her lips part. She stays silent.", []),
          (6, "REVERSE CUT", "CU", "29°", "locked, at her eye line",
           "{adam}'s face in the doorway, frontal, lit softly from the stairwell, the bright hall behind him. At <0.8> he opens his mouth and the words catch. He looks down, swallows, and looks back up at her at <2.4>. Then he says it, plainly; after it his face gives way.",
           [(3.2, 5.0, "Adam", "quiet, plain, the first true sentence", "They're gone, Mona.")])],
    perf="Mona's understanding is all in her eyes. Adam's chin trembles; after the line his mouth crumples.",
    phys="The door swings inward on its hinges; daylight spills across the landing floor.",
    light="The stairwell dim and grey-green; warm daylight pours out of the apartment as the door opens. White balance 5600K.",
    audio="The latch and the hinge, stairwell echo, street sound from inside the apartment.",
    locks=["Mona stays silent.", "Two foil dishes: one in her hands, one on the mat at her feet."])

run(id="G49", scene="12 · The door", nums="85 ★", look="PW", attach=["adam", "mona", "P09_drawing", "P01_yellow-cup", "L05_hallway"],
    ctx="Morning, a wide from inside the apartment looking down the hallway to the open front door: {mona} steps in and holds {adam}, two silhouettes in the bright doorway, while in the soft foreground the child's drawing stands propped against the yellow cup.",
    map="Camera inside the apartment, looking down the hallway of {L05_hallway} to the open front door. Foreground, lower left: the corner of the lace-covered dining table with {P09_drawing} leaning upright against {P01_yellow-cup}, soft. Midground: the hallway walls, the console and mirror. Background: Adam in the open doorway, the bright stairwell behind.",
    first="The first frame is the hallway receding to the open door, {adam} a dark figure in it with his head down, the drawing and the yellow cup soft in the foreground.",
    segs=[(6, None, "WS", "63°", "locked, eye level, focus on the doorway",
           "At <1.0> {mona} steps over the threshold and puts her arms around him; he stands rigid, then at <2.8> folds into her, his forehead on her shoulder. They hold, two silhouettes in the light. At <5.0> the focus eases forward to the drawing: the huge yellow sun, three small figures, a strip of blue.", [])],
    perf="His collapse into her is slow, starting at the shoulders.",
    phys="Her cardigan bunches under his hands; his back rises and falls.",
    light="The open front door is the brightest thing in the frame, burning out; the foreground in soft shade. White balance 5600K.",
    audio="Street sound, far; cloth; one long shaking breath out. Full, warm piano and strings completing the five-note tune.",
    locks=["The camera holds still; only the focus shifts at the end.", "The drawing carries pictures only."])

EDIT_ONLY = [
    ("01", "Black screen, 6s", "Sound only: road hum, wind, crayon on paper, a child humming five notes, a woman's soft laugh, a seatbelt click."),
    ("64", "White to black, 3s", "The white at the end of G35, held, then cut to black. A thin high tone."),
    ("76 ★", "The drawing, 5s", "Use the real drawing image full frame with a slow drift in the edit."),
    ("02–75", "4:3 crop", "Crop every present-day shot before the curtains to 4:3 from the centre."),
    ("77", "Aspect change", "Animate the crop from 4:3 open to 16:9 across G43."),
    ("86", "Title, 4s", "Black. Title: LOOK. The child's five-note hum, unfinished."),
    ("87", "Credits card, 3s", "One card, plus an AI-tools disclosure if the rules ask for one."),
]


def fmt(t):
    return f"{t:.1f}s"


def build(r):
    att = r["attach"]
    tag = {h: f"@image{i + 1}" for i, h in enumerate(att)}

    def sub(text, start=0.0):
        def t(m):
            assert m.group(1) in tag, (r["id"], m.group(1))
            return tag[m.group(1)]
        text = re.sub(r"\{([A-Za-z0-9_-]+)\}", t, text)
        return re.sub(r"<(\d+(?:\.\d+)?)>", lambda m: fmt(start + float(m.group(1))), text)

    segs = r["segs"]
    multi = len(segs) > 1
    o = ["SCENE CONTEXT", sub(r["ctx"]), "", "ACTIVE REFERENCES"]
    o += [f"{tag[h]} — {ANCHOR[h]}. 100% matches the reference." for h in att]
    o += ["", "LOCATION MAP", sub(r["map"]), "", "FIRST FRAME / BLOCKING", sub(r["first"]), "", "FORMAT MODE",
          "Timed multishot: cuts only at the stated seconds; the camera holds each segment without cutting on its own."
          if multi else "One continuous shot; the camera holds it without cutting on its own.", "", "OPTICS"]
    t = 0.0
    for d, cut, size, fov, cam, act, ls in segs:
        o.append(f"{fmt(t)} to {fmt(t + d)} — {size}, {fov} FOV.")
        t += d
    o += [OPTIC[r["look"]] + (" No drift mid-segment." if multi else ""), "", "CAMERA"]
    t = 0.0
    for d, cut, size, fov, cam, act, ls in segs:
        o.append(f"{fmt(t)} to {fmt(t + d)} — {cam}.")
        t += d
    o += [TONAL, "", "ACTION"]
    t = 0.0
    lines = []
    for d, cut, size, fov, cam, act, ls in segs:
        if cut:
            o.append(f"{fmt(t)} {cut}")
        body = sub(act, t)
        for a, b, who, how, words in ls:
            assert a < b <= d + 1e-6, (r["id"], words)
            body += f" {fmt(t + a)} to {fmt(t + b)}, {who}, {how}: \"{words}\""
            lines.append(f"{fmt(t + a)} {who}: \"{words}\"")
        o.append(f"{fmt(t)} to {fmt(t + d)} — {body}")
        t += d
    assert abs(t - round(t)) < 1e-6 and 4 <= t <= 30, (r["id"], t)
    r["dur"] = int(round(t))
    humans = [h for h in att if h in CHARS]
    perf = sub(r["perf"]) if r["perf"] else ""
    if humans and r["id"] != "G23":
        perf = (perf + " " + SKIN).strip()
    if perf:
        o += ["", "PERFORMANCE", perf]
    dolls = [h for h in att if h in DOLLS]
    phys = sub(r["phys"]) if r["phys"] else ""
    if dolls:
        phys = (phys + " The mannequins are hollow, hard and rigid; they keep every joint at its angle and move only where Adam's hands carry them.").strip()
    if phys:
        o += ["", "PHYSICS", phys]
    o += ["", "LIGHTING", sub(r["light"]), "", "AUDIO", sub(r["audio"])]
    if lines:
        o += ["Lines, each spoken once, in English: " + " · ".join(lines), "Only these voices are heard."]
    else:
        o.append("The sound is only the room and the listed effects.")
    o += ["", "STYLE", STYLE[r["look"]], "", "POSITIVE LOCKS"]
    locks = []
    for h in humans:
        if h == "adam":
            locks.append(f"Adam matches {tag[h]} in every frame he appears in: stubble, the healed scar at his right temple, the grey-blue shirt.")
        elif h == "adam-before":
            locks.append(f"Adam matches {tag[h]} in every frame he appears in: clean-shaven, smooth unmarked temples, the linen shirt.")
        else:
            locks.append(f"{ANCHOR[h].split(',')[0]} matches {tag[h]} in face, hair and clothes in every frame she appears in.")
    if dolls:
        locks.append(" and ".join(tag[h] for h in dolls) + (" stay" if len(dolls) > 1 else " stays")
                     + " rigid and motionless as furniture, with smooth blank faces.")
    locks += LOCKS[r["look"]] + [sub(k) for k in r["locks"]]
    if lines:
        locks.append("Each line lands once, at its time, from its speaker.")
    o += ["- " + k for k in locks]
    return "\n".join(o), tag


def main(md_path, html_path):
    built = [(r, *build(r)) for r in RUNS]
    total = sum(r["dur"] for r, _, _ in built)
    md = ["# LOOK — Seedance 2.5 prompts", "",
          f"**{len(built)} generations · {total} seconds of footage.** Written to the seedance-clean structure.", "",
          "## Settings for every run", "",
          "- **Seedance 2.5 Draft**, **16:9**, audio on. Generate a liked draft again in 1080p.",
          "- **Attach the element images in the order listed.** In the prompt the first is `@image1`, the second `@image2`, and so on.",
          "- The present (scenes 1–10) is framed centre-safe and cropped to 4:3 in the edit; the frame opens to 16:9 on the curtain shot.",
          "- All dialogue is English. Radio song and score in the clips are placeholders for the film's own music.",
          "- ★ hero shot · ○ can be dropped.", "",
          "## Run list", "", "| Run | Scene | Shots | Length | Attach, in order |", "|---|---|---|---|---|"]
    for r, _, tag in built:
        md.append(f"| [{r['id']}](#{r['id'].lower()}) | {r['scene']} | {r['nums']} | {r['dur']}s | "
                  + ", ".join(f"{i + 1} `{h}`" for i, h in enumerate(r["attach"])) + " |")
    md += ["", "## Made in the edit, not generated", "", "| Shot | What | How |", "|---|---|---|"]
    md += [f"| {s} | {w} | {h} |" for s, w, h in EDIT_ONLY]
    md += ["", "## Prompts", ""]
    for r, p, tag in built:
        md += [f"### {r['id']}", "", f"**{r['scene']} · shots {r['nums']} · {r['dur']}s**  ",
               f"{SETTINGS} · duration {r['dur']}s  ",
               "Attach in order: " + ", ".join(f"@image{i + 1} = `{h}`" for i, h in enumerate(r["attach"])), "",
               "```text", p, "```", ""]
    open(md_path, "w").write("\n".join(md))
    e = html.escape
    rows = "".join(f"<tr><td><a href='#{r['id']}'>{r['id']}</a></td><td>{e(r['scene'])}</td><td>{e(r['nums'])}</td>"
                   f"<td>{r['dur']}s</td><td>{e(', '.join(f'{i + 1} {h}' for i, h in enumerate(r['attach'])))}</td></tr>"
                   for r, _, _ in built)
    cards = "".join(
        f"<section id='{r['id']}'><header><h2>{r['id']}</h2><div class='meta'><b>{e(r['scene'])}</b> · shots {e(r['nums'])}"
        f" · <span class='pill'>{r['dur']}s</span> <span class='pill'>16:9</span></div>"
        f"<button onclick=\"cp(this)\">Copy prompt</button></header>"
        f"<div class='att'>Attach in order: {''.join(f'<code>@image{i + 1} = {e(h)}</code>' for i, h in enumerate(r['attach']))}</div>"
        f"<pre>{e(p)}</pre></section>" for r, p, _ in built)
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
<p class="lead">{len(built)} generations · {total} seconds of footage · seedance-clean structure</p>
<ul><li><b>Seedance 2.5 Draft</b>, <b>16:9</b>, audio on. Generate liked drafts again in 1080p.</li>
<li><b>Attach the element images in the listed order</b>: the first is <code>@image1</code>, the second <code>@image2</code>, and so on.</li>
<li>The present is framed centre-safe and cropped to 4:3 in the edit.</li>
<li>All dialogue is English. Radio song and score are placeholders for the film's own music.</li></ul>
<h2>Run list</h2><div class="tw"><table><tr><th>Run</th><th>Scene</th><th>Shots</th><th>Length</th><th>Attach, in order</th></tr>{rows}</table></div>
<h2>Made in the edit</h2><div class="tw"><table><tr><th>Shot</th><th>What</th><th>How</th></tr>{edit}</table></div>
{cards}</main><script>
function cp(b){{const t=b.closest('section').querySelector('pre').innerText;navigator.clipboard.writeText(t).then(()=>{{b.textContent='Copied';setTimeout(()=>b.textContent='Copy prompt',1200)}})}}
</script></body></html>"""
    open(html_path, "w").write(page)
    print(len(built), "runs,", total, "seconds")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
