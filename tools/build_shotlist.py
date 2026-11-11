#!/usr/bin/env python3
"""Builds shot-list.md with computed running timecodes."""
import sys

# (duration_s, priority, look, shot_size, picture, camera, sound)
# priority: "H" hero (must be perfect), "" normal, "C" cuttable if time runs out
# look: "P" present (4:3, locked, cool) / "F" flashback (full frame, handheld, warm) / "-" graphic
SCENES = [
    ("0 · COLD OPEN", "Black screen. The whole film is hidden in this sound.", [
        (6, "", "-", "Black",
         "Black screen. No title.",
         "—",
         "Road hum. Wind through a cracked window. A crayon scratching paper. A child humming a 5-note tune. A woman's soft laugh. A seatbelt CLICK → hard cut."),
    ]),
    ("1 · MORNING — kitchen / dining table", "A normal family breakfast. Hide the truth for 25 seconds, then show it plainly, with no music sting.", [
        (4, "", "P", "ECU, macro",
         "A stove igniter clicks (the click lands on the cut). Blue flame catches under a small pot.",
         "Locked.",
         "Igniter click, gas hiss. A wall clock. Fridge hum."),
        (5, "", "P", "Top shot, insert",
         "A man's hands lay three plates on a wooden table: two adult plates, one small plate. Three forks. A child's yellow plastic cup.",
         "Locked, straight down.",
         "Ceramic on wood. Clock."),
        (5, "", "P", "MS, from behind",
         "ADAM at the counter, sleeves rolled, cutting the crusts off toast and slicing it into triangles. Curtains closed, glowing with daylight they keep out.",
         "Locked, 50mm.",
         "Knife on board. He hums the 5-note tune, slightly off."),
        (6, "", "P", "Wide, through the kitchen doorway",
         "The dining table in the dim room. Two seated figures, backlit by the curtained window: silhouettes only. Adam enters frame with the plates and serves them.",
         "Locked. Doorway as a frame within the frame.",
         "ADAM: \"Good morning, my loves.\""),
        (4, "", "P", "CU Adam",
         "First clear look at him: tired, gentle, unshaven, a healed scar at the right temple. He smiles at someone off-screen and waits, the way you wait for an answer. A small laugh, as if he got one.",
         "Locked, 85mm.",
         "ADAM: \"Nour, sit up straight, habibti.\" A pause the length of a reply. Only the clock."),
        (5, "H", "P", "Over-shoulder → CU",
         "He bends to kiss his wife's forehead. Focus racks from his lips to her: smooth matte plastic, a wig line, a seam at the neck. A mannequin in a burgundy cardigan.",
         "Locked, slow rack focus. No push, no sting.",
         "The kiss makes a small hollow sound. Clock."),
        (5, "H", "P", "Wide frontal, symmetrical",
         "The tableau: Adam seated between two mannequins at breakfast. The adult in burgundy, the child-size one in an unfinished yellow dress (pins, white tacking thread, one sleeve missing). Three full plates. He does not eat.",
         "Locked, 35mm, dead centre. Hold longer than is comfortable.",
         "ADAM: \"Mama's almost finished your dress.\""),
        (3, "C", "P", "Insert",
         "The kitchen bin as he scrapes a plate: layers of identical untouched toast triangles from other mornings.",
         "Locked, top angle.",
         "Scrape. Lid closes."),
        (4, "", "P", "Insert, slow push-in",
         "The entry console by the front door: a pile of unopened mail, a dead plant, car keys, and a sealed clear hospital belongings bag, dusty, untouched. (No readable text anywhere.)",
         "Very slow push-in, 50mm.",
         "Clock, further away. A neighbour's door somewhere."),
        (5, "", "P", "CU hands",
         "Adam kneels and fastens a small yellow sandal onto the child mannequin's rigid foot. The buckle closes.",
         "Locked, low.",
         "Buckle CLICK (same sound as the seatbelt)."),
        (2, "", "F", "ECU — FLASH 1",
         "A seatbelt tongue snapping into its buckle. A small hand. Golden light.",
         "Handheld, macro.",
         "The click, doubled. One beat of road hum."),
        (2, "", "F", "CU — FLASH 1",
         "A child's legs swinging off a back seat, yellow sandals, crayons rolling on the upholstery.",
         "Handheld.",
         "A second of the child's hum. Cut dead."),
        (4, "", "P", "CU Adam",
         "Still kneeling. Frozen, blinking. His fingers go to the scar. He shakes it off like a man waking up.",
         "Locked.",
         "Silence, then the clock returns. ADAM: \"...Where were we.\""),
    ]),
    ("2 · HAIR — living room, late morning", "Care as routine. The first time the illusion physically slips.", [
        (5, "", "P", "Wide",
         "Adam carries the child mannequin across the living room the way you carry a sleeping child: stiff legs sticking out, his hand cradling the head. He sets it on the sofa. The adult mannequin already sits in the armchair.",
         "Locked, 35mm. Safer staged from behind him.",
         "Footsteps. Plastic creak."),
        (6, "", "P", "MCU, profile",
         "He brushes the child mannequin's wig and attempts a braid with clumsy fingers. A glance toward the armchair.",
         "Locked, 85mm.",
         "ADAM: \"Mama does it better, I know. Don't tell her I said that.\""),
        (3, "", "P", "ECU",
         "The brush snags. The wig shifts sideways, exposing bare plastic scalp.",
         "Locked, macro.",
         "Bristles. A dry slide."),
        (3, "", "F", "CU — FLASH 2",
         "NOUR (6), real, eyes closed, laughing, wind from the car window whipping her hair. Sun flare.",
         "Handheld, 28mm, close.",
         "Wind roar, her laugh."),
        (3, "C", "F", "CU — FLASH 2",
         "A woman's hand reaches back from the front seat and tucks the hair behind the girl's ear. A wedding ring catches the sun.",
         "Handheld.",
         "Wind. The radio, faint."),
        (5, "", "P", "CU Adam",
         "His breath caught. Carefully, guiltily, he straightens the wig, smoothing it down with his palm.",
         "Locked.",
         "ADAM: \"Sorry. Sorry, habibti.\""),
    ]),
    ("3 · THE SEWING CORNER", "One shot. Answers where the mannequins came from, and plants the ending.", [
        (5, "", "P", "Wide, slow push-in",
         "LAYLA's sewing corner: a sewing machine still threaded with yellow thread, a pincushion, fabric rolls. The missing yellow sleeve lies under the needle. Two empty mannequin stands, clean circles in the dust where they stood.",
         "Slow push-in toward the sleeve under the needle.",
         "The clock. From the kitchen, a radio dial clicks on, static."),
    ]),
    ("4 · THE SONG & THE DANCE — evening", "The happiest he gets, and the moment it breaks in his hands.", [
        (4, "", "P", "Insert",
         "His hand tunes an old radio. Static resolves into a warm, old-fashioned song (original composition built on the 5-note tune).",
         "Locked, macro.",
         "Static → song."),
        (5, "", "P", "MS",
         "Adam cooking, stirring a pot, swaying a little. The adult mannequin stands in the kitchen doorway where he has placed her, as if watching him.",
         "Locked, 50mm.",
         "ADAM: \"You always say I put too much salt.\""),
        (3, "", "F", "Insert — FLASH 3",
         "The car radio. A woman's fingers turn the volume up on the same song.",
         "Handheld, macro.",
         "The song, brighter, through car speakers."),
        (4, "H", "F", "CU — FLASH 3",
         "LAYLA, real, in profile in the passenger seat, golden light, singing along badly and laughing at herself. She turns to look at him. Our first clear view of her face.",
         "Handheld, 35mm, from the driver's side.",
         "Her voice over the song."),
        (4, "", "P", "CU Adam",
         "A real smile, eyes wet. He wipes his hands on a cloth and holds one out toward the doorway.",
         "Locked.",
         "ADAM: \"Dance with me.\""),
        (8, "H", "P", "Wide, living room",
         "He slow-dances with the mannequin in the lamplight, her rigid arm over his shoulder, his cheek against her wig. The child mannequin sits on the sofa, facing them. This is the poster.",
         "Locked, 35mm, symmetrical. He turns; the camera does not.",
         "The song, small, from the kitchen. His feet shuffling."),
        (4, "", "P", "CU",
         "His face against the plastic cheek, eyes closed. Peace.",
         "Locked, 85mm.",
         "Song. His breathing."),
        (3, "", "F", "Insert — FLASH 3",
         "Her hand resting on his on the gearshift, her thumb stroking his knuckle.",
         "Handheld, macro.",
         "Song through car speakers. Road hum."),
        (3, "", "P", "CU",
         "The mannequin's arm slips out of its shoulder socket and slides down his back.",
         "Locked.",
         "A dry plastic pop."),
        (4, "", "P", "Wide",
         "The arm hits the floor and rocks to a stop. He stands holding a one-armed mannequin. The song keeps playing.",
         "Locked, same frame as the dance.",
         "Hollow knock on the floor. Song, indifferent."),
        (6, "H", "P", "MCU",
         "On his knees, he works the arm back into the socket, far too gently, far too fast. It clicks in. He holds the plastic hand against his forehead.",
         "First camera instability in the present: a slight handheld breath.",
         "ADAM: \"I'm sorry. I'm sorry. Did I hurt you?\""),
    ]),
    ("5 · THE KNOCK", "The outside world. The only other living person, and we only hear her.", [
        (3, "", "P", "Insert",
         "The front door from inside. Three knocks shake the chain.",
         "Locked.",
         "Knocks. The song under them."),
        (4, "", "P", "CU Adam",
         "He freezes, then reaches and turns the radio off.",
         "Locked.",
         "Song cuts. Total silence. Clock."),
        (8, "", "P", "Wide, down the hallway",
         "Adam small and still in the middle of the hall. The front door at the far end, a line of landing light under it, the shadow of two feet.",
         "Locked, 35mm, deep focus.",
         "MONA (O.S., through the door): \"Adam. I know you're in there. It's been four months... I lost them too.\""),
        (5, "H", "P", "CU",
         "He crouches by the child mannequin on the sofa and puts a finger to his lips.",
         "Locked, 85mm.",
         "ADAM (whisper): \"Shh. We're playing the quiet game.\""),
        (4, "C", "P", "Insert, floor level",
         "The gap under the door: the shadow sets something down. A foil-covered dish slides into the light. The feet leave.",
         "Locked, on the floor.",
         "Foil crinkle. Footsteps down a stairwell."),
        (4, "", "P", "CU Adam",
         "He listens to the steps fade. For one second his jaw trembles: somewhere, he knows. Then the mask comes back.",
         "Locked.",
         "ADAM: \"Who wants dinner?\""),
    ]),
    ("6 · DINNER & THE HEADLIGHTS — night", "A mirror of the breakfast tableau. The memory starts forcing its way in.", [
        (6, "", "P", "Wide frontal, symmetrical",
         "Same frame as the breakfast tableau, now night, one pendant lamp. Steam rises off three plates. He talks; he does not eat.",
         "Locked, identical to the breakfast wide.",
         "ADAM: \"Tomorrow we go to the sea. I promise. This time we'll get there.\""),
        (4, "", "P", "Insert",
         "He pours water into the yellow cup and keeps pouring. It overflows and spreads across the table. His eyes are somewhere else.",
         "Locked.",
         "Water. Far outside, a truck horn."),
        (4, "H", "P", "Wide, side angle",
         "A vehicle passes in the street. Its headlights come through the gap in the curtains, sweep across the wall and slide over the two blank faces.",
         "Locked. The light does all the moving.",
         "Engine passing, low."),
        (2, "", "F", "POV — FLASH 4",
         "Through a windshield: a desert road at dusk, oncoming headlights blooming.",
         "Handheld.",
         "Horn, rising."),
        (2, "", "F", "CU — FLASH 4",
         "Layla's face turning toward the road, her smile dropping. Cut to white on the last frames.",
         "Handheld.",
         "Horn → cut to nothing."),
        (5, "", "P", "CU Adam",
         "He is gripping the table edge. The cup is on its side, water running off the table. He looks at each of them.",
         "Slight handheld breath.",
         "Dripping. ADAM: \"...It's late. Bedtime.\""),
    ]),
    ("7 · BEDTIME — Nour's room", "The quietest scene. The only time the present lets her voice in.", [
        (5, "", "P", "Wide, through the doorway",
         "He carries the child mannequin down the dark hallway toward a room glowing with a star night-light.",
         "Locked, behind him.",
         "Footsteps. Dripping, fading."),
        (6, "", "P", "MS",
         "He tucks her in, pulls the blanket up to the plastic chin and sets a stuffed rabbit beside her. Crayon scribbles taped to the wall (shapes only, no words).",
         "Locked, 50mm.",
         "Blanket. Night-light motor, a faint tick."),
        (6, "", "P", "CU Adam, night-light on his face",
         "He kisses the forehead and stays there a moment too long. Stars drift slowly over his face.",
         "Locked, 85mm.",
         "ADAM: \"Tomorrow, the sea. Sleep now.\""),
        (4, "", "P", "Wide",
         "He reaches the door and switches off the lamp. Only the stars remain. His silhouette in the doorway.",
         "Locked.",
         "Switch. Silence. No clock in this room."),
        (5, "H", "P", "CU, profile in the doorway",
         "He is about to leave. He stops.",
         "Locked. Do not cut to the bed.",
         "Three seconds of nothing. Then, close and clear, a child's voice, the only time in the present: NOUR (O.S.): \"Baba... look.\""),
        (4, "H", "P", "CU face",
         "He does not turn around. His eyes fill.",
         "Very slow push-in.",
         "ADAM (whisper): \"...Not now, habibti.\" NOUR (brighter, car acoustics): \"Baba, LOOK!\" Road hum swells → cut."),
    ]),
    ("8 · THE ROAD — the full memory", "Full frame, handheld, warm. For the first time the fragments play in order and do not stop.", [
        (5, "", "F", "Wide exterior, tracking",
         "A modest family sedan on a two-lane desert road at golden hour. A thin line of sea on the horizon. An inflatable swim ring pressed against the back window.",
         "Tracking alongside, stable.",
         "The song on the car radio. Road hum, warm."),
        (4, "", "F", "Interior, from the back seat between the front seats",
         "Adam driving, Layla beside him, her hand on his. Sun low through the windshield.",
         "Handheld, 24mm.",
         "Layla singing along. He laughs at her."),
        (4, "", "F", "CU Nour",
         "Back seat. Nour drawing with a yellow crayon, tongue between her teeth, the paper on a book on her knees. She hums the 5-note tune.",
         "Handheld, 50mm.",
         "Crayon on paper (the sound from the cold open)."),
        (4, "", "F", "CU Layla",
         "She looks back at Nour, then at Adam.",
         "Handheld.",
         "LAYLA: \"An hour she's been drawing. She won't show me.\""),
        (3, "", "F", "CU, rear-view mirror",
         "Adam's eyes in the mirror, smiling.",
         "Handheld, macro.",
         "ADAM: \"What are you drawing, Nour?\""),
        (4, "", "F", "CU Nour",
         "She finishes with a flourish and holds the paper up. We see only its back, the sun glowing through it: shapes, nothing readable.",
         "Handheld.",
         "NOUR: \"Baba, look!\""),
        (4, "", "F", "MCU Adam",
         "Eyes on the road, the sun in them. He flips the visor down.",
         "Handheld.",
         "ADAM: \"One minute, habibti. I'm driving.\""),
        (3, "", "F", "CU Nour",
         "Leaning forward against the seatbelt, the paper held higher.",
         "Handheld.",
         "NOUR: \"Babaaa. Look!\""),
        (3, "", "F", "CU Layla",
         "Laughing, touching his arm.",
         "Handheld.",
         "LAYLA: \"Look at it, or she'll never stop.\""),
        (5, "H", "F", "CU Adam, slow motion",
         "He turns his head back. As he sees it, his face opens into pure joy. This is the happiest image in the film.",
         "Handheld, slow motion, 50mm.",
         "Sound drops to a muffled underwater hush. Only the 5-note hum stays clear."),
        (3, "", "F", "His POV",
         "Nour beaming, holding the paper up, so backlit that the drawing is burned out by the sun. We still do not see it.",
         "Handheld.",
         "The hush."),
        (2, "", "F", "CU Layla",
         "Her eyes go to the road. The smile falls.",
         "Handheld.",
         "LAYLA: \"Adam—\""),
        (2, "", "F", "Through the windshield",
         "Truck headlights filling the glass.",
         "Handheld, shaking.",
         "Horn, full."),
        (3, "", "-", "White → black",
         "Pure white. Then black. No impact is shown.",
         "—",
         "Everything cuts to nothing. A thin high tone."),
        (5, "H", "F", "Ground-level macro",
         "Asphalt at dusk. A yellow crayon rolls slowly across frame and stops against glittering crumbs of safety glass. Orange hazard light blinking, out of focus. No bodies, no blood.",
         "Locked, on the ground.",
         "The tone. A hazard relay ticking (the clock)."),
        (4, "H", "F", "ECU",
         "Adam's open eye, his cheek on the asphalt. Orange light blinking in it. A sheet of paper drifts past, out of focus.",
         "Locked.",
         "Tick. Tick. His breath."),
    ]),
    ("9 · THE FLOOR — Nour's room, night to dawn", "The lie has nowhere left to stand. Back to 4:3.", [
        (6, "H", "P", "ECU, match cut",
         "The same eye, the same angle, his cheek now on the bedroom floor. Night-light stars turning over his face.",
         "Locked. Exact match to the asphalt framing.",
         "The tick becomes the night-light motor."),
        (5, "H", "P", "His POV, low angle",
         "The bed. Under the blanket, plainly, a child-size plastic figure with its wig askew. Nothing else. Nothing speaks.",
         "Locked.",
         "Silence."),
        (8, "H", "P", "MS",
         "He pulls himself up against the bed and finally breaks: silent first, then with sound. The first real crying in the film. Hold it.",
         "Locked, 50mm. No cut.",
         "His voice. Score enters for the first time: the 5-note tune, single piano or oud notes."),
        (3, "C", "P", "Wide",
         "The room. He has not moved. The window edge turns from blue to grey-gold.",
         "Locked. Light change only.",
         "Score, very thin. First birds."),
    ]),
    ("10 · THE BAG — dawn, entry hall", "The thing he has walked past every day. He finally looks.", [
        (4, "", "P", "Wide, hallway",
         "He walks slowly to the entry console.",
         "Locked, the same hallway frame as the knock.",
         "Bare feet. Score holds one note."),
        (4, "", "P", "CU hands",
         "He lifts the sealed hospital bag out from under the mail. Dust slides off. He hesitates, then tears the seal.",
         "Locked.",
         "Plastic tearing."),
        (5, "", "P", "Top shot, insert",
         "The contents on the console: a woman's watch with a cracked face, stopped; a wedding ring; a stub of yellow crayon; a folded sheet of paper, creased and dirty.",
         "Locked, straight down (echo of the three plates).",
         "Objects on wood."),
        (5, "", "P", "CU hands",
         "He unfolds the paper. Its back is to us.",
         "Locked.",
         "Paper. His breath."),
        (6, "H", "P", "CU Adam",
         "His face as he sees it. Grief, and then, impossibly, a breath of a laugh.",
         "Very slow push-in, 85mm.",
         "ADAM: \"...I'm looking, habibti. I'm looking.\""),
        (5, "H", "-", "Insert, full frame",
         "The drawing, in crayon: three figures holding hands, the smallest in the middle, a strip of blue sea, their little car, and a huge yellow sun. No words. (Use a real child's drawing, scanned.)",
         "Slow drift.",
         "Score: the tune completes for the first time."),
    ]),
    ("11 · DAYLIGHT — morning", "The frame opens. The mannequins become objects again, and he lets them. From the curtain shot to the end, the present plays full width.", [
        (6, "H", "P", "MS",
         "He drags the heavy curtains open. Daylight floods the living room for the first time, dust hanging in the beam. During this shot the frame widens from 4:3 to full width.",
         "Locked. Aspect ratio opens over the shot.",
         "Curtain rings. The street, alive: traffic, voices, a vendor."),
        (5, "", "P", "Wide",
         "In hard daylight the two mannequins on the sofa are just objects in borrowed clothes. He stands looking at them.",
         "Locked, 35mm.",
         "Street sound. No score."),
        (6, "", "P", "CU hands",
         "He unbuttons the burgundy cardigan from the adult mannequin, folds it and presses it to his face for one breath.",
         "Locked.",
         "Buttons. His breath in the wool."),
        (6, "H", "P", "Wide, the sewing corner",
         "Both mannequins back on their stands, bare, except the child form still wearing the unfinished yellow dress. He lays the loose sleeve over its shoulder and steps back.",
         "Locked, same frame as scene 3.",
         "Score returns, warm."),
    ]),
    ("12 · THE DOOR", "The theme, in one action: he lets someone in. Full width.", [
        (3, "", "P", "Insert",
         "The front door. Three knocks, softer than last time.",
         "Locked, same insert as scene 5.",
         "Knocks."),
        (5, "", "P", "Wide, down the hallway",
         "The hallway frame from the knock scene. This time he walks all the way to the door. His hand on the handle. One breath.",
         "Locked.",
         "Footsteps. Chain sliding."),
        (5, "", "P", "Reverse, from the landing",
         "The door opens. MONA, mid-forties, holds a covered dish; yesterday's dish is still at her feet. She sees his face and understands before he speaks.",
         "Locked, 50mm.",
         "Stairwell echo."),
        (6, "H", "P", "CU Adam",
         "He tries to speak and can't. Then he says it aloud for the first time.",
         "Locked, 85mm.",
         "ADAM: \"They're gone, Mona.\""),
        (6, "H", "P", "Wide, from inside the apartment",
         "She steps in and holds him: two silhouettes in the bright doorway. In the soft foreground, on the table, the drawing propped against the yellow cup.",
         "Locked. Hold, then cut to black on a breath.",
         "Score, full, then out."),
    ]),
    ("END", "", [
        (4, "", "-", "Title",
         "Black. Title: LOOK  ·  بُصّ",
         "—",
         "Over black: the child's 5-note hum, alone, unfinished."),
        (3, "", "-", "Credits card",
         "One card: credits, plus an AI-tools disclosure if the rules ask for one.",
         "—",
         "Silence."),
    ]),
]

LOOK = {"P": "Present", "F": "Memory", "-": "—"}
MARK = {"H": " ★", "C": " ○", "": ""}


def tc(s):
    return f"{s // 60}:{s % 60:02d}"


def main(out):
    lines = []
    n = 0
    t = 0
    summary = []
    counts = {"H": 0, "C": 0, "": 0}
    look_secs = {"P": 0, "F": 0, "-": 0}
    cut_secs = 0
    body = []
    for title, intent, shots in SCENES:
        start = t
        body.append(f"## {title}")
        body.append("")
        if intent:
            body.append(f"*{intent}*")
            body.append("")
        body.append("| # | In | Dur | Look | Shot | Picture | Camera | Sound & dialogue |")
        body.append("|---|---|---|---|---|---|---|---|")
        for dur, pri, look, size, pic, cam, snd in shots:
            n += 1
            counts[pri] += 1
            look_secs[look] += dur
            if pri == "C":
                cut_secs += dur
            body.append(
                f"| {n:02d}{MARK[pri]} | {tc(t)} | {dur}s | {LOOK[look]} | {size} | {pic} | {cam} | {snd} |"
            )
            t += dur
        body.append("")
        summary.append((title, tc(start), tc(t), t - start, len(shots)))

    total = t
    lines.append("# LOOK — Shot List")
    lines.append("")
    lines.append(
        f"**{n} shots · running time {tc(total)}** (limit 7:00, so {420 - total}s of safety margin). "
        "Timecodes are computed from the durations, so they add up."
    )
    lines.append("")
    lines.append("How to read it:")
    lines.append("")
    lines.append(
        f"- **★ hero shot** ({counts['H']} of them): the film lives or dies on these. Generate them first and spend the retries here."
    )
    lines.append(
        f"- **○ cuttable** ({counts['C']} shots, {cut_secs}s): drop these first if the schedule slips. The story survives without them."
    )
    lines.append(
        f"- **Look = Present** ({look_secs['P']}s): 4:3 frame, camera locked off, curtains closed, cool and dusty, yellow is the only strong colour."
    )
    lines.append(
        f"- **Look = Memory** ({look_secs['F']}s): full-width frame, handheld, golden hour, warm, alive."
    )
    lines.append(
        "- Durations are edit lengths. Generate each clip a little longer and trim; the 2–3s flashes are cut out of longer takes."
    )
    lines.append(
        "- Dialogue is written in English here. Recommended delivery is Egyptian Arabic with English subtitles (see `story.md`)."
    )
    lines.append("")
    lines.append("## Scene map")
    lines.append("")
    lines.append("| Scene | In | Out | Length | Shots |")
    lines.append("|---|---|---|---|---|")
    for title, a, b, d, c in summary:
        lines.append(f"| {title} | {a} | {b} | {d}s | {c} |")
    lines.append(f"| **Total** | 0:00 | {tc(total)} | **{total}s** | **{n}** |")
    lines.append("")
    lines.extend(body)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")
    print(f"shots={n} total={total}s ({tc(total)}) hero={counts['H']} cuttable={counts['C']} ({cut_secs}s)")
    print(f"present={look_secs['P']}s memory={look_secs['F']}s graphic={look_secs['-']}s")
    for row in summary:
        print(row)


if __name__ == "__main__":
    main(sys.argv[1])
