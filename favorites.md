# Final cut (baba look, 2026-11-12)

45 favourites, identical to the Higgsfield folder **FAVOURITES** (`4cedb244-0db3-4268-bd61-d9b64006743d`).

| Shot | Take |
|---|---|
| G01 | 8ad4fa54 |
| G03 | 6ec1e1ad |
| G04 (kiss, 07★) | 41d0f3e0 |
| G05 (tableau, 08★) | 7d8378dd (the old-prompt take; covers G05) |
| G06 | 9081951b |
| G07 | 756491a8 |
| G08 | d58f1d5c |
| G09 | c5a1599d |
| G10 | a0c5b8dc |
| G11 | 88d4b73f |
| G12 | 4a61618b |
| G13 | 18ce6352 |
| G14 | 2b4009ce |
| G15a | 72b5cc86 |
| G16 | 31efcdb6 |
| G17 | 9fe9dba0 |
| G18 | 1d720a85 |
| G19 | 2cf11c7f |
| G20 | 221cf3da |
| G21 | 917293a7 |
| G22 | 6e8ca41d |
| G23 | ecdce175 |
| G25 | 4d694069 |
| G28 | 39fe0751 (old plate, inserts only) |
| G29 | fe2c6c1d |
| G30 | a41bfe89 |
| G31 | 5fdb8f2e |
| G32 | 059f4173 |
| G33 | 5abfeb16 |
| G34 | 1b465623 |
| G35 | 8aa391e4 (also gives G27) |
| G36 | c76936d3 |
| G37 | 41bdd36a |
| G38 | c4d92076 |
| G39 | 9b8ba5d8 |
| G40 | b16bd237 |
| G41 | 0b32f714 |
| G42 | bf11d1e5 |
| G42b | 9c30858b |
| G43 | 706da129 |
| G44 | b4cf79ce |
| G46 | 26784890 (knock; reuse for the first knock too) |
| G47 | 2fcc33c6 |
| G48 | 6aada38e |
| G49k | 42387b13 |

Dropped: G02, G15 (main), G24, G39b, G45.

## Gaps to decide
1. G24 dropped but G25 starts with the cup already spilled: the spill itself is never seen.
2. Flash 3 now has only the radio insert G15a: Layla singing and looking at him (25★) is gone.
3. G45 (80★, the sleeve on the child mannequin) is gone: the daylight scene ends on the cardigan.
4. Last image: shot 85 had the drawing propped against the yellow cup in the foreground; the kitchen hug G49k does not have it.
5. G28 is on the old bedroom plate; cut it short so the room does not read.

## Edit notes
- Knock: upscale one knock shot only and use it twice; lay the "I know you're in there" audio on the first use, the plain knock on the second. G19 is the dim night hallway, G46 is morning light: grade the reused shot to match.
- G43 and G44 stay two separate shots.
- All takes are 480p drafts: finalise to 1080p (draft_job_id) once the cut is locked.

## 1080p finalise cost (checked 2026-11-12)
- Seedance 2.5 finalise from a draft = **16 credits per second** (5 s = 80, 10 s = 160).
- 45 takes in FAVOURITES = 377 s → **6,032 credits**. With G15 (10 s) added: 387 s → **6,192**. Balance now 6,213.
- Savings: drop G42 bf11d1e5 if G42b replaces it (−96); upscale one knock only, G46, and drop G19 (−64); G28 is inserts only (−160 if skipped).
- G15 3a2554e0 back in: cut the radio opening (G15a covers it) and flip the close-up of her holding his hand so she reads as the passenger.
- Spill: G25 starts with the cup already spilled; play it as a jump cut (he drifted off).
- Last image: G49z a1eca541 (awaiting review): from the G49k end frame, camera tilts down and back; the drawing enters lower left on the hallway floor in front of the kitchen door. By the end only their legs are in frame.

## Cut as of 2026-11-12 15:40 — 41 takes in FAVOURITES
Dropped by the user since: G13 18ce6352 (sewing machine alone), G19 2cf11c7f (knock; G46 used once), G28 39fe0751, G42 bf11d1e5 (G42b replaces it), G38 c4d92076 (G39 already shows the mannequin in the bed). Added: G42b 9c30858b, G49z a1eca541.
G15 3a2554e0 copied into FAVOURITES (not favourited): 42 takes = 364 s = 5,824 credits to upscale. Balance about 6,190. No upscale until the user says so.

## Rough cut v5 (5:57)
- G35 dropped entirely: the road ends on G34 (truck fills the glass behind Adam) → white → black. Remove G35 8aa391e4 from FAVOURITES / the upscale list (−80 credits).
- 2026-11-13: removed from the FAVOURITES folder the two takes the cut no longer uses: G23 ecdce175 and G35 8aa391e4. FAVOURITES = 40 takes = 355 s = 5,680 credits to upscale (16/s). No upscale until the user approves.

## 1080p finalise
- Method (tested on G06 → 5674b3bf, 1920x1080, audio, same take): `generate_video` with model seedance_2_5, mode omni_reference, resolution 1080p, `draft_job_id` = the draft, the draft's own `seed`, `prompt`, `duration` and medias (role image → image_references, start_image/end_image kept). The API refuses an empty prompt.
- Draft params come from `show_generations` (params.prompt, params.seed, params.medias).
- G06 done: 5674b3bf. Remaining 39 takes = 351 s ≈ 5,616 credits; balance 6,109 after the test.

## 1080p status (2026-11-13) — folder "1080p FINAL" (33af5c6e-da18-45b4-aa2b-34f0e6ec871b)
Done (26): G01 75cdf456 · G03 c4da3721 · G04 a7e0c581 · G05 4e54b526 · G06 5674b3bf · G08 3cbc8acf · G09 26e3c884 · G10 edec3f86 · G11 d43aae34 · G12 62781679 · G14 7eb7d7b4 · G15a 3e014883 · G16 c81fab5b · G17 4f67699a · G20 3e40cf5d · G21 dfb4ec2d · G22 5336dcca · G25 ad78de1e · G29 fd275e76 · G30 50a92775 · G31 cea29628 · G32 ac03bced · G34 e40f8a66 · G36 de3d5a1b · G37 33a5ba80 · G46 57ce35e4
Failed ip_detected (2): G07 (a1b78fc0) · G18 (24efa4f9)
Not started (12): G15 · G33 · G39 · G40 · G41 · G42b · G43 · G44 · G47 · G48 · G49k · G49z
- The 26 drafts whose 1080p is done were moved into the subfolder FAVOURITES / "DONE - upscaled to 1080p" (147f6b86-32be-42c7-87e5-480d011aff67). FAVOURITES itself now holds only the 14 drafts still to upscale (G07, G15, G18, G33, G39, G40, G41, G42b, G43, G44, G47, G48, G49k, G49z) plus the two failed 1080p attempts (G07 a1b78fc0, G18 24efa4f9, ip_detected).
- The 14 drafts still to upscale were moved into the subfolder FAVOURITES / "TODO - needs 1080p" (c0cdc2e2-75d2-4eb8-b608-bf3177dc7310): G07, G15, G18, G33, G39, G40, G41, G42b, G43, G44, G47, G48, G49k, G49z. FAVOURITES root keeps only the two failed 1080p attempts (G07 a1b78fc0, G18 24efa4f9).
- 2026-11-13 credit check: balance 2,052.81. TODO upscale = 142 s × 16 = 2,272 → short by ~220 before any new draft. A 15 s draft costs 45. Waiting for the user's call on what to drop; the continuous G49 draft is on hold (start frame F49c_start uploaded as 78583acb, not confirmed).
- Correction: four more 1080p were already done by the user — G15 c0fbc45f, G40 f0a24b2e, G41 07f2d6a9, G42b 1a65ea31. Moved to "1080p FINAL"; their drafts moved to "DONE - upscaled to 1080p". 1080p done: 30 of 40.
- TODO now (10): G07, G18, G33, G39, G43, G44, G47, G48, G49k, G49z = 100 s = 1,600 credits. Balance 2,052 → fits with ~450 left. A 15 s continuous G49 draft (45) that replaces G49k + G49z would make the TODO 1,568.
- G49c continuous (kitchen hug + reveal of the drawing at the foot of the left door frame), 15 s draft 86415851, start F49c_start 78583acb.
- G49c 86415851 delivered: one take works (hug 0–10 s, camera drops to the drawing on the hallway floor by the door frame); at the end their faces leave the frame (legs only) and the drawing reads large. Awaiting the user's call.
- G33 fix: video_edit of 5abfeb16 with the P09 drawing on the sheet, draft 39d7f0fc (50 credits).
- G33 fixed: 39d7f0fc (video_edit of 5abfeb16) shows the real drawing in both Nour segments; rest of the take unchanged. Note: the rough cut mirrors Nour's segments; mirroring this take would flip the drawing (sun moves to the left). Upscale 39d7f0fc instead of 5abfeb16 (14 s = 224).
