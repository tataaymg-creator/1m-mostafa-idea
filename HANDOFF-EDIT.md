# LOOK · بُصّ — Handoff for the edit (2026-11-13)

Generation is finished. Every shot of the film is rendered at 1080p. The next job is the **rough cut** from these 1080p files, done on the user's own machine (Cowork). No more credits should be spent. The balance is about 450 and is for emergencies only.

## The film in one breath
Four months after a car crash killed his wife Layla and his daughter Nour (6), Adam keeps them alive at home as two shop mannequins. He serves them breakfast, braids the "daughter's" wig and dances with the "wife". Memories of the last drive break through in golden flashes. The last thing Nour said was **"Daddy, look!"**: she was holding up a drawing, he turned to look, and a truck hit them. At dawn he opens the hospital bag, finds the drawing and finally looks at it. He opens the curtains, takes the cardigan off the mannequin and opens the door to the neighbour Mona: **"They're gone, Mona."** She holds him. The film ends on the drawing on the floor.

- **Present:** a locked camera, a dim and dusty apartment, the curtains closed, sage-green walls. Yellow is the only strong colour (her dress, her cup, her sandal, the sun in her drawing).
- **Memory:** handheld, golden hour, warm, inside the car.
- **Format: everything stays 16:9.** The 4:3 idea from story.md was dropped by the user.
- **Sound:** all dialogue is in English and already inside the clips. No generated music exists. The song and the score are laid in during the edit. Before Adam breaks, the sound is only the room, the clock and the radio; the score enters when he breaks (G39 / G42b).

## Where the files are
Higgsfield project **baba look**, workspace `dad22dc2-d036-464d-9396-e84c3e0468e1`, project `92c8dd8a-7d90-4f19-9975-375b4becd001`.
- **`1080p FINAL`** (`33af5c6e-da18-45b4-aa2b-34f0e6ec871b`): the 38 clips below, 1920×1080, 24 fps, with audio. **This is the only source for the cut.** (The Higgsfield UI shows the count as 39, but there are 38 clips in it.)
- `FAVOURITES / DONE - upscaled to 1080p`: the 480p drafts behind them (reference only).
- Every clip downloads from `https://d8j0ntlcm91z4.cloudfront.net/user_3LxkwQeztcBcNp4neSeDhfcB8SR/hf_20261113_<stamp>_<job id>.mp4`; the stamp and id are listed below.
- Repo (branch `claude/wonderful-noether-yx6bsb`): `story.md`, `shot-list.md` (the original 87-beat script), `tools/rough_cut.py` (the ffmpeg recipe of the approved 480p rough cut v5, updated to this list), `props/P09-drawing.jpg` (the drawing at 1920×1086).

## Final shot list, in cut order (38 clips, 349.6 s raw)
Time = seconds inside the clip. "Whole" = use the full clip.

| # | Shot | 1080p clip (stamp_job id) | Len | What it is | Lines in the clip | Cut |
|---|---|---|---|---|---|---|
| | — | black card | 2 | Open on black | | |
| 1 | G01 | 104916_75cdf456-1166-42f0-acfc-ec1124f1635e | 10 | Kitchen at dawn: burner lit, Adam cuts toast into triangles | | whole |
| 2 | G03 | 104923_c4da3721-fe1d-4885-b9a7-e76137909e1c | 10 | Through the kitchen doorway: he serves two silhouettes | 3.8 "Good morning, my loves." · 6.4 "Nour, sit up straight, sweetheart." | whole |
| 3 | G04 | 104926_a7e0c581-e213-45f1-8adb-0c88d779291d | 5 | He kisses his wife's forehead; focus reveals the mannequin | | whole |
| 4 | G05 | 104931_4e54b526-563f-41d3-abad-f0b328ca1dd1 | 6 | Symmetrical tableau: Adam between the two mannequins, three full plates | 0.8 "Mommy's almost finished your dress." | whole |
| 5 | G06 | 104348_5674b3bf-08a4-4a93-a659-6e13466f5ef8 | 4 | Bin full of untouched toast | | whole |
| 6 | G08 (a) | 104943_3cbc8acf-98ce-487a-8590-71f68324713e | 10 | He buckles the yellow sandal on the child mannequin | | 0 → 1.4 (cut on the buckle click) |
| 7 | G09 | 104945_26e3c884-7b75-4b82-b432-b585a7d809d2 | 5 | FLASH 1: seatbelt click, small legs swinging | | whole |
| 8 | G08 (b) | same as 6 | | Back on his face | 8.2 "...Where were we." | 3.71 → end |
| 9 | G10 | 104955_edec3f86-6f9a-4618-8d26-bd45529930ad | 5 | He carries the child mannequin to the sofa | | whole |
| 10 | G11 | 104959_d43aae34-27e9-4af2-843c-d0c3bb051153 | 15 | Brushing and braiding the wig; it slides off; he puts it back | 1.0 "Mommy does it better, I know." · 3.9 "Don't tell her I said that." · 11.4 "Sorry." · 13.0 "Sorry, sweetheart." | whole |
| 11 | G12 | 105009_62781679-3a0c-4ab4-a8b2-69d4ba567698 | 6 | FLASH 2: Nour laughing in the wind, her mother's hand | | whole, **mirrored (hflip)** so Nour reads in the back right seat |
| 12 | G14 | 105025_7eb7d7b4-fa65-4e9e-bd64-6fd24981c132 | 13 | Radio on, he cooks; the wife mannequin in the doorway; he holds out his hand | 6.0 "You always say I put too much salt." · 11.3 "Dance with me." | whole |
| 13 | G15a | 105037_3e014883-d59c-4870-9ae0-d6ec0cc6823d | 4 | FLASH 3: Layla's hand turns up the car radio | | whole |
| 14 | G15 | 121024_c0fbc45f-6715-42fe-b4ca-01ac14b7677b | 10 | FLASH 3: Layla singing, looking at him | | 2.875 → end, **mirrored (hflip)** so she reads as the passenger |
| 15 | G16 | 105042_c81fab5b-5562-41d7-916b-b8471535a84e | 8 | He slow-dances with the wife mannequin (the poster shot) | | whole |
| 16 | G17 | 105044_4f67699a-6d98-4a6b-bec3-d94fc4a412b1 | 8 | Cheek to plastic; the arm slips out of the socket | | whole |
| 17 | G18 | 173658_8fc9425f-824c-4a10-92e6-d22807b650d0 | 10 | Arm on the rug; he sits her in the armchair; kneels, picks up the arm, holds it to his forehead | ~4.4 "I'm sorry. I'm sorry." · ~8.2 "Did I hurt you?" | whole (new take: he does not reattach the arm) |
| 18 | G46 (1st use) | 105504_57ce35e4-05fa-4004-92c4-f9773a2e6d9f | 4 | Three knocks on the front door | | whole. The approved rough cut left it ungraded; optionally grade it darker for the night (it is a morning shot). Mona's voice comes in G21. |
| 19 | G20 | 105050_3e40cf5d-0cd8-4be8-a41a-180bfd52dfe6 | 5 | He freezes and switches the radio off | | whole (the song stops here) |
| 20 | G22 | 105103_5336dcca-0a2b-4cca-ab68-9a84ca200c50 | 10 | Finger to his lips by the child mannequin | 1.4 "Shh." · 2.4 "We're playing the quiet game." | 0 → 4.66 (drop "Who wants dinner?") |
| 21 | G21 | 105058_dfb4ec2d-3607-4461-8ff6-951ded6eee74 | 8 | Deep wide down the hallway; Mona through the door | 0.6 "Adam." · 1.8 "I know you're in there." · 4.0 "It's been four months..." · 6.2 "I lost them too." | whole |
| 22 | G25 (a) | 105108_ad78de1e-5805-4804-aef7-acacf8761dcc | 8 | Dinner, the yellow cup spilled (played as a jump cut) | | 0 → 4.0 |
| 23 | G27 (from G34) | 110040_e40f8a66-3cf0-4bfc-b638-32d4094e9472 | | FLASH 4: headlights in his eyes | | G34 6.4 → 7.9, fade to white over the last 0.5 s |
| 24 | G25 (b) | same as 22 | | | 5.4 "...It's late." · 6.5 "Bedtime." | 4.0 → end |
| 25 | G29 | 105116_fd275e76-d59f-4864-9ab9-c48c4e0e0b7d | 16 | He tucks the child mannequin in, stars on the walls | 9.8 "Tomorrow, the sea." · 11.0 "Sleep now." | 0 → 12.0 |
| 26 | G30 | 105119_50a92775-23de-44d5-bce0-f8cd4e0b4c9a | 10 | In the doorway he stops; her voice behind him | 3.6 Nour: "Daddy... look." · 6.5 "...Not now, sweetheart." · 8.5 Nour: "Daddy, LOOK!" | whole |
| 27 | G31 | 105122_cea29628-df6b-48b6-9382-d5187a916bd7 | 5 | MEMORY: the family car on the desert road, golden hour | | whole |
| 28 | G32 | 105124_ac03bced-87ff-4175-94d7-0c17cbf3c1a8 | 15 | Inside the car: hands on the gearshift, Nour drawing | 9.2 Layla: "An hour she's been drawing." · 10.8 "She won't show me." · 12.6 Adam: "What are you drawing, Nour?" | whole |
| 29 | G33 | 175138_acc506d2-1153-4e03-bcc1-495dcb2b03a9 | 14 | Nour holds up the drawing; Adam drives; Layla laughs | 1.4 Nour: "Daddy, look!" · 5.4 "One minute, sweetheart." · 6.6 "I'm driving." · 8.4 Nour: "Daddyyy. Look!" · 11.8 Layla: "Look at it, or she'll never stop." | whole. **New take, no flip.** Nour sits in the middle of the back seat (accepted by the user). |
| 30 | G34 | same as 23 | 8 | Slow motion: he turns to look at her drawing and laughs; the truck fills the windshield | | whole, fade to white over 7.5 → 8.0 |
| | — | white card 1.5 + black card 1.5 | 3 | The crash is never shown | | |
| 31 | G36 | 110024_de3d5a1b-5121-464d-80af-6bd5f1dca3ed | 5 | A yellow crayon rolls across the asphalt to the safety glass | | whole |
| 32 | G37 | 110020_33a5ba80-1326-4518-9e94-1b574a5c803d | 10 | Match cut on his eye: asphalt → bedroom floor | | whole (match cut at 4.125) |
| 33 | G39 | 130826_1e46116c-73e5-40ba-82a0-0585d8eeef67 | 20 | Night to dawn: on the floor against the bed, he breaks | | whole (trim to taste) |
| 34 | G40 | 121036_f0a24b2e-770c-49c3-8aac-8955a22b0a30 | 5 | Dawn: he walks up the hall to the console | | whole |
| 35 | G41 | 121040_07f2d6a9-9776-4f07-9c89-7d7c265ff185 | 14 | He tears open the hospital bag; its contents | | whole |
| 36 | G42b | 113939_1a65ea31-e326-4eb2-8b9d-2ff09aa3cf82 | 13 | He unfolds the drawing and looks; the drawing itself | 4.6 "...I'm looking, sweetheart." · 8.4 "I'm looking." | whole |
| 37 | G43 | 130822_7d5b03d5-4c96-4011-a067-9929a9226db4 | 6 | He drags the curtains open; daylight floods in | | whole |
| 38 | G44 | 130817_d74974b9-6d20-417b-ae89-a73f58ebaebf | 11 | He unbuttons the cardigan off the wife mannequin | | jump cut: 0 → 5.9, then 7.9 → end |
| 39 | G46 (2nd use) | same as 18 | 4 | Three gentle knocks, morning | | whole |
| 40 | G47 | 131246_67af812f-e15e-4259-b159-5bf68ff10694 | 6 | He walks the length of the pale hallway to the door | | 0 → 3.5 (cut as his hand reaches the handle) |
| 41 | G48 | 173654_5ab89b1b-ba29-4fbf-8357-ad2eb8934ee1 | 11 | Mona at the door with the dish; his face | ~8.2 "They're gone, Mona." | whole (new take; his hallway behind him) |
| 42 | G49 | 170055_618b8ee1-848a-4310-b28c-dbe9413d1e01 | 15 | One take: she holds him in the kitchen doorway; the camera tilts down to the drawing on the floor | | whole, fade to black over the last ~1 s (picture and sound) |
| | — | black 1 · title "LOOK" + "بُصّ" 4 s · quote card 5 s | 10 | Ending cards | | Quote: "Grief is love that keeps setting the table." |

The approved 480p rough cut v5 ran about 5:57.

## Decisions already made (do not reopen)
- Out of the film: G02, G07 (the bag reads in G21/G40/G41), G13, G19, G23, G24, G28, G35, G38, G39b, G42, G45, G49k/G49z (replaced by the one-take G49).
- One knock clip (G46) is used twice. The "I know you're in there" line comes from G21.
- G43 and G44 stay as two separate shots.
- G35 was dropped. The road ends on G34 → white → black.
- G33: the user rejected the corner-pin plan and the G33b version. The new take G33 (acc506d2) is final.
- G18: in the new take he does not reattach the arm. He holds it to his forehead. The user accepted this.

## Gaps an editor may notice
- G25 starts with the cup already spilled. That is intended: a jump cut where he drifted off.
- The song: G14 tunes in "a warm old song". The user lays in the real song and score in the edit. The 5-note tune is the motif.
- 1080p clips come from the same seed as their drafts, so the cut points above (taken from the 480p takes) should line up. Check each one by eye: G08 1.4 / 3.71, G15 2.875, G22 4.66, G25 4.0, G34 6.4–7.9, G29 12.0, G44 5.9 / 7.9, G47 3.5.
